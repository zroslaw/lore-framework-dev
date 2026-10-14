---
lore: 1
type: topic
summary: "OpenAI features an agent-framework designer should know that differ from Claude (2026-10-14): portable plugins, import with sync, cloud-coordinated local work, dots, MCP Events, MCP hooks, plan sign-in, removed codex mcp-server."
parent: lore-context.md
---

# Notes for agent-framework designers

Checked 2026-10-14. Each fact is documented in the linked topics unless marked. The "why it
matters" lines are my inference.

- **One package for two products.** Plugins use one universal directory for ChatGPT and Codex, a
  portable `plugin.json` (agent-plugins.org schema), and still accept Claude-compatible manifests
  and `.claude-plugin/marketplace.json`. OpenAI even documents converting a Claude Code plugin.
  Why it matters: a Lore-style plugin could target Claude Code and Codex from one tree
  ([packaging](plugins-packaging-and-publishing.md)).
- **Import with continuous sync.** The desktop app imports instructions, skills, plugins, hooks,
  MCP config, subagents, and recent chats from Claude Code, Claude Cowork, and Cursor, and can keep
  them in sync ([Codex configuration](codex-configuration-and-extensibility.md)). Why it matters:
  users may run the same agent files in both ecosystems without noticing.
- **Cloud-coordinated local execution.** Work with local computer access is orchestrated in the
  cloud but runs steps on a connected computer, and falls back to a cloud container when the
  computer is offline. Claude has no exact match ([surfaces](chat-work-codex-and-dots.md)).
- **Dots** are persistent agents with their own cloud computer, Slack and Teams presence, self-set
  wake-ups, and private notes. They are the nearest product to "an agent with a lasting identity",
  which is Lore's core idea, but their memory is OpenAI-hosted, not git-backed.
- **MCP Events**: ChatGPT subscribes to server events through webhooks (MCP 2.0 protocol
  `2026-07-28`). An MCP server can wake a Work chat or a dot ([remote MCP](remote-mcp-per-surface.md)).
- **Hooks can call MCP tools**, run in the background, and need hash-based trust. In
  cloud-orchestrated Work and dots, only admin-defined remote MCP hooks run.
- **`codex mcp-server` is removed.** Anything that drove Codex as an MCP server must move to the
  Codex app server (JSON-RPC, experimental). lore-architect's notes on `codex mcp-server` (topic
  `engine-session-log-formats.md`) may be out of date — inference, flag to lore-architect.
- **Sign in with ChatGPT plan usage**: an open-source client can use a Plus or Pro user's ChatGPT
  plan for model calls ([developer platform](developer-platform.md)).
- **Agents API** runs the Codex harness as a managed service, so "Codex as a backend" exists
  without hosting the CLI.
- **Skill budgets**: Codex lists skills in at most 2% of context (8,000 characters if unknown);
  `AGENTS.md` total is capped at 32 KiB by default. Large Lore maps or many skills can be cut.
- **Memory hygiene**: Codex can keep chats that used MCP or web search out of memory generation
  (`memories.disable_on_external_context`).
- **Record & Replay** turns a demonstrated macOS workflow into a skill; **Plugin Extensions** add
  sidebars, panels, and editors to ChatGPT; **Sites** host web apps that use each visitor's
  connected plugins.
- **Shared thread snapshots**: read-only links to a local Codex thread, with secret redaction.

Sources: see the linked topics; plus https://learn.chatgpt.com/docs/whats-new/devday-2026 and
https://learn.chatgpt.com/docs/use-chatgpt
