---
lore: 1
type: topic
summary: "A fix's regression test covers the report that prompted it, not the branch the fix introduced; after writing a fix, ask what states the fix made newly reachable and test in that new partition."
parent: lore-context.md
---

# A Fix's Regression Test Covers the Case That Prompted It, Not the Branch the Fix Added

Round 2 of the v46 review fixed a rename being stranded by a hold, and added a regression test for
exactly that rename. The fix's implementation introduced a **new branch**: two pathspec files live
at once, one for everything to commit and one for the subset still needing `git add`. Both were
written to the same fixed filename, so the second overwrote the first and the commit ran against
the narrower list — **silently dropping every already-staged path while reporting it as
committed.**

The regression test passed. It performed `git mv` and nothing else, which leaves nothing unstaged,
so it took the single-pathspec path and never exercised the branch the fix had just created. Round
3 found it by walking status codes (`R `, `RM`, ` D`, `D `, `??`, `AM`, `MM`) rather than by
re-running the scenario.

**Practice: after writing a fix, ask what states the *fix* made newly reachable, and test those —
not the report that prompted it.** Concretely: if the fix adds a branch, a second resource, or a
new partition of the inputs, the test must land in the **new** partition, and the mixed case is
usually the one nobody writes.

Two smaller rules from the same defect:

- A helper that writes to a **fixed** path cannot be called twice while both results are live.
  Require a distinct name per call rather than documenting the hazard.
- **Report the effect, not the intent.** The committed list now comes from reading the commit back
  (`git diff-tree --name-only -r HEAD`), so a hook adding or dropping paths cannot make the report
  lie. [a-demo-must-test-the-state-it-leaves-behind.md](a-demo-must-test-the-state-it-leaves-behind.md)
  is the same instinct one level up.

This is the testing corollary of
[a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md) and
[fix-defects-are-context-errors.md](fix-defects-are-context-errors.md): the review round catches
the fix's defect only because the fix's own test cannot.
