# V46 — Safe Concurrent Lore Publication

**Design amendment:** [Session worktree decision](v46-session-worktree-decision.md) supersedes
this draft on eager boot binding, session-first `.worktree` layout, engine-independent lifecycle,
and required controlled local Lore integration. The prototype and invariants below have not yet
been updated to that decision; their validation is not evidence for the amended protocol.

**Status: revised design with an executable reference prototype; production integration not yet performed.**
**Updated:** 2026-09-13. **Scope:** one v46 release, no A/B/C release split.

This replaces the prior 1,663-line draft, including its rollback rule and global stranded marker.
The earlier design and seven reviews remain in Git history at `ebaed0f`; they are not additional
instructions to execute. The latest review is preserved in
[v46-prototype/review-input.md](v46-prototype/review-input.md).

## 1. Decision

**Each writing session gets its own Git worktree before its first write.** All of that session's
Lore edits, reflection, merge, summaries and publication use that worktree. The shared primary
checkout is a read/refresh view. Publication never commits, merges, resets or stages in it.

This is the prerequisite for the safety claims below, not an optimization. A short publication
lock cannot protect concurrent edits made before publication. Narrow staging protects unrelated
paths but cannot separate two writers' versions of the same file in one checkout.

A small deterministic helper in the existing `lr-core` runtime owns Git and operation records.
The model supplies the explicit write-set, commit message and semantic conflict resolutions.
No second Git state machine lives in executable prose. The helper is a new command surface inside
`lr-core`, not a new user-facing skill.

The change is larger than replacing finalize Phase 4 alone, but substantially simpler than trying
to make shared-index commits, rollback and warning cleanup behave as a transaction.

### Why this is different from the rejected sidecar publisher

The rejected design published copies of files while leaving the originals dirty in the primary
checkout, creating permanent pull collisions. Here **the original edits are made in the session
worktree from the start**; the primary checkout never receives them. After publication it can
fast-forward normally. The acceptance test must publish, pull the primary checkout, and begin the
next writing session. Testing the push alone is insufficient.

Do not retrofit this by copying arbitrary dirty primary files at finalize time. Existing dirty
work is a separate adoption/recovery case (§ 8).

## 2. Invariants

1. **One writer per session worktree.** Independent sessions never share an index or authoring
   directory. Host and delegated guests may share one session worktree only with disjoint file
   ownership; the host alone performs Git operations. Delegation does not create another publisher.
2. **Publication does not mutate primary checkout files, index or branch.** No rollback of its
   HEAD, including on failed publication. The common object database, private refs and operation
   records are shared intentionally.
3. **Commit an explicit write-set; push an explicit commit to an explicit destination.** A path is
   literal, repository-relative, and denotes a file or symlink, never a directory or glob. A narrow
   commit does not authorize publishing arbitrary existing local ancestry.
4. **Only an owning executor reconciles its operation's conflicted Lore.** Automatic resolution
   is limited to recorded paths under `agents/<owner>/{lore/**,lore-context.md,role.md}`. Other
   conflicts remain recoverable in the private worktree for an owning-agent or human handoff.
5. **Failed publication preserves its snapshot and records an outcome.** It never resets a
   branch, discards dirty work, deletes a Git lock, or repeats a snapshot commit on a simple retry.
   Unpublished history on a private session branch does not block primary boot pulls.
6. **Unknown is not success or recovery.** Missing acknowledgments, unreadable records, changed
   branch identity, interrupted transitions and unavailable Git evidence preserve the record and
   data. Status readers never delete records or use a clean primary checkout as proof of delivery.

The old invariant “a blocked attempt must leave no additional local commit” is withdrawn. It was a
proxy for keeping the shared checkout pullable and led to unsafe reset operations. Isolation
provides that property directly while retaining committed recovery data.

## 3. Session routing and lifecycle

The helper provides `begin`, `commit`, `publish`, `resume`, `status` and explicit `close` operations.
These are implementation API responsibilities; final CLI spelling is fixed when integrated into
`lr-core`. `begin` returns a concrete agent-directory mapping, session ID, branch and worktree.

### Begin before writing

- Resolve the primary repository's own Git root and existing upstream remote/full branch ref.
  Resolve one target URL deliberately; never infer publication from bare `git push` or silently
  create/change an upstream. Multiple candidate targets require an explicit choice.
- Fetch the destination to a private per-session ref and create the session worktree from its
  exact commit. **Do not branch from unpublished primary HEAD.** Existing unpushed primary commits
  must not enter a new session's publication as ancestors.
