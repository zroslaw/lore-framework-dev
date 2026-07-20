# Competitive Landscape — Similar Projects (re-surveyed 2026-07-20)

Survey of external projects occupying similar space to the lore framework. First surveyed 2026-07-02 alongside the multi-engine-portability assessment; re-surveyed 2026-07-20 — the space moved noticeably in those 18 days. **No project combines all of lore-framework's pieces** — named role-based agents + team-shared git repos + a deliberate reflect/merge lifecycle + attach/consult/recall cross-agent mechanisms — but individual axes that were differentiators in early July are eroding fast (see "What changed" below).

## Name collision: three external projects called "Lore" (new, 2026-07-20)

The name "Lore" is now contested in exactly this niche — relevant to the "Lore Agents" product-name decision (`lore-agents-product-name.md`):

- **amarlearning/lore** — "institutional memory for your codebase." Closest in *spirit*: captures decision reasoning (rejected alternatives, constraints) via Claude Code lifecycle hooks into a version-controlled `.lore/` directory, so **teams inherit knowledge via git** — the same team-shared-via-git bet we made. Three-tier promotion (temp → staging/branch → decisions on merge); decisions anchor to symbols, not line numbers. But: Claude-Code-only (built on its hook system), fully automatic capture (no deliberate reflect/merge), codebase-scoped not agent-scoped, nascent (4 stars, v0.2.1).
- **BYK/loreai** — most technically substantial. A transparent LLM-proxy doing incremental *distillation* (not summarization) into three tiers: SQLite FTS5 full history → timestamped observation logs → curated `.lore.md`/`AGENTS.md` maintained by a background curator agent. **Cross-engine** (Claude Code, Codex, OpenCode, Pi, any OpenAI/Anthropic-compatible API via gateway) with a *planned* team-sync feature literally called "Folk Lore." 85 stars, 69 releases, very active, self-declared experimental.
- **getlore-ai** — hosted knowledge tools for agents (semantic search + citations). Vendor-hosted pole; least similar.

## Surveyed projects (2026-07-02 baseline, updated)

- **claude-mem** — auto-captures sessions, compresses, re-injects (SQLite + ChromaDB vector search). **Now cross-engine** (Claude Code, Codex, Gemini, Copilot, OpenCode, more) and reportedly ~65K stars — no longer the Claude-bound personal tool of the first survey. Still: automatic capture, no roles, no team-sharing story.
- **claude-memory-compiler** — hooks capture sessions, an LLM "compiler" organizes them into cross-referenced knowledge articles (Karpathy's LLM-KB idea). Merge-equivalent is automated where ours is skill-triggered.
- **agentmemory** (two unrelated projects) — markdown memory, git-friendly, no database. `jayzeng/` targets Claude Code/Codex/Cursor with qmd semantic search; `rohitg00/` now claims **auto-install into 50+ agents' native skill directories** — the multi-engine packaging problem we solved by hand for 3 engines, solved there at breadth (though shallower per engine). Its per-role write-tagging (`AGENT_ID`) remains the closest external analog to per-agent lore ownership.
- **memsearch** (Zilliz) — markdown source of truth + Milvus vector index. Still the concrete model for our parked vector-search item (`vector-db-search-parked.md`; note the >100-topics trigger has since fired at ~147).
- **claude-supermemory, Letta/MemGPT, mem0, Zep** — hosted/DB-backed memory layers; opposite pole from our no-database, git-as-backend stance.
- **Karpathy LLM-Wiki pattern implementations** — a growing family: `ar9av/obsidian-wiki`, `nvk/llm-wiki`, multiple practitioner write-ups of self-maintaining markdown KBs, plus "one git repo as shared team brain" guides appearing as blog prose. The *pattern* is mainstream; the deliberate lifecycle around it is not.
- **Claude Code's own built-in auto memory** — still the real competitive pressure on the personal single-project use case; improves for free.

## Standards-level developments (new, 2026-07-20)

- **Google Open Knowledge Format (OKF)** — announced 2026-06-12, v0.1, Apache 2.0. Vendor-neutral spec for organizational knowledge as **markdown files + YAML frontmatter in directories**, linked by standard markdown links into a traversable knowledge graph, hostable in any git repo. Reserved filenames `index.md` / `log.md`; only required frontmatter field is `type`. Reference implementations shipped (sample bundles, BigQuery enrichment agent, HTML visualizer). This is a standards land-grab in exactly our substrate space. Note the direct convention conflict: OKF *requires* frontmatter on knowledge files; our lore topics are deliberately frontmatter-free. Tracked as a backlog item (evaluate alignment/adoption — see `framework-improvements-backlog.md` § OKF alignment).
- **AGENTS.md standardized under the Linux Foundation** — 60K+ projects, read natively by essentially every coding agent. The memory-file half of our engine bindings is now commodity infrastructure.

## What changed between 2026-07-02 and 2026-07-20

- **"Cross-engine" alone is no longer a differentiator.** The first survey's positioning claim — "every competitor is engine-bound by construction" — is dead: claude-mem, loreai, and rohitg00/agentmemory all now claim multi-engine support.
- **"Team-shared via git" is emerging elsewhere** — amarlearning/lore has it today; loreai plans it ("Folk Lore").
- **The substrate is standardizing** (OKF, Linux-Foundation AGENTS.md) — plain-markdown-in-git knowledge is becoming commodity, which validates the bet and commoditizes it simultaneously.

## Positioning implication (revised)

The moat has narrowed to the triad no surveyed project has *any* element of, let alone all three:

1. **Named role-based agents as the knowledge unit** — identity + role + own lore, vs. everyone else's codebase- or project-scoped memory.
2. **Deliberate, skill-triggered reflect/merge lifecycle** — curation as an intentional act, vs. automatic hook/proxy capture.
3. **Cross-agent collaboration mechanisms** — attach/consult/recall/spawn-teammate.

Positioning language should lead with the triad, not with cross-engine or git-sharing alone. The "Lore" name collision is a real (if early-stage) brand consideration for `lore-agents-product-name.md`. Canonical write-up of this framing (advertising pitch line, risk assessment, re-survey-cadence rule): `positioning-triad-differentiation.md`.

## Status

Re-surveyed 2026-07-20 (prior: 2026-07-02). This space moves in weeks, not months — re-survey before any positioning-sensitive ship (README rewrite, marketplace submission, public announcement).

## See Also

- `multi-engine-portability-direction.md` — the direction the original positioning implication fed; its uniqueness claim needs the 2026-07-20 revision above.
- `positioning-triad-differentiation.md` — the canonical positioning framing derived from this survey (advertising pitch, risk assessment, re-survey cadence).
- `team-shared-knowledge-principle.md` — foundational framing; now shared (in weaker form) by amarlearning/lore.
- `framework-as-engine-not-kb.md` — why lore-framework frames itself as an engine, not a KB tool.
- `lore-agents-product-name.md` — the product-name decision the "Lore" collision bears on.
- `vector-db-search-parked.md` — parked item `memsearch` models; trigger (>100 topics) has fired.
- `framework-improvements-backlog.md` § OKF alignment — the tracked improvement item from this survey.
