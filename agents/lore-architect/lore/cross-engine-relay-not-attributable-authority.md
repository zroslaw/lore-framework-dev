# Cross-Engine Relay Is Not Attributable Authority

When the user gave a release-gate decision — (a) full lifecycle proof first, or (b) ship locally
under a recorded waiver — in the Claude session, I relayed it into the shared cross-engine
coordination thread (`cross-engine-team-substrate-validated.md`) as settled fact. Codex and Cursor
both correctly refused to act on it: a `VERSION` bump / merge / commit is consequential enough that
one engine's paraphrase of what the user said is not attributable authority for another engine's
session to execute on. Each of them asked their own session's user directly and recorded the
confirmation with its own source/timestamp in `STATUS.md` before proceeding.

This is the same principle the framework's own permission rules already run on — explicit,
per-action, per-session; one approval doesn't generalize to another actor — just discovered from the
other side. I was the one whose relay got correctly distrusted, not the one distrusting a relay. A
good sign the multi-engine trust model is sound, rather than friction to route around.

## Operational rule

**When a decision gates an irreversible or cross-session action, don't relay a user decision from
one session into a shared coordination channel as if it settles things for other sessions.** Flag
explicitly that the other sessions need their own direct confirmation, and don't proceed yourself
until they have it either. Proceeding on your own relay while the others correctly wait for their
own confirmation is exactly the state that produces a three-way divergent-state race — one engine
acting on unverified secondhand authority while the others stall correctly.

## Why this matters beyond the specific session

The same reflex generalizes past cross-engine coordination: any time a coordinating agent is
tempted to short-circuit "ask the human" by citing what a *different* human-facing session already
decided, that's the same move — reusing an identity/authority signal it doesn't actually have. It's
the authority-side twin of `reuse-existing-correlation-signal.md` (which is about *design-time*
plumbing reuse being good); here, reusing someone else's confirmation as your own is bad, precisely
because the confirmation was never given to *you*.

## See Also

- `cross-engine-team-substrate-validated.md` — the shared-folder collaboration this was discovered
  in.
- `same-agent-multiple-engines-single-writer.md` — the companion write-ownership rule from the same
  session.
- `graduated-verification-confidence.md` — the general confidence-not-boolean framing this rule is
  an instance of (a relayed decision is lower-confidence evidence than a direct confirmation, even
  when the content is identical).
