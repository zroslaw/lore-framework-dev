# Operational Discipline: Background Headless CLI Probes, Don't Hard-Kill Them

When manually smoke-testing a new headless engine CLI (codex, cursor-agent, or any future
engine) outside the lifecycle harness's own timeout handling, run it backgrounded
(`nohup ... < /dev/null > out.log 2>err.log & disown`) and poll for completion, rather than a
single foreground call bounded by a hard wall-clock timeout.

## Why

A foreground `codex exec` run was killed by a 5-minute timeout and produced zero bytes of
stdout — indistinguishable from a total hang. The reasonable next question was "if it's
completely broken, should we just kill it?" Backgrounding the identical command and polling
instead showed the process had been working correctly the whole time (reading skill docs,
resolving the agent, running auto-pull) — it just hadn't flushed its JSONL stdout to the
redirected file before the SIGTERM landed. The hard kill destroyed the evidence needed to tell
"stuck" from "slow."

## How to apply

For any one-off manual probe of a long-running headless agent CLI, prefer `run_in_background`
(or `nohup ... & disown` + a poll loop) over a foreground call with an aggressive timeout.
Reserve hard foreground timeouts for calls already known to be fast. This is a general
debugging-discipline lesson, not specific to codex — it applies equally to cursor-agent and any
future engine driver work (see `codex-cli-plugin-loading-findings.md`,
`cursor-agent-cli-probe-findings.md`).

## See Also

- `lifecycle-testing-harness.md` — the harness these manual probes feed into.
- `multi-engine-portability-direction.md` — the direction these probes serve.
- `portable-shell-in-framework-docs.md` — sibling shell-portability discipline (different
  concern: GNU vs BSD binaries, not backgrounding).
