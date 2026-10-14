---
lore: 1
type: topic
summary: "MCP connectors on Claude: remote vs local, where each works, directory vs custom, and custom connector plans, sign-in, OAuth, headers, network reach, and MCP features. Open when asked if a connector works on a surface or plan."
parent: lore/extension-platform.md
---

# Connectors

Checked 2026-10-13 unless a section says otherwise. Documented.

- A **connector** is an MCP server registered on the account plus the user's sign-in to that
  service.
- **Remote connectors** (an http or sse URL) are called from Anthropic's cloud. They work on web,
  desktop, and mobile.
- **Local connectors** run as a program on the user's computer: desktop extensions (`.mcpb`), or
  plugin MCP servers marked "Runs in each session". They work in Claude Desktop, in Claude Code,
  and in a local Cowork session — never in web or mobile chat.
- **Directory and custom connectors** run on the same infrastructure. A directory listing is
  reviewed; a custom connector is added by URL.
- Connectors connected on web or desktop appear on mobile at the next sign-in. Browsing and adding
  connectors on the phone has a doc conflict: see [mobile app](claude-mobile-app.md).
- On Team and Enterprise, an Owner can add connectors for the org, and members then connect with
  their own accounts ([org controls](directory-publishing-and-org-controls.md)).

Recommendation: when a user wants the same tools on every device, prefer a remote connector. A
local one stays tied to the computer it runs on.

## Custom connectors (remote MCP)

Checked 2026-10-14. Documented.

- **Plans and surfaces:** Free, Pro, Max, Team, and Enterprise, on Claude (web), Claude Desktop,
  and Cowork. A Free user can have only one custom connector.
- **Who adds them:** on Pro and Max, the user. On Team, only Owners and Primary Owners, for the
  organization. On Enterprise, also people with a custom role that includes "Manage access to
  Libraries".
- **Where it works:** after it is added, the connector works in all clients, "including claude.ai,
  Claude Desktop, Cowork, and the mobile apps". The help article gives no steps to add one on
  mobile. Add it on the web at Customize > Connectors.
- **Sign-in options** in the add dialog: "Sign in now", "Sign in when needed", or "No sign in".
  **OAuth client** options: "Use Claude's published identity" (recommended), "Register
  automatically" (dynamic client registration), or "Use your own OAuth client".
- **Request headers** (beta, for a limited set of organizations): fixed credentials, such as an
  API key or a bearer token, that Claude sends on every request. You can use them together with
  OAuth, but not as an `Authorization` header on an OAuth connection.
- **Network:** connections come from Anthropic's cloud, not from the user's device. The server
  must be reachable over the public internet from Anthropic's IP ranges. A private server must
  allowlist those ranges. A server that is only behind a VPN or in a private network does not
  connect.
- **MCP features:** supported — tools, prompts, and resources; text and image tool results; text
  and binary resources. Not supported — resource subscriptions, sampling, and advanced or draft
  capabilities. Users can turn off single tools in the "Search and tools" menu.

Recommendation (inference): a server that is only on a private network cannot be a custom
connector. Use a local connector on a desktop surface, or make the server public and allowlist
Anthropic's IP ranges.

## Other products

Documented by the sibling agents, checked 2026-10-14: ChatGPT, Codex, and Cursor also accept
remote MCP servers over HTTPS with OAuth and dynamic client registration on their main surfaces.
The details differ per surface and plan. For detail, consult openai-expert
(`openai-expert/lore/remote-mcp-per-surface.md`) or cursor-expert
(`cursor-expert/lore/remote-mcp-by-surface.md`).

Sources: https://claude.com/docs/extend/overview ; https://claude.com/docs/connectors/directory ;
https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities ;
https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp ;
https://claude.com/docs/connectors/building ; https://claude.com/docs/connectors/custom/remote-mcp
