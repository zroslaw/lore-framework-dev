---
lore: 1
type: topic
summary: "Tested 2026-10-25 (Claude Code 2.1.309): the Agent tool's name parameter plus the Agent Teams flag decide if a named agent is a teammate or a plain subagent; how to tell them apart. Open for does-naming-create-a-team questions."
parent: lore/claude-code-subagents-tested.md
---

# Named agents and the Agent Teams switch

Named and unnamed subagents use the same `Agent` tool call. The `name` parameter is the switch,
and the experimental Agent Teams flag decides what it does. **Documented** 2026-10-25
(https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/agent-teams) and
**tested** in Claude Code 2.1.309.

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (in the `env` block of settings.json or the shell): an
  `Agent` call with a `name` launches a **teammate**. This holds in interactive sessions, unless
  the call is a fork or passes `isolation`. In non-interactive `-p` and Agent SDK sessions a named
  subagent stays plain. Claude may name subagents on its own, so teams can form unasked.
- Flag `0` or unset (off is the default): the same call launches a plain subagent. The name only
  becomes a `SendMessage` address. The setting is reread at each spawn, with no restart (tested).
- Signs of a teammate (tested): the spawn result is `name@session-<id>` and says the agent "will
  receive instructions via mailbox"; `ListAgents` shows it under Teammates; it reports with an
  idle notification (`teammate-message`). A plain subagent spawns as "Async agent launched" with a
  plain ID and reports with a completion notification.
- The `team_name` parameter is deprecated and ignored; a session has one implicit team.
- Teammates also keep the task tools and the cron tools (`CronCreate`). A teammate row hides 30 s
  after the whole panel goes idle, but the teammate stays addressable. A finished plain subagent
  row is removed at once.

**How to apply:** to get subagents without team side effects, set the flag to `0`; naming still
works for `SendMessage`. Does naming create a team? Only while the flag is on. The agent type
(for example `general-purpose`) does not matter; the name decides.

Related: [messaging and discovery](claude-code-subagent-messaging-and-discovery.md) (the two kinds
differ in who can message whom).
