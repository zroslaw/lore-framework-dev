---
lore: 1
type: topic
summary: "The harness's per-engine plugin-identity gate: how an installed plugin silently substitutes the tree under test, and the deterministic filesystem and engine-init-event checks that close it."
parent: lore-context.md
---

# Lifecycle Harness Doesn't Verify Which Plugin Actually Loaded

`tests/lifecycle/harness.py`'s `run_engine()` passes `--plugin-dir <framework_dir>` to every engine,
but on Codex and Cursor an **installed** plugin can silently win over that flag — the harness never
verifies which plugin actually loaded before trusting the run's result. Found 2026-07-27, running the
lifecycle suite against the parked `wip/lr-core-v31` branch for the first time.

## Confirmed mechanism

On the machine this was found on: Codex's `~/.codex/config.toml` had
`[marketplaces.lore-framework] source = ".../agent-workspace/lore-framework"` (the **main** checkout,
VERSION 30) and `[plugins."lr@lore-framework"] enabled = true` — that installed plugin took precedence
over the `--plugin-dir` flag pointing at the v31 worktree. Cursor's
`~/.cursor/plugins/cache/zroslaw-lore-framework/.../11ec0df.../` was a cached plugin at commit `11ec0df`
= tag `lr--v1.30.0`. Both engines ran a full lifecycle suite against **v30** while the harness, its
logs, and its summary all reported results as if v31 had been tested — nothing failed loudly; the tree
under test was just silently wrong.

Claude Code was unaffected only because nothing is installed for it globally on this machine —
`--plugin-dir` was the sole source. That's incidental to this machine's state, not a property of the
harness or of Claude Code generally; a machine with a globally-installed Claude plugin could hit the
same failure mode there too.

## Why this matters more than an ordinary coverage gap

A green run under this condition is a **false green on the actual release artifact**, and a red run is
equally uninterpretable — both look like valid gate results with nothing to distinguish them from a
genuine pass/fail. This is functionally the same danger as the sandboxed-review blind spot already in
lore (`lore-beings-mvp-takeover-review.md`, and the general rule in `role.md` § Lore-Curation
Disciplines), but via a **different mechanism**: not a blocked capability forcing an
"unverifiable" branch to run silently, but the environment substituting a *different artifact
entirely* for the one requested. Whether this counts as the second occurrence that promotes
`sandbox-degraded-review-blind-spot` to its own topic is a judgment call for whoever next reviews that
bar — the *shape* (environment quietly invalidates a gate result without erroring) matches; the
*mechanism* (artifact substitution vs. capability block) doesn't.

## Fix (harness) — applied

`tests/lifecycle/harness.py` now gates on plugin identity before trusting results
(merged to `lore-framework-dev` `main` 2026-07-27: A7 + follow-up hotfixes):

1. **`verify_plugin_identity`** — once per process, asks the engine to report
   `FRAMEWORK-ROOT` / `PLUGIN-VERSION` for the plugin that actually supplies lr skills, and
   asserts against `LR_FRAMEWORK_DIR`.
2. **VERSION form normalization** — accept bare `VERSION` (`30`) and plugin-manifest
   `1.30.0` as the same identity (`normalize_framework_version`). Live Claude probes reported
   the manifest form.
3. **Codex deterministic preflight** — because Codex has no `--plugin-dir`, check that an
   enabled `lr@lore-framework` marketplace `source` realpath-equals `LR_FRAMEWORK_DIR` and
   that the plugin cache has a matching VERSION. After that preflight, the engine probe uses
   **VERSION-only** (`require_root=False`): Codex always installs into a cache copy, so
   `FRAMEWORK-ROOT` never equals the worktree realpath even when correct.
4. **`run_matrix.py`** — runs the check once per engine and **skips that engine's modules** on
   failure (exit 2), so a wrong install cannot produce a false green across 7 modules.
5. **`run_engine`** — lazy same check on direct module invocation (`python3 tests/lifecycle/test_*.py`).

Opt-out: `LR_SKIP_PLUGIN_IDENTITY=1` (debug only). Unit coverage:
`tests/test_lifecycle_plugin_identity.py`.

## A7 shipped with two holes — both closed 2026-07-28

A7 passed on Cursor on 2026-07-27 and the suite still ran against v30. Reading the stored logs
found **two structural holes in `harness.py`**, plus a third defect in the evidence class of the
Cursor arm:

1. **Per-run `framework_dir` overrides were never checked.** The docstring assumed overrides were
   "absolute-path copies of the same tree." `test_08` is the only scenario handed a *different*
   tree — so the one test that needed verification was precisely the one skipping it.
2. **The check was cached per process** (`_IDENTITY_CHECKED_FOR`). That proves identity at probe
   time only, not that it still held for later runs in the same process.
