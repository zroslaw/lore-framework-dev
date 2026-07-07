# Benchmark measurement design — principles borrowed from industry evals

Distilled from the research pass (NIAH/RULER/NoLiMa, LongMemEval-V2, BEAM,
ImplicitMemBench, RAGAS) that shaped the quality benchmark
(`quality-benchmark-feature.md`). Reusable whenever we design a measurement for agent
behavior:

1. **Many simple probes beat few clever ones.** Keep per-probe scoring binary or
   near-binary; representativeness comes from volume, variety, and aggregation — not from a
   sophisticated per-question score.
2. **Score the pipeline in stages** (RAGAS decomposition). Retrieval → grounding →
   application as independent 0/1 checks tells you *where* a configuration loses points.
   The S2=1/S3=0 "knew it but didn't apply it" pattern was invisible in any single-number
   design and turned out to be the defining failure mode of sonnet-on-cursor
   (`benchmark-findings-engines-models.md`).
3. **A control arm isolates the treatment.** Same repo shape, needle removed — uplift =
   treatment − control separates "the lore helped" from "the model is smart". Corollary
   discovered live: strong models pass some norm probes (dry-run flag on destructive
   scripts) with no lore at all, so per-probe uplift can legitimately be ~0; the per-probe
   view catches what an aggregate would hide.
4. **Difficulty axes make a benchmark discriminating.** The easy catalog saturated at 100%
   across five configs — useless for ranking. Adding NoLiMa-style zero-lexical-overlap
   tasks, two-hop link chains, a superseded stale topic, and a tempting near-miss abstention
   spread treatment scores 62.5–100%. Saturation is a design smell, not a success signal.
5. **Fix the judge; deterministic-first everywhere else.** Judge model pinned (claude+haiku)
   across engines and runs so scores stay comparable; every stage that can be scripted (tool
   trace, canary/regex) is scripted — the same discipline as the lifecycle harness's
   structural assertions (`lifecycle-testing-harness.md` § Assertion style).

## See Also

- `quality-benchmark-feature.md` — the benchmark these principles produced (cluster anchor).
- `benchmark-findings-engines-models.md` — what the design made visible.
- `benchmark-harness-operational-lessons.md` — the operational (runtime) companion rules.
- `lifecycle-testing-harness.md` — the sibling harness whose deterministic-assertion premise principle 5 extends.
- `execution-testing-catches-blind-ambiguity.md` — the broader "measure by running, not by reviewing" principle family.
