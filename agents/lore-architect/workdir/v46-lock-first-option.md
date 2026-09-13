# V46 simplification option — short repository write locks

**Status:** proposal following the user's concern about session-worktree complexity. No production
behavior changed. The worktree design and prototype remain an evaluated alternative, not evidence
for this lock-based option. “Logs” in the user's message is provisionally interpreted as “locks.”

## Essence

Keep the existing checkout paths. Serialize each repository's write batches, including finalization,
with one common-directory writer lease. Concurrent conversations and read-only reasoning continue.
Different repositories can have independent writers. We deliberately serialize writes within a repo.

A batch is a complete small edit or the entire reflect → merge → summarize → commit/publication
operation. It is not one file-system syscall. Acquire before re-reading inputs and writing, not just
before `git add`. Re-read affected files after acquisition so a waiting session cannot overwrite a
newer edit with a replacement calculated from old context.

## The necessary tradeoff

A short lock cannot safely release ownership while leaving a private draft dirty in the shared
checkout. Current standalone merge and summarize explicitly promise not to commit. Three choices:

1. Commit each completed batch locally before releasing ownership; push remains a separate policy.
2. Retain ownership until those uncommitted edits are finalized, potentially blocking other writers
   for the rest of the conversation.
3. Isolate unfinished work outside the checkout, bringing back a patch/worktree adoption workflow.

**Recommendation for the simpler lock-based design: option 1.** It changes standalone writing
semantics and must be an explicit product decision before integration. This proposal does not itself
authorize arbitrary unpublished history to be pushed or change installed standalone skills.

## Batch protocol

1. Claim repository ownership with an opaque operation token. A busy repo gives a named owner/busy
   result; callers defer or retry later with a bound. Do not wait indefinitely inside a boot.
2. Verify branch/upstream and Git operation state. Refuse pre-existing staged or dirty work whose
   ownership cannot be established. No automatic stash, discard, or sweep into the new batch.
3. Re-read inputs under ownership. Write only the recorded paths. Delegated workers inherit the
   host's operation, edit disjoint assigned paths, and do not acquire another lease or run Git.
4. Commit that exact completed batch locally with literal pathspecs. Verify exact commit identity
   and scope under the same ownership. No rollback if verification fails; preserve and report.
5. Release only after the batch is committed and the expected checkout state is verified. A failed
   or interrupted batch keeps a recovery-required record and prevents unrelated writers proceeding.
6. Finalize holds ownership for its whole writing phase and bounded publication attempt. Other
   framework pulls/merges/updates must use the same ownership protocol. Explicit target/ref pushes,
   no force, bounded retries, and owning-agent semantic reconciliation remain required.

A local lock does not prevent another machine moving the remote. Rejected pushes still need
fetch/reconciliation or a clear pending-publication outcome. Keep failed commits; do not reset
history to erase an ahead count. An ordinary boot may report that local publication is pending;
its freshness cannot be guaranteed until remote and local history are reconciled.

## Publication ownership

Local commits prevent partial dirty work from being accidentally captured, but do not make a later
push selective: pushing a tip publishes all unpublished ancestors. Therefore finalization may
publish earlier **completed, explicitly publishable** batches in that repo, even from another
session. Each batch keeps its own commit message/attribution.

Work not approved for eventual shared publication must remain outside the shared branch. Pre-existing
unpushed commits are not automatically considered publishable. The first lock-based publication
must inspect/adopt them deliberately or stop. Repository-scoped completion and publishability are
required policy, not properties that can be inferred from a clean `git status`.

## Lock lifetime across model calls

A shell command that obtains an OS lock and then exits does not protect later model tool calls.
The owner must persist for the complete batch. A small helper can keep a durable owner record whose
claim/release operations are serialized with a short kernel lock. Release requires its exact token.
The record is a lease only in the ownership sense; **no time-based expiry or automatic stealing**.

A crash or unavailable owner identity becomes recovery-required. Reclaim requires proving the old
writer/children have stopped and inspecting the remaining Git state. Age alone proves neither.
This trades automatic recovery for a smaller implementation. Do not borrow the workspace-refresh
lock's mtime-based deletion scheme for a model-driven writing batch.

Readers must not load partial edits or conflict-marked role/context files during a write batch.
A boot encountering ownership in progress defers loading those mutable files or uses an explicitly
identified committed snapshot. All automatic Git mutations obey the same repo lease. This is a
cooperative framework protocol, not protection against arbitrary external editors or old plugins.

## Complexity and remaining validation

This removes per-session branch/worktree allocation, directory rebinding, worktree cleanup and
cross-worktree status. It retains a modest owner/recovery record, exact write-set commit handling,
publication outcomes, remote reconciliation and the need to update every writing entry point.

Before choosing it, prove with controlled local processes:

- Two batches updating the same file serialize and re-read, preserving both updates.
- A standalone batch commits before ownership is released, but never pushes on its own.
- Another host cannot release the lease or write through a stale token.
- Owner death midway through writing leaves data and a visible blocked state; no lease stealing.
- Boot/workspace refresh cannot mutate or load conflict-marked files during the batch.
- A remote race and a failed push preserve committed work with truthful status.
- An unrelated historical commit cannot ride along without an explicit publishability decision.

No test counts from the worktree prototype apply to this option. A full implementation decision
must accept both serialization and the standalone-local-commit/publication policy above.
