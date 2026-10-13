---
lore: 1
type: topic
summary: "What the Claude mobile app can do (2026-10-13): no Customize page, the connectors-directory doc conflict, what works in mobile chat, subagents by mode, and a recipe for the same setup on every device."
parent: lore/claude-apps-and-surfaces.md
---

# Claude mobile app

Checked 2026-10-13. Documented unless a line says otherwise. The mobile app (iOS, Android) is
mainly a client: what a user can do from the phone depends on where the session runs.

- **No Customize page** for skills or plugins on mobile. Users manage them on web or desktop.
- The mobile **"Connectors directory"** is the same MCP connector catalog as on desktop. The
  current help article says users can browse it on mobile and that adding connectors on mobile
  "is currently in beta". An older help page says browsing and adding on mobile are not possible.
  Treat the current article as authoritative and mention that the two pages conflict.
- Everything on the account works in **mobile chat**: remote connectors, skills, and plugin skills
  and commands. Connectors connected on web or desktop appear on mobile at the next sign-in. Local
  connectors do not work on mobile ([connectors](connectors.md)).
- **Interactive MCP Apps** render in mobile chat (since 2026-03-25).
- **Subagents from the phone** depend on the mode:
  - Normal chat: none (chat ignores plugin agents).
  - Code tab **cloud sessions**: full Claude Code sessions on Anthropic's servers that continue
    while the laptop is off. Subagents work there — inference; the docs do not say so for cloud
    sessions explicitly.
  - **Remote Control** steers an existing local Claude Code session.
  - **Dispatch** starts Cowork or Claude Code sessions on the user's desktop.
  - Cloud **Cowork** on mobile exists (since 2026-07-07), but the docs do not say whether it runs
    plugin agents.

## Recipe: the same setup on every device

1. Install skills, plugins, and connectors from Customize on web or desktop, not from the Claude
   Code CLI ([account sync](extension-platform.md)).
2. Connect each connector there.
3. Prefer remote connectors.
4. Turn on code execution so skills run in chat.
5. Use Dispatch, Remote Control, or cloud sessions for work that needs a computer.

Sources: https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities ;
https://claude.com/docs/extend/overview ; https://code.claude.com/docs/en/mobile ;
https://support.claude.com/en/articles/12138966-release-notes
