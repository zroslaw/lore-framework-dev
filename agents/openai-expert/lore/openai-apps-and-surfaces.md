---
lore: 1
type: area
summary: "Where each OpenAI surface runs and what it can reach: Chat, ChatGPT Work (cloud and local), Codex local and cloud, dots, the desktop and mobile apps, browser and Computer Use. Open for any which-surface-can-do-what question."
parent: lore-context.md
---

# OpenAI apps and surfaces

Scope: the ChatGPT apps (web, desktop, mobile), the modes inside them (Chat, ChatGPT Work, Codex),
dots, and the Codex surfaces (desktop, CLI, IDE, cloud, mobile, integrations). What each extension
does on each surface lives in the [extension platform](extension-platform.md). Which plan unlocks
each surface lives in [plans and models](plans-and-models.md).

## Where a session runs

This table is my synthesis of the documented facts in the child topics (checked 2026-10-14):

| Runs in | Surfaces | Reaches the user's files and local programs |
|---|---|---|
| OpenAI cloud, chat | Chat on web, desktop, mobile | No. Uses installed plugins (remote MCP, skills). |
| OpenAI cloud, agent container | ChatGPT Work on web and mobile; cloud Work on desktop; dots' own computer | No local files. Work continues with the computer off. |
| OpenAI cloud, Codex environment | Codex Cloud tasks (web, desktop, mobile, CLI, Slack, GitHub) | Only the repos and services in the published environment. |
| The user's computer | Codex in the desktop app, Codex CLI, IDE extension, local Work on desktop, scheduled tasks on local projects | Yes. The computer must be on, and for remote use, awake and online. |
| Cloud-coordinated, local execution | Work with "Local computer access with Work Cloud"; dots with a connected computer; Codex on mobile driving a host | Yes, through the connected computer while it is online. |

The phone is mainly a client. It reaches work that needs a computer only through a connected host
(Codex on mobile, synced Work, a dot's connected computer).

## Children

- [Chat, Work, Codex, and dots](chat-work-codex-and-dots.md) — the correct model of each mode,
  cloud vs local, cross-device sync, and the Claude equivalents.
- [Codex surfaces](codex-surfaces.md) — desktop, CLI, IDE, Codex Cloud, integrations, SDK and app
  server, versions, sign-in.
- [ChatGPT mobile app](chatgpt-mobile-app.md) — what works from the phone, by mode.
- [Browser, Computer Use, and Atlas](browser-computer-use-and-atlas.md) — the cloud browser, the
  desktop built-in browser, the Chrome extension, Computer Use, Appshots, and Atlas's shutdown.
