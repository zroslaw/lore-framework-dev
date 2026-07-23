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
  LR_QUALITY=1 python3 tests/quality/run_matrix.py --configs codex:gpt-5.4-mini --probes P4-paraphrase-recall,P10-parametric-gotcha --arms control
  python3 tests/quality/run_matrix.py --matrix deep --dry-run         # plan only, no runs

Token-exhaustion handling:
  --skip <engines|engine:model>   drop up front, e.g. --skip codex.
  A probe-arm run that times out or exits non-zero is recorded as a technical
  failure. The config is PARTIAL if it still produced scoreable rows; the
  runner exits non-zero only for hard FAILED configs.

Execution tracking:
  Every non-dry-run matrix creates quality/results/matrix-<timestamp>-<matrix>/
  with summary.json, summary.md, release-notes.md, stdout/stderr logs, and
  child per-config JSON. Cost is split into agent-run cost and judge-call cost;
  missing USD fields are marked unavailable rather than estimated.
  release-notes.md is the paste-ready section for release notes and is wrapped
  in stable lr-quality-report markers for later extraction.

Inner probe concurrency is unchanged: each config subprocess still honours
LR_QUALITY_JOBS for its probe x arm fan-out.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TESTS_DIR)
TEST_QUALITY = os.path.join(HERE, "test_quality.py")
REPORTING_GUIDE = "tests/quality/reporting.md"

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
        self.status = "pending"   # ok | partial | failed
        self.uplift = None        # behavior uplift pts (from result JSON)
        self.lus_uplift = None
        self.lus_treatment = None
        self.lus_control = None
        self.s3_treatment = None
        self.s3_control = None
        self.results_path = None
        self.exit_code = None
        self.duration_s = None
        self.stderr_tail = ""
        self.output = ""          # captured stdout (scorecard)
        self.stdout_path = None
        self.stderr_path = None
        self.command = None
        self.rerun_command = None
        self.cost = {}
        self.failed_runs = []
        self.probe_filter = []
        self.arm_filter = []
        self.completed_runs = 0
        self.engine_completed_runs = 0
        self.total_runs = 0
        self.technical_failures = 0
        self.engine_technical_failures = 0
        self.judge_technical_failures = 0

    def as_dict(self):
        return {
            "engine": self.engine,
            "model": self.model,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_s": self.duration_s,
            "results_path": self.results_path,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
            "stderr_tail": self.stderr_tail,
            "command": self.command,
            "rerun_command": self.rerun_command,
            "behavior_uplift_pct": self.uplift,
            "lus_uplift_pct": self.lus_uplift,
            "lus_treatment_pct": self.lus_treatment,
            "lus_control_pct": self.lus_control,
            "s3_treatment_pct": self.s3_treatment,
            "s3_control_pct": self.s3_control,
            "cost": self.cost,
            "failed_runs": self.failed_runs,
            "probe_filter": self.probe_filter,
            "arm_filter": self.arm_filter,
            "completed_runs": self.completed_runs,
            "engine_completed_runs": self.engine_completed_runs,
            "total_runs": self.total_runs,
            "technical_failures": self.technical_failures,
            "engine_technical_failures": self.engine_technical_failures,
            "judge_technical_failures": self.judge_technical_failures,
        }


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", errors="ignore") as fh:
        fh.write(text or "")


