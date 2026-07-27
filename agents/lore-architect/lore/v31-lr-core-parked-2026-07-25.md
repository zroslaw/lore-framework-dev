# v31 `lr-core` — Parked, Not Shipped (2026-07-25; addendum, review, and restructure through 2026-07-27)

The v31 `lr-core` work — a deterministic substrate script plus boot/attach/consult/pull-lore/
process-merge/lore-search doc rewiring, plus the Script Fallback Contract — is fully implemented and
has been through several trilens review rounds (all findings adjudicated). It is **not shipped**. The
user parked it explicitly, mid-session on 2026-07-25, after a rough and frustrating session — not
pushed to completion, not discarded. Follow-on sessions resumed it three times: the
literate-accelerator addendum, a review-and-fix pass, and the `trilens-loop.md` restructure (all
below).

**Current state as of 2026-07-27: everything is committed on `wip/lr-core-v31` in both repos, with
clean working trees. The branch is NOT merged to main and NOT pushed.** This changed from earlier
sessions, where the work sat uncommitted in the worktrees — the "nothing is committed" framing in the
sections below describes those sessions' end states, not today's.

| Repo | Branch head | Contents |
|---|---|---|
| `lore-framework` | `c3d418d` | restructure trilens-loop, correct Cursor subagent notes (on top of `63d2d86` WIP) |
| `lore-framework-dev` | `8fc46f0` | regression tests + `literate-accelerator-pattern.md` + a lore-context addition (on top of `cd71c76` WIP) |

## 2026-07-26 addendum: literate-accelerator redesign

A follow-on session (same parked branch/worktree pair; uncommitted at the time, committed on
2026-07-27) applied a further design change, user-directed: make `scripts/lr-core` the source of
truth for its own procedures via instructional comments *inside* the script, rather than a separate
prose fallback doc.

**What changed** (all still parked, now committed on the branch):
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

### Open item: `cursor.md` subagent-spawn binding — **RESOLVED 2026-07-27**

The gap (the Cursor profile naming `trilens-loop.md` as the semantics-class carve-out while the
compressed doc stated neither the classification nor the "no host-side fallback" rule) is closed. The
restructured doc now states its own semantics-class classification and the no-fallback rule in step
3, and `docs/engines/cursor.md` was corrected in the same commit. See § 2026-07-27 below and
`trilens-loop-v31-restructured.md`.

Worth remembering *how* it nearly went the other way: mid-session I reasoned that since all three
Tier-1 engines have native subagents the rule had no live case, and told the user the item could come
off the pre-ship list. The next review round returned it as a `BLOCKER` citing my own lore. See
`check-own-lore-before-dismissing-a-finding.md`.

## 2026-07-27: `trilens-loop.md` restructured, everything committed to the branch

A short follow-on session, entirely user-directed:

1. **`docs/trilens-loop.md` rewritten** from the parked one-paragraph version into a ~75-line
   structured doc — numbered loop, stopping rules, an explicit host/reviewer **exchange contract**,
   overrides. Three lenses restored as the stated default; severity/verdict/disposition vocabulary
   reinstated; hard three-round ceiling; regular-tier reviewer models restored. Full detail in
   `trilens-loop-v31-restructured.md`. This did **not** violate
   `trilens-loop-deliberately-minimal-2026-07-25.md` — every expansion was asked for step by step.
2. **One trilens round over the restructure** (hand-executor fidelity, internal consistency, corpus
   coherence): 18 findings, 11 applied, 5 declined, 1 accepted. It produced the `BLOCKER` that closed
   the `cursor.md` deferral above and a stale-release-note finding. Cost profile measured — see
   `parallel-reviewer-fanout-pattern.md` § Cost.
3. **`docs/engines/cursor.md` and `release-notes/31.md` corrected** in the same commit.
4. **Both repos committed on `wip/lr-core-v31`** (`c3d418d`, `8fc46f0`); working trees clean. Still
   not merged to main, still not pushed. Lifecycle suite still not run against this state.

Note for the eventual merge to main: `8fc46f0` includes a 5-line addition to the *branch's*
`agents/lore-architect/lore-context.md` (§ Skills & Docs, the literate-accelerator paragraph). Main's
`lore-context.md` has since moved in other sections, so expect a merge, not a fast-forward, on that
file.

## Where it lives

Branch `wip/lr-core-v31` in both `lore-framework` and `lore-framework-dev`, each checked out in its own
worktree at `<workspace>/.worktrees/<repo>/lr-core-v31/` (per `worktrees-convention.md`). Both
top-level `main` checkouts are clean — nothing of this work is visible from a normal boot on main.
`docs/trilens-loop.md` on main is still the full 325-line version described in `trilens-loop-feature.md`
— see `trilens-loop-v31-restructured.md` for the parked branch's current version of that doc, and
`trilens-loop-deliberately-minimal-2026-07-25.md` for the standing don't-auto-restore rule.

## Resuming

Don't reconstruct the plan from scratch. **The regression-tests, review, and `cursor.md`-deferral
portions of the previous resume lists are now done — don't redo them.**
`agents/lore-architect/workdir/GOAL-2026-07-25.md` **inside that worktree** (not the main checkout's
workdir) describes the *pre-round-1* plan and is stale on three points now: the two round-2
regression tests (written and mutation-verified), "trilens round 3" scoped only to the round-2 delta
(superseded twice by full-surface passes), and the `cursor.md` open item (resolved). Resume steps as
of 2026-07-27:

1. Run the full lifecycle suite (`LR_LIFECYCLE=1`) against branch head — still not run against any
   v31 state. This is the outstanding gate; per `post-convergence-edits-need-their-own-gate.md` it
   must run against `c3d418d`/`8fc46f0`, not an earlier tree.
2. Reconcile the Codex reviewer-tier model name before shipping — the user says **gpt-5.4**,
   `release-notes/30.md:49` and `trilens-loop-feature.md` say **gpt-4.5**. Fix forward in v31's notes;
   don't retro-edit shipped notes. See `trilens-loop-v31-restructured.md` § Caveat.
3. Ship: version-ship discipline in `role.md` (manifests, `versioning-release-types.md` backfill,
   cache-clear footer), then merge `wip/lr-core-v31` to main in both repos and push.
4. On merge, fold `literate-accelerator-pattern.md` and `trilens-loop-v31-restructured.md` into
   main's lore properly — the former arrives with the branch, the latter should collapse into
   `trilens-loop-feature.md` once the doc it describes is the shipped one.

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

- `trilens-loop-v31-restructured.md` — what `docs/trilens-loop.md` looks like on this branch now.
- `trilens-loop-deliberately-minimal-2026-07-25.md` — the standing don't-auto-restore rule for that
  doc, and the record of the original compression.
- `check-own-lore-before-dismissing-a-finding.md` — the near-miss that would have dropped the
  `cursor.md` item unresolved.
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
