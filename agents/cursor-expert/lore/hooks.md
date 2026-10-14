---
lore: 1
type: topic
summary: "Cursor hooks (2026-10-14): event list, hooks.json sources and priority, merge rules, cloud-agent and self-hosted support, team and MDM distribution, environment variables, and Claude Code hook compatibility."
parent: lore/extension-platform.md
---

# Hooks

Checked 2026-10-14. Documented unless a line says otherwise.

## What hooks are

Spawned processes that talk JSON over stdio. They run before or after stages of the agent loop and
can observe, block, or change behavior. Exit code `2` blocks the action, "to match Claude Code".
Command hooks are the norm; prompt-based hooks also exist (not in cloud agents).

## Events

- Agent: `sessionStart`, `sessionEnd`, `preToolUse`, `postToolUse`, `postToolUseFailure`,
  `subagentStart`, `subagentStop`, `beforeShellExecution`, `afterShellExecution`,
  `beforeMCPExecution`, `afterMCPExecution`, `beforeReadFile`, `afterFileEdit`,
  `beforeSubmitPrompt`, `preCompact`, `stop` (with `loop_limit`), `afterAgentResponse`,
  `afterAgentThought`.
- Tab: `beforeTabFileRead`, `afterTabFileEdit`.
- App: `workspaceOpen` (can return plugin paths to load).
- 3.24: shell and MCP hooks get a `tool_use_id` that matches `preToolUse`; every hook gets
  `transcript_path` when a `.jsonl` transcript exists.

## Sources and priority

Enterprise (MDM file: `/Library/Application Support/Cursor/hooks.json`, `/etc/cursor/hooks.json`,
`C:\ProgramData\Cursor\hooks.json`) → Team (dashboard, Enterprise only, synced every 30 minutes) →
Project (`.cursor/hooks.json`, trusted workspaces only) → User (`~/.cursor/hooks.json`). All
matching hooks run. `deny` beats `ask` beats `allow`. Plugins can also carry hooks.

## Environment variables

`CURSOR_PROJECT_DIR`, `CURSOR_VERSION`, `CURSOR_USER_EMAIL`, `CURSOR_TRANSCRIPT_PATH`,
`CURSOR_CODE_REMOTE`, and `CLAUDE_PROJECT_DIR` (an alias for Claude compatibility).

## Per surface

| Surface | Hooks that run |
|---|---|
| Editor, Agents Window, CLI | All sources and events (CLI fixes for `afterAgentThought`/`afterAgentResponse` in April 2026) |
| Cursor-hosted cloud agents | Repo `.cursor/hooks.json`; team and managed hooks on Enterprise. Command hooks only. Supported: shell, read, edit, tool, subagent, prompt, compact, response, thought, stop. Not: `sessionStart`, `sessionEnd`, MCP hooks, Tab hooks, `workspaceOpen`, user hooks |
| Self-hosted workers | Same as cloud, plus `sessionStart`/`sessionEnd` on claim and release |

Hooks do not run during early read-only exploration turns in the cloud.

## Claude Code compatibility

With "Include Third-Party Plugins, Skills, and Other Configs" on (default), Cursor loads Claude
Code hooks from `.claude/settings.local.json`, `.claude/settings.json`, and
`~/.claude/settings.json`, below all Cursor sources in priority. It maps Claude hook names to
Cursor events and accepts both Claude's nested `hookSpecificOutput` format and the flat format.

Sources: https://cursor.com/docs/hooks.md ; https://cursor.com/docs/reference/third-party-hooks.md ;
https://cursor.com/help/ai-features/cloud-agents.md ; https://cursor.com/docs/cli/changelog.md ;
https://cursor.com/docs/release-notes.md
