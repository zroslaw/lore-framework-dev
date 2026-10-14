---
lore: 1
type: area
summary: "How Cursor keeps persistent context: rules (project, user, team), AGENTS.md and CLAUDE.md, skills as modes, Project shared context, automation and Grok Bot memories, past chats, and where each applies. Open for remember questions."
parent: lore-context.md
---

# Memory and personalization

Scope: everything that makes Cursor's agent behave the same way across sessions for one user,
project, or team. Checked 2026-10-14.

## Which mechanism is which

Cursor has **no general memory feature** for the coding agent today. Cursor staff said in the
forum (2025-11-25) that the 2025 "Memories" feature was removed in 2.1.x and told users to move
memories into rules. The current docs do not describe it. Rules are the documented way to make the
agent remember.

| Mechanism | What it is | Where it applies |
|---|---|---|
| **Project rules** | `.cursor/rules/*.mdc` with `alwaysApply`, `globs`, `description` | Editor, CLI, cloud agents (from the repo) |
| **AGENTS.md / CLAUDE.md** | Plain markdown instructions, nested `AGENTS.md` per folder | Editor, CLI, cloud agents |
| **User Rules** | Text in Customize → Rules; stored on the account; syncs | Agent (Chat) on all surfaces; cloud agents (best-practices page) |
| **`~/.cursor/rules` files** | User rule files on one machine; no sync | Local agents on that machine |
| **Team Rules** | Dashboard text, optional globs, optional enforcement | All members, all repos, cloud agents |
| **Skills and Custom Modes** | Reusable instructions; a mode stays on every turn | Where skills load |
| **Project shared context** | Files a Project's agents add and sync across machines | Inside one Project |
| **Automation memories** | `MEMORIES.md` notes across runs of one automation | That automation |
| **Grok Bot memory** | Preferences, role context, work summaries per Bot | Grok Bot only |
| **Past chats** | `@Chats` mention, conversation search, side chats | Local agent sessions |

Rules do not apply to Tab, inline edit (User Rules), or Bugbot (it uses `.cursor/BUGBOT.md`).

## Children

- [Rules and AGENTS.md](rules-and-agents-md.md) — rule types, precedence, sync, CLAUDE.md, and
  per-surface behavior.
- [Persistent context and history](persistent-context-and-history.md) — the end of Memories,
  Project context, automation and Grok Bot memories, past-chat features.

Sources: https://cursor.com/docs/rules.md ; https://cursor.com/help/customization/rules.md ;
https://cursor.com/docs/cloud-agent/best-practices.md ; https://cursor.com/docs/agent/projects.md ;
https://cursor.com/docs/cloud-agent/automations.md ; https://cursor.com/docs/grok-bot.md ;
https://forum.cursor.com/t/are-my-memories-gone/144057 (third-party)
