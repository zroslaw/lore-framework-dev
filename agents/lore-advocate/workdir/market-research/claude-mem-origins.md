# claude-mem — Origins and Development History

**Researched:** 2026-09-12
**Subject:** https://github.com/thedotmack/claude-mem (npm: `claude-mem`)
**Researcher:** lore-advocate market-research sweep, first entry in this archive
**Method:** GitHub REST API (unauthenticated via `gh` and `curl`), npm registry + downloads API, `raw.githubusercontent.com` for historical file versions, DexScreener API, and web search/fetch of project-owned sites. Primary sources are distinguished from secondary throughout.

## Summary — the three most decision-relevant findings

**First, the adoption story and the attention story point in opposite directions.** claude-mem showed 93,703 GitHub stars as of 2026-09-12, but npm downloads stepped 14x in April 2026 (7,011 → 99,322/month) and have been flat-to-declining at 70–85K/month for the five months since. Stars kept climbing while real usage plateaued. A widely-repeated "74.8K stars" figure is not wrong, just stale — it fits a mid-2026 snapshot. **Second, the project's identity is unstable.** It rebranded to "Grok Mem" on 2026-09-03 — nine days before this research — while the npm package, the repo name, the docs domain, and the paid product all still say claude-mem/cmem; its README tagline has been rewritten five distinct times in twelve months; and in January 2026 it attached a Solana memecoin (`$CMEM`) promoted at the very top of the README, which is now functionally dead at roughly $7.2K FDV and $23/day volume. **Third, the architecture is nonetheless genuinely comprehensive and worth studying** — lifecycle hooks for capture, LLM compression, SQLite plus a Chroma vector DB for storage, and an MCP server implementing a three-layer progressive-disclosure retrieval pattern. It is all four approaches at once, not one, and that retrieval pattern is a real idea independent of any judgment about the project's trajectory.

---

## 1. Canonical repository — VERIFIED, exists

- **https://github.com/thedotmack/claude-mem**
- Repo id `1048065319`; created **2025-08-31T20:50:03Z**; default branch `main`; primary language TypeScript.
- License: **Apache-2.0** (as of 2026-09-12 — changed from AGPL-3.0, see §7).
- Homepage field: `https://claude-mem.ai` (which 308-redirects to `https://cmem.ai/`).
- Has issues, wiki, and discussions enabled. Web commit signoff required.
- npm package: **https://www.npmjs.com/package/claude-mem** — still the package name after the Grok Mem rebrand.
- Docs site: https://docs.claude-mem.ai
- Official Discord (from README): https://discord.com/invite/J4wttp9vDu

Verified via `gh api repos/thedotmack/claude-mem` and independently via the rendered github.com page.

Repository description as of 2026-09-12 (note the keyword-list character):

> Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More

Topic tags on the repo (20, as of 2026-09-12), which notably include direct competitor names:

`ai`, `ai-agents`, `ai-memory`, `anthropic`, `artificial-intelligence`, `chromadb`, `claude`, `claude-agent-sdk`, `claude-agents`, `claude-code`, `claude-code-plugin`, `claude-skills`, `embeddings`, `long-term-memory`, `mem0`, `memory-engine`, `openmemory`, `rag`, `sqlite`, `supermemory`

---

## 2. Who created it

- **Alex Newman**, GitHub handle **@thedotmack**.
  - GitHub user id `683968`; account created **2011-03-22T14:18:35Z**; 1,970 followers; 126 following; 125 public repos (all as of 2026-09-12).
  - Profile: https://github.com/thedotmack
  - Name confirmed from two primary sources: the GitHub profile API (`"name": "Alex Newman"`) and the npm package metadata (`"author": {"name": "Alex Newman"}`).
  - Commit author identity on the first commit: `thedotmack <thedotmack@gmail.com>`.
  - GitHub profile fields for company, blog, location, email, and bio were all **empty/null** as of 2026-09-12.

### Public presence

