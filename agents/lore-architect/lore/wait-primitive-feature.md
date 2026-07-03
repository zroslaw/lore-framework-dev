# Wait Primitive (`lr-wait`) — v18 Feature

The **on-demand wait/sleep/event primitive** for lore agents, shipped in v18. It lets a running agent *pause and resume* — on a timer, or on an external event that carries text (instructions or data). Aimed at background (`claude -p`) or occasionally-watched sessions.

It is the **inbound** counterpart to the outbound signal hooks (`Stop` / `Notification`, see `autonomous-agents-substrate.md` § Signal layer): those notify the *user* that the agent stopped; `lr-wait` lets an *external actor* wake the agent back up. This makes it the **first concrete inbound-signal step** of the autonomous-agents direction — see `autonomous-agents-vision.md`, `autonomous-agents-substrate.md`.

## Shape

- **`scripts/wait-server.py`** — pure-stdlib Python MCP **stdio** server (hand-rolled JSON-RPC 2.0; no `mcp` pip package). Two tools:
  - `wait_for_event(name?, mode="one"|"all", timeout_seconds=0, inbox?)` — blocks until a matching event file lands in the inbox, then returns its raw text. `name` = event type = filename prefix (matched as `"<name>."`, so `deploy` ≠ `deployment`). `mode`: `one` = oldest single event / `all` = drain all present. `timeout_seconds`: `0` = block indefinitely, `>0` = bounded (returns status `timeout`). Consumed files move to `processed/`.
  - `sleep(seconds)` — plain timer.
- **`scripts/lr-emit`** (bash) — the "wake it" side. Atomically (mktemp dotfile + `mv`) drops an event file into the inbox: `echo "..." | lr-emit --name deploy`. Anything that can write a file — cron, CI, a webhook, a human — can wake the agent.
- **`.mcp.json`** at the plugin root registers the server; Claude Code auto-launches it (see `plugin-mcp-server-convention.md`). **`skills/wait/SKILL.md` → `docs/wait.md`** is the thin-pointer skill + contract.
- **Inbox resolution:** explicit arg → `$LR_WAIT_INBOX` → cwd `./.lr-wait/inbox`.

## Key design decisions

- **MCP server, not a blocking Bash command.** A local stdio MCP tool call can block ~28h (`MCP_TOOL_TIMEOUT` default when unset); a command run via the agent's Bash tool is capped at the Bash-tool timeout (~10 min). MCP gives the clean, long block — *the* reason this is a server, not a script the agent runs directly.
- **Explicit tool, not a Stop hook.** On-demand — the agent waits only when instructed. A Stop hook fires on *every* stop and would need a marker-gate to distinguish "wait now" from "just stopped"; rejected as implicit and fragile.
- **File-inbox transport.** Events are files; content is plain text by default (JSON optional). Durable: an event emitted before *or* after the wait begins is not lost — the server scans the inbox before blocking. Decouples emitter from waiter (no sockets, ports, or long-lived daemon).

## Robustness (hardened after 3-lens review; all tested)

- `lr-emit` guards missing option values (a missing value was an infinite-loop hang — the review's MUST-FIX, empirically reproduced) and uses `mktemp` for unique filenames.
- `consume` is **claim-first**: atomic `os.rename` into `processed/` *then* read — no double-delivery when two sessions share one inbox.
- A mid-wait stray id-bearing request returns `-32603 busy` (never silently dropped → no host hang); cancellation + stdin-EOF handled.
- Event content capped ~1 MB (truncation flag); NaN / negative timeouts sanitized.

## Verification

- **Live headless:** a `claude -p` run held a foreground `wait_for_event` open through the wait and resumed with the event content — the agent even acted on an instruction embedded in the event. This confirmed the one open assumption from the plan (that a foreground MCP call blocks cleanly under `-p`).
- **Tests:** stdlib `unittest` in the dev repo (`lore-framework-dev/tests/test_wait.py` — see `plugin-vs-agent-repo-separation.md` § Dev-Only Artifacts), 23 tests (unit + integration), all green.

## Status

Built + reviewed + tested; shipped as **v18** but **not yet committed/pushed** (user holding the framework ship). Versioning classification + backfill in `versioning-release-types.md` (v18 entry: release-notes-only, cache-affecting). Conventions it established live in `plugin-mcp-server-convention.md`.

## See Also

- `plugin-mcp-server-convention.md` — the MCP-server-registration + `python3`-runtime conventions this feature established.
- `autonomous-agents-substrate.md`, `autonomous-agents-vision.md` — the autonomous direction this is the first inbound-signal step of.
- `versioning-release-types.md` — v18 classification (release-notes-only, cache-affecting: yes).
- `plugin-vs-agent-repo-separation.md` — where the tests live (dev repo, not plugin).
- `parallel-reviewer-fanout-pattern.md` — the 3-lens review that hardened this feature (validated the pattern for feature code, not just doc releases).
