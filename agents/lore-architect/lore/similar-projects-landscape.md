# Competitive Landscape — Similar Projects (surveyed 2026-07-02)

Survey of external projects occupying similar space to the lore framework, run alongside the multi-engine-portability assessment (`multi-engine-portability-direction.md`). **No project combines all of lore-framework's pieces** — named role-based agents + team-shared git repos + a reflect/merge lifecycle + attach/consult/recall cross-agent mechanisms — but the space is crowded on individual axes. Useful as a positioning reference, and as a landscape check before calling any framework mechanism "novel."

## Surveyed projects

- **claude-mem** — auto-captures Claude Code sessions, compresses, re-injects. Personal, fully automatic (no skill-triggered lifecycle), no roles, no team-sharing.
- **claude-memory-compiler** — closest in spirit: hooks capture sessions, an LLM "compiler" organizes them into cross-referenced knowledge articles (Karpathy's LLM-KB idea). Its merge-equivalent is automated where lore-framework's is skill-triggered (reflect/merge as deliberate phases, not a background hook).
- **agentmemory** (two unrelated projects, `jayzeng/` and `rohitg00/`) — markdown memory with semantic search; the `rohitg00` variant tags writes per-role (`AGENT_ID`) in multi-agent setups — the closest external analog to per-agent lore ownership.
- **memsearch** (Zilliz) — markdown as source of truth with a Milvus vector index on top. A concrete model for the day lore-framework's own parked vector-search item activates. See `vector-db-search-parked.md` (trigger: >100 topics/agent — currently ~90).
- **claude-supermemory**, Letta/MemGPT, mem0, Zep — hosted/DB-backed memory layers. Opposite pole from lore-framework's no-database, git-as-backend stance.
- **Claude Code's own built-in auto memory** — the real competitive pressure on the *personal, single-project* use case; it will keep improving for free. Lore-framework's moat is explicitly the team-shared, multi-agent, cross-session-lifecycle story, not personal note-taking.

## Positioning implication

Every listed competitor is bound to one engine (Claude Code) or to a vendor-hosted service. None federate knowledge across *different* coding agents sharing one git substrate. Once multi-engine ports exist (Codex, Cursor — see `multi-engine-portability-direction.md`), "a team with members on different AI coding tools shares one knowledge base" becomes a differentiator no surveyed competitor can match, because they're all engine-bound by construction. This is the sharpest answer yet to "how do we stand out" and should inform README/positioning language once a port ships.

## Status

Point-in-time survey (2026-07-02). Re-survey periodically — this is a fast-moving space (note how much shipped between the framework's early design and this survey: SKILL.md standardization, AGENTS.md adoption, several of these memory tools).

## See Also

- `multi-engine-portability-direction.md` — the direction this survey's positioning implication feeds.
- `team-shared-knowledge-principle.md` — the foundational framing that is lore-framework's actual differentiator against every surveyed project.
- `framework-as-engine-not-kb.md` — why lore-framework frames itself as an engine, not a KB tool like most of the surveyed projects.
- `vector-db-search-parked.md` — the parked lore-framework item `memsearch` is a concrete model for.
