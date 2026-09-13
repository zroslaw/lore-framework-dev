---
lore: 1
type: topic
summary: "When a review loop hits the round cap, classify findings by origin first; a stable core with a churning periphery means shrink what ships into tiers — then review each tier as the subset it actually ships as."
parent: lore-context.md
---

# Non-Convergence: Diagnose by Origin Before Reviewing Again

**When a review loop hits the round cap without a clean round, classify where the findings came from
before deciding what to do next.** Finding counts alone say nothing; origins do.

## The case (2026-09-13, lore-sync-hardening spec)

Three rounds over one design spec: 14 findings, then 16, then 13, with five BLOCK/BLOCKER verdicts
total. The counts suggest a document getting worse. Read by **origin**, the picture is completely
different:

- Rounds 1–2 found real flaws in the original design.
- Round 3's single BLOCK was a defect **round 2's own fix had introduced** — a conditional rollback
  whose exception was not merely wrong but never technically necessary. Fifth consecutive occurrence
  of the shape in
  [a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md).
- Across **nine reviewer passes, no lens ever attacked the core** (narrow staging, verify the commit,
  merge-and-retry, fail loudly). Every blocker landed in the elaboration around it.

## What that pattern means

Stable core, churning periphery, findings arriving from the previous round's own fixes: the document
has **outgrown what prose review can certify**. Another round buys another round of unreviewed fixes
([fix-defects-are-context-errors.md](fix-defects-are-context-errors.md) — the round cap guarantees
the last round's fixes ship unreviewed). The answer is to shrink what ships:

- **Tier A — the parts no lens ever touched.** Give it **one scoped round as the subset it will
  actually ship as** — "no further review" was wrong here, and a Tier-A-only round returned a BLOCK
  plus five findings that exist only because of the cut
  ([tiering-a-reviewed-spec-creates-unreviewed-seams.md](tiering-a-reviewed-spec-creates-unreviewed-seams.md)).
  Tier A usually holds the *detection* work, but that only argues for shipping it **first** if the
  later tiers preserve what it measures
  ([a-detection-tier-must-outlive-the-cure-it-measures.md](a-detection-tier-must-outlive-the-cure-it-measures.md)).
- **Tier B — the core.** One deep unconstrained cold reviewer, per
  [parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md)'s rule for a capped
  loop — not another three-lens round, because the lenses are spent and the remaining risk is
  **depth, not breadth**.
- **Tier C — whatever generated most of the findings.** Defer — but decide it from the rate that will
  exist *after* the cure, not the one Tier A can measure before it.

Worked instance: [v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).

## Corollary on lens ordering

The two lenses that found the largest holes here — **the operator's recovery experience** and **new
persistent state examined as state** — were both spent in the last rounds. **Spend them early.** Any
round that introduces a state file or a new stopping point should get those two lenses in the *same*
round, not two rounds later. This is the ordering half of
[lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md):
novelty decides *which* lens is worth a slot, life stage decides *which family*, and this decides
*when*.

Loop mechanics and the round cap itself: [trilens-loop-feature.md](trilens-loop-feature.md).
