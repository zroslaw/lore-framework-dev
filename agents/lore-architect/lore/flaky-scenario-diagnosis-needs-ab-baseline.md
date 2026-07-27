# Diagnosing Flaky-Scenario Regressions Needs an A/B Baseline

Thin pointer — the full lesson lives in `graduated-verification-confidence.md` § Addendum: diagnosing
flakiness needs an A/B baseline, not just more samples (2026-07-27), where it's folded in as a concrete
sharpening of that principle rather than duplicated here.

**One-line version:** for a suspected regression that manifests as an *intermittent* engine-run
failure, a sample from the candidate alone can't distinguish "this version regressed" from "this
scenario is just flaky at this model tier" — confirm causation with a same-size-or-larger sample
against the **pre-change baseline** before concluding anything.

## Where this came from

Diagnosing `test_boot.py`'s flaky `test_05` scenario against the parked v31 branch (2026-07-27): one
failing run was wrongly declared "a definitive v31 regression," then three more mostly-failing runs
were wrongly treated as confirmation. Running the same scenario against the shipped v30 baseline
showed a similar failure rate, proving the flakiness was pre-existing and shared, not v31-specific.
The real bug was `macos-var-symlink-realpath-ambiguity.md`.

## See Also

- `graduated-verification-confidence.md` — the full lesson and its connection to the broader
  confidence-not-boolean principle.
- `macos-var-symlink-realpath-ambiguity.md` — the actual bug this A/B baseline uncovered.
- `v31-lr-core-parked-2026-07-25.md` — the concrete session this diagnosis happened in.
