# Lore Agent Quality Benchmark (`tests/quality/`)

A third test track exists beside the lifecycle harness and the deterministic layer:
`lore-framework-dev/tests/quality/` measures **lore utilization** — did the lore make the
agent's output better — where the lifecycle harness (`lifecycle-testing-harness.md`) measures
procedure fidelity. Built and validated 2026-07-06/07. Design doc:
`workdir/draft-lore-quality-benchmark.md` (don't duplicate it here).

This topic is the anchor for the benchmark cluster: `benchmark-findings-engines-models.md`
(what the v1 runs showed), `benchmark-harness-operational-lessons.md` (failure-derived harness
rules), `benchmark-measurement-design-principles.md` (the reusable measurement-design
principles behind it), `quality-benchmark-v2-catalog.md` (the 18-probe v2 catalog), and
`quality-benchmark-v2-known-probe-gaps.md` (two v2 probes still open, ceiling-effect fix
needed).

## Mechanics

- **Planted-knowledge probes.** A fixture agent repo (23 topics) plants facts ("needles")
  that change the right answer to a task. v1 catalog: 8 probes in `probes.py` — easy trio
  (decision recall, gotcha avoidance, abstention) + hard five (paraphrase/NoLiMa-style, two-hop
  link chain, knowledge update over a stale topic, implicit dry-run norm, tempted abstention).
  **v2 catalog (2026-07-09, uncommitted): expanded to 18 probes / 8 categories** — adds
  negative-knowledge, synthesis, and workdir-tool categories, plus a third variant of each v1
  category. Validated on one real run with two probes still showing a ceiling effect. See
  `quality-benchmark-v2-catalog.md` and `quality-benchmark-v2-known-probe-gaps.md`.
- **Two arms per probe.** Treatment = needle present; control = same filenames and
  lore-context, needle neutralized. Same haystack, no needle — the score delta isolates
  knowledge value, not diligence.
- **Three-stage scoring.** S1 retrieval (tool-trace shows the needle file was opened),
  S2 grounding (fact appears in output; substring/regex), S3 application (behavior correct;
  binary LLM judge, one-line rubric). A 1-0-0 row = "found it, ignored it" — diagnostic,
  not just a grade.
- **Metrics.** LUS = stage points %, per arm; **Behavior Uplift** = S3%(treatment) −
  S3%(control) is the headline and the only number that is cross-engine comparable
  (S1 is unscorable on cursor).
- **Run on request:** `LR_QUALITY=1 [LR_ENGINE=claude|cursor|codex] [LR_TEST_MODEL=…]
  python3 tests/quality/test_quality.py -v`. The judge is always claude+haiku
  (`LR_JUDGE_MODEL`) regardless of engine, for comparability. Results JSONs land in
  `tests/quality/results/` (gitignored).

## v1 results (extended catalog, k=1, 2026-07-07)

| config | treatment S3 | control S3 | uplift |
|---|---|---|---|
| cursor+composer-2.5 | 100% | 25.0% | +75.0 |
| claude+sonnet | 100% | 37.5% | +62.5 |
| claude+haiku | 87.5% | 37.5% | +50.0 |
| codex+gpt-5.4-mini | 87.5% | 37.5% | +50.0 |
| cursor+sonnet | 62.5% | 25.0% | +37.5 |

Cost: ~$9 sonnet, ~$1.5 haiku per 16-run config; cursor/codex don't report cost.
Interpretation of these numbers: `benchmark-findings-engines-models.md`.

## Status and known measurement debt

- `tests/quality/` sits outside finalize's `agents/` commit scope (same placement rule as the
  lifecycle harness) — it needs its own manual commit. This now includes the whole v2 catalog
  and the judge-workspace-artifacts fix below — none of it is committed yet.
- **Fixed:** judge used to see final text only, deflating scores for file-writing
  engines/models. The judge now also sees workspace artifacts (git diff + new files) captured
  before the fixture is torn down — closes this gap. See `benchmark-harness-operational-lessons.md`.
- **Open:** two v2-catalog probes (P12-banned-library-avoidance, P16-workdir-tool-reuse) show a
  ceiling effect (control passes too — no discrimination) and need task-framing rework before
  the v2 catalog is ship-ready. See `quality-benchmark-v2-known-probe-gaps.md` — don't treat
  this as done without a fresh run showing a real split on both probes.
  Blocks `quality-benchmark-tiers-proposal.md`.
- k=1 (no repetitions) in v1; v2's one real run is also k=1.
- A LongMemEval comparative track was considered and deferred by the user ("has its
  drawbacks" — lore is deliberately lossy/curated, LongMemEval partly rewards verbatim
  trivia recall; revisit if cross-system comparison becomes a goal).

## See Also

- `benchmark-findings-engines-models.md` — the empirical findings from the v1 runs.
- `benchmark-harness-operational-lessons.md` — judge-invalidation, timeout, quota-batching, and
  null-byte-sanitization rules.
- `benchmark-measurement-design-principles.md` — the industry-eval principles the design borrows.
- `quality-benchmark-v2-catalog.md` — the 18-probe v2 catalog and the harness changes it needed.
- `quality-benchmark-v2-known-probe-gaps.md` — the two v2 probes still needing rework.
- `lifecycle-testing-harness.md` — the sibling track: procedure fidelity vs lore utilization.
- `execution-testing-catches-blind-ambiguity.md` — the shared premise: empirical runs catch what review can't.
- `multi-engine-portability-direction.md` — the portability claim the v1 results now back with data.
- `workdir/draft-lore-quality-benchmark.md` — the design doc.
