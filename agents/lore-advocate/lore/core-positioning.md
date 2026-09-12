---
lore: 1
type: topic
summary: "Positions Lore Agents around growing AI teams, role-bounded whole-session learning, collaboration, and practical proof, with the market-verified and contested claims and the settled name decision."
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
2. **Knowledge is role-bounded and taken from the whole session.** Two properties carry this pillar, and neither of them is "manual". First, reflection runs at the end of a session, over the entire session: with the full arc in view the agent can judge what mattered, what turned out wrong, and what was noise. Competitors extract from fragments — mem0 and CrewAI pull facts out of individual task outputs, Letta's sleeptime process fires roughly every five steps — so they summarize pieces without knowing how the story ended. Second, the agent's **role is the relevance boundary**: the role decides what is worth keeping in the first place, which is what keeps the knowledge base focused rather than merely large. Everyone else preserves everything and filters at retrieval time by similarity, recency decay, importance heuristics, or inferred scope — hoarding plus search. The contrarian contrast with mem0's "scaling wall" still holds, but the axis is **focused vs. everything**, never **manual vs. automatic**. Claim the posture and the reason for it, never the novelty.
3. **Specialists collaborate.** Agents recall their own knowledge and can consult, attach, and work with other agents' expertise.

The central mental model is a team of teammates: give specialists resources and tasks, work alongside them, and guide them when needed. In return, sustained work makes them more capable and self-sufficient over time. Reflection and merge turn decisions, feedback, domain knowledge, and operational wisdom into durable expertise. Do not frame that as the user approving what the agent learns. Finalization being user-invoked is an implementation detail — it can be triggered automatically when a session goes stale or is archived — so human approval is not an axis we compete on, and claiming it makes us the slow, high-maintenance option in a market that is automating.

Git-backed Markdown, portability, team sharing, and support across coding engines are important supporting facts, but they are not the principal differentiation on their own — and the git substrate specifically is no longer ours to claim. Letta shipped Context Repositories (Markdown with YAML frontmatter in a real git repo, syncable to a GitHub remote) on 2026-02-12, and Claude Code ships a native per-subagent `memory:` field whose `project` scope is documented as shareable through version control. Leading with the substrate invites an easy and correct rebuttal. Re-cut it as a **review and distribution** claim instead: expertise as a team artifact you clone, correct in a pull request, and publish. Letta's announcement never mentions pull requests, review, or teams, so that framing is unoccupied.

State the storage stance explicitly and before the file list: there is **no external knowledge base and no vector storage** — Lore Agents instead rely on what AI coding agents already do well, exploring, searching, and reading their own documents. This preempts the reader's assumption that this is another embeddings-and-retrieval product and reframes the absence as a deliberate bet on agent capability, not a missing feature.

At workspace scale the pieces compound rather than merely existing, and this is the flagship setting for public copy: multiple domains and agent repos, each specialist owning its own area; agents working **on top of the real source code of adjacent systems**, grounding Lore in it rather than in a detached note store; and dynamic expertise, where a working agent summons the specialist owning a neighboring domain with `/lr:attach` when a task crosses a boundary. The payoff is big, interconnected software areas — services, libraries, teams — that no single context holds at once; the workspace becomes a living map maintained by the agents who work in it. This is the strongest available answer to "isn't this just notes?" Frame it as a superlative about one setting ("where it shines brightest"), never as "built for" or "designed for" — hold it against the rule above not to reduce the core story to software engineering or the SDLC, and sequence it after the storage and collaboration story and before non-software use cases, so the emphasis cannot collapse into a developer-only claim.

The strongest current proof story is self-hosting: Lore Agents is developed with Lore Architect, a lore agent that holds the framework's design history and operational knowledge. Prefer this and other concrete demonstrations over abstract claims.

The first target audience is people who already use coding agents daily across multiple sessions or projects and are tired of repeatedly rebuilding context. This is a beachhead, not the category boundary. Start use cases with the broad continuity pattern, then show personal domains, research and evaluation, long-running projects, integrations, multi-specialist collaboration, and shared software expertise. Individual expertise can accumulate first and become team-shared by publishing the agent repo.

The voice mainly explains the practical product, then occasionally explores role-based agents, role-bounded learning, shared team knowledge, and agent collaboration as design ideas. Even for technical audiences, do not reduce the core story to software engineering or the SDLC. Keep terminology exact: distinguish the Lore Agents framework from Lore Agents as named specialists whenever grammar or product meaning could be ambiguous.

