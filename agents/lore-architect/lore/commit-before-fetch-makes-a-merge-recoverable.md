---
lore: 1
type: topic
summary: "When a tool both saves local work and integrates remote work, commit first: every merge is then commit-to-commit, abort restores an exact prior state, and a conflict can be left in progress rather than aborted."
parent: lore-context.md
---

# Commit Before You Fetch, and the Merge Becomes Recoverable

When a tool has to both **save** local work and **integrate** remote work, the ordering decides
whether anything can be lost. Committing first makes every merge commit-to-commit rather than
commit-to-dirty-tree:

- nothing the user has is unsaved when remote content arrives;
- `git merge --abort` always restores an exact prior state;
- conflict markers only ever land on content already in the object database, so a conflict can be
  left **in progress** for a human or model to resolve, instead of being aborted defensively;
- `git pull --ff-only`'s file-granular failure modes stop applying
  ([git-ff-only-is-file-granular.md](git-ff-only-is-file-granular.md)).

This is the safety argument `/lr:workspace-sync` rests on
([workspace-sync-feature.md](workspace-sync-feature.md)), and it is why that command needs none of
the banned recovery operations — no `stash`, no `--autostash`, no `reset --hard`
([dont-autostash-it-reports-success-while-corrupting.md](dont-autostash-it-reports-success-while-corrupting.md)).

**The caveat that proves the rule:** any path deliberately *not* committed — a hold, or a source
repo that is never committed by design — stays dirty, so an incoming commit touching that path
still makes git decline the merge. That is a distinct outcome (`refused`), and it must be reported
and never pushed past, rather than folded into "failed".

**Generalizes past git:** when a procedure both persists and reconciles, persist first, so
reconciliation operates on two durable states.
