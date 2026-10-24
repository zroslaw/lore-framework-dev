---
lore: 1
type: topic
summary: "How a Codex host is extended (2026-10-14; subagents 2026-10-24): AGENTS.md discovery, skills, config.toml layers, hooks, subagents, custom agents, the concurrency cap, and import from Claude Code, Cowork, or Cursor."
parent: lore/extension-platform.md
---

# Codex configuration and extensibility

Checked 2026-10-14. Documented unless a line says otherwise. These apply to the ChatGPT desktop app
(Codex and local Work), Codex CLI, and the IDE extension on the same host.

## AGENTS.md

- Global: `~/.codex/AGENTS.override.md` or `AGENTS.md` (first non-empty). Project: from the Git
  root down to the working directory, one file per directory (`AGENTS.override.md`, then
  `AGENTS.md`, then `project_doc_fallback_filenames`). Files closer to the working directory come
  later and win. Limit `project_doc_max_bytes` = 32 KiB by default.
- Personal custom instructions in Codex live in the global `AGENTS.md`.
- `## Code Review Rules` sections guide GitHub code review.

## Skills

- Locations: `$CWD/.agents/skills` up to `$REPO_ROOT/.agents/skills` (REPO), `$HOME/.agents/skills`
  (USER), `/etc/codex/skills` (ADMIN), bundled (SYSTEM: `skill-creator`, `plan`, and others).
  Symlinks are followed. Same-name skills are not merged.
- Progressive disclosure: the initial list (name, description, path) uses at most 2% of context
  (or 8,000 characters); `skills.max_context_tokens` up to 10,000.
- Invoke with `$skill` or `/skills`, or implicitly by description. `$skill-installer` adds curated
  skills. Disable one with `[[skills.config]] path = ... enabled = false`.
- Custom prompts are deprecated; use skills.

## config.toml layers

- `~/.codex/config.toml` (user), `.codex/config.toml` (trusted projects only), system and
  cloud-managed configuration, and `requirements.toml` (enforced by admins). Separate profile
  files can live under `CODEX_HOME`.

## Hooks (GA since 2026-05)

- Events: `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`,
  `PostToolUse`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `Stop`, `Interrupt`.
- Sources: `hooks.json` or `[hooks]` in any config layer, and plugin-bundled hooks. All matching
  hooks run; command hooks for one event run concurrently.
- Non-managed hooks need review and **trust** (by hash) in `/hooks`; managed hooks are trusted by
  policy. `--dangerously-bypass-hook-trust` skips trust for one run.
- Handlers can be commands or **MCP tool hooks**; background hooks exist.
- Cloud-orchestrated Work and dots run only admin-defined remote MCP hooks; command hooks and
  plugin hooks do not run there.

## Subagents

- On by default in current Codex releases; `/subagents` in the CLI. ChatGPT Work also runs
  subagents in its hosted environment; **Ultra** reasoning delegates proactively.
- Custom agents: TOML files in `~/.codex/agents/` or `.codex/agents/`; limits under `[agents]`
  (`max_concurrent_threads_per_session`, `default_subagent_model`,
  `default_subagent_reasoning_effort`). A role can also be defined on the command line with
  `-c agents.<name>.description=...` and `-c agents.<name>.config_file=...`; its model and
  effort apply to the child (observed locally 2026-10-24, codex-cli 0.160.0).
- Concurrency cap (checked 2026-10-24): `agents.max_concurrent_threads_per_session` counts
  subagents only, not the primary thread. `agents.max_threads` is a legacy alias. The docs do
  not state the default ("Codex chooses the default"). Blogs say 6, and that spawns queue at the
  cap — third-party report, unverified.
- Messages between subagents: the docs describe none; coordination goes through the parent. The
  `agent_message_board` feature is still under development and off (checked 2026-10-24). But in
  a local test (codex-cli 0.160.0, 2026-10-24) a child called `send_message` with a sibling's
  path `/root/<task_name>` and the sibling received it directly, with no parent relay. Detail:
  [Codex multi-agent coordination](codex-multi-agent-coordination.md).
- The old URL developers.openai.com/codex/subagents redirects (308) to
  https://learn.chatgpt.com/docs/agent-configuration/subagents (checked 2026-10-24).
- Multi-agent v2 (checked in source for codex-cli 0.160.0 on 2026-10-22; spawn and
  `followup_task` tested 2026-10-24): `spawn_agent` `fork_turns` sets how much parent history a
  child gets; `wait_agent` waits 10 seconds to one hour; the base 60-second rule can keep a hub's
  waits short. Detail:
  [Codex multi-agent v2 bindings](codex-multi-agent-v2-bindings.md).

## Import from another agent (2026-08-11)

- The desktop app imports from **Claude Code, Claude Cowork, or Cursor**; Codex CLI `/import` from
  Claude Code or Cursor (up to 50 chats from the last 30 days).
- Mapping: instruction files → `AGENTS.md`; `settings.json` → `config.toml`; skills → skills;
  plugins → plugins; slash commands → skills; subagents → Codex subagents; hooks → Codex hooks;
  MCP config → Codex MCP config; Claude Code project memories → Codex memories. The desktop app
  can keep imports in sync.

Sources: https://learn.chatgpt.com/docs/agent-configuration/agents-md ;
https://learn.chatgpt.com/docs/build-skills ; https://learn.chatgpt.com/docs/hooks ;
https://learn.chatgpt.com/docs/agent-configuration/subagents ; https://learn.chatgpt.com/docs/import ;
https://learn.chatgpt.com/docs/config-file/config-basic ; https://learn.chatgpt.com/docs/custom-prompts
