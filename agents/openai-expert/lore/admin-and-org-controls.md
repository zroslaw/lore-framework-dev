---
lore: 1
type: topic
summary: "Business and Enterprise controls over plugins, MCP servers, skills, and agents (2026-10-14): the capability chain, Action control, RBAC, domain restrictions, Agent Security, managed configuration, workspace connections."
parent: lore/extension-platform.md
---

# Admin and org controls

Checked 2026-10-14. Documented unless a line says otherwise.

## The capability chain for one plugin

| Layer | What it decides | Where |
|---|---|---|
| Availability | Which roles can use or install the plugin | Workspace settings (web, desktop); the CLI uses its own browser |
| Included skills | What instructions it adds | Package and Skill controls |
| MCP server access | Who can use the server | Workspace apps, Permissions & roles |
| Actions | Read-only or an approved set (**Action control**), and **App permissions** for when ChatGPT asks | Workspace apps |
| Service authorization | What the connected account can see and do | The external service |
| Runtime permissions | What the agent can do with the data | Sandbox and approval controls |

- A member needs every layer. Installing a plugin for everyone does not give a shared account.
- **Workspace connections**: company-managed accounts for Team Tasks and @ChatGPT in Slack and
  Teams.
- **Verified-domain restriction**: stops company-domain accounts from connecting supported apps in
  personal or other workspaces. It needs the OAuth server to return a verified `email` claim.
- Enterprise owners can export the public plugin catalog as CSV (Admin > Plugins > Public).
- Third-party report: workspace permissions include **Use plugins**, **Upload plugins**, and
  **Create plugins with MCPs** (off by default on Enterprise).

## Agents and local clients

- **Agent Security** (DevDay 2026): Global policies for tools, files, network, approval policies,
  web search modes, apps, MCP servers, plugins, and rules for local and Codex Cloud execution;
  Work Cloud has separate controls. Configure most fields as TOML (`requirements.toml`).
- **Managed configuration**: admins push defaults and enforced requirements to the desktop app,
  CLI, and IDE (MDM, cloud-managed), including plugin marketplaces and browser and Computer Use
  limits.
- **Remote Control access** must be enabled by the admin before members pair phones with hosts.
- Feature switches such as dots, Computer History, GPT-6.1 Sol, and Astra are off by default in
  Enterprise until an admin enables them.

Sources: https://learn.chatgpt.com/docs/enterprise/apps-and-connectors ;
https://learn.chatgpt.com/docs/enterprise/agent-security ;
https://learn.chatgpt.com/docs/enterprise/managed-configuration ;
https://learn.chatgpt.com/docs/enterprise/shared-connections ;
https://developers.openai.com/plugins/build/auth ; third-party:
https://smartscope.blog/en/blog/chatgpt-sites-mcp-server-plugin-hosting-2026/
