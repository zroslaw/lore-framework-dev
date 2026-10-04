---
lore: 1
type: topic
summary: "User decision (2026-10-04): when picking a home agent, choose the best fit by role with the incumbent keeping close calls, and price per-agent cost in prose rather than a hard numeric cap."
parent: lore/user-feedback-working-style.md
---

# Feedback — The Host Follows the Best Role Fit

User decision (2026-10-04), shaping the finalize host-guest model
([finalize-participant-revision-design.md](finalize-participant-revision-design.md)): at
finalization the framework should find the **best** agent to be host — matching the session's topic
and results against each agent's role (the short descriptions in the workspace routing map and
skills, and `role.md`) — not merely add agents around whichever agent happened to be booted. The
user agreed the **booted agent keeps close calls**, for stability across re-runs.

On caps: keep agent additions **uncapped**, but say explicitly that every finalizing agent carries a
time-and-token "tax", so selection must be careful, conscious, and common-sense.

## How to apply

When designing anything that picks a "home" agent (summary home, owner, router):

- default to **best fit by role, with an incumbent tie-break** — the incumbent loses only when the
  evidence points clearly elsewhere;
- **price per-agent cost in prose** instead of imposing a numeric cap, and keep a cap as an extension
  point until data shows over-selection
  ([feedback-mvp-minimalism.md](feedback-mvp-minimalism.md)).
