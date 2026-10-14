---
lore: 1
type: topic
summary: "Remote MCP server (HTTPS, OAuth) per Cursor surface: editor, CLI, cloud agents, web, iOS, self-hosted, Remote Control, Grok Bot, SDK, API. Config source, transports, auth, call origin, approvals, plan gates, doc conflicts."
parent: lore/extension-platform.md
---

# Remote MCP by surface

Checked 2026-10-14. Documented unless a line says otherwise. Config format, OAuth fields, and
approval modes: [MCP in Cursor](mcp-in-cursor.md).

## Short answer

A remote MCP server with streamable HTTP and OAuth works on every Cursor agent surface. Surfaces
differ in which config they read, where the call comes from, and whether tool calls need approval.
Local agents read `mcp.json`; cloud runtimes read only the dashboard config.

| Surface | Where the user adds it | Transports | Call comes from | Tool-call approval |
|---|---|---|---|---|
| Editor, Agents Window (local agent) | Customize > MCPs, `mcp.json` (project, global), plugin, team marketplace. Cloud MCP servers set up on the web also show in Customize (3.19) | stdio, SSE, streamable HTTP | `mcp.json` URL servers: the user's computer (documented, indirect; see Network). Team cloud servers: Cursor's servers, unless an admin turns on "Run team MCP servers on members' machines" | Run Modes (Auto-review default) |
| CLI | Same `mcp.json` files; `agent mcp login` | stdio, HTTP, SSE | The user's machine (inference: same local client as the desktop) | Same allowlist; `--approve-mcps`; `--force` |
| Cloud agents (Cursor VM) | Dashboard only: MCP dropdown at cursor.com/agents (personal); Dashboard > Plugins & MCPs (team); API or SDK inline. Repo `.cursor/mcp.json` is not read | HTTP (recommended), stdio in the VM; SSE: conflict below | Cursor's backend proxies HTTP calls; credentials never enter the VM | None. Cloud agents never ask |
| Web (cursor.com/agents) | Same as cloud agents | Same as cloud | Cursor's backend | None |
| Cursor for iOS | Pick servers per run at launch (the Slack MCP is named); add and manage them on the web | Same as cloud | Cursor's backend | None; answer a sign-in card |
| Self-Hosted Machines (My Machines, Pools) | Cloud Agents dashboard, not repo `mcp.json` | stdio runs on the worker; HTTP/SSE run from Cursor's backend | Backend for URL servers | None |
| Remote Control | Not documented. Inference: the dashboard config, as on a worker | Not documented | Tool calls run on the computer. MCP: not documented; inference below | Not documented |
| Grok Bot | "Connect apps" plugins; team admins via the Team Marketplace | Not documented | Cursor's connector backend holds the OAuth tokens | Grok Bot Auto-review |
| SDK local / cloud, Cloud Agents API | Inline `mcpServers`; API type `http`, `sse`, or `stdio`; max 50 | As listed | Local: the caller's machine. Cloud: backend | SDK local: none unless `local.autoReview` |

## Which config each runtime reads

- **Local agents** (editor, Agents Window, CLI): `.cursor/mcp.json`, `~/.cursor/mcp.json`,
  plugins, and the user's and team's cloud MCP servers (documented).
- **Cloud runtimes**: only servers configured in the dashboard (the MCP dropdown at
  cursor.com/agents, Dashboard > Plugins & MCPs at cursor.com/dashboard/integrations) or inline in
  the API or SDK. Cursor staff, forum, 2026-04-17: "Cloud agents only pick up MCP servers
  configured through the dashboard ... Repo-level mcp.json isn't read by the cloud agent runtime"
  (forum statement). The Team Pool docs agree for workers: "Configure MCP servers through the
  Cloud Agents dashboard" (documented).
- Consequence: a project `.cursor/mcp.json` reaches local agents only. Cloud agents, cloud
  subagents (`/in-cloud`), runs started from web or iOS, and self-hosted runs need the server in
  the dashboard (inference for cloud subagents, web, and iOS: they are cloud-agent runs).
- No tool exists to debug MCP loading on self-hosted workers (forum staff, 2026-04-17).

## Auth per surface

- **Desktop**: OAuth with DCR or a static `auth` client; redirect `http://localhost:8787/callback`,
  or a Cursor-hosted callback page since 3.24. Static `headers` with `${env:...}`. Cloud MCP
  servers show a "cloud account" sign-in in Customize that finishes through a local browser
  redirect (3.19).
