---
lore: 1
type: area
summary: "How ChatGPT and Codex personalize: ChatGPT memory (summary, saved memories, chat history), projects, custom instructions, personality, writing style, Codex local memories, Computer History, and which applies on which surface."
parent: lore-context.md
---

# Memory and personalization

Scope: everything that makes ChatGPT or Codex respond differently for one user — what it remembers,
what it looks up from past work, and the instructions the user writes. Checked 2026-10-14.

## Which mechanism is which

The key fact: **ChatGPT memory and Codex memory are separate stores.** "ChatGPT web uses ChatGPT
memory, while local Codex clients use a separate local memory store and controls." (documented)

| Mechanism | What it is | Where it applies |
|---|---|---|
| ChatGPT memory | Account memory: a memory summary, saved memories, reference chat history | Chat and Work (web, desktop, mobile); dots use relevant ChatGPT memory |
| Project memory | Default or project-only memory per ChatGPT project | Chats in that project |
| Custom instructions and personality | Settings > Personalization (base style and tone) | ChatGPT; in Codex, personal instructions live in global `AGENTS.md` |
| Writing style | Learns the user's style from connected apps | ChatGPT Work on the web |
| Codex memories | Local memory files in `~/.codex/memories/`, off by default | Codex in the desktop app, CLI, IDE on that machine |
| Computer History | Opt-in macOS timeline of app and web activity, turned into memories | Desktop app (Pro, Business, Enterprise) |
| `AGENTS.md` | Required rules, not memory | Codex host and local Work |

Memory is built into the products. It is not an MCP server.

## Children

- [ChatGPT memory, projects, and instructions](chatgpt-memory-projects-and-instructions.md) —
  the 2026 memory system, controls, projects and project memory, custom instructions.
- [Codex memories and Computer History](codex-memories-and-computer-history.md) — the local
  memory store, its settings, and Computer History.
