---
lore: 1
type: topic
summary: "Cursor integrations and programmatic access (2026-10-14): Slack, Microsoft Teams, GitHub, GitLab, Bitbucket, Azure DevOps, Linear, Jira, Notion, JetBrains via ACP, Xcode MCP; Cloud Agents API, SDKs, admin APIs, and Origin."
parent: lore/cursor-apps-and-surfaces.md
---

# Integrations and public API

Checked 2026-10-14. Documented unless a line says otherwise. Most integrations are front doors to
[cloud agents](cloud-agents.md): setup asks for a repository provider, usage-based (on-demand)
pricing, and privacy settings.

## Chat and issue tools

| Integration | How a user starts work | Notes |
|---|---|---|
| Slack | `@Cursor <prompt>` in a channel or thread | Options `repo=`, `env=`, `branch=`, `model=`, `autopr=`, `worker=`, `pool=`, `channel=`; channel and team default pools; follow-ups in the thread |
| Microsoft Teams | `@Cursor <prompt>` | Installed from the Microsoft Marketplace; `repo`, `env`, `branch`, `model` options |
| GitHub | Comment `@cursor` on a PR or issue | The GitHub app also powers Bugbot; GitHub Enterprise Server supported. The My Machines page uses the handle `@cursoragent` |
| GitLab, Bitbucket Cloud, Azure DevOps | Repo provider for cloud agents and Bugbot; `@cursor` on Bitbucket PRs | GitLab self-hosted supported |
| Linear | Assign the issue to Cursor, or `@Cursor` in a comment | `[key=value]` options and parent-child labels |
| Jira | Assign a work item to Cursor or mention `@Cursor` | Jira Cloud with Rovo; **Teams and Enterprise only**; service-account or per-user auth |
| Notion | Notion Agents → New Agent → Cursor, then mention or assign | Beta; Notion Business or Enterprise; built on the Cursor SDK with a personal API key |

## IDEs and tools

- **JetBrains**: Cursor's agent inside IntelliJ, PyCharm, WebStorm and others through ACP, from
  the AI Assistant plugin's ACP registry. Needs a paid Cursor plan.
- **Xcode 26.3+**: Apple's built-in MCP server (`xcrun mcpbridge`, stdio, 20 tools) connects to
  Cursor like any MCP server. Needs a paid plan and a running Xcode.
- **Deeplinks**: `cursor://anysphere.cursor-deeplink/...` or `https://cursor.com/link/...` for
  prompts, commands, rules, and MCP installs.

## Programmatic access

| API or SDK | What it does | Availability |
|---|---|---|
| Cloud Agents API (`api.cursor.com/v1/...`) | Create agents and runs, stream, artifacts, environments, secrets, workers, pools, webhooks; inline `mcpServers` (max 50) | Beta, all plans |
| TypeScript SDK (`@cursor/sdk`, Node 22.13+) and Python SDK | Run Cursor's agent locally or in the cloud from code; same pricing and Privacy Mode as the IDE | All users (Start excludes the SDK) |
| SDK Bridge | Connect/protobuf protocol and binaries for other languages | All users |
| Admin, Analytics, AI Code Tracking, Bugbot APIs | Team members, usage, spend, audit logs, model access, metrics | Enterprise teams |
| Origin API | Origin repos, commits, checks, PRs, apps | Early beta |

- Auth: API keys from Dashboard → API Keys (`crsr_...`); Basic or Bearer. Default rate limit is
  20 requests per minute unless an endpoint says otherwise.
- The APIs and SDKs run agent workflows. They are not a raw chat-completions API.

## Origin

- Cursor's git forge in early beta: create repos, push and pull with git, mirror GitHub repos,
  PRs and stacks, code search at cursor.com/codebase, Origin Apps (App Marketplace, changelog
  2026-10-13), and an `origin` CLI.
- Plans: Start, Pro, Pro+, Ultra, Teams, Enterprise; not free; not with Legacy Privacy Mode.
- Origin MCP: `https://api.origin.cursor.com/mcp` (and `/mcp/readonly`), stateless streamable
  HTTP, tools only. Available only in Cursor and Grok Bot for now.

Sources: https://cursor.com/docs/integrations/slack.md ; https://cursor.com/docs/integrations/microsoft-teams.md ;
https://cursor.com/docs/integrations/github.md ; https://cursor.com/docs/integrations/linear.md ;
https://cursor.com/docs/integrations/jira.md ; https://cursor.com/docs/integrations/notion.md ;
https://cursor.com/docs/integrations/jetbrains.md ; https://cursor.com/docs/integrations/xcode.md ;
https://cursor.com/docs/reference/deeplinks.md ; https://cursor.com/docs/api.md ;
https://cursor.com/docs/cloud-agent/api/endpoints.md ; https://cursor.com/docs/sdk/typescript.md ;
https://cursor.com/docs/sdk/bridge.md ; https://cursor.com/docs/origin.md ; https://cursor.com/docs/api/origin/mcp.md ;
https://cursor.com/docs/models-and-pricing.md ; https://cursor.com/changelog
