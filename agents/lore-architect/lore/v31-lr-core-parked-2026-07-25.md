# v31 `lr-core` — Parked, Not Shipped (2026-07-25; addendum, review, and restructure through 2026-07-27)

The v31 `lr-core` work — a deterministic substrate script plus boot/attach/consult/pull-lore/
process-merge/lore-search doc rewiring, plus the Script Fallback Contract — is fully implemented and
has been through several trilens review rounds (all findings adjudicated). It is **not shipped**. The
user parked it explicitly, mid-session on 2026-07-25, after a rough and frustrating session — not
pushed to completion, not discarded. Follow-on sessions resumed it three times: the
literate-accelerator addendum, a review-and-fix pass, and the `trilens-loop.md` restructure (all
below).

**Current state as of 2026-07-27 evening session:** A7 plugin-identity gate is on
`lore-framework-dev` `main`. Codex marketplace + Cursor (cloud plugin disabled) were
repointed at the v31 worktree; a **valid** lifecycle re-run produced Codex **6/7** and
Cursor **4/7** — see `v31-lifecycle-rerun-partial-green-2026-07-27.md`. Plugin remains
parked on `wip/lr-core-v31` @ `cd8ece1`. Ship gate: triage remaining boot/Script-Fallback /
Cursor-sees-30 failures, then version-ship.

| Repo | Where it lives now | Notes |
|---|---|---|
| `lore-framework` | `wip/lr-core-v31` @ `cd8ece1` (worktree) | Still the ship gate. |
| `lore-framework-dev` | **`main`** (includes former WIP + A7) | Harness identity gate live. |

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

## 2026-07-27 (later): trilens rounds 1–3, then the first real lifecycle-suite run against v31

A same-day follow-on session ran the review-loop resume step from the section above, then — for the
first time — the outstanding empirical gate.

**Trilens-loop, three rounds, over v31's committed state:** 25 findings across 3 rounds, 21 applied, 3
declined, 1 accepted, zero sustained BLOCKERs. Round 1 found a genuine data-loss bug: a nested-repo
`git -C` escape in `version-check.md`'s **prose** migration gate — the same bug class round 1 of the
2026-07-26 session had already fixed in `scripts/lr-core` (`git-dash-c-needs-toplevel-guard.md`), but
the prose gate that runs in the same boot flow had never gotten the matching fix. Round 2 found that a
round-1 fix (a runtime-headroom note) had landed at only one of four call sites that needed it — caught
independently by two lenses in the same round, which is corroborating evidence, not redundant noise
(per `role.md`'s "convergent findings from two independent lenses" framing). **Round 3 did not
converge** — it hit the loop's hard 3-round ceiling with 2 HIGHs still outstanding; those two fixes are
committed but explicitly **ungated** (no round reviewed them) and disclosed as such rather than implied
clean. Commits: `cb24024`, `26dec86` (lore-framework); `49503ce`, `c63da4a` (lore-framework-dev).

**Real-engine lifecycle suite run for the first time against v31** (the gate the Resuming section above
flagged as never having run against any v31 state):

- **Claude Code / haiku is the only valid result**: 6/7 modules green; the 7th (`test_boot`) had one
  flaky scenario (`test_05`). Root-caused and fixed — a macOS-specific `pwd`-vs-`realpath` ambiguity in
  `version-check.md`'s nested-repo guard, not a v31 regression (confirmed via an A/B baseline run
  against shipped v30, which hit the identical bug at a similar rate). See
  `macos-var-symlink-realpath-ambiguity.md` and `flaky-scenario-diagnosis-needs-ab-baseline.md` for the
  bug and the diagnosis methodology, respectively. Fix committed as `cd8ece1` (lore-framework).
- **Codex and Cursor runs are invalid, not red** — both engines silently resolved an *installed* v30
  plugin instead of the `--plugin-dir` worktree the harness passed them, so all 7 modules on each ran
  against the wrong tree while looking like a normal pass/fail result. This is a harness/environment
  gap, not a v31 defect — see `lifecycle-harness-plugin-identity-unverified.md` for the mechanism and
  the fix needed in the harness itself. **Net effect: today's suite produced exactly one trustworthy
  data point (Claude/haiku), not three.**

