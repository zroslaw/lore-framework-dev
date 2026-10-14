---
lore: 1
type: topic
summary: "Cursor persistent context beyond rules (2026-10-14): the removed Memories feature, Project shared context, automation memories, Grok Bot memory, @Chats, conversation search, side chats, shared transcripts, plans, and resume."
parent: lore/memory-and-personalization.md
---

# Persistent context and history

Checked 2026-10-14. Documented unless a line says otherwise.

## The end of Memories (agent memory)

- Cursor added "Memories" for the coding agent in mid-2025. On 2025-11-25 Cursor staff wrote in
  the forum: "The Memories feature was intentionally removed starting from version 2.1.x." They
  advised the Command Palette command "Export memories" (it writes an `.mdc` file) and moving the
  content into User or Project Rules. A search summary also cited a staff reply that only the
  management UI was removed; I did not verify that thread. (Forum, third-party grade; I found no
  official changelog entry.)
- The current docs and help pages do not describe a general memory for the coding agent. They
  point users to rules, AGENTS.md, and skills.

## Memory-like features that exist now

- **Project shared context** (Projects, 2026-09-10): each Project keeps files that sync across
  every cloud and local machine its agents use. Agents add research, artifacts, and what they learn
  about the codebase and the user's preferences.
- **Automation memories**: an Automations tool that reads and writes named notes (`MEMORIES.md` by
  default) across runs of one automation, outside the working filesystem; on by default; the user
  can view, edit, and delete them.
- **Grok Bot memory**: each Bot keeps stable preferences, role context, and summaries of prior
  work. Memory is per Bot; shared files and handoffs move context between Bots.
- **Cloud subscriptions**: a cloud agent keeps its full conversation while it waits for events for
  up to 180 days.

## Past conversations

- `@Chats` adds context from a previous conversation to the current one.
- **Conversation search**: Cmd+K in the Agents Window searches past transcripts with a local index;
  Cmd+F searches the open chat.
- **Side chats** (`/side`, `/btw`): durable child chats; `@`-mention one to pull its context back.
- **Shared transcripts**: Team or Public links (`cursor.com/s/...`); recipients can "Fork to
  Cursor". Teams and Enterprise only; not with "No Storage" Privacy Mode.
- **Plans** (Plan mode) are saved files: in the home directory by default, or in the workspace.
- CLI: `agent resume`, `--resume <chat-id>`, `/fork`, `/rewind`. SDK: an `Agent` object keeps
  conversation state across runs.

## Compared with Claude (inference)

Claude has an account memory that follows the user into every chat. Cursor has none for the coding
agent; persistent context is file-based (rules, AGENTS.md, skills, Project files) or scoped to one
automation or one Bot. A framework that keeps its own memory in files, such as Lore, does not
compete with a built-in Cursor memory.

Sources: https://cursor.com/docs/agent/projects.md ; https://cursor.com/docs/cloud-agent/automations.md ;
https://cursor.com/docs/grok-bot.md ; https://cursor.com/docs/cloud-agent/capabilities.md ;
https://cursor.com/help/customization/context.md ; https://cursor.com/help/ai-features/conversation-search.md ;
https://cursor.com/help/ai-features/side-chats.md ; https://cursor.com/help/ai-features/shared-transcripts.md ;
https://cursor.com/docs/agent/plan-mode.md ; https://forum.cursor.com/t/are-my-memories-gone/144057 (forum)
