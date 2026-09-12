# How claude-mem Was Promoted — Growth Post-Mortem

**Researched:** 2026-09-12
**Subject:** [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — persistent memory for AI coding agents, by Alex Newman ([@thedotmack](https://github.com/thedotmack))
**Researched by:** claude-mem promotion research pass, for the lore-advocate market-research archive
**Method:** public sources only — GitHub API, npm registry API, git history of a full repo clone, hn.algolia.com API, dev.to API, Wayback Machine, DexScreener API, web search and page fetches

## Summary — the one conclusion that matters

**Both of claude-mem's growth inflections were installer / host-surface changes, not content events.** In October 2025 the project shipped a Claude Code plugin manifest and npm downloads stepped 37x (47 -> 1,768/month). In April 2026 it replaced its custom installer with native Claude plugin commands and added manifests for more agent hosts, and npm downloads stepped 14x (7,011 -> 99,322/month) while stars went 46.1K -> 65.8K in thirteen days. No article, no Show HN, no Product Hunt launch and no video sits in either window. Meanwhile every channel the maintainer personally pushed on underperformed badly: his one Hacker News self-submission got 2 points, his second Product Hunt launch got 2 upvotes while the repo had 90K stars, and his project memecoin is worth almost nothing. The content about claude-mem — dev.to articles, YouTube videos, blog coverage — is entirely third-party and arrived *after* the growth, written because the project was already big. For a maintainer trying to learn from this: the transferable lesson is distribution engineering and release cadence, not writing.

> **Caveat carried throughout:** Reddit could not be measured at all (see the Reddit section). That is **unknown**, not zero. X/Twitter post-level engagement is likewise **unverified**.

---

## 1. Chronological timeline

Volatile figures are date-stamped in place; they decay.

| Date | Event | Who | Evidence |
|---|---|---|---|
| 2025-08-30 | npm package `claude-mem@2.0.0` published — code exists before the public repo | maintainer | [registry.npmjs.org/claude-mem](https://registry.npmjs.org/claude-mem) |
| 2025-08-31 | GitHub repo created | maintainer | GitHub API `repos/thedotmack/claude-mem` |
| **2025-09-06** | First public commit, "Initial release v3.3.8". **Landing page `claude-mem.ai` live the same day**, titled *"Claude-Mem \| Your AI Assistant Finally Has a Memory"* | maintainer | repo git log; [Wayback 20250906211833](https://web.archive.org/web/20250906211833/https://claude-mem.ai/) |
| 2025-09 | 47 npm downloads for the month — effectively zero traction | — | [npm downloads API](https://api.npmjs.org/downloads/range/2025-08-01:2026-09-12/claude-mem) |
| 2025-09 → 10 | 26 commits in Sept, 228 in Oct — shipping in near-silence | maintainer | repo git log |
| **2025-10-19** | **Ships `.claude-plugin/marketplace.json` (v4.0.2)** — installable from inside Claude Code instead of via global npm install | maintainer | commit `47c1398c` |
| 2025-10 | **npm 1,768/month — a 37x step from September, which then holds** | — | npm downloads API |
| 2025-11-03 / 11-13 | v5.0.0, v6.0.0 | maintainer | repo tags |
| **2025-11-30** | **v6.4.1 "Live AMA Announcement"** — ships a time-aware **in-terminal announcement to the installed base** for the first AMA (Dec 1–5, 5–7pm EST), with a live 🔴 indicator that auto-expires | maintainer | [commit 6e8d8231](https://github.com/thedotmack/claude-mem/commit/6e8d8231) |
| **2025-12-04** | **Product Hunt launch**, tagline *"An AI that takes notes on other AI's work in real-time"*. Same day ships **v6.5.1 "Product Hunt Launch Day UI Updates"** — PH badge rendered *inside the terminal* and in the viewer header, with a separate tracking URL for analytics | maintainer | [commit be28c095](https://github.com/thedotmack/claude-mem/commit/be28c095); [producthunt.com/products/claude-mem](https://www.producthunt.com/products/claude-mem) |
| 2025-12-08 | v7.0.0 | maintainer | repo tags |
| **2025-12-09 / 12-10** | **GitHub Trending #1 TypeScript (daily).** Also #1 TypeScript and #3 all-languages for Week 50 2025; #2 TypeScript for the month of December | organic | [trendshift.io/repositories/15496](https://trendshift.io/repositories/15496) |
| 2025-12-11 | Third party submits repo to HN — **1 point, 0 comments** | third party | [HN 46229436](https://news.ycombinator.com/item?id=46229436) |
| 2025-12-12 | Trendshift badge added; **README auto-translation script + cache** → Chinese, Japanese, Korean, Arabic, later Tagalog and zh-TW | maintainer | commits `6ebb6783`, `25684ea8` |
| 2025-12-22 | v8.0.0; Product Hunt badge removed from header | maintainer | commit `1cd0b534` |
| 2025-12-29 | "docs(cursor): Add marketing copy and value proposition messaging" | maintainer | commit `ed826925` |
| 2025-12-30 | **Maintainer self-submits to HN**: *"Cursor-Mem Now Available Claude-Mem 8.5.0"*, linking a tweet. **2 points, 1 comment.** He posted full marketing copy as the first comment; nobody engaged | maintainer | [HN 46429613](https://news.ycombinator.com/item?id=46429613) |
| 2026-01-05 | v9.0.0 | maintainer | repo tags |
| **2026-01-06** | **$CMEM Solana memecoin** — Meteora liquidity pool created | maintainer | [DexScreener](https://dexscreener.com/solana/6mzfakwnac6gsk1edfx93dzeukgfzrfq4uhwarhgsqyd) |
| 2026-01-13 | $CMEM contract address and trading links (Bags.fm, Jupiter, Photon, DEXScreener) added to the **README header** | maintainer | [commit c3149462](https://github.com/thedotmack/claude-mem/commit/c3149462) |
| **2026-01-15** | **Official X account (@Claude_Memory) and Discord link added to README** | maintainer | [commit 901cff90](https://github.com/thedotmack/claude-mem/commit/901cff90) |
| 2026-01-28 | Third-party dev.to article, 14 reactions — the highest dev.to engagement found | third party | [dev.to/suede](https://dev.to/suede/the-architecture-of-persistent-memory-for-claude-code-17d) |
| 2026-02-03 | "docs: update documentation links to official website" across 29 READMEs | maintainer | commit `596f0ad1` |
| **2026-02-03** | **Trendshift #1 repository across ALL languages (daily).** #6 all-languages for the month of February | organic | [trendshift.io/repositories/15496](https://trendshift.io/repositories/15496) |
| 2026-02-06 | "MAESTRO" automated PR-triage merges community translation and docs PRs at volume | maintainer | commits `2a62a94b`, `1e04f82f` |
| 2026-02-10 | v10.0.0 | maintainer | repo tags |
| 2026-02-17 | Maintainer comments on an unrelated HN thread, referencing claude-mem in passing | maintainer | [HN 47050658](https://news.ycombinator.com/item?id=47050658) |
| 2026-02-27 | Third-party dev.to article, 4 reactions | third party | [dev.to/shimo4228](https://dev.to/shimo4228/embedding-memory-into-claude-code-from-session-loss-to-persistent-context-54d8) |
| **2026-03-04** | **In-person launch party: "Claude-Mem Pro @ Mem0" — Claude-Mem in the Cloud**, Mem0 HQ, 564 Market St, San Francisco, 6:00 PM. Co-hosted by Alex Newman and Hassan Ferozpurwala. Live demo, three-layer memory architecture, origin story, Q&A. Event copy cites "over 30,000 GitHub stars" | maintainer | [luma.com/mwsp6qgz](https://luma.com/mwsp6qgz) |
| 2026-03-16 | Third-party YouTube video "Claude-Mem: Give Claude Code a Permanent Memory" | third party | [youtube.com/watch?v=EW2f7IFdtv8](https://www.youtube.com/watch?v=EW2f7IFdtv8) |
| 2026-03-17 | Star History chart added to README (added, removed, restored same day) | maintainer | commits `4d7b2978`, `8d740312`, `033c1c45` |
| 2026-03-28 | Third party submits repo to HN again — **2 points, 1 comment** | third party | [HN 47558167](https://news.ycombinator.com/item?id=47558167) |
| **2026-04-02** | "fix: add **Codex plugin manifest for discoverability**" | maintainer | commit `a74ff003` |
| 2026-04-03 | "update install CLI, ESM compat, and **Gemini CLI docs**" | maintainer | commit `76a880a3` |
| **2026-04-04** | **v11.0.0 — "refactor: replace custom installer with native Claude plugin commands."** Same day: semantic context injection via Chroma on UserPromptSubmit, `claude-mem-sync` for multi-machine sync | maintainer | commits `21b10b46`, `876cc4d8`, `5a274208` |
| **2026-04-07** | **v12.0.0.** smart-explore expanded to 24 languages with user-installable grammars | maintainer | commits `95889c7b`, `d0676aa0` |
| 2026-04-07 | Augment Code publishes "claude-mem hits 46.1K stars" (author Ani Galstian) | third party | [augmentcode.com](https://www.augmentcode.com/learn/claude-mem-46k-stars-persistent-memory-claude-code) |
| 2026-04-08 | "feat: Knowledge Agents — queryable corpora from claude-mem" | maintainer | commit `c648d5d8` |
| **2026-04** | **npm 7,011 -> 99,322 downloads/month — a 14x step** | — | npm downloads API |
| **2026-04-15** | **$CMEM header reverted** out of the README | maintainer | commit `4c792f02` |
| 2026-04-19 | Docker container "for easy spin-up" | maintainer | commit `97c7c999` |
| **2026-04-20** | **65.8K stars** at v12.3.8 — 1,792 commits, 106 contributors, 244 releases. **46.1K -> 65.8K in 13 days** | — | [augmentcode.com, pub. 2026-04-23](https://www.augmentcode.com/learn/claude-mem-65k-stars) |
| 2026-04-22 | Telegram notifier added | maintainer | commit `f2d361b9` |
| 2026-05-02 | UX redesign: installer, provider rename, `/learn-codebase`, welcome card, SessionStart hint | maintainer | commit `9e297305` |
| 2026-05-08 | v13.0.0 | maintainer | repo tags |
| 2026-05 → 08 | npm plateaus: 85,405 / 70,457 / 70,316 / 79,060 per month | — | npm downloads API |
| 2026-06-09 | **Deep telemetry** — GeoIP on worker events, person profiles "to unlock retention/cohort analytics", token-economics and compression metrics | maintainer | commits `4bdea1e2`, `217e2809`, `245c9b4e` |
| 2026-06-27 | Trendshift #4 daily JavaScript; #8 weekly (Week 25); #11 monthly JavaScript for May | organic | [trendshift.io/repositories/15496](https://trendshift.io/repositories/15496) |
| 2026-07-09 | Cloud sync feature, docs page and README pointer | maintainer | commits `770d7e28`, `1d12941e` |
| **2026-07-27** | **Product Hunt launch #2 — "CMEM Cloud"**, tagline *"Cross-device cross-agent context synced in real-time"*. **2 upvotes, 3 comments, day rank #151, not featured by Product Hunt** | maintainer | [hunted.space/product/claude-mem](https://hunted.space/product/claude-mem) |
| 2026-09-02 | Third-party dev.to article by `terminalchai` — **0 reactions, 0 comments** | third party | [dev.to/terminalchai](https://dev.to/terminalchai/claude-mem-persistent-long-term-memory-for-ai-coding-agents-5f8p) |
| **2026-09-02 / 09-03** | **Rebrand to "Grok Mem" begins** — `grok-mem.ai`, README lockup copy, Grok Bot install | maintainer | commits `8a434bbc`, `be44b6c8` |
| **2026-09-12** | **Snapshot as of research date: 93,703 stars, 8,246 forks, 300 watchers, 137+ contributors, 193 open issues, 234 npm versions, 2,686 commits, Apache-2.0. `claude-mem.ai` 308-redirects to `cmem.ai`** | — | GitHub API, npm registry, repo clone |

---

## 2. The April 2026 inflection — the single most important question

npm downloads stepped from **7,011 in March 2026 to 99,322 in April 2026 (14x)** and then plateaued in the 70–85K/month band through August. Stars moved **46.1K (Apr 7) -> 65.8K (Apr 20)**, the steepest verified segment in the project's life.

### Ruled out — no promotion event sits in this window

- **No Product Hunt launch.** The only two were 2025-12-04 and 2026-07-27.
- **No Hacker News submission.** The nearest were third-party posts at 1 and 2 points (2025-12-11, 2026-03-28).
- **No dev.to article.** Nearest were 2026-01-28 (14 reactions) and 2026-02-27 (4 reactions), both third-party, both months earlier.
- **No AMA or event.** The Mem0 launch party was 2026-03-04, a month earlier, and already cited "30,000+ stars".
- **No Trendshift peak.** Peaks were 2025-12-09 and 2026-02-03.
- **No YouTube spike attributable to the maintainer** — he has no channel.

### What does sit in the window — all within nine days

1. **2026-04-04, v11.0.0 — "replace custom installer with native Claude plugin commands."** Install stopped being `npm install -g claude-mem && claude-mem install` and became a native `/plugin install`. Mechanically the strongest candidate.
2. **2026-04-02 — Codex plugin manifest "for discoverability."** The intent is stated in the commit message itself.
3. **2026-04-03 — Gemini CLI docs**; **2026-04-19 — Docker image**. More hosts, more discovery surfaces.
4. **2026-04-07, v12.0.0** — two major versions in four days.

### Why the plateau shape supports this reading

A content spike decays. A distribution change steps and holds. April stepped and held (99K, then 85K / 70K / 70K / 79K). That is the signature of a **one-time expansion in addressable install surface**, not virality.

### The precedent

The same pattern had already happened once, an order of magnitude smaller: shipping `.claude-plugin/marketplace.json` on **2025-10-19** took npm from **47/month (Sept) to 1,768/month (Oct), 37x**, and held. **Both of this project's inflections are installer/host-surface changes.**

### Honest limit

This is temporal correlation plus a plausible mechanism, not proof. No download-referrer data is public. Nobody — not the maintainer, not any coverage — has published an attribution claim. Augment Code explicitly declines to attribute, writing only that the star count *"tells me this pain point is much more widespread than vendors would like to acknowledge."*

---

## 3. Channel-by-channel findings

### 3.1 DEV Community (dev.to) — third-party only, near-zero impact

**Correcting the premise this research started from:** the dev.to article did not drive growth. It was published **2026-09-02**, twelve months after the repo and roughly five months after the April inflection, and has **0 reactions and 0 comments** (checked 2026-09-12). Its author, `terminalchai`, runs a near-daily open-source-tool column — 27 articles, mostly 0–3 reactions each. It is a lagging indicator of fame, not a cause of it.

Articles found, all third-party, none by the maintainer:

- 2026-01-28 — [The Architecture of Persistent Memory for Claude Code](https://dev.to/suede/the-architecture-of-persistent-memory-for-claude-code-17d), `suede`, **14 reactions / 1 comment** (highest found)
- 2026-02-27 — [Embedding Memory into Claude Code](https://dev.to/shimo4228/embedding-memory-into-claude-code-from-session-loss-to-persistent-context-54d8), `shimo4228`, 4 / 1
- 2026-09-02 — [Claude-Mem: Persistent Long-Term Memory for AI Coding Agents](https://dev.to/terminalchai/claude-mem-persistent-long-term-memory-for-ai-coding-agents-5f8p), `terminalchai`, **0 / 0**
- Dates unverified: [kanta13jp1](https://dev.to/kanta13jp1/adding-persistent-memory-to-claude-code-with-claude-mem-plus-a-diy-lightweight-alternative-4gha), [wonderlab "Open Source Project of the Day (Part 21)"](https://dev.to/wonderlab/open-source-project-of-the-day-part-21-claude-mem-persistent-memory-compression-system-for-1db8), [ohugonnot](https://dev.to/ohugonnot/persistent-memory-in-claude-code-whats-worth-keeping-54ck)

**Structure of the terminalchai article**, since article structure was an explicit research question: ~800 words, problem-first. Opening sentence verbatim: *"One of the most persistent hurdles in working with command-line AI coding assistants (such as Claude Code, Antigravity CLI, and OpenCode) is context fragmentation across sessions."* Second sentence: *"claude-mem is an open-source memory compression and retrieval engine created by thedotmack."* Then five feature descriptions, install instructions, conclusion. **No code demo and no concrete example early.** Tags: #ai #programming #opensource. A competent but generic tool writeup — consistent with its zero engagement.

### 3.2 Hacker News — no Show HN ever, and the maintainer's own attempt failed

This is the most counter-intuitive finding in the research.

- **No Show HN for claude-mem exists.** Verified against the Algolia `tags=show_hn` index. Every Show HN returned for memory-for-Claude is a *competitor* — Recall (171 pts), A-MEM, echovault, claude-mem-viz, Hopsule, Engram, Memex.
- The repo was submitted to HN **twice, both times by third parties, both flopped**: [handfuloflight, 2025-12-11 — 1 point, 0 comments](https://news.ycombinator.com/item?id=46229436) and [perelin, 2026-03-28 — 2 points, 1 comment](https://news.ycombinator.com/item?id=47558167).
- The maintainer's **own** submission — [2025-12-30, "Cursor-Mem Now Available Claude-Mem 8.5.0"](https://news.ycombinator.com/item?id=46429613) — got **2 points**. He posted full marketing copy as the first comment: *"Every Cursor session starts fresh—your AI forgets yesterday's work. Claude-mem fixes that by building cumulative knowledge about your codebase, decisions, and patterns."* Nobody engaged.

**But HN mattered, in a different way: claude-mem became the category's default comparison benchmark.** 21 HN comments reference it, overwhelmingly in the form "how is this different from claude-mem?":

- *"curious how this is different from claude-mem?"* — [on Show HN: A-MEM, 2026-01-15](https://news.ycombinator.com/item?id=46637436)
- *"Congrats for this! how does this differs from claude-mem? I've been using claude-mem for a while now"* — [2025-12-30](https://news.ycombinator.com/item?id=46427906)
- *"what's the difference between you guys and any persistent development memory tools like claude-mem?"* — [Show HN: Hopsule, 2026-03-17](https://news.ycombinator.com/item?id=47415524)
- *"There are actually good tools to reduce token use like claude-mem"* — [2026-03-31](https://news.ycombinator.com/item?id=47585038)
- *"Any thoughts on claude-mem + context-mode?"* — [Claude Opus 4.7 thread, 2026-04-16](https://news.ycombinator.com/item?id=47795027)
- Competitors positioning against it: *"every Claude Code memory plugin I looked at (claude-mem, Total Recall, ContextForge) solves stateless sessions the same way"* — [Engram, 2026-03-18](https://news.ycombinator.com/item?id=47422640)
- An unprompted user endorsement: *"I installed claude-mem today and it's already come in handy"* — [2025-12-30](https://news.ycombinator.com/item?id=46430502)

That is category leadership earned elsewhere and *reflected* on HN, not manufactured on it.

### 3.3 Reddit — NOT MEASURED. This is a real gap.

**I could not retrieve a single Reddit data point.** Every access path failed on 2026-09-12:

- `reddit.com/search.json` returned HTTP 302/403 to scripted requests
- `old.reddit.com` returned HTTP 302
- WebFetch is blocked from reddit.com by the tool
- redlib mirrors returned HTTP 429 and 410
- reddit.com is excluded from the search tool's allowed domains (the crawler is blocked by Reddit)

**Treat this as UNKNOWN, not as zero.** Given that r/ClaudeAI and r/ClaudeCode are among the largest venues for exactly this tool category, it is entirely plausible that meaningful Reddit promotion happened and this research simply cannot see it. Anyone extending this research should check r/ClaudeAI, r/ClaudeCode, r/LocalLLaMA, r/AI_Agents and r/LLMDevs manually in a browser. **Do not cite this document as evidence that Reddit promotion did not occur.**

### 3.4 X / Twitter — accounts confirmed, engagement UNVERIFIED

- Official project account **@Claude_Memory** and maintainer account **[@thedotmack](https://x.com/thedotmack)**, both added to the README on 2026-01-15 ([commit 901cff90](https://github.com/thedotmack/claude-mem/commit/901cff90)).
- The account was demonstrably used for launches: on 2025-12-30 he submitted an @Claude_Memory tweet to Hacker News, which is how the account surfaced in this research at all.
- One confirmed tweet promotes a live-coding stream: *"This will show everyone EXACTLY how I use Claude-Mem to code things from scratch. I think it'll be a really fun time with probably a lot of laughs, joy, heartache, probably lots of cursing at the thing… you really never know when you're working against the clock 😭"* ([status/2011685458515017745](https://x.com/thedotmack/status/2011685458515017745))
- **Post dates, follower counts, impressions and engagement could not be retrieved** — x.com blocked all fetch paths. Whether X drove meaningful traffic is **unknown**.

### 3.5 LinkedIn — no evidence found

Profile exists and is branded **"Alex Newman - Claude-Mem"** ([linkedin.com/in/alexnewman](https://www.linkedin.com/in/alexnewman/)) — his professional identity is fully merged with the project. **No launch posts or promotional posts were found.** Not verified either way beyond the profile itself.

### 3.6 YouTube — no maintainer channel found; third-party videos only, all post-growth

**No evidence found** that the maintainer produced, hosted or seeded any video. Third-party videos found:

- [Claude-Mem: Give Claude Code a Permanent Memory](https://www.youtube.com/watch?v=EW2f7IFdtv8) — 2026-03-16
- [How To Give Claude Persistent Memory [Claude-mem]](https://www.youtube.com/watch?v=LfkpNyTsi7o)
- [Claude Mem GitHub Walkthrough: Preserve AI Coding Context After Every Terminal Restart](https://www.youtube.com/watch?v=U7nhQWn6UJs)
- [I Gave Claude Code Permanent Memory - The Results Are Shocking](https://www.youtube.com/watch?v=EsFa7W-FYdM)

These cluster in and after **March 2026** — i.e. after Trending #1 in December and February. Consistent with creators chasing an already-hot repo, not with seeding.

### 3.7 Third-party coverage — organic, and lagging

- [Augment Code, "claude-mem hits 46.1K stars"](https://www.augmentcode.com/learn/claude-mem-46k-stars-persistent-memory-claude-code) — pub. 2026-04-07, author Ani Galstian
- [Augment Code, "claude-mem hits 65.8K stars"](https://www.augmentcode.com/learn/claude-mem-65k-stars) — pub. 2026-04-23, author Paula Hingel. Notes much of claude-mem's own development was co-authored with Claude Opus 4.5/4.6/4.7, "a visible example of AI-assisted open source development at scale"
- [agentpedia.codes complete guide](https://agentpedia.codes/blog/claude-mem-persistent-memory-guide)
- [alternativeto.net/software/claude-mem](https://alternativeto.net/software/claude-mem)
- [claudemarketplaces.com](https://claudemarketplaces.com/plugins/thedotmack-claude-mem)
- [skillsllm.com/skill/claude-mem](https://skillsllm.com/skill/claude-mem)
- [Labyrinth Analytics, honest 4-way comparison](https://labyrinthanalyticsconsulting.com/blog/claude-memory-primitive-vs-loreconvo-vs-claude-mem-vs-mem0) — 2026-08-18

**All coverage appears organic.** No evidence of seeding was found. Notably, two of the largest pieces are content marketing by a *competitor* (Augment Code), writing about claude-mem because it was too big to ignore.

### 3.8 Docs site / landing page — existed on day one

`claude-mem.ai` was live on **2025-09-06, the same day as the first public commit** ([Wayback](https://web.archive.org/web/20250906211833/https://claude-mem.ai/)). The first snapshot is a single line: *"Claude-Mem | Your AI Assistant Finally Has a Memory"*.

By [2025-12-16](https://web.archive.org/web/20251216130058/https://claude-mem.ai/) it was a full site leading with *"AI MEMORY THAT ACTUALLY WORKS — Stop explaining context. Start building faster."* and the install command above the fold: `/plugin marketplace add thedotmack/claude-mem && /plugin install claude-mem`.

As of 2026-09-12 `claude-mem.ai` 308-redirects to `cmem.ai`, and the README points at `grok-mem.ai`.

---

## 4. The framing and hook — verbatim

- **Landing page, day one (2025-09-06):** *"Your AI Assistant Finally Has a Memory"*
- **Landing page (Dec 2025):** *"AI MEMORY THAT ACTUALLY WORKS — Stop explaining context. Start building faster."* and *"Claude-Mem is your AI's trusty note-taking sidekick. Never lose track ever again."*
- **First README (Sept 2025):** *"Remember that one thing? Neither do we… but `claude-mem` does! 😵‍💫"* / *"Stop repeating yourself. `claude-mem` remembers what you and Claude Code figure out, so every new chat starts smarter than the last."* / *"⚡️ 10-Second Setup"*
- **Product Hunt (2025-12-04):** *"An AI that takes notes on other AI's work in real-time"*
- **Landing page mechanism line:** *"One AI takes notes about what another AI does."*
- **Event copy (2026-03-04):** *"AI agents forget everything between sessions. Every conversation starts from zero. Claude-Mem fixes that."*
- **Current repo description (2026-09-12):** *"Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions."*

**The pattern:** the pain is always **re-explaining yourself** — never architecture, never embeddings, never RAG. The mechanism is always described as a **character** ("note-taking sidekick", "one AI takes notes about what another AI does"), never as a system. And the **install command sits adjacent to the hook every single time**.

---

## 5. Sequence pattern — tool-first, decisively

Working npm package (2025-08-30) -> public repo and landing page the same day (2025-09-06) -> **roughly twelve weeks shipping in near-silence** (npm under 2K/month) -> first promotion beat (AMA, 2025-11-30) -> Product Hunt (2025-12-04) -> Trending #1 (2025-12-09).

He published **no theory post, no manifesto, no "how I built it," no architecture essay.** He shipped 234 npm versions and 2,686 commits in twelve months — up to 23 releases in a single day — and let distribution do the work. The articles came roughly a year later, from other people, because the thing was already everywhere.

**Articles were an output of traction, never an input.**

---

## 6. Maintainer vs. third parties — the cleanest split in the data

**The maintainer did:** landing page on day one · npm + GitHub + Claude Code plugin listing · in-terminal AMA announcement · Product Hunt launch (2025-12-04) with an in-product PH badge and tracking URL · one failed HN self-submission · $CMEM memecoin · official X account and Discord · README auto-translation into 6+ languages · in-person launch party at Mem0 HQ · Star History in README · relentless release cadence · host-surface expansion · deep telemetry · Grok Mem rebrand.

**Third parties did:** both non-self HN submissions of the repo (both flopped) · **all** dev.to articles · **all** YouTube videos · all blog, newsletter, comparison and aggregator coverage · the HN comment culture that made it the category benchmark · GitHub Trending and Trendshift placement.

**Headline for another maintainer: he wrote zero articles and never got a Show HN off the ground.**

---

## 7. Deliberate and repeatable vs. luck and timing

### Repeatable

1. **Landing page live on day one**, before any traction. Cheap, and it meant every later mention had somewhere to land.
2. **Promotion shipped inside the product.** The AMA notice and the Product Hunt badge were *released as versions* into users' terminals, with tracking URLs. The installed base became the distribution channel. **The single most transferable tactic in this research.**
3. **Relentless release cadence as the growth engine** — 234 versions in 12 months, up to 23 in a day. Every release refreshes GitHub Trending eligibility and npm ranking.
4. **Remove install friction, then remove it again.** Both inflections are this.
5. **Expand host surface aggressively** — Claude Code, Cursor, Codex, Gemini, OpenCode, Copilot, OpenClaw, Hermes, Docker. Each host is a new discovery channel.
6. **Auto-translated READMEs** via a script with a cache — six-plus languages.
7. **Merge community PRs at volume** (137+ contributors, automated PR triage). Contributors become advocates.
8. **Instrument everything** — GeoIP, cohort and retention analytics, badge tracking URLs. He measured what worked.

### Luck / timing / not repeatable

- Anthropic shipping the Claude Code plugin marketplace at the exact moment this project existed, and claude-mem being early into it.
- **GitHub Trending #1 across all languages** — a self-reinforcing flywheel you cannot buy.
- The category being completely unserved in late 2025.

### Failed, and equally instructive

- **Hacker News self-promotion: 2 points.** He tried; it did not work.
- **Product Hunt launch #2 (2026-07-27): 2 upvotes, rank #151, not featured** — with ~90K stars behind it.
- **The $CMEM Solana memecoin** (pool 2026-01-06, README links 2026-01-13). As of 2026-09-12: **FDV $7,190, 24h volume $23**. Pulled from the README header by 2026-04-15. A crypto token did not grow a dev tool, and plausibly cost credibility.
- **dev.to: 0 reactions** on the most recent article, at 93K stars.

---

## 8. Confidence and limits

| Claim | Confidence |
|---|---|
| Repo/npm/commit/tag dates, star and download counts | **High** — primary APIs and a full repo clone |
| Both inflections coincide with installer/host changes | **High** — dates are exact on both sides |
| Installer changes *caused* the inflections | **Medium** — correlation plus mechanism; no referrer data exists |
| No Show HN ever existed | **High** — Algolia `show_hn` index checked directly |
| dev.to did not drive growth | **High** — all articles post-date growth, engagement 0–14 |
| YouTube/LinkedIn maintainer promotion | **Low / no evidence found** — absence of evidence, not evidence of absence |
| X engagement levels | **Unknown** — accounts confirmed, metrics unretrievable |
| Reddit, entirely | **UNKNOWN — not measured.** All access paths blocked |

Product Hunt engagement numbers for the 2025-12-04 launch conflict across sources (one aggregator reports 119 upvotes / 15 comments; the Product Hunt product page rendered as 16 upvotes / 115 comments, likely transposed fields). **The date is confirmed; the numbers are not.**

Figures in this document are as of **2026-09-12** and will decay. The project was mid-rebrand to "Grok Mem" at the time of research, so names and URLs may have moved since.
