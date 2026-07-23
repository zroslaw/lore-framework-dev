# Quality Benchmark Strategy

This document explains the design strategy behind the lore quality benchmark:
what it measures, why it uses treatment/control arms, how S1/S2/S3 scoring
works, how to interpret partial results, and how to add new probes.

For report terminology, see [`reporting.md`](reporting.md). For the actual test
case catalog, see [`probes.py`](probes.py).

## Purpose

The quality benchmark answers one question:

> Does lore measurably improve an agent's behavior on tasks where lore should matter?

The framework already has deterministic tests and lifecycle tests. Those tests
can prove that commands run, files are written, and engines complete workflows.
They do not prove that lore improves the substance of the answer.

The quality benchmark fills that gap. It checks whether an agent:

1. Finds the relevant lore.
2. Grounds its answer in that lore.
3. Applies the lore correctly in the final behavior.

## Non-Goals

The quality benchmark is not:

- a replacement for unit tests
- a replacement for lifecycle tests
- a full general intelligence benchmark
- a benchmark of raw model knowledge
- a benchmark of prompt style alone
- a pass/fail release gate where every technical outage is a behavioral failure

It is specifically a lore-utilization benchmark.

## Core Design

Each probe is a controlled experiment.

The benchmark builds a throwaway fixture agent repository with lore topics and
then asks a real engine to perform a task. Each probe runs in two arms:

- `treatment` — the important lore fact is present.
- `control` — the important lore fact is removed or neutralized.

The repo shape stays comparable between arms. Filenames and distractor topics
are kept similar so the benchmark measures the effect of the lore fact, not the
effect of an obvious missing file.

The key measurement is the difference between treatment and control.

If treatment succeeds and control fails or abstains correctly, that is evidence
that lore affected behavior. If both arms succeed, the task may be too easy or
answerable from general knowledge. If both arms fail, the probe may be too hard,
the engine may not be using lore, or the scoring rubric may need inspection.

## Why Treatment And Control Matter

Without a control arm, a benchmark can confuse lore use with generic model
competence.

Example: if the task asks for a safe migration time and the model chooses a
reasonable generic off-peak hour, that might look good. But if lore says the
real forbidden window is 02:00-04:00 UTC, we need to know whether the model used
that project-specific fact or simply guessed.

The control arm removes the project-specific fact. This lets the benchmark ask:

- Did the treatment answer improve because the fact was present?
- Did the control answer avoid inventing a fact it did not have?
- Is the probe actually measuring lore, or is it answerable without lore?

## Probe Structure

