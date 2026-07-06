# Lifecycle Harness — Parallelization (Future Improvement)

User-raised 2026-07-06. The layer-3 lifecycle suite (`lore-framework-dev/tests/lifecycle/`)
is safe to parallelize in principle but runs **one scenario at a time** today.

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
- **Stdlib ethos** — prefer `LR_LIFECYCLE_JOBS` + `ProcessPoolExecutor` over adding pytest/xdist
  unless the team explicitly opts into a dev dependency.

## Suggested approaches (pick one later)

1. **`LR_LIFECYCLE_JOBS=N` runner** — small script wrapping discover, one process per test module
   (`test_boot.py`, …). Stays stdlib-only.
2. **Parallel by engine** — run Claude and Cursor suites in two terminals (simplest, no code).
3. **Optional pytest-xdist** — if dev-repo accepts a non-stdlib test extra.

Also optional: rename test files so discover order matches catalog #1–21 (cosmetic for debugging
only).

## See also

- `lifecycle-testing-harness.md` — harness overview
- `tests/lifecycle/harness.py` — module docstring TODO
- `workdir/draft-testing-pipeline.md` — original design
