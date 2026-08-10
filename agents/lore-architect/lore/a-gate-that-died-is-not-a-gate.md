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

## See Also

- [gate-waiver-is-a-record.md](gate-waiver-is-a-record.md) — the second disposition; same discipline.
- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) — a gate result belongs to a specific artifact state.
- [trilens-loop-feature.md](trilens-loop-feature.md) — the loop and its stopping rules.
- [graduated-verification-confidence.md](graduated-verification-confidence.md) — "did not run" is a confidence level, not a boolean.
