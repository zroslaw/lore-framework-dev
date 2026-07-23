#!/usr/bin/env python3
"""Parallel runner for Lore Beings lifecycle gates.

This is intentionally separate from tests/lifecycle/run_matrix.py. Lore Beings
tests have a higher blast radius than the standard framework lifecycle suite:
they spawn real Keeper sessions, may briefly run background process trees, and
cost real API money. The runner refuses to execute unless
LR_LIFECYCLE_BEINGS=1 is set; --dry-run is always safe.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TESTS_DIR)

MODULES = ["test_lrb_lifecycle.py"]
ENGINE_DEFAULTS = ["claude", "codex", "cursor"]
MODEL_DEFAULTS = {"claude": "haiku", "codex": "gpt-5.4-mini", "cursor": "composer-2.5"}


def parse_csv(value, allowed=None):
    items = [part.strip() for part in value.split(",") if part.strip()]
    if allowed is not None:
        unknown = [item for item in items if item not in allowed]
        if unknown:
            raise ValueError("unknown value(s): %s" % ", ".join(unknown))
    return items


def group_by_engine(configs):
    groups = OrderedDict()
    for engine, module in configs:
        groups.setdefault(engine, []).append((engine, module))
    return groups


class ModuleResult:
    def __init__(self, engine, module):
        self.engine = engine
        self.module = module
        self.model = MODEL_DEFAULTS.get(engine)
        self.status = "pending"
        self.exit_code = None
        self.duration_s = None
        self.stdout_path = None
        self.stderr_path = None
        self.stdout_tail = ""
        self.stderr_tail = ""

    def as_dict(self):
        return {
            "engine": self.engine,
            "module": self.module,
            "model": self.model,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_s": self.duration_s,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", errors="ignore") as fh:
        fh.write(text or "")


def run_module(engine, module, test_filter, base_env, run_dir):
    result = ModuleResult(engine, module)
    result.model = base_env.get("LR_TEST_MODEL") or MODEL_DEFAULTS.get(engine, "haiku")
    env = {**base_env, "LR_ENGINE": engine, "LR_LIFECYCLE_BEINGS": "1"}
    if "LR_TEST_MODEL" not in env:
        env["LR_TEST_MODEL"] = result.model

    debug_dir = os.path.join(run_dir, "debug", safe_name(engine), module[:-3])
    env.setdefault("LR_DEBUG_DIR", debug_dir)

    cmd = [sys.executable, os.path.join(HERE, module), "-v"]
    if test_filter:
        cmd.extend(["-k", test_filter])
    print("  start %-7s %s" % (engine, module), flush=True)
    start = time.monotonic()
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    result.duration_s = round(time.monotonic() - start, 3)
    result.exit_code = proc.returncode
    result.status = "ok" if proc.returncode == 0 else "failed"
    result.stdout_tail = (proc.stdout or "")[-1200:]
    result.stderr_tail = (proc.stderr or "")[-1200:]

    stem = "%s-%s" % (safe_name(engine), module[:-3])
    stdout_path = os.path.join(run_dir, "logs", stem + ".stdout.txt")
    stderr_path = os.path.join(run_dir, "logs", stem + ".stderr.txt")
    write_text(stdout_path, proc.stdout)
    write_text(stderr_path, proc.stderr)
    result.stdout_path = os.path.relpath(stdout_path, run_dir)
    result.stderr_path = os.path.relpath(stderr_path, run_dir)

    mark = "ok" if result.status == "ok" else "FAILED"
    print("  %-6s %-7s %s (%.1fs)" % (mark, engine, module, result.duration_s), flush=True)
    return result


def run_configs(configs, test_filter, engine_jobs, module_jobs, base_env, run_dir):
    groups = group_by_engine(configs)
    results = {}

    def run_engine_group(engine, engine_configs):
        workers = module_jobs if module_jobs > 0 else len(engine_configs)
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futures = {
                pool.submit(run_module, e, m, test_filter, base_env, run_dir): (e, m)
                for e, m in engine_configs
            }
            for fut in as_completed(futures):
                results[futures[fut]] = fut.result()

    outer = engine_jobs if engine_jobs > 0 else len(groups)
    with ThreadPoolExecutor(max_workers=max(1, outer)) as pool:
        futures = [
            pool.submit(run_engine_group, engine, engine_configs)
            for engine, engine_configs in groups.items()
        ]
        for fut in futures:
            fut.result()

    return [results[c] for c in configs]


def summarize(results):
    ok = sum(1 for r in results if r.status == "ok")
    failed = [r for r in results if r.status != "ok"]
    print("\n" + "=" * 72)
    print("  LORE BEINGS LIFECYCLE RUN SUMMARY")
    print("=" * 72)
    print("  %-8s %-28s %-8s %s" % ("engine", "module", "status", "seconds"))
    print("-" * 72)
    for r in results:
        print("  %-8s %-28s %-8s %.1f" % (r.engine, r.module, r.status, r.duration_s or 0))
    print("-" * 72)
    if failed:
        print("  %d/%d module runs ok; FAILED: %s" % (
            ok,
            len(results),
            ", ".join("%s:%s" % (r.engine, r.module) for r in failed),
        ))
    else:
        print("  %d/%d module runs ok" % (ok, len(results)))
    print("=" * 72)
    return not failed


def build_parser():
    parser = argparse.ArgumentParser(description="Run Lore Beings lifecycle gates.")
    parser.add_argument("--engines", default=",".join(ENGINE_DEFAULTS),
                        help="comma-separated engines to run (default: claude,codex,cursor)")
    parser.add_argument("--modules",
                        help="comma-separated test module filenames; default is all beings modules")
    parser.add_argument("--engine-jobs", type=int, default=0,
                        help="max engines running at once (default: all selected engines)")
    parser.add_argument("--module-jobs", type=int, default=1,
                        help="max modules per engine at once (default: 1)")
    parser.add_argument("--results-dir", default=os.path.join(HERE, "results"),
                        help="directory for run JSON and logs (default: lifecycle_beings/results)")
    parser.add_argument("--test-filter",
                        help="unittest -k filter applied inside each selected module")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the resolved plan and exit without running tests")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        engines = parse_csv(args.engines)
        modules = parse_csv(args.modules, allowed=MODULES) if args.modules else list(MODULES)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not engines or not modules:
        print("no engines or modules selected", file=sys.stderr)
        return 2

    configs = [(engine, module) for engine in engines for module in modules]
    groups = group_by_engine(configs)
    engine_jobs = args.engine_jobs if args.engine_jobs > 0 else len(groups)
    module_jobs = args.module_jobs

    print("suite: lore-beings")
    print("engines: %s" % ", ".join(engines))
    print("modules: %s" % ", ".join(modules))
    if args.test_filter:
        print("test filter: %s" % args.test_filter)
    print("concurrency: up to %s engine(s), up to %s module(s) per engine" % (
        engine_jobs,
        module_jobs if module_jobs > 0 else "all",
    ))
    if args.dry_run:
        print("\n[dry-run] no tests executed.")
        return 0

    if os.environ.get("LR_LIFECYCLE_BEINGS") != "1":
        print("refusing to run: set LR_LIFECYCLE_BEINGS=1 to enable this suite "
              "(or use --dry-run)", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join(args.results_dir, "%s-lore-beings" % stamp)
    os.makedirs(run_dir, exist_ok=False)

    base_env = dict(os.environ)
    start = time.monotonic()
    results = run_configs(configs, args.test_filter, engine_jobs, module_jobs, base_env, run_dir)
    duration_s = round(time.monotonic() - start, 3)
    all_ok = summarize(results)

    summary = {
        "schema_version": 1,
        "suite": "lore-beings",
        "started_at": stamp,
        "duration_s": duration_s,
        "framework_dir": os.path.abspath(base_env.get(
            "LR_FRAMEWORK_DIR",
            os.path.join(HERE, "..", "..", "..", "lore-framework"),
        )),
        "engines": engines,
        "modules": modules,
        "engine_jobs": engine_jobs,
        "module_jobs": module_jobs,
        "test_filter": args.test_filter,
        "status": "ok" if all_ok else "failed",
        "results": [r.as_dict() for r in results],
    }
    summary_path = os.path.join(run_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("\nresults saved: %s" % summary_path)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
