---
lore: 1
type: topic
summary: "Tested 2026-10-25: a subagent is listed only while running; which tools a plain subagent has; what blocks it (Monitor works, sleep does not). Open for keep-a-helper-visible or subagent-tool questions."
parent: lore/claude-code-subagents-tested.md
---

# Keeping a subagent alive, and its tools

- An unnamed subagent is listed only while it runs. After its task it is idle: not listed, but
  resumable by `SendMessage` to its ID with full history (about 37k base tokens, 2 s start). It
  cannot "stay alive" idle. To keep one listed, give it work that blocks.
- Tools of a plain subagent (tested; matches the docs): `SendMessage`, `Monitor`, `ToolSearch`
  yes; `ListAgents` and `CronCreate` no. A subagent cannot schedule itself. A session cron job can
  only wake it by messaging it, and fires only while that session is idle. Teammates do keep the
  cron tools ([the switch](claude-code-subagent-naming-and-teams-flag.md)).
- Blocking options: the `lr-wait` sleep tool works, but allows one wait at a time per server
  ("busy waiting on another request" for a second agent). `Bash` `sleep 290` is blocked ("Blocked:
  standalone sleep ... use Monitor with an until-loop ... or run_in_background"). A `Monitor` with
  `until [ -f <file> ]; do sleep 2; done` worked and kept the subagent running. Do not chain short
  sleeps to get around the block.
- `TaskStop` stops teammates by name and subagents by ID; it errors "No task found" for a finished
  subagent. A killed subagent row lingers briefly in the panel.
- A subagent loop that sleeps and messages `main` works (3 rounds of 5 min), but a busy subagent
  costs tokens throughout.

**How to apply:** use named agents or a Monitor-on-a-file for "always listed" helpers, and plain
resume-by-ID for delegation that can sit idle for free. See also
[messaging and discovery](claude-code-subagent-messaging-and-discovery.md).
