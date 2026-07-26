# v31 `lr-core` — Parked, Not Shipped (2026-07-25, extended 2026-07-26)

The v31 `lr-core` work — a deterministic substrate script plus boot/attach/consult/pull-lore/
process-merge/lore-search doc rewiring, plus the Script Fallback Contract — is fully implemented and
has been through two trilens review rounds (all findings applied). It is **not shipped**. The user
parked it explicitly, mid-session, after a rough and frustrating session — not pushed to completion,
not discarded.

## 2026-07-26 addendum: literate-accelerator redesign

A follow-on session (same parked branch/worktree pair, no new commits — still fully uncommitted)
applied a further design change, user-directed: make `scripts/lr-core` the source of truth for its
own procedures via instructional comments *inside* the script, rather than a separate prose
fallback doc.

**What changed** (all still parked/uncommitted):
- `scripts/lr-core`'s module docstring now names the script's own comments as the spec (previously:
  "procedure docs remain normative"). `cmd_preflight`, `cmd_discover`, `cmd_scan`, and helpers
  (`pull_repo`, `compare_versions`, `detect_teammate`, `_resolve_agent`) gained numbered,
  instruction-shaped docstrings. Zero behavioral change — confirmed by the full existing
  `tests/test_lr_core.py` suite (38/38) passing unmodified, plus a manual `py_compile` and a live
  `preflight` invocation showing an identical JSON shape.
- `docs/conventions.md` § Script Fallback Contract: the **Accelerator** category redefined as
  **literate** — script comments are the fallback spec, not a companion doc.
- `docs/agent-boot.md` § Manual Boot Procedure, `docs/auto-pull.md` §§ Steps 1–3, and the fallback
  sentences in `attach.md`/`consult.md`/`lore-search.md`/`process-merge.md`/`pull-lore.md` were all
  thinned from restated hand-procedures to pointers naming specific `scripts/lr-core` functions.
  `auto-pull.md` dropped from 100 to 80 lines; kept only genuinely caller-side policy (the
  reporting-verbosity table) or conceptual framing absent from the script.
- New lore-architect topic **`literate-accelerator-pattern.md`** — written directly into the
  **worktree's** `lore/` (`.worktrees/lore-framework-dev/lr-core-v31/agents/lore-architect/lore/`),
  **not** into this repo's main-checkout `lore/`. It documents the pattern generally (the one rule:
  comments must read as freestanding instructions, not code annotations) and names `scripts/lr-core`
  as the first instance. **Do not duplicate it into this repo's lore now** — the pattern's only
  instance is itself unshipped, so the topic lands naturally on `main` when v31 ships. A future
  session should look for it by that filename inside the worktree if it needs the pattern before
  then.
- `release-notes/31.md` updated to describe the new shape instead of the old "prose is normative"
  framing.

**Trilens-review gap — read before shipping.** The resume list below (regression tests, trilens
round 3, lifecycle suite, ship) predates this addendum and does **not** cover it. The existing
"trilens round 3" resume step was scoped only to the round-2 correctness-fix delta — it does **not**
cover today's comment/doc rewrite. Per `post-convergence-edits-need-their-own-gate.md`'s framing, a
review that ran before an edit lands doesn't gate that edit: **none of the literate-accelerator
surface (the script's new docstrings plus the ~9 touched doc files) has been trilens-reviewed yet.**
Before shipping, widen round 3's scope to include this addendum, or run a dedicated extra pass —
either way, don't treat the pre-existing round-3 plan as sufficient on its own. Verification already
done this session that round 3 can build on rather than re-derive: tests green (38/38), `py_compile`
clean, a live CLI spot-check, and a grep sweep for stale "is normative" phrasing.

## Where it lives

Branch `wip/lr-core-v31` in both `lore-framework` and `lore-framework-dev`, each checked out in its own
worktree at `<workspace>/.worktrees/<repo>/lr-core-v31/` (per `worktrees-convention.md`). Both
top-level `main` checkouts are clean — nothing of this work is visible from a normal boot on main.
`docs/trilens-loop.md` on main is still the full 325-line version described in `trilens-loop-feature.md`
— see `trilens-loop-deliberately-minimal-2026-07-25.md` for the parked compression of that doc, same
branch/session.

## Resuming

Don't reconstruct the plan from scratch. Resume steps — missing regression tests for two round-2
fixes, trilens round 3, the full lifecycle suite, then commit+push — are recorded in
`agents/lore-architect/workdir/GOAL-2026-07-25.md` **inside that worktree** (not in the main checkout's
workdir). Read that file first, **but treat its "trilens round 3" step as under-scoped**: it predates
the 2026-07-26 literate-accelerator addendum above and was written to cover only the round-2
correctness-fix delta. Widen it (or add a dedicated pass) to also cover the addendum's surface before
shipping.

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
- `post-convergence-edits-need-their-own-gate.md` — the framing behind why the addendum's surface
  needs its own trilens pass rather than inheriting round 2's clearance.
- `literate-accelerator-pattern.md` — **not yet in this repo's lore**; lives only in the worktree's
  `lore/` until v31 ships (see 2026-07-26 addendum above). Look for it there, not here, if you need
  the pattern before then.
