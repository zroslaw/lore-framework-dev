---
lore: 1
type: topic
summary: "Rejected design: publishing lore by building a commit on origin/<branch> with git plumbing and never moving local HEAD — it works, and it plants a fresh permanent pull blocker on every publish."
parent: lore-context.md
---

# Sidecar Publish — Rejected, Do Not Re-Propose

**The idea.** Never commit locally. Fetch, build a commit on top of `origin/<branch>` with git
plumbing against a temporary index (`GIT_INDEX_FILE` + `read-tree` + `hash-object -w` +
`update-index --cacheinfo` + `write-tree` + `commit-tree`), push it, retry against the new head. It
demonstrably works: I published a lore topic to a live remote from a repo that was simultaneously
diverged, dirty, and holding an untracked collision.

It was still rejected, on three independent grounds.

1. **`git commit -- <paths>` already builds a temporary index internally.** That was the single
   property the plumbing existed to provide, and it is available in one porcelain command with a
   documented manual fallback.
2. **"Never move local HEAD" is the bug, not the feature.** After a sidecar push the session's own
   new file is still untracked locally *and* now exists in the remote commit (an untracked
   collision); the rewritten `lore-context.md` is still locally modified. Every publish plants a
   fresh **permanent** pull blocker — local HEAD freezes on day one while the remote advances
   forever ([git-ff-only-is-file-granular.md](git-ff-only-is-file-granular.md)).
3. **The plumbing loses fidelity.** Hardcoded `100644` silently demotes executables and follows
   symlinks, `--cacheinfo` cannot express a deletion, and `commit-tree` ignores `commit.gpgsign`.

## What it is worth remembering for

The general lesson outlives the case: **the clever mechanism solved a problem that had a boring
solution**, and the demo that "validated" it tested only the push — see
[a-demo-must-test-the-state-it-leaves-behind.md](a-demo-must-test-the-state-it-leaves-behind.md),
which this case produced.

Context: [lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md),
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).
