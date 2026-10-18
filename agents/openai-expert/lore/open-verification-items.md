---
lore: 1
type: topic
summary: "OpenAI questions to verify: MCP plan and surface support, desktop Lore, memory rollout, third-party reports, and Codex SDK packages, session controls, and usage exports. SDK questions added 2026-10-18; earlier items date from 2026-10-14."
parent: lore-context.md
---

# Open verification items

Items 1–7 date from 2026-10-14. Two research passes did not settle those facts. When a question depends on one,
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
8. **Codex SDK and managed-runtime details** (open questions added 2026-10-18; not reverified).
   The session discussion did not retain a complete source-to-claim record for these details:
   - Which Codex SDK packages and languages are current, and how do they differ from the general
     Agents SDK and the Codex app server?
   - Which session methods support queued follow-ups, steering, and interruption, and at which
     execution boundaries do they take effect?
   - Which usage, tracing, and export data covers root sessions and subagents, and which data is
     unsuitable for billing?
   Settle: check current official OpenAI documentation and the
   [Codex repository](https://github.com/openai/codex), then record sources for each supported
   behavior. The general SDK versus managed-harness distinction is already in
   [Developer platform](developer-platform.md), checked 2026-10-14; this question does not
   reverify or replace that record.

## Tell lore-architect when asked

`codex mcp-server` is removed (documented). lore-architect's notes that mention it can be out of
date. Detail: [Notes for agent-framework designers](notes-for-agent-framework-designers.md).

How to research these items: [Research method for OpenAI docs](research-method-for-openai-docs.md).
