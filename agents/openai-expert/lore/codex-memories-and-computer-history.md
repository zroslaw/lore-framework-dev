---
lore: 1
type: topic
summary: "Codex local memories (off by default, ~/.codex/memories/, per-chat /memories control, config keys) and Computer History (opt-in macOS activity timeline for Pro, Business, Enterprise). Open for what Codex remembers between sessions."
parent: lore/memory-and-personalization.md
---

# Codex memories and Computer History

Checked 2026-10-14. Documented.

## Codex memories

- **Off by default.** Turn on in the desktop app (Settings > Personalization > **Enable Codex
  memories**) or with `[features] memories = true` in `config.toml`. Per machine.
- Codex turns eligible past chats into memory files under `~/.codex/memories/` (summaries, durable
  entries, recent inputs, evidence). It skips active or short chats, redacts secrets, and updates
  in the background after a chat goes idle. It can skip a pass when rate-limit headroom is low.
- `/memories` (desktop app and CLI) sets, per chat, whether the chat uses memories and whether it
  feeds future ones. The IDE extension uses the host's store.
- Keys: `memories.generate_memories`, `memories.use_memories`,
  `memories.disable_on_external_context` (keeps chats that used MCP, web search, or tool search out
  of memory generation), `memories.min_rate_limit_remaining_percent`, `memories.extract_model`,
  `memories.consolidation_model`.
- Treat the files as generated state; keep required rules in `AGENTS.md`.
- Import can bring Claude Code project memories into Codex memories
  ([Codex configuration](codex-configuration-and-extensibility.md)).

## Computer History

- Opt-in, macOS desktop app. Turns activity in allowed apps and websites (interaction events,
  accessibility text; no screenshots, no audio) into a searchable timeline and memories that
  ChatGPT and Codex can use.
- Plans: Pro, Business, Enterprise (admins must enable it for Business and Enterprise); not Plus.
  Launched 2026-08-10 to 14; EEA, Switzerland, and UK from 2026-08-17 to 21.
- Users can pause it, exclude apps and sites, and delete items or all history. **Delete Codex
  memories** also clears Computer History on that machine.

Sources: https://learn.chatgpt.com/docs/customization/memories ;
https://learn.chatgpt.com/docs/customization/computer-history ; https://learn.chatgpt.com/docs/pricing ;
https://learn.chatgpt.com/docs/whats-new
