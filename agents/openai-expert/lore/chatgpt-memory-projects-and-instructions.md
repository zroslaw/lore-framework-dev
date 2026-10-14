---
lore: 1
type: topic
summary: "ChatGPT memory as of 2026-10-14 (memory summary system from June 2026, saved memories, reference chat history, plan differences), temporary chats, projects and project-only memory, custom instructions, personality, writing style."
parent: lore/memory-and-personalization.md
---

# ChatGPT memory, projects, and instructions

Checked 2026-10-14. help.openai.com blocks fetches, so the memory facts below come from search
snippets of the Memory FAQ (8590148) and press reports. Labels per line.

## Memory

- Two long-standing settings (Memory FAQ, documented via snippets): **Reference saved memories**
  (details the user asked ChatGPT to keep) and **Reference chat history** (draws on past chats).
  Turning off saved memories also turns off chat history. Settings "may vary slightly" by plan.
- **New memory system** (third-party reports of OpenAI's 2026-06-04 announcement): one **memory
  summary** per user, updated automatically, editable, with time-sensitive facts revised as dates
  pass. US Plus and Pro first; Free and Go "over the coming weeks"; Plus and Pro get 2x capacity.
  Users can switch back to the legacy saved-memories system in Memory controls. I did not confirm
  the Free and Go rollout status.
- Plan differences (third-party, older): Free once had saved memories only; Plus and Pro had full
  chat-history reference. Recheck before quoting.
- **Temporary Chat**: does not use or create memories (Memory FAQ, documented via snippets).
- Deleting a chat does not remove a saved memory that came from it (same source).
- Manage at **Settings > Personalization** on the web. Work uses the account's memory settings, not
  the local Codex store (documented, learn.chatgpt.com).
- Dots keep their own notes in addition to relevant ChatGPT memory (documented).
- Memories began rolling out to the EEA, UK, and Switzerland in June 2026, off by default there
  (documented, What's new).

## Searching past work

- **Reference chat history** (above) is the automatic way ChatGPT uses past chats. Anthropic's
  equivalent is "search past chats"; OpenAI does not document whether its retrieval shows as tool
  calls (not checked).
- **Search chats**: Cmd/Ctrl+K on the web; search also matches folders and conversation titles on
  web, iOS, and Android (documented, 2026-08). The desktop app has **Search chats** in the sidebar.
- **Library**: saved files can be added to a new conversation without uploading again (web,
  documented 2026-08).
- Codex has its own local chat search (content and branch names) and `codex resume` (documented).

## Projects

- A ChatGPT project keeps chats (Chat and Work), files, connected **Sources**, and project
  instructions together. It does not give access to a local folder (documented).
- The desktop **Projects** view also holds **local projects** (one or more folders; the primary
  folder drives `AGENTS.md`, skills, and `config.toml` discovery) (documented).
- Projects exist on all plans; project sharing reached Free, Plus, Pro, and Go on web, iOS, and
  Android on 2025-10-22 (help article 10169521, via snippets).
- Project memory: **default** or **project-only**, set at creation; a third-party guide quotes
  that project-only cannot be reverted to default. Shared projects do not see a member's personal
  memories or instructions (third-party quoting OpenAI).

## Instructions and style

- **Custom instructions** apply across chats; in Codex they are the global `AGENTS.md`
  (documented).
- **Personality**: Settings > Personalization > Base style and tone; changes style, not
  capability (documented).
- **Writing style** for Work on the web: connect email, messaging, or document apps, then turn on
  **Use writing style**; off at Settings > Personalization > Writing (documented).

Sources: https://learn.chatgpt.com/docs/personalize ; https://learn.chatgpt.com/docs/customization/memories ;
https://learn.chatgpt.com/docs/projects ; https://learn.chatgpt.com/docs/whats-new ;
https://help.openai.com/en/articles/8590148-memory-faq (snippets) ;
https://help.openai.com/en/articles/10169521-projects-in-chatgpt (snippets) ; third-party:
https://www.thurrott.com/a-i/337052/openai-is-improving-how-chatgpts-memory-works ;
https://www.memorylake.ai/blogs/chatgpt-project-memory-modes
