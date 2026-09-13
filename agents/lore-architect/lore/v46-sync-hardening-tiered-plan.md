---
lore: 1
type: topic
summary: "Active project state: lore-sync-hardening ships as one v46 release (tiering withdrawn); the deep cold review is done and applied, two review gates remain; spec is workdir/draft-lore-sync-hardening.md."
parent: lore-context.md
---

# v46 Lore-Sync Hardening — One Ship

**Everything ships as v46: all ten changes, no tiers, no v47** (user, 2026-09-13, superseding the
tiered plan the same day). The authoritative statement is § 0 of the spec.

The work was cut into tiers A/B/C earlier that day and briefly carried two different ship orders.
Both are withdrawn. The tiering was itself the problem: it put a version number in three places, a
marker that half the document assumed and half deferred, and a convention whose rules cited a
document in another tier — and the seams generated findings in two consecutive rounds
([tiering-a-reviewed-spec-creates-unreviewed-seams.md](tiering-a-reviewed-spec-creates-unreviewed-seams.md)).
**Tier vocabulary survives in the spec as review history, not as a plan.**

The authoritative artifacts are on disk, not here:

- **`workdir/draft-lore-sync-hardening.md`** — the spec: ten changes (C1–C8), five invariants,
  45 tests. § 0 is the ship map; § 14 the review history.
- **`workdir/what-to-improve.md`** — the standing ranked list, where this work sits first
  ([standing-improvement-list-practice.md](standing-improvement-list-practice.md)).

## Where it stands

**Seven review rounds. The deep unconstrained cold review is done and its findings are applied; two
gates remain.**

Round 7 was the deep pass the non-convergence rule prescribes — one cold reviewer, no assigned lens,
grounded in the live framework docs rather than the spec's claims about them. Verdict **BLOCK**,
thirteen findings (3 BLOCKER, 5 HIGH, 4 MEDIUM, 1 LOW), all verified before applying. The three
blockers are worth remembering as shapes, not just fixes:

- **A rollback with no correct target.** `reset --soft HEAD^` assumed this operation's commit is the
  tip; after a completed merge it is not, so the rollback would have dropped the merge and stranded
  the commit — the ratchet the rule exists to prevent, produced by the rule itself.
- **A failure table that was not exhaustive.** Plain non-fast-forward rejection had no row, and it is
  the only blocked outcome of the entire update path. An unlisted outcome means the executor guesses.
- **A fix cancelled by a condition left in place.** `update.md` states the zero-ahead gate in three
  places; removing one and keeping another left the push still skipped and the retry marker born
  stale. See [a-change-set-is-wider-than-its-diff.md](a-change-set-is-wider-than-its-diff.md).

**Still owed before implementation:** (1) a single reviewer over round 7's own amendments — every
round here that fixed something introduced something
([a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md)); and
(2) a first review of the stranded-publish marker, its canonical reader and C8, which were deferred
through every round and have never been examined as shipping work.

## Why the review kept not converging

Three three-lens rounds did not converge (14 → 16 → 13 findings, five BLOCK/BLOCKER verdicts), and
the reason dictated the response — see
[non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md).
**Each round's fixes were themselves unreviewed, so the spec was never implementation-ready as
written even when it read finished.** Rounds 4 and 5 changed the *unit* of review rather than the
rigor (a subset alone; then the tiering amendments) and found sixteen more findings between them —
[lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)
§ Change the unit. Round 7 changed the *instrument* instead: one deep unconstrained reviewer that
verified the spec's claims against the live docs rather than reading the spec on its own terms. It
found three blockers nine prior lens-passes had not, which is the case for that substitution when a
lens loop stalls.

Problem statement: [lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md).
Rejected alternative: [sidecar-publish-rejected.md](sidecar-publish-rejected.md).
Record the ship in [versioning-release-types.md](versioning-release-types.md) when it lands.
