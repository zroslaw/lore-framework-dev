---
lore: 1
type: topic
summary: "Implemented for the v47 release candidate: finalize revises its participants before Phase 1 — best-fit host, uncapped additions with a cost note, and one confidentiality gate."
parent: lore-context.md
---

# Finalize Participant Revision

**Status: implemented in the v47 release candidate (commit `33c7461`), not published, merged, or
tagged.** First written 2026-10-03 in an autonomous design cycle
([feedback-autonomous-design-cycle.md](feedback-autonomous-design-cycle.md)); revised 2026-10-04 by
user decision in a design dialogue and re-reviewed (design rounds 4–6 and spec rounds 1–3, three
cold reviewers each, all ending without BLOCKER/HIGH). v47 is release-notes-only and
cache-affecting. The workdir pair preserves the original design and exact-edit record:

- `workdir/draft-finalize-participant-revision-design.md` — problem, design, edge cases,
  rejected alternatives, extension points, §9 review log;
- `workdir/draft-finalize-participant-revision-spec.md` — the exact edits.

The candidate passed a valid isolated Codex 0.160.0 nothing-booted (D3) dogfood run: it discovered
only the fixture workspace, selected and booted the role-fitting `helper-agent`, persisted a
release-calendar canary, and committed and pushed the fixture-local result. The complete
deterministic suite (635 tests across 17 modules, including 62 focused contract tests) and the
plugin check passed; the check's only finding was an unrelated stale Codex v32 cache backup.
Lifecycle and TriLens were intentionally not run. The abandoned
`v46-sync-hardening` worktree had no unique commits or diff beyond current main, so it was removed
rather than merged.

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
  topic, it stays. An already-attached guest can be promoted without a new attach. A demoted booted
  agent becomes an ordinary guest.
- **Selection guards:** knowledge squarely in the role and needed at its next boot; a named owner in
  the descriptions wins; judge the session, not quoted external content; knowledge *about* an agent
  is not *for* it (otherwise the chronicler pulls in every agent); precision over recall.
- **Uncapped additions with an explicit cost note:** each added agent costs a full attach, reflect
  and merge pass — "there is no cap, so use common sense: add every agent that clearly learned
  something, skip marginal ones". A hard cap stays an extension point.
- **Confidentiality is one gate line before step 1, failing closed**
  ([feedback-keep-confidentiality-guards-small.md](feedback-keep-confidentiality-guards-small.md)):
  if a repo *described* as confidential (routing map or `lore-repo.md`) is in use — an active
  agent's repo, files read from it, or an agent consulted from it — revision changes nothing; with
  nothing booted, finalize stops. The confidential line prints only when revision would have changed
  something, so routine sessions inside a confidential repo stay silent. Manual `/lr:attach` remains
  the override. Being one line, it can later be swapped for real visibility metadata as a unit.
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
  `skipped` (`--transcript` or the confidentiality gate).
- `--transcript` skips the section; standalone reflect, merge, and summarize are unchanged.
- **Edits outside `finalize.md`:** short summarize Step 3 / field-note edits, one consult sentence,
  one SKILL line; `attach.md` deliberately untouched.

## If changing this feature

Use the workdir pair for the original decisions, rejected alternatives, and exact-edit record; read
the current `finalize.md` before proposing a change. Lifecycle context:
[finalization-process.md](finalization-process.md).
