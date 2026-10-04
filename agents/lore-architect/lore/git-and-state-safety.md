---
lore: 1
type: area
summary: "Rules for git operations and state files in automatic paths: ff-only granularity, no autostash, common-dir vs worktree state, hint-not-verdict state files, atomic writes and path identity."
parent: lore-context.md
---

# Git and State Safety

Git and state-file safety for automatic paths. Moved from `lore-context.md`; bodies live in the members.

## Standing rules

- **Git safety in automatic paths.** `git pull --ff-only` is **file-granular** — only divergence
  (the permanent one), a modified tracked file an incoming commit also changes, or an untracked
  collision block it; unrelated dirty and staged paths fast-forward fine
  (`git-ff-only-is-file-granular.md`). **Never `--autostash`**, `stash`, `--force` or `reset --hard`
  in an automatic path: autostash on a content collision exits 0 and writes conflict markers into the
  file, silently corrupting lore (`dont-autostash-it-reports-success-while-corrupting.md`). Repo-wide
  state goes at `--git-common-dir`, per-checkout at `--absolute-git-dir`
  (`git-common-dir-for-repo-wide-state.md`); a fault-recording state file is a **hint** to revalidate
  and self-clear, never sole evidence — nor is a notice printed before acting a record that the
  action happened (`a-state-file-is-a-hint-not-a-verdict.md`). **When a tool
  both saves and integrates, commit before you fetch** — every merge is then commit-to-commit, abort
  restores an exact prior state, and a conflict can be left *in progress* rather than defensively
  aborted (`commit-before-fetch-makes-a-merge-recoverable.md`). **A deny-list must exempt the
  operations that reduce what it guards against** — for a commit filter, every deletion, keyed on the
  operation and not on one encoding of it, or the guard blocks removal of the very file it objects to
  (`a-guard-must-not-block-its-own-remedy.md`). **`git -C <path>` need not act on `<path>`**: it
  escapes up to an enclosing repo, and follows `core.worktree` to an entirely different directory —
  one `rev-parse --show-toplevel` vs `realpath` comparison catches both
  (`git-dash-c-needs-toplevel-guard.md`).

## Members

- [git-common-dir-for-repo-wide-state.md](git-common-dir-for-repo-wide-state.md)
- [git-dash-c-needs-toplevel-guard.md](git-dash-c-needs-toplevel-guard.md)
- [git-ff-only-is-file-granular.md](git-ff-only-is-file-granular.md)
- [dont-autostash-it-reports-success-while-corrupting.md](dont-autostash-it-reports-success-while-corrupting.md)
- [commit-before-fetch-makes-a-merge-recoverable.md](commit-before-fetch-makes-a-merge-recoverable.md)
- [relative-git-refs-retarget-when-a-procedure-moves-head.md](relative-git-refs-retarget-when-a-procedure-moves-head.md)
- [prove-superseded-before-discarding-colliding-wip.md](prove-superseded-before-discarding-colliding-wip.md)
- [fold-feature-into-local-main-via-stash.md](fold-feature-into-local-main-via-stash.md)
- [a-state-file-is-a-hint-not-a-verdict.md](a-state-file-is-a-hint-not-a-verdict.md)
- [a-reported-error-is-not-proof-the-file-survived.md](a-reported-error-is-not-proof-the-file-survived.md)
- [a-guard-must-not-block-its-own-remedy.md](a-guard-must-not-block-its-own-remedy.md)
- [lock-claim-directory-creation-vs-contention.md](lock-claim-directory-creation-vs-contention.md)
- [macos-var-symlink-realpath-ambiguity.md](macos-var-symlink-realpath-ambiguity.md)
- [realpath-for-identity-logical-for-contract-shape.md](realpath-for-identity-logical-for-contract-shape.md)
- [live-system-state-validate-on-a-copy-first.md](live-system-state-validate-on-a-copy-first.md)
- [name-keyed-global-registry-cannot-answer-per-scope.md](name-keyed-global-registry-cannot-answer-per-scope.md)
- [release-commit-hash-from-tag.md](release-commit-hash-from-tag.md)
- [committed-artifacts-carry-relative-paths.md](committed-artifacts-carry-relative-paths.md)
- [lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md)
- [sidecar-publish-rejected.md](sidecar-publish-rejected.md)
