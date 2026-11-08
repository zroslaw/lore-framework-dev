---
lore: 1
type: topic
summary: "Claude Agent SDK, formerly Claude Code SDK (2026-10-18): Claude Code as a Python or TypeScript library you host; built-in tools and features, sessions, multi-turn and resume APIs, and what a builder still writes."
parent: lore/developer-platform.md
---

# Claude Agent SDK

Formerly the Claude Code SDK. Option 4 of the [four ways to build an agent](developer-platform.md).
Checked 2026-10-18.

## Documented

Sources: the `claude-api` skill bundled with Claude Code 2.1.302; https://code.claude.com/docs/en/agent-sdk.

- Claude Code packaged as a library: `claude-agent-sdk` (Python) and
  `@anthropic-ai/claude-agent-sdk` (TypeScript). You call `query(prompt, options)`, and it drives
  the full agent loop.
- It includes the built-in tools (Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch), MCP,
  subagents, hooks, permissions, sessions, and context management.
- It is a harness only: you host it.
- The `claude-api` skill does not generate Agent SDK code; it points to the Agent SDK docs. Use
  the docs page above for code questions. The page index is https://code.claude.com/docs/llms.txt
  (Agent SDK pages: `cost-tracking`, `observability`, `subagents`, `hooks`, `sessions`,
  `hosting`, `agent-loop`, `typescript`, `python`).

## Sessions and multi-turn

**Documented**, https://code.claude.com/docs/en/agent-sdk/sessions, checked 2026-10-18.

- Python `ClaudeSDKClient`: each `client.query()` continues the same session; read replies with
  `client.receive_response()`.
- TypeScript has no session-holding client: pass `continue: true` (most recent session in the
  directory) or `resume: <session-id>`. The experimental V2 session API (`createSession()`) was
  removed in TypeScript Agent SDK 0.3.142. Streaming input mode also exists: one `query()` call
  carries several user turns.
- `resume` takes a session ID (from `session_id` on the result message); `forkSession` /
  `fork_session` branches a copy. `persistSession: false` (TypeScript) keeps nothing on disk.
- Sessions are saved as `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` on the local
  machine. To resume on another host, use a `SessionStore` adapter or move the file.
- `listSessions()`, `getSessionMessages()`, `getSessionInfo()`, `renameSession()`,
  `tagSession()` (Python snake_case equivalents) read and organize saved sessions.
- Permission prompts: a `canUseTool` callback (TypeScript name seen in the hooks docs).

## Session sources and streaming

