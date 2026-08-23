# Design — Automatic daily workspace refresh

**Status:** design, not implemented. Ready for handover.
**Target version:** v42 (cache-affecting).
**Owner:** lore-architect.
**Date:** 2026-08-23. Revision 2, after three-lens cold review.

> **Revision 2 changes.** §4's evidence corrected (a factual error). §6 gains a lock file — the
> original concurrency guard did not actually exclude, and a killed refresh silently disabled the
> feature for 16h. §8 substantially rewritten: the JSON contract in revision 1 invented fields the
> scanner does not emit, and specified values with no derivation path. §9, §10, §11 and §12
> adjusted to match. All code claims in this revision were verified by reading the source.
>
> **Revision 2.1.** § 13 Q1 (per-child dirty guard) closed: report, do not guard. New § 8.9 carries
> the reasoning; `pulled` becomes a list with a per-repo `dirty` flag (§ 8.5, § 8.8) and § 9.2 gains
> the reporting rule.
>
> **Revision 2.2 — lean pass over revision 2's own additions.** Four redundancies removed: the JSON
> object carried two overlapping enums (`status` and `result`) that disagreed on `failed`; `result`
> carried a `running` value duplicating the lock file's existence; `reason: blocked` duplicated a
> non-empty `blocked_repos`; and the lock file carried a timestamp the filesystem already stores as
> mtime. Nothing was added.
>
> **Revision 2.3.** § 13 Q4 closed by reframing: the refresh **never clones**. A workspace with
> missing declared repos short-circuits to `setup-required` and defers to the user (new § 8.10).
> This removes a day-one failure where a fresh workspace's first boot would time out mid-clone.

---

## 1. Problem

Work in a workspace for days and its repos go stale. Nothing tells you. `/lr:workspace-pull`
exists, but it only runs when a human remembers to type it — and the whole point of the failure
mode is that nobody remembers.

The workspace repo itself is included in this. It carries `lore-workspace.md`, so a stale
workspace root also means a stale view of which repos exist at all.

## 2. Solution in one line

At agent boot, if the workspace has not been refreshed in 16 hours, refresh it — pull everything,
scan for problems, and report only what blocks the user.

## 3. Scope

**In scope**
- A workspace-refresh leg in `lr-core preflight`.
- Persistent state and a lock under `<workspace>/.tmp/lr-state/`.
- Extraction of a reusable minimal-YAML parser from `common.py`.
- Reporting rules in `docs/agent-boot.md` Step 2, and a raised timeout figure in Step 1.

**Out of scope**
- A workspace *cleanup* command. `/lr:workspace-status` already diagnoses and names fixes; what was
  missing is that it never ran on its own. An auto-*fixing* command is separate work.
- Any change to `/lr:workspace-pull`'s own behaviour or output.
- Any change to `workspace_scan`'s finding set. See § 8.6 for why the blocked-repo probe lives in
  the refresh leg instead.
- Background/async refresh. The refresh is synchronous and bounded.

---

## 4. Key decision: sequential, not parallel

The original design ran the workspace refresh **in parallel** with preflight's existing agent-repo
pull. **Do not implement it that way.**

1. `scripts/workspace-pull` **has no TTL awareness** — it does not know `.git/lr-last-pull` exists,
   so it pulls the agent's own repo regardless of what preflight just did.
2. The agent's repo is normally a top-level repo inside the workspace, so **phase 4 pulls the exact
   repo preflight's agent leg is pulling.** Two concurrent `git pull` calls on one repo contend on
   `.git/index.lock`, and one fails with an error unrelated to the real cause.
3. There is **no way to exclude a specific repo** from phase 4. The script takes one positional
   argument (`Usage: workspace-pull [WORKSPACE_DIR]`, line 46 `WORKSPACE_INPUT="${1:-.}"`) and no
   options. Adding an exclusion means adding an option parser.

> **Correction from revision 1.** That revision claimed the script "accepts no arguments — there is
> no argv handling at all." That is false; it takes a positional workspace directory. The
> conclusion is unchanged — there is still no per-repo exclusion — but the stated evidence was
> wrong.

And the parallelism buys almost nothing. Both legs block boot either way, so parallelism saves only
the *overlap*: one repo's pull (~1s), at most once per 16 hours — in exchange for a lock-contention
bug and an option parser.

**Decision: sequential — agent repo first, then the workspace refresh.** If the workspace leg times
out, the agent's own lore is already fresh.

**Accepted cost.** The agent repo is pulled twice on a refresh boot; the second is a no-op
`Already up to date`. One redundant round-trip on one repo, once per 16 hours. Making
`workspace-pull` TTL-aware would remove it, but that changes a shared script for no user-visible
gain. Recorded so a future reader knows it was a choice.

---

## 5. Trigger and timing

| Property | Value |
|---|---|
| Trigger point | `lr-core preflight`, after the whole agent-repo `if/else` block (see § 8.1) |
| TTL | 16 hours (`57600` seconds) |
| TTL basis | `last-attempt`, **never** `last-success` |
| Mutual exclusion | Lock file, exclusive create (§ 6.3) |
| Stale-lock reclaim | 300 seconds |
| Blocking | Yes — synchronous, bounded |
| Cloning | Never. A workspace needing clones short-circuits to `setup-required` (§ 8.10) |
| Failure mode | Warning. Never fatal. Boot continues. |

### Why 16 hours and not 24

A 24-hour window drifts. Start work at 09:00 Monday and Tuesday's 09:00 boot falls just inside the
window, so the refresh slips to lunchtime — and later every day after. A 16-hour window always
clears overnight, so the first boot of each day refreshes.

### Why `last-attempt` and not `last-success`

If the TTL keyed off success, a persistent failure would make **every** boot pay the full timeout.
Keying off attempt means a bad morning costs one slow boot, not one per boot.

---

## 6. On-disk state

Two files under `<workspace>/.tmp/lr-state/`:

| File | Purpose | Lifetime |
|---|---|---|
| `workspace-refresh` | Readable state — when, whether, why | Persistent |
| `workspace-refresh.lock` | Mutual exclusion + crash detection | Only while a refresh runs |

### 6.1 Why a directory, not one shared state file

- **Concurrency.** This workspace runs parallel sessions, including a live launchd Keeper. A shared
  file means two unrelated features can write it at the same moment and one silently loses. One
  file per concern gives a single writer.
- **Independent lifetimes.** "Delete the file to force a refresh" stays safe.
- **No nesting.** A shared file needs a section per feature, which needs a nesting-capable parser.

Future features add a **sibling file**, never a key.

`/.tmp/` is already one of the three standard ignore lines (`/.worktrees/`, `/.lr-beings/`,
`/.tmp/`), so these files are gitignored in any workspace that has been through `workspace-pull` or
`workspace-init`. See § 6.6 for the first-run case.

### 6.2 State file format

Extensionless. No fences. Comments plus scalar `key: value`.

```
# Lore workspace refresh state. Written automatically at agent boot.
# Delete this file to force a refresh on the next boot.
last-attempt: "2026-08-22T16:14:03+07:00"
last-success: "2026-08-21T08:52:11+07:00"
result: failed
reason: pull-failed
```

| Field | Read by logic | Values | Notes |
|---|---|---|---|
| `last-attempt` | **Yes** | ISO 8601 with offset | Drives the TTL. Written before the refresh runs. |
| `last-success` | No | ISO 8601 with offset | Written only on `ok`. Human diagnostic. |
| `result` | No | `ok`, `partial`, `failed` | Human diagnostic only. Terminal values only. |
| `reason` | No | see § 8.5 | Present only when `result` is `partial` or `failed`. |

> **`result` is not the crash guard, and carries no `running` value.** Revision 1 relied on a stuck
> `result: running` being noticeable. It is not: nothing reads it, so a killed refresh left a
> *fresh* `last-attempt` and the workspace silently went unrefreshed for a full 16 hours — the exact
> failure the feature exists to prevent. The lock file (§ 6.3) is the real mechanism, and its
> existence *is* the in-progress signal — so a `running` value would be a second, weaker
> representation of the same fact. `result` therefore only ever holds a terminal outcome, and a file
> whose `result` predates its `last-attempt` simply means the run has not finished yet.

**Timestamps are quoted.** The framework parser returns strings, but a real YAML parser auto-types
an unquoted ISO timestamp into a datetime. Quoting keeps it a string either way.

**Local offset, not `Z`.** `16:14:03+07:00` is readable at a glance; `09:14:03Z` forces timezone
arithmetic to answer "was this this morning?".

### 6.3 Lock file — mutual exclusion and crash detection

Revision 1 claimed "atomic write-and-rename is sufficient and no locking is needed." That prevents
a *torn file*; it does not prevent two *processes* from both reading a stale stamp, both deciding
to refresh, and both invoking `workspace-pull` against the same repos — the `index.lock` contention
§ 4 exists to avoid.

**Claim protocol:**

1. Read the state file. If `last-attempt` is within TTL → status `fresh`, stop. (Cheap path, no
   lock taken. The overwhelmingly common case.)
2. If a lock file exists:
   - Read its **mtime**. If older than 300 seconds, a previous run died — delete it and continue to
     step 3.
   - Otherwise another session is refreshing right now → status `in-progress`, stop. **Do not
     wait.**
3. Create the lock with `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`. If this raises
   `FileExistsError`, another session won the race → status `in-progress`, stop.
4. Re-read the state file and re-check the TTL. The winner of a race may have just finished. If now
   within TTL → release the lock, status `fresh`, stop.
5. Write the state file: `last-attempt: <now>`, preserving any prior `last-success` and `result`.
6. Run the refresh.
7. Rewrite the state file with the final `result`, `reason`, and updated `last-success` on success.
8. Delete the lock — in a `finally` block, so it is released on any exception path.

