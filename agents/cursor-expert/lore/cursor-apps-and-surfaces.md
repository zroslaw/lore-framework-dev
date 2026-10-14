---
lore: 1
type: area
summary: "Where each Cursor surface runs the agent and its tools, and what it can reach: editor and Agents Window, CLI, cloud agents, self-hosted machines, Remote Control, web, iOS, integrations, Bugbot, Grok Bot. Open for which-surface questions."
parent: lore-context.md
---

# Cursor apps and surfaces

Scope: the Cursor apps (desktop, CLI, web, iOS) and the agent types users reach through them. What
each extension does on each surface lives in [extension platform](extension-platform.md). Which
plan unlocks a surface lives in [plans and models](plans-and-models.md).

## Where an agent runs

My synthesis of the documented facts in the child topics (checked 2026-10-14):

| Agent loop | Tool calls run on | Surfaces | Reaches local files and programs |
|---|---|---|---|
| User's computer | User's computer | Editor, Agents Window local agents, CLI, JetBrains (ACP), SDK local runtime | Yes |
| Cursor cloud | Cursor-managed VM | Cloud agents, cloud subagents, Projects, Automations, Bugbot Autofix | No. Cloned repos, VM, secrets only |
| Cursor cloud | User's machine | My Machines worker, Team Pool worker, Remote Control | Yes. The machine must stay awake and online |
| Cursor cloud | Persistent cloud computer per account | Grok Bot | No. Its own cloud computer |

Model inference always runs on Cursor's hosted models. The SDK docs say it plainly: "local" means
a local agent loop and local files, not a local model (documented, SDK page). The Remote Control
docs say the loop "moves to the cloud" when a local session is handed off, so a local agent's loop
runs on the user's computer (documented, iOS page).

**The phone and the browser are clients.** They start, steer, and review cloud agents and Remote
Control sessions. They cannot run tools themselves.

## Ways to start or steer agent work

- **Desktop**: Agents Window or editor; pick Local, Worktree, Cloud, or a remote machine. Move a
  local chat to the cloud ("Move to Cloud") or back.
- **CLI**: `agent`; prefix a message with `&` to hand it to a cloud agent.
- **Web**: cursor.com/agents on any device.
- **iOS**: Cursor for iOS; Remote Control for local sessions.
- **Chat and issue tools**: `@Cursor` in Slack, Microsoft Teams, Linear, Jira, Notion; `@cursor`
  on GitHub PRs and issues and on Bitbucket PRs ([integrations](integrations-and-public-api.md)).
- **Code**: Cloud Agents API, TypeScript and Python SDKs.
- **Events and schedules**: Automations ([Bugbot and Automations](bugbot-and-automations.md)).

## Children

- [Editor, Agents Window, and agent modes](editor-agents-window-and-modes.md) — the desktop app,
  modes, Tab, subagents, Projects, side chats, canvases.
- [Cursor CLI](cursor-cli.md) — the `agent` command, headless mode, ACP, MCP and plugin commands.
- [Cloud agents](cloud-agents.md) — VMs, environments, triggers, subscriptions, hooks, billing.
- [Self-hosted machines and Remote Control](self-hosted-machines-and-remote-control.md) — tool
  calls on the user's own machine.
- [Mobile and web](mobile-and-web.md) — Cursor for iOS, Android PWA, cursor.com/agents.
- [Integrations and public API](integrations-and-public-api.md) — Slack, GitHub, Linear, Jira,
  Notion, JetBrains, Xcode, APIs, SDKs, Origin.
- [Bugbot and Automations](bugbot-and-automations.md) — PR review and event-driven cloud agents.
- [Grok Bot](grok-bot.md) — the general knowledge-work agent product.
