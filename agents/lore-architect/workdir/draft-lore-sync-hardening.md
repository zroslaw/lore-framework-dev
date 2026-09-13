# Draft — Lore Sync Hardening (v46)

**Status:** design, revised after **three** review rounds (3, then 4, then 3 cold lenses) — the
loop's hard ceiling. Round 3 closed with one BLOCK, applied. **Not converged**: the round-3 fixes
are themselves unreviewed, and the ceiling stopped the loop rather than a clean round.
**Author:** lore-architect, 2026-09-13
**Layer:** plugin (all changes live in `lore-framework/`)
**Type:** release-notes-only, **cache-affecting** (touches `scripts/` and SKILL.md-referenced docs)

---

## 1. Problem

Lore agent repos accumulate local commits that are never pushed. Nothing in the framework
detects, reports, or recovers from that. Once a repo diverges, every subsequent boot's
`git pull --ff-only` fails permanently, the agent loads stale lore in degraded mode, and the
health command cannot see it.

### 1.1 Verified git behaviour

`git pull --ff-only` is already file-granular. Dirty tracked files and untracked files at
unrelated paths do **not** block it. Exactly three states block a pull:

| # | Blocking state | Frequency |
|---|---|---|
| 1 | Local unpushed commit **and** remote advanced → `fatal: Not possible to fast-forward` | common; **never self-heals** |
| 2 | Locally modified tracked file that an incoming commit also changes | common (almost always `lore-context.md`) |
| 3 | Untracked file at a path an incoming commit creates | rare |

Push side:

| # | Blocking state | Frequency |
|---|---|---|
| 4 | Remote moved since session start → push rejected | common under concurrency |
| 5 | `git add agents/` sweeps a concurrent session's in-progress edits into an unrelated commit | every finalize under concurrency |

Case 4 manufactures case 1: `resolve-conflicts.md` retries three times, then gives up, leaving
a local commit behind. `/lr:update` manufactures it too — its push gate refuses when the branch
is already ahead, leaving the update commit local.

### 1.2 Supporting defects

- `repo_scan.py` computes no ahead/behind for agent repos. Case 1 is invisible to `/lr:check`.
- `workspace_refresh.py:needs_refresh` keys on `last-attempt`, not `last-success`. A refresh that
  fails still resets the 16h clock.
- `scripts/workspace-pull` Phase 0 skips the workspace-root pull whenever **any** tracked file is
  dirty. This contradicts the correct rule stated 30 lines away in
  `workspace_refresh.py:_blocked_repos` ("dirty alone does not mean blocked"), and guarantees
  staleness for exactly the heavy users whose trees are always dirty.
- `git pull --ff-only --autostash` on a real content collision **exits 0**, reports success, and
  leaves conflict markers in a `UU` working tree. It must never enter this codebase.

### 1.3 Relationship to existing framework patterns

Two existing procedures already implement **narrow pathspec staging → pathspec commit →
post-commit path verification → undo on mismatch**: `docs/update.md` § Automatic Publication and
`docs/workspace-push.md` Step 4. They apply it to the framework's two rarest operations. The most
frequent write path, `/lr:finalize` Phase 4, has none of it.

**Steps 1–3 of this design generalize that existing pattern. Step 4 does not — it is new.**

Both precedents deliberately refuse to merge on rejection. `workspace-push.md` § Failure handling
says verbatim: *"Do not force, do not merge automatically: report it and suggest
`/lr:workspace-pull`."* `update.md` leaves the commit and a marker local. Neither contains a
fetch-and-merge retry loop.

That refusal is correct **for those two callers** and wrong for finalize:

- `workspace-push.md` operates on the *workspace* repo, whose managed files are configuration a
  human is confirming through an approval gate. Automatic merging there would reconcile a user's
  config edits without asking. It keeps its own no-merge policy and its own failure handling (C3b).
- `update.md` runs at boot, where latency matters and where the executor must not be making
  content judgments about lore (see C3, boot-time mode).
- `/lr:finalize` is an explicit end-of-session publish of content the session itself authored, with
  the session context needed to reconcile it present. Merge-retry belongs here and only here.

An implementer looking to the precedents for the shape of the merge step will find its opposite.
That is intentional and is recorded here so it is not read as an oversight.

---

## 2. Invariants

Five rules. Everything below is an application of one of them.

- **I1 — No framework operation may leave a lore repo with a local commit that is not on the
  remote, without saying so loudly.** A stranded commit is a permanent boot-pull failure; it may be
  an accepted outcome, never a silent one.
- **I2 — Every framework commit names its paths.** Never `git add <directory>`, never a bare
  `git commit`. A commit must contain only what this operation authored.
- **I3 — Never resolve a conflict by discarding.** No `--autostash`, no `--force`, no `reset --hard`,
  no `stash` in any automatic path. A refusal is a safe outcome; a silent overwrite is not.
- **I4 — Never content-judge a file this operation did not author.** Automatic conflict resolution
  is permitted only on a path that is simultaneously (a) in the operation's recorded write-set,
  (b) within `resolve-conflicts.md` § Scope, and (c) owned by an agent an executor is booted as.
  Everything else stops for a human.
- **I5 — A publication blocked by another party never leaves the repo further ahead than it found
  it.** "Blocked by another party" means a Foreign conflicted path or a merge refused by a
  concurrent session's dirty tree — the recurring conditions. Transient failures (network, auth,
  timeout, no upstream) are excluded on purpose: they keep the commit, because the same commit is
  what a later plain `git push` publishes, and waiting work accumulating is not a ratchet. See
  § 4 Step 5b.

I4 and I5 are separate from I3 on purpose. I3 bars an unsafe *mechanism* (discarding data); I4 bars
unsafe *authority* (judging content you do not own); I5 bars an unsafe *aftermath*. Collapsing them
reads shorter and makes each one less checkable at its point of use — and it was I4's separate
naming that made the first round's blocker findable at all.

---

## 3. Scope

**Ten changes**, counting C3a/C3b as their own rows. **C1, C2, C3 and C3a are the cure; C4 and C8
are the visibility; C5, C6 and C7 are correctness fixes that stand alone; C3b is documentation
only.** No new script, no new CLI subcommand, no data-model change, no migration.

| ID | Change | Kills |
|---|---|---|
| C1 | New shared procedure doc `docs/publish-lore.md` | — (single canonical source for C2/C3/C3b) |
| C2 | `finalize.md` Phase 4 → narrow staging + verify + merge-retry-push | 5, 4, 1 |
| C3 | `update.md` publication routed through the same doc, in no-merge mode | 1 |
| C3a | `resolve-conflicts.md` retargeted to content reconciliation; Scope widened | — |
| C3b | `workspace-push.md` gains one cross-reference line (no rewiring) | — (documentation only) |
| C4 | New `/lr:check` finding R16 — agent repo ahead/diverged | 1 (visibility) |
| C5 | `workspace_refresh.py` TTL keys on `last-success` | blind 16h window |
| C6 | `workspace-pull` Phase 0 attempts the pull instead of pre-refusing | false staleness |
| C7 | `conventions.md` — new § Tooling: Git Safety | silent corruption |
| C8 | `lrb status` surfaces a being whose agent repo carries a stranded-publish marker | **silent failure under the unattended daemon** |

### Deliberately out of scope

- **Sidecar publish via git plumbing.** `git commit -- <paths>` already builds a temporary index
  internally; that was the only property the plumbing bought. Rejected on maintenance cost and on
  the verified finding that it leaves the working tree permanently unable to pull.
- **Generated `lore-context.md`.** Only an LLM can author it (`conventions.md` § Lore Context,
  `process-merge.md` Step 4), so regenerating it does not remove the collision. Separate design.
- **Unique/append-only lore topic filenames.** Genuinely good and independent; addresses cases 2
  and 3, the two rarest. Separate design, separate ship.
- **Dropping automatic conflict resolution entirely.** A design that narrowed staging (I2) and
  retried the push, but stopped loudly on *any* conflict — Ours or Foreign alike — would need no
  `<mode>` parameter, no ownership test, and no two-class table, and the ratchet could not arise
  because a blocked merge would always abort before any commit existed. Genuinely simpler, and
  raised as such in round 3. **Rejected on what it costs the common case:** the automatic
  reconciliation it removes is `resolve-conflicts.md`'s existing behavior, and the file it most
  often reconciles is `lore-context.md` — which every finalization rewrites, making it the single
  most frequent collision in the system. Trading a routine automatic merge for a manual stop every
  time two sessions run the same agent makes the user's commonest day worse, not better. The
  simplification is real; the trade is bad. Recorded so the decision is visible rather than
  implicit.
- **Reading authoritative lore from `origin/<branch>`.** Promising reframing — dissolves cases 1–3
  as *read* problems — but changes what boot sees (it would stop seeing uncommitted local lore).
  Needs its own design.

---

## 4. C1 — `docs/publish-lore.md` (new shared procedure doc)

Follows the shared-procedure-doc pattern: a non-skill procedure used by more than one call site, so
it gets its own doc and every caller points at it rather than restating it.

**Audience note:** internal procedure doc. There is no `/lr:publish-lore` skill.

### Inputs

- `<repo>` — absolute path. Must be its own git root.
- `<paths>` — the **write-set**: repo-relative paths this operation authored. Explicit list, never
  a directory, never a glob. This list is also the authority for conflict classification in Step 4,
  so it must be recorded, not recomputed later from git state.
- `<message>` — commit subject.
- `<mode>` — `merge-retry` or `no-merge`. Callers that must not perform content judgment or must not
  block on network round-trips pass `no-merge` (see C3).
