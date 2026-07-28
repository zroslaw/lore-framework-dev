# Fold feature worktree into local main via stash

When local `main` already carries unrelated uncommitted WIP, merge a finished feature branch by:

1. `git stash` the unrelated dirty paths on the top-level `main` checkout
2. `git merge` the feature branch into that checkout
3. `git stash pop`
4. `git worktree remove` the feature worktree

Do not commit or push the unrelated WIP as part of folding the feature. Do not merge into the feature worktree — keep the top-level checkout on the default branch (workspace invariant).

Used when folding `lore-architect/workspace-scratch-ignores` into local `main` while v33 follow-up edits were still dirty on `lore-framework` / `lore-framework-dev`.
