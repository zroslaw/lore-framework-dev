---
lore: 1
type: topic
summary: "What the ChatGPT mobile app can do (2026-10-14): Chat and Work with plugins, Codex Cloud tasks, Codex on mobile driving a connected Mac or Windows host, dots, and what does not work on the phone."
parent: lore/openai-apps-and-surfaces.md
---

# ChatGPT mobile app

Checked 2026-10-14. Documented unless a line says otherwise. The mobile app (iOS, Android) is
mainly a client: what a user can do from the phone depends on where the work runs.

## What works on the phone

- **Plugins in Chat and Work.** "On mobile, you can use plugins available to your account in Chat
  or Work." Plugins installed on web or desktop are account-level, so they are available on the
  phone. The iOS composer suggests installed plugins and their skills (iOS 1.2026.202, July 2026).
- **ChatGPT Work** runs in the cloud from mobile. Synced Work tasks (Local computer access with
  Work Cloud) started on desktop continue on mobile; local steps still need the computer online.
- **Codex Cloud**: open **Codex**, select a published environment, start or continue a task.
  Creating an environment needs web or desktop.
- **Codex on mobile (remote connections)**: pair the phone with a Mac or Windows host that runs
  the ChatGPT desktop app (**Settings > Connections > Control this Mac or PC**, scan a QR code).
  From the phone: start chats in host projects, steer, approve commands and MCP calls, review
  diffs and terminal output. **The host supplies everything**: files, shell, MCP servers, skills,
  plugins, Computer Use, browser. Workspaces may need an admin to enable Remote Control access.
  Pairings unused since 2026-06-08 must be redone. Preview started 2026-05-14 (Mac), Windows
  hosts 2026-05-25. The iOS tab is now **Codex** (older builds show **Remote**).
- **Dots**: create and talk to a dot on mobile (setup since 2026-10-09); calls supported.
- **Scheduled tasks from app events** (Gmail, Slack, GitHub triggers) run on web and mobile.
- **ChatGPT Voice** with Codex: through Remote on iOS (documented in the 2026-07-20 to 24 digest).

## What does not work on the phone

- **Desktop-only plugins** (local stdio MCP, local programs) are not available on mobile.
- Local MCP servers in `config.toml` are not reachable from mobile Chat or Work; they work only
  through a connected host (Codex on mobile).
- **Adding a custom MCP server** is documented for ChatGPT on the web only
  ([remote MCP per surface](remote-mcp-per-surface.md)).
- The Apple Messages plugin runs on the Mac only.
- Mobile web is not supported for dots.

## Recipe: the same tools on every device (inference, from the facts above)

1. Install plugins from the Plugins page on web or desktop, and connect each one there.
2. Prefer remote MCP servers (or plugins that wrap them) over local stdio servers.
3. For work that needs a computer, keep a host online and use Codex on mobile or synced Work.

Sources: https://learn.chatgpt.com/docs/plugins ; https://learn.chatgpt.com/docs/mobile ;
https://learn.chatgpt.com/docs/remote-connections ; https://learn.chatgpt.com/docs/dots ;
https://learn.chatgpt.com/docs/automations ; https://learn.chatgpt.com/docs/whats-new ;
https://developers.openai.com/plugins/deploy/desktop-only
