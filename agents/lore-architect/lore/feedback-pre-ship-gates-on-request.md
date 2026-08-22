---
lore: 1
type: topic
summary: "User decision 2026-08-22: the lifecycle suite and the TriLens loop are on-request, not default gates; the ship record still names each one's disposition."
parent: lore-context.md
---

# Pre-Ship Gates Are On Request

**User decision, 2026-08-22.** The two expensive pre-ship gates — the lifecycle suite
(`tests/lifecycle/`) and `/lr:trilens-loop` — are **no longer default**. They run only when the
user asks for them.

## Why

The user's stated reason, from repeated experience: running both by default slowed development
drastically and consumed tokens fast. On most ships the return did not justify that cost.

This is a **cost decision, not a claim that the gates are unnecessary.** Everything the gates
catch, they still catch. See `lifecycle-testing-harness.md` and
`execution-testing-catches-blind-ambiguity.md` for what is being traded away, and
`versioning-release-types.md` for the v40 record — a ship that deferred both gates and carried
five defects to users, four of them one shape that had been degrading real boots since v38.

## What did not change

The **disposition record**. Every ship still names each gate `passed`, `waived`, or
`did not run` (`gate-waiver-is-a-record.md`). The default is now `did not run` — written into the
ship record and said out loud in one line at ship time, never silently omitted.

Nor did the ordering change. When the empirical leg runs, it runs
**lifecycle suite → dogfood onto this workspace → TriLens over whatever those disturbed**. The
user reaffirmed TriLens-after-dogfooding on 2026-08-22. Dogfooding produces the evidence the
reviewers read, so a TriLens run before it reviews a state that no longer exists — and a gate
result belongs to one specific artifact state (`post-convergence-edits-need-their-own-gate.md`).

## What still runs by default

The deterministic tests, `/lr:check`, and ordinary dogfooding. Those are cheap.

The quality benchmark (`quality-benchmark-feature.md`) was already on-request and is unaffected.

## Where this policy lives: my lore only

Verified 2026-08-22 by grepping `lore-framework/docs/`, `skills/`, and `README.md` for `trilens`,
`lifecycle suite`, and `pre-ship`: **no plugin-layer artifact asserts that either gate is a required
pre-ship gate.** The plugin documents `/lr:trilens-loop` only as an available tool — the README
command table, engine-profile entries about how its subagents spawn, and `docs/engines/cursor.md`'s
use of it as a subagent-independence example.

So the gate policy is entirely mine: `role.md` and `lore-context.md` in `lore-framework-dev`.
Flipping a gate between default-on and on-request is an **agent-lore edit — no VERSION bump, no
manifest bump, no release notes, no cache-clear footer.** Do not go hunting the plugin docs for it,
and do not open a release for it.

The inverse is worth watching: if this policy should ever bind other adopters, it has no
plugin-layer home yet and would need one.

## See Also

- `gate-waiver-is-a-record.md` — the three dispositions and why a waiver is itself a record.
- `a-gate-that-died-is-not-a-gate.md` — "did not run" is neither a pass nor a waiver.
- `lifecycle-testing-harness.md` — what the suite covers when it is requested.
- `trilens-loop-feature.md` — the loop's shape and termination guards when it is requested.
- `feedback-mvp-minimalism.md` — sibling user-preference topic on scoping cost.
