# v31 `lr-core` — Parked, Not Shipped (2026-07-25; addendum + round-1 review 2026-07-26)

The v31 `lr-core` work — a deterministic substrate script plus boot/attach/consult/pull-lore/
process-merge/lore-search doc rewiring, plus the Script Fallback Contract — is fully implemented and
has been through two trilens review rounds (all findings applied), plus a further 2026-07-26 review
round (below) that closed the gap the addendum had opened. It is **not shipped**. The user parked it
explicitly, mid-session on 2026-07-25, after a rough and frustrating session — not pushed to
completion, not discarded. A 2026-07-26 follow-on session resumed the parked work twice: first for
the literate-accelerator addendum, then for a review-and-fix pass (both below). Still nothing is
committed or pushed as of either session's end.

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

**Trilens-review gap — CLOSED by the 2026-07-26 round-1 review below.** At the time this addendum
landed, the resume list (regression tests, trilens round 3, lifecycle suite, ship) predated it and
did not cover it — the existing "trilens round 3" resume step was scoped only to the round-2
correctness-fix delta, not this comment/doc rewrite. Per `post-convergence-edits-need-their-own-gate.md`'s
framing, a review that ran before an edit lands doesn't gate that edit. **This gap is now closed**:
the round-1 review (see next section) deliberately scoped its cold-lens pass across the *entire* v31
surface — committed WIP + this addendum + the session's new tests — as a superset of the narrower
"round 3" plan, specifically so the reviewed artifact state equals the shippable one. Verification
that round used as its baseline (already done before the addendum landed, not re-derived): tests
green (38/38), `py_compile` clean, a live CLI spot-check, and a grep sweep for stale "is normative"
phrasing.

## 2026-07-26 round-1 review: closes the addendum gap, finds and fixes real bugs

A same-day follow-on session ran the review pass the addendum above flagged as missing, plus filled
in the two regression tests the round-2 resume list had already called out as outstanding:

1. **The two missing round-2 regression tests were added**: the `GIT_UNRUNNABLE`-at-every-call-site
   distinction, and `scan` not misreporting an unreadable git history as "uncommitted or untracked".
   Both verified by mutation (revert the fix, confirm the new test fails, restore) rather than
   trusting a pass — see `verify-regression-tests-via-mutation.md`.
2. **One trilens review round was run**, explicitly using the **v31 compressed**
   `docs/trilens-loop.md` (the parked one-paragraph version on `wip/lr-core-v31`, per user
   instruction — see `trilens-loop-deliberately-minimal-2026-07-25.md`), not the shipped 325-line v30
   version on `main`. Scope was the *entire* v31 change set in both repos (committed WIP + this
   addendum + the session's new tests) — the deliberate superset described above.
3. Three cold lenses (hand-executor, adversarial correctness, corpus coherence) all returned
   `SHIP-WITH-FIXES`, zero BLOCKERs, 5 HIGH total. All verified against real files (most reproduced)
   before fixing. Applied: a real mutating-git-operation bug where `pull_repo`/`scan` ran `git -C`
   against a directory that wasn't its own repo's toplevel and silently walked up into an enclosing
   repo (see `git-dash-c-needs-toplevel-guard.md`), a signal-death/unrunnable-sentinel collision, a
   non-ASCII git-quotepath bug, an int-equal-but-string-different version-comparison bug, a BOM
   silently voiding frontmatter, an exit-2 payload indistinguishable from a determinate failure, a
   Manual Boot Procedure path that skipped the version-check/teammate-conventions step, and the
   literate-accelerator contract having no floor for "the script file itself is gone" — plus release
   notes that contradicted the accelerator's own definition and omitted the `trilens-loop.md` rewrite
   entirely. Tests: 38 → 51, all green.
4. **The user then stopped the loop deliberately**: no round 2, no further review iteration,
   lifecycle suite not run, nothing committed or pushed. This was an explicit "keep it minimal, don't
   loop — just finish what you already found" instruction, not a quality judgment on the round.

### Open item: `cursor.md` subagent-spawn binding — deferred, not decided

`docs/engines/cursor.md`'s `subagent-spawn` binding still names `trilens-loop.md` as the carve-out
for "subagent independence is the semantics" — but the compressed 15-line doc no longer states any
engine-binding instruction or the "no subagent mechanism → stop" rule. Both the hand-executor and
corpus-coherence lenses found this independently, so it is a real gap. Per
`trilens-loop-deliberately-minimal-2026-07-25.md`, re-expanding any part of the compressed doc needs
a fresh, explicit user decision — **this was surfaced, not applied.** Resolve before shipping v31,
one way or another: either fix `cursor.md`'s pointer to stop claiming a rule the doc no longer
states, or re-expand the relevant slice of `trilens-loop.md`.

## Where it lives

Branch `wip/lr-core-v31` in both `lore-framework` and `lore-framework-dev`, each checked out in its own
worktree at `<workspace>/.worktrees/<repo>/lr-core-v31/` (per `worktrees-convention.md`). Both
top-level `main` checkouts are clean — nothing of this work is visible from a normal boot on main.
`docs/trilens-loop.md` on main is still the full 325-line version described in `trilens-loop-feature.md`
— see `trilens-loop-deliberately-minimal-2026-07-25.md` for the parked compression of that doc, same
branch/session.

## Resuming

Don't reconstruct the plan from scratch. **The regression-tests-and-review portion of the previous
resume list is now done — don't redo it.** `agents/lore-architect/workdir/GOAL-2026-07-25.md` **inside
that worktree** (not the main checkout's workdir) still describes the *pre-round-1* plan and is now
stale on two points: it lists the two round-2 regression tests as outstanding (they're written and
mutation-verified) and describes "trilens round 3" as scoped only to the round-2 delta (the round-1
review above superseded it with a full-surface pass instead). Resume steps as of this session's end:

1. Decide the `cursor.md` subagent-spawn deferral (see above) — fix the stale pointer or re-expand
   the relevant slice of `trilens-loop.md`.
2. Run the full lifecycle suite (`LR_LIFECYCLE=1`) — not yet run against this state.
3. Ship: commit + push both worktrees, per the normal version-ship discipline in `role.md`.

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
  needed its own trilens pass rather than inheriting round 2's clearance — satisfied by the round-1
  review above.
- `git-dash-c-needs-toplevel-guard.md` — the mutating-git-operation bug found and fixed in round 1
  (nested-repo `git -C` escape).
- `verify-regression-tests-via-mutation.md` — how the two round-2 regression tests added in round 1
  were verified to actually pin their bugs.
- `literate-accelerator-pattern.md` — **not yet in this repo's lore**; lives only in the worktree's
  `lore/` until v31 ships (see 2026-07-26 addendum above). Look for it there, not here, if you need
  the pattern before then.
