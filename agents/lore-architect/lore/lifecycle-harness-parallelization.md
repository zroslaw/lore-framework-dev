# Lifecycle Harness — Parallelization

User-raised 2026-07-06. The layer-3 lifecycle suite (`lore-framework-dev/tests/lifecycle/`)
is safe to parallelize in principle. As of 2026-07-22, standard lifecycle release gates should use
`tests/lifecycle/run_matrix.py`, which wraps the existing `unittest` modules in isolated subprocesses
and records durable JSON/log evidence under `tests/lifecycle/results/`.

## Why parallelize

A full pass is ~15–45 minutes per engine (19 scenarios × one headless engine subprocess each).
Developers validating framework doc changes (`LR_FRAMEWORK_DIR` + cheap model) wait on serial
wall time unnecessarily.

## Why it's safe

Each scenario is isolated:

- Own `tempfile.mkdtemp` workspace + agent repo + local bare `origin` (no network)
- Shared read-only `LR_FRAMEWORK_DIR` plugin under test
- No cross-test git state or shared working directories

`unittest discover` order is **not** catalog order (e.g. scenario #7 recall runs after #10–13
because `test_recall.py` sorts after `test_finalize.py` alphabetically) — but order doesn't
affect correctness because fixtures don't leak.

## Constraints / risks

- **API rate limits** — don't run all 19 concurrently on one engine; cap workers (e.g. 3–5 by
  test file, or 2 engines in separate terminals).
- **Log noise** — parallel runs need per-worker log prefixes or separate log files.
- **Cost bursts** — same total spend, but concentrated; may trip quotas faster.
- **Stdlib ethos** — keep this as a stdlib runner around `unittest`, not pytest/xdist, unless the
  team explicitly opts into a dev dependency.

## Implemented approach

`tests/lifecycle/run_matrix.py` runs one process per `(engine, test module)` pair. Default standard
suite: `test_boot.py`, `test_consult_attach.py`, `test_finalize.py`, `test_recall.py`,
`test_repo_workspace.py`, and `test_takeover.py`. Lore Beings coverage is no longer a `--suite`
mode inside this runner; it lives in the separate `tests/lifecycle_beings/run_matrix.py` entry
point because it is gated by `LR_LIFECYCLE_BEINGS=1` and has higher blast radius.

Default concurrency is intentionally conservative: all selected engines may run in parallel, but
modules within one engine run serially (`--module-jobs 1`) unless the operator raises it. This gives
most of the wall-time win across separate provider accounts without causing avoidable same-account
quota bursts.

Typical release-gate command:

```bash
LR_LIFECYCLE=1 python3 tests/lifecycle/run_matrix.py --engine-jobs 3 --module-jobs 1
```

Targeted rerun after a failure:

```bash
LR_LIFECYCLE=1 python3 tests/lifecycle/run_matrix.py --engines codex --modules test_finalize.py
```

Lore Beings dry-run and gated run:

```bash
python3 tests/lifecycle_beings/run_matrix.py --dry-run
LR_LIFECYCLE_BEINGS=1 python3 tests/lifecycle_beings/run_matrix.py --engine-jobs 3 --module-jobs 1
```

Each run writes a timestamped directory containing `summary.json`, per-module stdout/stderr logs,
and `LR_DEBUG_DIR` captures. Use that artifact as the release evidence instead of reconstructing
status from session summaries.

## Still Open

Also optional: rename test files so discover order matches catalog #1–21 (cosmetic for debugging
only).

## See also

- `lifecycle-testing-harness.md` — harness overview
- `tests/lifecycle/harness.py` — module docstring TODO
- `workdir/draft-testing-pipeline.md` — original design