- Place worktrees under `<workspace>/.worktrees/<repo>/lore-<session-id>/`, with a unique private
  branch. Random IDs, not timestamps or model-selected agent names, prevent collisions.
- For an offline start, the production helper may use a resolvable cached upstream commit, clearly
  reporting that freshness is unknown. No upstream/cached base permits read-only boot; local-only
  authoring requires an explicit local-only session, with no automatic publication destination.
  Never fall back from an ambiguous destination to publishing primary HEAD.
- Return the session mapping to the host. Every subsequent write path uses it, including direct
  mid-session workdir/role edits and standalone reflect/merge/summarize. The primary path must not
  remain in a guest's write brief after a session has been bound.
- Read-only consults/searches do not allocate writer worktrees. A writer begins lazily, but before
  its first write; allocation itself never implies permission to finalize or publish.
- After lazy binding, re-read the role, Lore context and affected target files from the returned
  worktree before authoring. They may differ from what the host read in primary at boot. Never
  apply a whole-file replacement computed from an older primary snapshot to the new remote base.

### Boot and refresh inside a bound session

Boot/attach/merge-resolver subagents receive the **session agent directory**, the shared session ID,
and `--no-pull`. They load Lore from that worktree. They do not discover another agent directory by
name, create their own worktree, or trigger workspace refresh. Remove both merge's boot auto-pull
and its separate defensive preflight refresh for a bound session. Integration with the latest
remote happens once, under the host publisher, after snapshotting the write-set.

Ordinary read-only boots may continue to refresh primary checkouts with bounded, noninteractive,
file-granular `--ff-only` pulls. Explicitly disable inherited `merge.autoStash` and `rebase.autoStash`
in those commands. No automatic scan/refresh iterates private session worktrees.

### Ownership and interruption

Use a kernel-owned, nonblocking per-session lock while executing helper commands. Never unlink a
lock file to take ownership; process exit releases the OS lock. Persist an operation phase before
every mutating Git transition, so a killed helper leaves an observable incomplete operation.

Between commands the worktree belongs to the host session. Subagents may edit only assigned paths;
all Git calls return to the host helper. Beginning a second host command against that session
requires its existing opaque session identity, not just an agent name.

These are cooperative framework guarantees. Arbitrary external Git commands, plugins ignoring the
binding, and external edits to the same private files are outside the writer protocol. Detect
unexpected HEAD/branch/index changes and stop without resetting them. Do not claim an advisory
lock prevents arbitrary external writes. Validate the binding at each writing entry point.

## 4. Snapshot and publication

### Commit

1. Verify worktree/repository/branch identity and expected HEAD. Refuse unexpected merge, rebase,
   cherry-pick, index changes or another active command. Detect rebase/sequencer directories, not
   only `REBASE_HEAD`, which is not a complete operation detector.
2. Collect explicit authored paths: retained merge handoffs, actually deleted reflections,
   unmerged reflections, session-authored edits outside merge, and summary paths. Add `Reflections
   removed: <paths|None.>` to the handoff. Validate the entire set before staging anything.
3. Record `committing` with expected parent and write-set, then use deletion-aware literal
   pathspec staging and commit. Preserve Git's file modes, symlinks, deletions, signing and hooks.
4. Record the exact snapshot commit after verifying its parent and paths. A failed verification
   means unknown state and **no push**, never a reset. A crash after Git commits but before the
   record advances is recoverable from the private branch; do not silently adopt an unknown commit.
5. A genuine empty snapshot is a no-op. An existing pending snapshot still needs publication;
   “nothing newly staged” does not acknowledge earlier delivery.

Additional uncommitted work blocks publication of that frozen operation until deliberately handled;
it is not silently included or discarded. A retry reuses the snapshot. A subsequent authoring batch
uses another operation/session after the current one is completed or explicitly handed off.

### Publish

Use the recorded snapshot SHA and resolved target URL plus full destination ref. A bare push,
`push.default`, `remote.*.push`, `pushRemote` and a different `pushurl` must not change the destination.
Require a normal non-force fast-forward update. Fetch into a private ref; avoid shared FETCH_HEAD.

For each invocation, permit at most three push attempts in `merge-retry` mode and one in `no-merge`
mode. Persist the phase before pushing. Fetch the exact destination afterward and verify that it
contains the attempted commit; this also recovers a push whose acknowledgment was lost. If that
verification is unavailable, record `unknown`, retaining the commit. A successful network exit
alone must not clear an unrelated operation or claim a different branch received the snapshot.

On rejection, inspect fresh destination ancestry before merging:

- If it already contains the snapshot, record delivered.
- If the destination has not advanced beyond an ancestor of the snapshot, another refusal such as
  a hook or policy caused rejection. Record it; merging will not help.
- If history was rewritten relative to the recorded session base, stop for deliberate recovery.
- Otherwise `merge-retry` may merge that exact remote commit in the private worktree and retry.
  `no-merge` stops and preserves the snapshot.

A clean merge may add a merge commit on the private branch. Report it. The primary branch and
index remain untouched whether publication succeeds or fails. Finalize reports one authored
snapshot per touched repo, with any integration merge commits separately; the old one-commit-total
wording must change. Partial publication across repos keeps successful deliveries and reports each
pending repo independently. Never roll back success to restore symmetry.

### Semantic conflicts

List and classify **all** conflicted paths before any resolution. Snapshot the merge parents and
index entries for nonconflicted paths. Delegate only eligible paths to their owning executors,
passing session paths and `--no-pull`. Reuse an owning executor booted before the Git merge where
possible. A fresh resolver loads identity/context from the recorded pre-merge commit through a
read-only snapshot; conflict-marked `role.md` or `lore-context.md` is resolution input, never its
boot authority. Give it both committed sides and the exact writable target paths. A guest may
return file edits, never a Git commit or push.
When the engine cannot provide an owning executor, return a named handoff instead of silently
resolving the guest's Lore in the host context.

Before the helper stages resolutions and completes the merge, verify unchanged expected HEAD,
MERGE_HEAD, nonconflicted index entries, and no unrelated working-tree changes. Restrict staging
to recorded resolution paths. If the knowledge-graph check needs edits elsewhere, explicitly expand
and validate the resolution write-set before making them; never broaden it by scanning dirty files.

Foreign conflicts, unresolved questions and interrupted resolutions stay in the private worktree.
Both original inputs remain in its parent commits. There is no automatic rollback and no need to
abort another session's merge. Repeated status/retry requests do not create more commits.

## 5. Durable outcomes and status

Replace the single global YAML marker with **one JSON record per session operation** under
`<git-common-dir>/lr-publish/<session-id>.json`. These are runtime records, never committed. The
common location makes every checkout able to discover them; it does not make their contents
branch-global. Keep records scoped to the session branch, worktree and destination.

Record at least: schema version, opaque operation ID, canonical/worktree identity, private branch,
base SHA, expected HEAD, payload SHA when available, target URL/ref, phase/outcome, reason,
conflicted paths/expected merge parents when applicable, last verified destination SHA/time, and
first failure time once an actual failure occurs. No retry counter is needed. Store credentials
outside records and redact credential-bearing URLs from status output.

Use unique temporary files, flush/fsync, atomic replacement and directory fsync. A fixed `.tmp`
filename borrowed from the separately locked refresh writer is not safe here. The session lock
serializes record updates. The first-failure time is stable through retries; updated blocking paths
and reasons are written even when their reason category is unchanged.

| State | Meaning and next action |
|---|---|
| active | Bound writing session; not evidence of publication or a fault. Display separately from pending delivery. |
| committing / publishing / merging | Operation underway while its command lock is held; if the owner ended, interruption requiring resume/inspection. |
| pending | Known committed snapshot not yet verified delivered; retry this snapshot to the recorded target. |
| conflict | Private merge awaiting eligible semantic resolution or human handoff; show exact paths and owning agents. |
| unknown | Evidence unavailable or identity changed; preserve data and record, inspect/resume deliberately. |
| published | This operation's snapshot was verified reachable from its destination. Delivery acknowledgment, not a promise that remote history can never be rewritten. |

`status` is read-only: no network, file removal, or clearing “foreign” branches. It never infers
recovery from primary `ahead == 0`, a missing primary MERGE_HEAD or a branch mismatch. Unknown
schemas and malformed records produce a named unavailable-state item and survive for inspection.
Missing worktrees are recovery issues while their private branch/commit may still preserve data.

An explicit `resume` fetches the recorded target and acknowledges the **same** operation only when
its snapshot is reachable there. Otherwise it retries only after validating identity and any merge
state. It must not bless an unexpected tip merely because the old parent is an ancestor. Records
for other branches/sessions are neither overwritten nor acknowledged. Manual pushes become visible
through this explicit refresh; last-known status is labeled as such in between.

C4/R16 reports two independent facts: primary ahead/behind counts, and pending/interrupted session
operations. Primary ahead-only is informational; primary divergence is a warning. A blocked private
operation remains visible even when primary is completely synchronized. Do not claim every blocked
publication breaks boot. Include checkout, destination, reason, paths and age where known.

