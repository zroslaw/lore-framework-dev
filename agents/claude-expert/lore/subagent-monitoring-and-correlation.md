---
lore: 1
type: topic
summary: "Subagent monitoring (2026-10-18): seeing and correlating subagents with their session in Managed Agents (thread REST API) and the Agent SDK (stream fields, hooks, traces, local transcripts); what an API exposes."
parent: lore/developer-platform.md
---

# Subagent monitoring and correlation

**Documented**, checked 2026-10-18, unless a line says otherwise. Sources:
https://code.claude.com/docs/en/agent-sdk/subagents,
https://code.claude.com/docs/en/agent-sdk/hooks,
https://code.claude.com/docs/en/agent-sdk/sessions,
https://code.claude.com/docs/en/agent-sdk/observability, and the `claude-api` skill bundled with
Claude Code 2.1.302 (`shared/managed-agents-multiagent.md`, `shared/managed-agents-events.md`).

Short answer: Managed Agents exposes every subagent through its REST API. The Agent SDK gives the
same detail locally (stream, hooks, files, OpenTelemetry) but has no hosted API. The Tool Runner
has no subagents.

## Managed Agents — through the API

- Each subagent is a **thread** of the session. `GET /v1/sessions/{sid}/threads`
  (`client.beta.sessions.threads.list`) returns each `SessionThread` with `id`, `status`, `agent`
  (a snapshot of its config), **`parent_thread_id`** (null for the primary thread),
  `workflow_run_id` (set only on dynamic-workflow threads), `archived_at`, and optional `stats`
  and `usage`.
- Full detail per subagent: `GET /v1/sessions/{sid}/threads/{tid}/events` and `.../stream`.
  Live text previews of a child appear only on the child's own stream.
- The primary (session) stream is a condensed view: `session.thread_created`,
  `session.thread_status_*`, `agent.thread_message_sent` (task out) and
  `agent.thread_message_received` (report back). Direction is relative to the stream that carries
  the event. Tool calls from a thread carry its `session_thread_id`.
- Per-thread `usage.list_cost` does not sum to the session total (the session figure adds
  running time); the session figure is authoritative.
- Console session viewer: one timeline lane per thread, with per-thread context size and cost.
- Limits: one level of delegation, 25 child threads per session (advisor and workflow-run threads
  are exempt; workflow runs have their own limits).

## Agent SDK — locally

- **Stream:** a subagent starts with an `Agent` tool call (`Task` in older versions and in the
  `system:init` tool list; match both). Every message from inside a subagent carries
  `parent_tool_use_id` (the ID of that `Agent` call). TypeScript messages also carry `agent_id`,
  equal to the `task_id` of the subagent's task events (v0.3.292+). Messages carry `session_id`.
- **Hooks:** `SubagentStart` and `SubagentStop` give `agent_id`, `agent_type`, and
  `agent_transcript_path`. All hooks share `session_id`; hooks that fire inside a subagent also
  carry `agent_id` and `agent_type`, which gives a per-subagent tool audit.
- **Traces (beta):** a subagent's `llm_request` and `tool` spans nest under the parent's
  `claude_code.tool` span, so the whole delegation tree is one trace; spans carry `session.id`.
- **Transcripts:** each subagent's transcript is a separate file. `listSessions()` and
  `getSessionMessages()` (Python `list_sessions()`, `get_session_messages()`) read saved sessions;
  a `SessionStore` adapter mirrors transcripts to the builder's own storage.
- **Cost:** `total_cost_usd` and `modelUsage` include subagents; `usage` does not. Inference: no
  per-subagent cost field was found; input and cache tokens can be summed per
  `parent_tool_use_id`, but output tokens cannot (the per-step value is a placeholder).
- **Caps:** `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (default 3), `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
  (default 20), and `maxBudgetUsd` for the whole tree.
- **No hosted API.** To get a central API, ship these signals to the builder's own backend
  (hooks, OpenTelemetry, `SessionStore`).

## Tool Runner

No subagents. If a builder runs several loops, the builder correlates them, for example with an
own OpenTelemetry parent span or own IDs.

**How to apply:** when someone needs a central API to inspect subagent runs, Managed Agents has
it ready to use. With the Agent SDK, the same detail exists but the builder must collect it.
See also [observability and cost](agent-observability-and-cost.md).
