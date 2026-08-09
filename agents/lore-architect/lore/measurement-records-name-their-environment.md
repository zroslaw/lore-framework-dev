---
lore: 1
type: topic
summary: "A recorded environment-dependent number (boot footprint, token cost, timing) must name the engine/profile/machine it was measured under, or it generates false drift alarms."
parent: lore-context.md
---

# Measurement Records Name Their Environment

A ship-record measurement is only reproducible if the record names the environment it was taken
in.

**The instance (v36, 2026-08-09):** the v36 release-notes Validation section quoted a
22,223-token boot footprint (7,525 system-prompt tokens) without saying it was measured under the
**codex** engine profile. On the same tree the claude profile measures 6,234 system-prompt tokens
— so a Claude reader re-measuring would suspect tree drift where there was none. Caught in final
review; fixed by naming the profile and giving the claude figure alongside.

**Rule:** when recording an environment-dependent number — boot footprint, per-engine token cost,
timing — name the engine/profile/machine axis it depends on, or the record generates false drift
alarms in later re-measurement.

This is the measurement-flavored sibling of "a gate result belongs to a specific artifact state"
([post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md)):
there a green run belongs to a specific tree; here a recorded number belongs to a specific
environment.

## See Also

- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) — the artifact-state sibling.
- [cursor-boot-context-cost-measurement.md](cursor-boot-context-cost-measurement.md) — a measurement record that does name its environment (Cursor, o200k_base, dated).
- [benchmark-measurement-design-principles.md](benchmark-measurement-design-principles.md) — measurement-design principles for agent-behavior benchmarks; same family, design-time rather than record-time.
