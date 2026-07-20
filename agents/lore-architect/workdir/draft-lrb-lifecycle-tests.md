# DRAFT — Being Keeper Lifecycle Test Scenarios (real-engine catalog)

Design draft, 2026-07-20. Companion to `draft-lore-beings.md` (the Keeper design + build/review
history) and `tests/README.md`'s existing 27-scenario Layer-3 lifecycle catalog. **Design only —
nothing here has been built.** Scope: what a *real* engine subprocess must validate about the
Being Keeper that the 76-test stub-engine suite (`tests/test_lrb.py`) structurally cannot, run
against all three engine kinds the Keeper spawns (`claude`, `codex`, `cursor`).

## 0. What this catalog deliberately does NOT re-cover

`tests/test_lrb.py` already exercises, deterministically and at zero cost, against a stub engine:
scheduling math (cron, missed-fire catch-up, same-day dedup), the daily-USD spawn gate and
concurrency cap, outbox validation (horizon, budget, malformed requests), PID-identity *logic*
(reuse detection, confirmed-match/-mismatch/unknown branches — with the check itself mocked/
stubbed), crash-safety (state.json corruption, re-adoption after restart), the single-instance
daemon lock, and CLI plumbing (`engines add` validation, `schedule`, `pause`/`resume`). None of
that is redesigned here. This catalog exists for exactly one reason: **only a real engine
subprocess can prove the Keeper's actual invocation of `claude`/`codex`/`cursor-agent` is correct**
— real argv, real headless behavior, real result-JSON shape, real cost fields, real process trees
to kill, real `ps` output to parse identity from.

## 1. Prerequisite: home-directory sandboxing — ALREADY EXISTS, no code change needed

Checked `scripts/lrb.py` directly (`lrb_home()` / `launchagents_dir()`, lines 78–86): `$LRB_HOME`
(default `~/.lore-beings/`) and `$LRB_LAUNCHAGENTS_DIR` (default `~/Library/LaunchAgents`) are
**already** environment-var overridable, specifically so the CLI is sandboxable for tests — this
was a deliberate build-time decision (§5 of the design draft: "adopted during the build... makes
the whole CLI sandboxable for tests as a result"). `tests/test_lrb.py`'s `LrbTestCase.setUp` and
`tests/test_lrb_cursor_real_e2e.py` already both use exactly this mechanism per-test/per-run. **No
prerequisite code change is required before writing Keeper lifecycle tests.** The design below is
just "use the mechanism that's already there, consistently, with guaranteed teardown around it."

One thing that is *not* yet a convention, because no test needed it before: a shared,
reusable fixture helper that sets/restores these two env vars safely across a `unittest` class
(the existing users are either a single `LrbTestCase.setUp`/`tearDown` pair or a one-shot
standalone script). §4 below proposes that helper.

## 2. Scenario catalog

Tiers reflect priority/cost tradeoff, not execution order. **Tier A is the ship-gate-equivalent
minimum** (mirrors `quality/`'s "regular" vs "deep" matrix split in spirit — one representative
real pass per engine kind first, everything else is depth added on top).

| # | Scenario | Engine kind(s) | Stub-safe or real-required | Cost-risk |
|---|---|---|---|---|
| A1 | Core loop: existential task fires → real spawn → result parsed → cost charged → ledger `ok` → no same-day refire | claude | **real-required** | low |
| A2 | Core loop (codex): JSONL `turn.completed` parsed, usage tokens ledgered, flat `session_cost_usd` charged | codex | **real-required** | low |
| A3 | Core loop (cursor): claude-shaped JSON parsed, real `total_cost_usd` charged | cursor | **real-required** | low (already exists — `test_lrb_cursor_real_e2e.py`, see §6) |
| B1 | Timeout kill takes down the **real process tree**, not just the direct child | claude | **real-required** | low–medium |
| B2 | Timeout kill takes down the real process tree | codex | **real-required**, lower priority | low–medium |
| B3 | Timeout kill takes down the real process tree | cursor | **real-required**, lower priority | low–medium |
| C1 | Self-scheduling round trip via real Bash-invoked `lrb schedule` (permission_mode full) | claude | **real-required** | low–medium (sonnet-class, see §7) |
| C2 | Self-scheduling round trip | codex | **real-required**, lower priority | low–medium |
| C3 | Self-scheduling round trip | cursor | **real-required**, lower priority | low–medium |
| C4 | Self-scheduling **denied** under `permission_mode: default` — being reports the denial, doesn't hang, tick loop keeps going | claude | **real-required** | low |
| D1 | PID-identity re-adoption check against a **real engine's actual `ps` command string** (not the stub's) | claude | **real-required** | low |
| D2 / D3 | Same, codex / cursor | codex / cursor | **real-required**, lower priority | low |
| E1 | `lrb daemon` as an actual OS subprocess (not the in-process `Keeper().tick()` loop every other tier uses) — daemon.lock, SIGTERM shutdown, minimal launchd-shaped PATH env, one real spawn inside it | claude | **real-required** | low, but highest *process*-risk (see §5) |