def git_state(repo):
    def run(*args):
        try:
            return subprocess.check_output(
                ["git", "-C", repo] + list(args),
                text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    sha = run("rev-parse", "HEAD")
    status = run("status", "--porcelain")
    return {"path": repo, "sha": sha, "dirty": bool(status)}


def iso_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def shell_join(parts):
    return " ".join(shlex.quote(str(p)) for p in parts)


def _extract_summary(result, stdout):
    """Pull the results-JSON path from stdout and read the headline numbers."""
    m = RESULTS_LINE.search(stdout)
    if not m:
        return
    path = m.group(1)
    result.results_path = path
    try:
        with open(path) as f:
            payload = json.load(f)
            agg = payload["aggregate"]
        payload_results = payload.get("results") or []
        result.total_runs = len(payload_results)
        engine_failures = [
            {
                "type": "engine",
                "probe": r.get("probe"),
                "arm": r.get("arm"),
                "exit_code": r.get("exit_code"),
                "stderr_tail": r.get("stderr_tail"),
            }
            for r in payload_results
            if r.get("exit_code") != 0
        ]
        judge_failures = [
            {
                "type": "judge",
                "probe": r.get("probe"),
                "arm": r.get("arm"),
                "exit_code": "judge",
                "stderr_tail": r.get("judge_verdict") or "judge call failed",
            }
            for r in payload_results
            if r.get("judge_error")
        ]
        result.failed_runs = engine_failures + judge_failures
        result.engine_technical_failures = len(engine_failures)
        result.judge_technical_failures = len(judge_failures)
        result.technical_failures = len(result.failed_runs)
        result.completed_runs = result.total_runs - result.technical_failures
        result.engine_completed_runs = result.total_runs - result.engine_technical_failures
        if payload.get("status") in ("ok", "partial", "failed"):
            result.status = payload["status"]
        result.probe_filter = payload.get("probe_filter") or []
        result.arm_filter = payload.get("arm_filter") or []
        if agg:
            result.uplift = agg.get("behavior_uplift_pct")
            result.lus_uplift = agg.get("lus_uplift_pct")
            result.lus_treatment = agg["treatment"].get("lus_pct")
            result.lus_control = agg["control"].get("lus_pct")
            result.s3_treatment = agg["treatment"].get("s3_pass_rate_pct")
            result.s3_control = agg["control"].get("s3_pass_rate_pct")
            result.cost = agg.get("cost", {})
            tf = agg.get("technical_failures", {})
            if isinstance(tf, dict):
                result.engine_technical_failures = max(
                    result.engine_technical_failures,
                    tf.get("engine_count", result.engine_technical_failures),
                )
                result.judge_technical_failures = max(
                    result.judge_technical_failures,
                    tf.get("judge_count", result.judge_technical_failures),
                )
                result.technical_failures = max(
                    result.technical_failures,
                    tf.get("count", result.technical_failures),
                )
                result.engine_completed_runs = (
                    result.total_runs - result.engine_technical_failures
                )
                result.completed_runs = result.total_runs - result.technical_failures
            if result.status == "failed" and result.technical_failures:
                result.status = "partial"
        else:
            agent_costs = [
                r.get("cost_usd") for r in payload_results
                if r.get("cost_usd") is not None
            ]
            result.cost = {
                "agent_known_usd": round(sum(agent_costs), 6),
                "judge_known_usd": 0.0,
                "total_known_usd": round(sum(agent_costs), 6),
                "agent_unavailable_runs": sum(
                    1 for r in payload_results if r.get("cost_usd") is None
                ),
                "judge_unavailable_calls": 0,
            }
    except (OSError, KeyError, TypeError, ValueError):
        pass


def run_config(engine, model, base_env, run_dir, probes, arms):
    """Run one (engine, model) config as an isolated test_quality.py subprocess."""
    result = ConfigResult(engine, model)
    config_results_dir = os.path.join(run_dir, "configs")
    env = {
        **base_env,
        "LR_ENGINE": engine,
        "LR_TEST_MODEL": model,
        "LR_QUALITY_RESULTS_DIR": config_results_dir,
    }
    if probes:
        env["LR_QUALITY_PROBES"] = ",".join(probes)
    if arms:
        env["LR_QUALITY_ARMS"] = ",".join(arms)
    cmd = [sys.executable, TEST_QUALITY, "-v"]
    result.command = shell_join(cmd)
    result.rerun_command = (
        "LR_QUALITY=1 "
        f"python3 tests/quality/run_matrix.py --configs {engine}:{model} "
        "--engine-jobs 1 --model-jobs 1"
    )
    if probes:
        result.rerun_command += f" --probes {','.join(probes)}"
    if arms:
        result.rerun_command += f" --arms {','.join(arms)}"
    print(f"  ▶ start   {engine}:{model}", flush=True)
    start = time.monotonic()
    proc = subprocess.run(
        cmd,
        cwd=HERE, capture_output=True, text=True, env=env,
    )
    result.duration_s = round(time.monotonic() - start, 3)
    result.exit_code = proc.returncode
    result.output = proc.stdout
    result.stderr_tail = (proc.stderr or "")[-800:]
    _extract_summary(result, proc.stdout)
    if not result.results_path or proc.returncode != 0:
        if result.results_path and result.status == "partial":
            pass
        else:
            result.status = "failed"
    elif result.status == "pending":
        result.status = "ok"
    stem = f"{safe_name(engine)}-{safe_name(model)}"
    stdout_path = os.path.join(run_dir, "logs", stem + ".stdout.txt")
    stderr_path = os.path.join(run_dir, "logs", stem + ".stderr.txt")
    write_text(stdout_path, proc.stdout)
    write_text(stderr_path, proc.stderr)
    result.stdout_path = os.path.relpath(stdout_path, run_dir)
    result.stderr_path = os.path.relpath(stderr_path, run_dir)
    if result.results_path:
        result.results_path = os.path.relpath(result.results_path, run_dir)
    mark = "✔" if result.status == "ok" else "!" if result.status == "partial" else "✗"
    tail = (f"uplift {result.uplift:+.1f} pts" if result.uplift is not None
            else f"FAILED (exit {proc.returncode})")
    cost = result.cost.get("total_known_usd")
    cost_part = f", known cost ${cost:.4f}" if cost is not None else ""
    print(
        f"  {mark} done    {engine}:{model}  — {tail}{cost_part} "
        f"({result.duration_s:.1f}s)",
        flush=True,
    )
    return result


def run_matrix(configs, engine_jobs, model_jobs, base_env, run_dir):
    """Two-level fan-out: engine groups in parallel, models within each engine
    limited by model_jobs. Returns results in the input config order."""
    groups = group_by_engine(configs)
    results = {}

    def run_engine_group(engine, engine_configs):
        workers = model_jobs if model_jobs > 0 else len(engine_configs)
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            probes = base_env.get("LR_QUALITY_PROBES", "")
            arms = base_env.get("LR_QUALITY_ARMS", "")
            probe_list = [p for p in probes.split(",") if p]
            arm_list = [a for a in arms.split(",") if a]
            futs = {pool.submit(
                run_config, e, m, base_env, run_dir, probe_list, arm_list
            ): (e, m)
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
    partial = sum(1 for r in results if r.status == "partial")
    failed = [r for r in results if r.status == "failed"]
    print(f"  {ok}/{len(results)} configs ok"
          + (f", {partial} partial" if partial else "")
          + (f", {len(failed)} FAILED: "
             + ", ".join(f"{r.engine}:{r.model}" for r in failed) if failed else ""))
    print("=" * 72)
    return not failed


def cost_totals(results):
    total = 0.0
    unavailable = 0
    for r in results:
        cost = r.cost or {}
        total += cost.get("total_known_usd") or 0.0
        unavailable += cost.get("agent_unavailable_runs", 0)
        unavailable += cost.get("judge_unavailable_calls", 0)
    return {"known_usd": round(total, 6), "unavailable_fields": unavailable}


def exact_rerun_command(configs, args):
    parts = [
        "LR_QUALITY=1",
        "python3",
        "tests/quality/run_matrix.py",
        "--configs",
        ",".join(f"{e}:{m}" for e, m in configs),
        "--engine-jobs",
        str(args.engine_jobs),
        "--model-jobs",
        str(args.model_jobs),
    ]
    if args.no_local_config:
        parts.append("--no-local-config")
    if args.probes:
        parts.extend(["--probes", args.probes])
    if args.arms:
        parts.extend(["--arms", args.arms])
    return shell_join(parts)


def failed_probe_rerun_commands(results, no_local_config):
    commands = []
    for r in results:
        if not r.failed_runs:
            continue
        by_arm = OrderedDict()
        for failed in r.failed_runs:
            probe, arm = failed.get("probe"), failed.get("arm")
            if probe and arm:
                by_arm.setdefault(arm, set()).add(probe)
        for arm, probes in by_arm.items():
            cmd = (
                "LR_QUALITY=1 "
                "python3 tests/quality/run_matrix.py "
                f"--configs {r.engine}:{r.model} "
                f"--probes {','.join(sorted(probes))} "
                f"--arms {arm} "
                "--engine-jobs 1 --model-jobs 1"
            )
            if no_local_config:
                cmd += " --no-local-config"
            commands.append(cmd)
    return commands


def markdown_summary(summary):
    lines = []
    lines.append("# Quality Matrix Run")
    lines.append("")
    lines.append(f"- Status: `{summary['status']}`")
    lines.append(f"- Started: `{summary['started_at']}`")
    lines.append(f"- Ended: `{summary['ended_at']}`")
    lines.append(f"- Wall time: `{summary['duration_s']:.1f}s`")
    lines.append(f"- Matrix: `{summary['matrix']}`")
    lines.append(
        f"- Known cost: `${summary['cost']['known_usd']:.4f}` "
        f"(unavailable cost fields: `{summary['cost']['unavailable_fields']}`)"
    )
    lines.append(f"- Framework SHA: `{summary['framework']['sha']}`")
    lines.append(f"- Dev repo SHA: `{summary['dev_repo']['sha']}`")
    lines.append(f"- Report field guide: `{summary.get('reporting_guide', REPORTING_GUIDE)}`")
    lines.append("- Release notes section: `release-notes.md`")
    lines.append("")
    lines.append("## Rerun")
    lines.append("")
    lines.append("```bash")
    lines.append(summary["rerun"]["all"])
    lines.append("```")
    if summary["rerun"].get("failed"):
        lines.append("")
        lines.append("Non-ok configs only:")
        lines.append("")
        lines.append("```bash")
        lines.append(summary["rerun"]["failed"])
        lines.append("```")
    if summary["rerun"].get("failed_probe_subsets"):
        lines.append("")
        lines.append("Failed probe subsets:")
        lines.append("")
        for cmd in summary["rerun"]["failed_probe_subsets"]:
            lines.append("```bash")
            lines.append(cmd)
            lines.append("```")
    lines.append("")
    lines.append("## Configs")
    lines.append("")
    lines.append(
        "| engine | model | status | seconds | engine ok | scored | tech E/J | "
        "LUS T/C | LUS uplift | S3 T/C | S3 uplift | known cost | artifacts |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---|---:|---|---:|---:|---|")
    for r in summary["results"]:
        s3_uplift = (
            f"{r['behavior_uplift_pct']:+.1f}"
            if r["behavior_uplift_pct"] is not None else ""
        )
        lus_uplift = (
            f"{r['lus_uplift_pct']:+.1f}"
            if r.get("lus_uplift_pct") is not None else ""
        )
        lus = ""
        if r.get("lus_treatment_pct") is not None and r.get("lus_control_pct") is not None:
            lus = f"{r['lus_treatment_pct']}/{r['lus_control_pct']}"
        s3 = ""
        if r["s3_treatment_pct"] is not None and r["s3_control_pct"] is not None:
            s3 = f"{r['s3_treatment_pct']}/{r['s3_control_pct']}"
        known = r.get("cost", {}).get("total_known_usd")
        known_s = f"${known:.4f}" if known is not None else ""
        artifacts = []
        if r.get("results_path"):
            artifacts.append(r["results_path"])
        if r.get("stdout_path"):
            artifacts.append(r["stdout_path"])
        lines.append(
            f"| {r['engine']} | {r['model']} | {r['status']} | "
            f"{r['duration_s'] or 0:.1f} | "
            f"{r.get('engine_completed_runs', 0)}/{r.get('total_runs', 0)} | "
            f"{r.get('completed_runs', 0)}/{r.get('total_runs', 0)} | "
            f"{r.get('engine_technical_failures', 0)}/"
            f"{r.get('judge_technical_failures', 0)} | "
            f"{lus} | {lus_uplift} | {s3} | {s3_uplift} | {known_s} | "
            f"{'<br>'.join(artifacts)} |"
        )
    lines.append("")
    return "\n".join(lines)


def release_notes_section(summary):
    """A paste-ready, stable-marker report block for framework release notes."""
    run_id = summary.get("run_id") or "unknown-run"
    lines = [
        f"<!-- lr-quality-report:start schema=1 run_id={run_id} -->",
        "## Quality Benchmark",
        "",
        f"Status: **{summary['status'].upper()}**  ",
        f"Matrix: `{summary['matrix']}`  ",
        f"Run: `{run_id}`  ",
        f"Wall time: `{summary['duration_s']:.1f}s`  ",
        (
            f"Known cost: `${summary['cost']['known_usd']:.4f}` "
            f"(unavailable cost fields: `{summary['cost']['unavailable_fields']}`)  "
        ),
        f"Field guide: `{summary.get('reporting_guide', REPORTING_GUIDE)}`",
        "",
        "| Engine | Model | Status | Engine OK | Scored | Tech E/J | Treatment LUS | Control LUS | LUS Uplift | Treatment S3 | Control S3 | S3 Uplift | Known cost | Time |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary["results"]:
        cost = r.get("cost", {}).get("total_known_usd")
        cost_s = f"${cost:.4f}" if cost is not None else "n/a"
        lus_treatment = _pct_cell(r.get("lus_treatment_pct"))
        lus_control = _pct_cell(r.get("lus_control_pct"))
        lus_uplift = _signed_pts(r.get("lus_uplift_pct"))
        s3_treatment = _pct_cell(r.get("s3_treatment_pct"))
        s3_control = _pct_cell(r.get("s3_control_pct"))
        s3_uplift = _signed_pts(r.get("behavior_uplift_pct"))
        engine_ok = f"{r.get('engine_completed_runs', 0)}/{r.get('total_runs', 0)}"
        scored = f"{r.get('completed_runs', 0)}/{r.get('total_runs', 0)}"
        tech = (
            f"{r.get('engine_technical_failures', 0)}/"
            f"{r.get('judge_technical_failures', 0)}"
        )
        lines.append(
            f"| {r['engine']} | {r['model']} | **{r['status'].upper()}** | "
            f"{engine_ok} | {scored} | {tech} | {lus_treatment} | "
            f"{lus_control} | {lus_uplift} | {s3_treatment} | {s3_control} | "
            f"{s3_uplift} | {cost_s} | {r.get('duration_s') or 0:.1f}s |"
        )

    lines += ["", "### Technical Failures", ""]
    failure_groups = _failure_groups(summary["results"])
    if failure_groups:
        lines += [
            "| Engine | Model | Type | Exit | Count | Reason | Examples |",
            "|---|---|---|---:|---:|---|---|",
        ]
        for group in failure_groups:
            lines.append(
                f"| {group['engine']} | {group['model']} | {group['type']} | "
                f"{group['exit_code']} | {group['count']} | {group['reason']} | "
                f"{group['examples']} |"
            )
        lines.append("")
        lines.append("Full per-probe failure rows are in `summary.json`.")
    else:
        lines.append("None.")

    lines += ["", "### Rerun", ""]
    if summary["rerun"].get("failed_probe_subsets"):
        lines.append("Target only the technically failed probe subsets:")
        lines.append("")
        for cmd in summary["rerun"]["failed_probe_subsets"]:
            lines.append("```bash")
            lines.append(cmd)
            lines.append("```")
    elif summary["rerun"].get("failed"):
        lines.append("Rerun non-ok configs:")
        lines.append("")
        lines.append("```bash")
        lines.append(summary["rerun"]["failed"])
        lines.append("```")
    else:
        lines.append("No rerun needed.")

    lines += [
        "",
        "Artifacts:",
        f"- Machine summary: `{summary.get('summary_json', 'summary.json')}`",
        f"- Human summary: `{summary.get('summary_md', 'summary.md')}`",
        f"- Report field guide: `{summary.get('reporting_guide', REPORTING_GUIDE)}`",
        "",
        f"<!-- lr-quality-report:end schema=1 run_id={run_id} -->",
        "",
    ]
    return "\n".join(lines)


def _pct_cell(value):
    return f"{value:.1f}%" if isinstance(value, (int, float)) else "n/a"


def _signed_pts(value):
    return f"{value:+.1f}" if isinstance(value, (int, float)) else "n/a"


def _failure_groups(results):
    groups = OrderedDict()
    for r in results:
        for failed in r.get("failed_runs", []):
            reason = (failed.get("stderr_tail") or "").replace("\n", " ").strip()
            reason = reason[:80] if reason else "technical failure"
            key = (
                r["engine"],
                r["model"],
                failed.get("type") or "technical",
                failed.get("exit_code"),
                reason,
            )
            group = groups.setdefault(key, {
                "engine": r["engine"],
                "model": r["model"],
                "type": failed.get("type") or "technical",
                "exit_code": failed.get("exit_code"),
                "reason": reason,
                "examples": [],
                "count": 0,
            })
            group["count"] += 1
            if len(group["examples"]) < 5:
                group["examples"].append(
                    f"{failed.get('probe')}/{failed.get('arm')}"
                )
    out = []
    for group in groups.values():
        examples = group.pop("examples")
        more = group["count"] - len(examples)
        group["examples"] = ", ".join(f"`{e}`" for e in examples)
        if more > 0:
            group["examples"] += f" (+{more} more)"
        out.append(group)
    return out


def write_run_artifacts(run_dir, summary):
    summary["run_id"] = os.path.basename(run_dir)
    summary["summary_json"] = "summary.json"
    summary["summary_md"] = "summary.md"
    summary["release_notes_md"] = "release-notes.md"
    summary["reporting_guide"] = REPORTING_GUIDE
    summary_path = os.path.join(run_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    markdown_path = os.path.join(run_dir, "summary.md")
    write_text(markdown_path, markdown_summary(summary))
    release_notes_path = os.path.join(run_dir, "release-notes.md")
    write_text(release_notes_path, release_notes_section(summary))
    return summary_path, markdown_path, release_notes_path


def matrix_status(results):
    if any(r.status == "failed" for r in results):
        return "failed"
    if any(r.status == "partial" for r in results):
        return "partial"
    return "ok"


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
    p.add_argument("--probes", default="",
                   help="comma-separated probe ids to run inside each config "
                        "(default: all probes)")
    p.add_argument("--arms", default="",
                   help="comma-separated arms to run inside each config "
                        "(default: treatment,control)")
    p.add_argument("--no-local-config", action="store_true",
                   help="ignore matrix-config.local.json and use canonical "
                        "defaults (what a release ship gate uses)")
    p.add_argument("--engine-jobs", type=int, default=0,
                   help="max engines running at once (default: all)")
    p.add_argument("--model-jobs", type=int, default=1,
                   help="max models of one engine at once (default: 1, sequential)")
    p.add_argument("--results-dir", default=os.path.join(HERE, "results"),
                   help="directory for run JSON, markdown, logs, and per-config JSON (default: quality/results)")
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
    if args.probes:
        os.environ["LR_QUALITY_PROBES"] = args.probes
    if args.arms:
        os.environ["LR_QUALITY_ARMS"] = args.arms

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join(
        args.results_dir,
        "matrix-%s-%s" % (stamp, safe_name(matrix_label)),
    )
    os.makedirs(run_dir, exist_ok=False)

    started_at = iso_now()
    start = time.monotonic()
    results = run_matrix(configs, engine_jobs, model_jobs, dict(os.environ), run_dir)
    duration_s = round(time.monotonic() - start, 3)
    ended_at = iso_now()
    print_scorecards(results)
    all_ok = print_summary(results, skip, matrix_label)
    failed_configs = [(r.engine, r.model) for r in results if r.status != "ok"]
    failed_rerun = None
    if failed_configs:
        failed_rerun = (
            "LR_QUALITY=1 "
            "python3 tests/quality/run_matrix.py "
            f"--configs {','.join(f'{e}:{m}' for e, m in failed_configs)} "
            "--engine-jobs 1 --model-jobs 1"
        )
        if args.no_local_config:
            failed_rerun += " --no-local-config"
        if args.probes:
            failed_rerun += f" --probes {args.probes}"
        if args.arms:
            failed_rerun += f" --arms {args.arms}"

    summary = {
        "schema_version": 1,
        "suite": "quality-matrix",
        "matrix": matrix_label,
        "status": matrix_status(results),
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_s": duration_s,
        "command": shell_join(["python3", "tests/quality/run_matrix.py"] + sys.argv[1:]),
        "cwd": REPO_ROOT,
        "framework": git_state(os.path.abspath(os.environ.get(
            "LR_FRAMEWORK_DIR",
            os.path.join(HERE, "..", "..", "..", "lore-framework"),
        ))),
        "dev_repo": git_state(REPO_ROOT),
        "configs": [{"engine": e, "model": m} for e, m in configs],
        "skipped": sorted(skip),
        "engine_jobs": engine_jobs,
        "model_jobs": model_jobs,
        "no_local_config": bool(args.no_local_config),
        "probe_filter": args.probes,
        "arm_filter": args.arms,
        "cost": cost_totals(results),
        "rerun": {
            "all": exact_rerun_command(configs, args),
            "failed": failed_rerun,
            "failed_probe_subsets": failed_probe_rerun_commands(
                results, args.no_local_config
            ),
        },
        "results": [r.as_dict() for r in results],
    }
    summary_path, markdown_path, release_notes_path = write_run_artifacts(run_dir, summary)
    print(f"\nrun summary saved: {summary_path}")
    print(f"markdown summary saved: {markdown_path}")
    print(f"release-notes section saved: {release_notes_path}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
