# Cursor Agent CLI — Probe Findings (first probe, later superseded)

First hands-on probe of `cursor-agent` (2026.07.01) as a port target, ahead of the parked
`workdir/draft-port-cursor.md`.

## Findings

- **`--plugin-dir <path>` exists and mirrors Claude Code's own flag** — same name, same
  per-invocation local-directory semantics. Of the two port targets, this makes cursor the
  lower-friction one for the lifecycle harness driver: no persistent install/registration step
  like codex needs (see `codex-cli-plugin-loading-findings.md`).
- Also relevant for headless driving: `--print`/`-p`, `--output-format json`, `--force`/`--yolo`
  (skip confirmation), `--trust` (trust workspace non-interactively), `--workspace <path>`.
- Login/account status confirmed healthy (`cursor-agent status` → logged in as
  zroslaw@gmail.com), and `--list-models` works.

## Blocked on quota, not tooling

A live smoke-test call (`cursor-agent -p "..." --output-format json --force --trust`) failed
immediately with `ActionRequiredError: You've hit your usage limit` — an account-level Cursor
Pro/Agent usage cap, not a harness or CLI-integration bug. Login and model listing both work
fine, isolating the failure to quota, not tooling.

## Status at the time

Cursor driver work is parked until the usage limit resets or the account is upgraded. No cursor
scenario has been run yet — codex got the first real empirical pass this session instead,
specifically because it was unblocked (see `codex-cli-plugin-loading-findings.md`).

Next step once unblocked: repeat the same smoke test pattern used for codex — a single
`test_boot.py`-equivalent happy-path run — before deciding whether to add a full `cursor` branch
to `run_engine()`.

## Later result (2026-07-05)

This blocked first probe is now **superseded** by a real successful validation run:

- local separate build `lore-framework-cursor/`
- explicit `docs/engines/cursor.md`
- full currently-implemented lifecycle catalog green on the real local engine (`19/19`)

See `cursor-port-validated-end-to-end.md` and `cursor-cli-and-harness-operational-notes.md`.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction this probe serves.
- `codex-cli-plugin-loading-findings.md` — the sibling probe, further along (first PASS obtained).
- `lifecycle-testing-harness.md` — where a `cursor` branch would land in `run_engine()` once
  unblocked.
- `cursor-port-validated-end-to-end.md` — the later successful local validation.
