---
lore: 1
type: topic
summary: "Before blaming a change for a red lifecycle module, read that module's verdicts across the retained results/*/summary.json history — pre-existing flakes separate from real regressions in seconds, ahead of any transcript reading."
parent: lore-context.md
---

# Triage a Red Module Against Its Own Result History

**The retained `results/` tree is the cheapest triage instrument the harness has, and it is the one
I nearly skipped.** Run this comparison *before* reading transcripts, let alone before editing code.

On the v44 run, four Claude modules went red. Reading `results/*/summary.json` across the previous
ten runs separated them in seconds:

| module | prior verdicts on the pre-change checkout | verdict |
|---|---|---|
| `test_boot` | failed, failed, failed, ok, failed, ok, ok | pre-existing flake |
| `test_consult_attach` | failed, failed, failed, ok, ok, ok, ok | pre-existing flake |
| `test_finalize` | failed, failed, ok, failed, failed, ok, ok | pre-existing flake |
| `test_repo_workspace` | ok, ok, ok, ok, failed | **real, attributable** |

Three of four reds were noise. Only the fourth was worth a transcript.

## Two supporting techniques

**A/B against the previous framework tree.** `LR_FRAMEWORK_DIR=<old checkout>` plus `--test-filter`
settles "is this my change?" definitively — `test_05` failed identically on v43. This is the same
instrument as
[prove-a-new-test-red-against-the-previous-tag.md](prove-a-new-test-red-against-the-previous-tag.md),
pointed at a failure instead of at a new assertion.

**A failure that moves between runs carries no information.** `test_05` failed at three different
assertions across three runs — no stamp / stamp-no-commit / commit-no-push, the exact distribution
its own source comment documents. I briefly attributed the movement to a fix of mine; it was
non-determinism. **A scenario asserting the end state of a long model-driven chain fails at whatever
step the model stopped at, and cannot certify anything until it is restructured.** `test_05`,
`test_08` and `test_12` are all this shape today; `test_08` additionally reads the wrong capture
surface ([transcript-vs-final-message-assertions.md](transcript-vs-final-message-assertions.md)).

## The rule

An assertion message names what was observed, never why — so a red list is a hypothesis. Rank the
evidence by cost: result history, then A/B against the old tree, then stored transcripts, then a
fresh engine probe. Only the last one costs money, and it is almost never the one that answers the
question.

## See Also

- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md) — the
  parent reflex: verify state, and verify *which* bug, before acting.
- [a-red-test-may-be-asserting-a-true-fact.md](a-red-test-may-be-asserting-a-true-fact.md) — the
  other direction: the red side may be the correct one.
- [v31-lifecycle-rerun-partial-green-2026-07-27.md](v31-lifecycle-rerun-partial-green-2026-07-27.md)
  — the run where four of six failures were misread on first pass.
- [lifecycle-harness-exit-code-is-not-a-verdict.md](lifecycle-harness-exit-code-is-not-a-verdict.md)
  — read the summary block, not the exit code, to get the red list in the first place.
- [lifecycle-testing-harness.md](lifecycle-testing-harness.md) — the harness and its retained
  artifacts.
