---
lore: 1
type: topic
summary: "Design (2026-08-23, unimplemented, v42 candidate) for an automatic 16h workspace refresh as a second leg of lr-core preflight — its load-bearing decisions and the two implementation traps recorded for whoever builds it."
parent: lore-context.md
---

# Automatic Daily Workspace Refresh (design, v42 candidate)

Full doc: `workdir/draft-workspace-auto-refresh.md` (committed `f09ed9a`, `lore-framework-dev`).
**Design only as of 2026-08-23 — not implemented, targeted at v42, cache-affecting.**

The gap it closes: `/lr:workspace-status` already diagnoses workspace drift and names each fix; what
was missing is that *it never ran on its own*. This is
[freshness-contracts-at-session-boundaries.md](freshness-contracts-at-session-boundaries.md) applied
one layer out — from the agent repo to the whole workspace.

## Shape

`lr-core preflight` gains a **second leg**, after the existing agent-repo `if/else` block. If the
workspace has not been refreshed in 16h it runs `workspace-pull`, then an in-process workspace scan,
and reports only what blocks the user.

## Load-bearing decisions, each with a reason that cost something to find

- **Sequential, not parallel** with the existing agent-repo pull. `workspace-pull` has no TTL
  awareness, so its phase 4 pulls the same repo preflight just pulled — concurrent `git pull` on one
  repo contends on `index.lock`. Parallelism would save ~1s per 16h.
- **16h, not 24h.** A 24h window drifts later every day; 16h always clears overnight.
- **The TTL keys on `last-attempt`, never `last-success`** — otherwise a persistent failure makes
  every boot pay the full timeout.
- **A lock file with `O_EXCL` and a 300s stale reclaim.** Write-before-pull does not exclude across
  processes; both sessions can read stale and both pull. And a killed refresh left a *fresh*
  timestamp, silently disabling the feature for a full TTL window — the exact failure the feature
  exists to prevent.
- **The refresh never clones.** Missing declared repos short-circuit to `setup-required` and defer to
  the user. See
  [short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md).
- **Dirty child repos are reported, not guarded.** See
  [guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md).
- **`findings` reuses `workspace_scan`'s `{id, severity, data}` verbatim**, filtered to `warn`;
  `docs/workspace-status.md` keeps ownership of message and fix prose
  ([script-emits-data-doc-owns-the-words.md](script-emits-data-doc-owns-the-words.md)).
- **`pulled` derives from `git rev-parse HEAD` snapshots**, never from parsing `workspace-pull`'s
  coloured terminal output.
- **`workspace-scan` runs in-process**, not as a subprocess — same package as preflight. That is what
  makes the two-scan structure in the clone short-circuit affordable.

## Traps recorded in the doc for implementers

- **`cli.py` wraps all of `cmd_preflight` in one `except Exception` → exit 2 → *every* boot routes
  into the Manual Boot Procedure.** Every new I/O call must degrade to a status value, never raise.
- **`subprocess.run(timeout=)` SIGKILLs bash only**; `workspace-pull`'s backgrounded `git` children
  survive and keep writing. Needs `start_new_session=True` plus a process-group kill.

Two more surfaced during implementation itself, not while drafting the design:

- **The lock-claim primitive must not collapse "couldn't create the lock" into "contended."** The
  first-ever run on a brand-new workspace hit `FileNotFoundError` (parent dir didn't exist yet)
  inside a bare `except OSError: return False`, reading as normal contention. Fix: a tri-state
  `"claimed"`/`"in-progress"`/`"error"` result, with `os.makedirs` on the lock's parent attempted
  first and kept separate from the `O_EXCL`/staleness logic. See
  [lock-claim-directory-creation-vs-contention.md](lock-claim-directory-creation-vs-contention.md).
- **A new `preflight.py` leg that needs `workspace_scan.py` must import it locally, not at module
  top level.** `workspace_scan.py` imports `preflight` at its own module level, so a top-level
  `preflight.py -> workspace_refresh -> workspace_scan -> preflight` chain fails at load time; the
  fix is a deferred `from . import workspace_refresh` inside `cmd_preflight` itself. See
  [deferred-import-breaks-lr-core-preflight-cycle.md](deferred-import-breaks-lr-core-preflight-cycle.md).

## Deliberately out of scope

A workspace cleanup command. `/lr:workspace-status` already diagnoses and names fixes.

## See Also

- [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md) — the surface this
  automates, including what its scanner does *not* detect.
- [freshness-contracts-at-session-boundaries.md](freshness-contracts-at-session-boundaries.md),
  [auto-pull-mechanism.md](auto-pull-mechanism.md) — the agent-repo-level precedent.
- [framework-improvements-backlog.md](framework-improvements-backlog.md) § Workspace & Environment.
