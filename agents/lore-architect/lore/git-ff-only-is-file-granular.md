---
lore: 1
type: topic
summary: "git pull --ff-only is file-granular: only divergence, a modified tracked file an incoming commit touches, or an untracked collision block it — and shipped code gates on the wrong one."
parent: lore-context.md
---

# `git pull --ff-only` Is File-Granular, Not Repo-Granular

`git pull --ff-only` does **not** fail because "the repo has uncommitted files." Only three states
block it. Verified directly against git 2.50.1 in a scratch repo, not read from documentation:

1. **Divergence** — a local unpushed commit *and* an advanced remote → `fatal: Not possible to
   fast-forward`. **Permanent; never self-heals.** The dirty state of the tree is irrelevant here.
2. **A modified tracked file that an incoming commit also changes** → `Please commit your changes or
   stash them before you merge`. Byte-identical content does not help: git compares index-vs-HEAD,
   so an identical local edit is still a local modification.
3. **An untracked file at a path an incoming commit creates** → `The following untracked working
   tree files would be overwritten by merge`.

Everything else fast-forwards cleanly, local edits preserved byte-for-byte: dirty tracked files at
unrelated paths, untracked files at unrelated paths, and **staged** changes at unrelated paths. A
local commit with an unmoved remote is simply `Already up to date`.

## Operational consequence

Before designing around "the dirty tree blocks us," establish **which of the three states is
actually occurring**. They have different causes and different fixes, and only the first is
permanent — which is why lore-repo staleness is a divergence problem, not a dirtiness problem
([lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md)).

It also means `--ff-only` is safe to run against a dirty tree: it refuses loudly in exactly the two
cases where it would clobber, and otherwise leaves the working tree untouched. That is the invariant
the boot and merge auto-pulls rest on ([auto-pull-mechanism.md](auto-pull-mechanism.md)).

**Shipped bug, v45.** `scripts/workspace-pull` Phase 0 skips the workspace-root pull whenever *any*
tracked file is dirty, on a code comment asserting `--ff-only` "would refuse to clobber it anyway."
That assertion is false, and the correct rule is stated 30 lines away in
`workspace_refresh.py:_blocked_repos`. Two derivations of one git fact, and the wrong one gates —
[single-canonical-source-discipline.md](single-canonical-source-discipline.md) failing in code.
Fix tracked as C6 in
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).

See also
[dont-autostash-it-reports-success-while-corrupting.md](dont-autostash-it-reports-success-while-corrupting.md)
(why the refusal must stay a refusal) and
[verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md).
