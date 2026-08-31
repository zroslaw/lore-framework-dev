---
lore: 1
type: topic
summary: "The automatic 16h workspace refresh shipped in v42 as a second leg of lr-core preflight — its load-bearing decisions, the two design-time traps, and the shipped bug where its state root follows cwd instead of the workspace."
parent: lore-context.md
---

# Automatic Daily Workspace Refresh (designed 2026-08-23, shipped in v42)

Full doc: `workdir/draft-workspace-auto-refresh.md` (committed `f09ed9a`, `lore-framework-dev`).
Designed 2026-08-23 and **shipped in v42** (2026-08-23, cache-affecting). The decisions below
survived implementation; keep them as the record of *why* the leg looks the way it does.

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

## Bug found in use: state root follows cwd, not the workspace (2026-08-31)

Observed during a finalization, not designed for. Merge's Step 0 specifies:

```
python3 "<framework-root>/scripts/lr-core" preflight --agent-dir "<agent-dir>" --fresh --no-teammate-check
```

No `--workspace`, so it defaults to the current directory — and my cwd was
`<repo>/agents/lore-architect/reflections/`, where I had just written the reflection topics. The
refresh leg then created **`reflections/.tmp/lr-state/workspace-refresh`**, a second state file
inside an agent's own directory, 31 minutes after the legitimate one at the workspace root.

Three consequences, in increasing severity:

1. **Litter.** A `.tmp/lr-state/` tree appears wherever a session's cwd happens to be.
2. **The TTL is defeated.** The 08:01 refresh should have suppressed the 08:32 one under the 16h
   window. It did not, because the second look-up used a different root and found no state. A TTL
   keyed to a path that moves is not a TTL.
3. **It escapes the gitignore.** The workspace-owned line is `/.tmp/` — **anchored to the workspace
   root**. A nested `.tmp/` inside a lore agent repo is not matched, so it shows as untracked and is
   exactly the kind of thing a directory-wide `git add` sweeps into a commit
   ([concurrent-session-committed-my-uncommitted-work.md](concurrent-session-committed-my-uncommitted-work.md)).

The design already resolves a session started inside `.worktrees/` back to the real workspace root.
That upward resolution is **not general**: from an arbitrary subdirectory it does not walk up to the
workspace root, so the worktree case reads as a special case rather than the rule.

**The fix belongs in the resolver, not the procedure.** Telling every call site to pass
`--workspace` is the wording-not-structure move that
[the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md)
warns about — `workspace_refresh` should resolve its state root by searching upward for the
workspace marker, the way `preflight --agent-dir` already searches upward for `role.md`, and refuse
to write state at all when no workspace root is found. Filed for the backlog.

Two smaller notes worth keeping: the anchored-gitignore gap is its own hazard independent of this
bug (`workspace-owned-default-ignore-lines.md`), and this is a second instance of the general lesson
that **a path-derived default is a proxy that fails exactly where the user's cwd is legitimate but
unusual** ([short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md)).
