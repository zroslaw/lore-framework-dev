# Cross-Engine Team Substrate — Validated

A three-engine (Claude, Codex, Cursor) collaboration ran end-to-end on the v32 shortcut-bootstrap
design via an ad hoc shared-folder protocol: `workdir/v31-feedback/` holding `PROTOCOL.md`,
`STATUS.md`, append-only `messages/NNN-<engine>.md`, and `CONCLUSION.md` on convergence. It went
through two full cycles — design-to-verdict (rounds 1–4) and a build-classification/release-
readiness round (round 5) — with **no protocol rewrite**, only a vocabulary shift
(proposal/agree/counter → must-complete/not-required/admin) between rounds.

## What's reusable vs. task-specific

The substrate proved reusable; the message-type vocabulary did not need to be fixed in advance:

- **Shared folder** as the coordination surface — no shared process, no live session, just files
  under version control (or at least a shared filesystem) that every engine's session can read and
  append to.
- **Append-only log** (`messages/NNN-<engine>.md`) — sequential, attributable, never edited after
  the fact.
- **Filename-owns-uniqueness on sequence collisions** — if two engines write `messages/003-*.md`
  concurrently, the filename itself (including the engine suffix) disambiguates; no locking needed.
- **Mutual idle-exit** — the protocol ends when all participants agree nothing changed since the
  last round, not on a fixed round count.
- **Evidence-in-the-opening-message** — each round's first message states what was verified and
  how, not just a conclusion, so downstream participants can corroborate or contest specific claims
  rather than re-deriving them.
- **Task-defined vocabulary** — the message-type enum (proposal/agree/counter, or must-complete/
  not-required/admin, or whatever a future task needs) is *not* part of the reusable substrate. Let
  each task define its own; don't try to design one universal taxonomy up front.

## Operational recommendation

Next time multiple engine sessions need to coordinate on a real task (not just a review pass),
reach for this shared-folder pattern directly rather than reinventing session-log conventions —
cite `lore-framework-dev/agents/lore-architect/workdir/v31-feedback/` as the worked example, and
`workdir/draft-cross-engine-team-feature.md` as the drafted feature proposal (reviewed live by
Cursor: agreed that a bare scaffold + one worked example beats a template-per-task-type, and one
continuous thread beats phase folders by default — Codex had not weighed in on the draft before
session end, an open thread if the feature proposal is revisited).

## See Also

- `same-agent-multiple-engines-single-writer.md` — the write-ownership rule discovered mid-use of
  this same substrate, when two of the three engine sessions turned out to be the same agent
  identity.
- `cross-engine-relay-not-attributable-authority.md` — the trust rule discovered in the same
  collaboration: one session's paraphrase of a user decision is not authority for another session
  to act on.
- `independent-engine-review-catches-structural-blind-spots.md` — what the collaboration actually
  caught (a structural design flaw and a corroborated bug), as opposed to how it was run.
- `multi-engine-portability-direction.md` — the broader cross-engine direction this substrate
  serves; this topic is about *how sessions coordinate*, that one is about *engine parity*.
- `versioning-release-types.md` — the v32 entry records this collaboration as the design process
  behind the shortcut-bootstrap release.
- `spawn-teammate-feature.md` — a different cross-agent mechanism (in-session Agent Teams
  teammates, single engine); this substrate is for *separate sessions on separate engines*
  instead.
