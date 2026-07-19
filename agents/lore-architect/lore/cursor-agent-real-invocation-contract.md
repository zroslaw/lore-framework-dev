# Cursor `cursor-agent` real invocation contract (empirical + harness)

Documents the headless contract the Being Keeper's `cursor` engine kind implements. Primary
empirical basis: the lifecycle harness driver (`lore-framework-dev/tests/lifecycle/harness.py`)
and prior Cursor CLI probes (`cursor-agent-cli-probe-findings.md`, `cursor-cli-and-harness-
operational-notes.md`). A live JSON capture during this implementation was blocked because
`cursor-agent status` reported not logged in in the build environment — re-run
`tests/test_lrb_cursor_real_e2e.py` after `cursor-agent login` to confirm on a live account.

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

If `total_cost_usd` is absent, the Keeper may charge a configured flat `--session-cost-usd` per
finished session (optional at `engines add`; same safe-direction rule as codex).

## stderr

Route stderr to a sibling file, not merged into stdout — same rule as claude/codex. Gate success on
parsed JSON, not empty stderr.

## Keeper wiring

Landed in `scripts/lrb.py`: `ENGINE_KINDS` includes `cursor`; `spawn_session` cursor branch;
`_finish` cursor branch with reported-cost + flat fallback; `lrb engines add --plugin-dir`.

## See Also

- `engine-kinds-design-decision.md` — per-kind dispatch pattern
- `codex-exec-real-invocation-contract.md` — the cost-blind kind precedent
- `cursor-cli-and-harness-operational-notes.md` — harness driver notes
- `docs/beings.md` — user-facing reference
