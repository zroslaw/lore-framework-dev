---
lore: 1
type: topic
summary: "Cursor skills, slash commands, and subagents: locations, cloud sync, nesting, billing, parent-only Task returns with no sibling channel, CLI-tested resume by ID, transcript paths, and parallel counts. Includes Claude and Codex paths."
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
- Nesting (since 2.5, documented): the main agent and its direct subagents can start subagents; a
  subagent spawned by a direct subagent cannot start further subagents. Resume a subagent by its
  agent ID.
- **Inference** (checked 2026-10-24, one Cursor editor session): the cap is missing **Task**, not
  only policy text. A level-1 subagent (child of the main agent) has Task and a child spawn
  succeeds. A level-2 subagent has no Task, so it cannot spawn level-3. The same level-1 parent can
  still spawn a grandchild with its own Task call.
  Treat depth as **at most one hop below the main agent's direct subagents**. For deeper trees,
  the main agent or a level-1 subagent must issue more Task calls; do not expect the level-2 worker
  to delegate further.
- Isolation on request: each subagent in its own git worktree or its own cloud VM.
- **Cloud subagents** (`/in-cloud`, `/autopilot`, Agents Window): run on a VM and use the team's
  cloud MCP servers, not the local session's.
- Billing: each request bills at the model that ran it. A named third-party model draws from Other
  Models even when the parent is on Auto, Grok, or Composer. On legacy request plans without Max
  Mode, subagents run on Composer.

## Who a subagent can reach

Checked 2026-10-24. The missing sibling channel is a Cursor platform limit. A model choice,
including Composer 2.5, does not add a channel between subagents.

- **Documented** (https://cursor.com/docs/subagents.md): a subagent starts with a clean context.
  The parent must put needed context in the Task prompt. The subagent returns one final message
  to the parent. Parallel Task calls run siblings at the same time. They do not share a transcript.
- **Inference** from one Cursor session on 2026-10-24, consistent with that page:
  - Two subagents exchange a message only when the parent copies one reply into the next Task
    prompt. There is no direct send.
  - `resume` with the same agent id continues that subagent's own thread. A new Task without
    `resume` starts clean. `resume: "self"` forks the parent. It does not open a sibling.
  - The parent has no roster of live subagents. It has only the agent ids it stored.
  - A background run ends when the subagent returns a final answer. A long `sleep` does not park
    a worker. The model can answer and finish the turn early.
  - `interrupt: true` on `resume` stops a running subagent. There is no delete or destroy tool
    for an agent id. After a stop, `resume` still works.
- **Tested in the CLI** (ran it, 2026-10-24, `cursor-agent` 2026.10.22-27dcf5f):
  - Run: `cursor-agent -p --force --trust --model gpt-5.6-terra-medium "<prompt>"` in a folder
    with `.cursor/agents/memtest.md` (frontmatter `name`, `description`,
    `model: gemini-3.7-flash-low`). The main thread called `subagent_type: "memtest"`.
  - The tool is `Subagent({description, prompt, subagent_type, run_in_background})`, called
    through `CallDynamicTool`. A second call `Subagent({..., resume: "<id>"})` continues the same
    subagent. In 3 of 3 runs the subagent recalled its first brief: resume keeps the full context.
  - The transcript does not record a model name. The subagent `model` field is set, but the model
    that ran is not confirmed.
  - Transcripts: `~/.cursor/projects/<path-slug>/agent-transcripts/<chat id>/subagents/<subagent
    id>.jsonl`. The first turn and the resumed turn are in the same file.
- **Parallel count** (third-party report, forum; no official cap found): a staff post
  (2026-02-24) says "the model decides how many sub-agents to run in parallel". Users saw 3–4
  unless the prompt names a number. Subagents run in batches: the next batch waits for all of the
  previous batch. A reply on 2026-07-02 (staff role not confirmed) says there is no fixed limit,
  but "multiple dozens may run into issues".
  https://forum.cursor.com/t/subagents-dont-maximize-parallel-dispatch/152679 ;
  https://forum.cursor.com/t/what-is-maximum-sub-agent-creation-limit/164696
- Patterns that fit this shape: the parent orchestrates and passes a structured handoff; a shared
  file can be a mailbox (watch write races on one checkout); use a worktree or a cloud VM when
  siblings edit the same tree; use a Project when the work is long-lived. A Project is a
  coordinator hub, and Agent SDK peers are separate full agents, not a relay for these subagents
  ([editor and Agents Window](editor-agents-window-and-modes.md),
  [integrations and public API](integrations-and-public-api.md)).

## Commands

- Reusable prompts invoked with `/` in Agent chat; markdown files in `.cursor/commands/` (project),
  at user level, as team commands from the dashboard, or in plugins (`commands/`, `.md` or `.txt`).
- `/migrate-to-skills` converts slash commands to skills with `disable-model-invocation: true`
  and converts "Apply Intelligently" rules to skills (since 2.4).

Sources: https://cursor.com/docs/skills.md ; https://cursor.com/docs/subagents.md ;
https://cursor.com/help/models-and-usage/available-models.md ; https://cursor.com/docs/customize-cursor.md ;
https://cursor.com/docs/reference/plugins.md ; https://cursor.com/docs/reference/deeplinks.md ;
https://cursor.com/docs/enterprise/llm-safety-and-controls.md ; https://cursor.com/docs/release-notes.md