C8 uses that same reader for each being's repository, deduplicated per repository. Show repository
publication trouble separately from the being's last process outcome: it may be another session's
operation in the same repo. Add JSON fields and aggregate counts explicitly; `cmd_status` currently
has no existing not-ok total to reuse. No record is deleted by inspecting status.

`close` is explicit cleanup after verified delivery and a clean worktree, under its session lock.
Never force-remove a worktree or delete a private branch with unacknowledged commits. Retain a small
published receipt or remove that exact terminal record as part of close; do not infer cleanup from
mtime. Automated abandoned-session cleanup is out of scope.

## 6. Automatic updates and other publishers

**Keep automatic updates conservative.** They may run in a private maintenance worktree only when
primary has no unpublished local commits or dirty update targets. They use a fresh destination
base and `no-merge` publication. They do not publish primary's existing ancestry. Concurrent primary
changes after the initial gate remain outside that private branch and cannot ride along.

Check migrations against the maintenance worktree's stamp/content, not a stamp read from another
checkout. Failed publication leaves the maintenance snapshot pending. Do not claim primary was
upgraded until its bounded fast-forward/readback succeeds. A primary refresh blocked by local edits
is a separate outcome from successful remote delivery.

Unify update retry with the operation record. Existing `lr-update-pending` markers are read as
legacy hints; validate their exact branch, upstream, commit and sole-ahead condition before a retry.
Never weaken their safety predicate to force a retry. If invalid, report the record and preserve
it for explicit recovery. Do not silently migrate it into authorization to push unrelated commits.

`workspace-push` keeps its approval boundary and no-merge policy. Its approved snapshot must also
be prepared/published in a private worktree before it can claim concurrent-writer safety. Until
that routing is integrated it remains a documented legacy shared-checkout publisher, not an
invariant-compliant precedent. The user-approved workspace rescue snapshot is a separate operation;
its whole-tree capture must have exclusive workspace ownership and must never be cited as a
publication shortcut.

## 7. Standalone refresh correctness

### C5 — success TTL and failure backoff

Staleness uses `last-success`. Attempt cadence uses persisted outcome and `last-attempt`:

- Successful refresh: set both stamps, `result: ok`, failures 0.
- Failed/partial: retain last-success, set last-attempt/outcome, increment failures.
- Setup-required: retain last-success, set `result: setup-required`, failures 0. Its retry/message
  cooldown uses last-attempt and configured TTL; it is neither an imaginary refresh success nor
  an unthrottled error. It previously depended on the attempt TTL being replaced here.
- Interrupted attempt: record `in-progress` before invoking the refresh. Once its lock is no longer
  held, apply bounded failure backoff to that interrupted attempt rather than suppressing forever.

For valid failures, `delay = min(max(ttl, 0), 900 * 2**(n-1))`, with the exponent/counter clamped
**before** exponentiation. Missing/malformed/negative counters self-heal to 0; n=0 adds no delay.
`ttl <= 0` always attempts, including after failure or setup-required. Offset-aware ISO stamps stay
compatible with the current parser. Missing, malformed, naive or future timestamps never cause
permanent suppression. Missing success means due, not permission to bypass valid failure backoff.

Preserve the failure count in every write_state call, including the pre-invocation write. Bound
retry arithmetic and Git calls. Update CLI help, docstrings and manual fallback from this one rule.
A backed-off boot can remain quiet; `check` reports last-known unsuccessful refresh state when asked.

### C6 — primary workspace pull

Attempt bounded `pull --ff-only` first with inherited autostash disabled. Let Git decide whether dirty
tracked or untracked files actually collide. Only on failure classify the useful error: divergence,
dirty/untracked collision, auth/network, no upstream, interrupted Git operation or unknown. Preserve
Git's error line and report counts as last-known when fetch fails. Do not tell an offline user to
commit/stash, and do not report “up to date” merely because a count could not be obtained.

### C7 — conventions

State the six invariants once and reference them from callers. Keep examples consistent: pending
delivery does not always imply broken boot; private merge completion is an allowed whole-index
commit only under exclusive session ownership and expected-index validation. No reset, stash,
autostash, force-push or lock-file deletion is an automatic recovery action.

## 8. Existing sessions, dirty work and recovery

Installation does not move existing session files or switch primary branches. Read-only boots
continue working. New writing entry points create/reuse a bound worktree. Old sessions still
holding primary paths cannot be made safe by installing a new helper; warn once and require a
restart/rebinding before claiming the new guarantees.