13 scenarios total; **9 are the recommended minimum** (A1–A3, B1, C1, C4, D1, E1); B2/B3/D2/D3 are
explicitly marked lower-priority extensions (§8 explains why).

## 3. Per-scenario assertions

**A1/A2/A3 — core loop.** Build one being with one existential task on `this_minute_cron()` (same
helper pattern as `LrbTestCase`), engine configured for real (`shutil.which("claude"/"codex"/
"cursor-agent")`, real `--kind`, and for codex a real `--session-cost-usd`, for cursor a real
`--plugin-dir` pointing at `FRAMEWORK_DIR`). Drive `Keeper().tick(cfg)` in a poll loop (the
pattern already in `test_lrb_cursor_real_e2e.py`) until `running` is empty and `last_runs` is set.
Assert: ledger's last entry has `outcome == "ok"`; `cost_usd` is a **positive** float (not the
stub's canned value — this is the whole point: real cost reporting shape); for codex, `cost_usd`
equals exactly the configured flat rate and `usage` is present with real token counts; for
claude/cursor, `usage` (if present) has real token counts and `cost_usd` came from the engine's own
`total_cost_usd`, not a fallback. Assert `state.json`'s `spent_today_usd` reflects the same charge.
Assert the per-session log file on disk contains the real engine's JSON/JSONL, and the **sibling
`.stderr.log`** exists (may be empty for claude/cursor; for codex, assert it's non-empty — codex is
*documented* (docs/beings.md, built from real observation) to write spurious `ERROR` lines to
stderr on successful runs, and this is the exact scenario that proves stderr/stdout separation
still protects cost parsing against that real noise, not just the stub's simulated
`STUB_STDERR_NOISE`). Assert `lrb status --json` (drive via the CLI subprocess, not just in-process
state) shows the same being with `last_outcome: "ok"` and a non-empty `log_dir`.

