# `/lr:trilens-loop` — Change-Scoped Iterated Review (v30 Feature)

The shipped instrument for the architect's multi-round multi-lens review discipline. Shipped in
framework **v30** (`lore-framework` main `11ec0df`, tag `lr--v1.30.0`, manifests `1.30.0`,
release-notes-only, no migration). Canonical doc: `lore-framework/docs/trilens-loop.md`; thin-pointer
skill `skills/trilens-loop/SKILL.md` plus the Cursor wrapper `.cursor-skills/lr-trilens-loop/`.

**Shape:** resolve scope → pick 3 lenses → spawn 3 independent reviewers → triage → fix → repeat with
fresh reviewers until a round comes back clean.

## Promotion, not invention

This is `parallel-reviewer-fanout-pattern.md` — my own discipline, hardened across the v11–v28 ships —
promoted from agent lore to plugin capability. The user had independently articulated the same flow in
the 2026-06-01 lr-dev dialogue (`workdir/draft-lr-dev.md` §5), and it sat in
`framework-improvements-backlog.md` as "Reusable multi-lens review skill." Filed there as a DF-module
skill (`lr:dev-review`); **shipped as core**, because the pattern is domain-agnostic — doc sweeps and
lore edits, not just code. DF/AIQA is a consumer, not the owner.

The lore topic remains the *judgement* layer (which lenses work, convergence profiles, what to do when
reviewers disagree or stall); the skill is the *execution* layer. Reach for the skill; consult the
topic for lens choice and triage judgement.

## Load-bearing design points

All of these were earned during the ship, not assumed:

- **Semantics-class subagents — no host-side fallback.** Reviewer independence *is* the deliverable,
  so an engine that can only run serially must stop and report rather than degrade. This is the axis
  named in `subagent-as-optimization-vs-subagent-as-semantics.md`, and it is why v30 also had to
  correct the Cursor profile.
- **Default scope = the session's changes**, defined as the *union* of the files this session touched
  and the uncommitted changes in the repos those files live in. The union is load-bearing: a fresh
  session pointed at a dirty tree has an empty first term, and treating git status as a mere
  cross-check resolves the scope to nothing. An empty scope stops and reports rather than spawning
  reviewers over nothing. It is **not** a git range — that's what separates it from a PR review.
- **One free-text argument, no flags** (user decision). Free text outranks every default *including*
  the rails; the obligation is **disclosure, not refusal** — when free text switches a rail off, the
  skill says so in its output instead of complying silently. A user-requested self-review is performed
  and labelled a self-review rather than a trilens review. Flags were rejected as engine-fragile; free
  text matches `/lr:recall [hint]`.
