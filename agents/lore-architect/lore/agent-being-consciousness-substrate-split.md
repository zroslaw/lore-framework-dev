# Agent Being = LLM Consciousness + Deterministic Supervisor Substrate

Named principle surfaced during the 2026-07-19 "Agent Beings" brainstorm. The direction has since settled its design and naming (same day, design dialogue): the module is **Lore Beings**, the supervisor daemon is the **Being Keeper** — see `lore-beings-design.md` (anchor) and `workdir/draft-lore-beings.md` (full agreed design). This topic keeps its original filename; the principle it names is unchanged and governs that design.

## The principle

**An autonomous lore agent's "consciousness" (reasoning, planning, judgment) must be LLM-driven, but its "autonomic nervous system" (scheduling, spawning, monitoring, budget enforcement, kill switch) must be deterministic code, never a model.**

## Why it matters

An agent cannot reliably be its own circuit breaker. If the supervisor that decides "has this run exceeded budget, should I kill it" is itself an LLM session, the safety mechanism inherits every failure mode it's supposed to guard against (runaway loops, misjudged urgency, drift). Budget caps and kill switches only hold if enforcement sits outside the reasoning loop entirely.

This also resolves the framework's oldest open question in this space cheaply: "cost / loop safety... need budget caps and a kill switch" was listed as an open question in `autonomous-agents-vision.md` since the original 2026-04-26 brainstorm. Under the consciousness/substrate split, budget safety falls out of the architecture for free — it's just something the deterministic supervisor does, not a separate mechanism to design.

## Diagnostic

When designing any piece of the autonomous-agents / Lore Beings direction, ask: is this judgment (route to LLM) or is this enforcement/bookkeeping (route to the Being Keeper, the deterministic supervisor)? Existential-task *content* (what to do during a morning-plan session) is judgment. Existential-task *scheduling and execution* (when to spawn, how much budget, whether to kill) is substrate.

## Precedent already in lore

This isn't a new invention — the framework's `lr-wait` (`wait-primitive-feature.md`) is already a deterministic (stdlib Python, no LLM) MCP server providing the inbound half of this pattern. The switchboard daemon sketch in `autonomous-agents-substrate.md` was already conceived as a non-LLM daemon. The Being Keeper generalizes that precedent to own the *between-session* half (scheduling existential tasks, spawning headless engine sessions, budget/kill-switch), where `lr-wait` owns the *within-session* synchronous half.

## See Also

- `autonomous-agents-vision.md` — the parked vision this principle now sharpens (esp. the "cost / loop safety" open question)
- `autonomous-agents-substrate.md` — the switchboard daemon precedent
- `wait-primitive-feature.md` — the shipped deterministic inbound-signal precedent
- `naming-foundational-principles.md` — the meta-rule this topic follows (name the framing, not just the mechanism)
- `system-design-principles.md` — index of named principles; this one is listed there
- `lore-beings-design.md` — anchor for the settled Lore Beings design this principle governs; full design in `workdir/draft-lore-beings.md`
- `framework-improvements-backlog.md` § Major Directions § Autonomous Agents / Lore Beings — the direction's backlog home
