---
lore: 1
type: topic
summary: "The v44 Skill Purpose Announcement convention (drafted, unshipped): every skill opens with a Step 0 announcement authored in its own doc, written as onboarding material in framework vocabulary."
parent: lore-context.md
---

# Skill Purpose Announcement convention (v44 draft)

Every skill prints a short user-facing announcement before its first procedural step, in a
`## Step 0 — Announce` section holding one instruction line and the announcement itself as a
blockquote.

**Status: drafted, not shipped.** The work lives uncommitted in the worktree
`.worktrees/lore-framework/v44-skill-announcements` on branch `v44-skill-announcements`. The user
intends to extend it in a later session, so v44 has **no** entry in
[versioning-release-types.md](versioning-release-types.md) — that topic is a shipped-release history,
and adding a draft to it would make an unshipped version look released.

## Origin

User observation, 2026-08-30: `/lr:workspace-init` and `/lr:workspace-status` "just silently start to
do smth on the background." Legible to the author, opaque to an adopter. The framing that decided the
shape: announcements are **onboarding material, not status lines** — reading them in sequence teaches
the framework's vocabulary without a separate tutorial.

## Design decisions and why

- **Authored per skill, in that skill's own doc.** My first proposal was a shared rule doc that all
  33 skills point at, justified by `single-canonical-source-discipline.md`. The user rejected it, and
  was right: the *rule* is shared, the *text* is not. The generalized lesson is
  [per-site-authoring-is-not-duplication.md](per-site-authoring-is-not-duplication.md).
- **`## Step 0 — Announce`, before the first procedural step.** Location decides whether an
  instruction runs; Step 0 is the one position a paged doc cannot skip past
  ([instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)).
- **Framework concepts, never internals.** "I pull its lore agent repo," not the script that does it.
  The reader is an engineer who has not read our source. My first drafts named `lr-core` calls and
  were rejected for it.
- **Bold the one thing a newcomer is most likely to get wrong** — judged per skill. I first proposed
  a mechanical rule (always bold what the skill does to your files); the user rejected it as verbose
  and mis-targeting, because a fixed slot makes several announcements end on a limp "nothing is
  changed" while the genuinely surprising thing goes unmarked. **A formatting rule that fires the
  same way every time stops carrying information.**
- **Say "subagent".** I wrote "a separate helper" for generalization; the user's correction:
  "everyone knows what subagent is... 'helper' brings more confusion then generalization." Do not
  soften engineering vocabulary for an engineering audience.
- **"Lore agent repo", not "repo",** wherever a git repo holding agents is meant — a workspace
  commonly holds both those and the ordinary source repos the agents work on.
- **Explain the basics every time, briefly.** Explain-once-per-session was considered and rejected:
  it is a rule each of 33 docs would have to implement, with no reliable way for a skill to know what
  already ran in the session.

## Shape facts worth keeping

33 skills, but not 33 docs. `list-agents` and `list-repos` have no companion doc and carry Step 0 in
`SKILL.md`; the two `df-*` skills live under `df/`, not `docs/`; and `register-repo.md` backs **four**
skills, so its Step 0 branches on the invoked operation. Editing a Cursor mirror's source
(`skills/*/SKILL.md`) requires re-running `scripts/sync-cursor-skills` — which is **python3, not
bash**, despite carrying no extension.

The convention text lives in `conventions.md` § Skill Purpose Announcement.

## Known gap

There is **no mechanical enforcement** — no `/lr:check` item verifies Step 0 presence. That is a gap,
not a decision, and it is worth closing when v44 resumes: a convention with no check drifts, and this
one has 33+ sites to drift across
([consistency-checks.md](consistency-checks.md), `point-of-use-guardrails-beat-recorded-lore.md`).

## See Also

- [per-site-authoring-is-not-duplication.md](per-site-authoring-is-not-duplication.md) — the design
  rule this case produced.
- [step-number-cross-references-fail-silently.md](step-number-cross-references-fail-silently.md) —
  inserting this Step 0 into `agent-boot.md` is what surfaced that trap.
- `skill-doc-pattern.md`, `slash-command-system.md` — where skills and their docs are specified.
- `adopter-command-surface-curation.md` — the adjacent newcomer-facing IA work this feeds.
