---
lore: 1
type: topic
summary: "OpenAI plugin packaging (portable Agent Plugins plugin.json, .codex-plugin overlay, Claude-compatible manifests), marketplaces, workspace publishing, public submission, desktop-only plugins, and converting a Claude Code plugin."
parent: lore/extension-platform.md
---

# Plugins: packaging and publishing

Checked 2026-10-14. Documented unless a line says otherwise.

## Package formats

- **Portable (preferred)**: root `plugin.json` with
  `"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"`, plus `skills/`,
  `mcp.json` (each server declares a transport `type`), and `assets/`. OpenAI-specific settings
  (presentation, registered MCP server mappings, hooks, `onboardingSkill`) go under
  `extensions.com.openai`.
- **Codex compatibility**: `.codex-plugin/plugin.json` (with `.mcp.json`, `.app.json`, `hooks/`,
  `scripts/`). Still supported; `@plugin-creator` scaffolds this layout. Used only when
  `extensions.com.openai` is absent (the two are not merged).
- **Claude-compatible**: OpenAI also accepts "legacy and Claude-compatible manifests". The desktop
  app reads a **legacy-compatible marketplace at `$REPO_ROOT/.claude-plugin/marketplace.json`**.
- A skill is a folder with `SKILL.md` (`name`, `description`); optional `agents/openai.yaml` for
  UI metadata, `allow_implicit_invocation`, and declared MCP tool dependencies.

## Marketplaces (local and team distribution)

- Repo marketplace `$REPO_ROOT/.agents/plugins/marketplace.json`; personal marketplace
  `~/.agents/plugins/marketplace.json`. Entries need `policy.installation` (`AVAILABLE`,
  `INSTALLED_BY_DEFAULT`, `NOT_AVAILABLE`), `policy.authentication` (on install or first use), and
  `category`. Sources: local path, Git (`url`, `git-subdir`, `ref`/`sha`), or an npm package.
- CLI: `codex plugin marketplace add owner/repo [--ref] [--sparse PATH]`, `... list`,
  `... upgrade`, `... remove`. Install from the `/plugins` browser.
- Installed copies live in `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` (`local` for
  local plugins). Enable per repo with `[plugins."name@marketplace"] enabled = true` in
  `.codex/config.toml` (trusted projects only).
- Admins can import and sync a GitHub marketplace for the workspace (Admin > Plugins).

## Sharing and publishing

- **Personal**: a plugin created in ChatGPT (for example from a custom MCP server) appears under
  **Personal** in the Plugins page. The plan matrix lists **plugin sharing** on Plus, Pro,
  Business, Enterprise.
- **Workspace**: an admin publishes a plugin to selected roles (Plugins > Personal > ... >
  Publish). It stays inside the workspace. Disable with `features.plugin_sharing = false`.
- **Public directory**: submit at https://platform.openai.com/plugins (Apps Management write
  access, identity verification, OpenAI review). Remote MCP must be a stable public HTTPS
  Streamable HTTP endpoint; domain verification via `/.well-known/openai-apps-challenge`; OAuth
  servers need OIDC `openid` and `email` scopes and a UserInfo endpoint. Tool updates go through
  continuous review; other changes need a new version.
- **Desktop-only plugins** (local stdio MCP, local programs): badge **Desktop only**, install only
  from the desktop app, usable only in local threads. Public submission of local MCP is limited to
  allowlisted partners.
- **Lifecycle hooks** must be removed before public submission; hook plugins are distributed for
  manual install in Codex desktop.

## Converting a Claude Code plugin

OpenAI publishes a guide for it:

- Skills move as they are. Replace "Claude" with neutral wording in skill text.
- `commands/` and `agents/` → convert to skills. `hooks` → remove for the public directory.
- `userConfig` and `${user_config.*}` are not supported → explicit inputs, OAuth, hosted storage,
  or Codex-local config.
- `bin/`, `settings.json`, `CLAUDE.md`: keep needed helpers, call them by package-relative path,
  remove Claude-only settings. Claude live artifacts are not supported.
- A skills-only archive with `.claude-plugin/plugin.json` can be uploaded directly; the portal
  converts it to `.codex-plugin/plugin.json`. `.mcpb` files are not accepted.

Sources: https://developers.openai.com/plugins/build/plugins ;
https://developers.openai.com/plugins/deploy/submission ;
https://developers.openai.com/plugins/deploy/desktop-only ;
https://developers.openai.com/plugins/guides/submit-claude-plugin ;
https://learn.chatgpt.com/docs/build-skills ; https://learn.chatgpt.com/docs/pricing
