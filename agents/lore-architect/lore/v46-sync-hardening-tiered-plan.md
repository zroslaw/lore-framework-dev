---
lore: 1
type: topic
summary: "Active project state: the v46 lore-sync-hardening work ships in three tiers (A land now, B one deep cold review, C deferred); the authoritative spec is workdir/draft-lore-sync-hardening.md."
parent: lore-context.md
---

# v46 Lore-Sync Hardening — Tiered Shipping Plan

**Decision, 2026-09-13 (user-approved): the v46 lore-sync-hardening work ships in three tiers, and
implementation does not start from the spec as it stands.**

The authoritative artifacts are on disk, not here — this topic is the pointer and the ordering
decision:

- **`workdir/draft-lore-sync-hardening.md`** — the spec: ten changes (C1–C8), five invariants, 34
  tests. § 14a carries this ordering; § 14 the full review history.
- **`workdir/what-to-improve.md`** — the standing ranked list, where this work sits first
  ([standing-improvement-list-practice.md](standing-improvement-list-practice.md)).

## The tiers

- **Tier A — land first, no further review.** C5 (refresh TTL keys on `last-success`, not
  `last-attempt`), C6 (`workspace-pull` Phase 0 stops pre-refusing on a dirty tree), C7
  (`conventions.md` § Tooling: Git Safety), and **C4 in bare form** — R16 reporting agent-repo
  ahead/behind with no marker dependency. Zero findings against these across nine reviewer passes.
  Bare R16 is also the **instrument**: it measures how often divergence actually happens, which is
  what should decide Tier C.
- **Tier B — the cure.** C1 (`docs/publish-lore.md`), C2 (finalize Phase 4), C3 (update publication
  in `no-merge` mode), C3a (`resolve-conflicts.md` retargeted). **Run one deep unconstrained cold
  reviewer over Tier B alone before implementing.**
- **Tier C — deferred by design.** The stranded-publish marker, C8 (`lrb status`), and the
  Ours/Foreign conflict classification. These produced most of the findings in every round; decide
  from Tier A's data whether to build them at all.

## Why it is tiered rather than reviewed again

Three review rounds did not converge (14 → 16 → 13 findings, five BLOCK/BLOCKER verdicts), and the
reason dictated the response — see
[non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md).
**Round 3's fixes are themselves unreviewed, so the spec is not implementation-ready as written even
though it reads finished.**

Problem statement: [lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md).
Rejected alternative: [sidecar-publish-rejected.md](sidecar-publish-rejected.md).
Record the ship in [versioning-release-types.md](versioning-release-types.md) when it lands.
