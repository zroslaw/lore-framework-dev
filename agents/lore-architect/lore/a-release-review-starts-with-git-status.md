---
lore: 1
type: topic
summary: "Run git status on every repo before the diff and before the notes — a dirty tree means the review's subject does not exist yet, and uncommitted fixes are the most invisible form of ungated work."
parent: lore-context.md
---

# A Release Review Starts With `git status`, Not With the Diff

Asked to review the v45 release, I read the release notes and the committed diff first. The working
tree was dirty — four files in the framework worktree, one in the paired dev worktree — and those
uncommitted changes carried **three real defect fixes, each with its own regression test**.

So the tree I was reviewing was not the tree that would have shipped, and no gate result belonged to
either one. Every count in the Verification section was measured against a third state.

**Make `git status` on every repo the first command of a release review**, ahead of the diff and
ahead of the notes. A dirty tree is not a detail to note in passing; it means the review's subject
does not exist yet, and it changes what the review is *for* — the first finding becomes "commit
this", not "here is a bug".

## Corollary for authoring, not just reviewing

Uncommitted fixes are the most invisible form of ungated work. A post-gate *commit* at least leaves
a SHA that can be compared against the gate's recorded state. A dirty file leaves nothing, and
`git log` looks clean.

## See Also

- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) —
  the general rule this instantiates: a gate result belongs to a specific artifact state. This is
  its cheapest detector.
- [a-release-record-goes-stale-while-you-fix-it.md](a-release-record-goes-stale-while-you-fix-it.md)
  — why the counts in the notes were measured against a state that no longer existed.
- [concurrent-session-committed-my-uncommitted-work.md](concurrent-session-committed-my-uncommitted-work.md)
  — in this workspace a dirty file is not even reliably *mine*, which raises the cost of skipping
  the check.
- [blast-radius-audit-when-a-gate-is-waived.md](blast-radius-audit-when-a-gate-is-waived.md) — the
  audit that follows once the subject tree is settled.
