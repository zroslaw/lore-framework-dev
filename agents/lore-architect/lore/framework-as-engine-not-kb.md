# Framework-as-engine, not knowledge base

**Foundational framing principle.** When introducing the Lore Framework to newcomers, lead with **"LRF is the environment, engine, and tooling for running self-improving Lore Agents"** — not "LRF is a team-shared knowledge base."

The knowledge base is a *consequence* of how Lore Agents persist their state. It is not the framework's identity. Leading with KB framing produces three predictable problems:

1. Readers picture a static, curated artifact (Confluence-shaped) and miss the self-improvement / learning-by-doing dynamic that's the actual point.
2. The question "why not just use a wiki?" surfaces immediately and is hard to dispel.
3. The agent-as-executor framing gets lost — agents become "tools that read the KB" rather than "specialized AI co-workers that get better with use."

The correct layering when explaining the framework:

1. **LRF (engine, environment, tooling)** — what runs and operates the system. Claude Code is the substrate; LRF is the layer that turns it into a host for Lore Agents.
2. **Lore Agents (self-improving specialized AI agents)** — the unit of value. They execute tasks, accumulate knowledge and skills via reflection, share state via git.
3. **Knowledge + skills (per-agent persisted state)** — what each agent carries. Knowledge is info in markdown. Skills are tools + instructions. Both grow. See `knowledge-vs-skills-distinction.md`.
4. **Synergy effect (KB-and-skills sharing)** — what *emerges* when multiple people use the same agents. Team accumulation, org-scale value, adoption-compounds-value dynamic.

Surfaced when drafting the Lore Agents Intro for the Activities team — initial drafts framed LRF as "a knowledge-and-skills sharing system" and were rejected three times before the correct framing landed.

Companion to `team-shared-knowledge-principle.md` (which is true at the *outcome* layer); this principle covers the *identity* layer. Together with `agents-are-executors-first.md`, these three name the foundational identity claims of the framework: shared (not personal), engine (not KB), executor (not advisor).

Per `naming-foundational-principles.md` — name foundational framings as their own topics rather than leaving them implicit in the mechanisms they motivate.
