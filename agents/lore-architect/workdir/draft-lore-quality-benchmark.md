# Draft — Lore Agent Quality Benchmark (LAQ)

Status: draft v1, 2026-07-06. Companion to `draft-testing-pipeline.md` (lifecycle harness).
Goal: a measurable score for how well a lore agent *uses* its lore — recalls the right
knowledge when a task needs it, and adjusts its behavior accordingly.

The lifecycle harness answers "did the agent follow the procedure?"
This benchmark answers "did the lore make the agent's output better?"

## Design premises

1. **Many simple probes, not few clever ones.** Each probe is scored in simple stages.
   The representative number comes from aggregating across a varied catalog
   (the NIAH / RULER / LongMemEval approach).
2. **Score the pipeline in stages.** Per probe, three independent 0/1 checks:
   - **S1 Retrieval** — did the agent open the load-bearing lore file?
     (structural: transcript / file-read trace)
   - **S2 Grounding** — does the output carry the planted fact?
     (script: canary token or grep)
   - **S3 Application** — did the *behavior* change the right way?
     (LLM judge, binary label, one-line rubric per probe)
   A 1-0-0 result is diagnostic: found the file, ignored it.
3. **Control run isolates lore value.** Same fixture, same task, but the load-bearing
   topics are replaced with neutral filler of similar size (repo shape and haystack
   size preserved — we remove the needle, not the haystack). Headline metric:
   **Lore Uplift = treatment score − control score.**
4. **Deterministic where possible, judge only where necessary** — same discipline as
   the lifecycle harness. Only S3 (and the abstention category) need a judge.

## Probe categories (v1)

Mirrors what lore actually holds: decisions, gotchas, workflows, updates, links,
gaps, preferences. Mapped from LongMemEval-V2 / BEAM / ImplicitMemBench categories.

| # | Category | Planted lore | Task | S3 pass looks like |
|---|----------|-------------|------|--------------------|
| 1 | **Decision recall** | A decision + reasoning ("we use X, never Y, because Z") | Task where the decision applies | Output follows X; ideally cites why |
| 2 | **Gotcha avoidance** | A known trap ("staging API rejects batches >100") | Task that naturally walks into the trap, no hint given | Output avoids the trap unprompted |
| 3 | **Workflow knowledge** | Multi-step procedure with one non-obvious step | "Do the procedure" | Non-obvious step present, right order |
| 4 | **Knowledge update** | Old topic superseded by newer topic (dated) | Task where old vs new answers differ | Uses the newer fact |
| 5 | **Multi-hop recall** | Fact sits 2 hops away via topic links; entry topic only points | Task needing the distant fact | Follows the link chain; uses the fact |
| 6 | **Abstention** | Nothing — the topic plausibly *could* exist but doesn't | Question about the missing knowledge | Says lore doesn't cover it; no invention |
| 7 | **Implicit adaptation** | A user/style preference, stated once | Task that doesn't mention the preference | Output silently reflects it |

Notes:
- Category 6 has no S1/S2; it is judge-only (binary). It guards against the failure
  mode where high recall is bought by confabulation.
- Category 7 is the ImplicitMemBench idea — the strongest test of "lore-aware
  behavior" as opposed to "lore-aware answers".

## Difficulty axes (variants per probe)

- **Depth D0/D1/D2** — fact summarized in `lore-context.md` / only in a deep topic /
  only 2 link-hops away. (NIAH depth analog.)
- **Lexical overlap L0/L1** — task shares words with the lore topic / task is fully
  paraphrased, no shared keywords. (NoLiMa analog — L1 tests semantic recall,
  not grep.)
- **Distractor load N** — number of plausible-but-irrelevant topics in `lore/`.
  Start with fixed N≈15; scale later.

## Scoring & aggregation

- Per probe: S1+S2+S3 (0–3), except abstention (0/1 scaled).
- **Lore Utilization Score (LUS)** = earned points / possible points, as %,
  reported overall + per category + per difficulty axis.
- **Lore Uplift (LU)** = LUS(treatment) − LUS(control). Headline number.
- k repetitions per probe (start k=3), report mean; flag high-variance probes.
- Cost and latency recorded but reported separately (per user: different metrics).

## Harness reuse

- Fixture builder + engine drivers from `tests/lifecycle/harness.py`
  (throwaway agent repo, canary tokens, headless engine run, `LR_TEST_MODEL`).
- New: probe spec format (planted files, task prompt, S1 target file, S2 canary,
  S3 rubric line), control-fixture generator, judge runner, score aggregator.
- Gate behind `LR_QUALITY=1` (real API cost, like `LR_LIFECYCLE=1`).
- Judge model fixed and versioned (results comparable across runs); judge prompts
  stored in-repo like any other procedure doc.

## v1 scope suggestion

- 7 categories × 2 probes × 2 variants (D/L mix) = **~28 probes**.
- ×2 (treatment + control) ×3 reps ≈ 170 runs. On sonnet, extrapolating lifecycle
  costs (~$0.10–0.30 for short single-shot scenarios): roughly **$20–50 and a few
  hours serial** — parallelization matters more here than for lifecycle
  (see `lifecycle-harness-parallelization.md`).
- Start smaller for the pilot: 1 probe per category, k=1, treatment+control
  (~14 runs) to validate the probe format and judge rubrics before scaling.

## Open questions

- Judge calibration: spot-check judge labels by hand for the pilot; measure
  judge–human agreement before trusting S3 at scale.
- Should S1 count reads via `/lr:recall` fan-out differently from direct reads?
- Fixture realism: synthetic lore vs snapshots of real agent repos (synthetic first —
  controllable canaries; real-repo track later as "field benchmark").
- Cross-engine: same probes on claude/codex/cursor would measure engine effect on
  lore utilization — the multi-engine story extends here naturally.

## Sources (industry patterns borrowed)

- NIAH / RULER — depth×length grid, task categories, accuracy aggregation.
- NoLiMa — zero-lexical-overlap probes (our L1 axis).
- LongMemEval(-V2), BEAM, MemBench — category sets incl. knowledge update,
  abstention; deterministic-first scoring, binary LLM-judge labels.
- ImplicitMemBench — implicit behavioral adaptation (our category 7).
- RAGAS — pipeline decomposition (context recall / faithfulness → our S1/S2/S3).
