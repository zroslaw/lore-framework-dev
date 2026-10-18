---
lore: 1
type: topic
summary: "Claude Agent SDK, formerly Claude Code SDK (2026-10-18): Claude Code as a Python or TypeScript library you host; built-in tools and features, recalled multi-turn and resume APIs, and what a builder still writes."
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
  the docs page above for code questions.

## From recall, not rechecked on 2026-10-18

Verify these names at the docs before relying on them:

- Multi-turn use like the CLI: Python `ClaudeSDKClient` (`query()`, `receive_response()`,
  `interrupt()`); TypeScript `query()` with streaming input (an async iterable of messages).
- Resume a past session by ID with the `resume` option.
- A `can_use_tool` callback for custom permission prompts.

## Inference

- It is a local library, not a hosted HTTP API. To send prompts from another device, wrap it in
  your own server, or use [Managed Agents](managed-agents.md).
- Building your own CLI on it is easy. The SDK does the model calls, tools, edits, context, and
  sessions; the builder writes only the UI (output rendering, permission prompts, and any slash
  commands).

For Claude Code itself (terminal, IDE, cloud sessions), see
[Claude apps and surfaces](claude-apps-and-surfaces.md).
