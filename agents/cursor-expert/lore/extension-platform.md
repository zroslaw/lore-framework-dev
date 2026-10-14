---
lore: 1
type: area
summary: "Cursor's extension model: the Customize page, components (plugins, rules, skills, subagents, commands, hooks, MCP), scopes, what syncs to the account, and what reaches cloud agents. Open for any what-loads-where or how-to-install question."
parent: lore-context.md
---

# Extension platform

Scope: how users and teams extend Cursor's agent — MCP, plugins and marketplaces, skills,
subagents, commands, hooks — and the admin controls over them. Rules and AGENTS.md live in
[memory and personalization](memory-and-personalization.md). Checked 2026-10-14 against
cursor.com docs (documented) unless a line says otherwise.

## Customize page

- **Customize** (sidebar in the desktop app) is one place to browse the **Cursor Marketplace**,
  install plugins, skills, and MCP servers, and turn rules, skills, subagents, commands, and hooks
  on or off. Filter by user, workspace, or team scope. It shows a team leaderboard of popular
  extensions and plugin **canvases** (shared setup templates).
- Community plugins and MCP servers: cursor.directory (third-party site; the docs point to it).

## Components and where they live

| Component | Project location | User location | Team distribution |
|---|---|---|---|
| Rules | `.cursor/rules/*.mdc`, `AGENTS.md`, `CLAUDE.md` | User Rules (account) or `~/.cursor/rules` (machine) | Team Rules (dashboard) |
| Skills | `.cursor/skills/`, `.agents/skills/` (also `.claude/`, `.codex/`) | `~/.cursor/skills/`, `~/.agents/skills/` | Publish to the team marketplace |
| Subagents | `.cursor/agents/` (also `.claude/`, `.codex/`) | `~/.cursor/agents/` | Plugins |
| Commands | `.cursor/commands/` | user-level commands | Team commands, plugins |
| Hooks | `.cursor/hooks.json` | `~/.cursor/hooks.json` | Team hooks (Enterprise), MDM |
| MCP | `.cursor/mcp.json` | `~/.cursor/mcp.json` | Team MCP servers, team marketplace |
| Plugins | Install at project scope | Install at user scope, `~/.cursor/plugins/local` | Team marketplaces |

## What follows the account, and what stays on the machine

- **Syncs**: User Rules set in Settings, Team Rules, installed marketplace plugins (lore-architect
  observed in August 2026 that a plugin enable syncs to the user's other machines and CLI
  sessions), personal and team cloud MCP servers configured at cursor.com/agents.
- **Stays local**: `~/.cursor/rules` files, `~/.cursor/skills/` (until synced for cloud agents),
  `~/.agents/skills/`, `~/.cursor/hooks.json`, `~/.cursor/mcp.json`, local plugins.
- **Cloud agents** get project files from the repo, user and team rules, synced personal skills,
  team and personal cloud MCP servers, and repo hooks (plus team hooks on Enterprise). They never
  see `~/.cursor` on the user's machine, and they do not read the repo's `.cursor/mcp.json`
  either (forum staff, 2026-04-17).

## Children

- [MCP in Cursor](mcp-in-cursor.md) — config files, transports, auth, features, approvals.
- [Remote MCP by surface](remote-mcp-by-surface.md) — the per-surface matrix for a remote MCP
  server: editor, CLI, cloud, web, iOS, self-hosted, Grok Bot, SDK.
- [Plugins and marketplaces](plugins-and-marketplaces.md) — formats, marketplace review, team
  marketplaces, install scopes, local plugins.
- [Skills, subagents, and commands](skills-subagents-and-commands.md) — locations, formats,
  built-in skills, cloud sync, Claude and Codex compatibility.
- [Hooks](hooks.md) — events, sources, cloud support, Claude Code hook compatibility.
- [Admin and enterprise controls](admin-and-enterprise-controls.md) — MCP allowlist, model access,
  Run Mode policy, privacy, identity, and audit.

Sources: https://cursor.com/docs/customize-cursor.md ; https://cursor.com/docs/plugins.md ;
https://cursor.com/docs/skills.md ; https://cursor.com/docs/subagents.md ; https://cursor.com/docs/hooks.md ;
https://cursor.com/docs/mcp.md ; https://cursor.com/help/customization/rules.md
