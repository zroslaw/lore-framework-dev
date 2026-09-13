---
lore: 1
type: topic
summary: "Lore agent repos go stale because three shipped framework paths manufacture divergence (local commit + advanced remote) and nothing reports it; the correct publish pattern already exists in the framework's two rarest operations."
parent: lore-context.md
---

# Lore Repo Divergence Is Self-Inflicted

Lore agent repos go stale because **the framework manufactures the state that breaks them** — not
because of git, and not because of user error. Established by reading the shipped v45 code, not
inferred.

The permanent failure is **divergence**: a local unpushed commit plus an advanced remote makes every
later boot's `pull --ff-only` fail forever, and boot continues in degraded mode on stale lore
(`agent-boot.md` § Act on the report). It is the only one of the three block states that never
self-heals ([git-ff-only-is-file-granular.md](git-ff-only-is-file-granular.md)).

## The three shipped paths that create it

- **`finalize.md` Phase 4** stages `git add agents/` — the whole tree, not the session's write-set —
  then commits and pushes **without fetching or merging first**. Under concurrency it also sweeps
  another session's in-progress edits into an unrelated commit, which is the mechanism already
  recorded in
  [concurrent-session-committed-my-uncommitted-work.md](concurrent-session-committed-my-uncommitted-work.md).
- **`resolve-conflicts.md`** retries three times on push rejection, then gives up **leaving the
  commit local**.
- **`update.md` § Automatic Publication** refuses to push when the branch is already ahead —
  precisely the diverged state — and keeps the update commit local, adding one more.

## Why nobody sees it

`repo_scan.py` computes no ahead/behind for agent repos, so `/lr:check` is blind to the only
permanent failure in the system ([unified-check-front-door.md](unified-check-front-door.md)).
`workspace_refresh.py:needs_refresh` compounds it by keying the 16h TTL on `last-attempt` rather than
`last-success`, so a failing refresh still resets its own clock
([workspace-auto-refresh-design.md](workspace-auto-refresh-design.md)).

## The pattern already exists, in the coldest code

The correct publish pattern — recorded write-set, explicit-pathspec staging, post-commit path
verification, preconditions re-resolved immediately before push — is **fully specified already**, in
`update.md` § Automatic Publication and `workspace-push.md` Step 4. The framework applied it to its
two **rarest** operations while the most frequent write path (finalize) has none of it.

**Generalizable move:** when a subsystem keeps failing, check whether the right pattern already
exists somewhere colder in the codebase before designing a new one. The clever alternative
considered here was rejected on exactly that ground —
[sidecar-publish-rejected.md](sidecar-publish-rejected.md).

Design and shipping order:
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).
