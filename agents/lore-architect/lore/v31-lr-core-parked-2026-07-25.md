# v31 `lr-core` — Parked, Not Shipped (2026-07-25)

The v31 `lr-core` work — a deterministic substrate script plus boot/attach/consult/pull-lore/
process-merge/lore-search doc rewiring, plus the Script Fallback Contract — is fully implemented and
has been through two trilens review rounds (all findings applied). It is **not shipped**. The user
parked it explicitly, mid-session, after a rough and frustrating session — not pushed to completion,
not discarded.

## Where it lives

Branch `wip/lr-core-v31` in both `lore-framework` and `lore-framework-dev`, each checked out in its own
worktree at `<workspace>/.worktrees/<repo>/lr-core-v31/` (per `worktrees-convention.md`). Both
top-level `main` checkouts are clean — nothing of this work is visible from a normal boot on main.
`docs/trilens-loop.md` on main is still the full 325-line version described in `trilens-loop-feature.md`
— see `trilens-loop-deliberately-minimal-2026-07-25.md` for the parked compression of that doc, same
branch/session.

## Resuming

Don't reconstruct the plan from scratch. Exact resume steps — missing regression tests for two round-2
fixes, trilens round 3, the full lifecycle suite, then commit+push — are recorded in
`agents/lore-architect/workdir/GOAL-2026-07-25.md` **inside that worktree** (not in the main checkout's
workdir). Read that file first.

Before starting *any* fresh work on `lr-core`, the Script Fallback Contract, or `trilens-loop.md`, check
for this branch/worktree pair first — a second attempt at the same design without checking would
duplicate work already done and reviewed.

## Relation to the normal parking drill

This is a different flavor of parking than `parked-design-preservation-pattern.md`'s revert-and-
workdir-draft drill: that pattern is for early/mid-draft design work reverted back to committed main
plus a `workdir/draft-*.md`. Here the work is *complete and reviewed* — it stays on its own
branch/worktree rather than being reverted, because reverting fully-implemented, twice-reviewed code
would throw away real work for no reason. Use the revert-and-draft drill for early-stage design pivots;
use branch/worktree parking (this instance) for complete-but-not-yet-shipped work that the user wants
held rather than pushed through or discarded.

## See Also

- `trilens-loop-deliberately-minimal-2026-07-25.md` — the parked `docs/trilens-loop.md` compression,
  same branch/session.
- `parked-design-preservation-pattern.md` — the sibling parking pattern for early-draft (not complete)
  work.
- `worktrees-convention.md` — the underlying worktree mechanism.
- `feedback-comply-promptly-after-repeated-pushback.md` — the working-style lesson from the same rough
  session.