**The lock file is empty.** Its mtime is the only thing read, and the filesystem maintains that for
free — so there is no format, nothing to parse, and no way for the lock itself to be malformed. A
pid or a start time inside it would be a second source for a fact `stat` already provides.

**Stale threshold is 300s** because the maximum bounded refresh is 90s + scan time (§ 8.4), and 300
leaves margin for a slow machine without letting a genuinely dead lock block a full TTL window.

A SIGKILL leaves the lock behind; the next boot sees it is stale, reclaims it, and refreshes
immediately. That is the crash-recovery path, and it is the reason step 1's TTL check is not
sufficient on its own.

### 6.4 State file write protocol

Write to a temp file in the same directory, then `os.replace()`. Atomic within a filesystem; never
leaves a half-written file for a concurrent reader.

Two writes (step 5 and step 7). The first is what makes the failure-backoff work, so it cannot be
merged into the second.

### 6.5 State file read protocol

Read `last-attempt`. **Refresh now** if any of these hold:

- The file does not exist.
- The file cannot be parsed.
- `last-attempt` is missing or not a valid ISO 8601 timestamp.
- `last-attempt` is **in the future** — the clock changed; do not wait it out.
- `now - last-attempt >= ttl`.

Every failure mode collapses to "refresh now", so a fresh workspace, a corrupted stamp and a
hand-edited file all self-heal at the cost of one extra refresh.

**Timezone handling:** `datetime.fromisoformat` on a string with an offset returns an
*offset-aware* datetime. Comparing it to a naive `datetime.now()` raises `TypeError`. Use
`datetime.now(timezone.utc)`, and treat any parse or comparison failure as "refresh now" rather
than letting it propagate (§ 8.7).

### 6.6 First-run ignore-line ordering

The state file is written before `workspace-pull` runs, but `workspace-pull` phase 3 is what
appends the `/.tmp/` ignore line. On a workspace that has never run either command, there is a
window where the file exists and is not yet ignored — and this workspace has a documented incident
of a concurrent session running a directory-wide `git add` and committing another session's work.

**Requirement:** before the first state write, ensure `/.tmp/` is present in the workspace
`.gitignore`, appending if missing. Idempotent, exact-line match, never auto-commit. Skip when the
workspace root is not a git repo.

> **Duplication, explicitly authorized.** `workspace_scan.py` has a *reader*
> (`gitignore_lines()`, `STANDARD_IGNORE_LINES`) but no writer; the append logic exists only in
> bash inside `workspace-pull` phase 3. This is a second implementation of one rule in two
> languages — the exact drift pattern that burned `parse_frontmatter` twice (§ 7). It is accepted
> here because the rule is a single exact-line append and the alternative (a shared helper called
> from bash) is disproportionate. **Mitigation:** put the Python appender next to
> `STANDARD_IGNORE_LINES` in `workspace_scan.py`, so reader and writer sit together and a future
> change to the ignore set has one obvious place to look.

---

## 7. Parser extraction

### Change

`common.py:239 parse_frontmatter` is already two steps: find the fences and collect body lines,
then parse those lines into scalars and block lists. Split at the seam that already exists.

```python
def parse_yaml_subset(lines):
    """Parse the minimal YAML subset the framework uses: `key: value` and
    `key:` + `  - item` block sequences. Not a general YAML parser."""
    # the entire existing body loop, moved verbatim

def parse_frontmatter(text):
    # unchanged fence detection, then:
    return parse_yaml_subset(body)
```

Descriptors keep using `parse_frontmatter`; the state store calls `parse_yaml_subset` directly.

### Why extraction, not a fence-optional `parse_frontmatter`

Making fences optional would **widen** a shared function and drop validation for every descriptor in
the framework. Extraction moves nothing: `parse_frontmatter` keeps its fence check, and the new
function never had one.

### Why not `.yml` and a real YAML parser

The framework is stdlib-only and there is no YAML in the stdlib. A `.yml` file would still be read
by the minimal-subset parser while its extension advertised anchors, nesting and multi-line strings
the parser does not implement.

### ⚠ Regression risk — read before touching this function

Two scars, both documented in comments inside the function:

1. **Repeated block keys.** A repeated `repos:` block must keep accumulating into the existing list.
   Resetting made the Python side and `workspace-pull`'s awk parser disagree about the declared repo
   set, and **URLs were lost silently**.
2. **`_strip_item_comment`** must keep mirroring `workspace-pull`'s awk parser. A rule applied on
   one side only produced a URL whose derived directory name matched nothing on disk, so a
   correctly-cloned repo was reported missing (S6) forever.

**Acceptance bar: a strictly behaviour-preserving move.** Change nothing inside the loop. Every
existing test passes unmodified.

