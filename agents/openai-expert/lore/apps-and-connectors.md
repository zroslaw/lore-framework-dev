---
lore: 1
type: topic
summary: "Apps (formerly connectors) in ChatGPT and Codex: what an app is, directory vs custom MCP apps, personal vs workspace connections, synced vs non-synced data, company knowledge, remote vs local, and where each kind works."
parent: lore/extension-platform.md
---

# Apps and connectors

Checked 2026-10-14. Documented unless a line says otherwise.

- An **app** is a connected MCP server plus the user's (or a shared) sign-in to that service. The
  admin docs use **app** and **MCP server** for the same thing. "Connector" is the older word
  (third-party report: renamed to "apps" in December 2025). Apps now reach users inside
  **plugins**; a plugin can bundle one or more apps with skills.
- **Directory apps**: OpenAI and partner plugins in the universal directory (for example Gmail,
  Google Drive, Slack, SharePoint, GitHub, Notion, Salesforce). Reviewed before listing.
  **Custom apps**: a custom MCP server added by URL and created as a personal or workspace
  plugin ([remote MCP per surface](remote-mcp-per-surface.md)).
- **Remote vs local**: remote apps (HTTPS MCP) are called from OpenAI's cloud and work on web,
  desktop, and mobile. Local MCP servers (stdio, or `config.toml` entries) run on the user's
  computer and work only on a Codex host — Codex in the desktop app, local Work threads, Codex
  CLI, IDE extension — and from the phone only through a connected host. Plugins that need them
  carry a **Desktop only** badge.
- **Accounts**: a personal connection uses the user's own account. **Workspace connections**
  (Business and Enterprise) use a company-managed account for Team Tasks and @ChatGPT in Slack
  and Teams. A plugin can prompt for sign-in at install or at first use. **Sign in with ChatGPT**
  (beta) can create or link a partner account (Airtable, GitLab, HubSpot, Notion, Supabase,
  Vercel) and shares only name, email, and picture.
- **Synced vs non-synced**: non-synced data from Chat and deep research is processed on demand and
  not indexed; synced apps index selected content in advance (the plugin page shows whether a
  connection supports sync).
- **Company knowledge** uses read-only tools; an MCP server qualifies when it implements the
  standard `search` and `fetch` tool schemas.
- **Data handling**: no model training on data accessed through apps for Business, Enterprise,
  and Edu; the connected service's own policies also apply.
- **Uninstalling a plugin** does not disconnect a separately connected MCP integration; disconnect
  it on the Plugins page.
- Recommendation (inference): when a user wants the same tools on every device, prefer a remote
  app. A local MCP server stays tied to one computer.

Sources: https://learn.chatgpt.com/docs/plugins ; https://learn.chatgpt.com/docs/enterprise/apps-and-connectors ;
https://learn.chatgpt.com/docs/enterprise/shared-connections ;
https://developers.openai.com/plugins/build/mcp-server ;
https://developers.openai.com/plugins/deploy/desktop-only ; third-party:
https://caipi.ai/blog/which-plans-support-mcp-2026
