---
lore: 1
type: topic
summary: "Claude plugins: Customize install paths (Discover, add marketplace, upload), limits, and the per-surface component support table for chat, Cowork, and Claude Code. Open before predicting whether a plugin works somewhere."
parent: lore/extension-platform.md
---

# Plugins: install paths and surface support

Checked 2026-10-13. Documented.

## Install paths in Customize

- **Discover**: Anthropic's default marketplaces and the directory (Pro, Max, Team, Enterprise).
- **Add > Add marketplace**: a Git repo on GitHub or GitHub Enterprise, or a public GitLab or
  Bitbucket repo. A private GitHub repo needs the Claude GitHub App.
- **Add > Upload plugin**: a `.zip` or `.plugin` file.
- Limits: 25 self-added marketplaces per account per org; 5,000 files or 200 MB per plugin.
- Plugins added from a marketplace URL or by upload are not reviewed; directory listings are
  ([publishing](directory-publishing-and-org-controls.md)).

Customize installs sync to the account and reach Claude Code as synced plugins; CLI installs do
not sync back ([account sync](extension-platform.md)).

## Component support per surface

From the docs table "Plugin feature support across platforms":

| Component | Chat | Cowork | Claude Code |
|---|---|---|---|
| Skills | Loaded | Loaded | Loaded |
| Commands | Loaded as skills | Run as `/plugin-name:command` | Run as `/plugin-name:command` |
| Agents, hooks | Ignored | Loaded | Loaded |
| Remote MCP | Works after the user connects it on the plugin's Connectors tab | Not recorded | Not recorded |
| Local MCP | Ignored | Works only when the session runs on the user's computer | Works ([connectors](connectors.md)) |
| MCP URLs that use `${user_config.*}` | Ignored | Cowork does not prompt for the values | Not recorded |
| LSP servers, output styles, themes, `settings` | No | No | Claude Code only |

"Not recorded" means my 2026-10-13 notes did not capture that cell; read the docs table before
answering it.

**A top-level `bin/` directory makes chat and Cowork refuse the whole plugin**, not just that
directory.

Sources: https://claude.com/docs/plugins/overview ; https://claude.com/docs/plugins/platform-support
