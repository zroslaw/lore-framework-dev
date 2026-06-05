# Draft — Auto-commit + auto-push after boot-time version upgrade

**Status:** parked 2026-06-05. User pulled the brake mid-draft — "looks a bit complicated for now." Working changes to `docs/version-check.md` were reverted; this draft preserves the design so we can resume without rebuilding it.

## Motivating failure mode

A lore agent repo can end up locally upgraded (migrations applied, version stamped, committed) but **never pushed** — leaving the team unaware of the bump. Real instance: `activities-lore-agents` carrying unpushed `stamp version 13` and `stamp version 15` commits. Today's `version-check.md` Step 4 explicitly invariants "No commits — the user reviews and commits the upgraded files themselves," which made this orphan-commit state structurally possible at every unattended boot.

## Two-line proposal (user's framing)

1. Each lore-repo agent update (migration / version bump) should be followed by a `git push` so the upgraded state propagates to the team.
2. Only the changes made during the migration/upgrade itself should be committed and pushed — unrelated dirty files (other agents' `workdir/*` runtime state, scratch artifacts) must stay in place, untouched.

The write-set computed by Step 1b of `version-check.md` already gives an exact, declared scope (migration `## Write Paths` ∪ `lore-repo.md`) — so "only the upgrade's changes" has a ready-made boundary, not a heuristic.

## Designed flow (the version that was almost shipped)

Insert two new steps between today's Step 3 (Stamp the new version) and today's Step 4 (Inform the user):

### Step 4 — Commit the upgrade

```
git -C "<lore-agent-repo>" add -- <write-set globs> lore-repo.md
git -C "<lore-agent-repo>" commit -m "stamp version F"
```

- Stage **only** the write-set ∪ `lore-repo.md`. Never `git add -A` and never `git add .`. Untouched runtime state outside the write-set must be preserved both in the working tree and out of the commit.
- If `git commit` fails (missing identity config, pre-commit hook, etc.): warn with the exact failure, leave the tree as-is (changes uncommitted), continue boot in degraded mode. Do not attempt to push.

### Step 5 — Push the upgrade (best-effort)

```
git -C "<lore-agent-repo>" push --ff-only
```

`--ff-only` is load-bearing: refusal triggers reconciliation (5b), not failure.

#### 5a. Push succeeded

Print `<lore-agent-repo>: upgraded from R to F (committed and pushed)`. Continue boot.

#### 5b. Push rejected — remote moved during the upgrade (parallel-boot race)

Another process (typically a parallel-booting teammate) pushed an upgrade for the same version range while we ran ours. Reconcile by content equality:

1. `git -C "<lore-agent-repo>" fetch`
2. Read remote `lore-repo.md`'s `version` field on the upstream branch (`git show origin/<branch>:lore-repo.md`).
3. **If remote version == F AND remote write-set content matches our local commit byte-for-byte** (compare each write-set file via `git show origin/<branch>:<file>` against our committed version):
   - Drop our local commit and adopt the remote's versions of the write-set files **only**:
     ```
     git -C "<lore-agent-repo>" reset --soft HEAD~1                          # uncommit, keep working tree
     git -C "<lore-agent-repo>" checkout origin/<branch> -- <write-set globs> lore-repo.md
     ```
   - Critically: do NOT `git pull`, do NOT touch any file outside the write-set. The same scoping that applies to the commit applies here — unrelated dirty files (`workdir/*`) must be preserved.
   - Print `<lore-agent-repo>: upgraded from R to F (remote already at F — adopted remote's write-set, local commit dropped)`. Continue boot.
4. **If remote version != F or remote write-set content differs** (genuine divergence):
   - Do NOT auto-rebase, auto-merge, or force-push.
   - Print `<lore-agent-repo>: upgraded from R to F locally, but push was rejected and remote diverged — local commit retained for manual review.` Continue boot in degraded mode.

If `fetch` itself fails (transport): warn, retain local commit, continue boot.

### Step 6 — Inform the user

One-line outcome per the Step 5 result: pushed / remote-already-at-F / push-rejected-diverged / commit-failed / fetch-failed.

## Invariants the design must keep

- **Boot never fails on version errors** — every commit/push/fetch/reconciliation failure path lands in degraded-mode boot with a visible warning.
- **Commit scope = write-set ∪ `lore-repo.md`** — never `git add -A`. Untouched runtime state outside the write-set is preserved in both the working tree and the commit.
- **Push is `--ff-only`, never forced.**
- **Reconciliation is content-equality only** — Step 5b adopts the remote write-set only when remote version == F *and* remote content matches local commit byte-for-byte. Any divergence falls through to manual review — no automatic rebase or merge.
- **Same scoping applies to the reconciliation checkout** — `git checkout origin/<branch> -- <write-set>` only; never a full `git pull`.

## Why this composes with auto-pull (v13)

The auto-pull at Step 2 of `agent-boot.md` runs *before* version check. So the common case — remote already bumped before our boot — is already handled (pull brings R up to F, no upgrade fires). The race is genuine only when two agents both pulled before either committed; the `--ff-only` push then designates first-writer-wins, and 5b is how the loser reconciles cheaply (content equality → adopt and drop).

## Asymmetry with `/lr:update`

Two boot-only behaviors, both motivated by boot being **unattended**:

- The write-aware collision gate (Step 1) — already boot-only.
- The auto-commit + auto-push (Steps 4–5) — boot-only for the same reason. `/lr:update` is interactive; the user reviews the diff, commits, and pushes themselves on their own schedule.

(Bringing either behavior to `/lr:update` is a possible future enhancement — track both together when this resumes.)

## Open seams flagged before parking

1. **Branch detection** — the draft used `origin/<branch>` as a placeholder. Need a concrete resolution (`git rev-parse --abbrev-ref --symbolic-full-name @{u}` or similar) and a fallback if no upstream is configured.
2. **Migration deletions/renames** — `## Write Paths` grammar today is globs only. If a migration deletes a file, the deletion path needs to be in the write-set so `git add -- <path>` picks up the deletion. Worth auditing existing migrations and possibly extending the grammar / `/lr:check` #20 to validate deletion declarations.
3. **Identity / network failure** — boot must survive missing `user.email`/`user.name`, missing remote, no network. Folded into the warn-and-continue paths but worth a real-world test.
4. **Versioning/cache** — would ship as a `release-notes/<N>.md` (`docs/version-check.md` is runtime-affecting, so cache-clear footer applies); plugin manifest bump `1.<VERSION>.0`; backfill `versioning-release-types.md`.
5. **Multi-round multi-lens review** — procedural-doc change, mandatory.

## Why parked

User judgement: the design is correct directionally but the surface area (commit + push + fetch + reconciliation + divergence handling, all unattended at boot) is too much to ship right now next to the in-flight DF/ULA + AIQA work. Capture and revisit.

## See Also

- `framework-improvements-backlog.md` § Versioning / Boot Auto-Upgrade — the parked entry pointing here.
- `lore-framework/docs/version-check.md` — current boot-time upgrade procedure (the doc this design would have edited).
- `lore-framework/docs/auto-pull.md` — composes with the proposal (auto-pull defuses most of the race).
- `lore-framework/docs/conventions.md` § Migration Write Paths — the write-set grammar this design reuses.
- `dirty-tree-gates-write-vs-read-distinction.md` — the v15 write-set discipline this proposal extends from "gate" to "commit + push scope."
- `freshness-contracts-at-session-boundaries.md` — the principle the proposal embodies on the *push* side (mirror of auto-pull on the *pull* side).
- `auto-pull-mechanism.md` — transport-aware ladder is the model for graduated network-failure handling here.
