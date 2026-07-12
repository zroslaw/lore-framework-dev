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

Env knobs: `LR_ENGINE` (default `claude`; supported: `claude`, `codex`, `cursor`),
`LR_TEST_MODEL` (engine-specific default), `LR_RUN_TIMEOUT` (seconds, default 420),
`LR_FRAMEWORK_DIR` (as above). For debugging real-engine variance, set `LR_KEEP_FIXTURES=1`
to keep throwaway workspaces and `LR_DEBUG_DIR=/path/to/debug` to dump each run's final
message and stderr tail.
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
| 7 | Repo newer than framework (Codex refresh guidance) | ✅ `lifecycle/test_boot.py` |
| 8 | Recall with hint | ✅ `lifecycle/test_recall.py` |
| 9 | Consult another agent | ✅ `lifecycle/test_consult_attach.py` |
| 10 | Attach a guest | ✅ `lifecycle/test_consult_attach.py` |
| 11 | Reflect | ✅ `lifecycle/test_finalize.py` |
| 12 | Merge | ✅ `lifecycle/test_finalize.py` |
| 13 | Summarize | ✅ `lifecycle/test_finalize.py` |
| 14 | Finalize end-to-end | ✅ `lifecycle/test_finalize.py` |
| 15 | Concurrent finalize collision | deferred — needs two-clone push-race scripting |
| 16 | Finalize with guest attached | deferred — needs cross-repo guest fixture |
| 17 | create-repo | ✅ `lifecycle/test_repo_workspace.py` |
| 18 | create-agent | ✅ `lifecycle/test_repo_workspace.py` |
| 19 | workspace-init | ✅ `lifecycle/test_repo_workspace.py` |
| 20 | workspace-pull | ✅ `lifecycle/test_repo_workspace.py` |
| 21 | check | ✅ `lifecycle/test_repo_workspace.py` |
| 22 | update --dry-run | ✅ `lifecycle/test_repo_workspace.py` |
| 23 | register-agent | ✅ `lifecycle/test_repo_workspace.py` |
| 24 | register-repo | ✅ `lifecycle/test_repo_workspace.py` |
| 25 | unregister-agent | ✅ `lifecycle/test_repo_workspace.py` |
| 26 | unregister-repo | ✅ `lifecycle/test_repo_workspace.py` |
| Tier 2 | wait/emit | covered by `test_wait.py` (protocol-level, not a lifecycle scenario) |
| Tier 2 | spawn-teammate | deferred — not headless-scriptable (multi-pane UI) |
| Tier 2 | df-repo-init, df-ula-file | deferred — BETA, out of scope for this pass |

## Quality benchmark (Layer: lore utilization)

`quality/` measures whether an agent's lore actually improves its output. Each probe plants a
"needle" fact in a fixture agent's lore, runs the agent on a task where that fact should change
the answer, and scores three stages — S1 retrieval, S2 grounding, S3 application (LLM judge) —
across a treatment arm (fact present) and a control arm (fact removed). The headline number is
**behavior uplift**: S3 pass-rate(treatment) − S3 pass-rate(control).

Gated behind `LR_QUALITY=1` (real engine calls, costs money). Two ways to run:

**Single config** — one engine/model, probe×arm parallel inside (`LR_QUALITY_JOBS`, default 3):

```bash
LR_QUALITY=1 python3 tests/quality/test_quality.py -v                     # claude:sonnet
LR_QUALITY=1 LR_ENGINE=codex python3 tests/quality/test_quality.py -v     # codex:gpt-5.4-mini
```

`LR_TEST_MODEL` overrides the model; unset, it defaults to the engine's regular model
(claude:sonnet, codex:gpt-5.4-mini, cursor:composer-2.5).

**Matrix** — `run_matrix.py` drives many configs in parallel, each an isolated
`test_quality.py` subprocess, across two concurrency axes:

```bash
LR_QUALITY=1 python3 tests/quality/run_matrix.py                            # regular, defaults (ship gate)
LR_QUALITY=1 python3 tests/quality/run_matrix.py --matrix deep --model-jobs 3
LR_QUALITY=1 python3 tests/quality/run_matrix.py --matrix deep --skip codex
LR_QUALITY=1 python3 tests/quality/run_matrix.py --model claude=opus-4.8
LR_QUALITY=1 python3 tests/quality/run_matrix.py --configs claude:haiku,claude:opus-4.8
python3 tests/quality/run_matrix.py --matrix deep --dry-run                 # plan only, no spend
```

**Tiers.** `--matrix regular` (the default — a bare `run_matrix.py` runs it) is one
representative "cheapest usable" model per engine; it's the per-release ship gate. `--matrix
deep` is the full engine×model matrix, run only on explicit request (expensive). The tier tables
are canonical defaults in `quality/harness.py` (`REGULAR_MODEL`, `DEEP_MODELS`, `ENGINE_ORDER`),
so a fresh checkout / CI release always resolves to the same default set.

**Configuring the tiers.** For persistent personal reconfiguration without editing code or
affecting releases, drop a git-ignored `quality/matrix-config.local.json` beside the harness:

```json
{ "engine_order": ["claude", "cursor"],
  "regular": {"claude": "opus-4.8"},
  "deep": {"claude": ["sonnet", "opus-4.8"]} }
```

Its keys layer over the defaults — `engine_order` (list) replaces the engine set; `regular`
(engine→model) and `deep` (engine→[models]) update per-engine entries. `--no-local-config` (or
`LR_QUALITY_NO_LOCAL=1`) ignores the file and forces the canonical defaults — **this is what a
release ship gate uses, so ships always pick up the default set regardless of any local file.**
Per-run overrides need no file: `--model claude=opus-4.8` (swap one engine's model), `--configs`
(any explicit set), `--skip`/`--only` (drop/keep engines or `engine:model` pairs).

**Concurrency.**
- `--engine-jobs N` — engines in parallel (default: all; different engines hit different token
  pools, so cross-engine parallelism is free).
- `--model-jobs N` — models of one engine in parallel (default: 1/sequential; models share an
  engine's token pool, so parallelizing them is what risks token/rate exhaustion).

**Failure tolerance.** A config that fails mid-run (e.g. token exhaustion) is recorded and the
rest of the matrix continues; the runner exits non-zero only if an *attempted* config failed
(`--skip`ped configs don't count). Per-config JSON lands in `quality/results/`; the runner prints
each scorecard plus a matrix summary.
