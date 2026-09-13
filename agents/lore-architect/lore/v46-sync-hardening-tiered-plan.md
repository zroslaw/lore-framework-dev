---
lore: 1
type: topic
summary: "V46 current design: one worktree per writing session, deterministic publication, per-session durable outcomes; reference prototype in workdir/v46-prototype, production integration still outstanding."
parent: lore-context.md
---

# V46 Lore-Sync Hardening — Current Design

All changes remain one v46 release. The A/B/C rollout was withdrawn; the filename is retained to
preserve existing links.

The current contract is `workdir/draft-lore-sync-hardening.md`; the reference implementation,
adversarial tests and their limitations are in `workdir/v46-prototype/README.md`. Production
integration is a separate remaining step, enumerated in the spec's § 9.

The 2026-09-13 code-grounded review reproduced shared-checkout rollback removing another session's
commit, a merge commit absorbing unrelated staged work, narrow update commits publishing unrelated
ancestors, bare push succeeding at the wrong destination, and marker predicates erasing evidence
of still-blocked publication. A common-directory marker also conflicted with branch-local cleanup.
The previous seven-round design and its provenance remain in Git history at `ebaed0f`.

The revised design uses a private worktree **before the first session write**, exact destination
publication, and durable per-operation outcomes. It eliminates shared-checkout rollback; pending
private commits cannot block primary boot pulls. A status read never acknowledges delivery or
deletes records. Primary synchronization and private publication health are separate facts.

This does not revive the rejected sidecar publisher: that mechanism copied dirty primary files
and left pull blockers behind; the new mechanism authors only in the private worktree and must
pass publish → primary pull → next-session tests. Existing dirty primary work still needs explicit
adoption; installing the helper cannot isolate old sessions that already hold primary paths.

The prototype validates mechanics, not production caller integration, cross-engine fidelity,
legacy migration or release readiness. Do not turn prototype test counts into a ship-gate result.
