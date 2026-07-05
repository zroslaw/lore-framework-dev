# Style Skills — A Category of `/lr:` Skill

**Style skills** are user-invoked `/lr:` skills that change how the agent *communicates or
collaborates*, as opposed to framework *operations* like `/lr:recall`, `/lr:merge`, `/lr:boot`. They
are ordinary invokable skills in the standard thin-pointer shape (`skills/<name>/SKILL.md` →
`docs/<name>.md`, auto-discovered from `skills/`), so they work on any engine that reads `SKILL.md`
(Claude Code, Codex, Cursor). Named as a distinct category 2026-07-05.

They are **regular invokable skills, not a boot-loaded mechanism.** A boot-loaded "soft skills"
subsystem was prototyped this session and deliberately reverted in favor of plain `/lr:` skills — see
`skill-request-defaults-to-regular-skill.md` and `framework-improvements-backlog.md` § Soft Skills.
The user re-asserts a style by invoking its trigger phrase; nothing is surfaced or loaded at boot.

## The three built (2026-07-05) compose on three levels

- **`/lr:plain-language`** — *sentence* level. Plain, simple English: short clear sentences, one idea
  at a time, concise but not compressed. Motivated by the user reading English as a second language —
  dense prose costs real re-reading effort. Trigger: "plain language" / "plain and simple".
- **`/lr:dialogue`** — *turn* level. Short conversational turns; the one essential thing now, details
  on demand, no long articles. Keep the user's mental context in sync (they multitask and may lose
  track). Move one step at a time and let them steer. Trigger: "dialogue" / "keep it short".
- **`/lr:follow-me`** — *thinking-direction* level. The user drives; the agent follows with small
  suggestions and doesn't race ahead or re-architect. Trigger: "follow me". Extracted up from lore
  (`soft-skill-follow-me-mode.md`) to the framework; canonical definition now in
  `lore-framework/docs/follow-me.md`, the lore topic keeps design history + when-to-self-adopt
  guidance.

The three stack cleanly (sentence / turn / thinking-direction), so they can be active together.

## Status

All three are **built but uncommitted**, deliberately held to ship with the **codex-adoption
release** (not v18 / lr-wait — they were pulled out of v18's release notes). Files:
`skills/{plain-language,follow-me,dialogue}/SKILL.md`, `docs/{plain-language,follow-me,dialogue}.md`.
`/lr:check` should pass on them (standard thin-pointer shape); give them a release-notes entry at the
port version when it's cut. Tracking + resume detail in `port-landing-next-steps.md`.

## See Also

- `soft-skill-follow-me-mode.md` — follow-me's design history (seed of the abandoned soft-skills concept).
- `skill-request-defaults-to-regular-skill.md` — the "make it a skill" = regular skill default that shaped this category.
- `slash-command-system.md` — the `/lr:` skill naming and thin-pointer mechanics these follow.
- `port-landing-next-steps.md` — where the uncommitted ship status is tracked.
- `framework-improvements-backlog.md` § Soft Skills — the framework-level concept, now resolved via this category.
