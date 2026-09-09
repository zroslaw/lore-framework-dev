---
lore: 1
type: topic
summary: "When a merge collides with local WIP, compute whether the incoming version contains it — extract with git show, diff untracked files directly, prove superset line by line with grep -qxF, back up before discarding."
parent: lore-context.md
---

# Prove WIP Superseded Before Discarding It in a Merge Collision

Merging the v45 branches, `lore-framework-dev` main held uncommitted WIP in
`framework-improvements-backlog.md`, and the incoming branch changed the same file. An untracked
`draft-lr-check-front-door.md` collided with a tracked file the branch adds.

This workspace runs concurrent sessions, including unattended ones, so **colliding WIP is not
necessarily mine and is never safe to assume disposable**. Blind `git stash` is also wrong here —
the stash stack is shared across worktrees, and another session can pop it.

## What worked, and is repeatable

1. **Extract the branch's version of each colliding file** with `git show <branch>:<path>` into a
   scratch file. Never compare against the branch by eye.
2. **Diff the untracked file directly.** The stray draft turned out byte-identical to the branch's
   tracked copy — a leftover from the same work, safe to delete because the merge restores identical
   content.
3. **Prove superset line by line, not by reading.** Take the WIP's added lines
   (`git diff | grep '^+'`), drop blanks, and assert each one appears in the branch version with
   `grep -qxF`. On the backlog, 28 of 30 matched; the 2 that did not were the branch's *improved*
   phrasings of the same sentences. That is a proof of supersession, not an impression of one.
4. **Back up to the scratchpad before discarding anyway**, and tell the user which files you touched
   and which you deliberately left alone.

## The general shape

When a mechanical check says "these collide", the real question is whether the incoming version
*contains* the local one — and that question has an exact answer. **Compute it.** An impression that
"the branch looks like it has this already" is how someone's work gets lost.

Leave every non-colliding dirty path untouched. Here that meant an unrelated advocate draft and a
`results/` directory.

## See Also

- [concurrent-session-committed-my-uncommitted-work.md](concurrent-session-committed-my-uncommitted-work.md)
  — why dirty state in this workspace has unknown authorship.
- [fold-feature-into-local-main-via-stash.md](fold-feature-into-local-main-via-stash.md) — the
  stash-around-the-merge move, and the case where it is *not* safe.
- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md) — same
  reflex: compute the fact before acting on the impression.
- [a-release-review-starts-with-git-status.md](a-release-review-starts-with-git-status.md) — the
  step that surfaces the collision in the first place.