3. **The Cursor arm was a model self-report, not a check.** It asked the engine which plugin root
   supplied its `lr` skills — unanswerable from inside a model. It reported
   `PLUGIN-IDENTITY-OK 31 <worktree>` truthfully (it read `--plugin-dir`'s tree) while a different
   tree served the skills. Codex was never exposed to this because
   `check_codex_plugin_sources()` was filesystem-deterministic from the start; the asymmetry was
   invisible because both engines "had A7 coverage." See `a-gate-cannot-be-a-model-self-report.md`.

**Fixes applied** (`lore-framework-dev` main, `03067c1` / `848d3fc`):

- Per-run `framework_dir` overrides are now verified, not assumed.
- The per-process cache is replaced by a verdict inherited through an `engine|realpath|VERSION`
  token, while each child subprocess still runs the deterministic filesystem check itself. This
  also removed the `test_takeover` 420s timeout, which was `run_matrix` probing once per engine and
  then every module subprocess re-probing.
- **`check_cursor_plugin_sources()`** — walks `~/.cursor/plugins/{local,marketplaces,cache}` and
  rejects any tree whose `VERSION` differs from `LR_FRAMEWORK_DIR`. Filesystem only, no engine
  call. Against the real machine state it named both stale v30 trees immediately.

**These fixes were subsequently exercised by the v33 full release gate** on Cursor/Composer 2.5,
Codex/gpt-5.4-mini, and Claude/Haiku, including the separate Keeper track. The result is valid
only because the installed-source checks and the identity probe passed before each shard.

**Cursor operational companion:** disabling/repointing alone is incomplete — Cursor's cloud
marketplace install rehydrates the cache from GitHub over `--plugin-dir`, and does so within ~25
seconds of a move-aside. See `cursor-cloud-plugin-rehydrates-over-plugin-dir.md`.

## v33 refinements (2026-07-29)

Plugin identity has two evidence layers: deterministic installed-source preflight where an engine
has a persistent marketplace/cache path (Codex and Cursor), and a loaded-plugin
`FRAMEWORK-ROOT`/`PLUGIN-VERSION` probe for the engine invocation. Keep both. The former prevents
an installed tree from silently taking precedence; the latter verifies the emitted identity of the
loaded bundle. Claude has no corresponding local marketplace preflight in this harness, so its
probe remains especially important.

The identity parser must be strict about the identity token but tolerant of presentation noise.
Cursor/Composer appended its completion sentence directly to `PLUGIN-VERSION: 33`; extracting only
the leading bare or manifest-version token preserves the assertion against the expected framework
version without accepting a mismatched version.

Per-run temporary framework copies are also engine-specific. Claude and Cursor load an explicit
plugin directory, so their override scenarios retain the deterministic installed-source check.
Codex has no per-invocation plugin-directory flag: its fallback fixture names the copied docs
directly while the installed marketplace baseline remains the identity being preflighted. Do not
require Codex's marketplace source to equal a temporary fixture copy; that would make the fallback
scenario impossible rather than safer.

## The Claude arm was the *third* self-report — fixed from the engine init event (v41, 2026-08-17)

Cursor's model-self-report arm was fixed in v33; **Claude's was the same defect, left standing, and
it eventually blocked an entire engine.** The Claude arm asked the *model* which plugin root supplied
its `lr` skills. On a machine with `lr` installed from the marketplace, the model greps the plugin
cache and reports that path, while the engine had actually loaded the `--plugin-dir` tree. In one
probe it cited a `.cursor-skills/` path Claude Code never registers at all. Result: **every correct
Claude run was reported as a mismatch and the whole shard refused to start.**

Ground truth is the engine's own stream-json **`system`/`init` event**, which enumerates each loaded
plugin with its `path` and `source`. It showed exactly one `lr` plugin, `source: lr@inline`, path =
the tree under test — so `--plugin-dir` wins cleanly over the installed marketplace plugin, the
opposite of what the model reported.

Reading that event removes the model from the loop entirely: green on the real tree, red on a
mismatched one, **~4.5s instead of ~20.5s**, and it now also catches a `plugin.json` disagreeing with
`VERSION`.

This is the second confirmed instance of the Cursor-arm failure shape, this time blocking a whole
engine rather than one arm. See `a-gate-cannot-be-a-model-self-report.md`.

**Costly corollary — don't build the fix on the self-report's premise.** Before touching the identity
gate, an entire `--settings enabledPlugins:false` mechanism plus a new shared test module wired into
three harnesses was built on the model's claim that the marketplace cache outranks `--plugin-dir`.
Deterministic ground truth showed the opposite, and all of it was reverted. Even the intermediate
canary probe — planting a marker in a copied tree and asking the model which body it saw — was still
a model self-report, and gave a wrong answer. A failing gate names an **observation, never a
mechanism**: get engine-emitted ground truth first. See
`verify-before-acting-on-suspected-bugs.md`.

## Concrete instance this bit

The 2026-07-27 *first* lifecycle run against the parked v31 branch (`v31-lr-core-parked-2026-07-25.md`):
Claude/haiku produced the only trustworthy result (6/7 green, one flaky scenario root-caused and fixed
— see `macos-var-symlink-realpath-ambiguity.md`); Codex and Cursor's results from that same run were
**invalid, not red**.

The second run, after A7 + engine repoint, was only *partly* rescued: Codex's shard became valid,
but **Cursor's shard was still uninterpretable** — holes 1–3 above let it run on v30 again. That was
found only on 2026-07-28 by reading the stored logs. See
`v31-lifecycle-rerun-partial-green-2026-07-27.md` for the corrected triage; do not trust the
original six-item failure list from that run.

## See Also

- `lifecycle-testing-harness.md` — the harness this gap lives in.
- `a-gate-cannot-be-a-model-self-report.md` — the principle the Cursor arm violated; the general
  rule this instance produced.
- `cursor-cloud-plugin-rehydrates-over-plugin-dir.md` — Cursor-specific rehydration over `--plugin-dir`.
- `transcript-vs-final-message-assertions.md` — the sibling harness-evidence defect found in the
  same 2026-07-28 log review.
- `v31-lr-core-parked-2026-07-25.md` — the concrete run this invalidated, plus the valid re-run.
- `lore-beings-mvp-takeover-review.md` — the sibling sandboxed-review blind spot (blocked capability,
  not artifact substitution).
- `post-convergence-edits-need-their-own-gate.md` — the adjacent framing that a gate result belongs to
  a specific artifact state; this is a sharper case where the state was never the intended one at all.
- `macos-documents-permission-loss-mid-session.md` — another "environment makes a run uninterpretable"
  case, different mechanism (permission loss vs. wrong artifact resolved).
