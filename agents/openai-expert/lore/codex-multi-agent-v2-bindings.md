---
lore: 1
type: topic
summary: "Codex multi-agent v2 hub bindings (codex-cli 0.160.0; source 2026-10-22, run 2026-10-24): fork_turns, child model via custom role, followup_task, wait_agent timeouts, the 60-second rule, exec_command polling."
parent: lore/extension-platform.md
---

# Codex multi-agent v2 bindings

Checked 2026-10-22 against codex-cli 0.160.0. Source: the openai/codex source at tag
`rust-v0.160.0` (`multi_agents_v2/spawn.rs`, `wait.rs`, `agent/child_config.rs`,
`config/mod.rs`, `unified_exec/mod.rs`, `process_manager.rs`) and local rollout logs.

Label: **documented in source** (I read the code), unless a line says otherwise. The official docs
do not describe `fork_turns` or the wait settings. The subagents doc agrees on model inheritance.
The latest stable CLI is newer than 0.160.0 ([Codex surfaces](codex-surfaces.md)). Recheck the
source at the installed tag before you rely on a number here.

Use this topic when you design a hub: a root Codex session that starts role subagents and waits
for them. The general subagent facts (custom agents, `[agents]` limits) are in
[Codex configuration and extensibility](codex-configuration-and-extensibility.md). Lore's own use
of this subsystem belongs to lore-architect (its `codex-native-multi-agent-subsystem.md` topic).

## spawn_agent: what the child gets

- `fork_turns: "all"` (or no value) copies the full parent history. The child inherits the parent
  model and effort, and it does not accept a model or effort override.
- `fork_turns: "none"` starts a new thread. The child gets only these items: the base
  instructions; the skills, permissions, and plugins messages; the multi-agent message;
  `AGENTS.md`; the environment context; the config `developer_instructions`; and the task message.
- A positive integer copies the last N turns. In `codex exec`, the first turn holds the full task
  prompt, so `"1"` is almost the same as `"all"`.
- Model and effort with `"none"`: use the arguments `model` and `reasoning_effort`. If you omit
  them, `[agents] default_subagent_model` and `default_subagent_reasoning_effort` apply when they
  are set. If they are not set, the child uses the parent's **current** model and effort, not the
  config default model.

## wait_agent

- `timeout_ms`: default 30,000; minimum 10,000 (Codex raises a lower value to 10,000); maximum
  3,600,000 (one hour).
- Config keys in source: `[features.multi_agent_v2] min_wait_timeout_ms`,
  `default_wait_timeout_ms`, `max_wait_timeout_ms`. Not tested in a real run
  ([open verification items](open-verification-items.md), item 9).
- A wait returns early when any message comes to the hub.
- Cost (observed in local logs): the wait itself costs no tokens. Each return costs one full model
  request, about 62K to 80K input tokens, most of them cached. Many short waits cost more than a
  small number of long waits.

## The 60-second base rule

- The Codex base instructions tell the model not to block for more than 60 seconds, and not to
  leave the user without an update for more than 60 seconds. The multi-agent text tells the model
  to "prefer longer waits (minutes)". These two rules conflict, and a hub can obey the base rule
  and wait only 60 seconds at a time.
- `AGENTS.md` and the task prompt come below the base instructions. Whether a sentence there
  overrides the 60-second rule is not verified (open item 9).
- Stronger controls: set the `min_wait_timeout_ms` floor in config, or pass
  `-c developer_instructions=...` (children get it too). `model_instructions_file` replaces the
  full base prompt; OpenAI strongly discourages that.

## exec_command polling

These rules apply to any Codex session, hub or child, that runs a long command.

- `yield_time_ms` is limited to 250–30,000 ms. A command that is still running returns a
  `session_id` and no `exit_code`.
- Poll with `write_stdin {session_id, chars: "", yield_time_ms: 300000}` until `exit_code`
  appears. An empty poll can wait up to `background_terminal_max_timeout` (default 300,000 ms).
- Each poll returns only the new output. Codex cuts output at `max_output_tokens` (default
  10,000) and at a 1 MiB buffer. Write long output to a file, then read the file.

## Lessons from one hub run (observed 2026-10-22)

- A hub used `fork_turns: "all"` and 60-second waits. It sent a status message to a child that
  was working, and the child stopped early.
- A child read only the output of one 30-second yield and did not poll. It never saw its test
  result.
- Recommendations (inference, from these two failures): give each role child `fork_turns: "none"`
  and a complete task message; wait in long intervals; do not send a message to a working child
  unless the task needs it; poll every long command until `exit_code` appears.

## Tested run: custom-role model and followup_task (2026-10-24)

**Observed locally** (I ran it), codex-cli 0.160.0. Command, with no project config:

```
codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --enable multi_agent \
  -c 'agents.memtest.description="..."' \
  -c 'agents.memtest.config_file="<abs path>/memtest.toml"' \
  --skip-git-repo-check -s workspace-write "<prompt>" < /dev/null
```

`memtest.toml` held `model = "gpt-5.6-luna"` and `model_reasoning_effort = "low"`.

- The subagents ran on gpt-5.6-luna, low effort (their `turn_context` shows it). So a custom role
  defined with `-c agents.<name>.config_file=...` sets a subagent model and effort from the command
  line.
- The main thread called `spawn_agent({task_name, agent_type: "memtest", fork_turns: "none",
  message})`. `fork_turns: "none"` gave each child a new, empty context.
- It then called `followup_task({target: "/root/<task_name>", message})` to continue the same
  child after it finished. 3 of 3 children recalled their first brief.
- Local feature flags showed `multi_agent` stable true and `multi_agent_v2` stable false. Path
  addressing (`/root/...`) and `followup_task` still worked.
- Each child has its own rollout file in `~/.codex/sessions/YYYY/MM/DD/`. Both turns of a child
  are in that one file (`task_started` and `task_complete` events). The main thread used about
  19K tokens; the run took about 1 minute.
- This run did not test the wait settings (open item 9).

A child can also send to a sibling with `send_message` and the path `/root/<task_name>` (tested
2026-10-24): [Codex multi-agent coordination](codex-multi-agent-coordination.md).

To read the hub's and children's records after a run, or to ask a past child a question, see
[Codex session logs and resume](codex-session-logs-and-resume.md).

Sources: https://github.com/openai/codex/tree/rust-v0.160.0 (the source files named above) ;
https://learn.chatgpt.com/docs/agent-configuration/subagents ; local rollout logs under
`~/.codex/sessions/` (2026-10-22 and 2026-10-24).