- **Project X account: @Claude_Memory** — https://x.com/Claude_Memory. This is set as the `twitter_username` on his GitHub profile and is listed in the README as the "Official X Account."
- **Personal X: @thedotmack** — https://x.com/thedotmack (example post surfaced in search: https://x.com/thedotmack/status/2011685458515017745)
- **LinkedIn: https://www.linkedin.com/in/alexnewman/** — headline reads "Claude-Mem". Not fetched directly (LinkedIn blocks automated fetch); surfaced via web search. A LinkedIn post announcing the project: https://www.linkedin.com/posts/alexnewman_github-thedotmackclaude-mem-a-claude-activity-7391306333355925504-p975
- **Product Hunt listing:** https://www.producthunt.com/products/claude-mem
- **Commercial entity: "glass brain"** — the cmem.ai footer reads "© 2026 glass brain · cmem.ai" (https://cmem.ai/about). Contact address `hello@cmem.ai`.

### Background — UNVERIFIED

Secondary sources describe Newman's background as spanning "AI Product Management, Solutions Architecture, and Forward Deployed Engineering":

- https://agentpedia.codes/blog/claude-mem-persistent-memory-guide
- https://www.augmentcode.com/learn/claude-mem-65k-stars

**I could not confirm this from any primary source.** His GitHub bio and company fields are empty; LinkedIn was not directly fetchable. Treat the background description as unverified secondary reporting.

### Prior projects — effectively none of note

This is a single-hit profile, not an established open-source maintainer. Of his 125 public repos, ranked by stars as of 2026-09-12:

| Stars | Created | Repo | Description (truncated) |
|---|---|---|---|
| 93,703 | 2025-08-31 | `claude-mem` | Persistent Context Across Sessions for Every Agent |
| 44 | 2025-10-01 | `mcp-client-cli` | CLI for any Model Context Protocol server |
| 38 | 2026-02-23 | `sequential-thinking-skill` | Claude Code skill replicating Sequential Thinking MCP |
| 21 | 2026-02-06 | `aims` | AI Messenger Service — watch AI bots communicate in real time |
| 18 | 2025-09-16 | `claude-mem-docs` | docs.claude-mem.ai |
| 17 | 2026-02-01 | `crab-mem` | Continuous cognition for OpenClaw agents |
| 16 | 2026-02-24 | `mackeroni-skills` | Agent skills for Claude Code and Gemini CLI |
| 13 | 2025-10-14 | `HIPAApotamus` | (no description) |
| 11 | 2025-09-08 | `claude-commands` | Custom Claude Code commands |
| 9 | 2026-05-15 | `humanish` | Single-use scoped credential helper |
| 9 | 2026-04-11 | `redplanet-cleaning-station` | (no description) |
| 9 | 2026-02-02 | `crabspace-app` | "MySpace for AI Agents" |
| 7 | 2025-11-27 | `rad-mem` | Domain-flexible temporal intelligence |
| 5 | 2026-02-27 | `notch` | Schema-less CLI state machine for LLM agents |

The next-highest repo after claude-mem has **44 stars** — a roughly 2,100x gap. Nearly every other repo was created *after* claude-mem, i.e. they are downstream of its success, not prior credentials.

---

## 3. When it started

| Event | Date | Source |
|---|---|---|
| npm first publish (`v2.0.0`) | **2025-08-30T03:04:46Z** | npm registry `time` field |
| npm package record created | 2025-08-31T03:20:12Z | npm registry |
| GitHub repo created | **2025-08-31T20:50:03Z** | GitHub API `created_at` |
| First commit on `main` | **2025-09-06T19:34:53Z** | GitHub API, commit `598369e8942eb731651e391b01f60bb7329cc57c` |
| First GitHub Release / tag (`v3.5.4`) | **2025-09-09T06:12:33Z** | GitHub releases API |

**Important nuance:** the first commit message is *"Initial release v3.3.8"* — the git history *begins* at version 3.3.8, and npm's first published version was 2.0.0 six days before the repo's first commit. Development prior to 2025-09-06 was not published as commit history (squashed, or the repo was recreated). So the project's true origin predates its visible git history by at least a week, and the pre-3.3.8 development is not publicly inspectable.

The three oldest commits, all on 2025-09-06:

```
598369e894  2025-09-06T19:34:53Z  Initial release v3.3.8
(next)      2025-09-06T19:36:38Z  Remove internal documentation
(next)      2025-09-06T19:41:36Z  Initial release v3.3.8
```

---

## 4. Release cadence

All figures as of 2026-09-12.

- **344 GitHub releases** (from `releases?per_page=1` pagination Link header, `page=344` rel="last")
- **365 git tags** (same method)
- **2,686 commits** on `main` (from `commits?per_page=1` Link header)
- **234 published npm versions** — fewer than GitHub releases, so not every GitHub release reached npm
- npm dist-tags: `latest` = `13.24.23`; a second tag `community-edge` = `13.10.3-community-edge.0`

### Version arc

| Version | Date | Note |
|---|---|---|
| `2.0.0` | 2025-08-30 | first npm publish |
| `3.3.8` | 2025-09-06 | first commit in git history |
| `3.5.4` | 2025-09-09 | first GitHub release |
| `4.0.0` | 2025-10-19 | "Plugin data directory and auto-starting worker" |
| `4.3.0` | 2025-10-25 | "Progressive Disclosure Context" |
| `12.0.0` | by 2026-04-07 | per secondary snapshot |
| `12.3.8` | 2026-04-20 | per secondary snapshot |
| `13.24.23` | **2026-09-11T17:33:49Z** | current latest as of 2026-09-12 |

Major version 4 → 12 inside roughly six months is aggressive semver churn rather than eight architectural rewrites.

### Current cadence is extreme

Eleven releases — `v13.24.13` through `v13.24.23` — all shipped on **2026-09-11**, within roughly eleven hours:

```
v13.24.23  2026-09-11T17:33:49Z
v13.24.22  2026-09-11T17:19:45Z
v13.24.21  2026-09-11T16:56:34Z
v13.24.20  2026-09-11T10:06:08Z   (appears twice in the API listing)
v13.24.19  2026-09-11T09:45:53Z
v13.24.18  2026-09-11T09:17:10Z
v13.24.17  2026-09-11T08:41:08Z
v13.24.16  2026-09-11T08:02:46Z
v13.24.15  2026-09-11T07:31:22Z
v13.24.14  2026-09-11T07:11:46Z
v13.24.13  2026-09-11T06:35:21Z
```

Note `v13.24.20` appears **twice** in the releases API listing with an identical timestamp — a duplicate release entry, itself a small signal about release hygiene.

Recent README-touching commits are now almost entirely `chore: bump version to …`. Last push to the repo: 2026-09-11T18:13:59Z.

---

## 5. Adoption — measured figures

**All figures below are as of 2026-09-12 and will decay.**

| Metric | Value (2026-09-12) | Source |
|---|---|---|
| Stars | **93,703** | GitHub API `stargazers_count`; corroborated by rendered page showing "93.7k" |
| Forks | **8,246** | GitHub API |
| Watchers (subscribers) | **300** | GitHub API `subscribers_count` |
| Open issues + PRs | **193** (`open_issues_count`) | GitHub API |
| Open issues alone | **22** | rendered github.com page — implying roughly **171 open pull requests** |
| Contributors | **137** | `contributors?per_page=1` Link header |
| npm downloads, last 30d | **70,559** (2026-08-12 → 2026-09-10) | api.npmjs.org |
| npm downloads, last 7d | **13,245** (2026-09-04 → 2026-09-10) | api.npmjs.org |
| npm downloads, 2025-09-01 → 2026-09-12 | **440,029** | api.npmjs.org range endpoint |
| Repo size | 484,790 KB | GitHub API |

### Top contributors (2026-09-12)

```
thedotmack           2196
rodboev               66
Copilot               58
ousamabenyounes       31
stantheman0128        22
posthog[bot]          15
cursoragent           14
Chenglinwei1997       13
alessandropcostabr    11
Glucksberg            10
```

Of the top ten "contributors," three are bots or AI agents (`Copilot`, `posthog[bot]`, `cursoragent`). The author accounts for 2,196 of ~2,686 commits — roughly 82%. The "137 contributors" headline number is therefore a long tail of single-commit contributors, not a distributed maintainer base.

### On the "74.8K stars" claim

**Not refuted — stale.** The real current figure is **93,703 as of 2026-09-12**, confirmed by two independent reads: the REST API (`stargazers_count: 93703`) and the rendered github.com page ("93.7k"). 74.8K is consistent with a snapshot from roughly mid-2026. Nothing found supports 74.8K as a *current* number.

### Why the star figure is a weak adoption signal — the measurements

This is measurement, not speculation. I did **not** find direct evidence of star inflation and do not claim it.

#### WITHDRAWN INFERENCE — watchers/stars ratio (retracted 2026-09-12, same day as publication)

**The measurements below stand. The inference drawn from them has been withdrawn.** Originally this section argued that claude-mem's unusually low watchers-to-stars ratio was evidence of weak or inflated adoption. That argument does not hold.

**Watchers-to-stars ratio, all pulled the same way on 2026-09-12 (measurements retained):**

| Repo | Stars | Watchers | Watchers/stars | Forks/stars |
|---|---|---|---|---|
| **thedotmack/claude-mem** | 93,703 | 300 | **0.32%** | 8.80% |
| microsoft/vscode | 192,028 | 3,523 | 1.83% | 21.93% |
| ollama/ollama | 180,711 | 1,012 | 0.56% | 9.86% |
| langchain-ai/langchain | 146,161 | 919 | 0.63% | 16.71% |

**Why it was withdrawn:** the companion study of mem0 (see `mem0-origins.md` in this directory) found mem0's watchers/stars ratio to be **0.38%** — effectively the same as claude-mem's 0.32% — despite mem0 having $24M in funding, a staffed team, and roughly **47x the real usage** (3.74M PyPI plus 472K npm downloads in August 2026, still climbing). A heuristic that assigns near-identical scores to a well-funded, heavily-used project and to the project under suspicion **does not discriminate**, and cannot be used as evidence in either direction. The comparison against ollama, langchain, and vscode is therefore retired as an argument; the numbers are kept only so a future reader can see what was measured and why it was insufficient.

The remaining points below do **not** depend on the retired heuristic and stand on their own:
- 93,703 stars against 70,559 monthly npm downloads — and that download curve has been **flat to declining since April 2026** (§6). Stars kept climbing while usage did not. This divergence is measured directly from npm and is independent of any ratio heuristic.
- The author's other 124 repos top out at 44 stars.
- A memecoin was attached to the project in January 2026 (§9), supplying a direct incentive for star and fork farming.
- **Ecosystem context matters.** In this same period other Claude-adjacent repos reportedly hit 50K stars in two hours (https://github.com/hinet/claude-code) and a single-file `CLAUDE.md` repo reached roughly 100–144K stars (https://miraflow.ai/blog/karpathy-claude-md-100k-github-stars-ai-coding-2026). Stars in this niche are not priced the way they are elsewhere on GitHub.

**Practical conclusion:** 93.7K stars here should not be read as ~93.7K adopters. The npm download curve is the more defensible adoption number.

---

## 6. Star growth over time — PARTIALLY VERIFIED ONLY

**I could not obtain a genuine star-growth curve.** Recording the failures so a future researcher does not repeat them:

- `GET /repos/thedotmack/claude-mem/stargazers` returns **HTTP 401 "Requires authentication"** — both through `gh` (the local token was invalid) and through plain unauthenticated `curl`, with and without the `Accept: application/vnd.github.star+json` header needed for `starred_at` timestamps. Getting per-star timestamps requires a valid GitHub token.
- The star-history.com SVG (`https://api.star-history.com/svg?repos=thedotmack/claude-mem&type=Date`) fetched successfully (HTTP 200, 64,864 bytes). I calibrated its axes precisely — x-axis ticks at October (2025), 2026, April, July, linear at 1.863 px/day; y-axis 0 at y=423.833 with 20K increments every 90.385 px, so the chart spans **Oct 2025 → past Jul 2026 with a y-axis reaching 80K+**. But the series is rendered in star-history's xkcd hand-drawn style, and the only long path in the document produced wildly non-monotonic values (e.g. an implied 45,394 stars/day on 2025-09-02, followed by negative deltas). **That extraction is garbage and I am not reporting a curve from it.** A future attempt should use a valid GitHub token against the stargazers endpoint instead.

### Secondary snapshots — timing is ambiguous, flagged not smoothed

Two articles from augmentcode.com give point-in-time figures. **Both carry "last updated June 18, 2026", so their star figures may be as-of the update date rather than the publication date.** This makes them unusable for precise inflection timing.

| Reported | Stars | Forks | Contributors | Releases | Version | Published | Updated |
|---|---|---|---|---|---|---|---|
| Snapshot A | 46.1K | 3.5K | 92 | 223 | v12.0.0 | 2026-04-07 | 2026-06-18 |
| Snapshot B | 65.8K | 5.6K | 106 | 244 | v12.3.8 (as of 2026-04-20), 1,792 commits | 2026-04-23 | 2026-06-18 |

- Snapshot A: https://www.augmentcode.com/learn/claude-mem-46k-stars-persistent-memory-claude-code
- Snapshot B: https://www.augmentcode.com/learn/claude-mem-65k-stars

A third secondary source, https://skillsllm.com/skill/claude-mem, lists 93.7k stars, consistent with today's measurement.

### The inflection that IS hard-verified: npm downloads

From the npm downloads range API (primary source, `https://api.npmjs.org/downloads/range/2025-09-01:2026-09-12/claude-mem`):

| Month | Downloads |
|---|---|
| 2025-09 | 47 |
| 2025-10 | 1,768 |
| 2025-11 | 441 |
| 2025-12 | 1,219 |
| 2026-01 | 2,342 |
| 2026-02 | 4,884 |
| 2026-03 | 7,011 |
| **2026-04** | **99,322** |
| 2026-05 | 85,405 |
| 2026-06 | 70,457 |
| 2026-07 | 70,316 |
| 2026-08 | 79,060 |
| 2026-09 (partial, through 09-12) | 17,757 |

**A 14x step-change in April 2026, then a plateau at roughly 70–85K/month that has been flat-to-slightly-declining for five months.** On the usage metric, the project is not currently growing. The single most informative fact in this report is that this curve and the star curve disagree.

---

## 7. README positioning over time — the pitch changed five times

**This is the highest-signal section.** 137 commits touched `README.md` (same count as contributors, coincidentally). The tagline was rewritten at roughly every phase change. Historical versions retrieved from `raw.githubusercontent.com` at specific commit SHAs.

### Phase 1 — 2025-09-06, commit `598369e894` (first commit)

Title: "Claude Memory System (claude-mem)"
Tagline: **"Truth + Context = Clarity"**

> A revolutionary memory system that transforms your Claude Code conversations into a persistent, intelligent knowledge base. Never lose valuable insights, code patterns, or debugging solutions again. Your AI assistant finally has a memory that spans across all your projects and sessions.

Structured around "The Problem We Solve" (Lost Context, Repeated Explanations, Fragmented Knowledge, Context Switching, Knowledge Decay) and "Key Features" led by "Intelligent Memory Compression." One-command setup pitch: `claude-mem install`.

### Phase 2 — 2025-09-09, commit `7978f84f6c`

Tagline: **"🎯 Context That Stands Out"**

> Transform your Claude Code from a goldfish into an elephant. Every conversation, every breakthrough, every "aha!" moment - captured, compressed, and ready when you need it.

The README's *first* content section became **"🗑️ Smart Trash™ — Never Truly Lose Anything"** — note the trademark symbol on a 30-day undelete feature. This phase also briefly carried a section called **"Shakespeare's Memory Theatre"**, which was removed twice (commits on 2025-09-10 "Remove Shakespeare's Memory Theatre section from README" and 2025-09-11 "Remove Shakespeare's Memory Theatre section"). Peak whimsy; minimum engineering signal.

### Phase 3 — 2025-10-19, commit `c41c4b21ea`

Title: "Claude-Mem"
Tagline: **"Persistent memory compression system for Claude Code"**

> Claude-Mem seamlessly preserves context across sessions by automatically capturing tool usage observations, generating semantic summaries, and making them available to future sessions. This enables Claude to maintain continuity of knowledge about projects even after sessions end or reconnect.

A complete reset to sober engineering voice: badges (License AGPL-3.0, version 3.9.17, Node >= 18), a table of contents, sections for Overview / How It Works / Installation / Usage / MCP Search Tools / Architecture / Configuration / Development / Troubleshooting / License. All marketing language gone. This is the version that reads like a credible infrastructure project.

### Phase 4 — 2025-10-25, commit `d4d6185bb4` (v4.3.0)

Centered logo lockup with light/dark variants.
Tagline: **"Persistent memory compression system built for Claude Code."**

Adds the "Mentioned in Awesome Claude Code" badge (https://github.com/hesreallyhim/awesome-claude-code), added via PR #24 on 2025-10-25. Later additions: a Trendshift badge (2025-12-12) and a "Star History" section (restored 2026-03-17, implying it had been removed at some point).

### Phase 5 — 2026-01-14, commit `c314946204` (PR #705) — the crypto turn

The **very top of the README, above the logo**, became:

> Official $CMEM Links: Bags.fm • Jupiter • Photon • DEXScreener
>
> Official CA: 2TsmuYUrsctE57VLckZBYEEzdokUF8j8e1GavekWBAGS (on Solana)

Simultaneously the README fanned out to roughly 28 translated locales (zh, ja, pt-br, ko, es, de, fr, he, ar, ru, pl, cs, nl, tr, uk, vi, id, th, hi, bn, ro, sv, it, el, hu, fi, da, no — later adding zh-tw, pt, tl, ur). The locale sprawl and the token promotion arrived in the same period.

Follow-on token commits: "Update README to reflect changes in $CMEM information" (2026-03-17), "Update CMEM token description in README" (2026-06-11).

### Phase 6 — 2026-09-03, commits `8a434bbc27`, `#3856`, `#3863` — the rebrand

Nine days before this research. Logo now links to `grok-mem.ai`, and the README states:

> Claude-Mem is now Grok Mem. The package is still `claude-mem`.

Tagline: **"Grok Mem is how Grok Bots remember. Sits next to Grok's own memory. Does not replace it."**

Commit messages for this phase: "docs: Grok mem README and install for Grok Bot" (2026-09-03), "docs: add npm claude-mem package handout in Grok Mem quick start (#3856)", "docs: night-launch Grok Mem README lockup copy (#3863)", "feat(grok-bot): Phase 0+1 awareness breathing for LFG and Orifice" (2026-09-09).

### Host-chasing timeline, visible in README commits

- 2026-02-13 — "docs: update openclaw install URLs to install.cmem.ai" (OpenClaw)
- 2026-04-03 — "feat: update install CLI, ESM compat, and Gemini CLI docs" (Gemini CLI)
- 2026-07-03 — "feat: remove Gemini CLI host integration (Phase A)" then "feat: add full Antigravity CLI support (Phase B)" — Gemini dropped and Antigravity added on the *same day*
- 2026-09-03 — Grok Bot / Grok Mem rebrand

### License change — AGPL-3.0 → Apache-2.0

The October 2025 README badges show **AGPL-3.0**. The current repo is **Apache-2.0**. The current README justifies this explicitly:

> We chose Apache-2.0 because durable agentic memory should be easy to embed in developer tools, local agents, MCP servers, enterprise systems, robotics stacks, and production agent harnesses.

A deliberate move to remove copyleft friction for commercial embedding. The repo also documents an open/commercial boundary in `docs/license.md` and `docs/ip-boundary.md`. The `ragtime/` subdirectory is separately noted as Apache-2.0.

**Direction of travel, summarized:** hype → engineering credibility → SEO/locale sprawl plus memecoin → chasing whichever agent host is currently hot. The one phase that read as a serious infrastructure project (Phase 3, Oct 2025) was not sustained.

---

## 8. Architecture

The core idea, in the project's own framing on cmem.ai: *"while one AI works, a second AI takes notes — building a memory that persists across every session."*

claude-mem installs **five Claude Code lifecycle hooks** (SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd — implemented as six hook scripts) that stream the agent's tool-use activity to a **local Bun-managed worker HTTP service**, which also serves a live web viewer UI on `localhost:37777` plus search endpoints. An LLM — invoked through the **Claude Agent SDK** — compresses that raw activity into structured "observations" and session summaries, persisted to **SQLite** (sessions, observations, summaries), with a **Chroma vector database** providing hybrid semantic plus keyword retrieval. Retrieval back into future sessions happens two ways: context injection at SessionStart, and an **MCP server exposing 4 search tools** used in a deliberate **three-layer progressive-disclosure pattern** — `search` returns a compact index with IDs (~50–100 tokens per result), `timeline` gives chronological context around an interesting hit, and `get_observations` fetches full bodies (~500–1,000 tokens per result) only for IDs already filtered down. The README claims this yields **"~10x token savings"** by filtering before fetching. A `mem-search` skill wraps the whole thing for natural-language queries, and a Claude Desktop skill allows searching memory from Desktop conversations.

So: **hooks for capture, LLM compression, SQLite + Chroma for storage, MCP for retrieval** — all four, not just one.

Additional architectural details worth recording:

- **Pluggable compression provider.** After install sign-in you choose: the hosted "claude-mem observer," your own OpenRouter or Gemini key, or your Anthropic plan.
- **Privacy control:** `<private>` tags exclude content from storage.
- **Progressive Disclosure** with token-cost visibility, shipped in v4.3.0 (2025-10-25), experimental announcement in v4.2.9.
- **Storage engine history:** migrated from `better-sqlite3` to `bun:sqlite` on 2025-10-15. Worker startup moved to PM2 (2025-10-19).
- **Hosts without hooks** are handled by tailing chat log files instead. For Grok Bot specifically, "needle" observations (`decision`, `bugfix`, `security_alert`, `sensitive`) are appended as dated `- YYYY-MM-DD [awareness] …` lines into `memory/log/YYYY-MM.md`; disabled via `CLAUDE_MEM_GROK_BOT_AWARENESS_ENABLED=false`.
- **Cloud Sync:** backs memories up to cmem.ai with no daemon — the worker syncs on write. https://docs.claude-mem.ai/cloud-sync
- **Release branches** and `CLAUDE_MEM_MODE` language/mode configuration are documented in the README.
- Architecture docs: https://docs.claude-mem.ai/architecture/overview
- Install targets as of 2026-09-12: `npx claude-mem install` (Claude Code default), `--ide grok-bot`, `--ide opencode`, Antigravity CLI (https://docs.claude-mem.ai/antigravity-cli/setup).

---

## 9. Funding, company backing, commercialization — three separate things

### a) Paid hosted tier — real and live

**cmem.ai** (claude-mem.ai 308-redirects there). Headline:

> CMEM Cloud remembers every decision and dead end, then briefs you and your agents in real time — so nothing gets explained or built twice.

Pricing as of 2026-09-12:

| Tier | Price |
|---|---|
| claude-mem (open source) | Free, Apache-2.0 |
| **CMEM Cloud** | **$20/month**, cancel anytime |
| **Team** | **$333/seat/month**, 3–50 seats |

CMEM Cloud provides offline-first cloud sync of the observations database, accessible via private MCP links, with a live memory feed on mobile.

**There is an in-installer commercial funnel.** From the current README: `npx claude-mem install` "sets everything up first, then asks you to sign in to claude-mem in your browser (email magic link — no card required). Signing in provisions a memory key for your account and unlocks the **claude-mem observer**: memory that runs off-plan, free for your first 30 days… When the free trial ends, memory automatically falls back to your Anthropic plan unless you subscribe." Opt-out is available via an explicit `--provider` flag, `CLAUDE_MEM_ONLINE_OPTIN=false`, or running in CI/non-interactive shells.

Sites: https://cmem.ai/ · https://cmem.ai/about · https://cmem.ai/features

### b) Sponsorship, not investment

The current README carries three sponsor badges:

- **Vercel OSS Program** — https://vercel.com/open-source-program (badge added 2026-06-18, commit `786e167b44`)
- **Greptile** — https://www.greptile.com, listed as "code review partner"
- **SerpApi** — https://serpapi.com

### c) $CMEM memecoin — attached, and it has cratered

- **Solana contract:** `2TsmuYUrsctE57VLckZBYEEzdokUF8j8e1GavekWBAGS`, launched via Bags.fm.
- **Meteora liquidity pair created 2026-01-06T07:59:49Z** — eight days before the README commit that promoted it.
- **A BASE contract is also listed** in the current README: `0x76b1967eec0ccaeb001bbbb2b40dc4badba31ba3`
- The README's own framing, still present as of 2026-09-12 under a heading "What About CMEM?":

> CMEM is a token created by a 3rd party but officially embraced by the creator of Claude-Mem (Alex Newman, @thedotmack). The token acts as a community catalyst for growth and a vehicle for bringing CMEM to the developers and knowledge workers that need it most.

- **Live market data from the DexScreener API on 2026-09-12:** price **$0.0000072**, FDV / market cap **$7,190**, liquidity **$6,808**, 24-hour volume **$23.20**. It is functionally dead.
- Sources: https://dexscreener.com/solana/6mzfakwnac6gsk1edfx93dzeukgfzrfq4uhwarhgsqyd · https://www.coinbase.com/price/claude-memory-solana-a3aa2ace · https://phantom.com/tokens/solana/2TsmuYUrsctE57VLckZBYEEzdokUF8j8e1GavekWBAGS

Note the earlier DexScreener search snippet showed a price of $0.0002244 while the direct API read on the same day returned $0.0000072 — roughly a 30x discrepancy, likely a stale cached search result versus live data. The live API read is the one to trust; either way the absolute magnitude is negligible.

### d) No venture funding found

No seed or VC round located from any source. Web search surfaced a statement attributed to Newman's own LinkedIn that he received a great deal of advice about raising a seed round but **does not have one**. I could not fetch LinkedIn directly to confirm that wording, so treat the *quote* as unverified — what I actually verified is the **absence of any announced round anywhere**.

---

## EXPLICITLY NOT VERIFIED

**This section is the reason this archive is worth keeping. Do not let these items harden into facts on re-reading.**

1. **Per-star timestamps and a real star-growth curve.** The GitHub stargazers endpoint returns 401 without authentication; the star-history.com SVG is drawn in xkcd style and my path extraction produced non-monotonic garbage. **The April 2026 inflection reported in §6 comes from npm download data, not from stars.** I do not know when stars actually inflected. Re-attempt with a valid GitHub token.
2. **Alex Newman's professional background** ("AI Product Management, Solutions Architecture, Forward Deployed Engineering") — secondary sources only, no primary confirmation.
3. **The exact as-of dates behind the 46.1K and 65.8K star snapshots.** Both articles carry a later "updated 2026-06-18" date, so their figures may not correspond to their publication dates.
4. **Whether star growth is organic.** I identified a clear farming incentive (the token) and a stars-vs-usage divergence, but found **no direct evidence either way** and make no claim. Note that my original watchers/stars argument for this was **withdrawn on 2026-09-12** — see the withdrawn-inference block in §5.
5. **Any "Used by" / dependent-repository count** — not exposed to unauthenticated API access and not visible on the page content I retrieved.
6. **The LinkedIn "no seed round" quote** — inferred from a search summary, not fetched from the source.
7. **Pre-2025-09-06 development history** — squashed or discarded; the git history begins at v3.3.8 and npm's first publish (v2.0.0, 2025-08-30) predates the first commit. What happened in versions 1.x–3.3.7 is not publicly inspectable.
8. **Whether CMEM Cloud has any paying customers** — pricing pages are live but no revenue, customer count, or traction figure was found.
9. **Whether the Grok Mem rebrand reflects any relationship with xAI.** grok-mem.ai states "No xAI key. No Claude Code," and no partnership is claimed anywhere. There is no evidence of any xAI relationship, and the naming appears to be unilateral.
10. **This file has been amended after publication.** On **2026-09-12** the watchers/stars comparison in §5 was demoted from evidence to a withdrawn inference, after the companion mem0 study refuted the heuristic. The file was not written in its current form; read §5's withdrawn-inference block before citing anything from that section.

---

## Assessment — three things worth weighing

1. **Usage plateaued five months ago.** npm has sat at roughly 70–85K/month since April 2026 while stars kept climbing. Those two curves disagreeing is the single most informative fact in this research. Whatever drove the April step-change, it did not compound.

2. **The project no longer knows what it is.** Renamed to Grok Mem nine days before this research while the package, docs domain, repo, and paid product all still say claude-mem/cmem. Add roughly 171 open PRs, eleven releases in a single day, a duplicate release entry, a keyword-stuffed description that name-drops competitors as topic tags, a host integration added and removed on the same day, and a memecoin banner that sat above the logo for eight months. This reads as a project optimizing for attention metrics, with correspondingly high churn risk for anyone depending on it.

3. **The architecture is genuinely comprehensive and worth studying regardless.** Hooks plus LLM compression plus SQLite plus vector search plus MCP progressive disclosure is a complete design, and the three-layer retrieval pattern (`search` → `timeline` → `get_observations`, filtering on cheap indices before paying for full bodies) is a real idea worth borrowing independent of any judgment about the project's trajectory or its maintainer's priorities.

---

## Source index

**Primary (project-owned or authoritative APIs):**
- https://github.com/thedotmack/claude-mem — repo, API, and raw file history
- https://github.com/thedotmack — author profile
- https://www.npmjs.com/package/claude-mem — registry metadata
- `https://registry.npmjs.org/claude-mem`, `https://api.npmjs.org/downloads/...` — versions and download counts
- `https://raw.githubusercontent.com/thedotmack/claude-mem/<sha>/README.md` — historical READMEs at commits `598369e894`, `7978f84f6c`, `c41c4b21ea`, `d4d6185bb4`, `c314946204`, `main`
- https://cmem.ai/ · https://cmem.ai/about · https://cmem.ai/features — commercial product and entity
- https://grok-mem.ai — rebrand site
- https://docs.claude-mem.ai — documentation
- https://x.com/Claude_Memory · https://x.com/thedotmack — author/project accounts
- `https://api.dexscreener.com/latest/dex/tokens/2Tsmu...` — token market data

**Secondary (third-party writing about the project):**
- https://www.augmentcode.com/learn/claude-mem-46k-stars-persistent-memory-claude-code
- https://www.augmentcode.com/learn/claude-mem-65k-stars
- https://agentpedia.codes/blog/claude-mem-persistent-memory-guide
- https://byteiota.com/claude-mem-persistent-memory-for-claude-code/
- https://skillsllm.com/skill/claude-mem
- https://ai.miraheze.org/wiki/Claude-mem
- https://ai-tldr.dev/releases/thedotmack-claude-mem/
- https://www.producthunt.com/products/claude-mem
- https://github.com/ArtemisAI/pi-mem — a downstream fork/derivative
- https://dexscreener.com/solana/6mzfakwnac6gsk1edfx93dzeukgfzrfq4uhwarhgsqyd · https://www.coinbase.com/price/claude-memory-solana-a3aa2ace
- Ecosystem star-inflation context: https://github.com/hinet/claude-code · https://miraflow.ai/blog/karpathy-claude-md-100k-github-stars-ai-coding-2026
