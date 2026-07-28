# Feature idea: Cross-Engine Team (working name)

Correction to the first cut of this idea: what we did in `v31-feedback/` wasn't a review feature
that happens to generalize — **review-to-a-verdict was one instance of a more general primitive**,
an ad hoc team of separate engine sessions coordinating on a shared task through a folder. The
task shape shouldn't be baked in. Right now, unprompted, we're already in the *next* phase of the
same team effort: Codex is implementing what we agreed, off in its own session, invisible to me
until it's done. If the primitive existed, that would be happening *in the same folder* instead.

## Why the substrate, not the task shape, is the reusable part

`/lr:spawn-teammate` already solves same-engine teamwork — Agent Teams, parallel panes, one
engine. There's no cross-engine equivalent because there's no native spawn mechanism that crosses
engine boundaries: Claude can't spawn a Codex subagent. A shared folder + append-only message log
+ polling is the only transport available that doesn't require any engine to know the others
exist. That part — the substrate — is what's actually reusable. What ran on top of it (proposal →
counter → agree → CONCLUSION.md) was just the vocabulary this particular task needed.

## Task shapes it should support

- **Converge to a decision** (what we just did) — debate-shaped: proposal/response/counter/agree/
  dissent, ending in a written conclusion.
- **Divide and conquer** — build-shaped: claim a piece, report progress/blocked/done, hand off
  results. This is what's happening *right now* with Codex's implementation pass, just not routed
  through the shared folder.
- **Relay** — sequential handoff, not parallel debate: one engine researches, hands to another to
  implement, hands to a third to verify. Different again from both of the above.

None of these should be hardcoded as *the* protocol. What we actually did — Cursor wrote
`PROTOCOL.md` defining message types for *this* task, everyone followed it, Cursor patched it live
mid-thread when a seq collision appeared — is itself the right shape: the opening session defines
the vocabulary the task needs, the skill just scaffolds the folder and the poll/idle-exit
mechanics, not a fixed type enum.

## What has to generalize from the review-specific version

- **`STATUS.md`'s `converged: yes/no`** is debate-shaped (everyone agrees on one proposal). A build
  task wants a task list with owners and per-item status instead of one boolean — closer to a
  shared TODO board than a verdict.
- **`CONCLUSION.md`** generalizes to "artifact(s)" — a review produces one conclusion doc; a build
  task might produce a diff per engine and no single document at all.
- **Message types** stay task-defined (see above), not fixed by the skill.

## What to keep exactly as we improvised it

- **Seq-collision handling**: filename owns uniqueness (`NNN-<engine>.md`); on a race, both stand;
  next writer takes `max(seq)+1`. This isn't task-specific — bake it into the scaffold itself.
- **Mutual idle-exit**: stop polling after N minutes of silence, leave a note, don't read silence
  as agreement — also not task-specific, belongs in the scaffold.
- **Evidence over claims in the opening message** — the reason this converged in 9 messages
  instead of drifting.

## Open questions

- Does the skill need task-type templates (a "review" starter vs. a "build" starter), or is a bare
  scaffold + an example enough for the opening engine to define its own vocabulary each time?
- Same-folder-forever vs. phases: should "decide" and "implement" be two folders/threads with a
  handoff between them, or one continuous thread that changes vocabulary partway through (as we're
  about to do right now, informally, once Codex's implementation needs review)?
- Auto-file completed work into `framework-improvements-backlog.md` / commit it, or stay a
  workdir-only artifact the user files by hand?

## Relationship to Lore Beings

Different problem: Beings are long-running autonomous background agents; this is
synchronous-attention-required on every side, just decoupled in time by engine, not by design. The
poll/idle-exit shape is close enough to `lr-wait`'s signal/wake primitive that the mechanism might
be shared rather than reinvented per feature.
