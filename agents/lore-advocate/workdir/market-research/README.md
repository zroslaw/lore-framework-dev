# Market Research

Competitive and comparative research on the agent-memory / agent-knowledge category.
Each entry is a point-in-time study. Figures inside decay — trust the date stamps, not the numbers.

Started 2026-09-12.

**Entries cross-check each other, and later entries have already corrected earlier ones.**
Where a conclusion has been revised, this index states the corrected version and points at the
superseded one. Do not cite a single file without checking here first.

## Entries

| Subject | Files | Researched |
|---|---|---|
| claude-mem (now "Grok Mem") — thedotmack / Alex Newman | [origins](claude-mem-origins.md), [promotion](claude-mem-promotion.md) | 2026-09-12 |
| mem0 (formerly embedchain) — mem0ai, YC S24, $24M raised | [origins](mem0-origins.md), [promotion](mem0-promotion.md) | 2026-09-12 |
| Multi-agent specialist landscape — does anything already do this? | [landscape](multi-agent-specialist-landscape.md) | 2026-09-12 |

Category ranking by stars at 2026-09-12: claude-mem 93,703 · mem0 65,153 · cognee 30,650 ·
supermemory 29,636 · agentmemory 28,363 · Letta 24,702.
**Stars proved misleading in all three studies** — see "How to measure" below.

## Corrections log

| Date | Correction | Affects |
|---|---|---|
| 2026-09-12 | Watchers/stars ratio **withdrawn** as evidence of weak adoption. mem0 scores 0.38% vs claude-mem 0.32% despite $24M funding and ~47x the usage — the heuristic does not discriminate in either direction. Measurement retained, inference retracted. | claude-mem-origins.md §5 |
| 2026-09-12 | "Installers cause growth" **narrowed**. mem0 shipped a Claude Code plugin 2026-03-25 with no effect on its download curve. Corrected rule below. | claude-mem-promotion.md |
| 2026-09-12 | "Landing page live on day one" **dropped** from the repeatable list. mem0 hit GitHub Trending #1 with unedited shadcn placeholder text still on its page. | claude-mem-promotion.md |

## What we now believe

### 1. Growth comes from reducing friction where your market already lives

The first study concluded "distribution beats content" from claude-mem's two inflections, both
installer changes (37x in Oct 2025 on shipping a plugin marketplace manifest; 14x in Apr 2026 on
moving to native `/plugin install`). Both stepped up and held — the shape of a permanent change,
not a decaying spike.

mem0 narrows this. It shipped a Claude Code plugin on 2026-03-25 and its PyPI curve stayed flat at
~92K downloads/day. No step. The difference: claude-mem *is* an agent-host tool, so that surface is
its entire market, while mem0 is a Python library for application developers.

**Corrected rule: friction reduction causes growth only on the surface where most of your market
already is.** For Lore Agents that surface *is* the coding-agent hosts — so the original conclusion
still applies to us, but for a reason we now understand rather than by analogy.

### 2. The higher-leverage move is becoming a dependency, not being installable

mem0's compounding growth came from being embedded in other people's frameworks: a CrewAI extra
(2024-11-25), a package inside LlamaIndex's own namespace (2024-10-31), a Vercel AI SDK provider,
AWS Agent SDK memory provider. A developer installs CrewAI and gets mem0 without choosing it.

A PR into someone else's framework costs nothing and scales down to a solo maintainer. This is the
single most transferable tactic found across all three studies.

### 3. Content did not grow either project

- **dev.to is worthless here.** claude-mem: one third-party article, 0 reactions, twelve months
  late. mem0: 15 third-party articles, peak 2 reactions, on a 65K-star project.
