# mem0 — Origins and Development History

**Researched:** 2026-09-12
**Subject:** https://github.com/mem0ai/mem0 (PyPI: `mem0ai` · npm: `mem0ai` · company: https://mem0.ai)
**Researcher:** lore-advocate market-research sweep, second entry in this archive (entry one: `claude-mem-origins.md`)
**Method:** GitHub REST API (unauthenticated `curl`; the local `gh` token is invalid, and the 60 req/hr unauthenticated ceiling was hit once and worked around), GitHub `.atom` release/tag feeds (not rate-limited), `raw.githubusercontent.com` for historical READMEs at specific commit SHAs, PyPI JSON API, pypistats.org API, `api.npmjs.org` downloads API, and web search/fetch of company-owned pages, the YC directory, and press coverage. Primary sources are distinguished from secondary throughout. Figures that decay are date-stamped in place.

## Summary — the three most decision-relevant findings

**First, mem0 is a pivot, and the pivot is the whole story.** The repo's 2023-06-20 creation date is real but belongs to a *different project*: `embedchain`, "the simplest open source retrieval (RAG) framework." The first commit is literally `Hello World` by Taranjeet Singh, and the first README is the single line `# embedchain`. The rename happened in one commit — `f842a92e25e4`, 2024-07-12, *"Rename embedchain to mem0 and open sourcing code for long term memory (#1474)"* — and both the `embedchain/` and (later) `openmemory/` directories have since been deleted from `main`. Anyone citing "founded 2023, 65K stars" is crediting mem0 with thirteen months of stars earned by a RAG framework. **Second, this is a funded company, not a solo project: $24M across a $3.9M seed (led by Kindred Ventures) and a $20M Series A (led by Basis Set Ventures), announced 2025-10-28, with Y Combinator (S24), Peak XV, the GitHub Fund, and a bench of infrastructure-CEO angels** — Datadog, Supabase, PostHog, Weights & Biases, ex-GitHub, Neo4j, Plaid. The open-source repo is the top of a funnel for a hosted platform with published tiers from free to $249/month to custom enterprise, and the README states the open-core boundary in a table ("Advanced Features: Self-Hosted = *Teasers*"). **Third, and most directly threatening to any Claude-Code-adjacent memory project: during 2026 mem0 moved into the coding-agent territory.** Between March and June 2026 it shipped an official CLI (`npm i -g @mem0/cli`), six agent skills installable via `npx skills add`, plugins for OpenClaw / OpenCode / DeepSeek / Pi Agent, and an "AI agents can mint an API key in under five seconds — no email, no dashboard, no OTP" self-signup flow. Its usage curve is real and still climbing: **3.74M PyPI downloads in 2026-08 and 472,300 npm downloads in 2026-08**, roughly 57 PyPI downloads per GitHub star per month against claude-mem's 0.84 npm downloads per star per month.

---

## EXPLICITLY NOT VERIFIED

**This section exists so these do not harden into facts on re-reading. Do not cite anything below as established.**

1. **Star-growth curve over time.** The GitHub `stargazers` endpoint requires authentication for `starred_at` timestamps and the local token is invalid. I have exactly three dated star readings (see §6) — 41,000+ (2025-10-28, company's own press release), 62,590 (2026-09-12, stale figure in mem0.ai's own site nav), 65,156 (2026-09-12, API). **I do not know when stars inflected, or how many of the 65,156 were earned as `embedchain` before 2024-07-12.** That last question is the single most important unanswered one in this report.
2. **PyPI download history before 2026-03.** pypistats.org serves only a rolling 180-day window and rate-limited me after two calls. The 14M-downloads figure for the Series A is the company's own claim, not my measurement. I have no verified monthly PyPI curve for 2024 or 2025.
3. **The anomalous `embedchain` PyPI download figures.** The abandoned package (last release 0.1.128, 2025-03-25) still recorded 387,037 downloads in 2026-08 and over 1M/month in April–May 2026. I have **no explanation** for this — it could be CI, mirrors, or a transitive dependency. Do not treat it as live adoption, and do not treat my dismissal of it as established either.
4. **Exact seed round date.** TechCrunch describes the $3.9M seed as "previously unannounced"; no date was given anywhere I looked. The 2025-10-28 date belongs to the *announcement* of both rounds, not to the seed's closing.
5. **Revenue, ARR, paying-customer count, or net retention.** Not disclosed anywhere. "Thousands of teams… Fortune 500 companies" is company marketing copy with no named logos attached.
6. **Whether the AWS "exclusive memory provider for the Strands Agents SDK" arrangement is contractual, exclusive in any binding sense, or still current.** The word "exclusive" comes from mem0's own press release. I found an AWS Database Blog post co-featuring mem0, which corroborates a real working relationship but not the exclusivity claim.
7. *(Resolved during research — kept for the record.)* I initially could not confirm Taranjeet Singh's GitHub account because I guessed the handle `taranjeetio` from his X handle; that account **404s**. The correct handle is **`taranjeet`**, verified from the rendered profile page. See §2. **Lesson for future entries: do not infer a GitHub handle from an X handle.**
8. **The verbatim text of Taranjeet's rename announcement post** (https://x.com/taranjeetio/status/1811789999257587785, dated 2024-07-12 by the search index). X returned HTTP 402 to WebFetch. I have only the search-engine snippet, quoted as such in §7.
9. *(Resolved during research — kept for the record.)* The contributor **distribution** was initially blocked by the exhausted API limit. I recovered it from GitHub's un-rate-limited `graphs/contributors-data` endpoint (see §6). Caveat that remains: **that endpoint returns only the top 100 contributors**, covering 2,538 of 2,626 commits; the remaining ~88 commits across ~295 contributors are not itemized.
10. **First GitHub Release date and the release-tag history before 2026-08.** The `.atom` feeds serve only the most recent 10 entries and the API budget was spent. I verified 399 releases / 403 tags by pagination header, and the release scheme (see §5), but not the first release's date.
11. **Whether `openmemory/` was deleted or merely relocated.** `openmemory/README.md` 404s on `main` as of 2026-09-12 and a 2026-03-24 commit removed its references from docs, but https://mem0.ai/openmemory still resolves. I did not establish what happened.
12. **Benchmark numbers.** Every LoCoMo / LongMemEval / BEAM score in §8 is mem0's own self-reported figure, including the competitor comparisons it publishes. None were independently reproduced. mem0 itself footnotes that platform scores "include proprietary optimizations not available in the open-source SDK."

---

## 1. Canonical properties — all VERIFIED to exist

