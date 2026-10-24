---
lore: 1
type: topic
summary: "Codex Desktop and CLI multi-agent boundaries (checked 2026-10-24): same-session messaging, direct sibling send_message by /root/<task_name> path, fixed app concurrency, and Agents API configuration."
parent: lore/openai-apps-and-surfaces.md
---

# Codex multi-agent coordination

Checked 2026-10-24. This topic separates documented API behavior from local observations. Recheck
the observations after a Codex update.

## One session tree

**Documented.** Multi-agent collaboration belongs to one agent session: the coordinator can create,
message, wait for, and interrupt its child agents. `max_concurrent_subagents` is configured when
an Agents API session is created. It is not a cross-session message bus.

Source: https://developers.openai.com/api/docs/guides/agents-api/multi-agent

**Observed locally.** In Codex Desktop, `collaboration.send_message` worked between child agents
of one chat. A separate Codex CLI session could not address those agents. To coordinate independent
Codex chats, use thread-level follow-up and status controls through a coordinator, or a shared
external system such as a task store or MCP service.

## Desktop versus API configuration

**Observed locally.** The Desktop chat did not expose a user setting to increase its active-child
limit; its harness allowed three active subagents. A user can ask the coordinator to use fewer,
but cannot raise that cap from the chat.

**Documented.** A custom Agents API session can set `max_concurrent_subagents` at creation. This
is the suitable path when an application needs a higher concurrent-worker limit.

## Hierarchy and scheduling

**Documented.** Child agents can create their own descendants. The active-subagent limit applies
to the entire tree, including children, grandchildren, and deeper descendants. The public
Responses API guide states no fixed tree-depth limit and does not specify a fairness or priority
policy for choosing among runnable agents.

Source: https://developers.openai.com/api/docs/guides/responses-multi-agent

**Observed locally.** A five-level Luna chain completed in Codex Desktop:
`luna_tree_scout` → `luna_tree_analyst` → `luna_tree_verifier` →
`luna_tree_executor` → `luna_tree_leaf`. A pending older worker initially consumed a shared slot
and blocked the final child. This confirms that the local active-child cap is tree-wide.

Operationally, use `spawn_agent` to create a child, `followup_task` to select and start or resume
one, `send_message` to queue information without starting a turn, `wait_agent` for a result, and
`interrupt_agent` to stop work. Treat ordering among more runnable agents than slots as
unspecified; the coordinator should choose the next worker explicitly with `followup_task`.

## Codex CLI test detail

**Observed locally, Codex CLI 0.160.0.** A persistent `codex exec` session created children that
sent and received direct greetings. The same test with `--ephemeral` failed during child creation
because the session store had no rollout. Do not use `--ephemeral` for a CLI multi-agent test.

## Sibling messages in Codex CLI (tested 2026-10-24)

**Observed locally, not documented.** codex-cli 0.160.0, main model gpt-5.6-terra (low effort),
`codex exec --enable multi_agent`. Verified in the child rollouts, not only in the main thread's
report.

- The main thread started two children with `spawn_agent` (`task_name: peer_a` and `peer_b`,
  `fork_turns: "none"`). Peer A called `send_message` with `target: "/root/peer_b"`. The tool
  result was empty (success). The main thread did not relay the message.
- Peer B received it as a response item `agent_message` with author `/root/peer_a`, recipient
  `/root/peer_b`, and the text header "Message Type: MESSAGE".
- The address is the task path `/root/<task_name>`. The child knew the path because its brief
  named it. No evidence shows that a child can list its siblings (not tested). So the parent must
  put each peer path in the brief.
- Cross-product comparison (for answers only; claude-expert and cursor-expert own those facts):
  Claude Code subagents can also message a sibling, but only with an agent ID that the main
  session gives; Cursor CLI has no peer tool.
- How to tell a peer message from a new task in a rollout:
  [Codex session logs and resume](codex-session-logs-and-resume.md), "Agent messages".

