---
lore: 1
type: topic
summary: "Cursor Cloud Agents as of 2026-10-14: isolated VMs, environments and Builds, multi-repo, start from scratch, ways to start one, subscriptions, hooks, skills, computer use, sharing, Privacy Mode, billing. Open for cloud-agent questions."
parent: lore/cursor-apps-and-surfaces.md
---

# Cloud agents

Checked 2026-10-14. Documented unless a line says otherwise. Cloud Agents were formerly called
Background Agents.

## What they are

- Each cloud agent runs in its own isolated VM with a full desktop: cloned repos, installed
  dependencies, secrets, startup commands, and network access. It works on a separate branch and
  pushes changes, usually as a PR. It keeps working with the user's computer off.
- Computer use: the agent drives the VM desktop and browser, and attaches screenshots, videos, and
  logs to the PR. The user can take over the remote desktop and hand it back.
- Run as many as needed in parallel. A curated set of models; the user picks the context size.
- Requirements: a paid plan; a connected GitHub, GitLab, Bitbucket Cloud, or Azure DevOps account
  with read-write access; Privacy Mode (not Privacy Mode Legacy), because cloud agents store code
  while they run.

## Environments

- Set up by an agent (recommended, under 10 minutes), by a saved snapshot, or by a Dockerfile in
  `.cursor/environment.json`. **Builds** prepare each environment in the background (blog
  2026-08-13: starts 3x faster).
- Resolution order: `.cursor/environment.json` in the repo → personal saved environment → team
  saved environment.
- **Multi-repo environments**: select several repos; Cursor clones each into the VM.
- **Start from scratch**: no repo; Cursor makes a draft Origin repository (paid plan and Origin).
- Cloud agents read `AGENTS.md`; the docs suggest a "Cursor Cloud specific instructions" section.
- Secrets: dashboard Secrets tab, team or environment scoped; injected at start. OIDC tokens and an
  agent metadata API come from a local socket (`http://cursor-agent/v1/...`).

## Ways to start one

Desktop (Cloud in the agent picker, or `/in-cloud` for a cloud subagent), cursor.com/agents, Cursor
for iOS, the CLI (`&` prefix), Slack, Microsoft Teams, GitHub (`@cursor` on PRs and issues),
Bitbucket PRs, Linear, Jira, Notion, the Cloud Agents API and SDKs, and Automations. Agents started
anywhere appear on every surface.

## Behavior in the cloud

- **No approvals**: Run Modes apply only to local agents; a cloud agent never asks.
- **Subscriptions**: the agent ends its turn and wakes on GitHub PR or CI events, Slack replies,
  Linear issue changes, or timers (`/subscribe`, `/loop`). Max 180 days. Not for service-account
  agents.
- **CI autofix**: fixes GitHub Actions failures on PRs it created (Teams only for now; max 10
  follow-ups; `@cursor autofix off`).
- **Hooks**: command hooks from the repo's `.cursor/hooks.json`; on Enterprise also team and
  managed hooks. No user hooks, no prompt hooks, no `sessionStart`/`sessionEnd`, no MCP hooks
  ([hooks](hooks.md)).
- **Skills and rules**: project skills and rules from the repo, user rules, team rules, and
  personal skills only after **Sync Skills for Cloud Agents**. Plugins: a release note says a
  plugin slash command in a follow-up now works "even if that plugin wasn't selected when the agent
  started" because the agent installs it first. Inference: a cloud agent loads a selected set of
  plugins at start. The docs have no plugin support table for cloud agents.
- **MCP**: team and personal cloud MCP servers, HTTP proxied by Cursor
  ([remote MCP by surface](remote-mcp-by-surface.md)). Only servers set up in the dashboard (or
  inline in the API) load; the runtime does not read the repo's `.cursor/mcp.json` (Cursor staff,
  forum, 2026-04-17). A built-in **Cursor Cloud MCP** gives run diagnostics: transcripts, events,
  environment, Builds, snapshots.
- **Sharing**: teammates with repo access can open an agent read-only; admins can allow team
  follow-ups.

## Billing

Charged at API rates of the selected model, from the plan's pools then on-demand. A spend limit is
set at first use. Automations always use the model's maximum context.

Sources: https://cursor.com/docs/cloud-agent.md ; https://cursor.com/docs/cloud-agent/capabilities.md ;
https://cursor.com/docs/cloud-agent/setup.md ; https://cursor.com/docs/cloud-agent/best-practices.md ;
https://cursor.com/help/ai-features/cloud-agents.md ; https://cursor.com/docs/hooks.md ;
https://cursor.com/docs/agent/security/run-modes.md ; https://cursor.com/docs/release-notes.md ;
https://cursor.com/blog/builds ;
https://forum.cursor.com/t/how-to-use-mcps-with-self-hosted-agents/157677 (forum, staff, 2026-04-17)
