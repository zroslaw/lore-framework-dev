---
lore: 1
type: topic
summary: "Positions Lore Agents around growing AI teams, deliberate curation, collaboration, and practical proof, with the market-verified and contested claims."
parent: lore-context.md
---

# Core Positioning

Do not lead with generic "persistent memory." That category is crowded and makes Lore Agents sound interchangeable with tools that automatically preserve session history.

Lead with the concrete pain: agents need repeated context, guidance, and instructions for future sessions, so doing work manually can feel easier than delegating it. Lore Agents lets that work compound instead of restarting from context reconstruction.

Lead with this product idea:

> Build a team of named AI specialists that learns and grows with you.

**This wording is contested in every component** and is due for a deliberate re-cut — see
[claims verified against the market](#claims-verified-against-the-market) below. The underlying
product idea stands; the phrasing is what the market has already occupied.

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
2. **Knowledge is deliberately curated.** Reflection and merge turn experience into useful working knowledge instead of automatically accumulating every interaction. Frame this as higher-quality, team-scale knowledge, not as extra maintenance. This is a contrarian posture rather than an invention: the rest of the market automates capture, and mem0 explicitly calls manual curation a "scaling wall" it exists to eliminate. Claim the posture and the reason for it, never the novelty.
3. **Specialists collaborate.** Agents recall their own knowledge and can consult, attach, and work with other agents' expertise.

The central mental model is a team of teammates: give specialists resources and tasks, work alongside them, and guide them when needed. In return, sustained work makes them more capable and self-sufficient over time. This is not automatic learning: reflection and finalization deliberately curate decisions, feedback, domain knowledge, and operational wisdom into durable expertise.

Git-backed Markdown, portability, team sharing, and support across coding engines are important supporting facts, but they are not the principal differentiation on their own — and the git substrate specifically is no longer ours to claim. Letta shipped Context Repositories (Markdown with YAML frontmatter in a real git repo, syncable to a GitHub remote) on 2026-02-12, and Claude Code ships a native per-subagent `memory:` field whose `project` scope is documented as shareable through version control. Leading with the substrate invites an easy and correct rebuttal. Re-cut it as a **review and distribution** claim instead: expertise as a team artifact you clone, correct in a pull request, and publish. Letta's announcement never mentions pull requests, review, or teams, so that framing is unoccupied.

State the storage stance explicitly and before the file list: there is **no external knowledge base and no vector storage** — Lore Agents instead rely on what AI coding agents already do well, exploring, searching, and reading their own documents. This preempts the reader's assumption that this is another embeddings-and-retrieval product and reframes the absence as a deliberate bet on agent capability, not a missing feature.

At workspace scale the pieces compound rather than merely existing, and this is the flagship setting for public copy: multiple domains and agent repos, each specialist owning its own area; agents working **on top of the real source code of adjacent systems**, grounding Lore in it rather than in a detached note store; and dynamic expertise, where a working agent summons the specialist owning a neighboring domain with `/lr:attach` when a task crosses a boundary. The payoff is big, interconnected software areas — services, libraries, teams — that no single context holds at once; the workspace becomes a living map maintained by the agents who work in it. This is the strongest available answer to "isn't this just notes?" Frame it as a superlative about one setting ("where it shines brightest"), never as "built for" or "designed for" — hold it against the rule above not to reduce the core story to software engineering or the SDLC, and sequence it after the storage and collaboration story and before non-software use cases, so the emphasis cannot collapse into a developer-only claim.

The strongest current proof story is self-hosting: Lore Agents is developed with Lore Architect, a lore agent that holds the framework's design history and operational knowledge. Prefer this and other concrete demonstrations over abstract claims.

The first target audience is people who already use coding agents daily across multiple sessions or projects and are tired of repeatedly rebuilding context. This is a beachhead, not the category boundary. Start use cases with the broad continuity pattern, then show personal domains, research and evaluation, long-running projects, integrations, multi-specialist collaboration, and shared software expertise. Individual expertise can accumulate first and become team-shared by publishing the agent repo.

The voice mainly explains the practical product, then occasionally explores role-based agents, deliberate curation, shared team knowledge, and agent collaboration as design ideas. Even for technical audiences, do not reduce the core story to software engineering or the SDLC. Keep terminology exact: distinguish the Lore Agents framework from Lore Agents as named specialists whenever grammar or product meaning could be ambiguous.

Working pitch, pending the re-cut described below:

> A team of named AI specialists that learns and grows with you.

Short-description copy currently uses the same promise: "Named AI specialists that learn and grow with you."

## Claims verified against the market

Verified on 2026-09-12 against the durable evidence base in
[market research](../workdir/market-research/README.md); its index carries a corrections log and
supersedes any single study file. Competitive positioning changes quickly, so recheck before any
positioning-sensitive publication or launch — but recheck against that archive rather than starting
over.

**The strongest verified claim available:** across the three largest subagent collections —
wshobson (39.6k), VoltAgent (25.0k), contains-studio (12.4k), about 76k stars combined — **0 of 981
agent definitions use the `memory:` field**. Roughly a thousand named specialists exist and none of
them remember anything. It was measured by clone-and-grep, so it is checkable rather than asserted,
and it is the cleanest one-line statement of what Lore adds.

**Also defensible:** role as the relevance boundary for what an agent learns — nobody else has this,
as the rest of the market filters by recency, importance, embedding, or file size; agents consulting
one another's separate knowledge bases; and cross-engine support combined with per-agent durable
knowledge.

**Crowded, avoid:** "a team of AI specialists" (CrewAI 58.4k, BMAD 52.9k, wshobson 39.6k); "AI
coworkers" and "memory that compounds" (OpenAI Frontier uses nearly this wording); "agents that
remember across sessions" (saturated); "plain Markdown you own, no lock-in" (basic-memory, Agentage);
"git-backed agent memory" (Letta got there first). Every component of the current tagline sits in
that list.

**Frame benefits as workflow and continuity, not accuracy.** GitOfThoughts (arXiv 2606.14470, June
2026) tested five memory stores and found cross-problem agent memory did not improve accuracy on new
problems. A hostile critic can cite it, so do not stand on ground that paper already took.

**Closest competitor is Letta Code** (~3.3k stars), which reaches roughly 3.5 of our 5 axes. It stops
short on roles (its subagents are generic utilities; memory is an identity, not a professional
remit), on deliberate curation, on cross-engine support (it is its own harness), and on team review.

Once a re-cut pitch is selected, hold it. Rewriting positioning repeatedly correlates with losing —
see [growth evidence](growth-evidence.md).

## The name collision

**"Lore" is already taken twice in this exact category:** `BYK/loreai` (withlore.ai, 110 stars,
actively pushed) positions itself as our direct opposite — "No context files. No workflow changes." —
and `makenotion/lore` (142 stars, Aug 2026) is Notion's "AI memory backed by Notion". Discoverability
and a distinctive identity are both at risk.

The decision is open. At zero stars the cost of renaming will never be lower than it is now, and it
rises every week. Decide it on collision risk alone: mem0's rename produced its largest growth event,
but only because it inherited a ~9K-star audience and GitHub Trending ranks stars *gained*, so a
rename here buys correctness rather than attention. Revisit before any public article or directory
submission, since both bake the name in.
