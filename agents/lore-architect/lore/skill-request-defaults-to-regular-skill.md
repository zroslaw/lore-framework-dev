# "Make it a Skill" Defaults to a Regular Invokable Skill, Not a New Mechanism

When the user says "make it a skill" (or "deliver X as a skill in the lr framework"), default to the
**existing regular invokable skill pattern** — `skills/<name>/SKILL.md` → `docs/<name>.md`, a slash
command. Do **not** invent a framework subsystem (boot-loaded mechanism, new always-on entity) unless
the user explicitly asks for one. The word "skill" already has a concrete, cheap implementation here;
reach for that first.

**Origin (2026-07-05).** Asked to deliver a communication behavior "as a skill," I over-built: a
boot-loaded, framework-level *soft-skills* subsystem (`docs/soft-skills.md` + a new `agent-boot.md`
step loading it for every agent) — effectively trying to resolve the open "soft skills as a formal
entity" backlog item on the fly. The user corrected me: they wanted a regular invokable `/lr:` skill,
not a new boot-time mechanism. I reverted the subsystem cleanly and rebuilt as normal thin-pointer
skills (the `/lr:plain-language`, `/lr:dialogue`, `/lr:follow-me` set — see `style-skills.md`).

**Why this is the overreach reflex again.** Same family as
`feedback-schemas-as-enforcement-overreach.md` (adding machinery where a lightweight convention was
wanted). Reaching for a new subsystem when a plain convention/skill suffices is the recurring failure
mode; catch it early.

**Disposition for the backlog item.** A boot-loaded soft-skill mechanism was **considered and
rejected** this session. If "soft skills as a formal entity" (`framework-improvements-backlog.md` §
Soft Skills) is revisited, note the user preferred plain invokable skills for this need — the
always-on/boot-loaded machinery wasn't wanted.

**Secondary lesson: confirm the interpretation first.** I guessed the mechanism instead of confirming,
costing a build+revert cycle. For an ambiguous "make it a X" where X could mean more than one
mechanism, state the interpretation in one line before building — cheap insurance against a re-do.
Consistent with `feedback-confirm-before-writing-lore.md`.

See `style-skills.md`, `skill-doc-pattern.md`, `feedback-schemas-as-enforcement-overreach.md`,
`feedback-confirm-before-writing-lore.md`, `framework-improvements-backlog.md`.
