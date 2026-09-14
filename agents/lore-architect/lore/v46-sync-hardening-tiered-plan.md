---
lore: 1
type: topic
summary: "Unversioned, deferred design for Lore-owned session worktrees: eager boot binding, local Lore integration and push, evidence limits and open work. It did not ship as v46 — v46 was spent on workspace-sync."
parent: lore-context.md
---

# Session-Worktree Lore-Sync Hardening — Unfinished, Unversioned Design

**DESIGN UNFINISHED — not ready for implementation, and no longer carrying a version number.**
The user paused the difficult design session on 2026-09-13 to preserve findings and continue later.
**This design did not ship.** v46 was spent instead on `/lr:workspace-sync`
([workspace-sync-feature.md](workspace-sync-feature.md)), released 2026-09-13 as tag
`lr--v1.46.0`, so production is at v46 and the label "v46" here is historical — treat the design as
**unversioned and deferred** until it is scheduled against a real release. All its changes remain
one release; the A/B/C rollout was withdrawn. The filename is retained because links point at it,
the same discipline this topic already applied to that withdrawal.

**The two are complements, not alternatives.** This design *prevents* the divergence states;
`workspace-sync` *resolves* them after the fact. Shipping the repair does not reduce the case for
the prevention, and the repair stays worth having once prevention lands
([lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md)). No
worktree lifecycle change has shipped: `.worktrees/<repo>/<slug>/` is still the installed
convention.

## Latest decision and source precedence

Read [the session worktree decision](../workdir/v46-session-worktree-decision.md) first. It is the
latest user-selected amendment and supersedes conflicting sections of
[the earlier draft](../workdir/draft-lore-sync-hardening.md): lazy first-write Lore binding,
repo-first layout, reliance on native engine lifecycle, and the primary-read-only publication
invariant. The draft and [reference prototype](../workdir/v46-prototype/README.md) retain useful
mechanics and evidence, but need redesign, not just caller integration.

Lore's Python runtime owns creation, durable registration, recovery and verification. Boot/attach
binds an agent's repository **before loading context**; agents in the same session and repository
reuse that worktree. Other repositories bind before their first write, including the workspace
repository if its tracked files will change. Read-only inspection needs no worktree.

The selected layout is `.worktree/<session-uuid>/<repo>/`: singular, session-first. This is a
**proposed replacement** for the installed `.worktrees/<repo>/<slug>/` convention, not current
runtime behavior. Canonical Git identity, not the display basename, determines repository reuse;
colliding names require distinct stable keys. Keep the durable session UUID separate from each
finalization/checkpoint UUID. Resume, compaction and repeated finalizations retain bindings;
independent sessions/forks have separate identities. Workers inherit explicitly and still need
coordinated file ownership and serialized Git operations. Finalization does not remove worktrees;
cleanup is explicit and must prove no remaining work, delivery or active operation.

A worktree checks out a branch already belonging to the original repository's shared Git database.
Create that branch at binding; there is no branch-import step at finalization. Record base, target
and publication policy. Do not force a branch already checked out by another session.

## Publication policy and remaining decisions

Inventory every bound repository and account for intended changes and unpublished history; never
blindly stage all files. For each participating Lore repository, attempt safe local default-branch
integration and remote push. Report local integration separately from remote delivery: offline
local integration leaves pending publication, not full success. Retry must preserve outgoing
history without duplicating work. There is no cross-repository atomicity promise.

Resolve integration in isolation, protect cooperating writers with a repository lock, recheck
identity and cleanliness, and advance the primary only by a verified fast-forward. Never overwrite
primary WIP or force-push. The finalizing session owns conflict resolution and validation, but
ambiguous semantics or unsafe primary state must leave an explicit blocked result. Locks do not
control arbitrary external Git writers; detecting and recovering from those races is open work.
Reread integrated Lore before continuing the session.

Source/document repository publication remains **workflow-dependent and unresolved as a universal
default**. The recommendation is a named feature branch from binding, then commit, required checks,
push and PR/MR under the project's authority, without automatic main integration. Content type
alone does not grant publication authority. Preserve a checkpoint and exact pending action where
that authority or policy is missing.

Native worktrees exist in Claude Code, Codex and Cursor, based on official documentation and
installed CLI help checked in this session; no complete three-engine lifecycle trial was run.
[Dated engine findings](../workdir/v46-native-worktree-engine-check.md) preserve sources and scope.
Native UI integration may expose Lore's bound paths, but cannot own a competing lifecycle.
Multi-root editing does not prove automatic isolation of independent nested repositories. A
worktree of the parent workspace does not create worktrees of its child repositories. A registry
or path reminder also does not enforce write isolation against unrestricted tools; guards and
explicit cooperative limitations still need design and tests.

## Evidence and boundaries

The 2026-09-13 code-grounded review reproduced shared-checkout soft reset removing another session's
commit, a merge commit absorbing foreign staged work, narrow commits publishing unrelated outgoing
ancestors, bare push succeeding at an unintended destination, and marker predicates erasing
still-blocked publication evidence. A common-directory marker also conflicted with branch-local
cleanup. The previous seven-round design and provenance remain in Git history at `ebaed0f`.

Isolation avoids shared-checkout authoring and rollback; it does not magically handle old sessions
already holding primary paths. This is distinct from the rejected dirty-primary sidecar publisher,
which copied files and left pull blockers behind. Preserve the publish → primary read → next-session
verification requirement and status reads that never acknowledge delivery or erase evidence.

The earlier prototype's 41 checks and five detected mutations are evidence for that prototype,
**not validation of the later boot-bound, repeated-checkpoint, local-first design**. Preserve exact
artifact/test dispositions in `workdir/v46-prototype/`. The lock-first exploration is unchosen
history, not current instructions.

Resume with stable UUID acquisition/recovery, boot/attach and write routing, crash recovery,
repeated checkpoints, source workflow and branch collisions, local-only delivery, concurrent
primary/remote changes, dirty-primary blocking, cleanup and tool guards. Update conventions,
procedures and prototype together, then exercise two repositories, same-repo agent reuse and
context restoration across all three engines. Do not infer release readiness from earlier checks.