**Regression tests live in two files** — `tests/test_lr_core.py` and `tests/test_workspace_scan.py`
(`TestDuplicateBlockKey`, `TestListItemComments`). Scoping "the existing frontmatter tests" to one
file misses half the bar.

**Land it as its own commit**, before the feature.

> **Reviewer note, recorded rather than resolved.** One lens argued this whole extraction is
> disproportionate — that reusing the existing `.git/lr-last-pull` bare-epoch stamp primitive would
> delete this section entirely. It was not adopted: `workspace-pull` phases 1/2/4 run whether or not
> the workspace root is a git repo, and `workspace_scan`'s S4 treats a local-only workspace as a
> supported mode, so `.git/` is not guaranteed to exist. It would also drop `last-success` and
> readability. The underlying criticism — that this takes on regression risk in a shared parser for
> one small file — is fair, and the acceptance bar above is the mitigation.

---

## 8. Preflight integration

### 8.1 Insertion point

Revision 1 described this as "between step 5 and step 6." There is no such seam. In
`preflight.py`, the agent-repo pull (`pull_repo`, line 761) and the version compare
(`compare_versions`, line 768) sit **inside one `if agent["repo"]:` block**, which has an `else`
branch (lines ~791–795) that hardcodes `skipped`/`unknown` and runs **no subprocesses**. Both
branches reconverge just before teammate detection (line ~797).

**Insert the new leg after the whole `if/else` block, before teammate detection.**

**On the no-repo branch the refresh still runs.** `--agent-dir` pointing outside any lore repo is a
real, exercised path, and the workspace can still have repos worth pulling. The agent-repo pull
being `skipped` says nothing about the workspace.

### 8.2 Workspace root resolution

`cmd_preflight` stores `--workspace` verbatim (`os.path.abspath(args.workspace)`), and
`agent-boot.md` Step 1 passes the raw session cwd. Per `docs/worktrees.md`, sessions routinely work
from `<workspace>/.worktrees/<repo>/<slug>/`.

Unresolved, the leg would run `workspace-pull` against a worktree path, find no descriptors, and
write `.tmp/lr-state/` plus a `.gitignore` edit **inside a disposable feature worktree**. Each
worktree cwd would also get its own independent state file, producing *more* refresh attempts than
the TTL intends.

**Requirement:** before doing anything, resolve the true workspace root. Walk up from
`data.workspace`; if the path contains a `.worktrees/<repo>/<slug>/` segment, the workspace root is
the parent of `.worktrees/`. Compare resolved real paths (`os.path.realpath`) — on macOS `/var` is a
symlink and logical comparison gives a false mismatch.

If no workspace root can be resolved, status `skipped`.

### 8.3 New CLI flags on `lr-core preflight`

| Flag | Default | Meaning |
|---|---|---|
| `--workspace-ttl <sec>` | `57600` (16h) | Refresh if the last attempt is older than this. `0` always refreshes. |
| `--no-workspace-refresh` | off | Skip the workspace leg entirely. |

`--fresh` bypasses **both** TTLs. `--no-pull` skips **both** legs.

Add `DEFAULT_WORKSPACE_TTL_SEC = 57600` and `WORKSPACE_LOCK_STALE_SEC = 300` next to the existing
`DEFAULT_PULL_TTL_SEC = 600` in `common.py`.

### 8.4 Subprocess bounding and process groups

`scripts/workspace-pull` is bash and must be a subprocess. Bound it with
`subprocess.run(..., timeout=90)`.

**`lr-core workspace-scan` must NOT be a subprocess.** `workspace_scan.py` is in the same package as
`preflight.py`, which already calls sibling functions in-process (`detect_engine`,
`compare_versions`). Extract the body of `cmd_workspace_scan` into a plain
`run_workspace_scan(workspace) -> dict` and call it directly. This removes an interpreter start, a
CLI re-parse, a JSON round-trip, and a second subprocess-timeout code path.

**Do not use the `timeout` / `gtimeout` binary.** GNU coreutils, absent on stock macOS/BSD.
Standing framework rule; `pull_repo` already follows it.

**Process groups — required.** `workspace-pull` forks parallel `git clone`/`git pull` jobs with `&`
and `wait`s on them. `subprocess.run(timeout=)` on expiry sends SIGKILL to **bash only**. Bash
cannot trap SIGKILL, so its `trap cleanup_signal INT TERM` never runs and its git children are
orphaned — still writing to the workspace after preflight has reported failure and moved on. That
reintroduces, through the timeout path, the exact lock contention § 4 was designed to avoid.

**Requirement:** spawn with `start_new_session=True` and, on timeout, kill the whole process group
(`os.killpg(os.getpgid(proc.pid), signal.SIGKILL)`) before returning. Use `subprocess.Popen` with an
explicit `communicate(timeout=...)` rather than `subprocess.run`, so the group kill is reachable.

Reuse `pull_repo`'s fail-fast environment:

```
GIT_TERMINAL_PROMPT=0
GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10'
```

