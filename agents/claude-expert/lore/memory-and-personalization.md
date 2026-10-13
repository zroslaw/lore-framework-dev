---
lore: 1
type: area
summary: "How Claude personalizes: memory topics, search past chats, account and project instructions, skills, and styles; which mechanism is which and where each applies. Open for any remember or personalize question."
parent: lore-context.md
---

# Memory and personalization

Scope: everything that makes Claude respond differently for one user — what it remembers, what it
can look up from past chats, and the instructions the user writes. Checked 2026-10-13.

## Which mechanism is which

Users and third-party articles often blur these. They are separate features with separate
settings:

| Mechanism | What it is | Where it applies |
|---|---|---|
| **Memory** | Topics Claude saves about the user while chatting | Account-wide outside projects; each project has its own memory space; shared with cloud Cowork |
| **Search past chats** | On-demand retrieval over raw past chats, shown as tool calls | Paid plans; non-project chats or one project, never across projects |
| **Instructions for Claude** | Text the user writes once in Settings | Account-wide |
| **Project instructions** | Text the user writes for one project | Inside that project only |
| **Skills** (and older **Styles**) | Reusable instructions, including tone and format | Wherever skills load ([extension platform](extension-platform.md)) |

Memory is built into Claude. It is not an MCP connector.

## Children

- [Memory and chat search](memory-and-chat-search.md) — topic-based memory, defaults per plan,
  Cowork sharing, search past chats, user controls, and what is undocumented.
- [Instructions, projects, and styles](instructions-projects-and-styles.md) — the written
  personalization settings and their doc conflicts.
