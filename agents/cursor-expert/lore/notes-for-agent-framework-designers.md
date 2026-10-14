---
lore: 1
type: topic
summary: "Cursor mechanisms an agent-framework designer should know (2026-10-14): Claude and Codex compatibility layers, open standards, MCP server design hints, cloud VM sockets, subscriptions, orchestration, SDK custom tools, and company context."
parent: lore-context.md
---

# Notes for agent-framework designers

Checked 2026-10-14. Documented unless a line says otherwise. Each item links to the topic with
detail.

## Cursor reads other tools' config

- Skills from `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/`.
  Subagents from `.claude/agents/` and `.codex/agents/` (`.cursor/` wins on name conflicts)
  ([skills, subagents, commands](skills-subagents-and-commands.md)).
- `CLAUDE.md` is read like `AGENTS.md` and is always applied ([rules](rules-and-agents-md.md)).
- Claude Code hooks from `.claude/settings*.json`, with name mapping and both response formats;
  exit code `2` blocks; `CLAUDE_PROJECT_DIR` is set ([hooks](hooks.md)).
- The CLI shows plugins imported from Claude Code. lore-architect found that Cursor falls back to
  `.claude-plugin/marketplace.json` when `.cursor-plugin/marketplace.json` is absent (read from
  Cursor's shipped code, not from docs).
- One setting governs most of this: "Include Third-Party Plugins, Skills, and Other Configs"
  (Settings → Agents → Third-Party Imports, on by default).

## Open standards Cursor supports

Agent Skills (agentskills.io), Agent Plugins (agent-plugins.org; Cursor does not expand
`${PLUGIN_ROOT}`), AGENTS.md (nested), MCP with the MCP Apps extension, and ACP (Agent Client
Protocol: `agent acp` serves JetBrains and custom clients).

## Hints for MCP server authors

- Prefer streamable HTTP: it is the only remote transport with no doc conflict on cloud surfaces.
- Do not rely on a committed `.cursor/mcp.json` to reach cloud agents or self-hosted workers: they
  read only dashboard config ([remote MCP by surface](remote-mcp-by-surface.md)).
- Mark destructive tools with `_meta["cursor/requiresConfirmation"]: true` in `tools/list`;
  Cursor prompts before every call to them, even under Auto-review ([MCP](mcp-in-cursor.md)).
- Support OAuth DCR, or register both fixed redirect URLs
  (`https://www.cursor.com/agents/mcp/oauth/callback`, `http://localhost:8787/callback`).
- Expect per-user OAuth, no approvals in the cloud, tool-count caps per model, and an
  `mcp_auth_error` event that skips the server and continues the run.
- MCP Apps UI must degrade to a plain tool result. Images return as base64 content.

## Cloud agent runtime features

- A local socket serves agent metadata (`http://cursor-agent/v1/meta-data/...`: agent id, owner,
  turn, model, repo URLs) and short-lived OIDC tokens for cloud federation.
- The built-in **Cursor Cloud MCP** lets an agent read its own run, events, transcripts, and
  environment Builds.
- **Subscriptions** let an agent end its turn and wake on GitHub, Slack, Linear, or timer events
  for up to 180 days. `/loop` and `/goal` give long-lived objectives ([cloud agents](cloud-agents.md)).

## Orchestration patterns in the product

- Subagents through the Task tool; one extra nesting level; background subagents write to
  `~/.cursor/subagents/`; resume by agent ID; isolation by worktree or VM.
- **Projects**: a coordinator agent that delegates and does no coding, with shared context files
  synced across machines — close to a persistent team lead.
- **Automation memories** (`MEMORIES.md` outside the workspace) — file-based memory like Lore's
  approach, scoped to one automation.

## SDK

`@cursor/sdk` and the Python SDK run the same agent harness locally or in the cloud. Custom tools
on `local.customTools` are exposed as an MCP server named `custom-user-tools`. `local.settingSources`
picks which on-disk layers load (`project` = `.cursor/`, `user` = `~/.cursor/`, `plugins`); without
it, a local agent loads only inline MCP servers. It does not apply to cloud agents.
`local.autoReview` adds the Auto-review classifier to headless runs.

## Company context

- Cursor (Anysphere) is part of SpaceX since 2026-08-14. Its frontier models (Grok 4.5–4.7) are
  co-trained with SpaceXAI. The X Subscription (2026-10-12) bundles Cursor with Grok and X.
- Cursor builds its own git forge (Origin, with an MCP server) and a general agent product (Grok
  Bot). Inference: Cursor's scope now reaches well beyond the editor.

Sources: https://cursor.com/docs/skills.md ; https://cursor.com/docs/subagents.md ;
https://cursor.com/docs/reference/third-party-hooks.md ; https://cursor.com/docs/plugins.md ;
https://cursor.com/docs/mcp.md ; https://cursor.com/docs/api/origin/mcp.md ;
https://cursor.com/docs/cloud-agent/capabilities.md ; https://cursor.com/docs/cloud-agent/metadata.md ;
https://cursor.com/docs/agent/projects.md ; https://cursor.com/docs/cloud-agent/automations.md ;
https://cursor.com/docs/sdk/typescript.md ; https://cursor.com/blog/joining-spacex ; https://x.ai/news/x-subscription
