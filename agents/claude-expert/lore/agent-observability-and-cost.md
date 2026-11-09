---
lore: 1
type: topic
summary: "Agent observability (2026-10-18): tokens, cost, context, budgets, and OpenTelemetry in the Agent SDK, Tool Runner, and Managed Agents; Claude Code cache TTL and cost from transcripts (2026-11-09); estimates versus billing."
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
  for each model. Each `modelUsage` entry has `costBasis` (v2.1.246+): `list`, `managed` (a
  `modelPricing` table), or `unknown`.
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

## Claude Code cache TTL

Checked 2026-11-09. Sources: https://code.claude.com/docs/en/prompt-caching,
https://code.claude.com/docs/en/agent-sdk/cost-tracking (documented), confirmed in a scan of
about 400 local transcripts (local test).

- Only the **main conversation within plan usage** gets the 1-hour cache TTL.
- Subagents, compaction, and title requests use the 5-minute TTL. The main conversation also
  drops to 5 minutes when it draws usage credits, and with an API key.
- Price each cache write from `usage.cache_creation.ephemeral_5m_input_tokens` and
  `ephemeral_1h_input_tokens`. Never infer the TTL from the login type.
- Fast mode on a subscription always draws usage credits (real money), so it also gets the
  5-minute TTL on the main conversation (inference from the two rules above).
- Prices per TTL: [models lineup](models-lineup.md#api-prices-with-cache-checked-2026-11-09).

## Claude Code cost from local transcripts

Local test, 2026-11-09, about 400 transcripts; record layout in
[local session observation](claude-code-local-session-observation.md). Recheck after a Claude
Code update.

- `total_cost_usd` and `modelUsage[].costUSD` are client-side estimates from the bundled price
  table (or `modelPricing`). They include subagents.
- The transcript **`cost-state` record** is written at normal process exit. It is cumulative
  across resumes, and it can be stale after the process is killed. It includes helper requests
  that the transcript does not show (title generation; away summaries in interactive CLI
  sessions).
- Assistant records repeat for each content block with the same message ID. The last record has
  the final `output_tokens`. The SDK placeholder warning above applies to streamed SDK messages,
  not to the transcript.
- Records with model `<synthetic>` have zero usage: skip them. `thinking_tokens` is a subset of
  output tokens; do not add it again.
- List-price arithmetic from transcript tokens (input, 5m and 1h cache writes, cache reads,
  output) reproduced `costUSD` exactly in 64 of 64 cases with exact token data.

**How to apply:** to rebuild Claude Code cost per session, sum the final usage of each message ID
from the main and subagent transcripts, price each cache write by its TTL field, and compare with
`cost-state`. A difference is usually helper requests or a stale `cost-state` after a kill.

## Authoritative billing

For all three: the Console Usage page and the Usage and Cost API
(https://platform.claude.com/docs/en/build-with-claude/usage-cost-api).

How context size affects cost: [long-context cost](long-context-cost.md).

**How to apply:** for a single dashboard across products, recommend OpenTelemetry from all three
into one backend (Langfuse, Datadog, Grafana, and so on). For a quick look without setup, point to
the Managed Agents Console viewer or the Agent SDK result message, and say that the SDK cost is an
estimate.
