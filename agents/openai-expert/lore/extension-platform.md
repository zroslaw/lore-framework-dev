---
lore: 1
type: area
summary: "OpenAI's extension model: plugins (skills, MCP servers, UI, hooks) in one directory for ChatGPT and Codex, custom MCP servers, Codex config, custom GPTs, admin controls. Open for any what-loads-where or how-to-install question."
parent: lore-context.md
---

# Extension platform

Scope: how users and orgs extend ChatGPT and Codex — plugins, skills, MCP servers (hosted and
local), Codex configuration files, custom GPTs, the directory, and admin controls. Checked
2026-10-14 against OpenAI docs (documented). This area changes every few weeks; recheck it.

## Vocabulary (2026)

- A **plugin** is the installable unit. It can hold **skills** (`SKILL.md` folders, open Agent
  Skills standard), **MCP servers** (remote or local), optional **UI** (MCP Apps standard plus
  OpenAI extensions), **browser extensions**, and **lifecycle hooks** (Codex runtime only).
- **App** and **MCP server** mean the same connected integration in the admin docs. "Connectors"
  is the older word. Plugins launched 2026-03-25 (Codex first) and now replace custom GPTs.
- **One universal plugin directory** serves ChatGPT and Codex. A public plugin is published once
  and is discoverable from every supported surface.

## Where plugins work

| Surface | Plugins | Notes |
|---|---|---|
| ChatGPT web, Chat and Work | Yes | Hosted tools only; no local config |
| ChatGPT desktop, Chat and Work | Yes | Desktop-only plugins (local MCP) only in local threads |
| ChatGPT mobile, Chat and Work | Yes | No desktop-only plugins |
| Codex in the desktop app | Yes | Also local marketplaces and `config.toml` MCP |
| Codex CLI | Yes, `/plugins` browser | Installs from configured marketplaces |
| IDE extension | **No** | MCP servers and skills still work |

Invocation: `@` mentions in ChatGPT; `$` mentions for skills in Codex. Bundled skills appear in new
chats after install.

## Children

- [Remote MCP per surface](remote-mcp-per-surface.md) — transport, auth, MCP features, plans, and
  confirmations for ChatGPT web, desktop, mobile, Codex CLI, and Codex Cloud. The most important
  topic in this area.
- [Apps and connectors](apps-and-connectors.md) — what an app is, directory vs custom, remote vs
  local, personal vs workspace accounts, synced data.
- [Plugin install and component support](plugin-install-and-component-support.md) — install paths
  per surface and the per-surface table for skills, MCP, hooks, and UI.
- [Plugins: packaging and publishing](plugins-packaging-and-publishing.md) — manifest formats,
  marketplaces, Claude Code compatibility, submission, desktop-only plugins.
- [Codex configuration and extensibility](codex-configuration-and-extensibility.md) — `AGENTS.md`,
  skill locations, `config.toml`, hooks, subagents, and import from Claude Code or Cursor.
- [Custom GPTs and their retirement](custom-gpts-and-retirement.md) — the GPT-to-plugin migration
  and its dates.
- [Admin and org controls](admin-and-org-controls.md) — workspace plugin controls, RBAC, Agent
  Security, managed configuration.

Sources: https://learn.chatgpt.com/docs/plugins ; https://learn.chatgpt.com/docs/skills-and-plugins ;
https://developers.openai.com/plugins/concepts/plugins ;
https://learn.chatgpt.com/docs/enterprise/apps-and-connectors
