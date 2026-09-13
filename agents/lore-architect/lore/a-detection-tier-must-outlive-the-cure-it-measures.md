---
lore: 1
type: topic
summary: "\"Ship the detector first for data\" only holds if the later change preserves the population being measured; if the cure removes the causes, the measurement expires when the cure lands."
parent: lore-context.md
---

# A Detection Tier Must Outlive the Cure It Measures

[non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md)
says a first tier usually includes the *detection* work, "which then produces the evidence the rest of
the design needs." That instrumentation argument is conditional, and I stated it unconditionally.

**The test to apply to any "ship the detector first" plan: does the later change alter the population
being measured?** If it does, the measurement expires when the cure lands, and instrumentation is not
a reason to ship the detector first — at best it is a reason the detector is cheap.

## The case (v46 lore-sync-hardening, 2026-09-13)

§ 14a justified shipping Tier A before Tier B partly as instrumentation: bare R16 "starts measuring
how often divergence actually occurs", and that data "should decide whether Tier C is built at all".
The user challenged the ordering — *why implement A before finalizing the design?* — and the argument
did not survive the question.

R16 in Tier A measures divergence **under the regime Tier B exists to replace**. The framework itself
manufactures that divergence — finalize stages and pushes without merging, conflict resolution gives
up leaving a commit, update's push gate refuses when already ahead
([lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md)) — and Tier B
removes those causes. So Tier A's numbers quantify a problem already known qualitatively and say
nothing about the residual rate *after* the cure, which is the only rate that decides whether Tier C's
machinery is worth building.

What remained true of Tier A was that it is small, safe and independently useful — arguments for it
being **inexpensive**, not for it being **first**. Against that sat a real cost: R16 is user-facing,
and the tier seams had already forced two rewrites of its wording and severity
([tiering-a-reviewed-spec-creates-unreviewed-seams.md](tiering-a-reviewed-spec-creates-unreviewed-seams.md)),
so shipping it early risks churning a warning users have begun to rely on.

**Decision, 2026-09-13 (user-directed):** design the cure to completion before shipping anything —
holding the detection work cost almost nothing. Later the same day the user withdrew the tiering
altogether and **all ten changes ship as one v46**, which settles this instance by removing the
ordering question
([tiering-a-reviewed-spec-creates-unreviewed-seams.md](tiering-a-reviewed-spec-creates-unreviewed-seams.md)
§ When to abandon the tiering). The test above is unaffected: it applies to any "ship the detector
first" plan, and here it is what showed the instrumentation argument was empty before the cut was
abandoned for independent reasons. Current ship state:
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).

Sibling shape: a guard or metric keyed on a state the design is about to change selects a population
that will not exist —
[guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md),
[measurement-records-name-their-environment.md](measurement-records-name-their-environment.md).
