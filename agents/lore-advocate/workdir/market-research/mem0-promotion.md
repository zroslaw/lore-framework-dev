# How mem0 Was Promoted — Growth Post-Mortem

**Researched:** 2026-09-12
**Subject:** [mem0ai/mem0](https://github.com/mem0ai/mem0) — "The Memory Layer for AI Agents", by Taranjeet Singh ([@taranjeetio](https://x.com/taranjeetio)) and Deshraj Yadav ([@deshrajdry](https://x.com/deshrajdry)), Mem0 Inc. (YC S24)
**Researched by:** mem0 promotion research pass — entry two in the lore-advocate competitive-research archive (entry one: [claude-mem-promotion.md](./claude-mem-promotion.md))
**Method:** public sources only — GitHub API, a full repo clone (2,626 commits, 403 tags), PyPI JSON + pypistats + pepy APIs, npm registry + downloads APIs, hn.algolia.com API (including item and `show_hn` indexes), dev.to API, Wayback Machine CDX + dated snapshots of the GitHub repo page (used to reconstruct a star timeline), Twitter snowflake-ID decoding, Y Combinator, Trendshift, Product Hunt aggregators, web search and page fetches

## Summary — the one conclusion that matters

**mem0's growth story is the opposite shape from claude-mem's, and the single biggest lesson is that mem0's biggest inflection was a repositioning of an asset it already owned — not a launch, and not an installer.** In one week in July 2024 the repo went from **9,368 to 17,141 stars (+7,773)** after the founders renamed their two-year-old, ~9K-star RAG framework *Embedchain* into *mem0*, announced it on X, and hit **GitHub Trending #1 on 2024-07-17**. They kept the old repo, so they kept the old stars, the old contributors and the old SEO. Every beat the brief expected to matter landed *after* that and moved far less: the **Show HN got 201 points — 100x claude-mem's 2 — and produced only about +766 stars over five days**. And in a direct test of entry one's thesis, mem0's Claude Code plugin (2026-03-25) produced **no download step at all** — PyPI held flat at ~92K/day across the window. So the two entries disagree in a useful way: claude-mem's growth was a step function driven by install surface; mem0's was a one-time repositioning burst followed by two years of smooth compounding driven by being a *dependency inside other people's frameworks* (CrewAI, LlamaIndex, Vercel AI SDK, AWS). For an unfunded maintainer the transferable part is not the funding and not the Show HN — it is that distribution-by-integration compounds, and that a good relaunch of something you already have beats a good launch of something new.

> **Caveats carried throughout:** Reddit is **NOT MEASURED** (see §3.4) — I got further than entry one (identified and solved the bot-challenge proof-of-work) but still could not read results. X/Twitter post-level engagement is **NOT MEASURED**. The star timeline is reconstructed from dated Wayback snapshots, so it is accurate at sample points and interpolated between them.

---

## 1. Chronological timeline

Volatile figures are date-stamped in place; they decay.

| Date | Event | Who | Evidence |
|---|---|---|---|
| 2023-06-19 | PyPI `embedchain` 0.0.1 published; GitHub org `mem0ai` created (as `embedchain`) | team | [PyPI](https://pypi.org/pypi/embedchain/json); GitHub API |
| **2023-06-20** | **Repo created — as `embedchain/embedchain`**, "Simplest open source retrieval (RAG) framework". First commit "Hello World" | team | repo git log; GitHub repo id 656099147 |
| 2023-06 → 2024-01 | Embedchain ships hard: 69/150/67/110/88/69/91/83 commits per month | team | repo git log |
| 2023-10-03 | `embedchain.ai` first archived | team | [Wayback CDX](http://web.archive.org/cdx/search/cdx?url=embedchain.ai&output=json) |
| 2023-10-20 | "Embedchain" submitted to HN — **3 points, 0 comments** | third party | [HN 37961663](https://news.ycombinator.com/item?id=37961663) |
| **2023-12-20** | **"Show HN: Sadhguru AI" — 7 points.** The meditation app whose viral Indian userbase produced the "it doesn't remember" feedback that motivated the pivot | team | [HN 38705522](https://news.ycombinator.com/item?id=38705522); [TechCrunch](https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps/) |
| **2024-02 → 2024-05** | **Embedchain stalls: 32 / 22 / 5 / 8 commits per month.** The project is dying | — | repo git log |
| 2024-05-18 | PyPI `mem0ai` 0.0.1 quietly published — new name reserved 8 weeks before it is used | team | [PyPI](https://pypi.org/pypi/mem0ai/json) |
| **2024-06-18** | **X: "Introducing @mem0ai – long term memory for AI agents… Last time, we launched a waitlist for Mem0 playground and got great feedback."** Waitlist-first, a month before code | team | [x.com/taranjeetio/status/1803112748618064096](https://x.com/taranjeetio/status/1803112748618064096) (date decoded from snowflake ID) |
| 2024-07-07 | "Integrate Mem0 (#1462)" — first mem0 code inside the embedchain repo | team | commit `bbe56107` |
| **2024-07-12** | **THE PIVOT: commit `f842a92e` "Rename embedchain to mem0 and open sourcing code for long term memory (#1474)".** Same repo, same stars, new identity. Stars that day: **8,993** | team | [commit f842a92e](https://github.com/mem0ai/mem0/commit/f842a92e); [Wayback 20240713](https://web.archive.org/web/20240713/https://github.com/mem0ai/mem0) |
| 2024-07-12 | Issue #1475 "Rebrand to mem0 unclear to consumers" — users confused; embedchain.ai left up with no notice | third party | [issue #1475](https://github.com/mem0ai/mem0/issues/1475) |
| **2024-07-15** | **X launch: "Introducing Mem0 (@mem0ai) - the memory layer for LLMs and AI Agents, enabling truly personalized AI interactions."** | team | [x.com/taranjeetio/status/1812862793324077338](https://x.com/taranjeetio/status/1812862793324077338) |
| **2024-07-17** | **GitHub Trending #1** | organic | [trendshift.io/repositories/11194](https://trendshift.io/repositories/11194) |
| **2024-07-18 → 07-25** | **THE INFLECTION: 9,368 → 17,141 stars. +7,773 in seven days (~1,110/day).** No Show HN, no Product Hunt, no article in this window | — | Wayback snapshots [0718](https://web.archive.org/web/20240718/https://github.com/mem0ai/mem0), [0720](https://web.archive.org/web/20240720/https://github.com/mem0ai/mem0), [0722](https://web.archive.org/web/20240722/https://github.com/mem0ai/mem0), [0725](https://web.archive.org/web/20240725/https://github.com/mem0ai/mem0) |
| 2024-07-22 | npm `mem0ai` 1.0.0 — TypeScript SDK, second language surface | team | [registry.npmjs.org/mem0ai](https://registry.npmjs.org/mem0ai) |
| 2024-07-26 | "Feat: Add mem0 newsletter link (#1588)" | team | commit `9148cce8` |
| **2024-08-01** | **`mem0.ai` first archived — still a half-built template** (placeholder copy: *"Some numbers and benchmarks and stuff here"*, *"Is it accessible? Is it styled? Is it animated?"*). Tagline: *"The Memory Layer for Personalized AI"*. Hero is a **code snippet**. Star widget reads 18,431 | team | [Wayback 20240801002341](https://web.archive.org/web/20240801002341/https://www.mem0.ai/) |
| 2024-08-16 / 08-20 | LangGraph docs; AutoGen docs — integration-doc machine starts | team | commits `1e39a22c`, `e31ca239` |
| **2024-09-04** | **Show HN: "Mem0 – open-source Memory Layer for AI apps" — 201 points, 61 comments.** Both founders answer nearly every question within minutes. **HN moderator `dang` flags "booster comments… presumably by friends trying to help the submitters out"** | team | [HN 41447317](https://news.ycombinator.com/item?id=41447317) |
| 2024-09-04 | **YC Launch page — 634 upvotes.** *"Mem0 adds memory to AI applications, solving the problem of repetitive, stateless interactions"* | team | [ycombinator.com/launches/LpA-mem0](https://www.ycombinator.com/launches/LpA-mem0-open-source-memory-layer-for-ai-apps) |
| 2024-09-03 → 09-08 | **Stars 20,600 → 21,366. The 201-point Show HN moved ~766 stars in five days** | — | Wayback snapshots |
| 2024-10-29 | npm `@mem0/vercel-ai-provider` — Vercel AI SDK surface | team | [npm](https://registry.npmjs.org/@mem0/vercel-ai-provider) |
| **2024-10-31** | **PyPI `llama-index-memory-mem0` — official LlamaIndex-namespace package.** mem0 is now inside someone else's framework | team/LlamaIndex | [PyPI](https://pypi.org/pypi/llama-index-memory-mem0/json) |
| 2024-11-04 | **Show HN: Mem0 Browser Extension — 34 points, 4 comments** | team | [HN 42042401](https://news.ycombinator.com/item?id=42042401) |
| **2024-11-25** | **CrewAI 0.83.0 declares `mem0ai` as a dependency extra — mem0 becomes a native CrewAI memory provider** | CrewAI | [PyPI crewai 0.83.0](https://pypi.org/pypi/crewai/0.83.0/json) |
| 2025-03-06 | MCP + Cursor docs (#2318) — first MCP surface | team | commit `41a42da7` |
| 2025-03-26 → 2025-05-23 | Integration-doc blitz: LiveKit, ElevenLabs, Pipecat, Flowise, Agno, Keywords AI, Google ADK, Mastra, Raycast | team | commits `69a91d5c`, `45e5f2af`, `039756ab`, `91a28c7f`, `31861e9a`, `9be6850b`, `1c44b675`, `6cebddeb` |
| **2025-04-28** | **arXiv paper 2504.19413 "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory."** HuggingFace Daily Papers 2025-04-29, **71 upvotes, submitted by `akhaliq` (third party)** | team | [arXiv](https://arxiv.org/abs/2504.19413); [HF papers](https://huggingface.co/papers/2504.19413) |
| 2025-05-06 | Competitor rebuttal: Zep publishes *"Lies, Damn Lies, & Statistics: Is Mem0 SOTA in Agent Memory?"* — **2 points on HN** | third party | [blog.getzep.com](https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory) |
| 2025-05-13 | **Show HN: OpenMemory — 8 points, 0 comments.** MCP play flops on HN | team | [HN 43974991](https://news.ycombinator.com/item?id=43974991) |
| **2025-07-03** | **Product Hunt: "OpenMemory Chrome Extension" — 172 upvotes, 10 comments, #5 Product of the Day.** *"Sync memory across AI's so they pick up where you left off."* | team | [hunted.space](https://www.hunted.space/product/openmemory-chrome-extension/launches/openmemory-chrome-extension) |
| **2025-04-14 → 2025-07-19** | **Stars 27,505 → 37,028 (+9,523 in ~14 weeks, ~97/day)** — the strongest sustained stretch after July 2024 | — | Wayback snapshots |
| **2025-10-28** | **Funding announced: $24M ($3.9M seed, Kindred Ventures; $20M Series A, Basis Set Ventures; + Peak XV, YC, GitHub Fund).** TechCrunch coverage. Cited: 41K stars, 14M Python downloads, API calls 35M (Q1) → 186M (Q3), 80,000+ developers signed up | team/press | [TechCrunch](https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps/); [mem0.ai/series-a](https://mem0.ai/series-a) |
| 2025-10-28 | Funding news submitted to HN twice — **2 points** and **1 point** | third party | [HN 45734522](https://news.ycombinator.com/item?id=45734522), [HN 45994916](https://news.ycombinator.com/item?id=45994916) |
| 2025-10-28 | **AWS names mem0 exclusive memory provider for their Agent SDK** (claimed in the Series A post) | AWS | [mem0.ai/series-a](https://mem0.ai/series-a) |
| **2025-11 → 2026-02** | **Commit volume collapses: 16 / 11 / 6 / 12 per month.** The quietest stretch in the repo's life, immediately after funding | team | repo git log |
| 2026-02-02 | OpenClaw plugin + docs (#3964) — agent-host plugin era begins | team | commit `3d3e875d` |
| **2026-03** | **Commits explode to 147/month** (then 119 in April, 200 in June) — an all-in pivot onto agent-host surfaces | team | repo git log |
| **2026-03-25** | **Claude Code + Cursor plugin (#4518)** | team | commit `3c2683c1` |
| 2026-04-02 | Codex plugin (#4665) | team | commit `c0cae686` |
| **2026-03 → 2026-04** | **PyPI holds FLAT at ~92,000 downloads/day across the plugin launch. No step.** | — | [pypistats](https://pypistats.org/api/packages/mem0ai/overall) |
| 2026-05-22 | "plugin v0.2.1 — Tiers 1-8 + PostHog telemetry" — instrumentation | team | commit `0d61af60` |
| 2026-07-29 | n8n community node (#6517) and Zapier app (#6518) — no-code surfaces | team | commits `d4869d24`, `e168d48e` |
| 2026-08-13 | Kimi Code plugin (#6919) | team | commit `ba2fb9f4` |
| 2026-08-22 / 08-24 | Strands MemoryStore (#7021); DeepSeek Harness plugin (#7027) | team | commits `8d5b7865`, `7e096155` |
| 2026-08-31 | MiniMax Marketplace plugin (#7027-adjacent) | team | commit `c9a0c19a` |
| **2026-09-12** | **Snapshot as of research date: 65,156 stars, 7,627 forks, 248 watchers, 738 open issues, 2,626 commits, 403 tags, Apache-2.0. PyPI `mem0ai` 42.36M total downloads, 189 releases; npm `mem0ai` 126 versions.** Landing page: *"AI memory that persists across sessions and agents"* | — | GitHub API, PyPI, pepy, npm |

---

## 2. The July 2024 inflection — the single most important question

Stars went **9,368 (2024-07-18) → 17,141 (2024-07-25): +7,773 in seven days**, roughly 1,110/day. For scale, mem0's *entire* sustained rate in 2026 is about **100/day**. Nothing else in the project's history is within an order of magnitude of that week.

### What sits in the window

1. **2024-07-12 — the rename.** `embedchain/embedchain` became `mem0ai/mem0` in a single commit. The repo, its ~9,000 stars, its contributor graph, its inbound links and its search history all carried over.
2. **2024-07-15 — the X announcement.** *"Introducing Mem0 (@mem0ai) - the memory layer for LLMs and AI Agents, enabling truly personalized AI interactions."*
3. **2024-07-17 — GitHub Trending #1.**

### Why the rename is the mechanism, not a coincidence

GitHub Trending ranks on **stars gained**, not stars held. A repo with an existing audience — 9K stargazers, a mailing list, watchers, an active contributor base — that suddenly reframes itself and announces to that base generates exactly the short sharp burst Trending rewards. Trending then puts it in front of a much larger audience, which is the flywheel. A brand-new repo has no base to burst from.

So the rename was not a cosmetic decision. **It converted two years of accumulated Embedchain audience into one week of concentrated signal**, at a moment when "memory for AI agents" was an unserved category and "RAG framework" was a crowded dying one. Note the timing: Embedchain had fallen to **5 commits in April 2024 and 8 in May**. They relaunched a stalling asset rather than starting over.

### Ruled out — what is *not* in the window

- **No Show HN.** It came **2024-09-04**, six weeks later.
- **No Product Hunt.** The only PH launch found was **2025-07-03**.
- **No article, paper or video.** The arXiv paper was **2025-04-28**, nine months later.
- **No funding announcement.** That was **2025-10-28**, fifteen months later.
- **No landing page worth the name.** On 2024-08-01 `mem0.ai` still carried shadcn placeholder text.

### Honest limit

This is temporal correlation plus a plausible mechanism. No referrer data is public. The star timeline is sampled from Wayback snapshots, so the precise day the burst started is bounded to 2024-07-18 ± 2 days, not pinpointed. The team has never published an attribution claim for this week.

---

## 3. Channel-by-channel findings

### 3.1 Hacker News — a genuine hit that barely moved the needle

This is the most counter-intuitive finding in the research, and it cuts directly against the assumption the brief started from.

**[Show HN: Mem0 – open-source Memory Layer for AI apps](https://news.ycombinator.com/item?id=41447317), 2024-09-04, 201 points, 61 comments** — by `staranjeet`. On raw numbers this is a strong Show HN and **100x claude-mem's 2-point self-submission**.

**And it produced roughly +766 stars over five days** (20,600 on 2024-09-03 → 21,366 on 2024-09-08). The July rename week produced +7,773 in seven.

What the founders did well, and what is copyable:

- **Both founders worked the thread in real time.** `staranjeet` (CEO) and `deshraj` (CTO) answered nearly every substantive question, often within 20–40 minutes, with structured numbered answers rather than marketing copy.
- **They shipped from inside the thread.** To a bug-adjacent request: *"Right now you cannot change the 'user' you are chatting as yet but we can definitely make it happen. **Will ship this update later today.** :)"*
- **They answered the competitive question head-on.** Asked how mem0 differs from Claude prompt caching: *"Claude's cache is designed for short-term memory, clearing every 5 minutes. In contrast, Mem0 is built for long-term information storage, retaining data indefinitely unless instructed otherwise."*
- **They conceded weaknesses.** On GDPR: *"Currently, we process data in the US and are not yet fully GDPR-compliant, but we're actively working on it."*

**What they did badly, and it is on the record.** HN moderator `dang` publicly flagged part of the thread: *"I flagged some (most? not sure) of them as booster comments, presumably by friends trying to help the submitters out. HN users aren't supposed to do that and **YC founders are given strict instructions not to do it** (and scoldings when it happens)."* Another user: *"If I see this many questions that could have been taken straight from an FAQ, all followed up with 'great question, we do so and so..', my alarm bells go off. **Shady marketing indeed.**"* The astroturfing was visible, called out, and moderated.

**Every other mem0 HN attempt underperformed:**

- [Show HN: Mem0 Browser Extension](https://news.ycombinator.com/item?id=42042401), 2024-11-04 — 34 points, 4 comments
- [Show HN: OpenMemory](https://news.ycombinator.com/item?id=43974991), 2025-05-13 — 8 points, 0 comments
- The $24M funding news, submitted by third parties — [2 points](https://news.ycombinator.com/item?id=45734522) and [1 point](https://news.ycombinator.com/item?id=45994916)
- The team's own [mem0.ai blog post](https://news.ycombinator.com/item?id=46840181), 2026-01-31 — 3 points, 0 comments

**Like claude-mem, mem0 became the category's default comparison benchmark on HN** — and unlike claude-mem, it is mostly being attacked. A partial list of competitor Show HNs positioning explicitly against it: [VAC Memory "80.1% LoCoMo vs Mem0's 68%"](https://news.ycombinator.com/item?id=46123550), [Engram "beats Mem0 by 20% on LOCOMO"](https://news.ycombinator.com/item?id=47153987), [Forensic "beats Mem0 with 90.1%"](https://news.ycombinator.com/item?id=47553405), [Cortex "beats Mem0 on LoCoMo"](https://news.ycombinator.com/item?id=47501353), [MenteDB "7x fewer tokens than mem0"](https://news.ycombinator.com/item?id=48912059), and a titled-as-criticism [Show HN: "Mem0 thinks our 2023 conversation happened in 2026"](https://news.ycombinator.com/item?id=47961750). There is even [I beat mem0 on long eval memory and could not care less](https://news.ycombinator.com/item?id=48919485). **Publishing a benchmark paper made mem0 the number everyone else benchmarks against — which is category leadership and a permanent attack surface at the same time.**

### 3.2 Product Hunt — one real launch, decent, late

**[OpenMemory Chrome Extension](https://www.hunted.space/product/openmemory-chrome-extension/launches/openmemory-chrome-extension), 2025-07-03 — 172 upvotes, 10 comments, #5 Product of the Day.** Tagline: *"Sync memory across AI's so they pick up where you left off."* Maker: Taranjeet.

No Product Hunt launch was found for the core mem0 library itself; `producthunt.com/products/mem0` returns 404 (checked 2026-09-12). Note this is an accessory product (a browser extension), not the thing that makes money — and it launched **a year after** the growth inflection.

Compare claude-mem: PH launch #1 in Dec 2025 with disputed numbers, PH launch #2 in Jul 2026 with **2 upvotes at rank #151**. mem0's 172/#5 is a materially better PH outcome, but it is still not where either project's growth came from.

### 3.3 dev.to / Medium / blogs — the strongest convergence with entry one

**The team publishes essentially nothing on third-party developer-content platforms, and everything written about mem0 there is third-party and near-dead.**

All 15 dev.to articles tagged `mem0` (dev.to API, 2026-09-12) are third-party. Engagement, in full:

| Date | Author | Reactions / Comments | Title |
|---|---|---|---|
| 2026-08-05 | `mukesh_13` | **1 / 4** | Mem0 vs Zep vs LangChain Memory vs Letta |
| 2026-08-25 | `alfredoizjr` | 1 / 0 | ContextForge vs Mem0 vs Zep |
| 2026-02-23 | `ninadwrites` | 2 / 0 | Self-Hosting Mem0: A Complete Docker Deployment Guide |
| 2025-06-13 | `surgedatalab` | 1 / 0 | Unlocking Memory in Agentic AI |
| 2026-09-05 | `mukesh_13` | 0 / 0 | Agentic AI Is Mostly Marketing |
| 2026-09-05 | `realmrmemory` | 0 / 0 | Choosing the Right AI Agent Memory Framework |
| …9 more | various | **all 0 / 0** | — |

**Peak engagement across every dev.to article about a 65,000-star project is 2 reactions.** Entry one found the same thing about claude-mem (0–14 reactions). Two completely different projects, same verdict: **dev.to is not a growth channel for developer infrastructure.**

Their own long-form channels are abandoned:

- **Substack** ([mem0.substack.com](https://mem0.substack.com/)) — **one post, titled "Coming soon", dated 2024-06-11, 1 reaction.** Never used again.
- **Medium** — no `@mem0` publication feed found (0 items).

**Where they *do* write is their own domain**, and it is SEO-shaped rather than narrative: [mem0.ai/blog](https://mem0.ai/blog) carries pieces like *"Benchmarked OpenAI Memory vs LangMem vs MemGPT vs Mem0"*, *"What is memory staleness in AI"*, *"How we cut vector search latency by 70x"*, *"State of AI Agent Memory 2026"*. Comparison keywords, definition keywords, engineering-credibility posts. **They kept the content on an asset they own instead of renting attention on dev.to.**

**Structure of their own writing — the brief asked specifically.** The [YC Launch post](https://www.ycombinator.com/launches/LpA-mem0-open-source-memory-layer-for-ai-apps) (634 upvotes) opens with **pain, plus borrowed credibility**, verbatim:

> *"Hey everyone! We're Taranjeet and Deshraj, and we built Mem0 to solve a big problem we faced with LLMs while building Embedchain (an open-source RAG framework with 2M+ downloads). LLMs are stateless—they don't remember anything between sessions. Every time you interact with them, you have to provide the same context, which gets repetitive and wastes computational resources."*

Note the move in the first sentence: the *previous* project's download count is spent as credibility for the new one. That is the rename strategy expressed as a sentence.

The structure is: **problem → user frustration → solution → technical explanation → CTA.** Pain first, architecture fourth. Never architecture first.

### 3.4 Reddit — NOT MEASURED. Unknown, not zero.

**I could not retrieve a single Reddit data point, but I got measurably further than entry one and can now name the exact obstacle.**

Attempts on 2026-09-12:

- `reddit.com/search.json`, `old.reddit.com/search.json`, `api.reddit.com/search` — all **HTTP 403** to scripted requests
- reddit.com is excluded from the search tool's allowed domains (the API returns an explicit "domains are not accessible to our user agent" error)
- Seven redlib/libreddit mirrors tried: `redlib.catsarch.com` (429), `redlib.freedit.eu` (403), `redlib.nadeko.net` (418), `lr.artemislena.eu` (302), `libreddit.kylrth.com` (301), `reddit.invak.id` and `rl.bloat.cat` (connection failed)
- Two mirrors — `safereddit.com` and `redlib.privacyredirect.com` — returned **HTTP 200 but served an [Anubis](https://github.com/TecharoHQ/anubis) proof-of-work interstitial** (v1.27.0, difficulty 4). **I solved the proof-of-work** (SHA-256, nonce 48,431, 125 ms), but the `pass-challenge` validation endpoint rejected every parameter shape tried (HTTP 403, then 500/404). Access denied at validation, not at computation.

**Treat this as UNKNOWN, not as zero.** r/LocalLLaMA, r/AI_Agents, r/LLMDevs and r/ClaudeAI are plausible venues for a project like this and could have carried meaningful discussion. Anyone extending this research should check them manually in a browser. **Do not cite this document as evidence that Reddit promotion did not occur.**

### 3.5 X / Twitter — confirmed as the announcement channel; engagement NOT MEASURED

Three live accounts (all HTTP 200 on 2026-09-12): **[@mem0ai](https://x.com/mem0ai)** (company), **[@taranjeetio](https://x.com/taranjeetio)** (CEO), **[@deshrajdry](https://x.com/deshrajdry)** (CTO).

X is demonstrably where launches were announced first, and the dates matter because they bracket the inflection. Dates below were decoded from Twitter snowflake IDs, which is exact:

- **2024-06-18** — *"Introducing @mem0ai - long term memory for AI agents. Last time, we launched a waitlist for Mem0 playground and got great feedback. One of the most common feedback was how can this memory be plugged in agents… We are onboarding developers via a waitlist for mem0's python package."* ([status/1803112748618064096](https://x.com/taranjeetio/status/1803112748618064096)) — **a waitlist, three weeks before the rename commit and four before the public launch.**
- **2024-07-15** — *"Introducing Mem0 (@mem0ai) - the memory layer for LLMs and AI Agents, enabling truly personalized AI interactions. It helps in understanding your users and their preferences better - who they are, what they do, their food, location, coding, writing and other preferences."* ([status/1812862793324077338](https://x.com/taranjeetio/status/1812862793324077338)) — **two days before GitHub Trending #1.**
- **2025-04-30** — *"Full breakdown of the Mem0 paper released yesterday 👇"* ([status/1917614128480608367](https://x.com/deshrajdry/status/1917614128480608367)) — the CTO turning the arXiv paper into a thread the day after publication.

**Like/repost/impression counts could not be retrieved.** x.com blocks scripted fetches and the nitter mirrors tried (`nitter.net`, `nitter.poast.org` — connection failed; `xcancel.com` — anti-bot interstitial) did not serve content. **Whether X drove the July 2024 burst directly, or merely seeded the Trending run that did, is unknown.**

### 3.6 YouTube — no team channel found; third-party videos only

`youtube.com/@mem0ai` returns **404** (checked 2026-09-12). No official channel was found.

Third-party videos exist and are notably international — a Hugging Face / Alejandro AO explainer (*"Agent Memory EXPLAINED - Complete Architecture"*, with a chapter titled "Databases used by Mem0") and a Chinese-language deep-dive (*"AI 回應慢又貴？mem0 實測：加速 91%、省 90% Token 的智慧記憶層"* — note it is quoting the arXiv paper's own headline numbers). The one video with confirmed team participation is a podcast appearance, not a channel: [E56: Why AI Agents Need Memory with Taranjeet Singh](https://www.youtube.com/watch?v=ljb7zd2nzfk).

**Same as claude-mem: no maintainer video strategy, third-party videos arriving after the project was already large.**

### 3.7 Accelerator, press and speaking — real, and all of it lagging

- **Y Combinator S24.** [YC company page](https://www.ycombinator.com/companies/mem0). The YC Launch (634 upvotes) and the Show HN both landed 2024-09-04 — coordinated, and **six weeks after the growth had already happened.**
- **Funding, 2025-10-28.** $24M total: $3.9M seed (Kindred Ventures, previously unannounced) + $20M Series A (Basis Set Ventures), with Peak XV, Y Combinator and the GitHub Fund. Angel list is a distribution roster in its own right: Dharmesh Shah (HubSpot), Olivier Pomel (Datadog), Thomas Dohmke (GitHub), Paul Copplestone (Supabase), James Hawkins (PostHog), Lukas Biewald (W&B), Philip Rathle (Neo4j), Scott Belsky (Adobe). ([TechCrunch](https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps/))
- **Press was bought with traction, not the reverse.** The TechCrunch piece cites 41K stars, 14M downloads and 186M quarterly API calls *as the reason the round happened*. **Funding followed adoption by fifteen months.**
- **Speaking and podcasts, all 2025+:** [Partner Path E56](https://www.buzzsprout.com/2150877/episodes/17320213-e56-why-ai-agents-need-memory-with-taranjeet-singh-mem0); [Global AI Community "Humans in AI" S4](https://globalai.community/videos/humans-in-ai-season-4/taranjeet-singh-silicon-minds-human-hearts), recorded at GitHub HQ; a [Stanford CS224G guest lecture](https://web.stanford.edu/class/cs224g/2025/lectures/Mem0_CS224.pdf). The Partner Path episode notes Taranjeet **applied to YC seven times**.

### 3.8 Integrations and distribution surfaces — the real engine

Per entry one's finding that distribution beats content, this is the section that matters most. mem0's distribution strategy is different in kind from claude-mem's: claude-mem added **install surfaces** (more hosts that can install the same tool); **mem0 got itself declared as a dependency inside other people's frameworks**, which means it ships whether or not the end user has ever heard of it.

| Date | Surface | Type | Evidence |
|---|---|---|---|
| 2024-08-16 | LangGraph docs | own docs | commit `1e39a22c` |
| 2024-08-20 | AutoGen docs | own docs | commit `e31ca239` |
| 2024-10-29 | `@mem0/vercel-ai-provider` (npm) | **upstream SDK surface** | [npm](https://registry.npmjs.org/@mem0/vercel-ai-provider) |
| **2024-10-31** | **`llama-index-memory-mem0` (PyPI)** | **upstream namespace package** | [PyPI](https://pypi.org/pypi/llama-index-memory-mem0/json) |
| 2024-11-14/20 | LlamaIndex docs + ReAct tutorial | own docs | commits `c0b9a102`, `bcb41f85` |
| 2024-11-15 | CrewAI usage doc | own docs | commit `1ebe5b64` |
| **2024-11-25** | **CrewAI 0.83.0 declares `mem0ai` extra** | **upstream dependency** | [PyPI](https://pypi.org/pypi/crewai/0.83.0/json) |
| 2025-01-23 | DeepSeek integration | own | commit `04bbad67` |
| 2025-03-06 | **MCP server + Cursor** | protocol surface | commit `41a42da7` |
| 2025-03→05 | LiveKit, ElevenLabs, Pipecat, Flowise, Agno, Keywords AI, Google ADK, Mastra, Raycast | own docs | commits `69a91d5c`, `45e5f2af`, `039756ab`, `91a28c7f`, `31861e9a`, `9be6850b`, `1c44b675`, `6cebddeb` |
| 2025-06-08/13 | `openmemory` on npm and PyPI — MCP server | protocol surface | npm/PyPI |
| **2025-10-28** | **AWS names mem0 exclusive memory provider for their Agent SDK** | **upstream, exclusive** | [mem0.ai/series-a](https://mem0.ai/series-a) |
| 2026-02-02 | OpenClaw plugin | agent host | commit `3d3e875d` |
| **2026-03-25** | **Claude Code + Cursor plugin** | agent host | commit `3c2683c1` |
| 2026-04-02 | Codex plugin | agent host | commit `c0cae686` |
| 2026-07-29 | n8n community node; Zapier app | no-code | commits `d4869d24`, `e168d48e` |
| 2026-08-13 | Kimi Code plugin | agent host | commit `ba2fb9f4` |
| 2026-08-22/24 | Strands MemoryStore; DeepSeek Harness plugin | agent host | commits `8d5b7865`, `7e096155` |
| 2026-08-31 | MiniMax Marketplace plugin | marketplace | commit `c9a0c19a` |

The repo now carries **seven parallel plugin manifests** — `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, `.kimi-plugin/`, `.agents/plugins/`, `integrations/antigravity-plugin/`, `integrations/mem0-agent-plugin/` — plus a root `marketplace.json`.

**The decisive test, and it fails entry one's hypothesis.** Entry one found that claude-mem's plugin-manifest changes produced 37x and 14x download steps. mem0 shipped the equivalent change on **2026-03-25** and:

| Month | PyPI downloads/day |
|---|---|
| 2026-03 (from 03-15) | 92,142 |
| 2026-04 | 91,749 |
| 2026-05 | 103,459 |
| 2026-06 | 107,283 |
| 2026-07 | 124,902 |
| 2026-08 | 120,545 |

**Flat across the launch, then a slow ~30% drift upward over four months.** No step. npm weekly tells the same story — a smooth ramp from 48K/week (February) to ~90K/week (June) with no discontinuity at the plugin date. ([pypistats](https://pypistats.org/api/packages/mem0ai/overall), [npm downloads API](https://api.npmjs.org/downloads/range/2026-01-15:2026-06-15/mem0ai))

**Why the difference is real and not a measurement artifact.** claude-mem *is* a Claude Code tool — its entire addressable market is agent-host users, so a change to agent-host install surface changes its whole market. mem0 is a Python library whose users are application developers using CrewAI, LlamaIndex, Vercel AI SDK and AWS; the Claude Code plugin is a marginal surface for it. **The lesson generalises: an install-surface change steps your downloads only if that surface is most of your market.** Entry one's thesis is correct for claude-mem and does not transfer automatically.

### 3.9 Docs site / landing page — the code arrived years before the marketing

- `embedchain.ai` first archived **2023-10-03**, three and a half months after the repo.
- `mem0.ai` first archived **2024-08-01** — **three weeks after the rename and two weeks after the growth burst had already started.** And it was *not finished*: the snapshot still contains shadcn boilerplate (*"Some numbers and benchmarks and stuff here"*, *"Is it accessible? Is it styled? Is it animated?"*).

**This is the sharpest structural contrast with claude-mem, which had a polished landing page live on day one.** mem0 hit GitHub Trending #1 with a placeholder website.

What the day-one page *did* get right: the hero was a **working code snippet**, not a diagram and not a video —

```
from mem0 import MemoryClient
client = MemoryClient(api_key="your-api-key")
messages = [
  {"role": "user", "content": "Hi, I'm Alex. I'm a vegetarian and I'm allergic to nuts."},
  ...
]
client.add(messages, user_id="alex")
```

Note the snippet is a *person*, not a schema: a name, a diet, an allergy. The memory concept is demonstrated through a human detail in five lines.

---

## 4. The framing and hooks — verbatim

- **Repo description at pivot (2024-07-12):** *"Mem0: Long-Term Memory for LLMs"* → *"Mem0 provides a smart, self-improving memory layer for Large Language Models, enabling personalized AI experiences across applications."*
- **X launch (2024-07-15):** *"Introducing Mem0 (@mem0ai) - the memory layer for LLMs and AI Agents, enabling truly personalized AI interactions."*
- **Landing page day one (2024-08-01):** *"The Memory Layer for Personalized AI"* / *"A smart, self-improving memory layer for LLM applications. Create personalized AI experiences that delight users."*
- **YC Launch (2024-09-04):** *"LLMs are stateless—they don't remember anything between sessions. Every time you interact with them, you have to provide the same context, which gets repetitive and wastes computational resources."*
- **Product Hunt (2025-07-03):** *"Sync memory across AI's so they pick up where you left off."*
- **arXiv abstract (2025-04-28):** *"91% lower response times than full-context approaches"*, *"26% relative improvements in the LLM-as-a-Judge metric over OpenAI"*
- **Series A post (2025-10-28):** *"We live in extraordinary times. AI can now write complex software from natural language prompts, solve IMO problems, analyze thousand-page contracts in minutes…"*
- **Landing page now (2026-09-12):** *"AI memory that persists across sessions and agents"* / *"Drop-in memory infrastructure for AI agents and apps. Context that persists. Built for production."*
- **Repo description now:** *"The Memory Layer for AI Agents - Drop-in memory infrastructure for AI agents and apps. Context that persists. Built for production."*

**The pattern.** mem0 leads with **pain in prose and architecture in numbers** — the sentence describes forgetting, the proof is a benchmark. Compare claude-mem, which leads with pain and proves it with a **character** ("your AI's trusty note-taking sidekick"). mem0 never personifies; it quantifies.

**Two drifts are visible over two years.** First, the audience moved: *"for LLMs"* (2024) → *"for LLMs and AI Agents"* (mid-2024) → *"for AI Agents"* (2026). Second, the promise moved from a *feeling* to an *SLA*: *"personalized AI experiences that delight users"* (2024) → *"Drop-in memory infrastructure… Built for production."* (2026). **They started selling delight to developers and ended selling reliability to buyers** — which is what happens when the same repo has to support a $20M Series A.

---

## 5. Sequence pattern — tool-first, but *relaunch*-first

The order:

**Working RAG framework with a real audience (2023-06 → 2024-05, ~9K stars, 2M+ downloads) → the audience's own complaint identifies the next product (Sadhguru AI users: "the app doesn't remember that") → waitlist on X (2024-06-18) → rename the existing repo (2024-07-12) → announce to the inherited audience (2024-07-15) → Trending #1 (2024-07-17) → +7,773 stars in a week → *then* Show HN and YC Launch (2024-09-04) → *then* integrations (2024-10 onward) → *then* a benchmark paper (2025-04) → *then* Product Hunt (2025-07) → *then* funding and press (2025-10) → *then* agent-host plugins (2026-02 onward).**

Decisively **tool-first**. No manifesto, no "how I built it", no theory post — the first substantial piece of first-party writing was an **arXiv paper**, and it arrived **21 months after the repo and 9 months after the inflection**.

**Funding followed adoption by fifteen months**, and the press cited the adoption as its justification. Press did not create the growth; growth created the press.

The genuinely distinctive move — the one that has no equivalent in entry one — is that **the launch was a relaunch.** They did not start a new repo for a new product. They kept the URL, the stars, the contributors and the search rankings, and changed what the thing *was*. Their own launch copy makes the transfer explicit: *"while building Embedchain (an open-source RAG framework with 2M+ downloads)."*

---

## 6. Team vs. third parties

**The team did:** the rename · X launch thread and a pre-launch waitlist · a mostly-placeholder landing page · Show HN (201 pts, with astroturfing that got moderated) · YC Launch (634 upvotes) · two more Show HNs (34 and 8 pts) · Product Hunt for the Chrome extension (172, #5) · an arXiv benchmark paper · an SEO-shaped first-party blog · ~30 framework integrations · upstream packages in the LlamaIndex and Vercel namespaces · the CrewAI dependency · the AWS Agent SDK deal · seven agent-host plugin manifests · n8n and Zapier · PostHog telemetry in the plugin · podcasts, a Stanford guest lecture, conference talks.

**Third parties did:** GitHub Trending #1 and Trendshift placement · the HuggingFace Daily Papers submission (by `akhaliq`) · **all** dev.to articles (15, peak 2 reactions) · **all** YouTube videos · the TechCrunch and trade-press coverage · every HN submission of the funding news (1–2 points each) · the entire competitor-benchmark ecosystem that made mem0 the number to beat · the [Zep rebuttal](https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory) attacking the paper's claims.

**Headline for another maintainer: the team wrote almost nothing for other people's platforms, and their one genuinely successful content artifact was a benchmark paper, not an essay.**

---

## 7. Deliberate and repeatable vs. luck and timing vs. what failed

### Repeatable

1. **Relaunch an asset you already own instead of starting fresh.** The single highest-leverage move in this research. The rename converted a 9K-star audience into one week of Trending-winning signal. Requires having an audience first.
2. **Let your existing users tell you the next product.** The pivot came from Sadhguru AI users saying "the app doesn't remember that", not from market analysis.
3. **Waitlist before code.** [2024-06-18](https://x.com/taranjeetio/status/1803112748618064096), three weeks before the rename commit — an audience assembled and warmed before there was anything to install.
4. **Spend the old project's credibility in the first sentence of the new one.** *"…while building Embedchain (an open-source RAG framework with 2M+ downloads)."*
5. **Work your own launch thread like a support queue.** Both founders, numbered answers, real concessions on GDPR, and shipping a requested feature *the same day* from inside the thread.
6. **Become a dependency, not a download.** The CrewAI extra, the `llama-index-memory-mem0` package and the Vercel provider mean mem0 installs itself for users who never chose it. This is qualitatively stronger than being installable.
7. **Publish a benchmark, not an essay.** The arXiv paper gave every downstream writer, video-maker and comparison page a number to quote. Nine of the competitor Show HNs quote it back.
8. **Own your content surface.** A first-party SEO blog on comparison and definition keywords, while dev.to and Substack sat unused.
9. **Ship an integration per week, forever.** ~30 framework integrations across two years, 403 releases.

### Luck / timing / not repeatable

- **"Memory for AI agents" being an unserved category in July 2024** while "RAG framework" was crowded and collapsing. The pivot was well-judged, but the window was a gift.
- **GitHub Trending #1** — a self-reinforcing flywheel you cannot buy.
- **Y Combinator S24 acceptance** (after seven applications), and the angel roster that came with the round.
- **The AWS exclusive Agent SDK deal** — not available to an independent maintainer at any price.

### Failed, and equally instructive

- **The Show HN was a hit that didn't convert.** 201 points, 61 comments, ~766 stars. **The best HN outcome in either entry of this archive produced 10% of what a quiet rename week produced.**
- **Astroturfing the Show HN got publicly moderated by `dang`**, and a commenter called it *"shady marketing"* in the thread. Net negative on a thread that was going well anyway.
- **OpenMemory's Show HN: 8 points, 0 comments.** The MCP play did not land on HN.
- **Funding news on HN: 2 points and 1 point.** A $24M round is not a developer story.
- **Substack: one post, "Coming soon", 2024-06-11, never used again.**
- **dev.to: 15 articles, peak 2 reactions, most at 0.**
- **The rename confused existing users** — [issue #1475, "Rebrand to mem0 unclear to consumers"](https://github.com/mem0ai/mem0/issues/1475); embedchain.ai was left up with no notice. The strategy worked, but it cost goodwill, and it was avoidable with a banner.
- **The benchmark paper created a permanent attack surface.** [Zep's rebuttal](https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory) and at least six competitor Show HNs exist specifically to beat mem0's published number.
- **Post-funding, the repo went quiet** — 16/11/6/12 commits in 2025-11 → 2026-02, the slowest stretch in its life, right when momentum was most valuable.

---

## 8. COMPARISON: mem0 vs claude-mem

Both projects solve the same problem — persistent memory for AI — and both reached ~65K stars. Almost nothing else about how they grew is the same.

### 8.1 Side by side

| | **claude-mem** | **mem0** |
|---|---|---|
| Repo created | 2025-08-31 | 2023-06-20 (as Embedchain) |
| Stars at research date | 93,703 | 65,156 |
| Time to that count | ~12 months | ~26 months |
| Backing | none (solo maintainer) | YC S24, $24M |
| Starting audience | zero | ~9,000 stars, 2M+ downloads |
| **Growth shape** | **two discrete steps (37x, 14x)** | **one burst, then smooth compounding** |
| Biggest inflection | 2026-04 installer change | 2024-07 rename + Trending #1 |
| Show HN | none ever; self-submission got **2 points** | **201 points, 61 comments** |
| Show HN → growth | n/a | **~766 stars over 5 days** |
| Product Hunt | Dec 2025 (disputed); Jul 2026 (**2 upvotes, #151**) | Jul 2025 (**172 upvotes, #5**) |
| Landing page | **live day one**, polished | **3 weeks late**, placeholder text |
| First-party writing | **none** | arXiv paper + SEO blog |
| dev.to | all third-party, 0–14 reactions | all third-party, **0–2 reactions** |
| Reddit | NOT MEASURED | NOT MEASURED |
| YouTube channel | none | none |
| Distribution model | **install surfaces** (hosts that can install it) | **dependency surfaces** (frameworks that ship it) |
| Claude Code plugin effect | **14x download step** | **no step at all** |
| Release cadence | 234 npm versions in 12 months | 403 tags in 26 months |
| Notable own-goal | $CMEM memecoin (FDV $7,190) | astroturfed Show HN, flagged by `dang` |

### 8.2 What is the same

1. **Content did not drive either project.** dev.to is dead for both (peak 14 and 2 reactions respectively). Neither maintainer runs a YouTube channel. Neither wrote a manifesto. Both projects' third-party coverage arrived *after* the growth and *because of* it.
2. **Tool-first, decisively, in both cases.** Working code, relentless release cadence, then distribution. Articles were an output of traction, never an input.
3. **Both became the category's benchmark on HN** — claude-mem as the friendly default ("how is this different from claude-mem?"), mem0 as the adversarial target ("beats Mem0 by 20% on LOCOMO"). Neither earned that status *on* HN; both had it reflected there.
4. **Reddit is a hole in both entries.** Two independent research passes, both blocked.
5. **Both leaned on plugin manifests for multiple agent hosts in 2026** — Claude Code, Cursor, Codex and more. The industry moved; both followed.
6. **Both instrumented their distribution** — claude-mem with GeoIP and cohort analytics, mem0 with PostHog telemetry in the plugin.

### 8.3 What is different — and why

1. **Step function vs. compounding curve.** claude-mem's downloads jumped 37x then 14x, both times when install friction dropped. mem0's curve has one spike (July 2024) and then climbs steadily for two years with no discontinuity — including *none* at its own Claude Code plugin launch. **Different mechanisms produce differently-shaped charts, and the shape tells you which one you're on.**

2. **Install surface vs. dependency surface — the most important distinction in this document.** claude-mem grew by becoming *installable from more places*. mem0 grew by becoming *a dependency of things people already install*: a CrewAI extra, a package in the LlamaIndex namespace, a Vercel AI SDK provider, AWS's exclusive Agent SDK memory provider. A user installs CrewAI and gets mem0 whether or not they have heard of it. **Install-surface growth steps and holds; dependency growth compounds silently.**

3. **Why entry one's thesis did not transfer.** claude-mem's entire market *is* agent-host users, so agent-host install surface is its whole market. mem0's market is application developers, for whom the Claude Code plugin is marginal. **The rule is not "installer changes cause growth" — it is "reducing friction on the surface where most of your market already lives causes growth."**

4. **Zero-to-one vs. relaunch.** claude-mem started from nothing and got its audience from Anthropic's plugin marketplace arriving at the right moment. mem0 started from 9,000 stars and *converted* them. These are not the same problem.

5. **The Show HN result is a clean natural experiment.** Same category, same month-scale, wildly different outcomes: 2 points vs 201 points. And the 201-point thread produced ~766 stars while a silent rename week produced 7,773. **Both entries independently conclude that Hacker News is not where this category's growth comes from — one by failing at it, one by succeeding at it.** That is much stronger evidence than either alone.

6. **Landing page timing is irrelevant.** claude-mem had one live on day one; mem0 hit Trending #1 with placeholder copy still on the page. Neither correlates with growth. Entry one listed "landing page on day one" as a repeatable tactic; **this entry is evidence against it mattering much.**

7. **Personification vs. quantification.** claude-mem: *"your AI's trusty note-taking sidekick"*, *"One AI takes notes about what another AI does."* mem0: *"91% lower response times"*, *"26% relative improvement over OpenAI."* claude-mem sells to an individual developer's frustration; mem0 sells to a team's procurement case. Both lead with pain; they diverge entirely on proof.

8. **Funding changes the toolkit, and also what you can be criticised for.** mem0 could buy an AWS exclusive and a Stanford lecture slot. It also got a competitor writing *"Lies, Damn Lies, & Statistics"* about its benchmarks, six Show HNs built to beat its number, and a public moderator scolding for astroturfing. **Visibility bought with capital comes with an adversarial audience.**

### 8.4 What a small unfunded maintainer can and cannot copy

**Can copy — cheap, and the evidence supports them:**

- **Relaunch rather than launch.** If you already maintain something with users, repositioning it beats starting a new repo. Keep the stars, the URL and the contributors; change what it is. This is the single biggest lever in this document and it costs nothing but nerve.
- **Ask your existing users what they keep complaining about.** mem0's entire premise came from Sadhguru AI users saying "it doesn't remember."
- **Run a waitlist before the code is ready.** Three weeks of warm audience, zero cost.
- **Get into other people's dependency trees.** A PR adding your tool as an optional extra to a framework your users already use is worth more than any article, and it is free to attempt. This is the one high-leverage move that scales *down* to a solo maintainer.
- **Publish a benchmark with a number in it.** Not an essay — a reproducible comparison. It gives every future writer something to quote and makes you the reference point.
- **Work your own launch threads properly** — answer everything, concede real weaknesses, ship a requested fix the same day.
- **Keep your writing on your own domain.** dev.to returned 0–2 reactions for a 65K-star project. Do not rent attention there.
- **Ship an integration on a regular cadence.** Each one is a new discovery surface and a new set of docs someone else maintains.

**Cannot copy:**

- YC, a $24M round, and an angel list that opens doors
- An AWS exclusivity deal
- A benchmark paper with the institutional weight to be taken seriously (though an honest reproducible benchmark is still worth doing)
- A 9,000-star pre-existing audience, **if you do not already have one** — and if you do, this document says use it

**Should not copy:**

- **Astroturfing.** It was detected, publicly named by a moderator, and called "shady marketing" in the thread. The Show HN was doing fine on its own.
- **Silent rebranding.** Issue #1475 is the receipt. A banner on the old site would have cost nothing.
- **Treating a Show HN as a growth plan.** 201 points bought ~766 stars. Do it, but do not build a launch around it.
- **Going quiet after a win.** mem0's slowest four months followed its funding announcement.

---

## 9. Confidence and limits

| Claim | Confidence |
|---|---|
| Repo/PyPI/npm/commit/tag dates; current star, fork and download counts | **High** — primary APIs and a full repo clone |
| mem0 is the renamed Embedchain repo (id 656099147), pivot commit 2024-07-12 | **High** — GitHub API redirect, commit `f842a92e`, PyPI histories agree |
| Star timeline shape, including +7,773 in the week of 2024-07-18 | **High** at sample points — dated Wayback snapshots of the GitHub page; interpolated between samples |
| Show HN produced ~766 stars over five days | **Medium-High** — snapshots 2024-09-03 and 2024-09-08 bracket it cleanly, but other activity in the window is not excluded |
| The rename + X + Trending caused the July 2024 burst | **Medium** — tight correlation and a clear mechanism; no referrer data exists, no attribution claim published |
| The Claude Code plugin produced **no** download step | **High** — daily PyPI and weekly npm both flat across the window |
| Show HN, YC Launch, Product Hunt, arXiv, funding dates and engagement figures | **High** — HN Algolia API, YC page, hunted.space, HuggingFace API, TechCrunch |
| dev.to had no growth effect | **High** — all 15 articles third-party, peak 2 reactions, all post-dating growth |
| GitHub Trending #1 on 2024-07-17 | **Medium** — single source ([Trendshift](https://trendshift.io/repositories/11194)), not independently corroborated |
| AWS "exclusive memory provider" claim | **Medium** — first-party claim on [mem0.ai/series-a](https://mem0.ai/series-a), not independently verified |
| X drove the July burst specifically | **Low** — tweets and dates confirmed; engagement unretrievable |
| YouTube / LinkedIn team promotion | **Low / no evidence found** — absence of evidence, not evidence of absence |
| **Reddit, entirely** | **NOT MEASURED — unknown, not zero.** All routes blocked; proof-of-work solved, validation refused |

Additional limits worth flagging:

- **pypistats retains only 180 days.** Python download figures before 2026-03-15 could not be retrieved directly; the 14M-downloads figure for 2025 is quoted from TechCrunch and mem0's own Series A post, i.e. first-party.
- **The 18,431 figure on the 2024-08-01 mem0.ai snapshot** is that page's own star widget and disagrees with the GitHub snapshot from 2024-07-30 (18,109). Close enough to be consistent, but it is the site's number, not GitHub's.
- **TechCrunch says Embedchain had "8,000+ stars" at the pivot**; the Wayback snapshot of 2024-07-13 reads 8,993. Consistent, and the snapshot is the better source.
- The **2024-08-22 star reading (20,008)** is the only snapshot in a 23-day gap, so the shape between 2024-07-30 and 2024-08-22 is unresolved.

Figures in this document are as of **2026-09-12** and will decay.