### 8.5 Deriving results — what is actually knowable

`scripts/workspace-pull` is a terminal-facing bash script: ANSI-coloured, streamed per-repo output,
ending in a prose summary. It has **no machine-readable output mode.** Revision 1 specified
`pulled: N` and a four-value `reason` taxonomy with no way to produce either. Screen-scraping
coloured prose would create a second parser of one script's output — the drift pattern that already
cost this codebase two silent bugs.

**Derive from git directly, never from the script's output.**

**Exit code** (verified from the script header):

| Exit | Meaning | `status` | `reason` |
|---|---|---|---|
| `0` | Nothing to do, or every clone/pull succeeded | `refreshed` | — |
| `1` | One or more clone/pull failures or conflicts | `partial` | `pull-failed` |
| `2` | Invalid invocation | `failed` | `invocation` |
| timeout | Bound exceeded | `failed` | `timeout` |

**`pulled`** — before invoking the script, snapshot two things for every top-level git repo (plus
the workspace root): `git rev-parse HEAD`, and whether `git status --porcelain` is non-empty. After
the script returns, re-read `git rev-parse HEAD`.

Every repo whose HEAD changed was pulled. The dirty flag from the pre-snapshot says whether that
repo had uncommitted work at the moment we moved it. Exact, needs no output parsing. Use the
existing `common.py` `git()` helper with a short timeout (5s); these are local reads.

Dirty state is sampled **before** the pull deliberately: that is the state that existed when the
decision to pull was made, and it is the fact the user needs told. See § 8.9 for why this is
reported rather than guarded.

**`reason`** — exactly three values, one per failure the exit code can distinguish: `timeout`,
`pull-failed`, `invocation`. Nothing else is derivable.

The revision-1 values `dirty` / `network` / `auth` / `conflict` are **removed** — nothing available
can tell them apart. A `blocked` value was also considered and rejected: a non-empty `blocked_repos`
(§ 8.6) already states that fact, and a `reason` mirroring it would be the same information in two
places, able to disagree.

### 8.6 Blocked-repo probe

The motivating case for this feature is a dirty repo that cannot be fast-forwarded. **The existing
scanner does not detect this** — S1 and S12 cover only the *workspace root's* git status, and there
is no per-child dirty finding. Revision 1 assumed otherwise.

Note that a dirty child does not automatically block a pull: `--ff-only` succeeds if the incoming
changes do not touch the dirty files. So the probe runs **only on exit 1**, and only to explain a
failure that already happened.

For each top-level git repo, two local calls (existing `git()` helper, 5s bound):

- `git -C <repo> status --porcelain` → non-empty means dirty
- `git -C <repo> rev-list --count HEAD..@{u}` → non-zero means behind

A repo that is **both dirty and behind** is a blocked repo. Emit it in `blocked_repos`. Anything
that raises or returns non-zero is skipped silently — this is a diagnostic, never a gate.

This lives in the refresh leg, not in `workspace_scan`. Adding a finding to a shared component used
by `/lr:workspace-status` is a wider change than this feature needs, and would require a new S-code
plus its prose row.

### 8.9 Dirty child repos are reported, not guarded — settled

`workspace-pull` phase 4 fast-forwards every top-level child repo with **no per-child dirty check**;
only the workspace root gets one (phase 0). `--ff-only` still succeeds when a repo has uncommitted
edits, provided the incoming commits do not touch the same files — so files change under the user
while the pull reports success.

Today that only happens when a human types the command and reads the output. Automating it means it
can happen at any boot, including boots the user did not start (the launchd Keeper, or a second
session).

**Decision: do not add a dirty guard. Report instead.**

1. **A guard would fight the feature's purpose.** Dirty is the normal state of a repo being worked
   in. Guarding on it means the most-used repos are precisely the ones that stop being pulled — they
   would stay stale indefinitely while emitting the same message every morning about
   work-in-progress the user has no intention of committing.
2. **It changes shared behaviour to cover the risk only partly.** `/lr:workspace-pull` would start
   skipping repos it pulls today, for every existing caller. And the genuinely dangerous case — a
   pull landing while another session is mid-edit — is not detectable by a dirty check at all. The
   § 6.3 lock does not cover it either: that lock excludes two *refreshes* from each other, not a
   refresh from someone's editor.
3. **Reporting supplies what is actually missing.** The problem is not that a file moved; it is not
   knowing it moved. Naming the repo solves that at a fraction of the cost, and a fast-forward never
   destroys uncommitted work — in the worst case the merge refuses and git says so.

Implementation: the `dirty` flag in `pulled` (§ 8.5) plus the reporting rule in § 9.2. No change to
`workspace-pull`.

### 8.10 Clone-required short-circuit — the refresh never clones

**This leg refreshes an existing workspace. It never performs initial setup.**

