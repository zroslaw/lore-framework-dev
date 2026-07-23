# Lore Framework Dev

This repository contains the development agents and test suites for the
[`lore-framework`](../lore-framework/) plugin.

It is intentionally separate from the plugin repository. The plugin repo stays
focused on distributable framework code; this dev repo keeps framework design
knowledge, lore-architect state, lifecycle tests, quality benchmarks, fixtures,
and release evidence.

## What Is Here

- [`agents/lore-architect/`](agents/lore-architect/) — the lore agent that maintains framework design context.
- [`lore-repo.md`](lore-repo.md) — lore workspace metadata for this agent repo.
- [`tests/`](tests/) — deterministic tests, real-engine lifecycle tests, keeper lifecycle tests, and quality benchmarks.

## Documentation Map

Start here if you are new to the repo:

- [`tests/README.md`](tests/README.md) — practical test-suite entry point: how to run tests, suite list, environment knobs, and result artifacts.
- [`tests/testing-strategy.md`](tests/testing-strategy.md) — overall testing strategy: test layers, cost/risk policy, release-gate policy, failure semantics, and when to add which kind of test.
- [`tests/quality/strategy.md`](tests/quality/strategy.md) — quality benchmark strategy: treatment/control design, S1/S2/S3 scoring, probe categories, interpretation, and probe-authoring rules.
- [`tests/quality/reporting.md`](tests/quality/reporting.md) — quality report field guide: explains report columns, abbreviations, metrics, artifacts, and links to each quality test case.

Quality benchmark source files:

- [`tests/quality/probes.py`](tests/quality/probes.py) — probe catalog and S3 rubrics.
- [`tests/quality/test_quality.py`](tests/quality/test_quality.py) — single engine/model quality runner.
- [`tests/quality/run_matrix.py`](tests/quality/run_matrix.py) — quality matrix runner and release-notes report generator.
- [`tests/quality/harness.py`](tests/quality/harness.py) — fixture builder, engine runner, and judge integration.

Lifecycle test source files:

- [`tests/lifecycle/run_matrix.py`](tests/lifecycle/run_matrix.py) — lifecycle matrix runner.
- [`tests/lifecycle/harness.py`](tests/lifecycle/harness.py) — shared lifecycle test harness.
- [`tests/lifecycle/keeper_harness.py`](tests/lifecycle/keeper_harness.py) — Being Keeper lifecycle harness.
- [`tests/lifecycle/test_boot.py`](tests/lifecycle/test_boot.py)
- [`tests/lifecycle/test_consult_attach.py`](tests/lifecycle/test_consult_attach.py)
- [`tests/lifecycle/test_finalize.py`](tests/lifecycle/test_finalize.py)
- [`tests/lifecycle/test_lrb_lifecycle.py`](tests/lifecycle/test_lrb_lifecycle.py)
- [`tests/lifecycle/test_recall.py`](tests/lifecycle/test_recall.py)
- [`tests/lifecycle/test_repo_workspace.py`](tests/lifecycle/test_repo_workspace.py)
- [`tests/lifecycle/test_takeover.py`](tests/lifecycle/test_takeover.py)

Deterministic test source files:

- [`tests/test_wait.py`](tests/test_wait.py)
- [`tests/test_session_takeover.py`](tests/test_session_takeover.py)
- [`tests/test_session_archive.py`](tests/test_session_archive.py)
- [`tests/test_lrb.py`](tests/test_lrb.py)

## Testing At A Glance

Most deterministic tests use only the Python standard library:

```bash
python3 -m unittest discover -s tests -v
```

Lifecycle tests call real coding engines and are gated:

```bash
LR_LIFECYCLE=1 python3 tests/lifecycle/run_matrix.py --engine-jobs 3 --module-jobs 1
```

Quality benchmarks call real engines and an LLM judge, so they are also gated:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py --no-local-config
```

Dry-run quality matrix, with no model spend:

```bash
python3 tests/quality/run_matrix.py --no-local-config --dry-run
```

## Release Evidence

Release-quality test evidence should be durable and rerunnable.

Quality matrix runs write:

```text
tests/quality/results/matrix-<timestamp>-<matrix>/
```

with:

- `summary.json` — machine-readable ledger for automation and exact reruns.
- `summary.md` — operator-facing run summary.
- `release-notes.md` — paste-ready release-note block.
- `logs/` — per-config stdout/stderr.
- `configs/` — per-config quality score JSON.

The quality release-note block links back to
[`tests/quality/reporting.md`](tests/quality/reporting.md), so external readers
can decode terms such as `LUS`, `S1/S2/S3`, `Engine OK`, `Scored`, and `Tech E/J`.

## Relationship To `lore-framework`

By default tests locate the plugin under test at the sibling path
`../lore-framework`. Override with `LR_FRAMEWORK_DIR` if needed:

```bash
LR_FRAMEWORK_DIR=/path/to/lore-framework python3 -m unittest discover -s tests -v
```

See [`lore-repo.md`](lore-repo.md) for the agent-repo role and the reason this
development repository is kept separate from the plugin repository.
