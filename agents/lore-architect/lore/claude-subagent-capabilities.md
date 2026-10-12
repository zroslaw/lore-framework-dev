---
lore: 1
type: topic
summary: "Claude Code subagents per the official docs (2026-10-12 snapshot, 2.1.296, read not run): SendMessage resume, peer messaging, nesting and concurrency caps, frontmatter fields, and a possibly stale named-teammate binding."
parent: lore/claude-engine-capabilities.md
---

# Claude Code Subagent Capabilities — Docs Snapshot (2026-10-12)

**Grade: read the docs** (code.claude.com/docs/en/sub-agents) against local build Claude Code
2.1.296. Nothing here was run. Each line is a claim to verify before it enters a profile binding or
any other contract ([engine-bundle-reading-has-an-evidence-grade.md](engine-bundle-reading-has-an-evidence-grade.md)).

- **Resume** — `SendMessage({to: <agent id or name>})` continues a subagent with its full history.
  Transcripts persist within the session, survive a restart when that session is resumed, and are
  deleted after `cleanupPeriodDays` (30 by default). The built-in `Explore` and `Plan` agents are
  one-shot: no ID, so no resume.
- **Peer messaging** — every subagent receives a system-reminder roster of `main` plus each named
  agent, all valid `SendMessage` targets, so subagents can message each other and the main
  conversation.
- **Nesting and concurrency** — subagents may spawn subagents, 3 levels deep by default
  (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; `1` disables nesting); 20 run concurrently
  (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).
- **Definition frontmatter** now includes `memory` (`user`/`project`/`local`; injects the first 200
  lines or 25KB of that directory's `MEMORY.md`), `skills`, `isolation: worktree`, `background`,
  `effort` and `maxTurns`.
- **Background subagents get a reduced tool set** — they keep `SendMessage` and `Skill`, not `Agent`.

## The named-teammate binding may be stale

`docs/engines/claude.md`'s subagent-spawn binding says a `name`d `Agent` call becomes an
Agent-Teams teammate that does not auto-return its report — a trap hit live in v30
([docs-engines-convention.md](docs-engines-convention.md) § Engine traps belong in the binding). The
2.1.296 tool schema describes `name` only as making the agent "addressable via SendMessage while
running", and marks `team_name` deprecated and ignored ("the session has a single implicit team").
One of the two accounts is out of date on this build.

**Re-verify by running a named and an unnamed `Agent` call before relying on either.** Until then
the binding stays as written: a docs or schema reading must not rewrite a point-of-use contract.
The sweep, with every site that states the trap, is filed in
[framework-improvements-backlog.md](framework-improvements-backlog.md) § Agent Teams / Spawn-Teammate
(additions).

## Compared with the other engines

Same snapshot, same grade: Cursor documents resume by agent ID but returns only a final result and
describes no inter-subagent messaging ([cursor-engine-capabilities.md](cursor-engine-capabilities.md));
Codex documents parent-mediated coordination, with `multi_agent_v2` and its message board off
([codex-native-multi-agent-subsystem.md](codex-native-multi-agent-subsystem.md)). As of 2026-10-12,
**Claude Code is the only engine whose docs describe peer messaging among subagents** — the
deciding fact for any design that wants agents to coordinate without routing through a hub
([spawn-teammate-feature.md](spawn-teammate-feature.md) § Autonomous-team fit).

## See Also

- [claude-engine-capabilities.md](claude-engine-capabilities.md) — the hub.
- [parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md) § Result delivery
  differs by spawn kind — the v18–v30 record of how named teammates behaved.
- [subagent-as-optimization-vs-subagent-as-semantics.md](subagent-as-optimization-vs-subagent-as-semantics.md)
  — why the spawn mechanism matters per procedure.