Without this rule the feature has a day-one bug. A brand-new workspace has no state file, so the
refresh fires on the very first boot — and `workspace-pull` phases 1 and 2 *clone* every declared
repo. Several clones blow the 90s bound easily; the process group is then killed mid-clone (§ 8.4),
leaving partial checkouts, and the user's first ever boot reports a failure.

Raising the budget does not fix it: § 9.1 already puts worst case near 200s against a 300s
documented bound, so a first-run allowance would push it past 400s.

**Rule.** Run `run_workspace_scan()` **before** invoking `workspace-pull`. If it reports **S6**
(declared repos absent from disk), cloning is required: **do not invoke `workspace-pull`.** Set
status `setup-required`, name the missing repos, and point at `/lr:workspace-pull`. Write the state
file as normal so the TTL applies and the message does not repeat every boot.

**Why S6 and not "is there a state file".** Deleting the state file is the documented
force-a-refresh gesture (§ 6.2). Keying the short-circuit on file absence would break that gesture:
a user who deleted the stamp to force a refresh would be told to go run a command instead. The real
question is not *"is this the first run"* but *"does this need to clone"* — and the scanner already
answers exactly that.

**Two scans, deliberately.** This pre-scan decides whether to pull; the post-pull scan (§ 8.8)
decides what to report. They answer different questions, and a pre-pull scan would report S7 and
S14 findings the pull is about to resolve. The cost is negligible precisely because § 8.4 made the
scan in-process: deterministic, no network, no subprocess.

A fresh workspace is also exactly the moment a human is present and can run a command — so
deferring to them costs nothing and keeps boot fast.

### 8.7 Exception discipline — required

`cli.py:115–121` wraps the **entire** `cmd_preflight` call in one `except Exception` that returns
`emit_fatal` and **exit 2**. Per `agent-boot.md` Step 1, exit 2 means preflight failed to complete
and the executor must run the **full Manual Boot Procedure**.

So an uncaught exception anywhere in the new code does not produce a quiet workspace warning — it
routes **every boot** into manual mode. That is precisely the boot-hot-path regression § 12 warns
about.

The existing code guards against this everywhere: `pull_repo`, `_write_stamp` and `run()` all
swallow `(IOError, OSError)` deliberately.

**Acceptance bar, equal in weight to § 7's:** every new I/O call, subprocess spawn, timestamp parse
and datetime comparison in this feature must be individually guarded and must degrade to a status
value, never raise. Specifically at risk: `os.makedirs`, `os.open`, `os.replace`, the `.gitignore`
append, `datetime.fromisoformat`, and naive-vs-aware datetime subtraction (§ 6.5).

### 8.8 JSON contract

`data.workspace_refresh`:

```json
{
  "status": "partial",
  "reason": "pull-failed",
  "last_attempt": "2026-08-23T08:12:44+07:00",
  "last_success": "2026-08-22T09:03:12+07:00",
  "pulled": [
    { "repo": "lore-framework", "dirty": false },
    { "repo": "lore-agents",    "dirty": true  }
  ],
  "blocked_repos": ["lore-chronicler"],
  "findings": [
    { "id": "S8", "severity": "warn", "data": { "repo": "lore-agents", "current": "feature/x", "default": "main", "detached": false } }
  ]
}
```

`status` — what the leg did:

| Status | Meaning |
|---|---|
| `refreshed` | Ran, everything succeeded |
| `partial` | Ran, one or more repos failed — see `blocked_repos` |
| `failed` | Could not run, or timed out — see `reason` |
| `setup-required` | Declared repos are missing; cloning is needed. Not attempted — see § 8.10 |
| `fresh` | Within TTL, skipped, no network |
| `in-progress` | Another session holds the lock |
| `skipped` | No workspace root resolvable, or no descriptors found |
| `disabled` | `--no-workspace-refresh` or `--no-pull` |

`reason` accompanies `partial` and `failed` only, per § 8.5.

**One enum, not two.** Revision 2 carried both a `status` and a `result` in this object, which
disagreed on the shared value `failed` and forced every reader to check two fields to learn one
thing. `result` now lives only in the state file, where it serves a human reading the file; the JSON
contract is `status` plus an optional `reason`.

**`pulled` is a list, not a count.** § 9.2 requires naming the repos, and the per-repo `dirty` flag
carries the § 8.9 signal. The count is `len(pulled)`.

**`findings` reuses the scanner's own shape verbatim** — `{"id", "severity", "data"}`, as emitted by
`workspace_scan.build_findings` (`workspace_scan.py:666`), filtered to `severity == "warn"`.
Revision 1 invented `code` / `subject` / `message` / `fix`; those fields do not exist.

**No prose in this object.** `workspace_scan`'s own docstring states that it is "the trigger
column" and that `docs/workspace-status.md` owns "the message and fix columns." S8's real fix text
is two sentences of conditional prose, not a static string. Emitting rendered messages here would
duplicate that catalog *and* violate the script-emits-data rule: a script string that reads like a
finished message gets printed as one, and printing it looks like handling the situation, so the
executor never reaches the doc that owns the remedy.