- **Three termination guards:** round cap (default 3); a reviewer-gated stop (the loop may not end
  while any reviewer's latest verdict is `BLOCK` unless the host says out loud it is overriding); and
  **"a silent round is not a clean round"** (≥1 reviewer must actually return; retry once, and the
  retry does not count against the cap). The second guard exists because otherwise the same session
  writes the fixes *and* grades its own convergence.
- **Three-state ledger:** `APPLIED` / `DECLINED` / `ACCEPTED (not applied — report-only)`. The third
  state exists because "no fixes" is a legitimate amendment, and folding those into `DECLINED` would
  misreport agreed findings as rejected.
- **Reviewers default to regular model tiers** — sonnet on Claude Code, **gpt-5.4** on Codex,
  composer-2.5 on Cursor — escalating a single lens only on demonstrated need. Budget belongs in
  rounds and independence, not model size (user decision, 2026-07-25; measured backing in
  `parallel-reviewer-fanout-pattern.md` § Cost). *Codex name reconciled 2026-07-27:* **gpt-5.4** is
  correct; `release-notes/30.md:49` says gpt-4.5 and stays that way — shipped notes are a historical
  record, and the correction of record is in `release-notes/31.md`.
- **Lenses are ways of looking, not places to look.** Splitting by file or target gives three
  reviewers doing identical thinking on different slices. Codex's cheapest tier did exactly that
  (`diff` / `lore-context` / `references`) until the doc said otherwise explicitly. The three lenses
  stay fixed for the whole loop, and each brief tells its reviewer what the other two own.
- **Briefs carry the goal, not the rationale** — see `parallel-reviewer-fanout-pattern.md`
  § Brief the goal, not the rationale.

## Sibling non-overlap

The skill is **change-scoped**, which is what separates it from its state-scoped siblings: `/lr:check`
checks a domain's content consistency, `/lr:doctor` diagnoses runtime ailments. It is **not** part of
finalization — it never writes lore, never reflects, never merges, never commits.

## Naming

`trilens-loop` = three perspectives + "lens" (the framework's existing word for this) + the loop as a
first-class part of the feature. Rejected: `/lr:review` (collides conceptually with engine built-ins),
`/lr:trilens` (drops the loop), `/lr:review-cycle` (drops the lenses), `/lr:triad` (collides with
`positioning-triad-differentiation.md` vocabulary).

## Verification and known gaps

- Lifecycle scenarios 28–29 (`tests/lifecycle/test_trilens_loop.py`) drive it end-to-end on real
  engines against a planted uncommitted lore topic with a dangling cross-reference and a contradiction
  against committed fixture lore. Scenario 28 allows fixes and asserts the target file was edited; 29
  amends the flow to report-only and asserts the file is byte-identical afterwards — a filesystem
  check of the free-text rail rather than a self-report. Both assert three distinct lenses. **Green
  3/3 engines** (claude/haiku, codex/gpt-5.4-mini, cursor/composer-2.5).
- Dogfooded on its own changes: four rounds, **14 → 6 → 1 → 0** findings, 20 applied and 1 declined.
  That loop caught a self-contradiction between the free-text rule and the no-self-review rule, the
  named-teammate trap (hit live — see `docs-engines-convention.md` § Engine traps belong in the
  binding), an unsourced factual claim about Cursor's changelog, a fix-the-fixes miss across three
  files, and a lifecycle scenario-number collision.
- **Known flakiness, shipped as-is:** codex at `gpt-5.4-mini` intermittently returns
  `FINDINGS: none` on scenario 28 over a file with two planted defects — declaring a silent round
  clean instead of following the retry-then-report rule. 1 failure in 2 repeat runs with an unchanged
  doc, so it reads as weak-model variance rather than a procedure defect. The rule is correct but not
  binding enough for that tier.
- **Closed seam (2026-07-28):** Cursor `Task` accepts free-text briefs (`prompt` + `subagent_type`).
  Validated in-session; throwaway `.cursor/agents/` definitions are obsolete for trilens/merge briefs.
  See `cursor-task-free-text-brief-validated.md`. Brief shape ≠ end-to-end proof of every fan-out
  procedure — upgrade claims still need tool-call logs, not a green scenario alone.

## See Also

- `parallel-reviewer-fanout-pattern.md` — the practice this was promoted from; still the judgement
  layer (lens catalog, convergence profiles, stall handling, triage rules).
- `subagent-as-optimization-vs-subagent-as-semantics.md` — the principle that forbids a host-side
  fallback here and forced the v30 Cursor profile carve-out.
- `post-convergence-edits-need-their-own-gate.md` — a converged loop only certifies the artifact state
  it ran against.
- `execution-testing-catches-blind-ambiguity.md`, `lifecycle-testing-harness.md` — the separate
  empirical leg; v30's review loop converged clean *and* the lifecycle run then exposed a weak-model
  fidelity gap the four rounds had not predicted.
- `docs-engines-convention.md` — the two engine-profile corrections that shipped alongside.
- `versioning-release-types.md` — the v30 entry (release-notes-only, cache-affecting: yes).
- `lr-dev-direction.md` — where this was originally filed as `lr:dev-review`.
- `sonnet-subagent-review-pattern.md` — the single-lens sibling, unchanged by v30.
- `trilens-loop-v31-restructured.md` — **`docs/trilens-loop.md` has been reworked twice on the parked
  `wip/lr-core-v31` branch** (325 lines → one paragraph → a ~75-line structured doc with an explicit
  host/reviewer exchange contract). None of it is on main; this topic describes the doc as it stands
  on main today. Check `v31-lr-core-parked-2026-07-25.md` for the parking location before assuming
  either later version is live.
- `trilens-loop-deliberately-minimal-2026-07-25.md` — the don't-auto-restore rule governing that doc.
