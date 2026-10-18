---
lore: 1
type: area
summary: "Claude developer platform for agent builders: the four ways to build an agent (manual loop, Tool Runner, Managed Agents, Agent SDK), how to pick one, and where to check API facts. Open for any build-an-agent question."
parent: lore-context.md
---

# Developer platform

Scope: building agents on the Claude API — the Messages API with a manual loop, the Tool Runner
helper, Managed Agents, and the Claude Agent SDK. Per-token model prices live in
[models lineup](models-lineup.md); consumer plans live in [plans and models](plans-and-models.md).
Facts here were checked on 2026-10-18 unless a line says otherwise.

## Four ways to build an agent

**Documented** — the `claude-api` skill bundled with Claude Code 2.1.302 (SKILL.md § "Building an
Agent: Four Approaches"), checked 2026-10-18.

Two questions separate the options: who supplies the **harness** (the agent loop and context
management), and who supplies the **deployment** (the infrastructure it runs on).

| # | Option | Harness | Deployment | Tools |
|---|---|---|---|---|
| 1 | Claude API, manual loop | you | you | only yours |
| 2 | Claude API, [Tool Runner](tool-runner.md) | SDK (loop only) | you | only yours |
| 3 | [Managed Agents](managed-agents.md) (beta) | Anthropic | Anthropic (one sandbox per session) | sandbox bash, files, code + skills + MCP + yours |
| 4 | [Claude Agent SDK](agent-sdk.md) | SDK (full Claude Code harness) | you | built-in Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch + MCP + subagents |

- Only Managed Agents gives a managed deployment. Options 1, 2, and 4 run where your code runs.
- Tool Runner and the Agent SDK are different packages, and people confuse them. Tool Runner is a
  helper inside the normal `anthropic` / `@anthropic-ai/sdk` package. The Agent SDK is the
  separate `claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk` package.

## How to pick

When someone asks "how do I build an agent with Claude", show the table first, then pick:

- Only the builder's own tools, inside an app → **Tool Runner** ("a loop with your tools only").
- A file and shell agent on the builder's own infrastructure → **Agent SDK** ("a Claude Code
  session in code").
- Hosted, scheduled, long-running, or sandboxed work, or work that must continue with the
  user's laptop off → **Managed Agents** ("a hosted agent with a sandbox that you reach over a web
  API").

These short framings worked well with users.

## How I check facts in this area

Observed in Claude Code 2.1.302 on 2026-10-18 (operational lesson):

1. **The bundled `claude-api` skill first.** Claude Code ships it; load it with the Skill tool,
   or find its files with `find /private/tmp -path '*bundled-skills*claude-api/SKILL.md'` (on
   macOS it was under `/private/tmp/claude-<uid>/bundled-skills/<version>/<hash>/claude-api/`;
   the path changes with each Claude Code version). Its `shared/` folder holds dated reference
   files: `managed-agents-*.md` (core, environments, self-hosted sandboxes, tools, memory,
   multiagent, outcomes, scheduled deployments, API reference), 13 quickstart templates in
   `managed-agents-quickstarts/`, model tables with prices (the cache date is in SKILL.md), and
   `live-sources.md` with the official doc URLs. `grep` over `shared/` answered most questions
   fast.
2. **platform.claude.com for its gaps and for every price.** The skill did not have the cloud
   sandbox specs or the Files API limits. Fetch
   https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference and
   https://platform.claude.com/docs/en/build-with-claude/files for those.
3. **code.claude.com for the Agent SDK.** The skill does not generate Agent SDK code. Use
   https://code.claude.com/docs/en/agent-sdk; find its pages in
   https://code.claude.com/docs/llms.txt. The skill's `shared/opentelemetry.md` also says that
   Agent SDK and Claude Code monitoring live on code.claude.com, not in the skill.

## Children

- [Tool Runner](tool-runner.md) — the SDK helper that runs the tool loop for your own tools; what
  it has, what it lacks, and typical uses.
- [Claude Agent SDK](agent-sdk.md) — Claude Code as a library: packages, built-in features, and
  what the builder still writes.
- [Managed Agents](managed-agents.md) — hosted agents with a sandbox: object model, features,
  use cases, environments, data limits, and pricing.
- [Observability and cost](agent-observability-and-cost.md) — token, cost, and context tracking,
  budgets, and OpenTelemetry for all three products; which numbers are estimates.
- [Subagent monitoring](subagent-monitoring-and-correlation.md) — how to see and correlate
  subagents with their session, and which data an API exposes.

Boundary: the OpenAI Agents SDK and OpenAI's hosted agents belong to openai-expert. Compare only
at the level a Claude answer needs.
