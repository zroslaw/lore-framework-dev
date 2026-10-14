---
lore: 1
type: topic
summary: "OpenAI facts that research could not settle (2026-10-14): custom MCP plan gating, custom MCP on mobile, MCP in Codex Cloud, MCP prompts, lr in desktop Codex, memory rollout, third-party-only facts. Check before relying on them."
parent: lore-context.md
---

# Open verification items

As of 2026-10-14. Two research passes did not settle these facts. When a question depends on one,
check it first, in a browser or with a hands-on test. If I cannot check it, I say that it is
unverified. The evidence for each item is in the linked topic. This list holds only the open
question and how to settle it. When an item is settled, update the linked topic and remove the
item here.

1. **Plans that can use "Add custom MCP server" in ChatGPT.** No primary page lists the plans, and
   third-party sources conflict. Evidence: [Remote MCP per surface](remote-mcp-per-surface.md),
   "Plan gating". Settle: read help article 12584461 in a browser.
2. **A custom-MCP plugin on ChatGPT mobile.** Plugins work on mobile (documented), but no page says
   that a personal plugin made from a custom MCP server works there. Evidence:
   [Remote MCP per surface](remote-mcp-per-surface.md), "Mobile". Settle: add the server on the
   web, install the plugin, then call it with `@` in the iOS or Android app.
3. **MCP in Codex Cloud tasks.** Not documented. One changelog entry mentions cloud plugin
   discovery in the MCP extension. Evidence: [Remote MCP per surface](remote-mcp-per-surface.md),
   "Codex Cloud". Settle: test with a published environment.
4. **MCP prompts.** No ChatGPT or Codex behavior is documented. Evidence:
   [Remote MCP per surface](remote-mcp-per-surface.md). Settle: recheck the MCP pages of both doc
   sites at each refresh.
5. **Lore `lr` in Codex inside the ChatGPT desktop app.** My inference is that it loads from the
   shared `~/.codex/plugins/cache`. Untested. Evidence:
   [Lore compatibility on OpenAI surfaces](lore-compatibility-on-openai-surfaces.md). Settle:
   install `lr` and boot an agent from Codex in the desktop app.
6. **Memory-summary rollout to Free and Go** (the new memory system, June 2026). Not confirmed.
   Evidence: [ChatGPT memory, projects, and instructions](chatgpt-memory-projects-and-instructions.md).
   Settle: read the Memory FAQ in a browser, or find the rollout in the What's new digest.
7. **Facts from third-party reports only:**
   - agent mode retirement in August 2026 — [Chat, Work, Codex, and dots](chat-work-codex-and-dots.md);
   - Atlas shutdown on 2026-08-09 — [Browser, Computer Use, and Atlas](browser-computer-use-and-atlas.md);
   - Pro tier usage multipliers — [Plans and pricing](plans-and-pricing.md).

## Tell lore-architect when asked

`codex mcp-server` is removed (documented). lore-architect's notes that mention it can be out of
date. Detail: [Notes for agent-framework designers](notes-for-agent-framework-designers.md).

How to research these items: [Research method for OpenAI docs](research-method-for-openai-docs.md).
