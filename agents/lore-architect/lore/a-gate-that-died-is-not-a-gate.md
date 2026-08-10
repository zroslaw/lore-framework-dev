---
lore: 1
type: topic
summary: "A gate that was launched and never reported is neither a pass nor a waiver — record it as 'did not run', and don't retry a structural failure."
parent: lore-context.md
---

# A Gate That Died Is Not a Gate

Extends [gate-waiver-is-a-record.md](gate-waiver-is-a-record.md) with a third disposition.

**Three dispositions. A ship record should name which applies to each gate:**

- **Passed** — ran to completion against a named artifact state.
- **Waived** — the user closed it deliberately; the waiver *is* the record.
- **Did not run** — launched and never reported, or never launched. Costs exactly the same as no gate.

## The instance (v37, 2026-08-10)

`/lr:trilens-loop` round 1 ran cleanly: three independent lenses, 11 findings, all applied, none
declined. Round 2 was launched with three fresh reviewers, and **all three died before reporting**
when the account hit its monthly spend limit. The honest ship record is "one clean review round,
not two" — which is what `versioning-release-types.md`'s v37 entry says.

The loop's own stopping rules already cover this ("a round where a lens did not actually report is
not a clean round for that lens… never bank a silent round as clean"). Living it added two things
the rule does not say out loud:

**The failure shape is deceptive.** The reviewers surfaced as *idle*, which to a casual reading is
indistinguishable from "finished and found nothing". A dead agent and a satisfied agent look alike
from the outside. So the check must be **"did it report?"**, never "did it complain?".

**Distinguish transient failure from structural before retrying.** The loop grants one retry that
does not count against the round ceiling — worth taking for a flake. An account spend limit will
fail identically on retry, so retrying it is theater. Name the lenses that never reported and stop.

## Alive but silent — ask before banking the round (v37, 2026-08-10)

The three-round rerun over the whole v37 release produced the *other* half of this shape. Two of nine
lenses (round 2 executability, round 3 doc coherence) signalled idle without ever sending findings.
Both had done the work: a single follow-up asking for "the findings list and your one overall verdict,
or say explicitly you found nothing" produced full reports, and one of them contained the round's
`BLOCKER`.

**An idle notification is not a report.** Before treating a round as complete, check that every lens
returned findings *and* a verdict, and re-request the missing ones once. That re-request does not count
against the three-round ceiling. Banking a silent lens as a clean lens is how a loop reports "3 rounds,
all clear" on 7 rounds of evidence.

This is cheap to tell apart from the spend-limit case above — **ask**. A dead reviewer cannot answer;
a quiet one answers immediately. The distinction matters because the two need opposite responses:
retrying a structural failure is theater, while re-asking a live reviewer is nearly free and recovers
real findings.

## See Also

- [gate-waiver-is-a-record.md](gate-waiver-is-a-record.md) — the second disposition; same discipline.
- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) — a gate result belongs to a specific artifact state.
- [trilens-loop-feature.md](trilens-loop-feature.md) — the loop and its stopping rules.
- [graduated-verification-confidence.md](graduated-verification-confidence.md) — "did not run" is a confidence level, not a boolean.
- [parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md) § Graceful degradation — a stalled reviewer's partial return is still additive evidence.
- [execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md) § Order the legs — the gate that was never launched, and saying so in the record.
