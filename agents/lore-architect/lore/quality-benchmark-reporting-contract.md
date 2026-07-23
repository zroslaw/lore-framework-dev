# Quality benchmark reporting contract

`tests/quality/run_matrix.py` now has a durable report shape. Every non-dry-run
matrix run writes a run directory with:

- `summary.json`
- `summary.md`
- `release-notes.md`
- per-config logs
- per-config JSON

The release-notes block is wrapped in stable `lr-quality-report` markers so a
caller can mechanically extract or replace it.

The reporting contract is not just "print the scores." A report must preserve
enough execution metadata to answer:

- what ran, including engine/model configs and selected probe tiers
- when it ran
- which relevant repo SHAs were tested
- how long it took
- what known cost was reported
- which cost fields were unavailable
- which cells failed technically
- how to rerun the full matrix
- how to rerun only failed probe/arm subsets

Future quality-reporting changes should extend this contract rather than
replace it ad hoc.

## Vocabulary and field guide

Quality reports use specialized terms: `S1`, `S2`, `S3`, `LUS`, `Engine OK`,
`Scored`, and `Tech E/J`. These are not self-explanatory to release-note
readers.

`tests/quality/reporting.md` is the field guide for the report format. It links
to the probe catalog and per-probe test cases; `tests/quality/strategy.md`
explains the benchmark design. Generated `summary.md`, `release-notes.md`, and
`summary.json` should point back to `tests/quality/reporting.md` so a reader can
decode the metrics without spelunking through source.

When the report format changes, update the field guide in the same change.
Keep this glossary scoped to quality benchmark reports. Lifecycle evidence has
its own artifact vocabulary under `tests/lifecycle/results/`, and Lore Beings
lifecycle evidence has the parallel but separate `tests/lifecycle_beings/results/`
track. Mixing those into the quality glossary makes release evidence harder to
audit because the three tracks answer different questions.

## Technical failures are scoreable incompleteness

Technical failures are distinct from behavioral failures. Engine timeouts,
non-zero exits, judge/provider outages, and session/quota failures make a config
or matrix `partial` when useful evidence still exists. They must not be
collapsed into S3 pass/fail behavior.

Reports split technical failures by source (`Tech E/J`): engine failures vs.
judge failures. They also split `Engine OK` from `Scored`, so a run where
engines mostly completed but S3 judging hit quota is visibly different from a
run where engines failed to execute.

This distinction is release-relevant: partial evidence can be acceptable only
when incomplete rows are explicit and targeted rerun commands are available.

## See Also

- `quality-benchmark-feature.md` - cluster anchor for the benchmark.
- `benchmark-harness-operational-lessons.md` - runtime failure lessons that
  shaped this contract.
- `benchmark-measurement-design-principles.md` - staged scoring and
  deterministic-first measurement principles.
- `lifecycle-testing-harness.md` - sibling empirical testing track.