**Documented**, checked 2026-11-06: the session APIs can list and read local CLI sessions,
and a fork creates a separate session with remapped message IDs. The live stream is a separate
source: partial API events accompany completed assistant blocks. Token deltas cover the main
agent; the CLI needs `--forward-subagent-text` to forward subagent text and thinking. Reconcile
partial updates with completed blocks, and keep the source identity. Do not treat a raw file,
an SDK message projection, and a live stream as identical. Sources: [session APIs](https://code.claude.com/docs/en/agent-sdk/sessions),
[streaming](https://code.claude.com/docs/en/agent-sdk/streaming-output),
and [CLI output](https://code.claude.com/docs/en/headless).

**Limit:** the local JSONL record format is not a published stable schema. Preserve unknown
records when inspecting it; do not assume the SDK projection includes every raw record. See
[upstream schema discussion](https://github.com/anthropics/claude-code/issues/49400).

**Local test**, CLI 2.1.317, 2026-11-04: a controlled capture contained API request-shape
and blob records, including a system array. These can contain private instructions; sanitize raw
files before sharing. In one cancellation test the file contained enqueue and remove records, an
aborted assistant block, and interruption markers. These observations do not establish a stable
format or behavior in other versions. Installed CLI help also described system prompt snapshots
that may persist across resume until compaction; the test did not establish the snapshot setting.

## Verified locally, streaming-input behavior (2026-11-08)

**Verified** with Claude Code 2.1.319 and `@anthropic-ai/claude-agent-sdk` 0.3.319 (the SDK
version follows the Claude Code version), macOS. Recheck on newer versions.

- **No prompt needed to start.** With streaming input, `query.initializationResult()` returns in
  about 10 s (user hooks run) with `models` (aliases `default`, `opus`, `sonnet`, `fable`,
  `haiku`, plus concrete IDs, each with `supportsEffort` and `supportedEffortLevels`), `account`
  (`apiProvider`, `subscriptionType`; treat account fields as private), `claude_code_version`, and
  `current_permission_mode` (present at runtime, missing from the TypeScript types). No model call.
- **One `system/init` and one `result` per prompt.** Prompts sent during a turn are queued.
  `priority: "now"` on a user message goes before queued prompts; the running tool call is not
  aborted, the current turn ends (its result can be empty), and the next turn reads the new prompt.
  Three prompts gave results in the order A, C (now), B.
- **Engine-started turns.** After a background subagent (`run_in_background`) finishes, the engine
  starts a new main turn itself (`init`, assistant text, `result`) with no prompt sent.
- **Task messages.** `system/task_started` (`task_type: "local_agent"`, `task_id`, `tool_use_id`,
  `subagent_type`, `spawn_depth`, `parent_task_id` when nested), `task_updated` (`patch.status`,
  `end_time`), `task_progress`, `task_notification`. Shell commands are tasks too (`local_bash`).
  `query.stopTask(id)` ends a task asynchronously (`task_updated` `killed`, then
  `task_notification` `stopped`). A SIGKILL of the engine process group right after `stopTask`
  leaves the command running, so wait for the notification. See
  [subagent monitoring](subagent-monitoring-and-correlation.md).
- **Shell commands run outside the engine's process group**: a `python3` command survived a group
  SIGKILL. Claude Code also blocks a standalone `sleep N`.
- **Context and limits.** `getContextUsage({detail:'summary'})` gives `model` (resolved ID),
  `totalTokens`, `maxTokens`, `rawMaxTokens` with no model call. The method named
  `usage_EXPERIMENTAL_MAY_CHANGE_DO_NOT_RELY_ON_THIS_API_YET` returns `rate_limits.five_hour` and
  `seven_day` (`utilization`, `resets_at`) and `subscription_type`; the SDK marks it experimental.
  A `rate_limit_event` message carries similar windows during a turn
  (see [OAuth usage](claude-code-oauth-usage.md)).
- **Resume.** `getSessionInfo(id)` returns `cwd`; `query({resume: id, cwd})` keeps the same session
  ID and appends to the same file.
- **Login and permissions.** Without a login the handshake succeeds; the first turn ends with an
  assistant message `error: authentication_failed` and a `result` with `subtype: "success"`,
  `is_error: true`, `result: "Not logged in · Please run /login"`. With `permissionMode: default`
  and no `canUseTool`, a tool needing approval is denied (`system/permission_denied`, error tool
  result) and the model continues; nothing hangs.
- **`/compact` as a prompt** gives `system/status compacting`, `system/compact_boundary`
  (`compact_metadata.trigger`, `pre_tokens`, `post_tokens`) and a result with 0 turns.
- **`spawnClaudeCodeProcess`** lets the host start the `claude` process itself (for its own
  process group); the returned child needs `stdin`, `stdout`, `kill`, `on('exit')`.
- **Undocumented**: env `CLAUDE_CODE_EMIT_SESSION_STATE_EVENTS=1` makes the engine emit
  `session_state_changed` (`running`, `idle`); it stays `running` while a background subagent
  works. Verified once.
- **Terms.** The SDK overview says third parties may not offer claude.ai login or its rate limits;
  use API keys. Own local use of one's own login worked technically; the terms reading is
  unsettled ([policy topic](subscription-oauth-third-party-policy.md)).

## From recall, not rechecked on 2026-10-18

- Python `client.interrupt()`, and the Python spelling `can_use_tool`.

## Monitoring

Cost, context, OpenTelemetry, and subagent tracking:
[observability and cost](agent-observability-and-cost.md),
[subagent monitoring](subagent-monitoring-and-correlation.md).

## Inference

- It is a local library, not a hosted HTTP API. To send prompts from another device, wrap it in
  your own server, or use [Managed Agents](managed-agents.md).
- Building your own CLI on it is easy. The SDK does the model calls, tools, edits, context, and
  sessions; the builder writes only the UI (output rendering, permission prompts, and any slash
  commands).
- Authentication: a product built on the SDK for other users needs an API key or a cloud
  provider, not a Free, Pro, or Max login (third-party report, 2026-10-22; see
  [subscription OAuth in third-party tools](subscription-oauth-third-party-policy.md)).

For Claude Code itself (terminal, IDE, cloud sessions), see
[Claude apps and surfaces](claude-apps-and-surfaces.md).
