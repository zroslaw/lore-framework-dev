---
lore: 1
type: topic
summary: "Observability for Claude agents (2026-10-18): token, cost, and context tracking, budgets, and OpenTelemetry in the Agent SDK, Tool Runner, and Managed Agents; which numbers are estimates and where real billing lives."
parent: lore/developer-platform.md
---

# Observability, usage, and cost for Claude agents

**Documented**, checked 2026-10-18, unless a line says otherwise. Sources:
https://code.claude.com/docs/en/agent-sdk/cost-tracking,
https://code.claude.com/docs/en/agent-sdk/observability,
https://code.claude.com/docs/en/agent-sdk/typescript,
https://platform.claude.com/docs/en/manage-claude/opentelemetry, and the `claude-api` skill
bundled with Claude Code 2.1.302 (`shared/opentelemetry.md`, `shared/managed-agents-events.md`,
`shared/managed-agents-core.md`).

Short answer: all three have it. Managed Agents gives the most with no setup (Console session
viewer). The Agent SDK gives good built-in numbers and OpenTelemetry export. The Tool Runner
gives raw `usage` per response plus the API SDK's OpenTelemetry tracing. For subagent tracking,
see [subagent monitoring](subagent-monitoring-and-correlation.md).

## Agent SDK

- **Result message** of each `query()` (`SDKResultMessage` / Python `ResultMessage`):
  `total_cost_usd`, `usage`, and `modelUsage` (Python `model_usage`) with tokens and `costUSD`
  for each model. Each `modelUsage` entry has `costBasis`: `list`, `managed` (a `modelPricing`
  table), or `unknown`.
- **The cost is a client-side estimate** from a price table bundled at build time. It can drift
  from the bill (price changes, unknown models, billing rules). Do not bill end users from it.
  The SDK does model data-residency pricing (`inference_geo: "us"` → ×1.1 on tokens).
- **Scope traps:**
  - `usage` excludes subagents; `total_cost_usd` and `modelUsage` include them. Use `modelUsage`
    for whole-tree token accounting.
  - Per-step usage is on each assistant message (`message.message.usage`; Python
    `message.usage`). Parallel tool calls share one message ID: count each ID once.
  - Per-step `output_tokens` is a placeholder from `message_start`. Read output tokens from the
    result message.
  - A resumed session's result already includes the earlier spend: read the latest result, do
    not sum. Independent `query()` calls: sum them. Streaming input mode: one result per turn;
    `total_cost_usd` is a running total; `/clear`, `/reset`, `/new` restart it.
  - After a session crash, the final `error_during_execution` result can carry zeroed cost
    fields.
- **Spend cap:** `maxBudgetUsd` (Python `max_budget_usd`), on the client estimate; result
  subtype `error_max_budget_usd`. `taskBudget` (alpha) is an API-side token budget.
- **Context:** `Query.getContextUsage({ detail })` (TypeScript) returns the same data as
  `/context`: `totalTokens`, `maxTokens`, `percentage`, `categories[]`, `autoCompactThreshold`,
  `messageBreakdown`, and per-item tokens for MCP tools, agents, memory files, and skills. Sending
  `/context` as a prompt attaches `context_usage` to the reply (v0.3.232+). Python equivalent
  not checked.
- **OpenTelemetry:** the SDK emits nothing itself; the Claude Code CLI child process exports.
  - Enable with `CLAUDE_CODE_ENABLE_TELEMETRY=1` and per-signal exporters:
    `OTEL_METRICS_EXPORTER` (tokens, cost, sessions, lines of code, tool decisions),
    `OTEL_LOGS_EXPORTER` (prompt, API request, API error, tool result events),
    `OTEL_TRACES_EXPORTER` plus `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` (traces, beta).
  - Spans: `claude_code.interaction` → `claude_code.llm_request`, `claude_code.tool` (with
    `tool.blocked_on_user` and `tool.execution`), `claude_code.hook`. Spans carry `session.id`.
  - The SDK injects `TRACEPARENT` so agent runs nest in the application's own trace.
  - Content is off by default; opt in with `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`,
    `OTEL_LOG_TOOL_CONTENT`, `OTEL_LOG_RAW_API_BODIES`.
  - Traps: never use the `console` exporter (stdout is the SDK message channel); export fails
    silently unless `CLAUDE_CODE_OTEL_DIAG_STDERR=1`; short runs can drop data, so lower the
    export intervals. In TypeScript, `options.env` replaces the environment: spread
    `process.env`.
  - Tag agents with `OTEL_SERVICE_NAME` and `OTEL_RESOURCE_ATTRIBUTES` (for example
    `enduser.id`, `tenant.id`, percent-encoded) for per-user audit trails.

## Tool Runner and the Claude API

- Every response carries `usage` (input, output, cache read, cache write). The builder sums and
  prices it.
- Context: `count_tokens` before sending; compaction and task budgets (beta) for long loops.
- **OpenTelemetry (beta), two independent sources:**
  - **SDK tracing** — spans from the application's process, set up in code; covers the client
    tools a tool runner runs and self-hosted sandbox tools. Works on every cloud platform.
  - **API tracing** — server-side spans sent to a destination an org admin adds in the Console or
    the Admin API; no code change; covers each model request, Managed Agents turns, and server
    and MCP connector tools. Claude API and Claude Platform on AWS only.
  - Default content mode is metadata only; full content is opt-in. Attributes follow the
    OpenTelemetry GenAI conventions (`gen_ai.*`).

## Managed Agents

- **Console session viewer** (no setup; Developers and Admins): session list with tokens and
  cost, a timeline with one lane per thread, the transcript, per-tool call counts, failures and
  median time, and per-thread context size and cost.
- **In code:** the session object's `usage` and the `session.usage` event: token totals,
  `list_cost`, `active_seconds`, web-search counts, budget echo. `span.model_request_end` carries
  `model_usage` per model request. `agent.thread_context_compacted` carries
  `pre_compaction_tokens`.
- Session budgets in USD pause the session at the cap
  ([pricing](managed-agents-pricing-and-alternatives.md)). Webhooks report state changes.

## Authoritative billing

For all three: the Console Usage page and the Usage and Cost API
(https://platform.claude.com/docs/en/build-with-claude/usage-cost-api).

How context size affects cost: [long-context cost](long-context-cost.md).

**How to apply:** for a single dashboard across products, recommend OpenTelemetry from all three
into one backend (Langfuse, Datadog, Grafana, and so on). For a quick look without setup, point to
the Managed Agents Console viewer or the Agent SDK result message, and say that the SDK cost is an
estimate.
