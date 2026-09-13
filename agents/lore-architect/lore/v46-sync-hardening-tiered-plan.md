---
lore: 1
type: topic
summary: "Active project state: v46 lore-sync-hardening is tiered (A, B, C), but nothing ships until Tier B is designed to completion and Tier C decided; the authoritative spec is workdir/draft-lore-sync-hardening.md."
parent: lore-context.md
---

# v46 Lore-Sync Hardening — Tiered Shipping Plan

**The work is tiered; the shipping order is not "Tier A first."** Decision, 2026-09-13
(user-directed, superseding § 14a of the spec): **design Tier B to completion and decide Tier C
before shipping anything.** Tier B needs its deep unconstrained cold review regardless, and holding
Tier A costs almost nothing — see
[a-detection-tier-must-outlive-the-cure-it-measures.md](a-detection-tier-must-outlive-the-cure-it-measures.md)
for why the "ship the detector first to get data" argument does not survive: Tier B removes the very
causes bare R16 would be counting.

The authoritative artifacts are on disk, not here — this topic is the pointer and the ordering
decision:

- **`workdir/draft-lore-sync-hardening.md`** — the spec: ten changes (C1–C8), five invariants, 34
  tests. § 14 carries the full review history; § 14a's *tiering* stands, its *ordering* does not.
- **`workdir/what-to-improve.md`** — the standing ranked list, where this work sits first
  ([standing-improvement-list-practice.md](standing-improvement-list-practice.md)).

## The tiers

- **Tier A — small, safe, independently useful; held, not shipped.** C5 (refresh TTL keys on
  `last-success`, not `last-attempt`), C6 (`workspace-pull` Phase 0 stops pre-refusing on a dirty
  tree), C7 (`conventions.md` § Tooling: Git Safety), and **C4 in bare form** — R16 reporting
  agent-repo ahead/behind with no marker dependency. Nine whole-spec reviewer passes found nothing
  here; a round scoped to **Tier A alone** then found six, including a BLOCK
  ([tiering-a-reviewed-spec-creates-unreviewed-seams.md](tiering-a-reviewed-spec-creates-unreviewed-seams.md)).
  C5's `retry_floor` was one of them —
  [a-rate-floor-is-wrong-in-both-directions.md](a-rate-floor-is-wrong-in-both-directions.md).
  R16 is user-facing and its wording and severity have already been rewritten twice at the tier
  seams; shipping it early would churn a warning users start to rely on.
- **Tier B — the cure.** C1 (`docs/publish-lore.md`), C2 (finalize Phase 4), C3 (update publication
  in `no-merge` mode), C3a (`resolve-conflicts.md` retargeted). **Design it to completion, then one
  deep unconstrained cold reviewer before implementing.**
- **Tier C — deferred by design.** The stranded-publish marker, C8 (`lrb status`), and the
  Ours/Foreign conflict classification. These produced most of the findings in every round. Decide
  from the divergence rate that exists *after* Tier B, not from anything Tier A could measure before
  it.

## Why it is tiered rather than reviewed again

Three review rounds did not converge (14 → 16 → 13 findings, five BLOCK/BLOCKER verdicts), and the
reason dictated the response — see
[non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md).
**Round 3's fixes are themselves unreviewed, so the spec is not implementation-ready as written even
though it reads finished.** Rounds 4 and 5 changed the *unit* of review rather than the rigor (Tier A
alone; then my own tiering amendments) and found sixteen more findings between them —
[lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)
§ Change the unit.

Problem statement: [lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md).
Rejected alternative: [sidecar-publish-rejected.md](sidecar-publish-rejected.md).
Record the ship in [versioning-release-types.md](versioning-release-types.md) when it lands.