**Non-git workspace is not `skipped`.** `workspace-pull` gates only phase 0 (root pull) and phase 3
(`.gitignore`) on the root being git-tracked; phases 1, 2 and 4 run regardless, and S4 treats a
local-only workspace as supported. The leg runs normally; only the ignore-line step (§ 6.6) and the
workspace-root HEAD snapshot are skipped.

---

## 9. Reporting — `docs/agent-boot.md`

### 9.1 Step 1 — raise the documented timeout

Step 1 currently says to give preflight "at least 180 seconds." That no longer fits. Worst case
today is already ~105s for the agent-repo leg alone (`GIT_TIMEOUT_SEC=60` for the pull, plus three
15s-bounded git calls). Adding 90s for `workspace-pull` puts the worst case near 200s.

The risk is specific and bad: it lands on exactly the boot where the feature triggers, and the
outer tool-call bound would kill preflight *before* its internal timeouts return gracefully —
producing the manual-boot fallback this feature exists to avoid provoking.

**Raise the documented minimum to 300 seconds**, and say in the release notes which number changed
and why.

### 9.2 Step 2 — the reporting bullet

Add one bullet, in sequence with the other `data.*` handlers:

- **`data.workspace_refresh`** —
  - `fresh`, `in-progress`, `skipped`, `disabled` → **say nothing.**
  - `refreshed` with `pulled` empty and no findings → **say nothing.**
  - `refreshed` with `pulled` non-empty → one line **naming the repos**, not just a count.
  - Any pulled repo with `dirty: true` → say on that line that it had uncommitted changes when it
    was updated. No remedy is offered: this is a notification, not a problem to fix.
  - `partial` or `failed` → one line naming the `reason`, plus any `blocked_repos`, plus the
    remedy command.
  - `setup-required` → one line naming the missing repos and `/lr:workspace-pull`. This is the one
    status that asks the user to act.
  - Each entry in `findings` → one line, rendered through the **same message/fix catalog
    `/lr:workspace-status` uses** (`docs/workspace-status.md`). Do not invent wording here.

**Name the repos, don't just count them.** A silent automatic fast-forward of a repo another
session has open is a surprise this workspace has already been bitten by in a related form. The
repo names are the difference between an audit trail and a mystery.

**The dirty note is informational and must not read as a warning.** Working in a dirty repo is
normal, and phrasing that implies the user should clean it up would fire almost every day and be
tuned out — taking the genuine signals in this same block with it. Per § 8.9 the whole point of
reporting is that the user learns a file moved, not that they are asked to do anything.

The bias is otherwise silence. A refresh that finds nothing must be invisible, or the signal is
trained away within a week.

**Never fatal.** Every outcome continues to Step 3.

### 9.3 Placement warning

`agent-boot.md` is long enough that executors page it, and location decides whether an instruction
runs — three rewrites of wording changed nothing where relocating the same text did.

Put this bullet **inside the existing Step 2 bullet list**, in sequence with its siblings. Not a
trailing note, not an appendix, not a fractional step number — a fractional step reads as an
optional aside and gets skipped.

---

## 10. Test plan

**Parser extraction (regression bar)**
- Every existing test in **both** `tests/test_lr_core.py` and `tests/test_workspace_scan.py` passes
  unmodified — including `TestDuplicateBlockKey` and `TestListItemComments`.
- New: `parse_yaml_subset` parses a fence-free file with leading `#` comments.

**State store**
- Missing / unparseable / malformed `last-attempt` → refresh.
- `last-attempt` in the future → refresh.
- Offset-aware vs naive comparison does not raise.
- Age just under TTL → skip. Just over → refresh.
- Write is atomic: no partial file observable.
- A prior `last-success` survives a later failed run.

**Lock**
- Two concurrent claims: exactly one proceeds, the other reports `in-progress`.
- A lock older than 300s is reclaimed and the refresh proceeds.
- A lock younger than 300s blocks and does **not** wait.
- The lock is released on the exception path, not only on success.
- SIGKILL mid-refresh → next run reclaims and refreshes immediately (**not** silent for 16h).
- The lock file is empty and its age is read from mtime — a lock with unexpected contents is still
  honoured, never parsed.

**Preflight**
- `--no-workspace-refresh` → `disabled`, no subprocess spawned.
- `--no-pull` → both legs disabled. `--fresh` → both TTLs bypassed.
- `--workspace-ttl 0` → always refreshes.
- Timeout → `failed` / `timeout`, **process group killed**, exit code unchanged, boot proceeds.
- Non-git workspace → leg runs, ignore-line step skipped.
- Declared repo missing from disk → `setup-required`, **`workspace-pull` is never invoked**, missing
  repos named.
- State file deleted but all declared repos present → a normal refresh, **not** `setup-required`.
  This is the documented force-refresh gesture and must not be broken.
