---
lore: 1
type: topic
summary: "OpenAI questions to verify: MCP plan and surface support, desktop Lore, memory rollout, third-party reports, Codex SDK details (2026-10-18), and Codex multi-agent v2 wait controls (2026-10-22). Others date from 2026-10-14."
parent: lore-context.md
---

# Open verification items

Items 1–7 date from 2026-10-14, and two research passes did not settle them. Items 8 and 9 have
their own dates. When a question depends on one, check it first, in a browser or with a hands-on
test. If I cannot check it, I say that it is unverified. The evidence for each item is in the linked topic. This list holds only the open
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
   - Pro tier usage multipliers — [Plans and pricing](plans-and-pricing.md);
   - Codex subagent concurrency default of 6, with spawns that queue at the cap (added 2026-10-24) —
     [Codex configuration and extensibility](codex-configuration-and-extensibility.md).
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
9. **Codex multi-agent v2 waits in a real run** (added 2026-10-22, codex-cli 0.160.0). The
   source defines both controls, but no run tested them. A real run on 2026-10-24 confirmed
   `spawn_agent` with `fork_turns: "none"`, a custom-role child model, and `followup_task`. It did
   not test the waits, so this item stays open. Evidence:
   [Codex multi-agent v2 bindings](codex-multi-agent-v2-bindings.md).
   - Do the `[features.multi_agent_v2]` keys `min_wait_timeout_ms`, `default_wait_timeout_ms`, and
     `max_wait_timeout_ms` change the `wait_agent` timeouts in a real hub run?
   - Does a sentence in `AGENTS.md` or in the task prompt override the 60-second rule in the base
     instructions, so that a hub waits for minutes?
   Settle: run a small hub with `codex exec`, one time with the wait floor in config and one time
   with only a prompt sentence. Read the `wait_agent` calls and their `timeout_ms` values in the
   rollout files ([Codex session logs and resume](codex-session-logs-and-resume.md)).

## Tell lore-architect when asked

`codex mcp-server` is removed (documented). lore-architect's notes that mention it can be out of
date. Detail: [Notes for agent-framework designers](notes-for-agent-framework-designers.md).

How to research these items: [Research method for OpenAI docs](research-method-for-openai-docs.md).
