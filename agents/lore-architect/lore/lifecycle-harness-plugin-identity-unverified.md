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

**Cursor operational companion:** disabling/repointing alone is incomplete — Cursor's cloud
marketplace install rehydrates the cache from GitHub over `--plugin-dir`. See
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`.

## Concrete instance this bit

The 2026-07-27 *first* lifecycle run against the parked v31 branch (`v31-lr-core-parked-2026-07-25.md`):
Claude/haiku produced the only trustworthy result (6/7 green, one flaky scenario root-caused and fixed
— see `macos-var-symlink-realpath-ambiguity.md`); Codex and Cursor's results from that same run were
**invalid, not red**. After A7 + engine repoint, a second run produced valid (partially green) results —
see that parking topic's later addendum / `v31-lifecycle-rerun-partial-green-2026-07-27.md`.

## See Also

- `lifecycle-testing-harness.md` — the harness this gap lives in.
- `cursor-cloud-plugin-rehydrates-over-plugin-dir.md` — Cursor-specific rehydration over `--plugin-dir`.
- `v31-lr-core-parked-2026-07-25.md` — the concrete run this invalidated, plus the valid re-run.
- `lore-beings-mvp-takeover-review.md` — the sibling sandboxed-review blind spot (blocked capability,
  not artifact substitution).
- `post-convergence-edits-need-their-own-gate.md` — the adjacent framing that a gate result belongs to
  a specific artifact state; this is a sharper case where the state was never the intended one at all.
- `macos-documents-permission-loss-mid-session.md` — another "environment makes a run uninterpretable"
  case, different mechanism (permission loss vs. wrong artifact resolved).
