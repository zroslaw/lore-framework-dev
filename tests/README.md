# lore-framework tests

Tests for the `lore-framework` plugin. They live here in the **dev repo**, not in the plugin repo,
which stays slim for marketplace distribution (see `lore-framework/docs/conventions.md` §
Dev-Only Artifacts and the `plugin-vs-agent-repo-separation` lore principle).

## Running

Stdlib only — no pytest, no install.

```bash
python3 tests/test_wait.py -v
# or
python3 -m unittest discover -s tests -v
```

## Locating the plugin

Tests find the plugin under test via `$LR_FRAMEWORK_DIR`, defaulting to the sibling
`../lore-framework`. Override if your layout differs:

```bash
LR_FRAMEWORK_DIR=/path/to/lore-framework python3 tests/test_wait.py -v
```

## Suites

- **`test_wait.py`**
  - `TestUnit` — pure helpers of `scripts/wait-server.py`: inbox resolution, match ordering by
    arrival time, the by-name prefix boundary (`deploy` ≠ `deployment`), `consume`→`processed/`,
    mode selection, and timeout/sleep timing. Loads the hyphenated server file via `importlib`.
  - `TestIntegration` — a live `wait-server.py` subprocess driven over real JSON-RPC stdio, plus the
    real `scripts/lr-emit`: handshake, `tools/list`, `sleep`, timeout, `one`/`all`, by-name,
    blocking-wake, and EOF shutdown.

## Lifecycle scenario tests (Layer 3)

`lifecycle/` holds end-to-end scenario tests: a throwaway fixture workspace (agent repo +
local bare `origin`, zero network) is built per test, a real engine runs a lifecycle prompt
headless in it, and a script asserts on the resulting files and git state. Design and full
scenario catalog: lore-architect `workdir/draft-testing-pipeline.md`.

**They call a real engine and cost API money**, so they are gated — skipped unless
`LR_LIFECYCLE=1`:

```bash
LR_LIFECYCLE=1 python3 tests/lifecycle/test_boot.py -v          # all boot scenarios
LR_LIFECYCLE=1 python3 tests/lifecycle/test_boot.py -v -k 01    # one scenario
```

Env knobs: `LR_ENGINE` (default `claude`; the only driver so far), `LR_TEST_MODEL`
(default `sonnet`), `LR_RUN_TIMEOUT` (seconds, default 420), `LR_FRAMEWORK_DIR` (as above).
In CI, provide engine auth (e.g. `ANTHROPIC_API_KEY`) and set `LR_LIFECYCLE=1`; run
nightly/on-demand, not per-commit.

Scenario catalog status (numbering per the draft):

| # | Scenario | Status |
|---|---|---|
| 1 | Boot happy path | ✅ `lifecycle/test_boot.py` |
| 2 | Boot pulls fresh commits | ✅ `lifecycle/test_boot.py` |
| 3 | Boot degraded (remote unreachable) | ✅ `lifecycle/test_boot.py` |
| 4 | Boot unknown agent | ✅ `lifecycle/test_boot.py` |
| 5 | Boot version mismatch (release-notes-only) | ✅ `lifecycle/test_boot.py` |
| 6 | Upgrade gate on dirty tree | ✅ `lifecycle/test_boot.py` |
| 7 | Recall with hint | ✅ `lifecycle/test_recall.py` |
| 8 | Consult another agent | ✅ `lifecycle/test_consult_attach.py` |
| 9 | Attach a guest | ✅ `lifecycle/test_consult_attach.py` |
| 10 | Reflect | ✅ `lifecycle/test_finalize.py` |
| 11 | Merge | ✅ `lifecycle/test_finalize.py` |
| 12 | Summarize | ✅ `lifecycle/test_finalize.py` |
| 13 | Finalize end-to-end | ✅ `lifecycle/test_finalize.py` |
| 14 | Concurrent finalize collision | deferred — needs two-clone push-race scripting |
| 15 | Finalize with guest attached | deferred — needs cross-repo guest fixture |
| 16 | create-repo | ✅ `lifecycle/test_repo_workspace.py` |
| 17 | create-agent | ✅ `lifecycle/test_repo_workspace.py` |
| 18 | init | ✅ `lifecycle/test_repo_workspace.py` |
| 19 | workspace-sync | ✅ `lifecycle/test_repo_workspace.py` |
| 20 | check | ✅ `lifecycle/test_repo_workspace.py` |
| 21 | update --dry-run | ✅ `lifecycle/test_repo_workspace.py` |
| Tier 2 | wait/emit | covered by `test_wait.py` (protocol-level, not a lifecycle scenario) |
| Tier 2 | spawn-teammate | deferred — not headless-scriptable (multi-pane UI) |
| Tier 2 | df-repo-init, df-ula-file | deferred — BETA, out of scope for this pass |