- `<owner-agent>` — **the agent this executor session is booted as**, or `none` for workspace-level
  callers. It is a fact about the executor, never a per-call selection: finalize commits the host
  and any co-resident guests into one commit per repo (`finalize.md` § Cross-repo guests), and in
  this workspace `lore-agents` holds eleven agents in one repo, so one call's write-set routinely
  spans several agents' subtrees. Asking the caller to name "the" owner would have no answer.
  Paths belonging to any *other* agent simply fail the I4 ownership test and are handled by
  Step 4a's escalation, which is the correct outcome.

### Preconditions (check in order; each failure stops with a named reason, never a guess)

1. `git -C "<repo>" rev-parse --show-toplevel` equals `<repo>`'s real path. Otherwise stop:
   `not its own git root`. (Same guard as `preflight.py:git_toplevel`; `git -C` silently walks up.)
2. `BRANCH=$(git -C "<repo>" rev-parse --abbrev-ref HEAD)`. If `HEAD`, stop: `detached HEAD`.
   **Use this resolved branch explicitly everywhere below** — never infer from `@{u}` alone, because
   a worktree under `.worktrees/<repo>/<slug>/` is on a feature branch and inferring would publish
   lore there.
3. **No merge, rebase, or cherry-pick may be in progress.**
   `git -C "<repo>" rev-parse -q --verify MERGE_HEAD` must print nothing. If it prints a sha, stop
   with `merge in progress` and tell the user to finish it (`git -C "<repo>" commit --no-edit`) or
   abandon it (`git -C "<repo>" merge --abort`).

   **This precondition is load-bearing, not hygiene.** Verified: a pathspec commit inside an
   unfinished merge fails with `fatal: cannot do a partial commit during a merge.`, exit 128, with
   `HEAD` unchanged — which is indistinguishable from a genuine no-op by exit code alone. A session
   killed mid-Step-4a leaves `MERGE_HEAD` behind, and without this check every later publication on
   that repo would report success and write nothing, forever. No commit is ever created, so R16's
   ahead-count cannot see it either. Check the same for `REBASE_HEAD` and `CHERRY_PICK_HEAD`.
4. `git -C "<repo>" rev-parse --abbrev-ref --symbolic-full-name @{u}`. If absent, the commit is
   still performed; push is skipped with reason `no upstream`.
5. Nothing else to record. An earlier draft captured a pre-operation ahead-count to condition the
   rollback on; that condition was wrong (see Step 5b) and the value is no longer needed. The
   ahead-count for the report is read at Step 5c, when it is actually used.

### Procedure

**Step 1 — Stage the write-set, deletion-aware.**

```bash
git -C "<repo>" add -A -- <paths>
```

`-A` with an explicit pathspec covers creation, modification and deletion. Never a bare `-A`.

**Step 2 — Commit the same explicit paths.**

```bash
git -C "<repo>" commit -m "<message>" -- <paths>
```

A pathspec commit ignores the index for every path it does not name, so a concurrent session's
*staged* work stays staged and uncommitted.

> **Narrowed, not closed.** A pathspec commit takes each named path's **current working-tree
> content**, not the version Step 1 staged. If another session rewrites one of these same files
> between Step 1 and Step 2, that newer content lands. Publishing a lore file's current state is
> intended; what the pathspec rules out is committing somebody else's *unrelated* file. This is the
> same caveat `workspace-push.md` Step 4 already records.

**Detecting "nothing to publish": decide it from what Step 1 staged, before committing.**

```bash
git -C "<repo>" diff --cached --name-only -- <paths>
```

Empty → there was nothing to publish. Stop with `nothing to publish`; that is a success.
Non-empty → a commit **must** result. If the commit then fails for any reason, that is a hard
failure: report git's error line and stop. Never call it `nothing to publish`.

Do not decide this from git's message text, and do not decide it from "non-zero exit with `HEAD`
unchanged". Message text is not stable — git prints `nothing to commit` on a clean tree,
`no changes added to commit` when a tracked file is dirty elsewhere, and
`nothing added to commit but untracked files present` when the collision is an untracked file.
And exit-code-plus-unchanged-`HEAD` is exactly the signature of the blocked-merge fatal that
precondition 3 exists to catch, so using it would re-open that hole from the other side.

**Step 3 — Verify the commit.**

```bash
git -C "<repo>" show --name-only --format= HEAD
```

Every path must be in `<paths>`. If any is not:

```bash
git -C "<repo>" reset --soft HEAD^
```

then report the unexpected paths and stop. Do not push. Leaving a commit you have just declared
wrong on the branch is not a safe stopping point — the next push carries it.

**Step 4 — Push.**

Attempt the push:

```bash
git -C "<repo>" push                       # or: push -u origin HEAD when origin exists, no upstream
```

- **Success** → done. Report `✓ <repo>: committed <sha>, pushed to <branch>`. **If Step 4a merged
  first, say so in the same line** — `…, merged <n> incoming commit(s) first`. An automatic merge
  changes the shape of the user's history; they must not discover it later in `git log` with no
  record of why.
- **Rejected (non-fast-forward)**:
  - In `no-merge` mode → stop and go to Step 5. Do not fetch, do not merge.
  - In `merge-retry` mode → go to Step 4a. Up to **3** push attempts in total.
- **Rejected for another reason** (auth, remote unreachable, timeout) → stop, Step 5.
- **`fatal: Unable to create '.git/index.lock': File exists`** at any point in Steps 1–4 → another
  process is mid-`add` or mid-`commit` in this repo: a second session, another skill, or the
  unattended daemon. **Do not delete the lock file** — it is usually held by a live process, and
  removing it corrupts that run's index write. Stop and report it; do not poll, do not wait in a
  loop. Re-running is the caller's decision and must restart from Step 1, because what is dirty has
  changed. In an unattended session, stopping with the lock reported is the correct end state.

**Step 4a — Reconcile (merge-retry mode only).**

```bash
git -C "<repo>" fetch origin
git -C "<repo>" merge "origin/${BRANCH}" --no-edit
```

- **Merge clean** → retry the push.
- **Merge refuses** (`Your local changes to the following files would be overwritten by merge`) →
  a **concurrent session's** dirty files collide with the incoming commits.
  `git -C "<repo>" merge --abort`, stop, Step 5.
- **Merge fails irrecoverably** (divergent history from a force-push, network loss, merge-config
  error) → `git -C "<repo>" merge --abort`, stop, Step 5.
- **Merge reports conflicts** → classify before resolving anything. List them:

  ```bash
  git -C "<repo>" diff --name-only --diff-filter=U
  ```

  Partition the conflicted paths into **two** classes:

  | Class | Condition | Action |
  |---|---|---|
  | **Ours** | in `<paths>` **and** under `agents/<name>/{lore/**, lore-context.md, role.md}` for some agent `<name>` | Resolve per `resolve-conflicts.md` § Resolve conflicted files — inline when `<name>` is `<owner-agent>`, otherwise via a subagent booted as `<name>`. `git add -- <those paths>` as each is resolved. |
  | **Foreign** | everything else | **Never resolve automatically** (I4). Go to Step 5. |

  The Ours condition is the three-way intersection I4 states: in the write-set, inside
  `resolve-conflicts.md` § Scope, and agent-owned. All three clauses are load-bearing:

  - **Write-set** — I1 permits a stranded commit to persist, and its files enter this merge while
    sitting outside the current operation's write-set. Verified: with a prior stranded commit
    touching `other.md` and a current commit touching only `topic.md`, `git merge origin/main`
    conflicts on `other.md`. Narrow staging constrains *this* commit, not commits already on the
    branch.
  - **Scope** — `resolve-conflicts.md` § Resolve conflicted files gives judgment rules for lore
    topics, `lore-context.md` and `role.md` and for nothing else. A conflicted
    `agents/<name>/reflections/**` path or a `sessions/**` summary is in the finalize write-set and
    agent-owned, yet has no resolution rule; so is `lore-repo.md` in the update write-set. All are
    Foreign. For `/lr:update` that is narrow in practice — both sides stamp the same version `F`,
    so git takes the identical change without conflict; a genuine `lore-repo.md` conflict means the
    two sides disagree about the version, which warrants a human.
  - **Ownership** — one repo can hold many agents' subtrees, so a conflicted path may belong to an
    agent this executor has no domain context for. Inline versus subagent is an execution detail of
    the same rule, not a third class. If a subagent cannot be spawned, or the owning agent is not
    resolvable in this workspace, the path is Foreign.

  When every conflicted path is Ours and resolved: `git -C "<repo>" commit --no-edit`, then retry
  the push.

**Step 5 — Unpublished-work handling (I1, I5).**

Step 4 ended without a successful push. Do three things, in this order.

**5a — Abort any in-progress merge, and know what it costs.** `git -C "<repo>" merge --abort`.
Verified: this restores the working tree to its pre-merge content and exits 0 — including
**reverting any Ours-class resolution already staged in this attempt**. No data is corrupted and
nothing on disk before the merge is lost, but in-flight resolution work is discarded and a later
retry redoes it from scratch. Say so rather than implying resolution was banked.

**5b — Decide whether to keep this operation's own commit (I5).** Classify the failure:

| Failure | Keep the commit? |
|---|---|
| Network, auth, timeout, remote unreachable, no upstream | **Keep.** A later retry succeeds unchanged, and the commit is durable. |
| Foreign conflicted path, or `merge` refused by a third party's dirty tree | **Always roll back** with `git -C "<repo>" reset --soft HEAD^`. No exceptions. |

