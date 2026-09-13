# V46 — session worktree ownership and finalization decision

Date: 2026-09-13. Status: user-selected design direction; not implemented.

This supersedes the earlier proposals on layout, eager Lore binding, engine ownership,
and required local Lore integration. Source/document repository publication defaults below
are recommendations pending the applicable repository workflow, not blanket merge authority.

## Ownership and layout

Lore's Python runtime creates, registers, recovers and verifies worktrees. Native engine
worktree management is not a dependency. Optional engine integration may expose the bound
paths to tools and review UI, but must not create a second competing lifecycle.

Use the user-selected workspace layout (an explicit change to the existing convention):

```
.worktree/<session-uuid>/lore-framework-dev/
.worktree/<session-uuid>/lore-agents/
.worktree/<session-uuid>/<source-or-document-repo>/
```

Ignore the container in workspace Git. Store a durable canonical repository identity,
primary path, worktree path, branch, repository kind and publication policy in the session
registry. Names aid inspection; Git identity is authoritative. Detect name collisions and
use stable unique repository keys rather than binding two repos with the same basename.

Boot/attach creates or recovers the agent's repository worktree before loading its context.
Another agent from the same repository and session reuses it. Another repository gets another
worktree. Source/document repositories bind before their first write. Bind the workspace repo
too if session work will modify its tracked files. Read-only inspection needs no worktree.

Repeated boots, resume, compaction and finalization retain the session UUID and bindings.
Independent sessions/forks receive independent identities. Workers explicitly inherit the
parent identity; sharing a worktree requires coordinated file ownership and serialized Git
operations. Parallel workers cannot edit the same files merely because their UUID is shared.

## Branches exist from the outset

A worktree is a checkout, not a separate repository needing import at finalization. Create
its named branch when binding it; that branch already belongs to the original repository's
shared Git database. Directory names and branch names need not match.

Lore branches may use `codex/lore/<session-uuid>` under this workspace's current branch-prefix
rule. Source branches follow the project's naming convention, e.g. `codex/feature-name`.
Record the base and intended target at binding. If a requested branch is already checked out
by another session, do not force-check it out or share its worktree: choose an isolated branch
under the project workflow, or request clarification if the exact branch is required.

## Finalization policy

Inventory every bound repository, including dirty/untracked files and unpublished commits.
Consider all changes; do not blindly stage secrets, generated files, unrelated edits or drafts.
Record an outcome for every repository; no cross-repository atomicity is promised.

For every participating Lore repository, finalization must attempt to commit the intended Lore
changes, integrate them into its local default branch and primary checkout, and push to the
configured remote target. Remote unavailability must not by itself prevent safe local integration.
Report local integration and remote delivery separately. A local-only result is pending remote
publication, not full success. Retry must not duplicate commits or lose the outgoing history.

Resolve integration in the isolated worktree against the latest known target. Protect primary
updates with a repository-scoped lock, recheck target identity and primary cleanliness, and
advance the primary only by a verified fast-forward. Never reset or overwrite primary WIP.
Reconcile again when the target moves; rejected pushes are retried through integration, never
force-pushed. Helper locks cover cooperating Lore processes, not arbitrary external Git writers;
external races remain a required detection/recovery test. The old prototype does not establish
this revised local-first publication protocol.

The finalizing session owns conflict resolution and validation. It must preserve and report a
blocked result if it cannot determine the correct meaning or safely update a dirty primary;
"always merge" is an obligation to attempt and account for delivery, not permission to guess
or discard another session's work. Reread integrated Lore before continuing the conversation.

For source/document repositories, use the repository's declared workflow. Recommended default:
commit the ready changes on the session's named feature branch, run the required checks, push
that branch, and create/update a PR or MR when the task or established workflow authorizes it.
Do not automatically merge into local or remote main. Direct integration is a separate explicit
policy. Missing publication authorization leaves a local checkpoint and an exact pending action.
Repository content type alone does not decide its delivery policy.

No worktree is removed simply because finalization completed. Later checkpoints reuse it;
explicit close must verify no dirty/untracked work, no undelivered history and no active operation.

## Required follow-through

Revise the main design's former primary-read-only invariant into controlled, verified primary
advancement; update the existing prototype and its tests before claiming implementation readiness.
Update boot, attach, write-routing, finalize, resume and workspace conventions together. Test
two repositories, same-repo agent reuse, crashes, repeated checkpoints, local-only delivery,
remote races, blocked primary updates, branch collisions and context restoration in all engines.

Python path resolution does not itself prevent unrestricted tools from editing primary paths.
Use write guards where supported; otherwise state the cooperative limitation explicitly.
