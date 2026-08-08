# Style — One Public Selector, Three Internal Components

`/lr:style` is the sole public Lore command for changing how the agent *communicates or
collaborates*, as opposed to framework *operations* like `/lr:recall`, `/lr:merge`, `/lr:boot`. It is
an ordinary thin-pointer skill (`skills/style/SKILL.md` → `docs/style.md`), so the same command model
works on Claude Code, Codex, and Cursor (using their respective plugin syntax).

It is a **regular invokable skill, not a boot-loaded mechanism.** A boot-loaded "soft skills"
subsystem was prototyped and deliberately rejected in favor of a plain `/lr:` skill — see
`skill-request-defaults-to-regular-skill.md` and `framework-improvements-backlog.md` § Soft Skills.
Nothing is surfaced or loaded at boot.

## The three internal components compose on three levels

- **`plain`** — *sentence* level. Plain, simple English: short clear sentences, one idea at a time,
  concise but not compressed. Motivated by the user reading English as a second language — dense prose
  costs real re-reading effort.
- **`dialogue`** — *turn* level. Short conversational turns; the one essential thing now, details on
  demand, no long articles. Keep the user's mental context in sync (they multitask and may lose
  track). Move one step at a time and let them steer.
- **`follow`** — *thinking-direction* level. The user drives; the agent follows with small
  suggestions and doesn't race ahead or re-architect. Extracted up from lore
  (`soft-skill-follow-me-mode.md`) to the framework; canonical definition remains in
  `lore-framework/docs/follow-me.md`.

The three stack cleanly (sentence / turn / thinking-direction). `/lr:style` accepts the exact
selectors `plain`, `dialogue`, `follow`, `all`, and `off`; selectors may be comma- or
space-separated. With no selector it uses `all`. Each call replaces the complete active set, so
`/lr:style dialogue follow` explicitly turns `plain` off if it was previously active. Invalid,
duplicate, and contradictory selector lists are rejected rather than guessed.

**Reading a multi-component selection.** Because the levels are orthogonal, choosing two or three
components says the last reply was wrong on each of those axes simultaneously, and is the strongest
form of the "too many words" feedback. Treat it as a stop signal: apply the selected set and hold it
until `/lr:style` changes it. Instance: 2026-07-27, all three at once after a measurement question
got an essay — see `feedback-too-many-words.md`.

## Status

Version 35 replaces the former three public commands with `/lr:style`; there are no old aliases.
The component documents remain separate canonical definitions beneath the single coordinator. This
is cache-affecting because engine catalogs can retain removed skills until their plugin cache refreshes.
When generated Cursor wrappers are removed or regenerated, parity verification must be genuinely
read-only: a `--check` mode that repairs drift is not verification.

## See Also

- `feedback-too-many-words.md` — the standing feedback these skills are the user's lever for; carries the multi-skill-invocation instance.
- `soft-skill-follow-me-mode.md` — follow-me's design history (seed of the abandoned soft-skills concept).
- `skill-request-defaults-to-regular-skill.md` — the "make it a skill" = regular skill default that shaped this category.
- `slash-command-system.md` — the `/lr:` skill naming and thin-pointer mechanics this follows.
- `framework-improvements-backlog.md` § Soft Skills — the framework-level concept, now resolved via this category.