Rolling back matters because the blocking cases **ratchet**. Steps 1–3 already created a commit
before Step 4a ran; if that commit survives every blocked attempt, each finalize adds another
stranded commit rather than clearing one, and a single foreign file blocks every agent sharing the
repo from ever publishing. No retry count fixes a ratchet. `reset --soft` restores exactly the
pre-Step-1 state with the content staged, so nothing is lost — the lore files stay on disk and the
next publication picks them up.

**The rollback is unconditional, and an earlier draft's "unless the repo was already ahead"
exception is withdrawn.** That exception was wrong on its own terms: `reset --soft HEAD^` removes
only the single most recent commit and cannot touch commits that were already ahead, so skipping it
in that case protected nothing and produced exactly the ratchet — `ahead` growing by one on every
repeat of the same block, in the one scenario where the block is most likely to repeat. All three
round-3 lenses caught this independently.

**5c — Record *why*, then report it.**

Prose alone is not enough: an unattended Being session prints to a log nobody parses, and its run is
recorded `is_error: false` — a clean run — so `lrb status` stays green while the repo rots.

**The marker is a hint, never a verdict.** Git already proves whether a repo is unpublishable —
`ahead > 0`, or a leftover `MERGE_HEAD`. The marker only annotates *why* and, through its own mtime,
*for how long*. Every consumer must revalidate against git and treat a marker whose condition git no
longer shows as **stale**: report nothing and delete it. Without that rule, a repo a human fixes by
hand reports a fault forever — re-creating the cry-wolf failure this design elsewhere forbids.

Write it at `git -C "<repo>" rev-parse --git-common-dir` (never committed):

```yaml
version: 1
branch: "<branch>"
reason: "<foreign-conflict | merge-blocked | network | auth | no-upstream | other>"
blocking_paths: ["<path>", ...]   # the Foreign or blocking paths; omit when not applicable
```

Four rules govern it, and they are the whole contract:

1. **`--git-common-dir`, not `--absolute-git-dir`.** Verified: in a linked worktree the latter
   resolves to `<repo>/.git/worktrees/<slug>`, a private path neither C4 nor C8 looks at, so a
   stranded publish from `.worktrees/<repo>/<slug>/` would be invisible to both. The common dir is
   shared by every checkout. (`preflight.py`'s `lr-last-pull` stamp deliberately uses the absolute
   git dir, because a pull stamp *is* per-checkout. A repo-wide fault marker is not.)
2. **No counters, no timestamps in the file.** Age comes from the file's own mtime. Write the file
   only when there is no marker, or when `reason` changes; otherwise leave it alone and let mtime
   stand for "first seen". This removes a read-modify-write that two concurrent publications — a
   session and the daemon — could interleave and lose, and it removes bookkeeping whose only
   consumer was a v46 decision this spec explicitly defers (§ 13.4). Write atomically: temp file
   plus `os.replace`, the pattern `workspace_refresh.py:write_state` already uses.
3. **Stale, malformed, or foreign markers are ignored and deleted.** Unparseable YAML, a `version`
   this reader does not know, a `branch` that is not the current branch, or a repo git shows as
   clean — all mean "no useful information here". Report nothing, delete the file. This follows the
   framework's established convention for its own state files: `needs_refresh` self-heals every
   malformed case, and `update.md` refuses a marker whose recorded facts no longer match git.
4. **One canonical reader.** Add a single `read_stranded_marker(repo)` to `scripts/lr_core/common.py`
   that applies rules 1 and 3 and returns a dict or `None`. C4 and C8 both call it; neither parses
   the file itself. Two independent parsers in two languages drifting apart is exactly the coupling
   the framework avoids elsewhere by centralizing.

Remove the marker on the next successful publication to this repo, and — per rule 3 — whenever any
consumer finds it stale.

Then compose the report **here, at the point of failure** — not a paraphrase, and never omitting the
consequence sentence:

```
<repo>: could NOT publish — <reason>.
<kept|rolled back> this session's commit; the lore files remain on disk.
This repo is ahead of its remote by <n> commit(s). Until it is resolved, every agent boot
from this repo will fail to pull and will load stale lore in degraded mode.
```

Read `<n>` here with `git -C "<repo>" rev-list --count @{u}..HEAD`, after the rollback decision in
5b — it must describe the state the user is actually left in. When `<n>` is 0 (a clean repo whose
publication was rolled back), drop the last two lines: there is nothing stranded, the work is simply
unpublished and waiting on disk.

Then a remedy **matched to the reason** — the generic one is wrong for the commonest case:

- **network / auth / no-upstream** —
  `git -C "<repo>" push` once connectivity or credentials are restored.
- **merge-blocked** (a third party's dirty tree) — name the blocking paths; the other session must
  commit or revert them, then re-run finalize.
- **foreign-conflict** — **do not** offer `git merge && git push`. Those commands re-hit the same
  content conflict and drop the user into a `UU` working tree holding lore they may not own, with
  less context than the framework had when it refused. Say instead: the conflicting paths are
  `<blocking_paths>`, owned by `<agent(s)>`; they came from commit(s) `<git log --oneline @{u}..HEAD>`;
  reconcile them by booting that agent (`/lr:boot <agent>`) and resolving there, or resolve them by
  hand, then push.

A stranded commit reported as a bare "push failed" is what produced the situation this design
exists to fix. The consequence sentence and the matched remedy are the deliverable.

### Invariants

- Never `--force`, never `--autostash`, never `stash`, never `reset --hard`, never `checkout` away
  from the user's branch (I3).
- Never stage or commit a path outside `<paths>` (I2).
- Never content-judge a path outside `<paths>`, or outside the executor's own agent subtree (I4).
- The retry cap is hard at 3. Git's ref update is compare-and-swap, so the loop cannot corrupt —
  but it must not spin.
- A failure here never rolls back a completed merge or migration; the lore files stay on disk.
  **In-flight conflict resolution is not preserved** — Step 5a's `merge --abort` discards it, by
  design and verified. Only content written before this publication began is durable.
- No path is content-judged unless it satisfies all three Ours clauses (I4).
- A blocked publication never leaves the repo further ahead than it found it (I5, Step 5b).

### Known residual

A merge blocked by a **third party's** dirty working tree, or by Foreign conflicted paths, stops the
publication. It is loud (Step 5c), durable as state (the marker), visible (C4), surfaced to the
daemon (C8), and — because Step 5b rolls this operation's commit back — it does not deepen. It
clears at the next publication once the blocking side commits or the foreign conflict is
reconciled. **It is not self-healing on its own**, and the earlier draft's claim that it was is
withdrawn: under sustained concurrency the blocking condition can persist indefinitely, which is
why the marker records the reason durably and why C8 exists. If real use shows this recurring, the documented next step is to perform the merge
in the object database with `git merge-tree --write-tree` (git ≥ 2.38) and push the resulting
commit without touching the working tree — a strictly additive extension to Step 4a that needs no
change to any caller.

### Fallback

This doc is plain prose executed by the model; there is no accelerator script, so the Script
Fallback Contract does not apply. If it is later scripted, this doc becomes the literate spec.

---

## 5. C2 — `finalize.md` Phase 4

### Current (docs/finalize.md, § Phase 4)

```
1. `git -C <repo> add agents/`
2. `git -C <repo> commit -m "Finalize session <short-uuid>"`
3. `git -C <repo> push`
```

### New

Replace steps 1–3 with: **compute the write-set, then follow `<framework-root>/docs/publish-lore.md`
for each touched repo**, with `<mode>` = `merge-retry` and `<owner-agent>` = the agent whose
subtree is being published.

**Computing the write-set.** It already flows to the host; almost nothing new is collected:

- Every path named under **Lore changes** in each active agent's Phase 2 merge handoff
  (`process-merge.md` handoff template) — agent-relative, so prefix with `agents/<agent-name>/`.
  The handoff already names created, updated, consolidated, simplified and **deleted** files.
- **Reflection files actually deleted by merge Step 6.** This requires a small addition to the
  handoff template (below) — do **not** derive it from "what Phase 1 produced." Merge Step 6 deletes
  a topic *only after its knowledge was successfully integrated* and explicitly leaves blocked or
  failed topics in place, and it may also delete **carried-over** topics from an earlier run that
  Phase 1 never listed. Deriving the set from Phase 1 both misses carried-over deletions and risks
  staging a failed topic this session did not integrate.
- The summary path(s) written in Phase 3, host and per-guest.

**Required change to `process-merge.md` Step 6 handoff template.** Add one field, with an explicit
`None.` value rather than omission, matching the template's existing convention:

```text
- Reflections removed: <agent-relative paths deleted in Step 6, current-session or carried-over; or None.>
```

Without it the host has no explicit-path source for a deletion, I2 forbids a directory pathspec, and
the file stays deleted-on-disk but tracked-and-dirty in git indefinitely.

If a merge handoff is missing or malformed for an agent, **do not fall back to `git add agents/`.**
Report that agent's repo as unpublished with the reason, and publish the others. An unverifiable
write-set is a stop, not a licence to widen the commit.

### Failure-handling section — rewrite

The current text says "the commit is already made locally" and offers manual retry. Update it to:

- **Push rejected** → handled inside `publish-lore.md` Step 4a; no longer a separate branch here.
- **Conflicts** → classified by `publish-lore.md` Step 4a into Ours and Foreign. Ours resolves —
  inline for this agent's paths, via a subagent booted as the owner for a co-resident guest's.
  Foreign stops, and Step 5b rolls this operation's commit back so the repo is no worse off.
- **Push impossible** → the stranded-commit report (`publish-lore.md` Step 5), verbatim.
- **Any merge subagent failed** → unchanged: do not publish that repo.
- **Summarize failed** → unchanged: publish reflect+merge output alone.

### Invariants section

Add: **Nothing this session did not author enters the commit.**

---

## 6. C3 — `update.md` § Automatic Publication

### The defect

> "attempt a push only when the branch has an existing upstream and it had **zero commits ahead**
> of that upstream before this update. Otherwise keep the new update commit local"

When the branch is already ahead — precisely the diverged state — this refuses to push and **adds
another** stranded commit. The gate's intent is right (never let unrelated local work ride along on
an automatic push); its remedy makes the disease worse.

