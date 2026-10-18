---
lore: 1
type: area
summary: "Managed Agents (beta, 2026-10-18): Anthropic-hosted agent loop with a sandbox per session; object model, features, typical uses, and when to pick it. Open for any hosted-agent question; children cover sandboxes, data, and pricing."
parent: lore/developer-platform.md
---

# Managed Agents

Option 3 of the [four ways to build an agent](developer-platform.md). Checked 2026-10-18.
Sources: the `claude-api` skill bundled with Claude Code 2.1.302 (`shared/managed-agents-*.md`,
the quickstart templates) and https://platform.claude.com/docs/en/managed-agents/overview.
**Documented** unless a line says otherwise.

## What it is

Anthropic runs the agent loop and hosts a sandbox container for each session. Builders use it
through a REST API with the beta header `managed-agents-2026-04-01`; the SDK sets the header on
`client.beta.*`. Public beta since 2026-04-08 (third-party report).

## Object model

- **Agent** — a saved, versioned configuration (model, system prompt, tools). Create it once.
- **Session** — one per job. It references an agent and an
  [environment](managed-agents-environments-and-data.md) and streams events. You send messages,
  tool results, approvals, and interrupts into it.
- Recommended practice: keep agents and environments as files and sync them with `ant apply`.

## Features

- Skills and MCP servers.
- **Vaults** — credentials substituted at egress; the sandbox never sees them.
- **Scheduled deployments** — cron.
- **Outcomes** — a grader iterates the agent against a rubric.
- **Multiagent** — a roster of up to 25 child threads; dynamic workflows for bigger jobs.
- **Memory stores** — persist across sessions.
- **Permission policies** — `always_allow`, `always_ask`, `auto`.
- **Session budgets** in USD ([pricing](managed-agents-pricing-and-alternatives.md)).

## Typical uses

Anthropic's Console quickstart templates: bug-hunter, performance-tuner,
support-to-eng-escalator (Intercom → repro → Jira), incident-commander (Sentry → Linear → Slack
war room), sprint-retro-facilitator, data-analyst, deep-researcher, field-monitor (weekly
brief), contract-tracker (Box → Asana), structured-extractor, support-agent, watchlist-scanner,
explainer-video-maker.

## When to pick it

Pick it when the job runs long or must continue with the user's laptop off, runs on a schedule,
needs a code or file sandbox, needs hidden credentials, fans out to many agents, or must pass a
quality check. For short jobs with the builder's own tools inside an app, use
[Tool Runner](tool-runner.md). For large data or a custom image, see the sandbox limits first.

## Children

- [Environments, sandboxes, and data](managed-agents-environments-and-data.md) — the cloud image
  and its limits (8 GB RAM, 10 GB disk, no custom image), self-hosted sandboxes, and how files,
  repos, and memory get in.
- [Pricing, adoption, and alternatives](managed-agents-pricing-and-alternatives.md) — session
  fees, budgets, early users, and other vendors' hosted-agent prices.