| Property | URL | Verified |
|---|---|---|
| Repository | https://github.com/mem0ai/mem0 | GitHub API, repo id `656099147` |
| Organization | https://github.com/mem0ai | API: org, created 2023-06-19T09:32:13Z |
| Company site | https://mem0.ai | HTTP 200 |
| Docs | https://docs.mem0.ai | HTTP 200 |
| Hosted app | https://app.mem0.ai | HTTP 200 |
| Research page | https://mem0.ai/research | HTTP 200 |
| PyPI (current) | https://pypi.org/project/mem0ai/ | HTTP 200, 189 versions |
| PyPI (CLI) | https://pypi.org/project/mem0-cli/ | HTTP 200 |
| PyPI (legacy) | https://pypi.org/project/embedchain/ | exists, 248 versions, abandoned |
| npm (current) | `mem0ai` | registry API: 126 versions |
| npm (CLI) | `@mem0/cli` | referenced in README; npmjs.com returns 403 to automated fetch (bot block), registry not separately confirmed |
| Benchmarks repo | https://github.com/mem0ai/memory-benchmarks | HTTP 200 |
| arXiv paper | https://arxiv.org/abs/2504.19413 | see §8 |

Note: `https://www.npmjs.com/package/mem0ai` returns **403** to automated fetch — this is Cloudflare bot-blocking of the *website*, not a missing package. The registry API at `https://registry.npmjs.org/mem0ai` returns full metadata.

**Repository description as of 2026-09-12:**

> The Memory Layer for AI Agents - Drop-in memory infrastructure for AI agents and apps. Context that persists. Built for production.

**Organization description as of 2026-09-12:** "The Universal Memory Layer for AI Agents". Org contact email: `founders@mem0.ai`. Org X handle: `@mem0ai`. Location: United States of America. 10 public repos, 1,194 followers.

**Repo topics (14, as of 2026-09-12):** `agentic-memory`, `agentic-memory-system`, `agents`, `ai`, `ai-agents`, `chatgpt`, `genai`, `llm`, `long-term-memory`, `memory`, `memory-management`, `python`, `rag`, `state-management`.

Worth noting against entry one: these are all **category** terms. No competitor names appear in mem0's topic tags, in contrast to claude-mem's topic list which included `mem0`, `openmemory`, and `supermemory`.

**License:** Apache-2.0. A 2025-09-30 commit, `445286a138cb`, is titled *"fix: update license information in README and pyproject.toml (#3522)"* — a license-metadata correction whose before/after state I did not establish.

---

## 2. Who created it

### Taranjeet Singh — Co-founder & CEO

Verified from the rendered GitHub profile (primary):

- Handle: **@taranjeet** — https://github.com/taranjeet (**note:** `github.com/taranjeetio` 404s — his X handle and his GitHub handle differ)
- Name: `Taranjeet Singh`
- Bio, verbatim: `Building @mem0ai`
- Works for: `@mem0ai` · Location: `San Francisco`
- Personal site: https://taranjeet.co/about
- X: `@taranjeetio` · LinkedIn: `in/taranjeet7114`
- 929 followers (as of 2026-09-12)

Further:

- Author of the first commit (`2b82ff695fd1`, 2023-06-20T08:59:41Z, message `Hello World`), committing as `Taranjeet Singh`.
- Listed as the author on the original PyPI `embedchain` package: `Taranjeet Singh taranjeet@embedchain.ai` (PyPI JSON API — primary).
- 4th-largest contributor to the repo by commit count (195 commits — see §6).
- YC directory entry (https://www.ycombinator.com/companies/mem0) gives his title as Founder/CEO and this bio: joined **Khatabook** (YC S18) as first growth engineer, moving to Senior PM; began his career at **Paytm**; built an AI tutoring app featured at **Google I/O**; co-created **EvalAI**; and launched "the first GPT app store," scaling it past 1M users.
- Forbes Technology Council profile exists: https://councils.forbes.com/profile/Taranjeet-Singh-Co-founder-CEO-Mem0/426fb5ad-7d97-43a5-a0ad-3797c6a75c33 (secondary).

### Deshraj Yadav — Co-founder & CTO

Fully verified from the GitHub API (primary), user id `2945708`, account created **2012-12-02T18:24:25Z**:

- Handle: **@deshraj** — https://github.com/deshraj
- Name: `Deshraj Yadav`
- Company: `@mem0ai`
- Location: `San Francisco`
- Blog: `deshraj.xyz`
- X: `@deshrajdry`
- 129 public repos, 1,255 followers (as of 2026-09-12)
- **Bio, verbatim:** `CTO @mem0ai | ex-Tesla Autopilot | ex-Snap | Co-founder @caliperai | Creator eval.ai`

The YC bio adds: led the AI Platform at **Tesla Autopilot** (large-scale training, model evaluation, observability for full self-driving); created **EvalAI** as his Georgia Tech master's thesis; published at **CVPR, ECCV, and AAAI**.

### The contrast with entry one is stark and is the point

claude-mem's creator had, aside from claude-mem, no repo above 44 stars. mem0's two founders have: a prior open-source project with real traction (EvalAI), AI-infrastructure leadership at Tesla, a prior YC company in their background (Khatabook, as an employee), and a published arXiv paper with their names on it. **This is a credentialed founding team, and the funding outcome follows from that rather than from the star count.**

---

## 3. Origin story — it began as embedchain, a RAG framework

**This is the highest-value section of the report.** The GitHub repo creation date of 2023-06-20 is accurate and misleading at the same time.

### The timeline of the pivot

| Date | Event | Source |
|---|---|---|
| **2023-06-19T09:32:13Z** | GitHub org created (now `mem0ai`; originally the `embedchain` org — github.com/embedchain/embedchain still 301-redirects to github.com/mem0ai/mem0) | GitHub API `orgs/mem0ai` |
| **2023-06-19T09:50:07Z** | PyPI `embedchain` **0.0.1** published — *one day before the repo's first commit* | PyPI JSON API |
| **2023-06-20T08:58:36Z** | GitHub repo created | GitHub API `created_at` |
| **2023-06-20T08:59:41Z** | First commit `2b82ff695fd1`, message **`Hello World`**, author Taranjeet Singh | GitHub API |
| 2023-06-20T09:02:08Z | `Add gitignore` | GitHub API |
| 2023-06-20T09:12:52Z | `Add simple app functionality` | GitHub API |
| 2023-06-20T11:09:08Z | `Merge pull request #1 from embedchain/add-simple-app` | GitHub API |
| **2024-05-18T18:50:22Z** | PyPI **`mem0ai` 0.0.1** published — the new package appears ~8 weeks *before* the repo rename | PyPI JSON API |
| **2024-07-12T14:51:33Z** | Commit **`f842a92e25e4`**: *"Rename embedchain to mem0 and open sourcing code for long term memory (#1474)"* | GitHub API, README commit log |
| 2024-07-22T22:46:04Z | npm `mem0ai` **1.0.0** first publish | npm registry `time` |
| 2024 (Summer) | **Y Combinator S24 batch** | https://www.ycombinator.com/companies/mem0 |
| 2025-03-25 | PyPI `embedchain` **0.1.128** — the final embedchain release | PyPI JSON API |
| by 2026-09-12 | `embedchain/` directory **404s** on `main` | raw.githubusercontent.com |

### Why they pivoted — the founders' own account (secondary, but consistently reported)

Per TechCrunch's 2025-10-28 piece and echoed in other coverage: while running embedchain, the founders launched a **meditation app inspired by Sadhguru**. It gained traction in India, but — quoting TechCrunch's rendering of the founders' account — *"users kept sharing the same feedback: 'Hey, I'm on this meditative journey, but the app doesn't remember that.'"* That feedback drove the pivot to memory. TechCrunch also quotes the founders on the strategic logic: memory is *"becoming one of their key moats now that LLMs are getting commoditized."*

Source: https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps

### The unanswered question

embedchain was a genuinely popular RAG framework — the founders describe it as having had "2M+ downloads" before the rename, and its PyPI record shows 248 published versions. **A substantial but unquantified share of mem0's 65,156 stars were earned by a project that no longer exists in the repo.** I could not determine the split (NOT VERIFIED #1). Treat any "mem0 has 65K stars" claim as measuring the *repo*, not the product.

---

## 4. Git history at a glance

All figures as of 2026-09-12, from GitHub API pagination `Link` headers.

| Metric | Value | How measured |
|---|---|---|
| First commit | 2023-06-20T08:59:41Z (`2b82ff695fd1`) | `commits?per_page=1&page=2626` (oldest) |
| Commits on `main` | **2,626** | `commits?per_page=1` Link `rel="last"` |
| Commits touching `README.md` | **167** | `commits?path=README.md&per_page=1` Link |
| Contributors | **395** | `contributors?per_page=1` Link |
| Releases | **399** | `releases?per_page=1` Link |
| Tags | **403** | `tags?per_page=1` Link |
| Last push | 2026-09-11T15:36:33Z | API `pushed_at` |
| Repo size | 64,771 KB | API `size` |

Unlike claude-mem, mem0's git history is **continuous from the first commit** — no squash, no history restart, no version-number discontinuity. The full embedchain era is inspectable at `raw.githubusercontent.com` by SHA (I fetched READMEs from 2023-06-20 onward successfully).

---

## 5. Release model and cadence

mem0 does **not** ship one unified version. It is a monorepo with **per-package tags**, which is why the "399 releases" figure is not comparable to a single-package project's. Sample from the `.atom` feed (https://github.com/mem0ai/mem0/releases.atom), the ten most recent as of 2026-09-12:

```
2026-09-10T15:31:52Z  handoff-runtime-59939c003f6b3eb8add709e5897f7bfbe3e9f4d8
2026-09-09T14:40:27Z  Mem0 Pi Agent Plugin (v0.3.0)
2026-09-09T14:38:44Z  Mem0 OpenCode Plugin (v0.3.0)
2026-09-09T14:36:49Z  Mem0 DeepSeek Plugin (v0.3.0)
2026-09-09T14:34:30Z  Mem0 OpenClaw Plugin (v1.1.0)
2026-09-02T13:19:10Z  Mem0 Node SDK (v3.1.8)
2026-09-02T13:18:18Z  Mem0 Python SDK (v2.0.20)
2026-08-27T08:22:06Z  Mem0 DeepSeek Plugin (v0.1.1)
2026-08-27T08:20:51Z  Mem0 Strands Integration (v0.1.1)
2026-08-24T13:22:24Z  Vercel AI SDK Provider (v3.0.2)
```

**Note the composition of that list: four of the ten most recent releases are coding-agent plugins** (Pi Agent, OpenCode, DeepSeek, OpenClaw), all four shipped within six minutes of each other on 2026-09-09. See §9.

### Current versions (2026-09-12)

| Package | Version | Released |
|---|---|---|
| PyPI `mem0ai` | **2.0.20** | 2026-09-02T13:19:29Z |
| npm `mem0ai` | **3.1.8** (`latest`); `3.0.0-beta.2` (`beta`) | 2026-09-02T13:20:22Z |
| PyPI `embedchain` | 0.1.128 (abandoned) | 2025-03-25T07:49:00Z |

The Python and Node SDKs carry **different major versions** for the same product (2.x vs 3.x) — a versioning inconsistency worth knowing if you write docs that reference "mem0 v2".

### Version arc

| Milestone | Date | Source |
|---|---|---|
| `embedchain` 0.0.1 on PyPI | 2023-06-19 | PyPI |
| `mem0ai` 0.0.1 on PyPI | 2024-05-18 | PyPI |
| npm `mem0ai` 1.0.0 | 2024-07-22 | npm registry |
| **mem0ai v1.0.0** ("API modernization, improved vector store support, enhanced GCP integration") | 2025-10-16 | README commit `394203d1b5f5` |
| v3 pipeline ported to OSS (hybrid search, entity extraction, additive scoring) | 2026-04-14 | README commit `a488e19044e4` |
| `mem0ai` 2.0.20 / npm 3.1.8 | 2026-09-02 | PyPI + npm |

PyPI `mem0ai` release cadence in 2026 is roughly weekly-to-fortnightly (2.0.13 on 07-22, 2.0.14 on 07-25, 2.0.15 on 08-01, 2.0.16 on 08-04, 2.0.17 on 08-05, 2.0.18 on 08-11, 2.0.19 on 08-24, 2.0.20 on 09-02). This is **disciplined** cadence — not the eleven-releases-in-one-day pattern documented in entry one.

---

## 6. Adoption — measured figures

### GitHub (2026-09-12, GitHub REST API)

| Metric | Value |
|---|---|
| Stars | **65,156** |
| Forks | **7,627** |
| Watchers (`subscribers_count`) | **248** |
| Open issues + PRs (`open_issues_count`) | **738** |
| Contributors | **395** |
| Commits | **2,626** |

The team-lead brief cited 65,153 as of 2026-09-12; my API read minutes later returned **65,156**. The discrepancy is three stars of drift, not an error.

### Contributor concentration — the sharpest contrast with entry one

Recovered from GitHub's `graphs/contributors-data` endpoint (which, usefully, is **not** subject to the 60/hr REST API limit). Top 100 contributors, covering **2,538 of 2,626 commits**, as of 2026-09-12:

| Contributor | Commits | Share of covered commits |
|---|---|---|
| `Dev-Khant` | 460 | 18.1% |
| `kartik-mem0` | 323 | 12.7% |
| **`deshraj`** (co-founder/CTO) | 248 | 9.8% |
| **`taranjeet`** (co-founder/CEO) | 195 | 7.7% |
| `whysosaket` | 184 | 7.2% |
| `cachho` | 106 | 4.2% |
| `deven298` | 92 | 3.6% |
| **`claude`** | 89 | 3.5% |
| `sidmohanty11` | 78 | 3.1% |
| `prateekchhikara` | 73 | 2.9% |
| `parshvadaftari` | 64 | 2.5% |
| `HrushiYadav` | 41 | 1.6% |
| `utkarsh240799` | 39 | 1.5% |
| `parthshr370` | 32 | 1.3% |
| `Itz-Antaripa` | 25 | 1.0% |

**Concentration:** top contributor **18.1%**, top 3 **40.6%**, top 10 **72.8%**.

Compare entry one: claude-mem's single author held **~82%** of all commits, and three of its top ten "contributors" were bots. mem0's top *human* contributor holds 18.1%, **neither founder is the top committer**, and no single person dominates. This is a staffed engineering team plus a genuine outside tail — consistent with a funded 10-person company rather than a solo project with drive-by PRs.

Two details worth noting: `prateekchhikara` (73 commits) is the **first author of the arXiv paper** — the research is done by someone who also ships code. And **`claude` appears as the 8th-largest contributor with 89 commits (3.5%)** — mem0 is merging a meaningful volume of Claude-authored commits into its own repo.

### A correction to an inference in entry one

Entry one flagged claude-mem's watchers/stars ratio of **0.32%** as unusually low against three large comparables (vscode 1.83%, ollama 0.56%, langchain 0.63%). mem0's ratio, measured the same way on the same day:

| Repo | Stars | Watchers | Watchers/stars | Forks/stars |
|---|---|---|---|---|
| **mem0ai/mem0** | 65,156 | 248 | **0.38%** | 11.70% |
| thedotmack/claude-mem | 93,703 | 300 | 0.32% | 8.80% |

**mem0 — YC-backed, $24M-funded, with a download curve two orders of magnitude above claude-mem's — has essentially the same watcher ratio.** That materially weakens the "low watcher ratio suggests inorganic stars" inference in entry one. The likelier explanation is a generational shift in how GitHub users use the Watch button. **Do not re-use the watcher-ratio heuristic without this caveat.**

### PyPI downloads — `mem0ai` (pypistats.org API, `without_mirrors`)

pypistats serves only a rolling 180-day window, so this begins at 2026-03:

| Month | Downloads |
|---|---|
| 2026-03 | 1,566,429 |
| 2026-04 | 2,752,475 |
| 2026-05 | 3,207,241 |
| 2026-06 | 3,218,505 |
| 2026-07 | **3,871,969** |
| 2026-08 | 3,736,911 |
| 2026-09 (partial, through ~09-11) | 793,544 |

**2.4x growth across the six months I can see, with a plateau forming at roughly 3.7–3.9M/month since July 2026.** Source: https://pypistats.org/api/packages/mem0ai/overall

### npm downloads — `mem0ai` (api.npmjs.org, full history since first publish)

This one I have complete, and it is the most informative series in the report:

| Month | Downloads | | Month | Downloads |
|---|---|---|---|---|
| 2024-07 | 173 | | 2025-10 | 104,545 |
| 2024-08 | 517 | | 2025-11 | 109,997 |
| 2024-09 | 853 | | 2025-12 | 146,280 |
| 2024-10 | 1,357 | | 2026-01 | 163,647 |
| 2024-11 | 1,801 | | 2026-02 | 201,020 |
| 2024-12 | 1,924 | | 2026-03 | **316,426** |
| 2025-01 | 3,302 | | 2026-04 | 369,684 |
| 2025-02 | 3,400 | | 2026-05 | 431,550 |
| 2025-03 | 8,275 | | 2026-06 | 394,917 |
| **2025-04** | **28,244** | | 2026-07 | 396,515 |
| 2025-05 | 50,511 | | 2026-08 | **472,300** |
| 2025-06 | 73,029 | | 2026-09 (partial) | 137,112 |
| 2025-07 | 88,321 | | | |
| 2025-08 | 109,364 | | | |
| 2025-09 | 110,057 | | | |

**Inflection points, with dates:**

- **2025-03 → 2025-04: 8,275 → 28,244 (3.4x in one month).** This is the sharpest single-month step in the series and it coincides with the arXiv paper period (2504.19413, April 2025). The correlation is suggestive; I have **not** established causation.
- **2025-08 through 2025-11: a genuine four-month plateau** at ~104–110K/month. Note this plateau covers the period *including* the Series A announcement (2025-10-28) — the funding did not produce an immediate usage step.
- **2025-12 → 2026-05: resumed climb, 146,280 → 431,550 (~3x in six months).** This is the coding-agent / CLI / skills period (see §9).
- **2026-06/07: a shallow dip** (394,917 / 396,515), then **2026-08 at 472,300 — a new all-time high.**

The curve has two plateaus and has broken out of both. **As of 2026-09-12 mem0 is still growing on both package registries.** This is the crisp contrast with entry one, where npm stepped 14x once in April 2026 and then went flat-to-declining for five months.

### Usage intensity per star — the cross-entry comparison

| Project | Stars (2026-09-12) | Monthly downloads (2026-08) | Downloads per star |
|---|---|---|---|
| mem0 (PyPI `mem0ai`) | 65,156 | 3,736,911 | **57.4** |
| mem0 (npm `mem0ai`) | 65,156 | 472,300 | 7.25 |
| claude-mem (npm) | 93,703 | 79,060 | 0.84 |

mem0 has **30% fewer stars than claude-mem and roughly 47x more real package usage on PyPI alone.** If you are choosing which project to treat as the real competitor, this table is the answer.

### The `embedchain` anomaly — flagged, unexplained

The abandoned predecessor package is still recording large numbers (pypistats, `without_mirrors`):

| Month | `embedchain` downloads |
|---|---|
| 2026-03 | 379,058 |
| 2026-04 | 1,044,511 |
| 2026-05 | 1,061,981 |
| 2026-06 | 650,751 |
| 2026-07 | 522,919 |
| 2026-08 | 387,037 |

Its last release was **2025-03-25**. A package with no releases in eighteen months should not pull 387K downloads/month. See NOT VERIFIED #3 — I have no explanation and am recording it rather than smoothing it away.

### Company-reported metrics — clearly marked as company claims

From the Series A press release (https://mem0.ai/series-a and https://www.prnewswire.com/news-releases/mem0-raises-24m-series-a-to-build-memory-layer-for-ai-agents-302597157.html), **as of 2025-10-28**:

- "41,000 GitHub stars and 14 million Python package downloads"
- API calls grew **"from 35 million in Q1 to 186 million in Q3"** (2025) — roughly 30% month-over-month per TechCrunch
- "**80,000+ developers**" signed up for the cloud service (TechCrunch)
- "Thousands of teams, from the fastest-growing startups to Fortune 500 companies" (no names given)
- Team size at Series A: **four people** (TechCrunch); the YC directory listed **10** as of 2026-09-12

The **41,000 → 65,156 star path from 2025-10-28 to 2026-09-12 (+59% in ~10.5 months)** is the only star-growth measurement I can defend, and it rests on the company's own press release for the starting point.

A third reading worth recording as a curiosity: mem0's own site nav displayed **62,590 stars** on 2026-09-12, while the API returned 65,156 the same day — the company's website is running a stale cached count.

---

## 7. Positioning over time — remarkably stable after one hard pivot

167 commits touched `README.md`. Historical versions fetched from `raw.githubusercontent.com` at specific SHAs.

### Phase 1 — 2023-06-20, commit `2b82ff695fd1` (first commit)

The entire README:

```
# embedchain
```

### Phase 2 — 2023-06-20, commit `b6304550de35` (same day, hours later)

> embedchain is a framework to easily create LLM powered bots over any dataset.
>
> It abstracts the enitre process of loading dataset, chunking it, creating embeddings and then storing in vector database.

[typo `enitre` in the original]. The worked example is a **"Naval Ravikant bot"** built from a YouTube video, a PDF of the Almanack, and two blog posts. Pure RAG. Not a word about memory.

### Phase 3 — through 2024-03-10, commit `a4d32aec2419` (the mature embedchain README)

> **Embedchain is an Open Source Framework for personalizing LLM responses.** It makes it easy to create and deploy personalized AI apps. At its core, Embedchain follows the design principle of being *"Conventional but Configurable"* to serve both software engineers and machine learning engineers.

Full badge row (PyPI, pepy downloads, Slack, Discord, Twitter `@embedchain`, Colab, codecov), an Elon Musk bot example, a live "Chat with PDF" demo. **The pain led with is personalization of LLM responses over your own data — a RAG pain, not a memory pain.**

### Phase 4 — 2024-07-12, commit `f842a92e25e4` — THE PIVOT

Title becomes, in one commit:

> **# Mem0: Long-Term Memory for LLMs**
>
> Mem0 provides a smart, self-improving memory layer for Large Language Models, enabling personalized AI experiences across applications.

Features listed: persistent memory for users/sessions/agents; self-improving personalization; simple API; cross-platform consistency. Install is `pip install mem0ai`. Storage example is Qdrant in Docker.

Taranjeet announced this publicly the same day (https://x.com/taranjeetio/status/1811789999257587785 — **not directly fetchable, HTTP 402; the following is a search-engine snippet, not a verified verbatim quote**):

> "We are changing our name from Embedchain to Mem0 (@mem0ai). This change reflects our growth, learnings, and sharpened focus over the past year. When we started Embedchain in June 2023, our goal was to create a framework that empowers developers of all backgrounds to build AI…"

### Phase 5 — 2024-08-07, commit `4a643a8449bb` — the positioning that stuck

> [Mem0](https://mem0.ai) enhances AI assistants and agents with an intelligent memory layer, enabling personalized AI interactions. Mem0 remembers user preferences, adapts to individual needs, and continuously improves over time, making it ideal for customer support chatbots, AI assistants, and autonomous systems.

**This paragraph has survived essentially unchanged for more than two years.** Compare the current `main` README (2026-09-12):

> [Mem0](https://mem0.ai) ("mem-zero") enhances AI assistants and agents with an intelligent memory layer, enabling personalized AI interactions. It remembers user preferences, adapts to individual needs, and continuously learns over time—ideal for customer support chatbots, AI assistants, and autonomous systems.

The only changes across 25 months: the pronunciation gloss `("mem-zero")` was added (present by 2025-01-30, commit `a06c9a99ae2c`), "continuously improves" became "continuously learns," and the use-case list was compressed. **The verticals named in August 2024 — assistants, customer support, healthcare, productivity, gaming — are the same five named today.**

**This is the direct inverse of entry one's finding.** claude-mem rewrote its tagline five times in twelve months. mem0 rewrote it once, at the pivot, and then held it for two years. For a maintainer deciding whose positioning to study: mem0's is the one that demonstrates conviction.

### Phase 5a — the commercial funnel was present from day one of the pivot

The August 2024 README, the *first* substantive Mem0 README, already leads Get Started with the paid product:

> The easiest way to set up Mem0 is through the managed [Mem0 Platform](https://app.mem0.ai). This hosted solution offers automatic updates, advanced analytics, and dedicated support. [Sign up](https://app.mem0.ai) to get started.
>
> If you prefer to self-host, use the open-source Mem0 package.

Hosted first, self-host second — **eight weeks before the YC S24 batch and fifteen months before the Series A.** The open-source project was structured as a funnel from the moment it became mem0.

### Phase 6 — 2025-10-16, commit `394203d1b5f5` — benchmarks become the pitch

The v1.0.0 README adds a "🔥 Research Highlights" block:

> - **+26% Accuracy** over OpenAI Memory on the LOCOMO benchmark
> - **91% Faster Responses** than full-context
> - **90% Lower Token Usage** than full-context

**The lead argument shifts from "what it does" to "here are numbers against a named competitor."** The competitor named is OpenAI.

### Phase 7 — March–June 2026 — the coding-agent turn

After a **five-month README freeze** (2025-10-16 → 2026-03-24), a dense burst:

```
2026-03-24  docs: remove OpenMemory references from docs, README, and issue templates (#4520)
2026-03-27  feat: add official mem0 CLI (Python & TypeScript) (#4575)
2026-03-28  docs: improve CLI dev workflow and prioritize Node.js installation (#4579)
2026-04-14  feat(oss): port v3 pipeline with hybrid search, entity extraction, additive scoring
2026-04-16  docs: new algorithm migration guides + memory evaluation (#4811)
2026-04-23  Self-hosted dashboard and admin auth (#4837)
2026-05-05  feat(skills): add mem0-integrate + mem0-test-integration pipeline skills (#4961)
2026-05-13  docs(readme): update LongMemEval benchmark to 94.8 and add Temporal Reasoning (#5131)
2026-05-14  feat(cli): Agent Mode bootstrap + claim flow (Python + Node) (#5123)
2026-05-16  docs: promote "Sign up as an agent" + drop plugin-sync prose (#5152)
2026-05-17  docs: link platform migration guide from readme (#5171)
2026-06-12  feat(skills): add mem0-oss-to-platform migration skill (#5455)
2026-07-09  docs: update README benchmarks to current temporal-reasoning results (#6182)
```

Read that list as a strategy: **kill the old side-product (OpenMemory), ship a CLI, ship an OSS-to-Platform migration skill, and make AI agents themselves the signup surface.** §9 covers what this means.

### Phase 8 — April 2026 — the algorithm rewrite

The current README leads with a "New Memory Algorithm (April 2026)" table and five bullets: single-pass ADD-only extraction (no UPDATE/DELETE — memories accumulate rather than being overwritten), agent-generated facts treated as first-class, entity linking, multi-signal retrieval (semantic + BM25 + entity, fused), and temporal reasoning.

**Direction of travel, summarized:** RAG framework → memory layer for LLMs → memory layer for *agents* → benchmarked memory layer → memory layer *installed by coding agents*. Each move is a narrowing toward a sharper wedge. No renaming, no host-chasing whiplash, no token.

---

## 8. Architecture — and how it differs from claude-mem

mem0 is a **library and API, not an agent integration.** Its unit of work is `memory.add(messages, user_id=...)` and `memory.search(query, filters=...)`, called explicitly from your application code. On `add()`, an LLM (default `gpt-5-mini`) extracts salient facts from a conversation turn; those facts are embedded (default `text-embedding-3-small`) and written to a **hybrid datastore** — a vector store for semantic similarity, a graph store for entity relationships, and a key-value/history store for the record log (library mode defaults to local Qdrant at `/tmp/qdrant` and SQLite at `~/.mem0/history.db`; the self-hosted Docker server uses Postgres + pgvector). Memory is scoped along three axes — **user, session, and agent** — which is the design decision that most distinguishes it: it is built for a multi-tenant application serving many end users, not for one developer's laptop. The April 2026 v3 pipeline replaced the original ADD/UPDATE/DELETE reconciliation with **single-pass ADD-only extraction** (one LLM call, memories accumulate, nothing overwritten) plus entity linking and multi-signal retrieval that scores semantic, BM25 keyword, and entity matches in parallel and fuses them, with time-aware temporal reasoning on top. The graph variant, **Mem0ᵍ**, is described in the paper as adding graph-based memory representations over the base architecture.

**The contrast with claude-mem is a contrast of layer, not of quality.** claude-mem hooks into a *single coding agent's lifecycle* (SessionStart, PostToolUse, Stop) to capture what one developer's agent did, compresses it, and injects it back via MCP — it is invisible plumbing for one person's Claude Code. mem0 is an *SDK your product calls* to remember things about *your users* — the developer writes the `add()` and `search()` calls, and the memories belong to end users of an application. **claude-mem is developer-facing tooling; mem0 is application infrastructure.** They compete for the phrase "AI memory" and for the same stars, but they do not compete for the same integration point — *except* where mem0's 2026 coding-agent push (§9) deliberately crosses into claude-mem's layer.

### The paper

**arXiv 2504.19413**, *"Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory"*, April 2025. Authors: Prateek Chhikara, Dev Khant, Saket Aryan, **Taranjeet Singh**, **Deshraj Yadav**. https://arxiv.org/abs/2504.19413

Claimed results on the LOCOMO benchmark (10 conversations, ~600 dialogues and ~26,000 tokens each): **26% relative improvement on LLM-as-a-Judge over OpenAI**, Mem0ᵍ roughly 2% above base Mem0, **91% lower p95 latency** and **>90% token cost savings**.

Having a peer-reviewable artifact with named authors is a structural advantage over any competitor that has only a README. It gets mem0 cited in other people's papers.

### Current self-reported benchmarks (2026-09-12)

From the `main` README:

| Benchmark | Old | New | Tokens | Latency p50 |
|---|---|---|---|---|
| LoCoMo | 71.4 | **92.5** | 7.0K | 0.88s |
| LongMemEval | 67.8 | **94.4** | 6.8K | 1.09s |
| BEAM (1M) | — | **64.1** | 6.7K | 1.00s |
| BEAM (10M) | — | **48.6** | 6.9K | 1.05s |

Against competitors, from mem0's own "State of AI Agent Memory 2026" report (https://mem0.ai/blog/state-of-ai-agent-memory-2026, published 2026-09-12): **Zep** 80.32 on LoCoMo / 71.2 LongMemEval; **Letta** 74.0 on LoCoMo; **OpenAI Memory** 52.9 on LoCoMo, annotated "not independently confirmed."

**Two honesty notes, both from mem0's own text, which is to their credit:** the README states these scores "reflect Mem0's managed platform, which includes proprietary optimizations not available in the open-source SDK; open-source users should expect directionally similar gains but not identical numbers." And the evaluation harness is open-sourced at https://github.com/mem0ai/memory-benchmarks so the numbers can be challenged. **None of these were independently reproduced here (NOT VERIFIED #12).**

---

## 9. The 2026 coding-agent push — the part that should change a competitor's plans

This is not in the founding story but it is the most operationally relevant section. Over roughly six months in 2026, mem0 built a distribution channel aimed squarely at coding agents.

**1. An official CLI** (commit `3225e308590e`, 2026-03-27): `npm install -g @mem0/cli` or `pip install mem0-cli`, then `mem0 init` / `mem0 add` / `mem0 search`.

**2. Agent skills, distributed through the skills standard** (commits 2026-05-05 and 2026-06-12). From the current README, six skills, explicitly targeting *"Claude Code, Codex, Cursor, Windsurf, OpenCode, OpenClaw, and any tool that supports the skills standard"*:

```
npx skills add https://github.com/mem0ai/mem0 --skill mem0
npx skills add https://github.com/mem0ai/mem0 --skill mem0-cli
npx skills add https://github.com/mem0ai/mem0 --skill mem0-vercel-ai-sdk
npx skills add https://github.com/mem0ai/mem0 --skill mem0-integrate
npx skills add https://github.com/mem0ai/mem0 --skill mem0-test-integration
npx skills add https://github.com/mem0ai/mem0 --skill mem0-oss-to-platform
```

Note what `mem0-oss-to-platform` is: **an agent skill whose job is to migrate a user off the open-source package and onto the paid platform.** That is a conversion funnel implemented as a skill.

**3. Agent self-signup** (commit `e60292375167`, 2026-05-14, "Agent Mode bootstrap + claim flow"). From the current README, verbatim:

> AI agents can mint a working Mem0 API key in under five seconds — no email, no dashboard, no OTP. […] The human owner can claim the account later with `mem0 init --email <their-email>` — same key, memories preserved.

**The agent is the signup surface. The human is a later, optional step.** Whatever one thinks of that, it is a genuinely novel go-to-market primitive and it was promoted to the README quickstart on 2026-05-16 (`5f7ace2aef5f`).

**4. Per-host plugins**, four of them shipped within six minutes on 2026-09-09: OpenClaw (v1.1.0), OpenCode (v0.3.0), DeepSeek (v0.3.0), Pi Agent (v0.3.0).

**5. OpenMemory was killed to make room.** OpenMemory MCP — a local-first, private, Docker-based MCP memory server for Cursor/Claude/Windsurf — launched 2025-05-13 (https://mem0.ai/blog/introducing-openmemory-mcp) and had a Product Hunt run. On 2026-03-24, commit `2868bfe749d7` removed OpenMemory references from the README, docs, and issue templates, and `openmemory/README.md` **404s on `main`** as of 2026-09-12. An earlier commit (`da5941215047`, 2025-05-13) had already removed the OpenMemory directory from `pyproject`. https://mem0.ai/openmemory still resolves, so I cannot say the product is dead (NOT VERIFIED #11) — but mem0's *local-first, privacy-first, MCP-server* product line was deprioritized in the repo, and the CLI/skills/platform line replaced it.

**That last point is the strategic tell.** mem0 tried the local-first MCP memory server — the shape closest to claude-mem and to Lore — and walked away from it in favour of a hosted platform reached through agent-installed skills.

---

## 10. Company, funding, and commercial model

### The company

**Mem0**, San Francisco. Y Combinator **Summer 2024** batch (https://www.ycombinator.com/companies/mem0). Status: Active. Team size listed as **10** on the YC directory as of 2026-09-12 (TechCrunch described a four-person team at the Series A in October 2025). Contact: `founders@mem0.ai`.

### Funding — $24M total, announced 2025-10-28

| Round | Amount | Lead | Source |
|---|---|---|---|
| Seed | **$3.9M** | **Kindred Ventures** | TechCrunch (the release itself does not break out the split) |
| Series A | **$20M** | **Basis Set Ventures** | TechCrunch |
| **Total** | **$24M** | — | https://mem0.ai/series-a (company's own page) |

**Participating:** Y Combinator, Peak XV Partners, GitHub Fund.

**Angels** (per TechCrunch, corroborated in part by the company release): Dharmesh Shah (HubSpot), Scott Belsky (Adobe), Olivier Pomel (Datadog), Thomas Dohmke (ex-GitHub), Paul Copplestone (Supabase), James Hawkins (PostHog), Lukas Biewald (Weights & Biases), Brian Balfour (Reforge), Philip Rathle (Neo4j), Jennifer Taylor (Plaid).

Valuation: **not disclosed** anywhere I looked.

Primary: https://mem0.ai/series-a · https://www.prnewswire.com/news-releases/mem0-raises-24m-series-a-to-build-memory-layer-for-ai-agents-302597157.html
Secondary: https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps · https://www.finsmes.com/2025/10/mem0-raises-24m-in-series-a-funding.html · https://inc42.com/buzz/mem0-raises-24-mn-to-scale-its-ai-memory-infrastructure/ · https://kindredventures.com/announcement/mem0-building-the-memory-infrastructure-for-personalized-ai/

### Pricing (https://mem0.ai/pricing, as of 2026-09-12)

| Tier | Price | Add requests/mo | Retrieval requests/mo | Notable |
|---|---|---|---|---|
| **Hobby** | Free | 10,000 | 1,000 | Unlimited end users, 1 project, community support |
| **Starter** | **$19/mo** | 50,000 | 5,000 | 1 project, community support |
| **Pro** | **$249/mo** | 500,000 | 50,000 | Unlimited projects, private Slack, advanced analytics, **graph memory**, **memory consolidation** |
| **Enterprise** | Custom | Unlimited | Unlimited | SLA, **on-prem deployment**, audit logs, SSO, custom integrations |

Plus "usage-based pricing for teams whose traffic doesn't map cleanly to a fixed tier."

Note the **13x jump from Starter to Pro** with nothing between — the ladder is built to push serious usage straight to $249 or to a sales conversation.

### The open-core boundary, stated by mem0 itself

The current README contains this table, which is unusually explicit:

| | Library | Self-Hosted Server | Cloud Platform |
|---|---|---|---|
| **Best for** | Testing, prototyping | Teams on their own infra | Zero-ops production |
| **Setup** | `pip install mem0ai` | `docker compose up` | Sign up at app.mem0.ai |
| **Dashboard** | — | Yes | Yes |
| **Auth & API Keys** | — | Yes | Yes |
| **Advanced Features** | — | **Teasers** | **All included** |

The word is *Teasers*. mem0 is telling self-hosters, in the README, that they get a demo of the good parts. Combined with the benchmark footnote ("Mem0's managed platform… includes proprietary optimizations not available in the open-source SDK") and the `mem0-oss-to-platform` migration skill, the boundary is drawn deliberately and consistently: **the OSS package is a complete, usable product and simultaneously an advertisement with a built-in migration path.**

### Distribution partnerships

- **AWS** — mem0 states AWS selected it as **"the exclusive memory provider"** for the Strands Agents SDK (https://mem0.ai/blog/aws-and-mem0-partner-to-bring-persistent-memory-to-next-gen-ai-agents-with-strands). The repo ships a "Mem0 Strands Integration" release (v0.1.1, 2026-08-27). AWS's own Database Blog has co-published on mem0 + ElastiCache for Valkey + Neptune Analytics (https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/). **The "exclusive" characterization is mem0's; see NOT VERIFIED #6.**
- **Framework integrations** named in the press release: CrewAI, Flowise, Langflow. LangGraph and the Vercel AI SDK are covered in the README/docs.
- Compliance claims surfaced in secondary coverage: **SOC 2 and HIPAA**. Not verified against a primary trust-center page.

### No token, no rebrand, no memecoin

Recorded explicitly because entry one found all three. mem0 has: a single name since 2024-07-12, no cryptocurrency, no third-party token "embraced by the creator," and no locale-sprawl SEO README. Whatever else is true, the governance signal here is clean.

---

## Assessment — five things worth weighing

1. **mem0 is the real competitor, and the star counts mislead in the opposite direction from entry one.** claude-mem has 44% more stars and roughly 1/47th the PyPI usage. If the archive's purpose is to find who actually occupies the "AI memory" position, it is mem0 — 3.7M PyPI + 472K npm downloads in 2026-08, both still climbing, against a company with $24M and a named AWS relationship.

2. **The origin story is a pivot, and pivots of this shape are repeatable.** embedchain was a RAG framework with real traction that its founders judged to be the wrong layer, and they converted it — brand, repo, package, org, and audience — in a single commit on 2024-07-12, entered YC eight weeks later, and raised $24M fifteen months after that. The trigger was reportedly a meditation app whose users complained it did not remember them. For a maintainer, the transferable lesson is that the star history and the package name are not the asset; the audience is, and it survives a rename.

3. **The layer distinction is real but mem0 is deliberately eroding it.** mem0 is application infrastructure (you call `add()`/`search()` on behalf of your users); claude-mem and Lore-shaped tools are developer plumbing (hooks capture what your agent did). Those were separate markets until 2026, when mem0 shipped a CLI, six installable agent skills, four coding-agent plugins, and an agent-mints-its-own-API-key signup flow. **Anyone building developer-facing agent memory should assume mem0 will be sitting in the same `npx skills add` catalogue.** The counter-signal is that mem0 *also* deprioritized OpenMemory, its local-first private MCP server — so it is entering via hosted-platform distribution, not via local-first design. That gap (local-first, private, no account, no hosted dependency) is the one mem0 has visibly chosen not to defend.

4. **It is a staffed project, not a personality.** Top committer at 18.1%, top three at 40.6%, neither founder in the top two, 395 contributors total. Entry one's subject was 82% one person. If the question is "which of these survives its founder losing interest," the answer is not close — and that changes how much weight to put on any dependency risk assessment.

5. **Positioning conviction is a measurable asset.** mem0's core README paragraph has survived 25 months and roughly 130 README commits nearly word for word, while the project underneath it rewrote its retrieval algorithm, added a graph store, published a paper, raised twice, and built a CLI. The pitch stayed still while the product moved. That is the opposite of entry one's five-taglines-in-twelve-months, and it is the cheaper of the two strategies to copy.

---

## Source index

**Primary (project-owned, company-owned, or authoritative APIs):**
- https://github.com/mem0ai/mem0 — repo metadata, commits, pagination-header counts
- https://github.com/mem0ai — organization
- https://github.com/deshraj — co-founder profile (GitHub API)
- `https://github.com/mem0ai/mem0/releases.atom` · `.../tags.atom` — release/tag feeds
- `https://github.com/mem0ai/mem0/graphs/contributors-data` — per-contributor commit totals (**method note for future entries: this JSON endpoint is not subject to the 60 req/hr unauthenticated REST API limit and is the way to get contributor distribution without a token**)
- https://github.com/taranjeet — co-founder profile (rendered HTML; the REST API budget was spent)
- `https://raw.githubusercontent.com/mem0ai/mem0/<sha>/README.md` — historical READMEs at `2b82ff695fd1`, `b6304550de35`, `a4d32aec2419`, `f842a92e25e4`, `4a643a8449bb`, `a06c9a99ae2c`, `394203d1b5f5`, `main`
- `https://pypi.org/pypi/mem0ai/json` · `https://pypi.org/pypi/embedchain/json` — version and publish-date history
- `https://pypistats.org/api/packages/mem0ai/overall` · `.../embedchain/overall` — 180-day download windows
- `https://registry.npmjs.org/mem0ai` · `https://api.npmjs.org/downloads/range/...` — npm versions and full download history
- https://mem0.ai · https://mem0.ai/pricing · https://mem0.ai/series-a · https://mem0.ai/research · https://mem0.ai/openmemory
- https://mem0.ai/blog/state-of-ai-agent-memory-2026 · https://mem0.ai/blog/introducing-openmemory-mcp · https://mem0.ai/blog/aws-and-mem0-partner-to-bring-persistent-memory-to-next-gen-ai-agents-with-strands
- https://docs.mem0.ai · https://docs.mem0.ai/open-source/overview · https://app.mem0.ai
- https://www.ycombinator.com/companies/mem0 — YC directory (batch, founder bios)
- https://www.prnewswire.com/news-releases/mem0-raises-24m-series-a-to-build-memory-layer-for-ai-agents-302597157.html — company press release
- https://arxiv.org/abs/2504.19413 — the paper
- https://github.com/mem0ai/memory-benchmarks — open-sourced evaluation harness
- https://x.com/taranjeetio/status/1811789999257587785 — rename announcement (**not fetchable, HTTP 402**)

**Secondary (third-party writing about the company):**
- https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps — the richest single secondary source (seed/A split, pivot story, usage metrics)
- https://kindredventures.com/announcement/mem0-building-the-memory-infrastructure-for-personalized-ai/ — seed lead's own announcement
- https://www.finsmes.com/2025/10/mem0-raises-24m-in-series-a-funding.html
- https://inc42.com/buzz/mem0-raises-24-mn-to-scale-its-ai-memory-infrastructure/
- https://www.bwdisrupt.com/article/mem0-raises-24-mn-from-basis-set-ventures-peak-xv-partners-others-577381
- https://www.business-standard.com/companies/start-ups/mem0-raises-24-million-series-a-funding-to-build-memory-layer-for-ai-agents-125102900850_1.html
- https://theaiinsider.tech/2025/11/17/mem0-raises-24m-to-launch-universal-ai-memory-platform-for-apps-and-agents/
- https://councils.forbes.com/profile/Taranjeet-Singh-Co-founder-CEO-Mem0/426fb5ad-7d97-43a5-a0ad-3797c6a75c33
- https://www.crunchbase.com/organization/mem0 · https://tracxn.com/d/companies/mem0/ (not fetched; listed for a future researcher)
- https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/
- https://deepwiki.com/mem0ai/mem0/15.2-openmemory-mcp-server
- https://www.producthunt.com/products/openmemory-mcp-2
- https://valueaddvc.com/blog/the-ai-memory-problem-how-startups-are-solving-for-persistent-context — competitive framing vs Letta and Zep