Probe definitions live in [`PROBES`](probes.py#L354). A probe has:

- `id` — stable name shown in reports, such as `P7-implicit-adaptation`.
- `category` — the behavior class being tested.
- `difficulty` — informal description of why the probe is easy or hard.
- `task` — prompt given to the engine.
- `s1_target` — lore file or files expected to be read.
- `s2_check` — deterministic substring or regex grounding check.
- `s3_rubric` — LLM judge rubric for behavioral application.
- `stages` — the subset of S1/S2/S3 used by the probe.

The fixture lore topics live in the same file:

- `NEEDLE_TOPICS` — facts that differ between treatment and control.
- `DISTRACTOR_TOPICS` — topics that are identical in both arms.
- `WORKDIR_FILES` — non-lore files available in the fixture workspace.

## Stage Strategy

The benchmark deliberately separates three questions.

### S1: Retrieval

S1 asks whether the engine read the load-bearing lore file.

Implementation: [`score_s1_from`](test_quality.py#L156) checks the engine tool
trace for `s1_target`.

Why it exists: when S3 fails, S1 tells us whether the agent even found the
right lore. A failed S1 and failed S3 suggest retrieval failed. A passed S1 and
failed S3 suggest the agent found the lore but did not apply it.

Limitations:

- S1 depends on engines exposing useful tool traces.
- S1 does not prove comprehension.
- S1 may be skipped for engines or probes where the trace is unavailable.

### S2: Grounding

S2 asks whether the answer contains the load-bearing fact.

Implementation: [`score_s2_from`](test_quality.py#L167) applies the probe's
`s2_check` to the final answer plus captured workspace artifacts.

Why it exists: S2 distinguishes "read the file" from "used the fact in the
answer." It is deterministic and cheap, so it survives judge outages.

Limitations:

- S2 is keyword/regex based.
- S2 can pass even when the final behavior is still wrong.
- S2 should use a stable, specific marker, not a vague natural-language phrase.

### S3: Application

S3 asks whether the final answer actually satisfies the behavioral rubric.

Implementation: [`judge_s3`](harness.py#L440) calls the LLM judge with the task,
answer, artifacts, and the probe's `s3_rubric`.

Why it exists: S3 is the closest metric to "did the lore improve the actual
result?" It catches cases where the answer mentions the right fact but writes
bad code, schedules the wrong time, uses a banned library, or invents a fact.

Limitations:

- S3 costs money.
- S3 can hit judge provider limits.
- S3 is only as good as the rubric.
- S3 failures caused by judge outage are technical failures, not behavioral failures.

## Probe Categories

The current catalog covers eight behavior classes.

| Category | Purpose | Probe Examples |
|---|---|---|
| decision-recall | Remember direct project decisions. | [`P1`](probes.py#L356), [`P4`](probes.py#L414), [`P9`](probes.py#L511) |
| gotcha-avoidance | Avoid project-specific traps. | [`P2`](probes.py#L375), [`P5`](probes.py#L433), [`P10`](probes.py#L532) |
| abstention | Do not invent facts when lore is silent. | [`P3`](probes.py#L395), [`P8`](probes.py#L489), [`P17`](probes.py#L679) |
| knowledge-update | Prefer newer lore over stale or conflicting lore. | [`P6`](probes.py#L454), [`P13`](probes.py#L595) |
| implicit-adaptation | Apply unstated norms from lore. | [`P7`](probes.py#L471), [`P18`](probes.py#L699) |
| negative-knowledge | Avoid known-bad or banned approaches. | [`P11`](probes.py#L552), [`P12`](probes.py#L574) |
| synthesis | Combine multiple lore facts in one answer. | [`P14`](probes.py#L615), [`P15`](probes.py#L637) |
| workdir-tool | Reuse existing audited workspace tools. | [`P16`](probes.py#L659) |

These categories are intentionally broader than one scenario. A release-quality
benchmark should cover the shape of lore use, not just one lucky retrieval task.

## Difficulty Strategy

The catalog mixes easy and hard probes.

Easy probes verify the basic path:

- direct filename/topic overlap
- direct task wording
- one clear lore fact
- low ambiguity

Hard probes verify realistic lore use:

- paraphrased task wording
- multi-hop topic discovery
- conflicting old and new facts
- exact numeric constraints
- common best practice contradicted by local lore
- multiple facts that must be combined
- abstention when plausible defaults are tempting

This mix matters because a benchmark with only easy direct recall probes can
look healthy while missing the cases where lore is actually valuable.

## Scoring Strategy

The single-config runner computes:

- per-row S1/S2/S3 stage scores
- treatment and control LUS
- treatment and control S3 pass rates
- LUS uplift
- behavior uplift / S3 uplift
- cost and duration metadata
- technical failures

The matrix runner then aggregates these per config and writes the report
artifacts.

### LUS

LUS, or Lore Utilization Score, is:

```text
earned stage points / possible stage points
```

LUS includes S1/S2/S3 when those stages are available. It is useful as a
diagnostic metric because it can still show retrieval and grounding progress
when S3 judging fails.

LUS is not the headline behavioral metric. It is possible to earn S1 and S2
while still failing S3.

### Behavior Uplift

Behavior uplift is:

```text
treatment S3 pass rate - control S3 pass rate
```

This is the headline quality metric when S3 is available. It asks how much
better the lore-present arm behaved than the lore-removed arm.

### Why Both Metrics Exist

S3 uplift is the real behavioral signal. LUS is the diagnostic signal.

When judge calls succeed, prefer S3 uplift for release-quality claims.

When judge calls fail, LUS can still show whether engines mostly found and
grounded the lore before the outage. That is incomplete evidence, but it is
better than throwing away the run.

## Technical Failure Strategy

Real-engine benchmarks encounter provider limits, session limits, timeouts, and
judge outages. The benchmark treats those as technical failures, not behavioral
failures.

The report separates:

- engine failures — timeout, non-zero engine exit, malformed engine result
- judge failures — S3 judge session/rate/provider failure

This is why reports show `Tech E/J`. For example, `2/34` means two engine
failures and thirty-four judge failures.

A run with technical failures is `partial` if it still produced useful evidence.
It is `failed` only when no usable score artifact exists.

## Matrix Strategy

The quality matrix has two tiers.

`regular` is the release-gate tier. It uses one cheapest representative model
per engine:

- `claude:haiku`
- `codex:gpt-5.4-mini`
- `cursor:composer-2.5`

`deep` is the broader model matrix. It is explicit because it is more expensive.

The regular matrix is meant to be stable and comparable across releases. Local
customization is allowed for personal runs, but release runs should use
`--no-local-config` so the canonical matrix is not accidentally changed.

## Reporting Strategy

Every matrix run writes a durable result directory:

```text
tests/quality/results/matrix-<timestamp>-<matrix>/
```

The report artifacts have different audiences:

- `summary.json` — machine-readable ledger for automation and exact reruns.
- `summary.md` — human operator summary for debugging one run.
- `release-notes.md` — compact block to paste into release notes.

The release-notes block includes stable markers so tooling can extract or
replace it:

```text
<!-- lr-quality-report:start ... -->
...
<!-- lr-quality-report:end ... -->
```

All generated reports link to [`reporting.md`](reporting.md), which explains the
columns and abbreviations.

## Interpreting Results

Use this rough guide:

| Pattern | Likely Meaning |
|---|---|
| High treatment S3, low control S3 | Good lore effect. |
| High treatment LUS, low/no S3 due judge failures | Engine probably found and grounded lore; rerun S3 later. |
| High Engine OK, low Scored, many judge failures | Judge/provider problem, not engine execution problem. |
| Low Engine OK, many engine failures | Engine timeout/provider/CLI issue; rerun targeted rows. |
| Treatment and control both high | Probe may be answerable without lore or too easy. |
| Treatment and control both low | Probe may be too hard, retrieval may fail, or rubric may be too strict. |
| Control invents facts | Abstention behavior is weak. |

Do not over-read one run. Real engines vary. Look for patterns across probes,
categories, and repeated release runs.

## Adding A New Probe

Add a probe when it tests a distinct lore-utilization behavior. Do not add a
probe just because a lifecycle command needs coverage.

Checklist:

1. Pick the behavior category.
2. Add or reuse a treatment/control lore topic in `NEEDLE_TOPICS`.
3. Keep repo shape comparable between arms.
4. Write a task where the lore fact should matter.
5. Define `s1_target` as the load-bearing lore file or files.
6. Define `s2_check` as a stable marker for the important fact.
7. Write an S3 rubric that is binary, specific, and resistant to generic answers.
8. Choose stages. Most probes use S1/S2/S3; abstention probes often use S3 only.
9. Run the probe on at least one cheap model.
10. Inspect treatment and control outputs before trusting the score.

Good S3 rubrics say exactly what passes and exactly what fails. They should name
the project-specific constraint, not just say "answer correctly."

## Probe Anti-Patterns

Avoid probes where:

- the answer is obvious from general knowledge
- treatment and control differ in obvious filenames or repo shape
- the rubric rewards generic best practice instead of local lore
- S2 is a vague keyword that can appear accidentally
- the task asks directly for the hidden fact by name
- the control arm is so empty that abstention is trivial
- the expected answer depends on current real-world facts outside the fixture
- success requires network access or external services

The fixture should be self-contained. The benchmark should measure lore use, not
web lookup quality or external API availability.

## Release Use

For release notes:

1. Run the regular matrix with `--no-local-config`.
2. Inspect `summary.md` for operational issues.
3. Inspect `release-notes.md` for the compact publishable block.
4. If the run is partial, decide whether the technical failures are acceptable.
5. Rerun failed subsets when provider limits or timeouts are resolved.
6. Paste or mechanically insert the release-notes block into the release doc.

A partial quality result is acceptable only when the report makes the incomplete
rows explicit. Silent missing scores are not acceptable.

## Commands

Dry run, no spend:

```bash
python3 tests/quality/run_matrix.py --no-local-config --dry-run
```

Regular release-style matrix:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py --no-local-config
```

One config:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py --configs claude:haiku --engine-jobs 1 --model-jobs 1 --no-local-config
```

One probe and arm:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py --configs codex:gpt-5.4-mini --probes P4-paraphrase-recall --arms treatment --engine-jobs 1 --model-jobs 1 --no-local-config
```
