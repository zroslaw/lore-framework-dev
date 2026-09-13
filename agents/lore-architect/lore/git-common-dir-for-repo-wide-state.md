---
lore: 1
type: topic
summary: "Repo-wide state belongs at git rev-parse --git-common-dir; per-checkout state at --absolute-git-dir. Getting it backwards hides state exactly where the worktree convention puts work."
parent: lore-context.md
---

# `--git-common-dir` for Repo-Wide State, `--absolute-git-dir` for Per-Checkout

**Repo-wide state goes in `git rev-parse --git-common-dir`; per-checkout state goes in
`--absolute-git-dir`.** Getting this backwards makes state invisible exactly where the framework's
worktree convention puts work ([worktrees-convention.md](worktrees-convention.md)).

Verified, for a repo with a linked worktree:

```text
main tree  --absolute-git-dir : <repo>/.git
worktree   --absolute-git-dir : <repo>/.git/worktrees/<slug>     # private to that checkout
both       --git-common-dir   : <repo>/.git                      # shared
```

A file written through `--absolute-git-dir` from inside a worktree is **not visible from the main
checkout at all**.

## The trap this came from

`preflight.py`'s `lr-last-pull` stamp deliberately uses `--absolute-git-dir`, and its comment says
why: a pull stamp *is* per-checkout, so it should follow the worktree
([auto-pull-mechanism.md](auto-pull-mechanism.md)). I copied that line for a **repo-wide fault
marker**, where it is wrong — a fault recorded from `.worktrees/<repo>/<slug>/` would have been
invisible to both of its readers, which scan the top-level repo path only.

The general trap: **copying an idiom from working code without re-deriving whether its reason
applies.** The idiom was right; the reason was not transferable. Same family as
[realpath-for-identity-logical-for-contract-shape.md](realpath-for-identity-logical-for-contract-shape.md)
— two nearly identical git invocations that answer different questions, where picking the wrong one
fails silently rather than loudly.

Design rules for the file itself:
[a-state-file-is-a-hint-not-a-verdict.md](a-state-file-is-a-hint-not-a-verdict.md).
