# CrewAI — Quick Pass (2026-09-12)

**This is a quick pass, not a full study.** It was researched in a single afternoon from the repo and
the public docs, has no promotion/origins analysis, and should not be treated as equivalent to the
claude-mem, mem0, or landscape entries. CrewAI appeared in the earlier research only as the framework
mem0 embedded itself into; it had never been studied as a subject.

## What it is

Python framework for multi-agent workflows. `crewAIInc/crewAI`, created 2023-10-27, MIT.
58,410 stars, 8,413 forks, 767 open issues, pushed 2026-09-11 (very active).
Self-described: *"Fast and Flexible Multi-Agent Automation Framework."*

## How it works

An agent is config with three text fields — `role`, `goal`, `backstory` (plus `llm`, `tools`). Tasks
are defined separately; agents are grouped into a **crew**; execution is sequential or hierarchical
(one manager agent delegating).

**A crew is a one-shot job.** `crewai run` executes it once and exits. Their own first-crew guide uses
two agents — a "Senior Research Specialist" and a "Report Analyst". Real crews are typically 2-5
agents. The agent *definition* never changes on its own: it is text you wrote and you edit. The team
does not evolve; it is a list in a config file. Use cases are repeatable pipelines (research->report,
ticket triage, data enrichment, content generation) — automated workflows with LLM steps, not a
colleague you work alongside.

## Memory (docs read 2026-09-12)

A **unified memory API** that replaces the older short-term / long-term / entity / external split.
Retrieval scores on three signals: semantic similarity, recency (exponential decay), and an
importance value assigned at encoding. Memories live in filesystem-like scopes (`/project/alpha`,
`/agent/researcher`), and an LLM infers the scope when it is unspecified. Memory can be crew-level
(shared; the `memory=True` default), **agent-level** (private scoped views), or standalone, and it
persists across sessions.

Capture is semi-automatic: crews extract facts from task outputs by LLM and inject relevant context
into prompts. `remember()`, `recall()` and `extract_memories()` exist for explicit control but are
not the default path.

Storage is **LanceDB** at `./.crewai/memory` — an embedded vector database (SQLite-shaped, not a
server), binary on disk.

**Scoring against the five axes:** axis 2 (per-agent curated knowledge) is **P**, not N — per-agent
scoping exists, but capture is automatic and model-decided and nothing bounds it by a declared role.
Axis 3 stays **N**: a binary vector store cannot be read, diffed, or corrected in a pull request.
This supersedes the `N` in the landscape study's §2 table; see the corrections log in
[README](README.md).

## Commercial model

$18M raised (Series A led by Insight Partners, boldstart inception round; Andrew Ng and Dharmesh Shah
among angels). Free OSS library; money is a hosted enterprise platform — SSO, RBAC, deployment, 45-day
onboarding — billed by **workflow executions** (free tier 50/month, enterprise "contact us"). The
company claims ~half the Fortune 500 touched it and ~2B executions in 12 months. An outside estimate
put ARR near $3.2M in 2025 — **unverified, do not cite**.

## Adoption measurement caution

PyPI downloads (mirrors excluded) ran 300K-1.7M/day through July and August 2026, then fell to
~85K/day overnight on **2026-08-25** and stayed flat. A 95% single-day drop is not users leaving;
something automated stopped, or PyPI changed its bot filtering. Real installs are probably the
~85K/day floor.

## Positioning consequences

- The overlap is roles + collaboration; the gap is what an agent *keeps* between runs.
- One-line contrast that works: **they orchestrate agents; we accumulate expertise.** Their agents are
  workers you configure; ours are specialists you teach.
- "A team of AI specialists" remains unavailable to us — CrewAI owns that phrasing at 58.4k stars.
- **Both CrewAI and mem0 run the same business model**: free OSS library, paid enterprise platform on
  top. That is the category default. We are not doing it, and that should be a deliberate, stated
  choice rather than an omission.
