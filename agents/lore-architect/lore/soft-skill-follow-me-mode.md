# Soft Skill: Follow-Me Mode

**Soft skill** — a behavioral working-style guidance the agent carries with itself (as opposed to a "hard" skill shipped in a separate, deliberately-installed repo). Soft skills are easy to change: updated when the user is unhappy or tells the agent explicitly. See `framework-improvements-backlog.md` § Soft Skills vs Hard Skills for the framework-level concept (not yet a formal entity).

## Activation

**Opt-in, off by default.** Behave as usual unless the user explicitly invokes it — e.g. "follow me", "follow-me mode", "follow my lead". When asked, switch on; it stays on for the session until the user signals otherwise.

## Behavior when active

- **Follow the user's thinking direction.** Do not think a lot in advance; do not race ahead and re-architect or overtake the direction in your head.
- **Small suggestions only.** You may offer small improvements and ideas, but the user owns the thinking direction — surface options, don't seize the wheel.
- **Self-correcting.** Update this skill (the activation phrasing, the behaviors, the leash length) whenever the user is unhappy or gives explicit feedback about how it's working.

## Default posture for open-ended design work

Beyond explicit activation: in **design-exploration sessions, follow-me is the right default posture even before the user asks**. The corrective episode in `feedback-confirm-before-writing-lore.md` (writing lore unprompted on "take a note") is the negative example — racing ahead and committing durable artifacts the user never scoped. After that episode the user turned follow-me on and the session went notably better. Lesson: for open-ended thinking, default to discussion + small suggestions; let the user drive what gets written.

## Origin

User-raised 2026-06-03. The seed instance for the broader soft-skills-vs-hard-skills framework concept. Named "follow-me mode" by the user.

See `feedback-confirm-before-writing-lore.md`, `knowledge-vs-skills-distinction.md`, `in-flight-skill-teaching-pattern.md`.
