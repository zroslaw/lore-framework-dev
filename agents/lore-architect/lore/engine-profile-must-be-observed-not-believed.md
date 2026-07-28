# The Engine Profile Must Be Observed, Not Believed

**A binding must not be selected by the thing it binds.** The engine profile governs how a model
executes every step after boot — invocation syntax, subagent spawning, memory file, runtime
bounding. Letting the model decide which profile applies makes the model the authority on its own
execution contract.

## What went wrong (2026-07-28)

`agent-boot.md` Step 0 used to hand the model an ordered prose ladder and ask it to pick its own
engine. Booting as lore-architect I skipped the ladder entirely and answered "claude" from
out-of-band self-knowledge — the harness system prompt says which engine I am. Right answer, no
evidence.

Worse, **the ladder as literally written would have said `codex`.** One rung read "else if a
`~/.codex/` directory exists → codex", and this machine has Codex installed. The correct answer and
the documented procedure disagreed, and nothing in the boot would have surfaced that.

Two distinct defects, and the second is the general one:

1. **The rung was unsound.** The presence of another engine's config directory tests whether that
   engine is *installed*, never whether it is *running*. On any multi-engine workstation it fires
   for every session regardless of engine.
2. **The selector was the selected.** A model's belief about its own identity is not an observation
   of the running process. The two diverge exactly where a wrapper, an unusual install, or a nested
   subagent makes the profile matter most.

## The family this belongs to

Sibling of `a-gate-cannot-be-a-model-self-report.md`: there, a gate must not be implemented in the
medium it gates; here, a binding must not be selected by the thing it binds. Same diagnostic
question in both cases — **what evidence does this rest on, and could the thing under test have
produced that evidence?**

## Applied

Fixed in `scripts/lr-core` as `detect_engine`, reported as `data.engine` by preflight and consumed
at `agent-boot.md` Step 2. Ordered signals:

1. explicit `--engine` override (for a test harness or a user correcting a misdetection)
2. `CLAUDE_PLUGIN_ROOT`
3. process ancestry
4. framework-root containment
5. default, explicitly marked `confidence: "assumed"` rather than presented as a finding

**Ancestry matches the program** — the basename of the first argv field — never a substring of the
command line. Substring matching is wrong in both directions here: a shell sourcing
`~/.claude/shell-snapshots/…` reads as Claude Code, and `/Applications/Cursor.app/…/Cursor` reads as
Cursor when it is really another engine running inside Cursor's integrated terminal.

`agent-boot.md` Step 0 now states the rule directly: do not infer the engine yourself, and in
particular do not infer it from what you believe you are. The Manual Boot Procedure repeats it,
because engine selection is the step a model is most likely to think it can skip.

## Operational rule

**When a procedure step's input is a fact about the running environment, the step belongs in the
deterministic accelerator, not in prose.** Prose asks a model to observe; a script actually observes.

## See Also

- `a-gate-cannot-be-a-model-self-report.md` — the sibling rule, one layer over (verification rather
  than binding selection).
- `removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md` — what deleting the bad
  `~/.codex/` rung cost, and the rule that fell out of it.
- `literate-accelerator-pattern.md` — why `detect_engine`'s own comments are the normative spec for
  the manual path.
- `point-of-use-guardrails-beat-recorded-lore.md` — the same "put it where it executes" reflex.
- `docs-engines-convention.md` — the profile convention this selects into.
- `graduated-verification-confidence.md` — why the no-signal branch reports `assumed` instead of
  silently asserting a default.
