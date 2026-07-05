# Cursor CLI and Harness Operational Notes

Operational notes from running the framework on real local Cursor and wiring it into the lifecycle
harness.

Verified Cursor CLI behavior:

- `cursor-agent --plugin-dir <path>` works for local framework loading
- slash invocation works (`/lr:boot lore-architect`)
- `${CLAUDE_PLUGIN_ROOT}` is empty on this engine path
- `ps -o args= -p $PPID` works and exposes the parent `cursor-agent` command line, which is a
  strong engine-detection signal for boot Step 0
- `cursor-agent status` and `cursor-agent --list-models` may fail inside the sandbox because of
  macOS keychain access; rerunning outside the sandbox fixes this

Harness driver notes:

- Cursor can be driven headlessly via `cursor-agent -p`
- use `--output-format json` and parse the top-level `result`, `duration_ms`, and `usage` object
- pass stdin from `/dev/null`; do not let the process inherit an open stdin
- `--force`, `--trust`, and `--workspace <path>` are enough for deterministic fixture runs
- the `init` scenario must assert the engine-selected memory file (`AGENTS.md` on Cursor), not
  hardcode `CLAUDE.md`

The lifecycle harness and the framework's finalize flow have different commit scopes:

- the harness code lives under `lore-framework-dev/tests/`
- finalize phase 4 commits only `agents/`

So a successful local Cursor harness run can be fully validated in one session while still needing
a **separate manual commit** for `tests/` changes afterwards. Do not mistake that commit-scope gap
for a framework failure.

Recommendation: treat Cursor as a first-class harness engine now. The blocking state in
`cursor-agent-cli-probe-findings.md` is superseded by real successful runs; future regressions
should be caught by the harness, not rediscovered through manual smoke tests.
