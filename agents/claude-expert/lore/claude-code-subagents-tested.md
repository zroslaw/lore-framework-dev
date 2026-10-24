---
lore: 1
type: topic
summary: "Claude Code subagents, tested 2026-10-24: resume with SendMessage keeps full context, base cost and time per subagent, peer messages need an agent ID, nesting stops at level 3; plus the documented concurrency and depth limits."
parent: lore/claude-apps-and-surfaces.md
---

# Claude Code subagents: tested behavior

**Tested** (I ran it on 2026-10-24 in Claude Code: Opus main session, Haiku subagents) unless a
line says **documented**. One test run per item; recheck after a Claude Code update.

## Resume with full context

- An unnamed `Agent` subagent stays available after it finishes. `SendMessage` to its agent ID
  resumes it with its full history (3 of 3 resumes recalled a code word from the first brief).
- A rule in the first brief stays active after a resume until a later message cancels it
  explicitly (test: "do not repeat the code word").

## Cost and time (one data point)

- Base context of a Haiku subagent: about 37k tokens before any work (system prompt and tools,
  no Lore boot).
- Each resume added about 0.1k to 0.4k tokens.
- First start: 3 to 4 s. A resume: 19 to 29 s.

## Peer messages between subagents

- A subagent has `SendMessage` (deferred: load it with ToolSearch) but not `ListAgents`. Thus it
  cannot find its siblings.
- A send to a guessed name fails: "No agent named 'Y' is reachable".
- With the agent ID of a sibling, the send succeeds ("queued for delivery … at its next tool
  round"). A finished receiver is resumed with the message. The message arrives in an
  `agent-message from="<id>"` block.
- **How to apply:** to let subagents talk to each other, give each one the agent IDs of its peers
  in its brief.

## Nesting

- Levels 1 and 2 have the `Agent` tool. Level 3 has no `Agent` tool, not even as a deferred tool.
  There is no error; the tool is not there.
- This agrees with the documented default depth of 3 layers (below).

## Documented limits

**Documented**, https://code.claude.com/docs/en/sub-agents, checked 2026-10-24:

- 20 running subagents per session by default. The next spawn fails with
  `Concurrent subagent limit reached`, and the error tells Claude not to retry. Change the limit
  with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`. Ultracode does not enforce it. Needs v2.1.217 or
  later.
- No limit on the total number of subagents spawned in one session.
- Depth: up to three layers below the main conversation. Change it with
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; the value 1 turns nesting off.

See also: [subagent monitoring](subagent-monitoring-and-correlation.md) for how the Agent SDK and
Managed Agents expose subagents.
