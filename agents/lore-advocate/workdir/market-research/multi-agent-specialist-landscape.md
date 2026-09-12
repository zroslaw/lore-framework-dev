# Multi-Agent Specialist Landscape — Does Anything Already Do What Lore Agents Does?

**Researched:** 2026-09-12
**Subject:** Competitive landscape for [Lore Agents / lore-framework](https://github.com/zroslaw/lore-framework)
**Researcher:** lore-advocate market-research sweep, second entry in this archive
**Method:** Web search and page fetches of primary sources (vendor docs, vendor blogs, GitHub READMEs); GitHub REST API for repository metadata until the unauthenticated rate limit was exhausted, after which figures came from rendered GitHub pages; and **direct inspection of cloned repositories** for the subagent-collection question. Primary sources (vendor docs, repo contents) are distinguished from secondary (blogs, reviews, aggregators) throughout. Every volatile figure is date-stamped in place and decays.

---

## The five comparison axes

Lore Agents is compared against everything below on these five axes, restated from the framework's own defining properties:

1. **Named specialists with roles.** Not one general assistant. You boot a specific agent — a tax advisor, a health advisor, a framework architect — each with a declared role and domain. The role defines the relevance boundary for what that agent learns and keeps.
2. **Per-agent persistent curated knowledge ("Lore").** Each agent accumulates its own body of knowledge across sessions, and it is **deliberately curated, not automatically captured**: an explicit reflect step extracts what is worth keeping, and a merge step integrates it.
3. **Git-backed plain Markdown, team-shareable.** Knowledge lives as small Markdown topic files in git repos. A teammate can read, review, and change an agent's expertise in a pull request. Agents are shared by cloning a repo.
4. **Agents collaborate.** One agent can consult another (one-shot question), attach another as a guest for sustained co-work, or recall across several loaded agents at once.
5. **Cross-engine.** Runs on Claude Code, Codex, and Cursor from the same repo.

---

## Summary — the direct answer

**No single product ships all five axes together, but the answer is much less comfortable than "no competition," and two findings should change how Lore Agents positions itself.** First, **axis 3 is not a differentiator and has not been one since February 2026**: Letta shipped [Context Repositories](https://www.letta.com/blog/context-repositories/) on 2026-02-12, storing per-agent memory as Markdown-with-YAML-frontmatter in a real git repository that can be pointed at a GitHub remote, and Anthropic shipped a native per-subagent `memory:` field in Claude Code v2.1.33 (February 2026) whose `project` scope writes Markdown to `.claude/agent-memory/<name>/` and is documented as "shareable via version control." Lore Agents did not get to git-backed Markdown agent memory first, and claiming novelty there is falsifiable in one search. Second, **the closest competitor overall is Letta Code**, which combines per-agent persistent memory, Markdown files, git versioning, remote sync, and a background reflection process — roughly three and a half of the five axes. Where the field is genuinely empty is narrower and more specific than "git-backed memory": it is the combination of a **declared role that acts as the relevance boundary for learning**, a **user-invoked reflect→merge step as the default learning path** (the entire rest of the market is sprinting in the opposite direction — mem0 explicitly describes manual curation as a "scaling wall" it exists to eliminate), **named agents consulting each other's separately-maintained knowledge bases**, and **cross-engine portability**, which every close competitor lacks because each one is welded to a single harness. The crux question the lead asked — do the big subagent collections give their specialists durable knowledge — has a hard, verified answer: **no. Zero of 981 agent definitions across the three largest collections use the `memory:` field.** That is the real white space, and it is defensible.

---

## 1. The closest competitors, ranked

### 1st — Letta Code (`letta-ai/letta-code`) — **closer than expected**

- **URL:** https://github.com/letta-ai/letta-code · docs https://docs.letta.com/letta-code/memfs
- **Adoption:** ~3,300 stars (2026-09-12, GitHub repo page). Parent repo `letta-ai/letta` 24,704 stars (2026-09-12, GitHub API).
- **Who:** Letta (formerly MemGPT), venture-backed; the MemGPT paper lineage.
- **Commercial model:** open-source harness plus a hosted Letta API / cloud tier.

**What it actually does.** Letta Code is a standalone agent harness — a direct competitor to Claude Code, not a plugin for it. Its memory system, **MemFS**, is documented as a "git-backed memory filesystem that they can inspect and edit." Per the docs: *"Each memory is projected as Markdown with YAML frontmatter"*, laid out in a directory hierarchy (`system/`, `reference/`, `skills/`), and *"Every memory edit is committed to the MemFS git repository. This provides version history, conflict resolution, and a clear boundary between saved memory and uncommitted changes."* Memory can be pointed at a user's own GitHub remote with `/memory-repository set git@github.com:...`. There is an explicit `/remember` command, and a background "dreaming"/sleeptime process that consolidates lessons.

**Where it stops short.**
- **Axis 1 (roles) — weak.** Its built-in subagents are generic utilities (`general-purpose`, `forked`, `recall`, `history-analyzer`). There is no concept of a declared domain that bounds what an agent considers relevant. Memory is organized as `persona.md` / `human.md` — an *identity*, not a *professional remit*.
- **Axis 2 (deliberate curation) — inverted.** The default is automatic: every memory edit auto-commits, and sleeptime agents fire on a step interval (default every 5 steps) to rewrite memory without the user asking. `/remember` exists but is the exception, not the path. Lore's reflect→merge is user-invoked and end-of-session; Letta's is continuous and unattended.
- **Axis 3 (team review) — substrate yes, workflow no.** This is the important nuance. The git plumbing is there and is genuinely ahead of Lore's public claim. But the [Context Repositories announcement](https://www.letta.com/blog/context-repositories/) **does not mention pull requests, code review, or team-level memory sharing anywhere**. The framing is personal continuity and cross-device sync ("commits push back to the hosted repository"), not "your colleague reviews what your agent learned." *(Some secondary summaries infer team review from the git substrate; that inference is not supported by Letta's own text. Flagged as unverified.)*
- **Axis 5 (cross-engine) — no.** Letta Code is its own harness. It is cross-*model* (OpenAI, Anthropic, Z.ai) but you cannot run a Letta agent inside Claude Code, Codex, or Cursor. This is a structural gap, not a roadmap gap.

**Honest verdict: ~3.5 / 5.** On the axis Lore has been treating as its differentiator, Letta shipped first and shipped more. Lore's remaining edge over Letta is the role boundary, deliberate curation, cross-engine portability, and the review workflow as a stated practice.

---

### 2nd — Claude Code native subagent memory + Agent Teams (Anthropic)

- **URL:** https://code.claude.com/docs/en/sub-agents · https://code.claude.com/docs/en/agent-teams
- **Adoption:** bundled with Claude Code; effectively the largest distribution of any candidate here.
- **Commercial model:** proprietary, subscription/API.

**What it actually does.** Since v2.1.33 (February 2026), a subagent's frontmatter accepts `memory: user | project | local`. Per the docs: *"The `memory` field gives the subagent a persistent directory that survives across conversations. The subagent uses this directory to build up knowledge over time, such as codebase patterns, debugging insights, and architectural decisions."* The `project` scope writes to `.claude/agent-memory/<name-of-agent>/` and is described as *"project-specific and shareable via version control."* The first 200 lines / 25KB of `MEMORY.md` is auto-injected into the system prompt.

That is axis 1 (named specialists), a large part of axis 2 (per-agent durable knowledge), and a meaningful part of axis 3 (Markdown, in-repo, git-reviewable) shipped natively by the platform Lore Agents runs on.

**Where it stops short.**
- **Axis 2 (curation) — shallow.** Knowledge is written opportunistically mid-session by instruction in the system prompt. The only curation trigger documented is *size*: instructions to curate `MEMORY.md` fire when it exceeds 200 lines or 25KB. That is compaction, not selection-for-relevance. There is no reflect step, no merge step, no session-end lifecycle.
- **Axis 2 — possibly not even working.** [Issue #57507](https://github.com/anthropics/claude-code/issues/57507) reports the `memory:` field non-functional as of v2.1.137 (May 2026), with detailed telemetry ("empty memory directory after 5+ invocations in 3 days"). It was **closed as not planned** and is unconfirmed by maintainers. Treat as a credible community report, not established fact.
- **Axis 3 — one flat file per agent.** `MEMORY.md` with a 200-line injection ceiling is not a topic-file corpus with retrieval. It does not scale to a body of expertise.
- **Axis 4 (collaboration) — explicitly siloed.** Agent Teams give teammates messaging, a shared task list, and independent context windows — but teammates carry **no durable knowledge**, team directories are *"cleaned up automatically when the session ends,"* and per-subagent memory directories are siloed from each other: the code-reviewer cannot see what the security-auditor learned ([Hindsight, 2026-05-06](https://hindsight.vectorize.io/blog/2026/05/06/claude-code-subagents-shared-memory)). Agent Teams are also experimental and **disabled by default** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).
- **Axis 5 — none.** Claude Code only.

**Honest verdict: ~2.5 / 5**, but strategically the most dangerous entry on this list, because it is free, native, zero-install, and a plausible "good enough" for most users. Anything Lore says about per-agent Markdown memory must survive the question *"isn't that just the `memory:` field?"*

---

### 3rd — BMAD-METHOD (`bmad-code-org/BMAD-METHOD`)

- **URL:** https://github.com/bmad-code-org/BMAD-METHOD
- **Adoption:** 52.9k stars, 6.0k forks (2026-09-12, GitHub repo page). MIT.
- **Commercial model:** open source, MIT.

Ships a full cast of named specialists — Analyst, Product Manager, Architect, Developer, QA, Scrum Master, UX — each defined as Markdown and YAML files in git, installed via CLI, and **tool-agnostic across Claude Code, Codex, Cursor and Copilot**. Agents hand work to each other through file-based document handoffs.

That is axes **1, 3 (partial), 4, and 5** — four of five, at 52.9k stars, from a project most people in this space have heard of.

**Where it stops short — and it is the whole point.** BMAD agents **do not accumulate knowledge**. They produce per-project artifacts (a requirements doc, an architecture doc) and start the next project blank. What is version-controlled and reviewable is the agent's *prompt* and the project's *specs*, never a body of expertise the agent grew. Axis 2 is absent. BMAD is a *process* framework wearing the clothes of a team; Lore is a *learning* framework.

**Verdict: high surface overlap, zero overlap on the core.** The single biggest positioning risk in this report, because a skim-reader will conflate them.

---

### 4th — The large subagent collections — *the crux question, answered*

The lead asked whether the big community collections give each specialist durable knowledge or just a static prompt. **Verified by cloning each repository and grepping every Markdown file on 2026-09-12:**

| Collection | Stars (2026-09-12) | `.md` files | Files with a `memory:` frontmatter field |
|---|---|---|---|
| [wshobson/agents](https://github.com/wshobson/agents) | 39,576 | 767 | **0** |
| [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | 25,021 | 176 | **0** |
| [contains-studio/agents](https://github.com/contains-studio/agents) | 12,414 | 38 | **0** |
| **Total** | **76,011** | **981** | **0** |

*(Star counts via GitHub API, 2026-09-12. Repositories cloned at `--depth 1` and inspected directly; `grep -rl '^memory:'` returned zero matches in all three.)*

**Nearly 1,000 named specialist agents across 76,000 stars of community adoption, and not one of them has durable knowledge.** They are static prompts. wshobson/agents is notable for being genuinely multi-harness (Claude Code, Codex, Cursor, OpenCode, Copilot, Antigravity) — it has axis 1 and axis 5 and still has nothing on axis 2.

This is the strongest, most defensible finding in the report, and it is the clearest way to explain what Lore Agents adds.

---

### 5th — basic-memory (`basicmachines-co/basic-memory`)

- **URL:** https://github.com/basicmachines-co/basic-memory · https://basicmemory.com/
- **Adoption:** 3,935 stars (2026-09-12, GitHub API). AGPL-3.0.

Plain Markdown notes in a local folder, one note per entity, with a link-based semantic graph, served to any MCP host — Obsidian-compatible and git-versionable. Strong on axis 3's substrate and axis 5.

**Stops short:** it is **one shared knowledge base, not per-agent** (axis 1 and axis 2's "per-agent" clause both fail), notes are written automatically by the assistant during conversation (axis 2's curation clause fails), and there is no agent-to-agent consultation (axis 4 fails). Closest analogue to Lore's *storage*, nothing like its *structure*.

---

## 2. Comparison table — top 10 candidates against the five axes

Legend: **Y** = ships it and markets it · **P** = partial, or possible with configuration but not shipped as the default · **N** = no.

| # | Product | Stars / adoption (2026-09-12) | 1. Named roles | 2. Per-agent curated knowledge | 3. Git Markdown, team-reviewable | 4. Agents collaborate | 5. Cross-engine | Score |
|---|---|---|---|---|---|---|---|---|
| — | **Lore Agents** (baseline) | 0 stars | Y | Y | Y | Y | Y | 5.0 |
| 1 | **Letta Code** | ~3.3k | P | P (auto by default) | Y (substrate) / P (workflow) | P | N | ~3.5 |
| 2 | **BMAD-METHOD** | 52.9k | Y | **N** | P (specs, not learning) | Y | Y | ~3.5* |
| 3 | **Claude Code native** (`memory:` + Agent Teams) | bundled | Y | P (shallow; possibly broken) | P (flat `MEMORY.md`) | P (siloed) | N | ~2.5 |
| 4 | **wshobson/agents** | 39.6k | Y | **N** (0/767 verified) | P (prompts only) | P | Y | ~2.5 |
| 5 | **Letta server** (`letta-ai/letta`) | 24.7k | P | P (auto: sleeptime) | N (database) | P | N | ~1.5 |
| 6 | **CrewAI** | 58.4k | Y | N | N | Y | N | 2.0 |
| 7 | **basic-memory** | 3.9k | N | P (auto-written) | Y | N | Y | ~2.5 |
| 8 | **Notion Lore** (`makenotion/lore`) | 142 | P (`Agent:` field) | N (auto-capture) | P (shared, not git) | P | Y | ~2.0 |
| 9 | **mem0** | category leader | N | **N** (explicitly anti-curation) | N | N | Y | 1.0 |
| 10 | **OpenAI Frontier** | enterprise, closed | Y | P (auto "compounding") | N | Y | N | ~2.0 |

\* BMAD's ~3.5 is misleading and the table should never be shown without the footnote: it scores on four axes while scoring **zero on axis 2**, which is the one that defines the category.

**Also evaluated, all scoring ≤1.5 and none overlapping on axis 2 or 3:** AutoGen (60.9k), MetaGPT (70.3k), LangGraph (41.5k), ChatDev (34.3k), cognee (30.7k), supermemory (29.6k), OpenAI Agents SDK (29.4k), Swarm (22.0k), CAMEL-AI (17.7k), agent-squad (7.8k, now `2FastLabs/agent-squad`), Zep (4.9k), AG2 (4.9k), Agency Swarm (4.6k). *(All star figures 2026-09-12, GitHub API.)* These are orchestration libraries: they give you named roles for the duration of a run and nothing survives it.

---

## 3. Is axis 2 — deliberate curation, not automatic capture — unique?

**Very nearly, and more importantly the entire market is moving the other way.** This is the strongest genuine differentiator, stronger than axis 3.

**What everyone else does is automatic capture:**

- **mem0** states the case against curation explicitly: manual curation *"eventually hits a scaling wall, which is why auto-capture sends each exchange to Mem0 after the agent responds"* ([mem0.ai](https://mem0.ai/blog/mem0-memory-for-openclaw)). Its pipeline is three automatic LLM passes — Write (extract facts), Manage (add/update/delete), Read.
- **claude-mem** (93.7k stars, 2026-09-12) captures *everything* the agent does and compresses it with an LLM — the purest form of the opposite approach, and the most adopted project in the adjacent space.
- **Cursor Memories** generates memories automatically with importance scoring, Hebbian association and consolidation — sophisticated, and entirely unattended.
- **Claude Code's `memory:`** is written opportunistically mid-task; its only curation trigger is file size.
- **cognee, supermemory, Zep** are auto-ingest graph/vector stores.

**The nearest things to deliberate curation:**

- **Letta's `/remember`** — a genuine user-invoked save. But it sits beside auto-commit-on-every-edit and interval-triggered sleeptime consolidation, so it is an override, not the path.
- **Letta's sleeptime agents** — these do *reflect*: *"the sleep-time agent will reflect on the original context to iteratively derive a learned context"* ([docs.letta.com](https://docs.letta.com/guides/agents/architectures/sleeptime/)). This is the single closest analogue to Lore's reflect step. **The difference is who decides and when:** Letta's fires automatically every N steps in the background; Lore's is invoked by the user at session end. That distinction is real but it is narrow, and it is a distinction of *control*, not of *capability*. Do not overstate it.
- **agentmemory** (`jayzeng/agentmemory`) ships a `MEMORY.md` described as "curated long-term memory" alongside auto daily logs — partial, small adoption.
- **Akephalos** — a local-first Markdown portable agent profile synced via plain files and git. Long-tail; not verified in depth.

**Verdict:** the *concept* of reflection is thoroughly trodden in research (Reflexion, generative agents, and the 2026 arXiv reflection-agent literature) and Lore cannot claim to have invented it. What appears genuinely unclaimed is **shipping user-invoked reflect→merge as the default and only learning path, with a declared role as the relevance filter for what qualifies.** No product found markets that. Claim the *posture*, not the invention.

---

## 4. Is axis 3 — git-reviewable knowledge a human edits in a PR — unique? **Tested hard: no.**

This axis was the leading hypothesis for the real differentiator. **It does not survive contact with the evidence, and this is the finding most likely to be expensive if ignored.**

Prior art that clearly predates or matches any Lore Agents public claim:

| Evidence | Date | What it establishes |
|---|---|---|
| [Letta Context Repositories](https://www.letta.com/blog/context-repositories/) | **2026-02-12** | Per-agent memory as text-with-YAML-frontmatter in a git repo; *"every change to memory is automatically versioned with informative commit messages"*; syncable to a user's GitHub remote |
| [Letta MemFS docs](https://docs.letta.com/letta-code/memfs) | current | *"Each memory is projected as Markdown with YAML frontmatter"*; hand-editable with ordinary file tools |
| [Claude Code `memory: project`](https://code.claude.com/docs/en/sub-agents) | **Feb 2026** (v2.1.33) | `.claude/agent-memory/<name>/`, Markdown, documented as *"shareable via version control"* |
| [basic-memory](https://github.com/basicmachines-co/basic-memory) | 2024-12 onward | Plain Markdown knowledge base, git-versionable, human-editable |
| [GitOfThoughts](https://arxiv.org/abs/2606.14470) | 2026-06 | Academic: agent memory as a git repo — *"replay, diff, and merge"* |
| [AGENTS.md ecosystem](https://visualstudiomagazine.com/articles/2026/02/24/in-agentic-ai-its-all-about-the-markdown.aspx) | 2026 | Markdown as a reviewable, diffable agent-control surface is now an industry norm, used by OpenAI Codex, Sentry, Apache Airflow, Temporal, Cloudflare |

**What survives.** The *substrate* is commodity. What no vendor found in this sweep actually markets is the **social workflow**: an agent's accumulated expertise treated as a team asset that a colleague reviews and amends in a pull request, and agents distributed to a team by cloning a repo. Letta's own announcement mentions no pull requests, no code review, and no team sharing; its framing is personal cross-device continuity. Claude Code says "shareable via version control" in a table cell and builds nothing around it.

**So the claim must be re-cut.** Not *"we store agent knowledge in git"* — that is 2026 table stakes and at least two competitors said it first. But *"an agent's expertise is a reviewable team artifact; you onboard a colleague's tax advisor by cloning a repo and you correct it in a PR"* — that framing is unoccupied. It is a workflow and distribution claim, not a storage claim.

---

## 5. WHITE SPACE — what genuinely nobody is doing

Ordered by defensibility.

1. **Durable knowledge attached to a large library of named specialists.** Verified: 0 of 981 agent definitions across the three biggest collections (76k stars combined) have any memory. The market has mass-produced specialist *prompts* and given none of them a *memory*. Lore sits exactly in that gap. **This is the single most defensible claim in the report.**
2. **A declared role as the relevance boundary for learning.** Every memory system found decides what to keep by recency, importance score, embedding similarity, or file size. None decides by *"is this within this agent's professional remit?"* Letta's memory is an identity (`persona.md`), not a remit. No competitor found has this concept at all.
3. **Named agents consulting each other's separately-maintained knowledge bases.** Lore's consult / attach / multi-agent recall has no real equivalent. Orchestration frameworks pass *messages and tasks* between agents; Claude Code teammates are explicitly siloed and evaporate at session end; Letta subagents share one agent's memory rather than querying a peer's independent corpus. Cross-expert knowledge consultation is effectively unoccupied.
4. **Cross-engine plus per-agent durable knowledge, together.** Every close competitor is welded to one harness: Letta Code is its own CLI, Claude Code memory is Claude Code only. The cross-engine players (basic-memory, Agentage, Notion Lore, agentmemory) are all *single shared pools*, not per-agent. Nobody occupies the intersection. Structural, not cosmetic.
5. **Reviewing an agent's expertise as a team practice.** The git substrate is commodity; the PR-review-of-knowledge workflow is marketed by no one (§4).
6. **A session-end lifecycle as a product surface.** `reflect` → `merge` → `summarize` → `finalize` as explicit user-invoked commands has no counterpart. Competitors hide consolidation in a background process.

---

## 6. CROWDED GROUND — claims Lore Agents should NOT make

Each of these is already made credibly, at scale, by someone with more distribution.

| Do not claim | Who already owns it | Evidence |
|---|---|---|
| "A team of named AI specialists / AI experts" | CrewAI (58.4k), BMAD (52.9k), wshobson (39.6k), VoltAgent (25.0k), MetaGPT (70.3k) | Star counts 2026-09-12 |
| "AI coworkers that learn / memory that compounds" | **OpenAI Frontier** — markets agents you *"hire"* and *"onboard,"* each with identity and *"memory that compounds over time"* | [openai.com/index/introducing-openai-frontier](https://openai.com/index/introducing-openai-frontier/), Feb 2026 |
| "Your agent finally remembers across sessions" | claude-mem (93.7k), mem0, Letta, Cursor Memories, Claude Code native | Saturated; this is the category's generic tagline |
| "Git-backed agent memory" | **Letta Context Repositories, 2026-02-12** | [letta.com/blog/context-repositories](https://www.letta.com/blog/context-repositories/) |
| "Plain Markdown you own — no black box, no vector DB, no lock-in" | basic-memory, Agentage Memory (*"no black-box vector store and no lock-in"*), agentmemory | [agentage.io](https://agentage.io/) |
| "Cross-tool / works with Claude, Cursor and Codex" | Agentage, Notion Lore, basic-memory, agentmemory, wshobson/agents, BMAD | Commodity by 2026 |
| "Per-agent persistent memory" (bare) | **Anthropic ships this natively** | [`memory:` frontmatter](https://code.claude.com/docs/en/sub-agents) |
| "Agents that collaborate" | Claude Code Agent Teams, CrewAI, AutoGen, BMAD, Cursor Projects | Ubiquitous |

**Two adversarial notes worth carrying into any public claim.**

- **The benefit of cross-session agent memory is not empirically settled.** [GitOfThoughts](https://arxiv.org/abs/2606.14470) (June 2026) tested five memory stores — none, a Markdown file, a vector DB, a graph, and git — across two benchmarks and two model sizes with pre-registered repeats, and found that agent memory from past problems **did not improve accuracy on new problems**. A sufficiently informed critic can cite this against the entire category, Lore included. Claims about *compounding expertise* should be framed as workflow and continuity benefits, which are observable, rather than accuracy benefits, which are contested.
- **There is a live backlash against the "AI employees" frame.** Commentary in 2026 describes an *"org-chart trap"* — giving agents names and titles makes people scrutinize their output less. Leaning hard on the "digital coworker" metaphor invites that critique.

---

## 7. Naming and positioning collisions

**"Lore" is already taken twice in this exact category. This is a real problem, not a footnote.**

1. **`BYK/loreai` — "Lore"** — https://github.com/BYK/loreai · https://withlore.ai/
   110 stars, created 2026-02-20, last pushed 2026-09-12 (active today). Tagline: *"Your AI never starts over. Lore keeps sessions coherent for days and millions of tokens... and turns every session into compounding memory across tools, providers, and (soon) your team."*
   **Same name, same category, same words** — memory, compounding, cross-tool, team. Its README says *"No context files. No workflow changes"* — it is positioned as the precise opposite of Lore Agents' deliberate approach, which makes confusion between the two actively damaging. It also holds `withlore.ai`.

2. **`makenotion/lore` — Notion's "Lore"** — 142 stars, MIT. Tagline: *"AI memory backed by Notion."* Announced [2026-08-18](https://www.notion.com/blog/building-shared-memory-for-ai-agents-in-notion) as *"shared, persistent memory for agents."* Cross-engine over MCP (Claude Code, Codex, Cursor), tracks agent identity via an `Agent:` field, team-shared vault.
   A **major-vendor** name collision in the same category, four weeks old, with Notion's distribution behind it. Notion will win any search contest for "lore agent memory."

3. **Tagline collision.** The framework's current tagline is *"Named AI specialists that learn and grow with you"* (GitHub, 2026-09-12). Every component is contested: "named specialists" by the subagent collections and CrewAI/BMAD, "that learn" by OpenAI Frontier, claude-mem, mem0 and Letta.

**Recommendation:** treat naming as an open decision requiring a deliberate call, not an assumption. Lore Agents currently has **0 stars** against competitors at 110, 142, 3.3k, 39.6k and 52.9k — it has the least to lose from a rename of anyone in this list, and the window to do it cheaply is now.

---

## 8. EXPLICITLY NOT VERIFIED

Everything in this section is a known gap. Do not treat any of it as established.

1. **Whether Letta Code users actually review memory in PRs.** Verified: the git substrate and GitHub remote sync. **Not verified:** any real team-review practice. Letta's announcement does not mention pull requests, review, or teams; some third-party summaries *infer* team review from the git substrate, and that inference is unsupported by primary text. If Letta ships explicit team/PR framing, Lore's §4 position narrows sharply.
2. **Whether Claude Code's `memory:` field works reliably.** [Issue #57507](https://github.com/anthropics/claude-code/issues/57507) is a detailed community report, closed as not planned, unconfirmed by maintainers. Not independently reproduced here. Do not state publicly that the feature is broken.
3. **Adoption of Claude Code's `memory:` field.** Verified: zero usage in the three largest *collections*. **Not verified:** usage in private repos or individual configs. "Collections don't use it" ≠ "nobody uses it."
4. **Exact star counts for `letta-ai/letta-code`, `bmad-code-org/BMAD-METHOD`, `makenotion/lore`.** These came from rendered GitHub pages after the unauthenticated API rate limit was exhausted, not from the API. Treat as approximate. `mem0ai/mem0`, `github/spec-kit` and `buildermethods/agent-os` star counts were **not obtained at all**.
5. **`MotiaDev/motia` and `awslabs/agent-squad` were not evaluated.** Both 404'd on the API; `agent-squad` appears to have moved to `2FastLabs/agent-squad` (7,759 stars). Neither was assessed on the five axes.
6. **Cursor Projects (launched 2026-09-10, two days before this research)** — "coordinator agents that keep shared context across sessions, delegate to thousands of subagents." Known only from a secondary source. **Not evaluated against the axes.** Given its recency and Cursor's distribution, this is the highest-priority follow-up in this report.
7. **OpenAI Frontier's memory architecture** is known only from the announcement and press coverage. Whether its memory is curated, per-agent, or inspectable is unknown.
8. **Long-tail candidates found but not investigated:** Akephalos (git-synced Markdown agent profile — potentially relevant to axes 3 and 5), Verified Memory Vault, kgai, OpenViking, Memorix, agentmemory (both `jayzeng/` and `rohitg00/`), Agentage Memory. Several were surfaced only through aggregator sites of uncertain reliability. Akephalos in particular warrants a direct look.
9. **The 86-system comparison at `carsteneu/ai-memory-comparison`** was identified but its data could not be read (the table lives on a rendered site, not in the README). It is the most likely source of candidates missed here.
10. **No pricing, revenue, funding, or real user-count data** was gathered for any commercial candidate. Stars and download counts are weak proxies — a caveat this archive already established in the claude-mem study.
11. **Reddit, Hacker News, X and Discord sentiment were not sampled** for any competitor.

---

## 9. What this changes — recommendations

1. **Stop leading with git-backed Markdown.** Letta shipped it in February 2026 and Anthropic shipped it natively. Leading with it invites an easy, correct rebuttal. Re-cut it as a *review and distribution* claim: an agent's expertise is a team artifact you clone, read, and correct in a PR.
2. **Lead with the verified gap instead.** *Nearly a thousand named specialist agents exist across 76,000 stars of community collections, and not one of them remembers anything.* It is concrete, checkable, and the cleanest one-line explanation of what Lore adds.
3. **Make deliberate curation the intellectual centre, framed as control.** The whole market is automating capture — mem0 calls manual curation a scaling wall. Lore's contrarian position is defensible *as a choice about who decides*, but the reflect *concept* is not novel and Letta's sleeptime reflection is close. Claim the posture, not the invention.
4. **Treat the role-as-relevance-boundary as the sharpest unclaimed idea.** No competitor found has it. It is also the hardest to copy, because it requires the agent to be a *domain* rather than a *persona*.
5. **Resolve the naming question deliberately and soon.** Two active "Lore" projects in this exact category, one of them Notion's. At 0 stars the switching cost will never be lower.
6. **Prepare a one-line answer to each of the three inevitable objections:** "isn't that just Claude Code's `memory:` field?", "isn't that Letta?", and "isn't that BMAD?" Each has a true, short answer — shallow/siloed/single-engine; automatic/single-harness/no role boundary; no accumulated knowledge at all — and each should be ready before any public launch.
7. **Follow up on Cursor Projects immediately.** Two days old, Cursor's distribution, and it targets persistent cross-session agent context. It is the most likely source of an unpleasant surprise.
