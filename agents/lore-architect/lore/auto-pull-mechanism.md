**Auto-pull (v13)** — boot, attach, and pre-merge automatically `git pull --ff-only` the agent's lore agent repo before reading lore. Plus a user-invoked `/lr:pull-lore` skill for mid-session force refresh of all active agents' repos.

The mechanism is the **freshness contract** for team-shared agent repos: whenever the host crosses a session-context boundary (boot, attach, the moment before merging reflections into lore), the local repo state must match the team's latest pushed state. Stale lore at merge time was the motivating failure — integrating reflections into days-old lore could re-introduce decisions the team already revised.

## Architecture

Single source of truth: `lore-framework/docs/auto-pull.md`. Four invocation sites delegate to it:

- `agent-boot.md` step 2 — host repo, before version check (so the version-check walk sees the freshest `lore-repo.md` stamp and any newly-pulled migrations)
- `attach.md` step 2 — guest repo, before version reconcile
- `process-merge.md` step 0 — defense-in-depth at the merge subagent (the boot pull already covers freshness; the explicit step makes the contract visible at the moment when stale lore is most damaging)
- `docs/pull-lore.md` (the `/lr:pull-lore` skill) — user-invoked, iterates auto-pull across active agents and re-reads their `role.md` and `lore-context.md`

## Per-Repo Procedure

`auto-pull.md` defines:

1. Skip cleanly if not a git repo or no `origin` remote (returns success — degraded mode).
2. `GIT_TERMINAL_PROMPT=0 git -C <repo> pull --ff-only` with a 60-second timeout.
3. Report per-site verbosity: boot/attach/merge are quiet on no-op (silent on `already up to date`, silent on skip); `/lr:pull-lore` is always verbose because user-invoked.

**No dirty-tree gate** — `--ff-only` is non-writing in spirit (advances `HEAD`, refuses if it would clobber working-tree edits). Different from `version-check.md`'s gate, which *does* refuse on dirty because version-check writes to `lore-repo.md`.

## Invariants

- **Best-effort.** Pull failures never block the surrounding flow; boot always completes.
- **No destructive actions.** No `--force`, no `git reset`, no `git checkout` away from the user's branch.
- **Uncommitted changes preserved.** `--ff-only` either advances cleanly or refuses with a clear error. Auto-pull never stashes.
- **Per-repo scope.** Multi-repo flows iterate; auto-pull itself is single-repo.
- **Idempotent.** Running twice on a clean repo produces no observable difference.

## /lr:pull-lore Specifics

`/lr:pull-lore` is the manual force-refresh:

1. Enumerates active agents (host + attached guests). Deduplicates shared repos.
2. Runs auto-pull per repo in parallel.
3. **Re-reads each active agent's `role.md` and `lore-context.md`** — essential, because the pull updated files on disk but Claude's working context still holds the pre-pull copies. Without the re-read, the new lore is on disk but not in working memory.
4. Reports verbose per-repo summary; flags material `role.md` / `lore-context.md` changes inline.

The "two-step" mental model (pull then re-read) is the discoverable surprise — captured prominently in `pull-lore.md`.

## Distinct From

- **`/lr:workspace-sync`** — workspace-wide: discovers `lore-repo.md` files, clones declared-but-missing repos, pulls every top-level git repo (including non-lore application repos). Auto-pull is single-repo and never clones. The two are explicit peers in their respective See Alsos.
- **`version-check.md`** — repo-version reconciliation: applies migrations and stamps `lore-repo.md` after a framework `VERSION` bump. Auto-pull is git-only and never modifies file contents. They run in sequence at boot — pull first so version-check sees freshest stamp.
- **`resolve-conflicts.md`** — finalize-time merge of remote conflicts in agent subtrees. Triggered only when push is rejected. Auto-pull is the *prevention* arm of the same problem.

The three sit on a spectrum: auto-pull keeps local repos fresh (so reads see current data); workspace-sync keeps the workspace fresh (so all repos are present); resolve-conflicts heals after a concurrent finalize collided.

## Worktrees

The framework's worktree convention keeps top-level checkouts on default branch. Auto-pull operates on whichever path was discovered by boot/attach:

- Top-level checkout: fast-forwards default branch as expected.
- Worktree on a feature branch: typically warns on non-fast-forward and degrades — feature-branch updates are managed manually.

Documented at `auto-pull.md` § Worktrees.

## Cache-affecting

v13 is release-notes-only + cache-affecting (new skill, modified SKILL.md-referenced docs). Release notes carry the Clear Plugin Cache footer hoisted near top, with the disambiguation phrasing per `cache-clear-footer-convention.md`.

## See Also

- `freshness-contracts-at-session-boundaries.md` — the underlying foundational principle that auto-pull operationalizes (boundary refreshes at boot/attach/pre-merge with `/lr:pull-lore` for the in-between case)
- `dirty-tree-gates-write-vs-read-distinction.md` — companion principle explaining why auto-pull deliberately has *no* dirty-tree gate (it's a read; the gate would be friction without safety)
- `shared-procedure-doc-pattern.md` — `docs/auto-pull.md` is the canonical example: one procedure, four call sites, audience-note banner, no `/lr:auto-pull` skill
- `versioning-release-types.md` — v13 history entry
- `workspace-sync-utility.md` — the workspace-wide peer
- `reflect-merge-execution-asymmetry.md` — the merge subagent boots → boot's auto-pull covers freshness; the explicit step 0 in process-merge is defense-in-depth, not redundancy
- `cache-clear-footer-convention.md` — applied here in release-notes/13.md
- `team-shared-knowledge-principle.md` — the underlying motivation: shared agent repos accumulate team knowledge; staleness is the failure mode auto-pull prevents
- `tooling-cwd-safety.md` — companion topic on `git -C` discipline (the auto-pull procedure follows this throughout)
