---
lore: 1
type: topic
summary: "Positions Lore Agents around growing AI teams, deliberate knowledge curation, collaboration, and practical proof."
parent: lore-context.md
---

# Core Positioning

Do not lead with generic "persistent memory." That category is crowded and makes Lore Agents sound interchangeable with tools that automatically preserve session history.

Lead with the concrete pain: agents need repeated context, guidance, and instructions for future sessions, so doing work manually can feel easier than delegating it. Lore Agents lets that work compound instead of restarting from context reconstruction.

Lead with this product idea:

> Build a team of named AI specialists that learns and grows with you.

Lore Agents are the named specialists themselves, not a separate coordinator that delegates to specialists. Guided by their roles and the user's feedback, they take responsibility for maintaining the context and instructions they need. Their curated, evolving context and knowledge is called **Lore**. The user retains direction and judgment while the agents perform the ongoing context maintenance.

Explain the product in layers: lead with the pain, working model, and benefit; introduce Git, Markdown, boot maps, reflection, merge, and other machinery afterward. A plain lifecycle is:

1. **Give a domain or project a named expert.** Define a clear role and domain so relevance has a boundary and the agent learns the right things instead of storing everything.
2. **Summon that expert through its registered direct shortcut.** Use `/lr:boot <agent-name>` as the generic fallback.
3. **Work together normally.** Supply resources, guidance, and feedback as the work develops.
4. **Finalize the session.** The agent reflects and merges durable lessons into Lore, using its role and domain to decide what is worth preserving.
5. **Return to accumulated expertise.** The next session begins with the agent's curated knowledge available.

When explaining technical anatomy, keep framework distribution separate from an individual agent's Lore. Put framework detail in getting started: Lore Agents is a plugin for Claude Code, Cursor, and Codex; its canonical behavior is expressed in Markdown instructions; and Python scripts only accelerate operations to save time and context tokens. Point readers to the canonical docs collection.

Describe Lore itself as the agent's Git-backed directory, not as a workspace. `role.md` defines the specialist's domain, `lore-context.md` carries essential every-session knowledge, and `lore/*.md` holds focused topics. The parent hierarchy forms a taxonomy while Markdown links form the wider knowledge graph; a generated Lore map makes both economical to navigate. At boot, the role, context, and map enter the agent's context. On complex work, the agent follows the map and uses ordinary shell, file-search, and read tools to open relevant topics. Finalization maintains the graph, Git supplies history, versioning, review, and sharing, and periodic grooming improves structure, links, concision, and retrieval.

The positioning has three connected pillars:

1. **Named, role-based specialists are the unit of knowledge.** An agent has an identity, responsibilities, and accumulated expertise that can span sessions and projects.
2. **Knowledge is deliberately curated.** Reflection and merge turn experience into useful working knowledge instead of automatically accumulating every interaction. Frame this as higher-quality, team-scale knowledge, not as extra maintenance.
3. **Specialists collaborate.** Agents recall their own knowledge and can consult, attach, and work with other agents' expertise.

The central mental model is a team of teammates: give specialists resources and tasks, work alongside them, and guide them when needed. In return, sustained work makes them more capable and self-sufficient over time. This is not automatic learning: reflection and finalization deliberately curate decisions, feedback, domain knowledge, and operational wisdom into durable expertise.

Git-backed Markdown, portability, team sharing, and support across coding engines are important supporting facts, but they are not the principal differentiation on their own.

The strongest current proof story is self-hosting: Lore Agents is developed with Lore Architect, a lore agent that holds the framework's design history and operational knowledge. Prefer this and other concrete demonstrations over abstract claims.

The first target audience is people who already use coding agents daily across multiple sessions or projects and are tired of repeatedly rebuilding context. This is a beachhead, not the category boundary. Start use cases with the broad continuity pattern, then show personal domains, research and evaluation, long-running projects, integrations, multi-specialist collaboration, and shared software expertise. Individual expertise can accumulate first and become team-shared by publishing the agent repo.

The voice mainly explains the practical product, then occasionally explores role-based agents, deliberate curation, shared team knowledge, and agent collaboration as design ideas. Even for technical audiences, do not reduce the core story to software engineering or the SDLC. Keep terminology exact: distinguish the Lore Agents framework from Lore Agents as named specialists whenever grammar or product meaning could be ambiguous.

Working pitch:

> A team of named AI specialists that learns and grows with you.

Short-description copy uses the same promise: "Named AI specialists that learn and grow with you."

Competitive positioning changes quickly. Recheck adjacent projects and public claims before a positioning-sensitive publication or launch. Several projects use "Lore" in adjacent categories, so discoverability and a distinctive identity require continuing attention.