### The fix

Route the push through `publish-lore.md` Step 4 with `<mode>` = **`no-merge`** and
`<owner-agent>` = `none`.

`no-merge` is deliberate and is the whole reason the mode parameter exists:

- This path also runs from **boot** (`version-check.md` Step 4 delegates here). Boot is the most
  latency-sensitive path in the framework; it must not acquire a synchronous fetch-merge-retry loop.
- Boot must not make **content judgments about lore** it has not loaded yet. I4 forbids it anyway,
  since `<owner-agent>` is `none` here and the update write-set contains no agent-owned lore.

So when the branch is already ahead: still commit (Steps 1–3 are unchanged and their verification
is what the zero-ahead gate was protecting by proxy), attempt one push, and on rejection emit the
Step 5 stranded-commit report — which additionally names the pre-existing commits via
`git -C "<repo>" log --oneline @{u}..HEAD` and states that the repo was already ahead *before* this
update. The ahead state is then resolved by the user, or by the next `/lr:finalize` on that repo,
which runs in `merge-retry` mode.

Keep unchanged: the write-set ∩ dirty-set deferral (§§ 1b/1c), narrow staging, the commit gate's
other three conditions, and the fresh precondition re-resolution immediately before push.

### C3 — the `lr-update-pending` marker

`update.md` writes an `lr-update-pending` marker (`version`, `commit`, `branch`, `upstream`) into
the absolute git dir immediately before pushing, removes it only on success, and on a later
`/lr:update` retries **only when `HEAD` equals the recorded commit and that commit is the sole
commit ahead**. This interaction must be stated explicitly or an implementer will drop it, because
`publish-lore.md` Step 4 reads as a complete push procedure with no marker step to slot into.

Specify in `update.md`:

- The marker is written **by `update.md`**, immediately before invoking `publish-lore.md` Step 4 —
  not by `publish-lore.md`, which knows nothing about updates.
- It is removed by `update.md` on a `pushed` result, and left in place on any other result.
- `no-merge` mode is what keeps the marker's retry contract valid: because no merge commit is ever
  created, `HEAD` still equals the recorded commit and the sole-commit-ahead test still means what
  it meant. **This is a second, independent reason the update path must not use `merge-retry`** —
  a merge-retry loop would move `HEAD`, permanently staling every marker and silently disabling
  automatic retry.

### C3a — `resolve-conflicts.md`

Four edits, in this order:

1. **Retarget the trigger sentence** from "push rejection" to "two versions of the same lore file
   must be reconciled, as classified by `publish-lore.md` Step 4a."
2. **Fix `git add agents/<your-name>/` in Step 4 to explicit conflicted paths** (I2). Do this
   *before* edit 3, which deletes the step containing it — otherwise the fix silently no-ops and a
   directory-add instruction survives in git history for a later half-revert to resurrect.
3. **Delete Step 1** (fetch/merge), **Step 4** (commit/push) and **Step 5** (retry) — now owned by
   `publish-lore.md` Step 4/4a. Step 2's content-judgment rules and Step 3's knowledge-graph check
   are the valuable part and stay.
4. **Widen § Scope explicitly.** It currently handles only `agents/<name>/{lore/**, lore-context.md,
   role.md}` and refuses `sessions/`, `lore-repo.md` and anything outside an agent directory. Keep
   that refusal — `publish-lore.md` Step 4a classifies those as Foreign — but state the mapping, so
   the two docs cannot drift: **the handled set is the intersection of this Scope with the caller's
   write-set; everything else is Foreign and stops for a human.**

Keep the § Execution model note. The default is now inline host resolution for own-agent conflicts;
the per-agent subagent fan-out remains for the other-agent class and is no longer optional there —
I4 requires it.

### C3b — `workspace-push.md` (cross-reference only)

`workspace-push.md` Step 4 already implements Steps 1–3 correctly and independently, including the
`index.lock` handling `publish-lore.md` adopted from it. Rewiring a working, invariant-compliant
procedure to delegate into a new doc is churn against zero behavior change, and the risk of
half-migrated prose is real.

**So: do not rewire it.** Add one line to `workspace-push.md` Step 4 naming `publish-lore.md`
Steps 1–3 as the canonical statement of the stage/commit/verify pattern, and one line to
`publish-lore.md` § Invariants noting that `workspace-push.md` is a deliberate `no-merge` caller
that keeps its own failure handling, because the workspace repo carries configuration a human is
confirming through an approval gate. That satisfies the single-canonical-source rule — which asks
for one canonical site and pointers elsewhere, not for one implementation — at the cost of two
sentences.

---

## 7. C4 — new finding R16 (agent repo ahead / diverged)

### Why

Case 1 is the only permanent failure and it is currently invisible. Detection is independently
valuable: it is the evidence that tells us, after a few weeks, whether C1–C3 actually worked, and
whether the § 4 Known residual occurs often enough to justify the `merge-tree` extension.

### Implementation — `scripts/lr_core/repo_scan.py`, `scan_repos()`

Inside the `for child in children:` loop, in the existing `if own_git:` block (which already
computes `dirty`), add — **no network**, `@{u}` reads the last-fetched ref:

```python
rc, out, _ = git(str(repo), ["rev-list", "--left-right", "--count", "@{u}...HEAD"], timeout=5)
if git_answered(rc) and rc == 0:
    parts = out.split()
    if len(parts) == 2 and all(p.isdigit() for p in parts):
        behind, ahead = int(parts[0]), int(parts[1])
        if ahead:
            findings.append(finding("R16", "warn", "repos", "sync",
                                    repo=info["name"], ahead=ahead, behind=behind,
                                    diverged=bool(behind)))
```

**Tier C only — skip the next two paragraphs when implementing C4 in bare form (§ 14a):** the
`read_stranded_marker` call below, and the *"The marker never fires R16 on its own"* paragraph
after it. The marker does not exist in Tier A. **Resume at *Anything else*, which does apply** —
its no-upstream suppression is generic and must survive into bare form, or every local-only repo
raises a false R16.

Then call `read_stranded_marker(repo)` (§ 4 Step 5c rule 4) and attach its result to the finding as
`marker` when it returns one. The marker, not the commit count, is what turns R16 from "you have
unpushed commits" into "publication has been failing for six days, because of this." Its age is the
file's mtime.

**The marker never fires R16 on its own.** It annotates a fault git independently shows; it does not
assert one. A marker found beside a repo git reports as clean is stale by definition — the reader
deletes it and says nothing. This is what stops a repo the user fixed by hand from reporting a fault
forever.

Anything else — no upstream, `git` cannot answer — adds no finding. Absence of a remote is a
legitimate state (`pull_repo` already treats it as `skipped`); it must not become a warning.

**Transient suppression.** `ahead > 0` is briefly true for a healthy repo between Step 2's commit
and Step 4's push. With no marker present and `ahead` commits all newer than 120 seconds, emit the
finding at `info`, not `warn`. A warning that cries wolf is ignored within a week, including the
once it matters.

Import `git_answered` from `.common` alongside the existing `git` import.

### Severity in bare form — amended after round 4

**Replace the 120-second debounce above with severity keyed on `diverged`.** In bare form:

```python
severity = "warn" if behind else "info"
findings.append(finding("R16", severity, "repos", "sync",
                        repo=info["name"], ahead=ahead, behind=behind,
                        diverged=bool(behind)))
```

That call replaces the one in the § 7 snippet above, which still hardcodes the literal `"warn"` —
copy this one, not that one.

`ahead > 0, behind == 0` is not a fault. `git pull --ff-only` fast-forwards straight through it
(§ 1.1), boot is unaffected, and it clears itself the moment the user pushes — it is the ordinary
state of any session that has committed and not yet pushed, which in this framework is most of
them. Warning on it puts a permanent increment into the warnings count `/lr:check` shows in its
compact summary, and within a week users learn that the counter means "you haven't pushed" and stop
reading it. That is the cry-wolf failure this spec spends § 4 forbidding, shipped in the very first
thing users see.

`ahead > 0, behind > 0` is the permanent failure — every boot's `--ff-only` now fails and the agent
loads stale lore. That earns `warn`.

This also removes the debounce's second git call and its timestamp parsing: the transient
commit→push window is ahead-only, so it is already `info` under this rule. The 120-second
paragraph above is superseded for bare form — it survives only if Tier C's marker is ever built,
where it discriminates a fresh marker from an old one.

### Fix text in bare form — the generic remedy is unsafe

`docs/findings-catalog.md`'s Fix column must **not** carry `fetch && merge && push` for the
diverged case. This spec says so itself, in § 4 Step 5c: *"do not offer `git merge && git push`.
Those commands re-hit the same content conflict and drop the user into a `UU` working tree holding
lore they may not own, with less context than the framework had when it refused."* Bare R16 cannot
distinguish a divergence that will merge cleanly from one hiding a real content collision, and the
safe branch in the original row is gated on `marker.reason`, which Tier A never produces. So bare
form inspects and hands off; it does not resolve.

### `docs/findings-catalog.md` — new row in § Repo findings

