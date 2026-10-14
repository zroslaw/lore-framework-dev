---
lore: 1
type: topic
summary: "Cursor skills (Agent Skills standard, locations, frontmatter, built-in skills, cloud sync, team publish), subagents (locations, fields, nesting, cloud subagents, billing), and slash commands. Includes Claude and Codex compatibility paths."
parent: lore/extension-platform.md
---

# Skills, subagents, and commands

Checked 2026-10-14. Documented unless a line says otherwise.

## Skills

- Cursor follows the open **Agent Skills** standard (agentskills.io). A skill is a folder with
  `SKILL.md` plus optional `scripts/`, `references/`, `assets/`.
- Locations: `.agents/skills/`, `.cursor/skills/` (project); `~/.agents/skills/`,
  `~/.cursor/skills/` (user, this machine). For compatibility Cursor also loads `.claude/skills/`,
  `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/`.
- Nested folders are scanned recursively. A `.cursor/skills/` inside a subdirectory is scoped to
  files under that directory.
- Frontmatter: `name` (must match the folder), `description` (both required); `paths` (globs),
  `disable-model-invocation`, `icon`, `color`, `metadata`.
- The agent picks skills by description, or the user types `/skill-name` (one message) or uses it
  as a **Custom Mode** (Option+Enter; stays on every turn).
- `/skills` in the CLI warns about spec limits: name over 64 characters, description over 1,024
  characters, body over about 5,000 tokens (CLI v2026.10.08).
- Built-in skills include `/automate`, `/autopilot`, `/canvas`, `/create-hook`, `/create-rule`,
  `/create-skill`, `/create-subagent`, `/cursor-blame`, `/loop`, `/migrate-to-skills`, `/review`,
  `/review-bugbot`, `/review-security`, `/sdk`, `/shell`, `/split-to-prs`, `/statusline`.
- **Cloud agents**: project skills always load. Personal skills load only after **Sync Skills for
  Cloud Agents** (Settings → Agents), which copies `~/.cursor/skills/` only, private to the user.
  Admins can disable sync for a team. Unsynced and `~/.agents/skills/` skills never reach cloud
  agents, Remote SSH sessions in the Agents Window, or self-hosted workers.
- **Share with a team**: publish a personal skill to the Default team marketplace (Teams,
  Enterprise). Cursor packs it into a plugin in a Cursor-hosted repo.

## Subagents

- The agent starts subagents with the **Task** tool. Each has a clean context and returns one
  final message. Foreground (blocking) or background (`is_background`). Several run in parallel.
- Built-in: **Explore** (fast model, parallel search) and **Browser** (browser via MCP). One help
  page also names **Bash**.
- Custom definitions: `.cursor/agents/`, `.claude/agents/`, `.codex/agents/` (project) and the same
  under `~/` (user). `.cursor/` wins on name conflicts. Fields: `name`, `description`, `model`
  (`inherit` default), `readonly`, `is_background`. Invoke with `/name` or by asking.
- Nesting (since 2.5): the main agent and its direct subagents can start subagents; a
  grandchild cannot. Resume a subagent by its agent ID.
- Isolation on request: each subagent in its own git worktree or its own cloud VM.
- **Cloud subagents** (`/in-cloud`, `/autopilot`, Agents Window): run on a VM and use the team's
  cloud MCP servers, not the local session's.
- Billing: each request bills at the model that ran it. A named third-party model draws from Other
  Models even when the parent is on Auto, Grok, or Composer. On legacy request plans without Max
  Mode, subagents run on Composer.

## Commands

- Reusable prompts invoked with `/` in Agent chat; markdown files in `.cursor/commands/` (project),
  at user level, as team commands from the dashboard, or in plugins (`commands/`, `.md` or `.txt`).
- `/migrate-to-skills` converts slash commands to skills with `disable-model-invocation: true`
  and converts "Apply Intelligently" rules to skills (since 2.4).

Sources: https://cursor.com/docs/skills.md ; https://cursor.com/docs/subagents.md ;
https://cursor.com/help/models-and-usage/available-models.md ; https://cursor.com/docs/customize-cursor.md ;
https://cursor.com/docs/reference/plugins.md ; https://cursor.com/docs/reference/deeplinks.md ;
https://cursor.com/docs/enterprise/llm-safety-and-controls.md ; https://cursor.com/docs/release-notes.md