- Agent dir outside any lore repo (`else` branch) → leg still runs.
- cwd inside `.worktrees/<repo>/<slug>/` → resolves to the real workspace root; no state file is
  written inside the worktree.
- **Exception discipline:** simulate a read-only `.tmp/`, a full disk, and a permissions error on
  `.gitignore`. Preflight must exit 0 with a status value, never exit 2.

**Pull derivation and dirty reporting**
- A repo whose HEAD advanced appears in `pulled`; one whose HEAD did not, does not.
- A repo dirty *before* the pull and advanced by it carries `dirty: true`.
- A repo made dirty only *by* other activity after the pre-snapshot does **not** retroactively
  change its flag — the snapshot is the record.
- A repo that is dirty but was **not** advanced does not appear in `pulled` at all.

**Lifecycle (real engine, on request)**
- Boot on a stale workspace surfaces exactly one refresh line naming repos.
- A dirty repo that gets fast-forwarded is named, and the line does not ask the user to fix it.
- Boot within TTL is silent.
- Boot with a dirty repo blocking a pull names the repo and its fix.

### Evidence discipline

Every new test must be shown **red against the previous release tag and green against HEAD**, in a
detached worktree via `LR_FRAMEWORK_DIR`. A green suite written by the author of the change is a
self-report until that is done.

Do not assert against prose strings copied out of a doc — that proves only that the doc still says
what its author wrote. Assert against the identifier's independent source.

---

## 11. Build order

1. **Parser extraction** — `common.py`. Own commit. Existing tests green in both test files.
2. **State store + lock** — read/write helpers, atomic write, `O_EXCL` claim, stale reclaim,
   ignore-line guard. Unit tests.
3. **`run_workspace_scan()` extraction** — pull the body out of `cmd_workspace_scan` so it is
   callable in-process. Behaviour-preserving; `lr-core workspace-scan` output must not change.
4. **Preflight leg** — flags, insertion point, workspace-root resolution, process-group bounding,
   HEAD-snapshot derivation, blocked-repo probe, JSON contract.
5. **`cmd_preflight` docstring** — its numbered steps **are** the normative fallback procedure
   (`agent-boot.md`'s Manual Boot Procedure sends readers straight to it). Adding a runtime step
   without updating it leaves the literate spec lying about what the script does. Decide explicitly
   whether the new step renumbers the existing seven or is appended.
6. **`agent-boot.md`** — Step 1 timeout figure, Step 2 bullet placed inline.
7. **Ship** — see § 12.

Step 1 must land alone. Steps 2–4 can be reviewed together.

---

## 12. Ship checklist

Touches `scripts/` and changes `agent-boot.md` runtime behaviour → **cache-affecting**.

- [ ] `VERSION` → `42`
- [ ] `versioning-release-types.md` — new entry: kind, scope, **cache-affecting: yes**
- [ ] Clear Plugin Cache footer in the release notes, **hoisted near the top**
- [ ] All four version-bearing manifests → `1.42.0`:
      `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (`lr` entry),
      `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json`
- [ ] `/lr:check` #19 passes
- [ ] Release notes state the `agent-boot.md` Step 1 timeout change explicitly (180s → 300s)
- [ ] Tag at push time — check the tag list, not just `git log`
- [ ] Re-audit the release notes' claims about themselves as the **last** pre-push step
- [ ] Every gate named `passed`, `waived`, or `did not run`

### Gate recommendation

Both expensive gates are on-request since 2026-08-22, so this is the user's call. State the risk
plainly when deciding:

**This change lands in the boot hot path, and § 8.7 shows exactly how a small mistake there becomes
a total boot regression** — one uncaught exception turns every boot into a manual boot. That is the
same surface where v40 shipped with both gates deferred and carried five defects to users, four of
them a single shape that had been silently degrading real boots since v38.

If the gates are skipped, the ship record says `did not run`, and what remains untested is said out
loud in one line.

---

## 13. Open questions

1. **Should `/lr:pull-lore` also reset the workspace stamp?** Leaning no — it is documented as
   *agent-repo* refresh, and widening it silently changes an existing command.
2. **Should `workspace-pull` become TTL-aware?** Would remove the redundant agent-repo pull in § 4.
   Deferred: changes a shared script for no user-visible gain.
3. **Is 16 hours right?** A judgement call, not a measurement. `--workspace-ttl` makes it adjustable
   without a release, so revisit from real use.
### Closed

- **Per-child dirty guard in phase 4** — closed 2026-08-23. Decided: report, do not guard. See
  § 8.9 for the reasoning and § 9.2 for the reporting rule.
- **Is 90s enough for a first-run clone?** — closed 2026-08-23. Wrong question: the refresh never
  clones. A workspace with missing declared repos short-circuits to `setup-required` and defers to
  the user. 90s bounds a pull-only run, which is the only run this leg performs. See § 8.10.
