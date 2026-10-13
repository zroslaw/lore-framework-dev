---
lore: 1
type: area
summary: "Where each Claude surface runs and what it can reach: chat, local and cloud Cowork, Dispatch, Claude Code Remote Control and cloud sessions, and the mobile app. Open for any which-surface-can-do-what question."
parent: lore-context.md
---

# Claude apps and surfaces

Scope: the Claude apps (web, desktop, mobile) and the session types users reach through them —
chat, Cowork, Dispatch, and Claude Code (terminal, IDE, desktop Code tab, cloud sessions, Remote
Control). What each extension does on each surface lives in
[extension platform](extension-platform.md). Which plan unlocks each surface lives in
[plans and models](plans-and-models.md).

## Where a session runs

The same feature behaves differently by surface because sessions run in three places. This table
is my synthesis of the documented facts in the child topics (checked 2026-10-13):

| Runs in | Surfaces | Reaches the user's files and local programs |
|---|---|---|
| Anthropic's cloud, chat sandbox | Chat on web, desktop, and mobile | No file changes on the computer; creates files for download. Desktop chat can still call local `.mcpb` extensions. |
| The user's computer | Local Cowork in Claude Desktop, Dispatch child tasks, Claude Code (CLI, IDE, desktop Code tab), Remote Control | Yes. The computer must be on, awake, and online. |
| Anthropic's cloud, agent environment | Cloud Cowork, Claude Code cloud sessions | No local files (inference: both run on Anthropic's servers). Work continues with the laptop closed (documented for cloud sessions). |

The phone is mainly a client. It reaches work that needs a computer only through Dispatch, Remote
Control, or cloud sessions.

## Children

- [Chat, Cowork, Dispatch, Remote Control, cloud sessions](chat-cowork-dispatch-remote-control.md)
  — the correct model of each session type, its requirements, and how they differ.
- [Claude mobile app](claude-mobile-app.md) — what works from the phone, by mode.
