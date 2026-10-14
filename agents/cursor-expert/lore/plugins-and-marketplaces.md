---
lore: 1
type: topic
summary: "Cursor plugins (2026-10-14): Cursor Plugin vs Agent Plugins formats, components, the reviewed Cursor Marketplace, team marketplaces and install modes, project or user install, local plugins and the symlink rule, CLI marketplace commands."
parent: lore/extension-platform.md
---

# Plugins and marketplaces

Checked 2026-10-14. Documented unless a line says otherwise.

## Two plugin formats

| Format | Manifest | Components |
|---|---|---|
| **Cursor Plugin** | `.cursor-plugin/plugin.json` (only `name` is required) | Rules (`.mdc`), skills, agents (subagents), commands, MCP servers, hooks, `variables` |
| **Agent Plugin** (open standard, agent-plugins.org) | Root `plugin.json` with the standard's `$schema` | Skills and MCP servers |

- Cursor detects the format from the manifest; install works the same way for both.
- Cursor does **not** expand the standard's `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in `mcp.json`.
  Use `${CURSOR_PLUGIN_ROOT}` for the plugin root.
- Default folders: `skills/`, `rules/`, `agents/`, `commands/`, `hooks/hooks.json`, `mcp.json`. A
  root `SKILL.md` makes a single-skill plugin. A manifest path replaces folder discovery for that
  component.
- `variables`: a JSON Schema of value names (tokens, URLs). Users or admins enter the values at
  install time; `mcp.json` uses `${VAR}` placeholders.
- Multi-plugin repos: `.cursor-plugin/marketplace.json`. Template repo: github.com/cursor/plugin-template.
- Plugins are "largely markdown files"; "no binaries are shipped" (marketplace security page).

## Cursor Marketplace

- Official, curated, at cursor.com/marketplace and in Customize. Plugins are Git repositories and
  must be open source. Cursor **manually reviews every plugin and every update**; updates do not
  flow automatically from source. Submit at cursor.com/marketplace/publish.
- Plugins respect the team MCP allowlist: a blocked MCP server inside a plugin installs but cannot
  make calls.
- Install: Customize → find the plugin → **Install** → choose **project** or **user** scope.
  Agent Plugins and Cursor Plugins use the same flow. The help page says plugins "work across
  Cursor desktop, web, and CLI".
- Import a GitHub repo as a marketplace in Customize ("From GitHub Repository"; it needs
  `.cursor-plugin/marketplace.json`). Rules and skills cannot be imported alone; package them in a
  plugin.

## Team marketplaces (Teams and Enterprise)

- Teams: 1 team marketplace. Enterprise: unlimited; only admins add marketplaces.
- Manage at Dashboard → Plugins & MCPs. Import from GitHub, GitLab, Bitbucket, or Azure DevOps.
- Install modes per plugin: **Default Off**, **Default On** (users can opt out), **Required**
  (always installed, cannot be removed).
- Access can be limited to Organization Groups (SCIM-synced).
- Auto Refresh on push for GitHub imports (needs the Cursor GitHub App; at most once per 10
  minutes). "Serve marketplace from Cursor" lets members use it without GitHub access.
- The **Default** team marketplace also carries Team MCP servers, so the same servers reach cloud
  agents and the Agent Window, IDE, and CLI. Members can **publish** a personal skill from
  `~/.cursor/skills/` to it (admins can turn this off); publishing installs nothing for others.

## Local plugins

- Put a plugin folder in `~/.cursor/plugins/local/<name>` and reload the window.
- **Symlink rule**: a symlink there loads only when its target resolves to a directory inside that
  folder. Cursor skips a symlink to a plugin repository elsewhere on disk.
- Teams and Enterprise: admins control **Allow Local Plugin Imports** (off by default on
  Enterprise). A marketplace install with the same name wins over the local copy.
- A `workspaceOpen` hook can return plugin paths to load for a workspace.
- CLI: `--plugin-dir <path>`, `enabled_plugins` in `~/.cursor/settings.json`, `/plugin`, and
  `agent plugin marketplace add|list|update|remove` ([Cursor CLI](cursor-cli.md)).
- Third-party imports: the setting "Include Third-Party Plugins, Skills, and Other Configs"
  (Settings → Agents → Third-Party Imports, on by default) loads Claude Code configs. The CLI
  shows plugins imported from Claude Code beside native ones.

## Lore framework notes

lore-architect owns how Lore installs on Cursor. Its notes record that a plugin enable is an
account-side operation with no non-interactive install command
(`lore-framework-dev/agents/lore-architect/lore/cursor-plugin-install-is-account-side.md`). The
symlink rule above is new public documentation that matters for any symlink-based install.

Sources: https://cursor.com/docs/plugins.md ; https://cursor.com/docs/reference/plugins.md ;
https://cursor.com/help/customization/plugins.md ; https://cursor.com/help/security-and-privacy/marketplace-security.md ;
https://cursor.com/docs/customize-cursor.md ; https://cursor.com/docs/reference/third-party-hooks.md ;
https://cursor.com/docs/cli/changelog.md
