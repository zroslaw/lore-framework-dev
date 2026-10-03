---
lore: 1
type: topic
summary: "DRAFT (2026-10-03, awaiting user review, intended v47): /lr:finalize revises which agents participate before Phase 1 — settled shape, guards, confidentiality rule, and where the full design and spec live."
parent: lore-context.md
---

# Finalize Participant Revision (Draft Design)

**Status: DRAFT, not implemented.** Written 2026-10-03 in an autonomous design cycle
([feedback-autonomous-design-cycle.md](feedback-autonomous-design-cycle.md)); the user reviews it
first. Implementation is planned for a later session as **v47** (release-notes-only,
cache-affecting). Authority is the workdir pair, not this summary:

- `workdir/draft-finalize-participant-revision-design.md` — problem, design, edge cases E1–E19,
  rejected alternatives, extension points, three-round review log;
- `workdir/draft-finalize-participant-revision-spec.md` — the exact edits.

## Problem

`/lr:finalize` should decide which workspace agents learn from the session: the session drifted,
the wrong agent was booted, nothing was booted, or a consulted agent should keep something.

## Settled shape

- **Key insight.** Finalization is already correct for any active-agent set; only the *set* is
  wrong. So the design adds one unnumbered `finalize.md` section, *Before Phase 1 — Revise the
  participants*, acting only through existing attach and boot (boot when nothing is booted, which
  also selects the engine profile).
- **Zero new terms, data, code, or flags.** One honest redefinition: at finalization, "host" means
  the *finalization host* — the booted agent, unless none of the session's durable knowledge
  plausibly belongs to its role and an added agent's does. A demoted booted agent becomes an
  ordinary guest.
- **Selection guards:** knowledge squarely in the role and needed at its next boot; a named owner in
  the descriptions wins; judge the session, not quoted external content; knowledge *about* an agent
  is not *for* it (otherwise the chronicler pulls in every agent); precision over recall.
- **Confidentiality fails closed on existing descriptions.** If an active agent's repo is described
  as confidential, or the session handled its material, additions are restricted to that same repo
  and held-back agents are named in the notice. A machine-checkable visibility field was rejected
  for now and kept as an extension point.
- **Notice:** an Operation Notice ([operation-notice-convention.md](operation-notice-convention.md)),
  printed *before* applying, only when something changes or is held back. The re-run rule
  re-evaluates rather than trusting an earlier notice — attach confirmations are the record
  ([a-state-file-is-a-hint-not-a-verdict.md](a-state-file-is-a-hint-not-a-verdict.md) § intent
  notices).
- **Completion line:** the SKILL completion line reports `revised` / `checked, no change` /
  `skipped`.
- **Revision never stops a finalize when an agent is booted** — every failure falls back to today's
  behavior ([an-optional-step-must-fail-back-to-baseline.md](an-optional-step-must-fail-back-to-baseline.md)).
- `--transcript` skips the section; standalone reflect, merge, and summarize are unchanged.
- **Edits outside `finalize.md`:** three short summarize Step 3 / field-note edits, one consult
  sentence, one SKILL line; `attach.md` deliberately untouched.

## When resuming

Read the design's review log before changing anything — it records what was applied, accepted, or
declined and why. Lifecycle context: [finalization-process.md](finalization-process.md).
