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
