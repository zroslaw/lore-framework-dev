---
lore: 1
type: topic
summary: "Tool Runner (2026-10-18): the beta helper in the Anthropic API SDKs that runs the tool loop for your own tools; entry points, per-turn hooks, what it lacks, and typical uses."
parent: lore/developer-platform.md
---

# Tool Runner

**Documented** — the `claude-api` skill bundled with Claude Code 2.1.302, checked 2026-10-18.
Option 2 of the [four ways to build an agent](developer-platform.md).

## What it is

A helper in the normal Anthropic API SDK. It runs the loop "send request → run tool → send result
→ repeat" for tools that you define. It does nothing else. Beta.

- **Python:** decorate functions with `@beta_tool`, call `client.beta.messages.tool_runner(...)`,
  then `runner.until_done()`.
- **TypeScript:** define tools with `betaZodTool`, call `client.beta.messages.toolRunner(...)`.
- Also in the Go, Java, Ruby, C#, and PHP SDKs.
- It takes the normal Messages API parameters, including `system`. It adds no system prompt of
  its own.
- **Per-turn hooks:** approval gates, logging, error interception, result modification, retries,
  streaming, and compaction.

## What it does not have

No built-in tools, no file access, no sandbox, no Claude Code system prompt, no CLAUDE.md, no
skills, no subagents, no permission prompts, no saved sessions. For those, use the
[Agent SDK](agent-sdk.md) or [Managed Agents](managed-agents.md).

## Typical uses

- A support bot that calls `get_order` and `refund_order`.
- A data assistant over `run_sql` and `search_docs`.
- Booking or shopping helpers.
- Internal operations bots (tickets, Slack, status pages).
- Small automations in which Claude picks the order of your functions.

It is a good fit when Claude must do only what your tools allow.