**B1/B2/B3 — real process-tree kill.** Task prompt instructs (with `permission_mode: full` so Bash
isn't denied) something that spawns a real child the Keeper must kill as a *tree*, e.g. "run `bash
-c 'sleep 120 & wait'` via your Bash tool and report when done" with `timeout-minutes: 1`. Before
the timeout fires, capture the *child* `sleep` PID (parse it from the session log / a marker file
the task prompt is told to write, e.g. `echo $! > sleep.pid`). Drive the tick loop until the Keeper
marks the session `timeout` and kills it. Assert: the ledger's outcome is `"timeout"`; **the
captured child `sleep` PID is also dead** (`os.kill(pid, 0)` raises `ProcessLookupError`) — this is
the concrete regression test for the round-1 finding "a kill signaled only the direct child... Bash/
MCP-server grandchildren could survive a 'hard kill'" (draft §16), now proven against a real
engine's real child-spawning shape instead of a stub that never spawns children.

**C1/C2/C3 — self-scheduling round trip.** `permission_mode: full`. Task prompt: "Using Bash, run
exactly this command (fill in `<N>` and `<datetime>`): `<the lrb_invocation from your spawn
prompt> schedule --agent <being_id> --at \"<now + 10 minutes, ISO, no tz>\" --timeout-minutes 10
\"Reply with exactly OUTBOX-ROUNDTRIP-OK\"`; then print DONE." Drive one tick (accepts into
`outbox/accepted/`), assert the accepted file exists with the right being/timeout, then drive the
tick loop forward past the requested `--at` (test controls wall-clock only by picking a near-future
`--at` and waiting for real time to pass — no clock mocking, since this is deliberately testing the
*real* Keeper process against *real* time, matching the real 30s tick cadence). Assert a second
ledger entry appears with `task == "work-session"`, `outcome == "ok"`, and the child session's log
contains `OUTBOX-ROUNDTRIP-OK`. This exercises exactly the seam flagged in draft §16 as "a genuine,
not-yet-closed gap": `lrb` is never on PATH, so the being must use the concrete invocation from its
own spawn prompt correctly, with correct shell quoting, under time pressure of a real model call.

**C4 — self-scheduling denied under default permission.** Same task prompt, `permission_mode:
default` (no `--dangerously-skip-permissions`). Drive the tick loop to completion. Assert: no file
appears in `outbox/` at all (the Bash call was denied, never executed); the ledger's `outcome` is
still `"ok"` (the *session* completed normally — it just couldn't do the denied thing); the
session's final output/log contains language indicating the being recorded the denial rather than
silently succeeding or hanging past its timeout. This is the regression test for §16's explicitly
named "genuine gap" — proving the being's own `being.md`-prescribed "don't block, report it"
behavior actually happens against a real engine's real permission system, not just that the prose
asks for it.

**D1/D2/D3 — real PID-identity.** Start a real session (`timeout-minutes` generous, task is a
trivial echo prompt with `permission_mode: full` not required). While it's running, capture its PID
from `state.json`'s `running` entry, and independently call the real `ps -p <pid> -o command=`
(exactly what `_pid_identity` does) to see what the *real* engine's command string looks like versus
the recorded `entry["command"]` (the configured engine path). Then simulate a Keeper restart:
construct a **fresh** `Keeper()` instance (empty `live_procs`, so the entry is "re-adopted" rather
than tracked) and call `_pid_matches_entry(pid, entry)` directly. Assert it returns `True` while the
session is genuinely still running (the confirmed-match branch, exercised for real). This is the
direct regression test for the fourth-review finding (draft §16): a sandboxed test environment that
blocks `ps` forces every identity check down the "unknown" path and can *never* exercise the
confirmed-match/-mismatch branches at all — silently green-lighting code whose primary path never
ran. §9 below states this as a hard environment prerequisite for the whole suite, not just D1–D3.

**E1 — real `lrb daemon` subprocess.** Unlike A–D (which all drive `Keeper().tick(cfg)` in-process,
same pattern as the existing cursor e2e), E1 launches `python3 <lrb.py> daemon` as an actual
`subprocess.Popen`, with `LRB_HOME`/`LRB_LAUNCHAGENTS_DIR` sandboxed and — specifically — a
**minimal PATH** (`/usr/bin:/bin:/usr/sbin:/sbin`, matching what launchd itself gives a job) rather
than the test's own rich shell PATH, to probe whether a real engine binary with a `#!/usr/bin/env`
shebang still resolves the way `cmd_install`'s plist-PATH-capture exists to guarantee (round-1
finding M7). Register a being with a real (cheap) engine, wait (via `lrb status --json` polled as a
subprocess, not in-process state — this must look exactly like an operator watching a real daemon)
for one ledger entry, then send SIGTERM to the daemon subprocess and assert: it exits within a few
seconds (graceful shutdown, not a hang); `$LRB_HOME/daemon.lock` is released (a second `lrb daemon
--once` immediately after does *not* refuse to start); no orphaned engine subprocess remains. This
is the only scenario in the catalog that touches the actual code path `launchd` will run in
production — every other tier deliberately avoids spawning `lrb daemon` itself to keep blast radius
down, per constraint 2.

## 4. Fixture/teardown strategy

**Reuse from `tests/lifecycle/harness.py` as-is:** `FRAMEWORK_DIR`, the `LR_TEST_MODEL`/
`LR_RUN_TIMEOUT`/`LR_KEEP_FIXTURES`/`LR_DEBUG_DIR` env-knob conventions and their exact semantics,
`_debug_dump`, and the general "tempdir + `addCleanup(shutil.rmtree, ...)`" fixture shape. These
transfer directly — nothing about them is Keeper-specific.

**What does NOT transfer, and needs a new sibling module** (`tests/lifecycle/keeper_harness.py`,
not a modification of `harness.py` — the concerns are different enough that cramming them in would
blur both): `harness.py` runs one headless engine call and inspects files/git state afterward; it
never manages a long-lived daemon-shaped process, a tick-loop poll, or process-group teardown.
Concretely, `keeper_harness.py` needs:

- `load_lrb()` — `importlib` load of `scripts/lrb.py`, identical to `test_lrb.py`'s
  `load_lrb_module()` (can literally be copied — it's 5 lines).
- `KeeperFixture` — a context manager: makes a tempdir, sets `LRB_HOME`/`LRB_LAUNCHAGENTS_DIR`
  into it (saving/restoring prior env values, same discipline as `LrbTestCase.setUp`/`tearDown`'s
  explicit pop-lists — this matters more here than in `test_lrb.py` because real-engine tests run
  much longer and a leaked env var has a bigger window to leak into an accidental real spawn),
  builds the workspace + being.md + task file(s), and writes a `config.json` with the **real**
  configured engine (probed via `shutil.which`, same shape `cmd_engines_add` would produce — reuse
  `lrb.require_plugin_dir`/`require_finite_nonnegative_float` directly from the loaded module
  rather than re-validating by hand).
- `run_tick_loop_until(keeper, cfg, workspace, being_id, predicate, deadline_s)` — generalizes the
  poll loop already written once in `test_lrb_cursor_real_e2e.py` (`while time.monotonic() <
  deadline: keeper.tick(cfg); ...; time.sleep(2)`) into a shared helper so A/B/C/D scenarios don't
  each reimplement it.
- `TeardownGuard` — **the constraint-2 mechanism.** A context manager whose `__exit__` runs
  unconditionally (success, assertion failure, or exception) and: (1) reloads `state.json` for the
  fixture workspace, and for every entry in every being's `running` list, verifies identity via the
  loaded module's own `_pid_matches_entry` (reusing the Keeper's real PID-reuse guard rather than a
  bare `kill` — this fixture must not accidentally SIGKILL an unrelated reused PID either) and
  SIGKILLs the process group if it matches, regardless of whether the entry is past its configured
  timeout; (2) if a `lrb daemon` subprocess handle was registered (E1 only), SIGTERM it, wait up to
  a few seconds, SIGKILL if still alive, and always `.wait()` on it to avoid a zombie. This must
  fire even when the test's own assertions raise mid-scenario — that's the entire point of
  constraint 2, and the existing `addCleanup(shutil.rmtree, tmp)` pattern alone doesn't cover it
  (deleting the fixture directory doesn't kill a still-running process rooted elsewhere).
- `engine_available(kind)` — generalizes `test_lrb_cursor_real_e2e.py`'s `cursor_logged_in()`
  (checks *authenticated*, not just *on PATH* — `harness.py`'s own `ENGINE_AVAILABLE` only checks
  `shutil.which`, which is not strict enough for Keeper scenarios where a present-but-logged-out
  binary would otherwise fail loudly mid-scenario instead of skipping cleanly) into one function
  covering all three engines' own auth-probe idiom (`claude`: a trivial `-p` call; `codex`: `codex
  login status` or equivalent; `cursor`: the existing `cursor-agent status` check, unchanged).

## 5. Env knobs

**Separate gate, not folded into `LR_LIFECYCLE`: `LR_LIFECYCLE_KEEPER=1`.** Reasoning, directly
answering the team lead's question: the 27 existing scenarios' worst case is "one headless engine
call that costs money and leaves files in a tempdir." Keeper scenarios' worst case additionally
includes "a real background process that can outlive the test" (E1) and "a real process tree the
Keeper must correctly kill" (B1–B3) — a strictly higher blast-radius class even with `TeardownGuard`
as a backstop. Someone comfortable opting into `LR_LIFECYCLE=1` (money spend) has not necessarily
signed up for "and also a daemon-shaped process might exist briefly on my machine." A distinct flag
lets CI or a developer run the cheap/existing 27 without ever touching Keeper-specific process risk,
and vice versa. Reuse everything else unchanged: `LR_ENGINE` (which single engine's scenarios run —
matches the existing convention in every other `lifecycle/test_*.py`), `LR_TEST_MODEL` (override,
see §7 for defaults), `LR_RUN_TIMEOUT`, `LR_FRAMEWORK_DIR`, `LR_KEEP_FIXTURES`, `LR_DEBUG_DIR`.

```bash
LR_LIFECYCLE_KEEPER=1 LR_ENGINE=claude python3 tests/lifecycle/test_lrb_lifecycle.py -v
LR_LIFECYCLE_KEEPER=1 LR_ENGINE=codex  python3 tests/lifecycle/test_lrb_lifecycle.py -v -k A2
```

## 6. File/module layout

**Recommend one file, `tests/lifecycle/test_lrb_lifecycle.py`, gated by `LR_ENGINE` like every
other file in `lifecycle/`** — not split per engine kind. Justification: the existing convention
(`test_boot.py`, `test_repo_workspace.py`, etc.) already handles "this scenario only makes sense
for one engine" via `self.skipTest(...)` inside a shared file (see `test_boot.py`'s
`test_07_boot_repo_newer_than_framework_codex_guidance`, which skips unless `LR_ENGINE == "codex"`)
rather than separate files — splitting Keeper tests into three files would be the one inconsistent
corner of the suite for no real benefit, since a single test run only ever drives one `LR_ENGINE`
at a time anyway. The one existing precedent that *does* stand alone,
`tests/test_lrb_cursor_real_e2e.py`, predates this convention (it's a standalone script, not
`unittest`, and lives outside `lifecycle/` entirely) — recommend **migrating its scenario into the
new file as A3** (folding in the stronger A1/A2-parity assertions from §3: `lrb status --json`
check, explicit `usage` check) and retiring the standalone script, rather than maintaining two
parallel patterns for the same engine kind indefinitely. This is a call-it-out, not a blocker — if
the team wants to keep the standalone script alive a bit longer during migration, that's fine too.

## 7. Cheapest-viable-model recommendation per engine kind

| Engine | Recommended model | Basis |
|---|---|---|
| claude | **haiku** (4.5) | Already the Chronicler's production model and the exact model real-verified through the tick loop during the build (draft §16: "claude/haiku: result JSON parsed, real $0.0188 charged"). Proven reliable for short, mechanical, well-specified prompts. |
| codex | **gpt-5.4-mini** | Matches `harness.py`'s existing default for codex and the exact model real-verified through the tick loop during the build (draft §16: "codex/gpt-5.4-mini: `E2E-CODEX-OK`, flat $0.05 charged"). |
| cursor | **composer-2.5** | Matches `LRB_CURSOR_MODEL`'s existing default in `test_lrb_cursor_real_e2e.py` — the only cursor model so far validated against the Keeper loop at all. |

**Flag: C1/C2/C3 (self-scheduling) are the one place a cheap model is likely too unreliable.**
Constructing the exact `lrb schedule --agent ... --at "<ISO, no tz, within 24h>" --timeout-minutes
N "..."` invocation from prose instructions — correct shell quoting, correct relative-datetime
arithmetic, using the *exact* invocation string from its own spawn prompt rather than typing bare
`lrb` — is meaningfully harder than "echo a codeword" or "run one fixed Bash command," and a wrong
quote or a slightly-off datetime doesn't produce a clean Keeper-side rejection so much as a request
that silently never lands, or a `rejected/` file the test then has to distinguish from "harness
bug" vs "model got the syntax wrong." **Recommend the next tier up for C1–C3 specifically**: sonnet
for claude, the standard (non-mini) codex model, and only fall back to the cheaper defaults if
observed reliable in practice. Getting a false failure from model flakiness rather than a real
Keeper bug defeats the point of the scenario, and the cost delta for three short sessions is small
next to the debugging cost of a flaky real-engine test.

## 8. Why B2/B3/D2/D3 are marked lower-priority, not cut

The mechanisms under test in Tier B (process-group `killpg` after `start_new_session=True`) and
Tier D (`_pid_matches_entry`'s two-separate-`ps`-calls identity check) are implemented once, in the
Keeper's own code, engine-agnostically — they don't branch on `engine_kind` at all. The risk that
would justify running B/D against codex and cursor too is specifically "does *this* engine's own
child-process-spawning shape (or its own binary's `ps` command-string shape) defeat a mechanism
that works fine for claude" — plausible (Codex's own sandboxing wrapper is exactly the kind of thing
that could differ) but unconfirmed. Recommend: ship B1/D1 (claude) first as the representative
proof the mechanism works against a real engine at all, and add B2/B3/D2/D3 only if (a) a real
incident or the Chronicler's week-long soak run surfaces an engine-specific gap, or (b) the team
wants stronger assurance before enabling `permission_mode: full` broadly across engines. This is
the same "regular vs deep matrix" tradeoff `quality/run_matrix.py` already makes explicit for a
different test family in this repo.

## 9. What only a real-engine test can catch (cross-referencing the review history)

- **Sandboxed-`ps`-blind-spot** (draft §16, fourth review): the single most concrete lesson in the
  Keeper's build history. A review/test environment that blocks `ps` forces every PID-identity call
  down the "unknown" branch and can *never* exercise confirmed-match/-mismatch — a suite that
  passes there proves nothing about the primary path. **This is a hard prerequisite for the whole
  catalog, not just D1–D3**: whoever runs `LR_LIFECYCLE_KEEPER=1` must do so on a real shell with
  working `ps`, not inside a permission-sandboxed CI runner or agent environment that blocks it —
  state this explicitly in the file's module docstring the way `harness.py` states its own
  gating rationale, so a future contributor doesn't accidentally "verify" the suite somewhere it
  structurally can't.
- **Stderr-noise-vs-cost-parsing fragility** (draft §16, round 1 H2): only real codex is documented
  to actually emit spurious stderr `ERROR` lines on success. A2's assertion on the sibling
  `.stderr.log` content is the only place in the whole suite (stub included) that exercises this
  against the real noise shape rather than a simulated `STUB_STDERR_NOISE` flag.
- **Kill-the-whole-tree, not just the child** (draft §16, round 1 H4): the stub engine is a flat
  single process — it structurally cannot expose "grandchildren survive a hard kill." B1 is the
  first test in the suite that gives the Keeper something with real grandchildren to kill.
- **`lrb` not on PATH / self-scheduling under real permission semantics** (draft §16, the
  build's own "genuine, not-yet-closed gap"): C1–C4 are the direct regression coverage for exactly
  the seam the design draft names as unresolved by construction, not oversight.
- **Cross-midnight budget accounting** — deliberately **excluded** from this catalog (already
  stub-covered by `test_daily_budget_resets_on_rollover` / `test_session_started_before_midnight_
  does_not_charge_new_day`); a real-engine version would require manipulating wall-clock/system time
  around midnight, which is a different and separately risky can of worms, not a Keeper-specific gap
  that only a real engine could reveal.

## 10. Explicitly do not attempt yet

- **`lrb install --launchd` actually loading into real launchd.** Not "not yet" — permanently out
  of scope for automated tests, full stop, per constraint 1. The non-`--launchd` plist-writing path
  is already covered (`test_install_is_sandboxed_and_idempotent`); real launchd install stays the
  deliberate, separate, user-triggered step the design draft already insists on (§5, §12).
- **B2/B3/D2/D3** (codex/cursor process-tree-kill and PID-identity) — reason: §8.
- **A full Chronicler-week-style multi-day soak as an automated test.** That's the MVP's own
  manual-run success criteria (draft §13), evaluated by a human reading the diary — not a
  CI-shaped assertion, and multi-day real-clock tests are their own risk category entirely
  separate from this catalog.
- **Cross-midnight real-engine spend accounting** — see §9's last bullet; stays stub-only.
