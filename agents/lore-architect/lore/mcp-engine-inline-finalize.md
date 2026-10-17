---
lore: 1
type: topic
summary: "MCP chat finalization is chat-inline: reflect and merge in the session; server stores no reflections; finalize alone publishes."
parent: lore-context.md
---

# MCP Engine — Inline Finalize

The Lore MCP surface (`docs/engines/mcp.md`, `docs/mcp-finalize-workflow.md`) is a shipped engine
profile, confirmed by the Lore MCP 0007–0009 product release (`lore-mcp-poc` `553e75b`, framework
pin `fd9e597`).

## Finalization shape

- **Reflect and merge run inline in the chat.** There is no subagent spawn on this surface; merge
  stays lossless because it is optimization-class
  (`subagent-as-optimization-vs-subagent-as-semantics.md`). This is the MCP instance of the
  reflect/merge asymmetry — both phases stay in the host conversation
  (`reflect-merge-execution-asymmetry.md`).
- **The server does not store reflections.** Procedure docs must not mention a `write_reflections`
  tool.
- **`finalize` is the only publication action.** Topic deletion uses `delete:topic:…`.

## Authority and release hygiene

- When the MCP product and framework docs disagree, **the MCP engine profile wins** for MCP chat
  sessions.
- Before a product release check, keep the vendored pin on `lore-framework` `main`.

## Related

- `docs/engines/mcp.md` — the five adapter bindings for this surface
- `docs/mcp-finalize-workflow.md` — the chat-side finalize procedure
- `finalization-process.md` — the four-phase lifecycle this surface adapts
- `multi-engine-portability-direction.md` — engines as profile adapters
