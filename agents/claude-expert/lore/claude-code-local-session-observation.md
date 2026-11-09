---
lore: 1
type: topic
summary: "Local Claude Code session observation: inference (2026-10-16) that monitors must separate a durable session from intermittent CLI processes, plus the verified transcript file layout (2026-11-08)."
parent: lore/claude-apps-and-surfaces.md
---

# Claude Code local session observation

**Label: inference** (2026-10-16). This is a local monitoring design conclusion, not a documented
Anthropic API contract. Recheck the local session-data format after a Claude Code update. It
contains no personal session content, credentials, or utilization data.

## Identity model

Treat a Claude Code conversation session and a `claude` process as different identities. A later
CLI invocation can resume the same session, so the stable session identifier is the dashboard
identity; a process is only an intermittent signal that work is currently running.

## Safe local observer

Use local Claude session metadata to discover sessions. Reconcile it with currently running
`claude` processes at a short interval. Store only the metadata required for operational status:
session identifier, workspace when available, timestamps, process state, and source confidence.
Do not collect prompts, replies, tool input or output, or credentials.

This preserves an idle but resumable session after its command process exits, and it prevents a
resume from being shown as a new conversation. The installed engine and the monitor service remain
the responsibility of **workstation-keeper**.

## Sources and limits

Source: local design review on 2026-10-16. No Anthropic public source was checked for this
implementation detail, so do not present it as a stable product guarantee.

## Transcript file layout, verified (2026-11-08, Claude Code 2.1.319)

**Verified** locally. Not a published schema: keep unknown records and tolerate a torn last line.

- Path: `<config>/projects/<cwd with every non-alphanumeric character replaced by "-">/<session id>.jsonl`
  (`<config>` is `CLAUDE_CONFIG_DIR` or `~/.claude`). The file appears when the first prompt runs.
- Subagents: `<session id>/subagents/agent-<id>.jsonl` and `agent-<id>.meta.json`. The meta file
  holds `agentType`, `description`, `toolUseId`, `spawnDepth`, `requestShape`
  (`foreground`/`background`), `pickedEffortModel`, `finished`, `isBuiltIn`, `name` (only when the
  Agent call named it), `parentAgentId` (nested). The stream's `task_id` is the `<id>`
  (see [Agent SDK](agent-sdk.md), [subagent monitoring](subagent-monitoring-and-correlation.md)). A
  subagent file holds only its own records (`isSidechain: true`, `agentId`), no copy of the
  parent's history.
- One assistant message is written as several records (one per content block) with the same
  `message.id`; each carries `message.usage`, and the later record has the final output count.
  Count usage once per message ID. `usage.input_tokens` excludes cache reads and cache creation.
- Parent links form a tree: an assistant record with a tool call can have two children (the next
  block and the tool result), so use file order, not `parentUuid`, for order. A real rewind gives
  two user prompts with the same parent.
- Compaction: `{type:"system", subtype:"compact_boundary", timestamp,
  compactMetadata:{trigger,preTokens,postTokens,durationMs}, logicalParentUuid}` followed by a user
  record with `isCompactSummary: true`. Manual `/compact` verified; automatic not tested.
- Other record types: `user`, `assistant`, `attachment`, `queue-operation`, `last-prompt`,
  `ai-title`, `session-owner` (holds account IDs: never copy), `mode`, `permission-mode`,
  `file-history-*`, `api-request*`, `tools-used`, `cost-state`, and `system` subtypes such as
  `stop_hook_summary`, `turn_duration`, `away_summary`.
- Thinking blocks are often recorded with empty `thinking` and a signature (text not kept).
- Cost from these records (`cost-state`, `<synthetic>`, cache TTL fields): see
  [observability and cost](agent-observability-and-cost.md#claude-code-cost-from-local-transcripts).