For legacy dirty or unpushed primary work, provide a concrete adoption report: exact paths/commits,
known authorship and destination. Never sweep it into a new session snapshot. Same-file concurrent
edits with no ownership evidence need human reconciliation. No stash, reset or automatic copy-and-
clean of primary WIP is authorized by routine begin/finalize. This is an explicit compatibility
boundary, not an automatically solved migration.

Primary refresh and newly isolated authoring may proceed around unrelated existing dirty files,
but the reported view must distinguish primary local work from the session's remote-based snapshot.
When the user's intended input is the dirty primary version, stop at that adoption boundary rather
than silently substituting the remote version.

## 9. Production change inventory

All of this ships together when complete. The old “no new script/subcommand, no data-model change”
claim is withdrawn: there is a helper command and a versioned runtime record, though no committed
Lore schema migration. Update the actual release manifests only when producing the release.

| Area | Required integration |
|---|---|
| `lr_core` / CLI | Session binding, helper state machine, shared outcome reader, bounded Git wrappers; recovery and explicit cleanup |
| boot / preflight / attach | Lazy writer binding, exact agent directory mapping; bound-session no-pull/no-refresh behavior |
| reflect / transcript reflection / merge / summarize / groom / direct authoring convention | Bind before first write; propagate session paths and retained write-set; remove bound merge's second auto-pull |
| finalize / conflict resolution | Host-owned Git, helper results, semantic-only owner handoffs, one publisher per touched repo |
| update / version-check | Maintenance worktree and conservative gates; legacy pending-record compatibility; verified primary refresh wording |
| workspace-push / workspace-init | Preserve approval scope, isolate approved publication, explicit rescue-snapshot exception |
| repo scan / findings catalog / check | R16 primary facts plus independent operation findings, shared reader, no destructive cleanup |
| `lrb status` | Shared-reader results and separate repository-publication health in text/JSON |
| workspace refresh / workspace-pull | Outcome-keyed backoff, setup-required persistence, file-granular pulls, error classification |
| engine profiles / conventions / worktrees | Bound-session routing and semantic-resolution capability differences; no shared-checkout safety overclaim |

## 10. Validation and release boundary

The executable prototype and test instructions are in [v46-prototype/README.md](v46-prototype/README.md).
It proves the central Git mechanism against real local repositories. It is **not** the installed
helper or evidence that engine prompts already route every write correctly.

Acceptance groups:

1. **Isolation:** two sessions edit the same topic; unrelated primary staged work; another session
   commits on primary during publication; external private tip/index changes are refused without
   reset. Verify primary files/index/ref before and after both successful and blocked publication.
2. **Delivery:** exact destination despite push configuration; nonconflicting retry; semantic
   conflict; foreign handoff; no-merge update; signing/hooks/deletion/symlink/mode fidelity; three
   actual rejected pushes; lost acknowledgment and resumed delivery.
3. **Recovery:** process death before/after commit, merge, push, receipt write and close; missing
   worktree; unsupported records; concurrent commands; Git index lock; unavailable Git/network;
   resume never adopts unowned commits or deletes failure evidence.
4. **Visibility:** primary ahead=0 with blocked private publication; cross-branch readers; one
   success beside another failure; status does not mutate records; last-known vs freshly verified
   delivery; Keeper text/JSON distinguishes process health from repository publication health.
5. **Refresh:** success age, partial/failure exponential backoff, no success yet, setup-required,
   malformed/future fields, enormous counters, TTL zero, unrelated dirty file, real dirty/untracked
   collision, interrupted operations and network failures.
6. **Next use:** publish → primary pull → ordinary boot → new writing session. This is required
   to rule out the rejected sidecar failure.
7. **Engine routing:** real engine first-write binding, guest binding, standalone writing skills,
   finalization, semantic resolution, and no accidental primary edits under concurrent sessions.

Use deterministic tests for mechanics/records/scanners/JSON; real engines only for execution
fidelity and semantic judgments. A prose containment test does not establish a safety property.
For existing runtime bugs demonstrate red on v45 and green on implementation. For new APIs compare
against a deliberately broken control or the original failing Git sequence, not an ImportError
against a version where the API did not exist.

Release gates: deterministic tests and check, isolated integration/dogfood, then requested engine
and independent reviews, each recorded against a named artifact. This revision does not grant a
ship verdict or reuse the prior design reviews as code-gate evidence. Production integration must
not be described as completed while any row of § 9 still executes the legacy writer path.
