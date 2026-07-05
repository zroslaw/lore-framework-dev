# Cursor Port Validation Report

Date: 2026-07-05

## Scope

Validated the separate local build:

- framework source: `/Users/yaroslav/Documents/git-repos/lore-framework-cursor`
- harness source: `/Users/yaroslav/Documents/git-repos/lore-framework-dev/tests/lifecycle/`
- engine: local `cursor-agent 2026.07.01-41b2de7`
- model used for all harness runs: `composer-2.5-fast`

## Implemented framework diff

Compared to canonical `lore-framework/`, the Cursor build changes only:

- `docs/agent-boot.md`
- `docs/attach.md`
- `docs/init.md`
- `docs/resolve-conflicts.md`
- `docs/engines/cursor.md` (new)

No skill files, migrations, DF files, or MCP files were changed in this build.

## Implemented harness diff

In `lore-framework-dev/`:

- `tests/lifecycle/harness.py`
  - added `cursor` engine driver via `cursor-agent -p`
  - made engine-binary detection engine-aware
  - added `memory_file_name()` helper for engine-specific `init` assertions
- `tests/lifecycle/test_repo_workspace.py`
  - made `test_18_init` assert the engine-selected memory file rather than hardcoding `CLAUDE.md`

## Verified Cursor facts

- `cursor-agent --plugin-dir <path>` works for local framework loading.
- slash-style invocation works (`/lr:boot lore-architect`).
- `${CLAUDE_PLUGIN_ROOT}` is empty on this engine path.
- `ps -o args= -p $PPID` is permitted and exposes the parent `cursor-agent` command line.
- the framework can now select an explicit `cursor` engine profile instead of silently defaulting to `claude`.

## Cursor profile shape

The implemented Cursor profile is intentionally conservative:

- `framework-root`: self-location only
- `invocation-syntax`: slash commands work; direct doc reads remain acceptable mid-task
- `memory-file`: `AGENTS.md`
- `runtime-bounding`: no Claude-style Bash timeout assumed
- `subagent-spawn`: **serial host-side override**, not claimed parallel fan-out

This was enough to validate the full currently-implemented Tier-1 lifecycle catalog on the real engine.

## Test results

Full suite command:

```sh
LR_LIFECYCLE=1 \
LR_ENGINE=cursor \
LR_TEST_MODEL=composer-2.5-fast \
LR_FRAMEWORK_DIR=/Users/yaroslav/Documents/git-repos/lore-framework-cursor \
python3 -m unittest discover \
  -s /Users/yaroslav/Documents/git-repos/lore-framework-dev/tests/lifecycle \
  -p 'test_*.py' -v
```

Result:

- **19 tests run**
- **19 passed**
- total wall time: **810.803s**

Scenario groups covered:

- boot (`test_boot.py`) — 6/6
- recall (`test_recall.py`) — 1/1
- consult / attach (`test_consult_attach.py`) — 2/2
- reflect / merge / summarize / finalize (`test_finalize.py`) — 4/4
- repo / workspace (`test_repo_workspace.py`) — 6/6

## Observed issue and fix during validation

One test initially failed:

- `test_18_init` expected `CLAUDE.md`

That was a **test bug**, not a framework bug. Cursor correctly writes `AGENTS.md` per the engine profile. The fix was to make the lifecycle test use an engine-aware memory-file assertion.

## Current open items

These were intentionally not part of this local Cursor build:

- landing the changes into canonical `lore-framework/`
- release notes / `VERSION` bump / manifest bump
- `lr-wait` / `.mcp.json` Cursor work
- DF / AIQA / migration-surface Cursor work
- proving a true Cursor-native subagent mechanism and replacing the serial host-side override

## Landing readiness

This build is suitable as a near-landing artifact:

- small, explicit framework diff
- explicit engine profile instead of accidental Claude fallback
- full implemented lifecycle catalog green on real local Cursor
- harness support included for future regression runs

Recommended landing order:

1. copy the five framework doc changes from `lore-framework-cursor/` into canonical `lore-framework/`
2. carry the two harness changes in `lore-framework-dev/`
3. add release notes for the Cursor engine profile
4. rerun the Cursor suite against canonical after landing
