---
lore: 1
type: topic
summary: "Tiering a reviewed spec is itself a change, and the subset has never been reviewed as a subset — run one scoped round over the tier you ship, watch the five seam shapes, and collapse the tiering once its seams produce findings twice."
parent: lore-context.md
---

# Tiering a Reviewed Spec Creates an Unreviewed Artifact at Every Seam

[non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md)
says that when a loop stalls, tier the spec: ship the untouched parts, give the core one deep
reviewer, defer what generated the findings. That still holds. What it missed: **the tiering is
itself a change, and the subset it carves out has never been reviewed as a subset.** Every prior
round read the whole document, in which the later tiers' artifacts exist by assumption.

## The case (v46 lore-sync-hardening, 2026-09-13)

Three rounds (14 → 16 → 13 findings) ended at the cap, and § 14a of the spec tiered it with
"Tier A — land first, **no further review**", on the strength of nine reviewer passes producing zero
findings against those four changes. I started implementing on that clearance. A round scoped to
**Tier A alone** then returned SHIP-WITH-FIXES / SHIP-WITH-FIXES / **BLOCK** — six real findings, two
of which would have shipped a user-visible regression:

- **C7 would have landed a convention the framework itself violates.** Its rule 1 forbids
  `git add <directory>`; `docs/finalize.md` § Phase 4 step 1 *is* `git -C <repo> add agents/`, and
  only C2 — a later tier — removes it. Two of C7's four rules also ended in `See publish-lore.md`, a
  document the later tier creates.
- **The R16 findings-catalog row contradicted § 4 of its own spec**, offering `merge && push` as the
  remedy where § 4 says in terms *"do not offer `git merge && git push`"*. Its safe branch was gated
  on marker data the bare tier never produces.

Neither defect exists in the whole spec. Both were **manufactured by the cut**.

## The rule

**After tiering, review the tier you are about to ship, as the artifact it will actually be.** It is
cheap — one scoped round — and it is not a fourth round of the same review, because the question has
changed from "is this design right?" to "does this subset stand alone?"
([lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)
§ Change the unit.)

## Where the seams are, in order of yield

1. Prose in the shipped tier citing a document a later tier creates.
2. A reporting or catalog row describing fields a later tier populates.
3. A rule the shipped tree does not yet comply with, because the fix is in a later tier.
4. Tests that cannot pass until a later tier lands.
5. A rollout section written for the whole ship (version, release notes, cache footer) with no answer
   for the partial one.

## Corollary — mark the boundary where the detail lives

Mark the tier boundary in the section that owns the detail, not only where the decision was recorded.
§ 7 carried a later-tier-only paragraph whose qualifier sat seven sections away in § 14a; an
implementer reads the section that owns the detail
([instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)).

And the tiering amendments are themselves fixes: a fifth round — one cold reviewer over my own
amendments — found ten more, two HIGH. One was mine and exactly the predicted shape: § 14 still
closed with *"the substitute for a fourth round is one deep unconstrained cold reviewer… before any
implementation begins"* while § 14a asserted readiness forty lines above. A new statement of a rule
left standing beside the old one, introduced while fixing something else
([fix-defects-are-context-errors.md](fix-defects-are-context-errors.md),
[a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md),
[single-canonical-source-discipline.md](single-canonical-source-discipline.md)).

## When to abandon the tiering rather than re-cut it

The seams kept reporting. After the Tier-A-only round above, **re-ordering the tiers (B before A)
immediately produced four more contradictions** — a version number stated in three places, a marker
half the document assumed and half deferred, a convention whose rules cited a document in another
tier. On 2026-09-13 the user withdrew the tiering entirely: **all ten changes ship as one v46.**

The lesson is not "don't tier". It is about the **second signal**: when the tier boundaries have
generated findings in *consecutive* rounds, the cut is not paying for itself, and **re-cutting
produces another unreviewed artifact rather than a cleaner one.** Collapse it.

Two markers that the cut costs more than it saves:

- **A decision has to be re-made per tier** — which version, which tests, which rollout section.
  Three rollout sections disagreeing about a version number is not a bookkeeping slip; it is the seam
  reporting itself.
- **A component keeps moving between tiers.** The conflict-classification rule moved from C to B
  because without it the cure had no defined behaviour — a sign the boundary was drawn *through* a
  mechanism rather than between mechanisms.

**When collapsing, do not delete the tier prose.** Mark it as review history and add one
authoritative ship map that explicitly wins over every section that contradicts it: the tier
vocabulary is load-bearing for the review record long after it stops being a plan, and the substantive
amendments each scoped round produced stay in force, because they were findings about the changes
themselves and not about the cut
([single-canonical-source-discipline.md](single-canonical-source-discipline.md)). Collapsing also
un-defers whatever the last tier held, which then owes a review it never had.

Worked instance and current ship state:
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md). Whether a first tier is worth
shipping first at all:
[a-detection-tier-must-outlive-the-cure-it-measures.md](a-detection-tier-must-outlive-the-cure-it-measures.md).
What to reach for instead, once the cut is gone and the loop is still stalled:
[review-grounding-beats-lens-novelty.md](review-grounding-beats-lens-novelty.md).
