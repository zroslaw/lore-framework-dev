---
lore: 1
type: topic
summary: "A relative git ref encodes a position, and a procedure with branching intermediate steps has no single position — record an absolute sha up front, guard the reset with is-ancestor, and never reset across a merge commit."
parent: lore-context.md
---

# A Relative Git Ref Silently Retargets When the Procedure Moves HEAD

`publish-lore.md`'s rollback said `git reset --soft HEAD^` to undo "this operation's commit". Correct
where it was written — and wrong by the time it runs, because an intermediate step (the merge-retry)
can put a **merge commit** on top first. `HEAD^` then means the merge's first parent, so the reset
drops the *merge* and leaves the original commit stranded: exactly the unpushed-local-commit ratchet
the rule existed to prevent, produced by the rule itself
([lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md)).

**The general shape: a relative ref (`HEAD^`, `HEAD~2`, `@{-1}`) encodes a position, and a procedure
with branching intermediate steps does not have one position.** The ref stays syntactically valid and
silently addresses a different commit — no error, no warning.

## Rules

- **Record an absolute sha at the start** — `PRE_HEAD=$(git rev-parse HEAD)` — and reset to that.
- **Guard the reset:** `git merge-base --is-ancestor "$PRE_HEAD" HEAD`. If the branch moved for
  reasons outside this operation, do not reset at all — a concurrent session may own the tip
  (`concurrent-session-committed-my-uncommitted-work.md`).
- **Refuse to reset across a merge commit.** Discarding someone else's merged work to undo your own
  commit is not a rollback; it is a history-destroying operation wearing a rollback's name — the same
  family as the automatic paths banned in
  [dont-autostash-it-reports-success-while-corrupting.md](dont-autostash-it-reports-success-while-corrupting.md).
- **A relative ref is still right where no intermediate step can move `HEAD`** — the same spec's
  post-commit verification uses `HEAD^` correctly. **Mark that in place**, or a later reader "fixes"
  the correct one to match the corrected one
  ([a-change-set-is-wider-than-its-diff.md](a-change-set-is-wider-than-its-diff.md)).

Found by the deep grounded review of the v46 spec
([review-grounding-beats-lens-novelty.md](review-grounding-beats-lens-novelty.md),
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md)). Related git-safety facts:
[git-ff-only-is-file-granular.md](git-ff-only-is-file-granular.md),
[git-common-dir-for-repo-wide-state.md](git-common-dir-for-repo-wide-state.md).
