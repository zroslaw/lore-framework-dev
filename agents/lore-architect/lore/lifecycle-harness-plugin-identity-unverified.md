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

## Fix needed (harness, not yet applied)

Before trusting any engine's lifecycle result, the harness should probe the loaded plugin's actual
`VERSION` (a cheap boot-time check, or a dedicated preflight scenario) and assert it equals
`framework_version()` of the `LR_FRAMEWORK_DIR` under test. Fail loudly and immediately on a mismatch,
rather than letting all 7 modules run to completion against the wrong tree. Filed as a harness fix on
`workdir/what-to-improve.md` and belongs in `framework-improvements-backlog.md` under whatever section
covers the lifecycle harness.

## Concrete instance this bit

The 2026-07-27 lifecycle run against the parked v31 branch (`v31-lr-core-parked-2026-07-25.md`):
Claude/haiku produced the only trustworthy result (6/7 green, one flaky scenario root-caused and fixed
— see `macos-var-symlink-realpath-ambiguity.md`); Codex and Cursor's results from that same run are
**invalid, not red** — both must be re-run once their sources are repointed at the actual worktree.

## See Also

- `lifecycle-testing-harness.md` — the harness this gap lives in.
- `v31-lr-core-parked-2026-07-25.md` — the concrete run this invalidated.
- `lore-beings-mvp-takeover-review.md` — the sibling sandboxed-review blind spot (blocked capability,
  not artifact substitution).
- `post-convergence-edits-need-their-own-gate.md` — the adjacent framing that a gate result belongs to
  a specific artifact state; this is a sharper case where the state was never the intended one at all.
- `macos-documents-permission-loss-mid-session.md` — another "environment makes a run uninterpretable"
  case, different mechanism (permission loss vs. wrong artifact resolved).
