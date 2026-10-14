---
lore: 1
type: topic
summary: "How users install OpenAI plugins per surface (Plugins page, CLI /plugins, marketplaces, admin import) and which components work where: skills, remote and local MCP, hooks, UI. Open before predicting where a plugin works."
parent: lore/extension-platform.md
---

# Plugin install and component support

Checked 2026-10-14. Documented unless a line says otherwise.

## Install paths

- **ChatGPT web and desktop**: the **Plugins** page (also **Customize > Plugins** in the left
  navigation; chatgpt.com/plugins). Tabs: **OpenAI**, the workspace's name, **Personal** (Created
  by me, Shared with me), plus an **Installed** row. Select **+** to install; connect the app when
  prompted. Start a new chat to use it.
- **Codex in the desktop app**: the same directory plus local and repo marketplaces as extra
  sources (`.agents/plugins/marketplace.json`, legacy `.claude-plugin/marketplace.json`). Restart
  the app after a local change.
- **Codex CLI**: `/plugins` opens a browser grouped by marketplace; install, uninstall, and
  toggle with Space. Add sources with `codex plugin marketplace add`. Start a new session after
  install.
- **IDE extension**: no plugin support. **Mobile**: no install flow is documented; plugins
  installed on the account appear in mobile Chat and Work.
- **Admins**: import and sync a GitHub marketplace for the workspace; set availability per role;
  publish personal plugins to the workspace.
- **API-key sign-in** (Codex CLI and desktop): OpenAI-curated plugins can be installed, but some
  need OAuth flows that API-key sign-in does not support.

## Component support per surface

My table from the plugin, MCP, hooks, and cloud-environment docs:

| Component | ChatGPT Chat and hosted Work (web, desktop, mobile) | Local Work and Codex (desktop app, CLI) | IDE extension | Codex Cloud |
|---|---|---|---|---|
| Skills | Loaded | Loaded | Standalone skills only | Repo skills only |
| Remote MCP (app) | Works after connect | Works | Through `config.toml` only | Not documented |
| Local stdio MCP | Ignored (Desktop only plugins in local threads) | Works | Through `config.toml` | Not documented |
| Lifecycle hooks | Not run in cloud orchestration; only admin MCP hooks | Run after trust review | Host hooks (inference) | Not documented |
| MCP Apps UI | Renders on web, desktop, and mobile | Desktop app | Not documented | No |
| Plugin Extensions (sidebars, panels, editors) | Web and desktop; composer mentions desktop only; Free and Go web "coming soon" | Desktop app | No | No |
| Browser extensions | Desktop app | Desktop app | No | No |

- A plugin's hook scripts must exist in the execution environment; installing on the web does
  not deploy them. Enterprise admins can deploy scripts by MDM.
- Plugins must work on both desktop and mobile, including UI, to pass public review.
- Uninstall removes the bundle; workspace-installed plugins can only be removed by admins.

Sources: https://learn.chatgpt.com/docs/plugins ; https://learn.chatgpt.com/docs/build-skills ;
https://learn.chatgpt.com/docs/hooks ; https://learn.chatgpt.com/docs/environments/cloud-environments ;
https://developers.openai.com/plugins/build/plugins ; https://developers.openai.com/plugins/build/extensions ;
https://developers.openai.com/plugins/deploy/submission
