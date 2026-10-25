---
lore: 1
type: area
summary: "Claude Code subagents, tested 2026-10-24 and 2026-10-25: resume keeps context, cost, nesting, limits; children cover the name and Agent Teams switch, messaging and discovery, and keeping a subagent alive. Open for any subagent question."
parent: lore/claude-apps-and-surfaces.md
---

# Claude Code subagents: tested behavior

Area for what Claude Code subagents do in practice. Short rules that hold in every case:

- The `name` parameter on `Agent` plus the Agent Teams flag decide the kind: flag on, a named
  agent is a teammate; flag off or unset (default), it is a plain subagent with a name.
- A named agent is reached by name; an unnamed one only by its agent ID.
- A subagent finds named agents through a roster in its context, not through `ListAgents`.

Children:

- [Named agents and the Agent Teams switch](claude-code-subagent-naming-and-teams-flag.md)
- [Messaging and discovery between agents](claude-code-subagent-messaging-and-discovery.md)
- [Keeping a subagent alive, and its tools](claude-code-subagent-liveness-and-tools.md)

**Tested** (I ran it on 2026-10-24 in Claude Code: Opus main session, Haiku subagents) unless a
line says **documented**. One test run per item; recheck after a Claude Code update.

## Resume with full context

- An unnamed `Agent` subagent can be resumed after it finishes (it is idle and not listed). `SendMessage` to its agent ID
  resumes it with its full history (3 of 3 resumes recalled a code word from the first brief).
- A rule in the first brief stays active after a resume until a later message cancels it
  explicitly (test: "do not repeat the code word").

## Cost and time (one data point)

- Base context of a Haiku subagent: about 37k tokens before any work (system prompt and tools,
  no Lore boot).
- Each resume added about 0.1k to 0.4k tokens.
- First start: 3 to 4 s. A resume: 19 to 29 s.

## Peer messages between subagents

Corrected 2026-10-25 (the first test sent only to guessed names and found no way to discover
siblings). Full results are in [messaging and discovery](claude-code-subagent-messaging-and-discovery.md).

- A subagent has `SendMessage` (deferred: load it with ToolSearch) but not `ListAgents`.
- A send to a name that does not exist fails: "No agent named 'Y' is reachable". Unnamed agents
  have no name, so only their agent ID works.
- A subagent does see a roster of `main` and the named agents at start, so it can find named
  siblings. A message arrives in an `agent-message from="<id>"` block; a finished receiver is
  resumed with it.
- **How to apply:** name the agents others must find, or put agent IDs in the brief.

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
