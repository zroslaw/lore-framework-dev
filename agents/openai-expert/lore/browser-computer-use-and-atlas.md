---
lore: 1
type: topic
summary: "OpenAI's browser and desktop-control features (2026-10-14): cloud browser, desktop built-in browser, browser extension, Site tools (WebMCP), Computer Use, Appshots, Record & Replay, and the Atlas shutdown."
parent: lore/openai-apps-and-surfaces.md
---

# Browser, Computer Use, and Atlas

Checked 2026-10-14. Documented unless a line says otherwise.

- **Browser in ChatGPT web**: Work uses a cloud browser. Website sign-in happens in a private
  form outside the chat (eligible plans; not Enterprise or Edu). The cloud browser has its own
  sessions, separate from the user's browser.
- **Built-in browser in the desktop app**: a shared view of websites and local web apps, with a
  separate profile. **Developer mode** (Settings > Browser > Enable full CDP access) gives Codex
  Chrome DevTools Protocol access (2026-06). Not available in Codex CLI or the IDE extension.
- **Browser extension**: Chrome, Edge, Brave, Opera, Vivaldi (2026-08-24 to 28). Mention open
  tabs, side chat, work in background tabs where the user is signed in.
- **Site tools (WebMCP)**: Work and Codex can call tools a website exposes, in the desktop
  built-in browser. Not available in Enterprise or Edu (2026-08).
- **Computer Use**: sees and operates macOS and Windows apps from Work or Codex in the desktop
  app; install the Computer Use plugin. Windows runs in the foreground. Not in the Linux preview
  and not in Codex Cloud environments.
- **Appshots**: send the frontmost window (screenshot plus text) to ChatGPT (macOS: both Command
  keys; Windows: both Alt keys).
- **Record & Replay**: demonstrate a workflow on macOS; ChatGPT turns it into a skill. Needs
  Computer Use.
- **Atlas** (OpenAI's own browser, macOS only): third-party report, not confirmed at a primary
  source — wind-down announced 2026-07-09, stopped working 2026-08-09; its features moved to the
  desktop built-in browser and the browser extension.

Sources: https://learn.chatgpt.com/docs/browser ; https://learn.chatgpt.com/docs/chrome-extension ;
https://learn.chatgpt.com/docs/webmcp ; https://learn.chatgpt.com/docs/computer-use ;
https://learn.chatgpt.com/docs/appshots ; https://learn.chatgpt.com/docs/extend/record-and-replay ;
https://learn.chatgpt.com/docs/whats-new ; third-party:
https://www.ai-toolbox.co/chatgpt-management-and-productivity/chatgpt-atlas-browser-guide-2026