| ID | Say using the finding data | Fix | Fix tier |
|---|---|---|---|
| R16 | The repo has `ahead` local commit(s) not on its remote, or a leftover `MERGE_HEAD`; when `diverged` is true it is also `behind`, so **every agent boot from this repo now fails to pull and loads stale lore**. Both counts are as of the last fetch — `check` never fetches — so state them as last-known, not current. When `marker` is present, also say *why* (`reason`) and *how long* (the marker file's mtime age); a marker days old is a persistent fault, not a transient one, and must not read as calmly as a fresh one. A marker beside a repo git shows as clean is stale — say nothing and delete it. When `marker.reason` is `foreign-conflict`, give the marker's own remedy, not the generic one. | `git -C "<repo>" fetch origin && git -C "<repo>" merge origin/<branch> && git -C "<repo>" push`; for `foreign-conflict`, boot the owning agent and reconcile the named paths first | 2 |

Wording rule: the R16 row must state the boot-pull consequence, not only the commit count. The
count alone reads as routine.

**Tier A replaces the row above with this one** (amended after round 4 — no `marker`, no
`MERGE_HEAD`, no blind merge, and the boot-pull consequence attached only to the state that
actually has it):

| ID | Say using the finding data | Fix | Fix tier |
|---|---|---|---|
| R16 | When `diverged` is false: the repo has `ahead` local commit(s) not yet on its remote. Say it plainly and do **not** imply breakage — boot pulls still succeed in this state; it clears on the next push. When `diverged` is true: the repo is `ahead` **and** `behind`, so **every agent boot from this repo now fails to pull and loads stale lore**, and it will stay that way until someone reconciles it. Both counts are as of the last fetch — `check` never fetches — so state them as last-known, not current. | Not diverged: `git -C "<repo>" push`. Diverged: `git -C "<repo>" fetch origin && git -C "<repo>" log --oneline --left-right @{u}...HEAD` to see both sides, then reconcile deliberately — boot the agent that owns the conflicting paths if lore files are involved. Never offer a bare `merge && push`: it re-hits the same conflict and leaves a `UU` tree holding lore the user may not own. | 2 |

---

## 8. C5 — refresh TTL keys on success

`scripts/lr_core/workspace_refresh.py`, `needs_refresh()`. It reads `last-attempt`; `last-success`
is written and never consulted. A workspace failing every attempt looks fresh for 16 hours.

**Change:** read `last-success` for the age comparison. Keep every existing self-heal branch
(missing, unparseable, naive, future-dated → refresh now); a missing `last-success` refreshes.

**Two questions, two stamps — do not collapse them into one floor.** *Amended after round 4;
the original single unconditional floor was wrong in both directions.*

- **Are we due?** Keyed on `last-success` alone: no usable stamp, or `now - last_success >= ttl`.
- **May we attempt now?** Keyed on the *outcome* of the last attempt, not merely its age.
  - The last attempt **succeeded** (`last-attempt` equals `last-success`, or there is no usable
    `last-attempt`) → attempt immediately. No floor.
  - The last attempt **failed or was partial** → require
    `now - last_attempt >= backoff(consecutive_failures)`.

`backoff(n) = min(ttl, RETRY_BASE * 2 ** (n - 1))` for `n >= 1`, with `RETRY_BASE = 900` seconds,
capped at the TTL. **`backoff(0)` is never evaluated** — `n == 0` means the last attempt did not
fail, which is the no-floor branch above. An implementer who reaches `backoff(0)` has mis-bucketed
the attempt; guard it rather than letting `2 ** -1` yield a silent 450.

**The counter, fully specified.** `consecutive-failures` is a new state-file field. It is written by
`write_state`, which gains a `consecutive_failures=None` keyword in its signature and emits
`consecutive-failures: "<n>"` quoted, exactly like the timestamps and for the same reason (the
framework parser returns strings regardless; quoting keeps a real YAML parser from auto-typing it).
`read_state` needs no change — it returns raw strings. `needs_refresh` parses it with
`int()` inside a `try`, and **every unusable shape self-heals to `0`**: absent, empty,
non-numeric, or negative. `0` means "no failures recorded", which routes to the no-floor branch —
the safe direction, consistent with this module's rule that a corrupt stamp costs one extra refresh
rather than suppressing one. This matches how `_stamp_age` already treats every malformed
timestamp.

**Which attempts increment it.** `refreshed` resets it to `0`. `failed` and `partial` increment it.
**`setup-required` does neither** — it leaves the counter untouched and is treated as a *success*
for the floor question, because it is not a failure to reach the remote: it is a workspace whose
repos were never cloned, which no amount of retrying fixes and which already suppresses its own
repeat messaging. Every one of `_do_refresh`'s four statuses is therefore assigned a bucket; add a
new one and this rule must be extended with it.

**What the backed-off case returns.** When the workspace is due but the floor has not expired,
`run_workspace_refresh` returns `{"status": "fresh"}`, unchanged from today — `agent-boot.md`
renders that silently, so a boot in this window says nothing. Worst case is one silent window of
`ttl`, which is exactly today's behaviour for a failing workspace, so this is not a regression; it
is the pre-existing ceiling reached by a different route. **Known gap, deliberately not closed in
Tier A:** nothing surfaces "this workspace has failed to refresh `n` times in a row." The
attempts that *do* run still report `partial` / `failed` with a reason, and `/lr:check` S19 still
reports freshness from pull evidence, so the condition is observable — just not proactively
announced. Revisit alongside R16's data.

**Why a flat floor fails.** Applied unconditionally it is simultaneously too strong and too weak.
Too strong: it silently floors *every* refresh at 900s regardless of the configured TTL, so
`--workspace-ttl 0` stops meaning "always refresh" — a documented CLI contract pinned by two
shipped tests (`test_workspace_refresh.py`, `test_ttl_zero_always_refreshes` at both call sites).
Too weak: real boots are hours apart, so a 900s floor never engages between them, and a workspace
that can never succeed — offline, expired credentials, or a Codex sandbox that blocks `.git`
network access — goes from one bounded 90s `workspace-pull` every 16 hours to one on *every boot*,
permanently. Keying the staleness question on `last-success` is correct and stays; the retry
cadence is a separate question and needs backoff, not a constant.

Update `needs_refresh`'s docstring — it is the literate spec for this function's manual fallback,
so the new rule must be stated there, not only in the code. Update `cli.py`'s `--workspace-ttl`
help text too: it currently says "if the last attempt is older than N seconds" and "0 always
refreshes", and both halves become false.

**Rollout note.** The two `test_ttl_zero_always_refreshes` tests pin the *old* contract. Under this
amendment `ttl=0` on a healthy workspace still refreshes immediately, so they should still pass —
verify that rather than assuming it, and if either fails, the amendment is wrong, not the test
(`a-red-test-may-be-asserting-a-true-fact.md`).

---

## 9. C6 — `workspace-pull` Phase 0

`scripts/workspace-pull`, Phase 0 (≈ lines 255–290).

The guard's own comment is the bug: *"Dirty = any staged or unstaged tracked change. `--ff-only`
would refuse to clobber it anyway; we skip explicitly so the warning is legible."* Verified false —
`--ff-only` succeeds on a dirty repo whenever the incoming commits do not touch the dirty files.

**Change:** invert the order. Attempt the pull first; only on failure run the fetch-and-count
reporting path.

```
if pull --ff-only succeeds:
    phase0_state="pulled"; record_repo_pull
else:
    # fetch, resolve upstream, count behind, warn with the number
    phase0_state="warned (...)"
```

**The existing warning wording must branch by cause, not be reused verbatim.** Today it ends
`commit or stash, then re-run` because it only ever fired for a dirty tracked file. Under the
inverted order it fires for every pull failure, including diverged history and auth or network
errors, where "commit or stash" is actively misleading advice.

- Dirty tracked file collides with an incoming commit → keep the existing wording.
- Diverged history → `workspace root has diverged from <upstream> — reconcile manually, then re-run`.
- Fetch or auth or network failure → report git's own error line; do not advise commit or stash.

Distinguish them from git's error output on the failed pull, not by re-deriving the repo state.
Correct the code comment to state the real rule, citing `workspace_refresh.py:_blocked_repos` as the
canonical statement.

---

## 10. C7 — `conventions.md`

New subsection under § Tooling (sibling of *CWD Safety* and *Portable Shell*):

> **## Tooling: Git Safety**
>
> Four rules bind every automatic git path in the framework.
>
> 1. **Name the paths.** Never `git add <directory>`, never a bare `git commit`. Stage and commit by
>    explicit pathspec, then verify with `git show --name-only --format= HEAD` that nothing else
>    rode along. A workspace can have concurrent and unattended sessions with work already staged.
> 2. **Never discard to resolve.** No `--autostash`, no `stash`, no `--force`, no `reset --hard` in
>    any automatic path. **`git pull --ff-only --autostash` exits 0 on a real content collision
>    while writing conflict markers into the file** — it converts a safe refusal into a silent
>    corruption that reports success. A refusal is an acceptable outcome; a silent overwrite is not.
> 3. **Never content-judge what you did not author.** Automatic conflict resolution is permitted
>    only on paths in the operation's recorded write-set, and only by an executor booted as the
>    agent that owns them. See `publish-lore.md` Step 4a.
> 4. **Never leave a commit stranded quietly.** An operation that commits but cannot push must say
>    that the repo is now ahead of its remote and that agent boots from it will fail to pull. See
>    `publish-lore.md` Step 5.

Cross-reference it from `publish-lore.md`, `finalize.md`, `update.md` and `workspace-push.md`
(pointer, not restatement).

### Tier A form — amended after round 4

**Ship rules 1 and 2 only.** Rules 3 and 4 both end in `See publish-lore.md`, which C1 creates and
C1 is Tier B. Landing them in Tier A adds two dangling cross-references to the one document every
automatic git path is bound by — the reference rot the standing improvement list already carries as
item A1. They move to Tier B, alongside the document they cite.

**Rule 1 ships with a Known gap, not silently.** `docs/finalize.md` § Phase 4 step 1 is literally
`git -C <repo> add agents/` — the exact directory-add rule 1 forbids. C2 is what fixes it, and C2
is Tier B. A convention that the framework's own shipped code visibly violates, with nothing saying
so, is worse than no convention: the next reader cannot tell whether it is a rule or an aspiration.
So Tier A's § Tooling: Git Safety carries a closing subsection, in the `### Known gap:
workspace-root paths` style this file already uses:

> **### Known gap: `finalize.md` Phase 4**
>
> `finalize.md` § Phase 4 stages `git add agents/`, which rule 1 forbids. It is the last automatic
> path in the framework that does, and it is scheduled for replacement by the `publish-lore.md`
> procedure. Until then, treat rule 1 as binding on all new and modified code and do not cite
> Phase 4 as precedent.

Do **not** fix `finalize.md` Phase 4 as part of Tier A. It is C2's job, C2 is gated behind the deep
cold review, and a partial hand-fix here is unreviewed Tier B work wearing Tier A's clearance.

---

## 10a. C8 — `lrb status` surfaces a stranded publication

**This closes the design's own premise.** I1 says no operation may fail silently. For an interactive
session "loud" means text the user reads. For an unattended Being it means nothing: the Keeper
redirects session stdout to `logs/<being>/…` and never parses it for meaning, the outcome contract
extracts only `total_cost_usd` / `is_error` / `result`, and a session that reports its own stranding
in prose and then ends normally is `is_error: false`. `beings.md` states plainly that a red line in
`lrb status` means a crashed, timed-out or over-budget session — a stranded publication is none of
those. So the daemon's repo can rot indefinitely while every status surface stays green.

**Change (`scripts/lrb.py`, `cmd_status`):** for each being, resolve its agent's repo and call
`read_stranded_marker(repo)` (§ 4 Step 5c rule 4). When it returns a marker, print one line for that
being — being name, repo, `reason`, and the marker's mtime age — and include it in `--json` under
the being's entry.

**Cost correction.** An earlier draft said this could "count toward the 'not ok' total that `status`
already reports". It cannot: `cmd_status` computes no ok/not-ok aggregate — verified, that concept
exists only in `cmd_validate`, which checks configuration rather than runtime health. C8 therefore
adds a small aggregate to `cmd_status` as well as the per-being line. Still modest — one canonical
reader call per being, no network, no git object access, and a being with no marker costs one
`os.path.exists` — but not a one-line hook into existing logic.

**Ordering:** C8 depends on C1 (the marker is defined there) and on nothing else.

---

## 11. Test plan

Fixture repos under a scratch dir; a bare repo as `origin`, two clones as concurrent sessions. Each
test asserts on git state, never on prose. New tests must be shown **red against `lr--v1.45.0`** and
green against HEAD, via a detached worktree with `LR_FRAMEWORK_DIR`.

### Deterministic (`tests/`, stdlib unittest — run modules individually per `tests/README.md`)

| # | Test | Asserts |
|---|---|---|
| T1 | `repo_scan` on a repo with 2 local commits, remote unchanged | R16 present, `ahead=2`, `diverged=False` |
| T2 | `repo_scan` on a diverged repo | R16 present, `diverged=True` |
| T3 | `repo_scan` on a clean synced repo, and on a repo with no upstream | no R16 in either |
| T4 | `needs_refresh` — `last-success` old, `last-attempt` recent | False before `retry_floor`, True after |
| T5 | `needs_refresh` — `last-success` absent | True |
| T6 | `needs_refresh` — `last-success` recent, `last-attempt` old | False |
| T7 | `workspace-pull` Phase 0 with an unrelated dirty tracked file | exit 0, root repo fast-forwarded |
| T8 | `workspace-pull` Phase 0 with a dirty file the incoming commit also touches | pull refused, dirty-cause wording emitted |
| T8b | `workspace-pull` Phase 0 on a diverged root | diverged-cause wording, **not** "commit or stash" |
| T9 | Grep the shipped tree for `--autostash`, `reset --hard`, `git add agents/`, bare `git add -A` without `--` | no hits outside `conventions.md`'s own prohibition text |

**Amended after round 4 — Tier A adjustments to this table:**

- **T1/T2 assert severity, not just presence.** T1 (ahead-only) must assert `severity == "info"`;
  T2 (diverged) must assert `severity == "warn"`. That is the cry-wolf guard, and without it the
  amended § 7 rule ships untested.
- **T4 is rewritten for the outcome-keyed backoff; T5 and T6 stand as written.** T5
  (`last-success` absent → True) and T6 (`last-success` recent, `last-attempt` old → False) both
  exercise the *due* question, which the backoff does not touch — no edit needed, and each still
  passes. T4 becomes: last attempt *failed*,
  `last-success` old → False before `backoff(n)`, True after. Add **T4b**: last attempt
  *succeeded*, `last-success` older than a `ttl` below 900 → **True immediately**, no floor. T4b is
  the regression guard for the `--workspace-ttl 0` contract, and it is red against the unamended
  design.
- **T9 is deferred to Tier B.** `docs/finalize.md` § Phase 4 currently contains `git add agents/`
  and only C2 removes it, so T9 cannot pass on a Tier-A-only tree. Landing it now means either a
  test that fails on green code or a pattern narrowed until it no longer catches the thing it
  exists to catch. Tier A instead runs **T9a**: the same grep for `--autostash`, `reset --hard`
  and `--force` in automatic paths only, which passes on the current tree and locks in rule 2 of
  § Tooling: Git Safety. **Scope the pattern to git invocations**, not bare flag names:
  `scripts/lrb.py:941` contains `cmd.extend(["--force", "--sandbox", "disabled"])`, a Cursor
  subprocess flag with nothing to do with git, and a naive `--force` grep fails on green code.
  Match `git` and the flag on one line (e.g. `grep -nE 'git .*(--autostash|--force|reset --hard)'`),
  and assert the hit set is empty outside `conventions.md`'s own prohibition text.

Tier A's deterministic set is therefore T1, T2, T3, T4, T4b, T5, T6, T7, T8, T8b, T9a.

### Procedure-level (`tests/lifecycle/`, real engine, cheapest tier)

| # | Scenario | Asserts |
|---|---|---|
| T10 | Finalize with a concurrent session holding staged edits under another agent | commit contains only the write-set; the other session's staged work is still staged and uncommitted |
| T11 | Finalize where the remote advanced mid-session, no conflict | push succeeds within the retry cap; repo ends `ahead=0` |
| T12 | Finalize where the remote advanced with a conflicting `lore-context.md` | conflict resolved inline, push succeeds, both sides' entries present |
| T13 | Finalize with push impossible (unreachable remote) | stranded-commit report emitted **including the literal boot-pull consequence sentence**; next `/lr:check` reports R16 |
| T14 | Boot in a repo with an unrelated dirty file and untracked files | pull succeeds; local edits byte-identical afterwards |
| T15 | **Finalize on a repo that already carries a stranded commit, where the remote conflicts on that stranded commit's file** | merge aborted, **no** inline resolution of the foreign path, stranded report names it (I4) |
| T16 | **`/lr:update` on an already-ahead repo, push rejected** | single push attempt, no merge commit created, `HEAD` still equals the `lr-update-pending` recorded commit, marker still valid for retry |
| T17 | Finalize while a stale `.git/index.lock` is held | reports the lock, does not delete it, does not spin |
| T18 | Merge deletes a **carried-over** reflection topic | the deletion is in the commit; no blocked/failed reflection is swept in |
| T19 | **Publish into a repo left mid-merge by a killed session** | stops with `merge in progress`; **never** reports `nothing to publish`; no commit created |
| T20 | **Publish where Step 1 stages nothing** | reports `nothing to publish`; exit path distinct from T19's |
| T21 | **Foreign-conflict stop on a repo that was at `ahead=0`** | this operation's commit is rolled back; `ahead` is 0 again; marker written with `reason: foreign-conflict` and the foreign paths |
| T22 | **Three consecutive foreign-conflict stops** | `ahead` never grows across them; exactly one marker exists, its mtime unchanged after the first write (same `reason`) |
| T23 | **Conflict on `agents/<name>/reflections/**` or a `sessions/**` summary** | classified **Foreign**, not Ours — it is agent-owned and in the write-set but outside `resolve-conflicts.md` § Scope |
| T24 | Host + guest sharing one repo, conflicts in both subtrees | guest paths resolve via a subagent booted as the guest, not inline by the host |
| T25 | Successful publish that required a merge | the success line names the merge and the incoming commit count |
| T26 | **`lrb status` with a marker present in a being's agent repo** (C8) | the being is listed as not-ok with reason and age |
| T27 | R16 with a marker beside a repo git shows as **clean** | marker treated as stale: nothing reported, file deleted |
| T28 | **Repeated foreign-conflict stops starting from `ahead > 0`** | `ahead` does not grow across them — the case the withdrawn carve-out would have regressed |
| T29 | **Stranded publish from inside a `.worktrees/<repo>/<slug>/` checkout** | marker lands in the shared common dir and is seen by both C4 and C8 |
| T30 | Two concurrent publications fail on the same repo at once | exactly one well-formed marker exists afterwards; no partial file |
| T31 | Marker with unparseable YAML, an unknown `version`, or a non-current `branch` | each ignored and deleted; no finding emitted |
| T32 | `ahead > 0` with all commits younger than 120s and no marker | R16 at `info`, not `warn` (C4 transient suppression) |
| T33 | `read_stranded_marker` called from both C4 and C8 paths on one marker | both report identical reason and age |

T13, T15, T19, T21, T26, T27 and T28 are the load-bearing ones. T27 guards the cry-wolf direction
(a marker must never outlive the fault it describes) and T28 guards the ratchet direction. T13 tests that the loud failure is actually
loud and T26 that it is loud *where nobody is watching*; T15 and T23 test I4; T19 tests the silent
no-op hole; T21 and T22 test I5's ratchet guard. Assert on the literal consequence sentence in T13
— executors routinely do the substantive work and drop the mandated output line.

T19 must be shown red against the current design as well as against `lr--v1.45.0`: the earlier
draft of this spec would have passed a blocked merge off as success, so this test is the regression
guard for a defect this review introduced and then removed.

---

## 12. Rollout

- **Version:** v46. Release-notes only — no migration, no repo file changes, no `lore-repo.md`
  schema change.
- **Cache-affecting:** yes (`scripts/lr_core/repo_scan.py`, `scripts/lr_core/workspace_refresh.py`,
  `scripts/workspace-pull`, and SKILL.md-referenced docs). Release notes carry the hoisted
  **Clear Plugin Cache** footer per `conventions.md` § Clear Plugin Cache.
- **Manifests:** bump all four to `1.46.0` (`.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`'s `lr` entry, `.cursor-plugin/plugin.json`,
  `.codex-plugin/plugin.json`).
- **History backfill:** add the v46 entry to `versioning-release-types.md` in the same finalization
  — kind, scope, cache-affecting annotation.
- **Skill count:** unchanged at 31. `publish-lore.md` is a procedure doc, not a skill.
- **Touched beyond docs:** `scripts/lr_core/common.py` (the canonical marker reader, § 4 Step 5c
  rule 4), `scripts/lr_core/repo_scan.py` (C4), `scripts/lr_core/workspace_refresh.py` (C5),
  `scripts/workspace-pull` (C6), `scripts/lrb.py` (C8).
- **Boot latency:** unchanged. C3 puts the update path in `no-merge` mode precisely so that
  `version-check.md` Step 4 does not inherit a fetch-merge-retry loop inside boot.
- **Multi-engine:** all changes are prose plus stdlib Python plus portable shell. Codex's sandbox
  blocks `.git` writes and network, so publication already degrades there; `engines/codex.md` gains
  one sentence stating that under a blocked sandbox the lore files remain on disk uncommitted and
  the user must publish manually — unchanged in substance, now stated.
### Tier A rollout — added after round 4

§ 12 above is written for the ten-change ship. Tier A is four of those ten, and needs its own
answers rather than a subtraction exercise:

- **Version: v46, release-notes-only, cache-affecting.** It touches `scripts/lr_core/repo_scan.py`,
  `workspace_refresh.py`, `common.py`, `cli.py`, `preflight.py`, `scripts/workspace-pull`, and two
  SKILL.md-referenced docs, so the release notes carry the hoisted **Clear Plugin Cache** footer
  per `conventions.md` § Clear Plugin Cache. No migration, no repo file changes, no schema change.
- **Tier B becomes v47**, and Tier C is decided from R16's data rather than scheduled. Shipping
  Tier A as its own version is not bookkeeping: R16 only starts measuring how often divergence
  actually happens once it is installed and running in a real workspace, and that measurement is
  what § 14a says should decide whether Tier C is built at all.
- **Manifests:** all four to `1.46.0`.
- **Skill count:** unchanged at 31. Tier A creates no skill and no new doc — `publish-lore.md` is
  Tier B.
- **Release notes must state what Tier A does *not* do.** It reports divergence; it does not stop
  the framework from causing it. A user who reads "lore sync hardening" and assumes finalize no
  longer strands commits will be wrong for a whole release cycle. One sentence, in the notes.
- **History backfill:** the v46 entry in `versioning-release-types.md` in the same finalization,
  describing the tier honestly — detection plus three contained fixes, not the cure.
- **Gate dispositions:** deterministic tests and `/lr:check` run; dogfood onto this workspace; the
  lifecycle suite and TriLens are `did not run` unless asked, and this round-4 design review is
  recorded as what it was — a design gate, not a code gate. It certifies the spec, not the
  implementation.

- **Ordering.** C5, C6 and C7 are independent and can land first. C1 precedes C2, C3, C3a, C3b,
  C4 and C8 — C4 and C8 both read the marker C1 defines. C4 without C1 is still worth landing
  (bare ahead/behind detection), so it may go early in reduced form if C1 slips.

---

## 13. Open questions

1. **Retry cap of 3.** Inherited from `resolve-conflicts.md`. It bounds the *transient* race only;
   Step 5b now handles the blocking cases, and no retry count fixes a ratchet. Proposal: keep 3.
2. **`git merge-tree` escape hatch** (§ 4 Known residual) — specify now, or only after the marker's
   R16's marker reporting shows the merge-blocked case actually recurring? Proposal: the latter.
   C1 now produces the very evidence needed to decide, which is a reason to wait rather than guess.
3. **Rollback versus durability (I5 versus crash-safety).** Step 5b rolls this operation's commit
   back on the blocking failures. That breaks the ratchet, but it also means an offline or blocked
   finalize leaves the session's lore staged rather than committed. Nothing is lost — the files are
   on disk and the next publication picks them up — but a user who believes "finalize means
   committed" will be surprised once. Accepted deliberately; the alternative is a repo that wedges
   harder every time it fails. Worth one sentence in the finalize release note.
4. **Marker lifetime.** Removed on the next successful publication, and by any consumer that finds
   it stale. Should a marker older than N days escalate R16 from `warn` to `error`? Proposal: not
   in v46 — report reason and mtime age first, and set any threshold from real data rather than
   taste. The marker deliberately carries no counters; mtime is the only age signal, which is
   enough for this decision and costs no bookkeeping.

---

## 14a. Implementation order — decided 2026-09-13, next session

Three review rounds did not converge, and reading *where* the findings came from says why. Rounds 1
and 2 found real flaws in the design. Round 3's single BLOCK was a defect **round 2's own fix
introduced**. Across nine reviewer passes nobody ever attacked the core — narrow staging, verify,
merge-retry, loud failure. What keeps breaking is the elaboration around it.

That is not a signal to review harder. It is a signal that this document has outgrown what prose
review can certify, and the answer is to ship it in tiers and let the cheap tier produce the
evidence for the expensive one.

**Tier A — land first.** C5 (refresh TTL on `last-success`), C6 (`workspace-pull`
Phase 0), C7 (`conventions.md` § Tooling: Git Safety), and **C4 in bare form** — R16 reporting
ahead/behind only, with no marker dependency. Nine reviewer passes produced zero findings against
any of these. Each stands alone, and bare R16 starts measuring how often divergence actually occurs.

> **Superseded in part, 2026-09-13.** "No further review" was wrong, and the reason is worth
> keeping: those nine passes reviewed the **whole spec**, in which Tier B's artifacts exist by
> assumption. Tiering is itself a change, and the subset had never been reviewed as a subset. A
> round-4 review scoped to Tier A alone returned two SHIP-WITH-FIXES and one **BLOCK**, six real
> findings, two of which would have shipped a user-visible regression (§ 14, *Fifth*). They are
> amended into §§ 7, 8, 10, 11 and 12. **Tier A is implementation-ready as amended**; the general
> lesson — carving a reviewed whole into tiers produces an unreviewed artifact at every seam — is
> the part that outlives this spec.

**Tier B — the cure.** C1, C2, C3, C3a. Before implementing, run **one deep unconstrained
cold reviewer** over Tier B alone — the framework's prescribed substitute when the round cap ends a
loop without a clean round (`parallel-reviewer-fanout-pattern.md`). Not a fourth three-lens round:
the lenses are spent, and the remaining risk is depth, not breadth.

**Tier C — defer, and decide from data.** The stranded-publish marker (§ 4 Step 5c), C8, and the
Ours/Foreign classification (§ 4 Step 4a). These generated the majority of findings in all three
rounds. Tier A's R16 will say within a few weeks whether the states they handle are frequent enough
to earn their cost. If divergence turns out to be rare once Tier B lands, most of Tier C should be
dropped rather than built.

**Do not implement Tier B or C from this document without the deep review.** Its last round's fixes
are unreviewed, and the one defect that reached round 3 was introduced by a fix, not by the original
design.

## 14. Provenance

Problem established by direct git experiment (7-case blocking matrix, autostash behaviour,
plumbing-publish feasibility), not from documentation.

Design reviewed twice. First, four cold-context reviewers on the original proposal — adversarial,
simplification, framework-coherence, alternative-designs; an earlier "sidecar publish via git
plumbing" design was dropped because three of four independently established that it leaves the
working tree permanently unable to fast-forward, and `git commit -- <paths>` supplies the one
property it was designed to provide.

Second, a round of three cold lenses on the first draft of this spec — simplicity/extensibility,
adversarial correctness, executor fidelity. Fourteen findings, all applied. What it forced:
invariant **I4** and a conflict classification (the first draft asserted conflicts could only touch
the current write-set, which a stranded commit disproves — verified by experiment); the `no-merge`
mode and the `lr-update-pending` marker contract; the C3a edit-ordering fix; the
`Reflections removed:` handoff field; a non-message-text test for "nothing to publish"; and the
corrected § 1.3 framing, since Step 4 is new design rather than a generalization of the precedents.
Round 3 below superseded two of these — the classification collapsed from three classes to two, and
the "nothing to publish" test moved again, from `HEAD`-comparison to the staged set.

Third, a round of four cold lenses on that revision — simplicity, conflict-classification
correctness, operator recovery, and a claim audit. Verdicts: SHIP-WITH-FIXES, **BLOCK**, **BLOCK**,
SHIP-WITH-FIXES. Sixteen findings, fifteen applied and one declined. The substantive changes it
forced:

- **The blocked-merge silent no-op.** A pathspec commit inside an unfinished merge fails
  `fatal: cannot do a partial commit during a merge.` with exit 128 and `HEAD` unchanged — the exact
  signature the previous draft classified as "nothing to publish, a success". A repo left mid-merge
  by a killed session would have swallowed every later publication, permanently and silently.
  Reproduced independently before applying. Fixed by a `MERGE_HEAD` precondition and by deciding
  emptiness from the staged set instead of from the exit code.
- **`<owner-agent>` was not singular.** Finalize commits host and co-resident guests into one commit
  per repo, and `lore-agents` holds eleven agents in one repo. Raised by two lenses independently.
- **The Foreign-conflict ratchet.** Aborting kept this operation's commit, so each blocked attempt
  added a stranded commit instead of clearing one, and one foreign file could block every agent in
  the repo forever. Produced invariant I5 and Step 5b's rollback rule; the earlier "self-healing"
  claim is withdrawn.
- **I1 was unenforceable for the unattended daemon.** "Loud" meant prose in a log nobody parses, and
  the Being's run is recorded `is_error: false`. Produced the durable marker (Step 5c) and C8.
- **The Ours class was wider than `resolve-conflicts.md` § Scope**, which would have sent conflicted
  `reflections/**` and `sessions/**` paths to a procedure that has no rule for them.
- Also: `merge --abort` discards staged resolution (the invariants implied otherwise); the
  Foreign-conflict remedy reproduced the failure it was recovering from; the three-class table
  collapsed to two; C3b demoted from rewiring to a cross-reference; the self-count corrected from
  eight to nine.

**Declined (1):** merging invariants I3 and I4 into one rule. They bar different things — unsafe
mechanism versus unsafe authority — and it was I4's separate naming that made round one's blocker
findable. I5 was added for the same reason rather than folded into either.

**Not converged.** Round 2 ended with two BLOCK verdicts and sixteen findings; those fixes have not
been reviewed. A third round, scoped to Step 5's rollback/marker logic and to C8, is the next step
before implementation.

Fourth, a round of three cold lenses on that revision — simplicity, the marker as persistent state,
and a first-principles regression against the original five failure cases. Verdicts: **BLOCK**,
SHIP-WITH-FIXES, SHIP-WITH-FIXES. Thirteen findings, all applied. What it forced:

- **The rollback carve-out was the ratchet, reintroduced.** Step 5b rolled back "unless the repo was
  already ahead" — which is precisely when a persistent block recurs, so `ahead` grew by one on
  every repeat. All three lenses caught it independently, and one observed that the exception was
  never even necessary: `reset --soft HEAD^` removes only the most recent commit and cannot touch
  commits already ahead, so it protected nothing. Now unconditional. Invariant I5 was restated to
  match what the table actually delivers, rather than overclaiming.
- **The marker was a verdict; it should be a hint.** Nothing invalidated it when a human fixed the
  repo by hand, so a healthy repo would have reported a fault forever — the cry-wolf failure this
  spec forbids three sections earlier, self-inflicted. Consumers now revalidate against git and
  delete a stale marker.
- **The marker was in the wrong place.** `--absolute-git-dir` diverges per worktree (verified), so a
  stranded publish from `.worktrees/` was invisible to both consumers — reopening the daemon hole
  round 2 closed. Now `--git-common-dir`.
- **The marker's counters were a lost-update race and premature.** `count`/`first_seen` required a
  read-modify-write two concurrent publications could interleave, and served only a decision § 13.4
  defers. Dropped for the file's own mtime. Two lenses converged on this.
- **Two parsers, no canonical reader.** C4 and C8 each parsed the marker independently. Now one
  `read_stranded_marker()` in `common.py`.
- Also: C8's cost was misdescribed (`cmd_status` has no ok/not-ok aggregate — verified); the
  `merge-blocked` reason had no field for its blocking paths; seven tests added, including the two
  guarding the directions this round found broken.

**Round 3 also proposed a materially simpler design** — drop automatic conflict resolution
altogether — which would remove the mode parameter, the ownership test and the whole two-class
table. Rejected, with the reason recorded in § 3: it trades away automatic reconciliation of
`lore-context.md`, the single most frequent collision in the system, for a manual stop every time
two sessions run the same agent. The simplification is real; the trade is bad.

Fifth, a round of three cold lenses scoped to **Tier A only** — tier-boundary/partial-ship,
call-site/integration reality, and installed-population/first-boot-after-upgrade. Run 2026-09-13 at
the user's direction, against a deliberately clean tree (a partial Tier A implementation was
reverted first so all three lenses certified one state). Verdicts: SHIP-WITH-FIXES,
SHIP-WITH-FIXES, **BLOCK**. Thirteen findings, six real after triage, all amended into §§ 7, 8, 10,
11 and 12 in place rather than recorded only here.

The round existed because **tiering is itself a change, and nobody had reviewed the subset as a
subset.** Every prior round read the whole spec, where Tier B's artifacts are present by
assumption. What it forced:

- **C5's flat retry floor was wrong in both directions** — two lenses, independently. Too strong:
  ANDed unconditionally it floors *every* refresh at 900s regardless of configured TTL, breaking
  the documented `--workspace-ttl 0` contract that two shipped tests pin. Too weak: real boots are
  hours apart, so the floor never engages between them, and a workspace that can never sync
  (offline, expired credentials, Codex's sandboxed `.git`) went from one bounded 90s
  `workspace-pull` per 16 hours to one on *every boot*, permanently — against § 12's own
  "Boot latency: unchanged". Replaced by outcome-keyed backoff.
- **C7 would have shipped a rule the framework itself breaks.** Rule 1 forbids `git add
  <directory>`; `finalize.md` § Phase 4 step 1 *is* `git add agents/`, and only C2 (Tier B) removes
  it. Now ships with an explicit Known gap, and rules 3–4 move to Tier B with the document they
  cite.
- **The R16 catalog row contradicted § 4 Step 5c** — it offered `merge && push` as the generic
  remedy, the exact sequence Step 5c calls unsafe because it re-hits the conflict and leaves a `UU`
  tree. Bare R16 cannot tell which divergences are clean, and the safe branch was gated on marker
  data Tier A never produces.
- **R16 warned on the ordinary unpushed-commit state**, which is not a fault at all — cry-wolf in
  the first thing users see, shipped alongside pages forbidding it. Severity now keys on
  `diverged`, which also deletes the 120s debounce, one git call and its timestamp parsing.
- Also: the marker paragraph in § 7 had no in-place "Tier C only" marking (the qualifier lived
  seven sections away in § 14a); the bare-C4 snippet omitted the debounce its own prose promised;
  T9 cannot pass on a Tier-A-only tree; and § 12 had no Tier-A rollout.

Sixth, **one cold reviewer over the round-4 amendments alone** — the lens being whether the fixes
introduced defects, this document's own recurring failure. Verdict: SHIP-WITH-FIXES, ten findings,
nine applied and one accepted. It was worth running: two were HIGH and one of those is the shape
the lens was chosen for — § 14's closing paragraph still read *"the substitute for a fourth round is
one deep unconstrained cold reviewer... before any implementation begins"*, directly contradicting
the readiness § 14a now asserts a few dozen lines earlier. A new statement of readiness left
standing beside an old statement of non-readiness is precisely `single-canonical-source-discipline`'s
failure mode, self-inflicted while fixing something else. The other HIGH: `consecutive-failures` was
introduced as "a new integer field" with no serialization, no parse-failure rule and no slot in
`write_state`'s signature — an implementer would have invented all three. Also forced: `backoff(0)`
guarded rather than left to evaluate `2 ** -1`; `setup-required` explicitly bucketed; the
backed-off return status stated and its silence recorded as a known gap; T9a's pattern scoped to
git invocations after verification that `scripts/lrb.py:941` carries a non-git `--force`; the § 7
skip note corrected from "four paragraphs" to the two actually skipped, since *Anything else* must
survive into bare form; and the amended severity rule given its own copyable call site.

**Accepted, not applied (1):** the finding that this document is now long enough that its tier
qualifications are hard to follow. True, and not fixable by another edit to it — the answer is that
Tier A's amendments live in the sections that own them, which is what round 4 did.

**Declined (1):** an off-switch or tuning knob for R16. It is clearable by pushing, so it is not the
unclearable-finding trap `conventions.md` warns about.

Lenses now spent across five rounds: adversarial, simplification/simplicity (×4),
framework-coherence, alternative-designs, executor fidelity, conflict-classification correctness,
operator recovery, claim audit, marker-as-persistent-state, first-principles regression,
tier-boundary/partial-ship, call-site/integration reality, installed-population/upgrade.

**Status after three rounds: not converged.** Findings fell 14 → 16 → 13, and the last round's were
smaller in kind — but it still produced a BLOCK, and its fixes are unreviewed. The loop's three-round
ceiling ended it, not a clean round. Per this framework's own rule, the substitute for a fourth
round is one deep unconstrained cold reviewer, and that is the recommended next step before any
implementation begins.

**Status after five rounds — this paragraph supersedes the one above for Tier A only.** The
sentence "before any implementation begins" was written when this document was one indivisible
ship. It still binds **Tier B and Tier C**: neither may be implemented without the deep
unconstrained cold reviewer. It no longer binds **Tier A**, which was carved out, reviewed on its
own in round 4, amended, and re-reviewed in round 5. Tier A is implementation-ready as amended
(§ 14a). Nothing else in this document is.
