---
lore: 1
type: topic
summary: "Claude memory as of 2026-10-13: topic-based memory, defaults per plan, sharing with cloud Cowork, search past chats, user controls, and the undocumented question of how memory reaches each chat."
parent: lore/memory-and-personalization.md
---

# Memory and chat search

Checked 2026-10-13. Source: the help article "How does Claude's memory work?" (documented), unless
a line says otherwise.

## Memory topics

- Claude saves separate **topics** about the user while it chats ("reflects changes as they
  happen"). Users view, edit, and delete them at **Settings > Memory > Topics**, or tell Claude in
  chat to remember or forget something.
- Around 2026-07-10 topics replaced a single summary that was updated every 24 hours
  (third-party reports).
- Each project has its own memory space, separate from other projects and from non-project chats.
- Sensitive topics (health, politics, and similar) are saved only when the user turns that on.
  Claude never saves government IDs, criminal history, financial account numbers, or immigration
  status.

## Defaults

- On by default for Free, Pro, and Max on web, desktop, and mobile.
- On Team and Enterprise, off per member until the member turns it on, after an Owner enables it.
- Memory reached the Free plan on 2026-03-02 (press report).

## Cowork

- Memory is shared between chat and **cloud** Cowork in both directions (announced 2026-08-25).
- Local Cowork sessions do not use memory. Anthropic gives no reason.

## Search past chats

- A separate feature on paid plans: retrieval (RAG) over the user's raw chats, run on demand and
  shown as visible tool calls. A 2025 third-party analysis named the tools `conversation_search`
  and `recent_chats`.
- Scope: non-project chats, or one project — never across projects.
- Toggle: "Search and reference chats" in Settings > Memory.

## Controls

- **Incognito chat** (ghost icon): not saved to history or memory.
- **Memory off for one chat**: click "+" before the first message. It is locked after the chat
  starts; the chat stays in history and searchable.
- **Pause**: keeps topics, stops using them.
- **Reset**: deletes everything, including project memories.
- Memory import and export are "experimental".

## Not documented

Whether all memory topics go into every chat or are retrieved on demand. To find out what is
exposed, ask Claude in the app to list its tools and the memory in its context. Not done yet.

Sources: https://support.claude.com/en/articles/11817273-how-does-claude-s-memory-work ;
https://simonwillison.net/2025/Sep/12/claude-memory/ ;
https://techcrunch.com/2026/08/25/claude-cowork-finally-remembers-what-you-told-the-app-in-chat/ ;
https://thenewstack.io/claudes-free-plan-can-now-remember-you/
