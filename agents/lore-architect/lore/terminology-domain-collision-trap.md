# Terminology trap: "Domain" — LRF term vs loose English

**Hard rule when writing for newcomers:** "Domain" is reserved for the LRF technical concept (top-level working directory where Claude Code is launched, scanned for agent repos at direct children, etc. — see `domain-directory-concept.md`). When the loose-English meaning is intended (subject area, problem area, area of expertise), use a different word: **area, subsystem, project, field of application**.

The collision is subtle and devastating. Both meanings are natural English; both are likely to appear in adjacent paragraphs of an onboarding doc; readers cannot tell which is meant; the moment they fail to disambiguate, the entire mental model breaks down.

Caught the hard way during the Activities team Lore Agents Intro: an early draft used "Domain" to describe what an agent covers ("a Lore Agent dedicated to a domain") *in the same paragraph* that introduced "Domain" as the LRF concept. The user reacted strongly. Six occurrences had to be swept and replaced with "area" / "subsystem" / "area-specific."

**Audit hygiene:** when writing or reviewing newcomer-facing prose, grep for "domain" and read every occurrence in context. Each one must be unambiguously the LRF technical sense; otherwise replace it.

This is a specific instance of the broader principle: **terminology hygiene matters most in onboarding docs**. Readers don't yet have the disambiguation context veterans take for granted. Reusing a defined term in its loose-English sense is the most reliable way to confuse them.

**Companion patterns to watch for:**

- "Lore" — defined LRF term, but also natural English. Less collision-prone but worth watching.
- "Agent" — overloaded across LLM industry usage; LRF's "Lore Agent" is specific. Always qualify when the distinction matters.
- "Skill" — LRF plugin skills (`/lr:*`) vs an agent's skills (tools + instructions). These now refer to the same kind of artifact in some cases but the framing differs. See `knowledge-vs-skills-distinction.md`.

When introducing any LRF term that has a natural-English homonym, name the collision explicitly in the definition and pick a different word for the natural-English sense. Better awkward phrasing than reader confusion.

**v11 vocabulary update:** "domain" was further refined — "Domain" now refers specifically to the *conceptual scope* of a single agent repo, while the *filesystem* sense (the dir Claude runs from) is now called **workspace**. The split matters because the framework now has skills (`/lr:workspace-sync`) and schemas (`repos:`) that operate at the filesystem level — calling that "domain" would have collided with both the agent-repo-scope sense and the loose-English sense. See `workspace-vs-domain-vocabulary.md` for the full split and disambiguation rules.

Companion of `onboarding-doc-narrative-pattern.md` — terminology hygiene is one of its tone rules, surfaced here as its own topic because the failure mode is independent and recurrent.