Working pitch, pending the re-cut described below:

> A team of named AI specialists that learns and grows with you.

Short-description copy currently uses the same promise: "Named AI specialists that learn and grow with you."

**Direction for the re-cut, not a decision.** The user pointed toward *"a team of virtual
self-learning and self-growing AI experts"* on 2026-09-12 and explicitly deferred the final wording.
The logic is that "named specialists" is the crowded half (CrewAI 58.4k, BMAD 52.9k, wshobson 39.6k)
while the growth property is what the subagent collections demonstrably lack. The tension to resolve
before adopting it: "that learn" is itself contested (OpenAI Frontier, claude-mem, mem0, Letta), so
this shifts weight onto the other crowded component. Whatever wording is selected has to carry what
actually distinguishes us — whole-session reflection and the role as the relevance boundary — rather
than a bare promise of learning. Develop it as explicitly compared variants, implement only the
selected one, and then hold it.

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

**The number means nothing to a first-time reader without setup, so never state it first.** Tested
live: the compressed archive form (three collection names, star counts, "981 definitions, zero use
the memory field") did not land and needed a full rephrase. Budget three to five short sentences
ahead of it, in this order: these GitHub collections of ready-made AI agents are very popular (76k
stars across three) -> one of those "specialists" is just a Markdown file holding instructions, a
prompt with a job title -> Claude Code has a `memory:` setting, one line that gives an agent a notes
folder it reads back later -> we downloaded all three collections, counted 981 agent files, and
searched for that line, and found zero -> so the market already loves named specialists, and every
one of them starts each session blank. The compressed form stays correct for the archive and for
readers already inside the category.

**Also defensible:** role as the relevance boundary for what an agent learns — nobody else has this,
as the rest of the market filters by recency, importance, embedding, inferred scope, or file size;
and reflection over a whole session rather than over individual task outputs or an N-step interval; agents consulting
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
short on roles, on curation control, on cross-engine support (it is its own harness), and on team
review. The concrete evidence for the roles gap is its `persona.md`, which sits in the always-loaded
`system/` tier and reads *"I am a Letta agent. I remember durable preferences and improve with use."*
That is a personality and a voice, not a declared domain, so nothing there bounds what the agent
considers worth saving. Its subagents — `recall`, `history-analyzer`, plus the "dreaming" and
"memory doctor" workers — are staff for the memory system, not named professionals with domains; the
word is shared, the concept is not, so never let a comparison table imply equivalence. Its default
update path is continuous and unattended (tool edits auto-commit; sleeptime fires on a step
interval); `/remember` is the exception. Same substrate, opposite control model.

**CrewAI (58.4k stars) is the orchestration contrast.** An agent there is config with three text
fields — `role`, `goal`, `backstory` — grouped into a crew that `crewai run` executes once and
exits; the definition never changes on its own, so the team is a list in a config file rather than
colleagues who develop. The one-line contrast that works: **they orchestrate agents; we accumulate
expertise** — their agents are workers you configure, ours are specialists you teach. Since
2026-09-12 they do ship memory (a unified API with agent-level scoping, LLM-inferred scopes, and a
LanceDB vector store), so do not claim they have none; claim that capture is automatic, model-decided,
unbounded by any declared role, and binary on disk rather than reviewable. Their phrase "a team of AI
specialists" remains unavailable to us. Both CrewAI and mem0 run the same business model — free OSS
library, paid enterprise platform — which is the category default; not doing it should be a stated
choice rather than an omission.

Once a re-cut pitch is selected, hold it. Rewriting positioning repeatedly correlates with losing —
see [growth evidence](growth-evidence.md).

## The name collision

**The name is settled: we keep "Lore Agents."** The user decided this on 2026-09-12 after being
walked through the full collision evidence. Do not re-open it or re-present the rename case unless
the user raises it.

The collision itself is accepted context and still shapes copy. "Lore" is taken twice in this exact
category: `BYK/loreai` (withlore.ai, 110 stars, actively pushed) positions itself as our direct
opposite — "No context files. No workflow changes." — and `makenotion/lore` (142 stars, Aug 2026) is
Notion's "AI memory backed by Notion". Two consequences to work with rather than around:

- **SEO expectations are bounded.** We will not out-rank Notion for "lore agent memory", so
  discovery has to come from the channels in [channel strategy](channel-strategy.md), not from
  owning the word.
- **Public copy must state our stance explicitly.** A competitor markets the opposite philosophy
  under the same word, so the name cannot be assumed to carry the meaning; say what Lore is.