- **Hacker News is settled across two opposite outcomes.** claude-mem self-submitted and scored 2
  points. mem0's Show HN scored 201 points and 61 comments — and produced only ~766 stars over five
  days, against 7,773 from a week with no launch at all. Do the Show HN; do not build a launch
  around it. (A moderator publicly flagged mem0's thread for astroturfed booster comments.)

### 4. Relaunch beats launch — if you already have an audience

mem0's largest single inflection was not a launch. In one week (2024-07-18 → 07-25) it went 9,368 →
17,141 stars by renaming a dying two-year-old RAG framework (Embedchain, ~9K stars, 5 commits in
April 2024) into mem0, announcing on X, and hitting GitHub Trending #1.

GitHub Trending ranks stars *gained*, so an existing audience bursting on command is exactly what
wins it. A new repo has no base to burst from. Directly relevant to any renaming decision.

### 5. Neither project led with the idea

Every hook was the user's pain in plain words — "Your AI Assistant Finally Has a Memory", "Stop
explaining context. Start building faster." Never architecture, never embeddings, never a theory of
agents. The install command sat next to the hook every time.

mem0 adds a second lesson: **positional conviction**. Its core README paragraph is unchanged for 25
months across ~130 README commits. claude-mem rewrote its pitch five times in twelve months. The one
that held still won on usage.

### 6. Ship a benchmark with a number, not an essay

mem0's arXiv paper made it the reference other projects benchmark themselves against. A number
others must cite outperforms an essay nobody links.

### 7. How to measure

Stars misled in all three studies, in three different directions: claude-mem's are inflated by a
memecoin farming incentive and diverge from a flat download curve; mem0's are partly inherited from
a different product (embedchain) pre-rename; and the watchers/stars ratio proved unable to tell the
two apart. **Use install and download curves.** Stars are a lagging attention metric, not adoption.

Neither founder's standing mattered: claude-mem's author had 124 other public repos topping out at
44 stars.

## What the landscape study changed in our thinking

**1. Git-backed Markdown agent memory is NOT ours.** Letta shipped Context Repositories on
2026-02-12 (Markdown + YAML frontmatter in a real git repo, syncable to a GitHub remote), and
Claude Code shipped a native per-subagent `memory:` field in v2.1.33 whose `project` scope is
documented as "shareable via version control". Leading with the git substrate invites an easy,
correct rebuttal. Re-cut it as a *review and distribution* claim instead — expertise as a team
artifact you clone and correct in a PR. Letta's announcement never mentions PRs, review, or teams.

**2. The verified gap is the subagent collections.** Cloned and grepped on 2026-09-12: **0 of 981**
agent definitions across wshobson/agents (39.6k), VoltAgent (25.0k) and contains-studio (12.4k) use
the `memory:` field. ~1,000 named specialists, 76k stars, none of them remember anything. This is
the cleanest, most checkable one-line statement of what Lore adds.

**3. Deliberate curation is contrarian, not just unique.** mem0 calls manual curation a "scaling
wall" it exists to eliminate. The whole market automates capture. Letta's sleeptime reflection is
close but fires automatically every N steps — the difference is *who decides and when*. Claim the
posture, not the invention.

**4. Closest competitor is Letta Code** (~3.3k stars), scoring ~3.5 of our 5 axes. It stops short on
roles (its subagents are generic utilities; memory is an identity, not a professional remit),
on deliberate curation, on cross-engine (it is its own harness), and on team review.

**5. "Lore" is taken twice in this exact category.** BYK/loreai (withlore.ai, 110 stars, active) and
makenotion/lore (Notion, 142 stars, Aug 2026). At 0 stars the cost of renaming will never be lower.

**6. The category's core benefit is empirically contested.** GitOfThoughts (arXiv 2606.14470, June
2026) tested five memory stores and found cross-problem agent memory did *not* improve accuracy on
new problems. Frame claims around workflow and continuity, not accuracy — a hostile critic can cite
this against us too.

## Implications for Lore Agents

- **Plugin-directory presence and one-command install** remain the highest-leverage moves, now for a
  understood reason (§1): the coding-agent hosts are where our market already lives. We ship as a
  Claude Code plugin and support Codex and Cursor — a discovery asset we are not yet using as one.
- **Get embedded in other people's frameworks** (§2). Cheapest compounding growth available.
- **The first public article opens with the pain and a concrete example.** The approach — named
  specialists, curated learning, knowledge reviewed in git — is the payoff, not the entrance.
  See [core positioning](../../lore/core-positioning.md) and [channel strategy](../../lore/channel-strategy.md).
- **Pick a pitch and hold it** (§5). Rewriting positioning repeatedly correlates with losing.
- **Claims to avoid:** "a team of AI specialists" (CrewAI 58.4k, BMAD 52.9k, wshobson 39.6k);
  "AI coworkers / memory that compounds" (OpenAI Frontier uses almost exactly this); "agents that
  remember across sessions" (saturated); "plain Markdown you own, no lock-in" (basic-memory,
  Agentage); "git-backed agent memory" (Letta got there first). The current tagline "Named AI
  specialists that learn and grow with you" is contested in every component.
- **Do not copy:** the memecoin, the GeoIP/cohort telemetry, eleven releases in a day, shipping
  promotional banners into users' terminals, or mem0's `oss-to-platform` migration funnel.
- **The undefended flank:** mem0 removed OpenMemory, its local-first private MCP memory server, from
  the README, docs and repo on 2026-03-24. They chose hosted platform over local-first. That is
  exactly where Lore Agents lives, and nobody funded is defending it.

## Known gaps

**Highest priority**

- **Cursor Projects** launched 2026-09-10 — coordinator agents with persistent cross-session
  context. Not evaluated against the five axes. Cursor's distribution makes this the top follow-up.
- **Reddit is NOT MEASURED in either promotion study** — unknown, not zero. Both agents were blocked
  (the second identified Anubis proof-of-work, solved the challenge, and was still refused at the
  validation endpoint). Needs a manual pass of r/ClaudeAI, r/ClaudeCode, r/AI_Agents, r/LocalLLaMA.

**Other**

- X engagement numbers could not be retrieved for either project; accounts confirmed, metrics not.
- No real star-growth curve for claude-mem; its April 2026 inflection is evidenced by npm downloads.
- How many of mem0's 65,156 stars were earned as embedchain before the rename is undetermined —
  the most important open question about that project's numbers.
- `carsteneu/ai-memory-comparison` (86 systems) could not be read; likeliest source of missed candidates.
- Long tail unexamined: Akephalos, Agentage Memory, Memorix, kgai, OpenViking, Verified Memory Vault.

## Method notes worth reusing

- `https://github.com/<repo>/graphs/contributors-data` returns per-contributor commit totals as JSON
  and is **not** subject to the 60/hr unauthenticated REST limit.
- Release and tag `.atom` feeds also bypass that limit.
- `api.npmjs.org/downloads/range/...` and `pypistats.org` give real adoption curves. Use these, not stars.
