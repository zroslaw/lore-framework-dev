#!/usr/bin/env python3
"""Parallel matrix runner for the lore-agent quality benchmark.

The benchmark itself (`test_quality.py`) runs ONE (engine, model) config per
invocation — config comes from LR_ENGINE / LR_TEST_MODEL, read once at import.
This runner drives the full matrix by spawning one isolated `test_quality.py`
subprocess per config and orchestrating them across two concurrency axes:

  --engine-jobs  how many ENGINES run at once      (default: all — claude,
                 codex, cursor in parallel; each engine hits a different
                 account, so cross-engine parallelism is effectively free)
  --model-jobs   how many MODELS of ONE engine run  (default: 1 — sequential;
                 at once                             raise to run e.g. claude
                 haiku ∥ opus. Models of one engine share that engine's token
                 pool, so parallelizing them is what actually risks the rate /
                 token exhaustion this knob defaults to avoiding.)

Each config stays a separate OS process, so config globals can't collide and a
crash or token-exhaustion in one config never corrupts another.

Tiers (from quality-benchmark-tiers-proposal.md):
  regular — one representative model per engine (the per-release ship gate);
            THE DEFAULT — a bare `run_matrix.py` runs this exact set.
  deep    — full engine x model matrix (explicit `--matrix deep` only; expensive).

The tier tables live in harness.py as canonical defaults. A fresh checkout / CI
release run always resolves to them, so releases are deterministic. To reconfigure
persistently for your own runs — swap a model, drop an engine — drop a git-ignored
`matrix-config.local.json` beside harness.py (see its docstring for the schema);
`--no-local-config` (or LR_QUALITY_NO_LOCAL=1) ignores it and forces the defaults,
which is what a release ship gate uses.

Per-run overrides (no file edit needed): --configs (any explicit set), --model
(swap one engine's model), --skip / --only (drop/keep engines or engine:model pairs).

Usage:
  LR_QUALITY=1 python3 tests/quality/run_matrix.py                    # regular, defaults
  LR_QUALITY=1 python3 tests/quality/run_matrix.py --matrix deep --model-jobs 3
  LR_QUALITY=1 python3 tests/quality/run_matrix.py --matrix deep --skip codex
  LR_QUALITY=1 python3 tests/quality/run_matrix.py --model claude=opus-4.8
  LR_QUALITY=1 python3 tests/quality/run_matrix.py --matrix deep --skip claude:opus-4.8
  LR_QUALITY=1 python3 tests/quality/run_matrix.py --configs claude:haiku,claude:opus-4.8
  python3 tests/quality/run_matrix.py --matrix deep --dry-run         # plan only, no runs

Token-exhaustion handling:
  --skip <engines|engine:model>   drop up front, e.g. --skip codex.
  A config that fails mid-run (non-zero exit — includes token exhaustion or
  timeout) is recorded as FAILED and the rest of the matrix continues. The
  runner exits non-zero if any ATTEMPTED config failed; skipped configs never
  count against the exit code.

Inner probe concurrency is unchanged: each config subprocess still honours
LR_QUALITY_JOBS for its probe x arm fan-out.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

HERE = os.path.dirname(os.path.abspath(__file__))
TEST_QUALITY = os.path.join(HERE, "test_quality.py")

RESULTS_LINE = re.compile(r"results saved:\s*(\S+)")


def preset_configs(name, engine_order, regular, deep):
    """Return the ordered (engine, model) list for a named preset, built from
    the resolved tier tables (defaults, optionally overlaid by local config)."""
    if name == "regular":
        return [(e, regular[e]) for e in engine_order if e in regular]
    if name == "deep":
        return [(e, m) for e in engine_order if e in deep for m in deep[e]]
    raise ValueError(f"unknown matrix preset: {name!r} (choose regular or deep)")


def apply_model_overrides(configs, overrides):
    """Replace an engine's model with a per-run override (--model engine=model),
    preserving config order. Engines not present in the matrix are ignored with
    a warning; --configs is the way to add new ones."""
    if not overrides:
        return configs
    engines_present = {e for e, _ in configs}
    for engine in overrides:
        if engine not in engines_present:
            print(f"warning: --model {engine}=... ignored — "
                  f"{engine} not in the selected matrix (use --configs to add it)")
    return [(e, overrides.get(e, m)) for e, m in configs]


def _parse_filter(spec):
    """Split a --skip/--only spec into engine-level and (engine, model) sets."""
    engines, pairs = set(), set()
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if ":" in tok:
            e, m = tok.split(":", 1)
            pairs.add((e.strip(), m.strip()))
        else:
            engines.add(tok)
    return engines, pairs


def parse_model_overrides(spec):
    """Parse --model 'claude=opus-4.8,codex=gpt-5.4' -> {engine: model}."""
    out = {}
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if "=" not in tok:
            raise ValueError(f"bad --model {tok!r} — expected engine=model")
        e, m = tok.split("=", 1)
        out[e.strip()] = m.strip()
    return out


def parse_configs(spec):
    """Parse an explicit --configs list like 'claude:haiku,codex:gpt-5.4-mini'."""
    out = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            raise ValueError(f"bad config {item!r} — expected engine:model")
        engine, model = item.split(":", 1)
        out.append((engine.strip(), model.strip()))
    if not out:
        raise ValueError("no configs parsed from --configs")
    return out


def group_by_engine(configs):
    """OrderedDict engine -> [(engine, model), ...] preserving first-seen order."""
    groups = OrderedDict()
    for engine, model in configs:
        groups.setdefault(engine, []).append((engine, model))
    return groups


class ConfigResult:
    def __init__(self, engine, model):
        self.engine = engine
        self.model = model
        self.status = "pending"   # ok | failed
        self.uplift = None        # behavior uplift pts (from result JSON)
        self.s3_treatment = None
        self.s3_control = None
        self.results_path = None
        self.exit_code = None
        self.stderr_tail = ""
        self.output = ""          # captured stdout (scorecard)


def _extract_summary(result, stdout):
    """Pull the results-JSON path from stdout and read the headline numbers."""
    m = RESULTS_LINE.search(stdout)
    if not m:
        return
    path = m.group(1)
    result.results_path = path
    try:
        with open(path) as f:
            agg = json.load(f)["aggregate"]
        result.uplift = agg.get("behavior_uplift_pct")
        result.s3_treatment = agg["treatment"].get("s3_pass_rate_pct")
        result.s3_control = agg["control"].get("s3_pass_rate_pct")
    except (OSError, KeyError, ValueError):
        pass


def run_config(engine, model, base_env):
    """Run one (engine, model) config as an isolated test_quality.py subprocess."""
    result = ConfigResult(engine, model)
    env = {**base_env, "LR_ENGINE": engine, "LR_TEST_MODEL": model}
    print(f"  ▶ start   {engine}:{model}", flush=True)
    proc = subprocess.run(
        [sys.executable, TEST_QUALITY, "-v"],
        cwd=HERE, capture_output=True, text=True, env=env,
    )
    result.exit_code = proc.returncode
    result.output = proc.stdout
    result.stderr_tail = (proc.stderr or "")[-800:]
    _extract_summary(result, proc.stdout)
    result.status = "ok" if proc.returncode == 0 else "failed"
    mark = "✔" if result.status == "ok" else "✗"
    tail = (f"uplift {result.uplift:+.1f} pts" if result.uplift is not None
            else f"FAILED (exit {proc.returncode})")
    print(f"  {mark} done    {engine}:{model}  — {tail}", flush=True)
    return result


def run_matrix(configs, engine_jobs, model_jobs, base_env):
    """Two-level fan-out: engine groups in parallel, models within each engine
    limited by model_jobs. Returns results in the input config order."""
    groups = group_by_engine(configs)
    results = {}

    def run_engine_group(engine, engine_configs):
        workers = model_jobs if model_jobs > 0 else len(engine_configs)
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futs = {pool.submit(run_config, e, m, base_env): (e, m)
                    for e, m in engine_configs}
            for fut in as_completed(futs):
                results[futs[fut]] = fut.result()

    outer = engine_jobs if engine_jobs > 0 else len(groups)
    with ThreadPoolExecutor(max_workers=max(1, outer)) as pool:
        futs = [pool.submit(run_engine_group, e, cfgs)
                for e, cfgs in groups.items()]
        for fut in futs:
            fut.result()
    return [results[c] for c in configs]


def print_scorecards(results):
    for r in results:
        header = f" CONFIG {r.engine}:{r.model} [{r.status}] "
        print("\n" + header.center(72, "#"))
        if r.output.strip():
            print(r.output.rstrip())
        if r.status == "failed" and r.stderr_tail.strip():
            print(f"  stderr tail: ...{r.stderr_tail.strip()[-400:]}")


def print_summary(results, skipped, matrix_label):
    print("\n" + "=" * 72)
    print(f"  QUALITY MATRIX SUMMARY — {matrix_label}")
    print("=" * 72)
    print(f"  {'engine':<9}{'model':<16}{'status':<9}{'uplift':<14}{'S3 T/C'}")
    print("-" * 72)
    for r in results:
        uplift = f"{r.uplift:+.1f} pts" if r.uplift is not None else "—"
        if r.s3_treatment is not None and r.s3_control is not None:
            s3 = f"{r.s3_treatment}/{r.s3_control}"
        else:
            s3 = "—"
        print(f"  {r.engine:<9}{r.model:<16}{r.status:<9}{uplift:<14}{s3}")
    if skipped:
        print("-" * 72)
        print(f"  skipped: {', '.join(sorted(skipped))}")
    print("-" * 72)
    ok = sum(1 for r in results if r.status == "ok")
    failed = [r for r in results if r.status == "failed"]
    print(f"  {ok}/{len(results)} configs ok"
          + (f", {len(failed)} FAILED: "
             + ", ".join(f"{r.engine}:{r.model}" for r in failed) if failed else ""))
    print("=" * 72)
    return not failed


def build_parser():
    p = argparse.ArgumentParser(
        description="Parallel matrix runner for the lore quality benchmark.")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--matrix", choices=["regular", "deep"], default="regular",
                     help="preset matrix (default: regular)")
    src.add_argument("--configs",
                     help="explicit engine:model list, comma-separated "
                          "(overrides --matrix), e.g. claude:haiku,claude:opus-4.8")
    p.add_argument("--skip", default="",
                   help="comma-separated engines or engine:model pairs to drop, "
                        "e.g. codex  or  claude:opus-4.8")
    p.add_argument("--only", default="",
                   help="comma-separated engines or engine:model pairs to keep "
                        "(drops all others)")
    p.add_argument("--model", default="",
                   help="per-run model swap, engine=model[,engine=model], "
                        "e.g. claude=opus-4.8 — replaces that engine's model in "
                        "the selected matrix")
    p.add_argument("--no-local-config", action="store_true",
                   help="ignore matrix-config.local.json and use canonical "
                        "defaults (what a release ship gate uses)")
    p.add_argument("--engine-jobs", type=int, default=0,
                   help="max engines running at once (default: all)")
    p.add_argument("--model-jobs", type=int, default=1,
                   help="max models of one engine at once (default: 1, sequential)")
    p.add_argument("--dry-run", action="store_true",
                   help="print the resolved matrix and concurrency plan, run nothing")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    # --no-local-config forces canonical defaults for BOTH the parent's preset
    # build and every child subprocess (via the inherited env).
    if args.no_local_config:
        os.environ["LR_QUALITY_NO_LOCAL"] = "1"
    engine_order, regular, deep = harness.load_tiers()

    if args.configs:
        configs = parse_configs(args.configs)
        matrix_label = f"custom ({args.configs})"
    else:
        configs = preset_configs(args.matrix, engine_order, regular, deep)
        matrix_label = args.matrix

    configs = apply_model_overrides(configs, parse_model_overrides(args.model))

    only_engines, only_pairs = _parse_filter(args.only)
    skip_engines, skip_pairs = _parse_filter(args.skip)
    if only_engines or only_pairs:
        configs = [c for c in configs
                   if c[0] in only_engines or c in only_pairs]
    configs = [c for c in configs
               if c[0] not in skip_engines and c not in skip_pairs]
    if not configs:
        print("no configs to run after --skip/--only filtering", file=sys.stderr)
        return 2
    skip = skip_engines | {f"{e}:{m}" for e, m in skip_pairs}

    groups = group_by_engine(configs)
    engine_jobs = args.engine_jobs if args.engine_jobs > 0 else len(groups)
    model_jobs = args.model_jobs

    print(f"matrix: {matrix_label}  |  {len(configs)} config(s), "
          f"{len(groups)} engine(s)")
    print(f"concurrency: up to {engine_jobs} engine(s) in parallel, "
          f"up to {model_jobs if model_jobs > 0 else 'all'} model(s) per engine")
    for engine, cfgs in groups.items():
        print(f"  {engine}: {', '.join(m for _, m in cfgs)}")
    if skip:
        print(f"skipped: {', '.join(sorted(skip))}")

    if args.dry_run:
        print("\n[dry-run] would run the configs above; nothing executed.")
        return 0

    if os.environ.get("LR_QUALITY") != "1":
        print("\nrefusing to run: set LR_QUALITY=1 to enable the benchmark "
              "(or use --dry-run).", file=sys.stderr)
        return 2

    results = run_matrix(configs, engine_jobs, model_jobs, dict(os.environ))
    print_scorecards(results)
    all_ok = print_summary(results, skip, matrix_label)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