A trilens reviewer this session also raised a `BLOCKER` claiming the branch's divergence from `main`
(four commits ahead on `main` since the fork point) meant a future merge would silently discard those
four commits — misreading `git diff main..HEAD`'s two-way rendering of divergence as a preview of merge
behavior. Verified false via `git merge-tree --write-tree`: zero conflicts, both sides' content present
in the resulting tree. Overridden, disclosed, and generalized as its own topic — see
`diverged-branch-diff-misread-as-merge-outcome.md`.

**Outstanding for v31 as of the post-A7 lifecycle re-run** (supersedes older resume lists):

1. Triage/fix the partial-green failures in `v31-lifecycle-rerun-partial-green-2026-07-27.md`
   (Codex R>F wording + Script Fallback notify; Cursor stamp/update-dry-run seeing 30; takeover
   identity-probe timeout).
2. Version-ship discipline once the gate is acceptably green: four manifests to `1.31.0`, the
   `versioning-release-types.md` v31 entry, the cache-clear footer (cache-affecting), then merge
   **`lore-framework`** `wip/lr-core-v31` → `main` and push. (`lore-framework-dev` already on main,
   including A7.)
3. Fold `trilens-loop-v31-restructured.md` into `trilens-loop-feature.md` when the plugin doc ships.
4. Restore Cursor cloud-plugin backup (`~/.cursor/plugins-backup-v31-*`) after parked-branch testing
   if normal IDE installs should return — see `cursor-cloud-plugin-rehydrates-over-plugin-dir.md`.

Plugin branch tip still `cd8ece1` on `wip/lr-core-v31`, clean, not merged/pushed.

## Where it lives

Branch `wip/lr-core-v31` in **`lore-framework`** (still the only unmerged side), checked out at
`<workspace>/.worktrees/lore-framework/lr-core-v31/`. **`lore-framework-dev` main now includes the
former WIP** (merged 2026-07-27); its worktree may still exist at
`.worktrees/lore-framework-dev/lr-core-v31/` but is no longer the source of truth for agent-repo
content. Top-level `lore-framework` `main` remains clean at v30 — nothing of the plugin work is
visible from a normal boot on main. `docs/trilens-loop.md` on main is still the full 325-line
version described in `trilens-loop-feature.md` — see `trilens-loop-v31-restructured.md` for the
parked plugin branch's version of that doc, and `trilens-loop-deliberately-minimal-2026-07-25.md`
for the standing don't-auto-restore rule.

## Resuming

Don't reconstruct the plan from scratch. **A7, Codex/Cursor repoint, and a valid lifecycle
re-run are done** — see `v31-lifecycle-rerun-partial-green-2026-07-27.md` for the failure list
that is now the ship gate. Older resume bullets about "never ran lifecycle" / "repoint sources"
are stale.

Next:
1. Triage/fix the partial-green failures (Script Fallback notify, Codex R>F wording, Cursor
   seeing framework 30 in update/boot scenarios, takeover identity-probe timeout).
2. Ship the plugin when the gate is acceptably green (manifests, version-history, cache-clear,
   merge `wip/lr-core-v31` → main).
3. Collapse `trilens-loop-v31-restructured.md` into `trilens-loop-feature.md` on ship; restore
   Cursor cloud-plugin backup if normal installs should return.

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
- `lifecycle-harness-plugin-identity-unverified.md` — the 2026-07-27 finding that Codex/Cursor silently
  resolved an installed v30 plugin instead of the worktree under test, invalidating both engines'
  results from this session's lifecycle run.
- `macos-var-symlink-realpath-ambiguity.md` — the macOS `pwd`-vs-`realpath` bug behind `test_boot`'s
  flaky scenario, found and fixed during the same run.
- `flaky-scenario-diagnosis-needs-ab-baseline.md` — the methodology correction (A/B against the v30
  baseline) that distinguished "pre-existing flaky scenario" from "v31 regression" for that same bug.
- `diverged-branch-diff-misread-as-merge-outcome.md` — the overridden `BLOCKER` from this session's
  trilens round, misreading `main`'s divergence from this branch as a preview of merge behavior.
