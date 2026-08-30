---
lore: 1
type: topic
summary: "Reserve lens, round, and converged for /lr:trilens-loop — naming another tool's fan-out with gate vocabulary corrupts the ship record; plus how the built-in /simplify differs from TriLens and why ours still earns its keep."
parent: lore-context.md
---

# Don't borrow gate vocabulary for work that is not that gate

2026-08-30, during v44 drafting: the user invoked `/simplify` — a **built-in Claude Code skill, not
ours** — whose own instructions mandate launching four parallel review agents. I named them
`reuse-lens`, `simplify-lens`, `efficiency-lens`, `altitude-lens`.

The user then asked: "have you just run trilens loop?" A fair question, and my naming caused it.
"Lens" is our TriLens vocabulary (`parallel-reviewer-fanout-pattern.md`,
[trilens-loop-feature.md](trilens-loop-feature.md)). Borrowing it for a different tool's fan-out made
a non-gate look like the gate.

**Why this is more than cosmetic.** Every ship record must name each gate `passed`, `waived`, or
`did not run` ([gate-waiver-is-a-record.md](gate-waiver-is-a-record.md)). Anyone reading that
scrollback later would reasonably conclude TriLens ran on v44. It did not. **Vocabulary leakage
corrupts the disposition record as effectively as a wrong entry would** — and it does so in the
scrollback, where no `/lr:check` can see it.

> **Rule:** reserve `lens`, `round`, and `converged` for `/lr:trilens-loop`. Name other review
> fan-outs for what they are (`cleanup-reuse`, `cleanup-efficiency`).

## `/simplify` overlaps TriLens structurally — the differences that still justify ours

Worth knowing, now that a built-in covers adjacent ground:

- `/simplify` is **single-pass**. TriLens **iterates until a round returns nothing worth fixing** —
  that convergence *is* the ship signal, and one pass cannot produce it.
- **No APPLIED/DECLINED ledger**, so a declined finding can resurface on a later run.
- **Quality only** — it explicitly does not hunt correctness bugs; `/code-review` is its sibling.
- **No death disclosure.** The user stopped three of the four agents mid-run, and nothing in
  `/simplify` distinguishes "stopped" from "found nothing." That is our own
  [a-gate-that-died-is-not-a-gate.md](a-gate-that-died-is-not-a-gate.md) showing up as a gap in
  someone else's tool — and a reason to keep reporting reviewer liveness myself rather than assuming
  the harness does it.

## The one finding that landed before the stop

Real, and worth keeping as method. A new test copied a workspace tree to a new path to prove a
shortcut "survives relocation" — but it could not fail independently of the test above it, because
the function under test takes the workspace as a plain parameter.

> **A test whose setup dramatizes the scenario but exercises no new branch is documentation wearing a
> test's clothes.**

The right repair was to move it up a level, not delete it: an end-to-end assertion through `scan()`
covering relative target → `registered: true` → S11 suppressed, which nothing else covered. See
[committed-artifacts-carry-relative-paths.md](committed-artifacts-carry-relative-paths.md) for the
defect that test exists to pin, and `prove-a-new-test-red-against-the-previous-tag.md` for the
mechanical version of the same question — a test that cannot go red proves nothing either way.

## See Also

- `parallel-reviewer-fanout-pattern.md` — the judgement layer TriLens's vocabulary belongs to.
- `gate-waiver-is-a-record.md`, `a-gate-that-died-is-not-a-gate.md` — the disposition record this
  protects.
- `feedback-pre-ship-gates-on-request.md` — why TriLens is opt-in, which is exactly why an
  accidental claim that it ran is expensive.
