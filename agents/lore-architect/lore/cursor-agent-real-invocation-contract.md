# Cursor `cursor-agent` real invocation contract (empirical + harness)

Documents the headless contract the Being Keeper's `cursor` engine kind implements. Primary
empirical basis: the lifecycle harness driver (`lore-framework-dev/tests/lifecycle/harness.py`),
the A3 Lore Beings lifecycle scenario (`tests/lifecycle_beings/test_lrb_lifecycle.py`,
2026-07-20, live `cursor-agent`), and prior Cursor CLI probes
(`cursor-agent-cli-probe-findings.md`, `cursor-cli-and-harness-operational-notes.md`). The earlier
standalone `tests/test_lrb_cursor_real_e2e.py` script (superseded by A3, weaker teardown
guarantees) was deleted 2026-07-20 once A3 fully covered its ground.

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
`session_cost_usd` flat fallback configured, cost would silently charge as `$0.00` forever and the
`daily-usd` spawn gate never trip — the exact cost-blind failure the `codex` kind's mandatory
`--session-cost-usd` guards against. **Fixed 2026-07-20:** `cmd_engines_add` now requires
`--session-cost-usd` for `cursor` too, same as `codex` (see `docs/beings.md`, `test_lrb.py`
`TestCliSubprocess.test_engines_add_cursor_kind_requires_session_cost`) — the flat fallback is
load-bearing for any real cursor being, and is enforced at config time rather than left to the
operator to remember. The A3 test config sets `session_cost_usd` to exercise exactly that fallback
path.

## stderr

Route stderr to a sibling file, not merged into stdout — same rule as claude/codex. Gate success on
parsed JSON, not empty stderr.

## Sandboxed shell tool escapes process-group kill (2026-07-20)

Real `cursor-agent` tool-invoked shell commands run inside a freshly `setsid`'d session (observed
process tree: a `zsh -c` sandbox wrapper as session leader, then `sh -c`, then the actual command —
all in a NEW process group distinct from the direct `cursor-agent` child's). `_kill`'s original
`killpg(pgid-of-the-direct-child)` cannot reach that group at all — confirmed live via the B3
lifecycle scenario, which left a real orphaned process running on the test machine (had to be
manually SIGKILLed) before the fix. Fixed same day: `_kill` now also walks the full ppid-descendant
tree (`_descendant_pids`) and signals every descendant directly — ppid links survive a `setsid`
even though pgid/session don't. Ordering matters: descendants must be enumerated BEFORE the parent
is signaled, or a fast-dying parent gets reaped and the OS reparents the survivor to PID 1,
overwriting the very ppid link the walk depends on. See `engine-kinds-design-decision.md`,
`lore-beings-mvp-takeover-review.md` § Fifth pass, and the general operational writeup in
`kill-tree-enumerate-before-signal-ordering.md` (the ordering rule for any future ancestry-based
kill-tree code) and `testing-simulate-process-escape-without-setsid-binary.md` (how the regression
test reproduces the setsid-escaped process tree on macOS without a real `cursor-agent` call). Adding
the `ps`-based descendant walk to `_kill`'s hot path also had a second-order effect — see
`hot-path-latency-can-expose-latent-test-timing-races.md`.

## Keeper wiring

Landed in `scripts/lrb.py`: `ENGINE_KINDS` includes `cursor`; `spawn_session` cursor branch;
`_finish` cursor branch with reported-cost + flat fallback; `lrb engines add --plugin-dir`;
`_kill`'s ppid-descendant-tree walk (`_descendant_pids`, 2026-07-20) closes the setsid-escape gap
above — engine-agnostic in the code, but empirically load-bearing for cursor specifically.

**Pre-ship checklist:** run `LR_LIFECYCLE_BEINGS=1 LR_ENGINE=cursor python3
tests/lifecycle_beings/test_lrb_lifecycle.py -v -k a3` on a machine where `cursor-agent status` shows
logged in; capture a real stdout JSON sample and confirm `total_cost_usd` presence/absence before
claiming empirical verification complete.

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
- `kill-tree-enumerate-before-signal-ordering.md` — the general enumerate-before-kill ordering rule this fix follows
- `testing-simulate-process-escape-without-setsid-binary.md` — the macOS-portable technique used to regression-test this without a real `cursor-agent` call
- `hot-path-latency-can-expose-latent-test-timing-races.md` — unrelated tests that broke when this fix's `ps` call slowed `_kill` down
- `docs/beings.md` — user-facing reference
