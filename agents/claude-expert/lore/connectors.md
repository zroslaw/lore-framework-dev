---
lore: 1
type: topic
summary: "MCP connectors on Claude: remote vs local, where each kind works (web, desktop, mobile, Cowork, Claude Code), and directory vs custom connectors. Open when asked whether a connector will work on a surface."
parent: lore/extension-platform.md
---

# Connectors

Checked 2026-10-13. Documented.

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

Sources: https://claude.com/docs/extend/overview ; https://claude.com/docs/connectors/directory ;
https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities
