# Empirical findings: lore utilization across engines and models

From the v1 quality-benchmark runs (2026-07-07; mechanics and numbers in
`quality-benchmark-feature.md`). These are evidence, not folklore — results JSONs live in
`tests/quality/results/`:

- **The boot-and-consult-lore path is robust down to weak model tiers.** On the easy
  catalog, all five configs (including haiku and gpt-5.4-mini on the doc-driven codex path)
  hit 100% treatment. Strong empirical support for the portability claim
  (`multi-engine-portability-direction.md`): the knowledge substrate works identically on
  claude, cursor, and codex.
- **Model–engine fit beats model tier.** Same engine (cursor): composer-2.5 scored 100%
  treatment, sonnet 62.5%. Same model (sonnet): claude engine 100%, cursor engine 62.5%.
  The pairing, not the model alone, predicts how reliably lore becomes behavior. Part of
  cursor+sonnet's gap is the final-text judging artifact
  (`benchmark-harness-operational-lessons.md`), but the S2=1/S3=0 cells with code shown
  (requests instead of falcon-fetch) were genuine application failures.
- **Control behavior is strikingly stable across vendors.** Every lore-less agent picked
  requests/urllib/boto3, sent 500 records in one request, and — ironically — proposed a
  02:00 cron for the migration, squarely inside the planted forbidden window. Stable
  counterfactuals make the uplift numbers trustworthy.
- **No confabulation observed anywhere:** 20/20 abstention cells passed, including the
  tempted variant (near-miss topic present). Composer's control P5 even explicitly refused
  to invent a schedule when the two-hop chain dead-ended — abstention appears to be a
  solved cell at current model tiers.
- **Some norms are innate to strong models** (dry-run flags on destructive scripts):
  sonnet/haiku/gpt-5.4-mini controls passed P7 unprompted; composer-2.5 and cursor+sonnet
  controls did not. Lore uplift for such norms depends on the model's own instincts — a
  reason to keep per-probe breakdowns (see `benchmark-measurement-design-principles.md`
  § control arm corollary).

## See Also

- `quality-benchmark-feature.md` — the benchmark this evidence comes from (cluster anchor).
- `benchmark-measurement-design-principles.md` — why per-probe, staged, controlled scoring made these findings visible.
- `multi-engine-portability-direction.md` — the direction these results empirically support.
- `haiku-ambiguity-detector.md` — the companion weak-tier principle on the procedure-fidelity side.
