---
lore: 1
type: topic
summary: "A user waiver of a release gate must be written into the ship record as 'closed by waiver, not by execution' — never let a waived gate silently look like a passed one."
parent: lore-context.md
---

# A Gate Waiver Is Itself a Record

When the user explicitly waives a release gate, the waiver is the closing of that gate — and it
must be recorded as such, in the same place a pass would have been recorded.

**The instance (v36, 2026-08-09):** the real-engine lifecycle gate was explicitly waived by the
user at ship time — deliberately excluded from release-candidate preparation and from the final
pre-push review. The waiver was written into `versioning-release-types.md`'s v36 entry (and the
implementation handoff) with the explicit framing "the waiver is this record".

**Rule:** never let a waived gate silently look like a passed one. A ship record that just omits
the gate is ambiguous between "ran and passed", "forgot", and "waived" — and the ambiguity resolves
in the reader's favor of "passed". Write "closed by waiver, not by execution", name who waived it
and when, and keep the waiver in the per-version record so later re-triage knows that version's
coverage honestly.

This composes with the artifact-state rule: a waiver, like a gate result, belongs to a specific
ship — it does not carry forward to the next version's gates.

## See Also

- [versioning-release-types.md](versioning-release-types.md) — the per-version record where waivers land; carries the v36 instance.
- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) — gate results (and waivers) belong to a specific artifact state.
- [graduated-verification-confidence.md](graduated-verification-confidence.md) — "closed by waiver" is a confidence level, not a boolean pass.
- [trilens-loop-feature.md](trilens-loop-feature.md) — § When the round cap bites: the sibling practice fact from the same ship.
