# Lore Framework Testing Strategy

This document explains how the `lore-framework` test suite is organized, what
each layer proves, when to run each layer, and how test results should be used
for releases.

The tests live in this dev repository, not in the framework plugin repository.
That keeps the marketplace plugin slim while still letting us test the real
plugin source from a sibling checkout.

## Goals

The test suite has four goals:

1. Prove deterministic framework behavior without spending model tokens.
2. Exercise real lifecycle workflows against real coding engines before release.
3. Measure whether lore improves agent behavior, not just whether commands run.
4. Produce durable, rerunnable evidence for release notes and later debugging.

These goals intentionally require different kinds of tests. A pure unit test can
prove parsing logic cheaply. A lifecycle test can prove that an engine can
actually execute `/lr:boot` or `/lr:finalize`. A quality benchmark can show
whether an engine used lore in a task where lore should matter.

## Test Layers

### Layer 1: Deterministic Unit And Protocol Tests

These tests run locally, use no model calls, and should be cheap enough for
normal development.

Examples:

- [`test_wait.py`](test_wait.py) — wait-server helpers and JSON-RPC protocol behavior.
- [`test_session_takeover.py`](test_session_takeover.py) — Cursor takeover conversion fixtures.
- [`test_session_archive.py`](test_session_archive.py) — session archive behavior.
- [`test_lrb.py`](test_lrb.py) — Being Keeper logic with stub engines.

Use this layer for:

- parsers
- file transforms
- state-machine logic
- JSON/JSONL handling
- deterministic command behavior
- edge cases that do not need a real engine

This layer should be the first place new coverage lands whenever possible.

### Layer 2: Stubbed Engine Integration Tests

Stubbed integration tests execute framework code around a fake or controlled
engine. They prove process handling, result parsing, file outputs, and error
paths without paying for a real model.

Examples:

- [`fixtures/stub_engine.py`](fixtures/stub_engine.py)
- [`fixtures/stub_codex_engine.py`](fixtures/stub_codex_engine.py)
- [`fixtures/stub_cursor_engine.py`](fixtures/stub_cursor_engine.py)

Use this layer when the framework behavior depends on engine-shaped outputs, but
the engine's intelligence is not the subject of the test.

### Layer 3: Real-Engine Lifecycle Tests

Lifecycle tests run real engines against disposable fixture workspaces. They
prove that the framework lifecycle actually works end to end under each engine.

Main files:

- [`lifecycle/harness.py`](lifecycle/harness.py)
- [`lifecycle/run_matrix.py`](lifecycle/run_matrix.py)
- [`lifecycle/test_boot.py`](lifecycle/test_boot.py)
- [`lifecycle/test_consult_attach.py`](lifecycle/test_consult_attach.py)
- [`lifecycle/test_finalize.py`](lifecycle/test_finalize.py)
- [`lifecycle/test_recall.py`](lifecycle/test_recall.py)
- [`lifecycle/test_repo_workspace.py`](lifecycle/test_repo_workspace.py)
- [`lifecycle/test_takeover.py`](lifecycle/test_takeover.py)

These tests are gated behind `LR_LIFECYCLE=1` because they call real engines and
cost money.

Use lifecycle tests to prove:

- boot behavior
- recall/consult/attach workflows
- reflection, merge, summarize, finalize flows
- repo/workspace scaffolding commands
- engine-specific headless execution behavior
- release-gate flows that cannot be trusted from stubs alone

The lifecycle matrix runner records durable results under
`tests/lifecycle/results/`.

### Layer 3b: Keeper Lifecycle Tests

Keeper lifecycle tests cover the Being Keeper runtime (`lrb`) where real process
behavior matters. They are gated separately with `LR_LIFECYCLE_KEEPER=1` because
some scenarios spawn real process trees or daemon subprocesses.

Main files:

- [`lifecycle/test_lrb_lifecycle.py`](lifecycle/test_lrb_lifecycle.py)
- [`lifecycle/keeper_harness.py`](lifecycle/keeper_harness.py)

Use this layer only for behavior that cannot be proved safely with stubs:

- real engine result JSON shape
- process-tree kill behavior
- daemon lock/shutdown behavior
- PID identity checks against real `ps` output
- real cost extraction from engine metadata

### Layer 4: Quality Benchmark

The quality benchmark measures whether lore improves agent behavior. It is not
just a lifecycle test. It asks: when the answer should depend on lore, does the
agent find the lore, ground its answer in it, and act correctly?

Main files:

