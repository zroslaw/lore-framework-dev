---
lore: 1
type: topic
summary: "An optional step inserted before a mandatory procedure must continue on the pre-feature path at every exit; stop only when no baseline exists. State it once as an invariant and grep each stop clause against it."
parent: lore/executable-prose-and-design-checks.md
---

# An Optional Step Must Fail Back to Baseline

**If the improvement cannot happen, the procedure continues exactly as it did before the feature.
It never ends early.** Every stop or abort clause in an optional step inserted ahead of a mandatory
procedure must be checked against the baseline path.

## How to apply

- Write the property **once, as an invariant** ("never stops because of X"), then grep every stop
  clause in the design and the spec against it.
- Enumerate the step's exits. Each is either **"continue on baseline"** or justified by the
  *absence* of a baseline (e.g. nothing booted at all, so there is no finalize to fall back to).

## Evidence

Finalize participant revision design, 2026-10-03
([finalize-participant-revision-design.md](finalize-participant-revision-design.md)). The
stop-rule regression appeared twice in a three-round review:

1. **Round 1.** "If no agent fits, stop" was vacuously true for a booted session with no durable
   knowledge — it would have dropped today's normal finalize. All three lenses caught it.
2. **Round 3.** It returned as "if the host cannot be attached, stop" in the wrong-agent case,
   where a booted host exists and only the optional swap failed. Two independent lenses caught it.
   The design doc already said "never stops because of revision"; the spec step contradicted it — a
   context error introduced by a fix round
   ([fix-defects-are-context-errors.md](fix-defects-are-context-errors.md)).

The recurrence is the point: stating the invariant in one doc does not protect the other. The grep
against each stop clause is the check.
