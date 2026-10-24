---
lore: 1
type: topic
summary: "Codex Desktop and CLI multi-agent boundaries (checked 2026-10-24): same-session messaging, fixed app concurrency, and Agents API configuration."
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

## Codex CLI test detail

**Observed locally, Codex CLI 0.160.0.** A persistent `codex exec` session created children that
sent and received direct greetings. The same test with `--ephemeral` failed during child creation
because the session store had no rollout. Do not use `--ephemeral` for a CLI multi-agent test.

