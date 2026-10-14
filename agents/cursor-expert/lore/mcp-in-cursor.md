---
lore: 1
type: topic
summary: "MCP in Cursor (2026-10-14): mcp.json locations and fields, transports, OAuth (DCR, static client, redirect URLs), headers and interpolation, supported MCP features, tool approval and Run Modes, permissions.json, install links, logs."
parent: lore/extension-platform.md
---

# MCP in Cursor

Checked 2026-10-14. Documented unless a line says otherwise. Per-surface behavior for a remote
server: [remote MCP by surface](remote-mcp-by-surface.md).

## Configuration

- Install from Customize > MCPs (one click, "Add to Cursor"), from a plugin, from a team
  marketplace, from an install link
  (`cursor://anysphere.cursor-deeplink/mcp/install?name=...&config=<base64 JSON>`), or by editing
  `mcp.json`.
- Files: `.cursor/mcp.json` (project, commit it to share) and `~/.cursor/mcp.json` (global). Both
  merge; on a name conflict the project entry wins. The CLI reads the same files.
- Only local agents read these files. Cloud agents and self-hosted workers read only servers set
  up in the dashboard, so a committed `.cursor/mcp.json` does not reach them (forum staff,
  2026-04-17; Team Pool docs). Details: [remote MCP by surface](remote-mcp-by-surface.md).
- **Cloud MCP servers** (team servers, and personal servers set up at cursor.com/agents) also show
  in Customize on the desktop, with a "cloud account" sign-in (3.19).
- Local server: `command`, `args`, `env`, `envFile` (stdio only), optional `"type": "stdio"`.
- Remote server: `url` plus optional `headers`, or an `auth` object for OAuth.
- Interpolation in `command`, `args`, `env`, `url`, `headers`: `${env:NAME}`, `${userHome}`,
  `${workspaceFolder}`, `${workspaceFolderBasename}`, `${pathSeparator}`/`${/}`.
- Extension API: `vscode.cursor.mcp.registerServer()` registers servers from a VS Code extension.
- Logs: Output panel → "MCP Logs". Toggle a server in Customize without removing it.

## Transports

The MCP page lists `stdio` (local, Cursor manages the process), `SSE`, and `Streamable HTTP` (both
"Local/Remote", multi-user, OAuth). Cloud agents restrict this; see the surface topic.

## OAuth and other auth

- Cursor supports OAuth for remote servers. The docs present static credentials as the
  alternative "instead of dynamic client registration", so OAuth 2.0 **Dynamic Client
  Registration** is the default path. For providers without DCR, or that need a fixed client or an
  allowlisted redirect URL (Figma and Linear are named), add static credentials:
  `"auth": {"CLIENT_ID": ..., "CLIENT_SECRET": ..., "scopes": [...]}`. Only `CLIENT_ID` is
  required. Without `scopes`, Cursor reads `scopes_supported` from
  `/.well-known/oauth-authorization-server`.
- Fixed redirect URLs (register both if users sign in from web and desktop):
  - Web and Cursor Agents: `https://www.cursor.com/agents/mcp/oauth/callback`
  - Desktop app: `http://localhost:8787/callback`
  - Cursor finds the server from the OAuth `state` parameter, so the same URLs work for every
    server.
- 3.24 (October 2026): servers whose OAuth apps reject localhost redirects can sign in through a
  Cursor-hosted callback page. Earlier fixes covered DCR `invalid_scope` errors and Microsoft
  Entra consent loops.
- Static secrets: `headers` (for example `Authorization: Bearer ${env:TOKEN}`).

## Protocol features

The MCP page table marks these **Supported**: Tools, Prompts, Resources, Roots, Elicitation, and the
MCP Apps extension (interactive UI from tools, with a plain fallback). Sampling is not listed.
Tools can return images (base64); Cursor attaches them to the chat. Paginated tool, prompt, and
resource lists load in full (release notes). The table does not say which surfaces support each
feature; inference: it describes the desktop app.

## Approval of tool calls (local agents)

- By default Cursor asks before an MCP tool call. MCP follows the same **Run Modes** as shell
  commands: **Auto-review** (default since 3.6, 2026-05-29: allowlisted tools run, others go to a
  classifier on Cursor's backend), **Allowlist**, **Run Everything**.
- `~/.cursor/permissions.json` `mcpAllowlist` uses `server:tool`, `server:*`, `*:tool`, `*:*`. It
  overrides the in-app MCP allowlist. Admin settings override the file. They do not merge.
- A tool that sets `_meta["cursor/requiresConfirmation"]: true` in `tools/list` always gets an
  approval prompt in Cursor clients, also under Auto-review (Origin MCP page; 3.23 release note),
  unless the user allowlisted it or uses Run Everything.
- CLI: `--approve-mcps`, `--force`, `/run-everything`. Cloud agents never ask.

## Limits and housekeeping

- Teams and members can each configure up to 1,000 MCP servers (release note, week of
  2026-09-14). The Cloud Agents API takes up to 50 inline servers.
- When servers expose more tools than a model accepts, cloud agents cap the MCP tools they send.

Sources: https://cursor.com/docs/mcp.md ; https://cursor.com/help/customization/mcp.md ;
https://cursor.com/docs/mcp/install-links.md ; https://cursor.com/docs/reference/permissions.md ;
https://cursor.com/docs/agent/security/run-modes.md ; https://cursor.com/docs/api/origin/mcp.md ;
https://cursor.com/docs/cli/mcp.md ; https://cursor.com/docs/release-notes.md ;
https://cursor.com/docs/cloud-agent/self-hosted/pool.md ;
https://forum.cursor.com/t/how-to-use-mcps-with-self-hosted-agents/157677 (forum, staff, 2026-04-17)
