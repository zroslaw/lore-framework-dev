# Quality benchmark v2 catalog (8 → 18 probes, 5 → 8 categories)

`tests/quality/probes.py` expanded from the v1 8-probe catalog to 18 probes across 8
categories, closing coverage gaps the v1 catalog had: with only 1-2 probes per category,
per-category scores were 0/50/100% noise, and whole probe types (synthesis, negative
knowledge, workdir-tool use) were untested.

## New categories

- **negative-knowledge** (P11, P12) — "we tried X, it failed, don't do it again" (a rolled-back
  Redis cache) and a banned library with a reason (pandas OOM-killed on prod-size dumps). A
  distinct, common lore payload from positive decisions; previously untested.
- **synthesis** (P14, P15) — tasks that need two needles from unrelated topics combined (an
  HTTP-client decision + a batching gotcha; an auth migration + a replica-snapshot schedule
  window). All v1 probes were single-needle.
- **workdir-tool** (P16) — lore points at an existing audited script in `workdir/tools/`; the
  agent should run it, not rewrite the logic. Tests the knowledge-vs-skills distinction
  (`knowledge-vs-skills-distinction.md`) empirically, not just the knowledge half.

Existing categories each gained a third variant: **decision-recall** gained a counter-default
probe (P9 — the recorded decision contradicts common best practice: no client-side retries,
since the API already retries server-side and duplicates cost money); **gotcha-avoidance**
gained a parametric probe (P10 — an exact figure, 40 req/min, must survive into code, not just
the concept); **abstention** gained a general-knowledge-tempted probe (P17 — asks the project's
target Python version, which models are tempted to guess from training data even though the
lore never recorded it); **knowledge-update** gained a dated-contradiction probe (P13 — two
topics disagree with no explicit "supersedes" marker; only the date and content should decide,
harder than P6's explicit-supersedes case); **implicit-adaptation** gained a second norm (P18 —
JSON-to-stdout/human-text-to-stderr, never hinted at in the task).

## Harness changes needed to support these

- `s1_target` may now be a list (synthesis probes) — S1 passes only if **every** listed file
  appears in the tool-input trace (`score_s1_from` in `test_quality.py`).
- Added `WORKDIR_FILES` (probes.py) + `build_quality_fixture(..., workdir_files=...)` (harness.py)
  — files written under `agents/<name>/workdir/` identically in both arms, so only the lore
  topic pointing at them (`records-export-tool.md`) differs across treatment/control.
- Scorecard's probe-name column was a fixed 24 chars; several v2 ids exceed that
  (`P17-abstention-general-knowledge` = 32 chars), corrupting alignment
  (`P11-failed-attempt-avoidancecontrol` ran together). Fixed by computing the column width
  from the actual data (`probe_w = max(24, max(len(probe id)) + 2)`) instead of a hardcoded
  constant — future long probe ids won't repeat this.

## Validation status

Offline: catalog lints clean (unique ids, valid regexes, every S1 target resolves to a real
needle, every needle is referenced by some probe, both arms produce identical file trees).

Real run: one full pass on cursor+composer-2.5 (ad-hoc shakeout runs default to
`LR_ENGINE=cursor`, see `benchmark-harness-operational-lessons.md` #3) — 0 errors, 0 invalid
judge cells, treatment 100% S3 (18/18), control 33.3% (6/18), behavior uplift +66.7 pts.

**Not ship-ready yet.** Two probes show a ceiling effect (control passes too, so they add zero
discrimination) — see `quality-benchmark-v2-known-probe-gaps.md`. That gap is still open as of
this writing; do not treat the v2 catalog as done until it's closed and re-run.

**Uncommitted.** Like the rest of `tests/quality/`, this is outside finalize's `agents/`
commit scope (same placement rule as the lifecycle harness) — needs its own manual commit.

## See Also

- `quality-benchmark-feature.md` — the benchmark this extends (cluster anchor).
- `quality-benchmark-v2-known-probe-gaps.md` — the two probes needing rework before ship.
- `quality-benchmark-tiers-proposal.md` — the queued regular/deep tier restructure; blocked on
  the known-probe-gaps fix landing first.