- [`quality/strategy.md`](quality/strategy.md) — detailed quality benchmark strategy.
- [`quality/reporting.md`](quality/reporting.md) — report terminology and field guide.
- [`quality/probes.py`](quality/probes.py) — probe catalog and scoring rubrics.
- [`quality/test_quality.py`](quality/test_quality.py) — single-config runner.
- [`quality/run_matrix.py`](quality/run_matrix.py) — matrix runner and release-note reporting.
- [`quality/harness.py`](quality/harness.py) — fixture building, engine calls, judge calls.

The benchmark is gated behind `LR_QUALITY=1` because it calls real engines and
an LLM judge.

Use this layer to evaluate:

- whether lore improves behavior versus a control arm
- whether engines read the right lore
- whether engines can apply facts that are paraphrased, hidden, conflicting, or multi-hop
- cross-engine and cross-model behavior differences
- release quality evidence for the framework

## Cost And Risk Policy

Not every test belongs in every development loop.

| Layer | Token Cost | Risk | Default Use |
|---|---:|---|---|
| Unit/protocol | none | low | run often and before commits |
| Stubbed integration | none | low/medium | run for framework behavior changes |
| Lifecycle | real engine cost | medium | release gate, nightly, or targeted work |
| Keeper lifecycle | real engine cost + process risk | high | targeted and release-gate only |
| Quality benchmark | real engine + judge cost | medium/high | release notes, model comparison, quality work |

Real-engine suites should default to the cheapest representative model per
engine. Larger model matrices are explicit, not accidental.

## Release-Gate Policy

A release should have:

1. Deterministic tests passing locally.
2. Lifecycle matrix evidence for the supported engines.
3. Quality benchmark evidence for the regular matrix.
4. Durable summaries saved under the relevant `results/` directory.
5. Release notes updated with the quality benchmark report block.

For quality benchmarks, a `partial` result can be acceptable release evidence
when the incomplete rows are technical failures and the report makes them clear.
A `failed` result means the suite did not produce a usable score artifact and
should not be treated as valid benchmark evidence.

## Failure Semantics

**Test failure** means the framework or benchmark assertion failed.

**Technical failure** means infrastructure prevented scoring or completion:
engine timeout, provider outage, token/session limit, judge outage, or malformed
engine result. Technical failures should be recorded and rerunnable.

**Partial result** means the run produced useful evidence but had technical
failures. Partial is not the same as failed.

**Failed result** means the run could not produce a usable artifact.

This distinction matters because real-engine test suites encounter provider
limits. The framework should preserve the evidence that did run, identify the
technical gaps, and produce exact rerun commands.

## Result Artifacts

Durable result artifacts are part of the test contract.

Lifecycle matrix runs write under:

```text
tests/lifecycle/results/
```

Quality matrix runs write under:

```text
tests/quality/results/matrix-<timestamp>-<matrix>/
```

Quality runs include:

- `summary.json` — machine-readable ledger
- `summary.md` — operator-facing run summary
- `release-notes.md` — paste-ready release-note block
- `logs/*.stdout.txt` / `logs/*.stderr.txt` — raw config logs
- `configs/quality-*.json` — per-config score JSON

The machine-readable files should carry enough information to answer:

- what command ran
- when it ran
- which repo SHAs were tested
- which engine/model configs ran
- what each config cost
- what timed out or hit a provider limit
- how to rerun the exact matrix or failed subsets

## Adding New Tests

Prefer the lowest layer that proves the behavior.

Add a deterministic test when:

- the behavior is local logic
- inputs and expected outputs can be controlled
- no real engine judgment is needed

Add a lifecycle scenario when:

- a real engine must follow framework instructions
- a CLI command must work end to end
- the result depends on real engine execution shape

Add a quality probe when:

- the question is whether lore changes answer quality
- treatment/control comparison is meaningful
- the task can be scored by retrieval, grounding, and application
- the expected answer can be expressed in a stable rubric

Do not add a quality probe for ordinary command correctness. Quality probes are
for lore utilization, not generic framework regression coverage.

## Running The Main Suites

Deterministic tests:

```bash
python3 -m unittest discover -s tests -v
```

Lifecycle matrix dry run:

```bash
python3 tests/lifecycle/run_matrix.py --dry-run
```

Lifecycle release-style run:

```bash
LR_LIFECYCLE=1 python3 tests/lifecycle/run_matrix.py --engine-jobs 3 --module-jobs 1
```

Quality matrix dry run:

```bash
python3 tests/quality/run_matrix.py --no-local-config --dry-run
```

Quality regular matrix:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py --no-local-config
```

Targeted quality rerun:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py --configs codex:gpt-5.4-mini --probes P4-paraphrase-recall --arms treatment --engine-jobs 1 --model-jobs 1 --no-local-config
```
