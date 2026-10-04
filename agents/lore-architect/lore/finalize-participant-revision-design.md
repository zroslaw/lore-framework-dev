---
lore: 1
type: topic
summary: "Shipped in v47: finalize revises its participants before Phase 1 — best-fit host, uncapped additions with a cost note, and one confidentiality gate."
parent: lore-context.md
---

# Finalize Participant Revision

**Status: shipped as v47 (2026-10-04, tag `lr--v1.47.0` at `17ba607`; implementation commit
`33c7461`).** First written 2026-10-03 in an autonomous design cycle
([feedback-autonomous-design-cycle.md](feedback-autonomous-design-cycle.md)); revised 2026-10-04 by
user decision in a design dialogue and re-reviewed (design rounds 4–6 and spec rounds 1–3, three
cold reviewers each, all ending without BLOCKER/HIGH). v47 is release-notes-only and
cache-affecting. The workdir pair preserves the original design and exact-edit record:

- `workdir/draft-finalize-participant-revision-design.md` — problem, design, edge cases,
  rejected alternatives, extension points, §9 review log;
- `workdir/draft-finalize-participant-revision-spec.md` — the exact edits.

Validation: an isolated Codex 0.160.0 nothing-booted dogfood run booted the role-fitting
`helper-agent` and persisted a canary; the deterministic suite (684 tests, 49 skipped, measured at
polish tip — see [a-release-record-goes-stale-while-you-fix-it.md](a-release-record-goes-stale-while-you-fix-it.md))
and the plugin check passed. Lifecycle: `FinalizeParticipantRevisionScenarios` in
`tests/lifecycle/test_finalize.py` (`test_14` wrong-host, `test_15` nothing-booted), green on Cursor
`composer-2.5` against the v47 worktree (2026-10-04); see
[lifecycle-testing-harness.md](lifecycle-testing-harness.md). The broader lifecycle suite and
TriLens were intentionally not run. The abandoned `v46-sync-hardening` worktree had no unique
commits beyond main and was removed.

## Problem

`/lr:finalize` should decide which workspace agents learn from the session: the session drifted,
the wrong agent was booted, nothing was booted, or a consulted agent should keep something.

## Settled shape

- **Key insight.** Finalization is already correct for any active-agent set; only the *set* is
  wrong. So the design adds one unnumbered `finalize.md` section, *Before Phase 1 — Revise the
  participants*, acting only through existing attach and boot (boot when nothing is booted, which
  also selects the engine profile).
- **Zero new terms, data, code, or flags.** One honest redefinition: at finalization, "host" means
  the *finalization host*.
- **Host = best fit by role** (2026-10-04, [feedback-host-follows-best-role-fit.md](feedback-host-follows-best-role-fit.md)),
  judged by matching the session's topic and results against agents' role descriptions. The booted
  agent keeps close calls: it is replaced only when **both** the main topic (where most effort went)
  and the main result lie in another agent's role; if they disagree or there is no clear main
  topic, it stays. When revision picks a new host that is **already attached**, **promote in place**
  — do not re-run `/lr:attach`. The displaced booted agent becomes an ordinary guest and stays in
  the active set for reflect, merge, and summarize; Phase 4 still commits its repo when its tree
  changed.
- **Selection guards:** knowledge squarely in the role and needed at its next boot; a named owner in
  the descriptions wins; judge the session, not quoted external content; knowledge *about* an agent
  is not *for* it (otherwise the chronicler pulls in every agent); precision over recall.
- **Uncapped additions with an explicit cost note:** each added agent costs a full attach, reflect
  and merge pass — "there is no cap, so use common sense: add every agent that clearly learned
  something, skip marginal ones". A hard cap stays an extension point.
- **Confidentiality gate — after selection, before apply, failing closed**
  ([feedback-keep-confidentiality-guards-small.md](feedback-keep-confidentiality-guards-small.md)):
  run the check **after** choosing the proposed host and automatic additions, **before** any boot or
  attach. It covers a confidential repo already in use **and** a confidential repo belonging to a
  proposed automatic addition (including the nothing-booted case "boot this host"). Discovering a
  confidential candidate without selecting it is allowed; only **selected** automatic participants
  trigger the gate. When it fires: skip apply, keep the original participants, report outcome
  `skipped` — including when no revision was planned (a quiet notice, still `skipped`, not `checked,
  no change`). With nothing booted and the gate fires, finalize stops. Manual `/lr:attach` remains
  the override. Being one gate line, it can later be swapped for real visibility metadata as a unit.
- **Demoted booted agent still commits.** Phase 4 must commit its repo when the session changed
  files under its agent dir — `finalize.md`'s *No empty commits* invariant would otherwise skip it
  (verified in the source; see
  [settle-conflicting-reviewer-claims-in-the-source.md](settle-conflicting-reviewer-claims-in-the-source.md)).
  The exception is written into that invariant itself, where Phase 4 reads it (2026-10-04 re-read).
- **Notice:** an Operation Notice ([operation-notice-convention.md](operation-notice-convention.md)),
  printed *before* applying, only when something changes. The re-run rule re-evaluates rather than
  trusting an earlier notice — attach confirmations are the record
  ([a-state-file-is-a-hint-not-a-verdict.md](a-state-file-is-a-hint-not-a-verdict.md) § intent
  notices).
- **One stop rule, stated once:** only with nothing booted — no agent qualifies, a confidential repo
  is in use, or the host's boot fails — finalize prints `Nothing to finalize: <reason>.` and stops
  with nothing written. A booted agent is never dropped; with one, every failure falls back to today's
  behavior ([an-optional-step-must-fail-back-to-baseline.md](an-optional-step-must-fail-back-to-baseline.md)).
- **Completion line:** names the final host and reports `revised` / `checked, no change` /
  `skipped` (`--transcript` or the confidentiality gate). A participant-revision **Operation Notice**
  states intent only — not evidence that revision happened. Outcome `revised` requires a **successful**
  boot, attach, or in-place host promotion. If every proposed attachment fails and the original host
  remains, report `checked, no change` even when a revising notice printed. Partial success (some
  attaches succeed while the proposed host fails) still counts as `revised`, with the booted agent
  retained as host.
- `--transcript` skips the section; standalone reflect, merge, and summarize are unchanged.
- **Edits outside `finalize.md`:** short summarize Step 3 / field-note edits, one consult sentence,
  one SKILL line; `attach.md` deliberately untouched.

## If changing this feature

Use the workdir pair for the original decisions, rejected alternatives, and exact-edit record; read
the current `finalize.md` before proposing a change. Lifecycle context:
[finalization-process.md](finalization-process.md).