- **CLI**: `agent mcp login <id>` with automatic callback; from SSH it prints port-forward steps.
- **Cloud, web, iOS**: OAuth is **per user**, also for team-shared servers. Redirect
  `https://www.cursor.com/agents/mcp/oauth/callback`. Signing in for a cloud agent from the desktop
  finishes through a local redirect. If auth fails, the run logs `mcp_auth_error`, skips that
  server's tools, and continues. Configs are encrypted at rest; `env`, `headers`, and
  `CLIENT_SECRET` cannot be read back.
- **SDK cloud**: Cursor runs the OAuth flow once on its servers and reuses the token. **SDK
  local** cannot open a browser; it reuses tokens from the Cursor app.

## MCP features per surface

Documented: the desktop feature table (tools, prompts, resources, roots, elicitation, MCP Apps).
Not documented: which of these work on cloud agents, web, iOS, or Grok Bot. Inference: plan for
**tools** only off the desktop. Origin's own MCP server is tools-only.

## Network

- **Local agents**: the desktop MCP client connects from the user's machine. Documented
  indirectly: the 3.19 release notes (Cursor IDE and Agents Window) say that on Windows, MCP
  servers and MCP sign-in trust the Intermediate, machine-wide, and enterprise CA stores, which
  fixes errors "when you connect through a corporate proxy or to an internal MCP server". So a
  server on the user's own network or VPN works for local agents. The docs example
  `http://localhost:3000/mcp` agrees.
- **Team cloud servers in the editor**: Cursor's servers call them by default. The admin switch
  "Run team MCP servers on members' machines" (Cursor web, week of 2026-09-14) runs every team
  HTTP server, and each member's own MCP servers, locally in members' IDEs. Cloud agents still use
  Cursor's servers (documented, release notes).
- **Cloud, web, iOS, and self-hosted URL servers** are called from Cursor's backend, so they "won't
  reach private endpoints" (forum staff, 2026-04-17). Inference: the server must be reachable from
  the public internet over HTTPS. For a private-network server, use stdio on a Self-Hosted Machine
  (documented for My Machines and Team Pools).
- Enterprise: MCP Allowlist URL entries restrict which remote URLs may run; per-server tool
  allowlists; a User MCP network denylist.

## Plan gates

- Local agents (editor, CLI): no plan gate for MCP found. The Start plan (India) lists MCP servers
  as included.
- Cloud agents, and so web and iOS runs: a paid plan with Cloud Agents. Free accounts can sign in to
  iOS but cannot start agents.
- Team MCP servers and team marketplaces: Teams (one marketplace) and Enterprise (unlimited).
- MCP Allowlist: Enterprise only. Bugbot MCP tools: Team and Enterprise.

## Conflicts and open points

- **SSE in the cloud** (still open): the capabilities page says "SSE and `mcp-remote` are not
  supported" for custom cloud MCP servers. The Cloud Agents API accepts `type: sse`, but its
  example uses `type: http` with an `/sse` URL. The My Machines and Team Pool pages, the
  self-hosted help, and the 2026-04-17 staff post say "HTTP/SSE" servers run from Cursor's
  backend. Use streamable HTTP for anything that must work in the cloud.
- **Remote Control**: no doc or release note describes MCP in a handed-off session. Inference,
  untested: Remote Control uses a worker that Cursor manages on the computer, so it probably
  follows worker routing — stdio servers on the computer, URL servers from Cursor's backend, and
  servers from the dashboard config rather than `.cursor/mcp.json`. Test before relying on it.
- Grok Bot: no documented way for an individual to add a custom MCP URL.

Sources: https://cursor.com/docs/mcp.md ; https://cursor.com/help/customization/mcp.md ;
https://cursor.com/docs/cli/mcp.md ; https://cursor.com/docs/cloud-agent.md ;
https://cursor.com/docs/cloud-agent/capabilities.md ; https://cursor.com/docs/cloud-agent/mobile.md ;
https://cursor.com/docs/cloud-agent/self-hosted/my-machines.md ;
https://cursor.com/docs/cloud-agent/self-hosted/pool.md ;
https://cursor.com/help/ai-features/self-hosted-machines.md ; https://cursor.com/docs/cloud-agent/api/endpoints.md ;
https://cursor.com/docs/sdk/typescript.md ; https://cursor.com/docs/grok-bot/teams.md ;
https://cursor.com/docs/enterprise/model-and-integration-management.md ;
https://cursor.com/docs/agent/security/run-modes.md ; https://cursor.com/docs/release-notes.md ;
https://forum.cursor.com/t/how-to-use-mcps-with-self-hosted-agents/157677 (forum, staff, 2026-04-17)
