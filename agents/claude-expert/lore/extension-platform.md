---
lore: 1
type: area
summary: "Claude's extension model: connectors, skills, and plugins, the Customize page, one-way account sync to Claude Code, and skills in chat. Open for any what-loads-where or how-to-install question."
parent: lore-context.md
---

# Extension platform

Scope: how users and orgs extend Claude — MCP connectors, skills, plugins, the directory, and the
admin controls over them. Checked 2026-10-13 against Anthropic's docs (documented). Recheck before
relying on it; this area changes often.

## The three extension types

- **MCP connectors** give Claude access to a tool or data source. Remote vs local decides where
  they work: [connectors](connectors.md).
- **Skills** are a `SKILL.md` with instructions plus optional scripts and reference files. Claude
  loads a skill when a task matches its description. Skills follow the open Agent Skills
  specification (agentskills.io), so a skill also works in other tools that adopt it.
- **Plugins** are installable packages of skills, commands, MCP connectors, and agents, optionally
  with hooks. What each component does on each surface:
  [plugins](plugins-install-and-surface-support.md).

## Customize and account sync

- **Customize** (claude.ai/customize and the desktop app) holds Skills, Connectors, and Plugins,
  each with a Discover tab. There is no Customize page on mobile
  ([mobile app](claude-mobile-app.md)).
- Installs from Customize attach to the account (per org). They show in chat on web, desktop, and
  mobile, load in Cowork, and arrive in Claude Code as "synced plugins" at the next session
  (`/reload-plugins`).
- **Sync is one-way.** A plugin installed from the Claude Code CLI stays on that machine; it does
  not appear in the account, chat, Cowork, or mobile.

## Skills in chat

- Skills in chat run in Claude's code sandbox, not on the user's computer.
- They need a Pro plan or higher and **Settings > Capabilities > Code execution and file
  creation** turned on.
- Invocation: automatic when the task matches, or type `/` in the message box (documented for web
  and desktop).

## Children

- [Connectors](connectors.md) — remote vs local, directory vs custom, where each works, and
  custom connector setup (plans, sign-in, network reach, MCP features).
- [Plugins: install paths and surface support](plugins-install-and-surface-support.md) — install
  paths, limits, and the per-surface component table.
- [Directory publishing and org controls](directory-publishing-and-org-controls.md) — submitting
  to the directory, review, and Team/Enterprise controls.

Sources: https://claude.com/docs/extend/overview ; https://claude.com/docs/skills/overview ;
https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory
