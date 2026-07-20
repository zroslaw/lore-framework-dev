# Cursor `cursor-agent` real invocation contract (empirical + harness)

Documents the headless contract the Being Keeper's `cursor` engine kind implements. Primary
empirical basis: the lifecycle harness driver (`lore-framework-dev/tests/lifecycle/harness.py`),
the A3 Keeper lifecycle scenario (2026-07-20, live `cursor-agent`), and prior Cursor CLI probes
(`cursor-agent-cli-probe-findings.md`, `cursor-cli-and-harness-operational-notes.md`).
`tests/test_lrb_cursor_real_e2e.py` still requires `cursor-agent login` to run.

## Invocation argv

```bash
cursor-agent -p PROMPT \
  --plugin-dir /path/to/lore-framework \
  --model MODEL \
  --output-format json \
  --trust \
  --workspace WORKSPACE \
  # permission_mode full adds:
  --force --sandbox disabled
```

- **`--plugin-dir`** is mandatory for Lore beings — skills load from the framework checkout; stored
  per engine in Keeper `config.json` as `plugin_dir` (validated: directory contains `VERSION`).
- **`--workspace`** matches the Keeper workspace root (also `cwd` for the subprocess).
- **`stdin`** must be `/dev/null` (harness and Keeper both set this).
- **`default` permission** — `--trust` only; headless Bash/Write may still be denied (same gap as
  other engines; see `docs/beings.md` § outbox).
- **`full` permission** — adds `--force --sandbox disabled` (matches lifecycle harness).

## Result JSON (claude-shaped)

With `--output-format json`, stdout is a **single JSON object** (same parser as claude-kind in
`scripts/lrb.py` `_parse_result_json`). Fields the Keeper uses:

| Field | Use |
|---|---|
| `result` | Session output text |
| `total_cost_usd` | Charged against `daily-usd` when present |
| `is_error` | `error` vs `ok` outcome |
| `usage` | Recorded in ledger when present |

**`total_cost_usd` is empirically absent, not just "may be absent" (2026-07-20).** The real A3
capture (`cursor-agent` 2026.07.16, model `composer-2.5`, `--output-format json`) had **no
`total_cost_usd` field at all** — only a `usage` object with token counts. This contradicts the
original Lore Beings build note (`draft-lore-beings.md` §16: "cursor: … real cost charged");
whether cursor's contract changed or that check never actually exercised the field is unconfirmed.
Consequence per `_finish`'s cursor branch: with `total_cost_usd` absent **and** no
`session_cost_usd` flat fallback configured, cost is silently charged as `$0.00` forever and the
`daily-usd` spawn gate never trips — the exact cost-blind failure the `codex` kind's mandatory
`--session-cost-usd` guards against. So the flat fallback is **load-bearing, not optional**, for
any real cursor being today. `cmd_engines_add` currently treats `--session-cost-usd` as **mandatory
for codex but optional for cursor** — an asymmetry that no longer matches what real cursor-agent
reports. Backlog: either make it mandatory for cursor too, or re-verify across more cursor models
that `total_cost_usd` is genuinely gone before hardening (see `framework-improvements-backlog.md`
§ Autonomous Agents / Lore Beings). The A3 test config adds `session_cost_usd` to exercise the
fallback — which is what any real deployment must do anyway.

## stderr

Route stderr to a sibling file, not merged into stdout — same rule as claude/codex. Gate success on
parsed JSON, not empty stderr.

## Keeper wiring

Landed in `scripts/lrb.py`: `ENGINE_KINDS` includes `cursor`; `spawn_session` cursor branch;
`_finish` cursor branch with reported-cost + flat fallback; `lrb engines add --plugin-dir`.

**Pre-ship checklist:** run `python3 tests/test_lrb_cursor_real_e2e.py` on a machine where
`cursor-agent status` shows logged in; capture a real stdout JSON sample and confirm
`total_cost_usd` presence/absence before claiming empirical verification complete.

## Backend reliability — transient flakiness observed 2026-07-20

Getting the A3 scenario green took 4 attempts for 1 clean pass, with 3 distinct **real backend**
failures — not Keeper or test bugs. Twice `cursor-agent`'s own stderr reported `"Connection lost,
reconnecting to https://agentn.global.api5.cursor.sh (attempt 1)..."` and hung to the Keeper's
timeout kill; once it exited with zero stdout (`"crashed"` outcome). Ruled out local causes:
`cursor-agent` was already latest (`2026.07.16-899851b`), no retry/timeout/reconnect flags exist in
`--help` to misconfigure, and `claude`/`codex` real calls ran fine concurrently on the same
machine/network. Best read: genuine transient instability on Cursor's own backend relay that day.

Operational takeaways: (a) before treating a future A3 failure as a new regression, check it against
this known flakiness first; (b) a `timeout`/`crashed` ledger entry is exactly the right signal for
the Keeper to record for real, so any retry belongs at the **test-harness** layer, not in `lrb.py`
— proposed but not yet actioned: a capped 1-retry for connection-loss/crash-shaped outcomes in
cursor-facing real-engine scenarios, with a visible notice when it fires so an emerging regression
isn't silently masked (backlog).

## See Also

- `engine-kinds-design-decision.md` — per-kind dispatch pattern
- `codex-exec-real-invocation-contract.md` — the cost-blind kind precedent
- `cursor-cli-and-harness-operational-notes.md` — harness driver notes
- `docs/beings.md` — user-facing reference
