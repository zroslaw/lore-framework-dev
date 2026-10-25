---
lore: 1
type: topic
summary: "Tested 2026-10-25: who can message whom among main, named, unnamed subagents and teammates; the sibling roster instead of ListAgents. Open before designing agents that talk to each other."
parent: lore/claude-code-subagents-tested.md
---

# Messaging and discovery between agents

One run per cell, Haiku agents. Roster text is documented at
https://code.claude.com/docs/en/sub-agents.

**Addresses.** A named agent is reached by name, an unnamed one only by its agent ID. A made-up
label such as "unnamed-1" is not a name: the send fails with `No agent named 'X' is reachable`.
`to: "main"` reaches the main conversation from a subagent. From a teammate, `main` means itself
and fails (the lead is `team-lead`; not tested).

**Teams off (all plain subagents):** every pair worked: named to named by name, named to unnamed
by ID, unnamed to named by name, unnamed to unnamed by ID, and all to `main`. Idle receivers are
resumed ("Resuming agent X"); busy ones queue the message for their next tool round. A receiver
may skip an ack that the sender asked for if its own brief says otherwise: a missing ack is not a
failed delivery.

**Teams on (named agents are teammates; see [the switch](claude-code-subagent-naming-and-teams-flag.md)):**
teammate to teammate by name works and wakes the receiver. Unnamed to teammate by name works.
Teammate to unnamed subagent by ID **fails**: "could not be resumed: No transcript found for
agent ID" (inference: teammates are separate sessions and look in the wrong transcript scope; the
docs are silent). A stopped teammate is not reachable by name. One named `general-purpose`
teammate had no `SendMessage` at all (cause unknown; the docs say `SendMessage` is added to
in-process teammates).

**Discovery.** No plain subagent has `ListAgents`; a teammate has it, and it lists teammates and
peer sessions but never unnamed subagents. Instead a subagent that has `SendMessage` gets a sibling
roster in its context at start: `Other agents active in this session, addressable via
SendMessage({to: name, message}): main, alpha, beta, ...`. It lists `main` and **named** agents
only, never unnamed ones, and is a snapshot from start (documented; whether a resume refreshes it
is untested). Unnamed peers become known only through the `from=` address of a message they send.

**How to apply:** to make agents talk, name the ones others must find, or put agent IDs in the
brief. Name the receiver before spawning the sender so the roster has it.
