# V46 exploration — boot-bound session worktrees

**Superseded where different:** [User-selected session worktree decision](v46-session-worktree-decision.md),
including layout, native-engine independence and local Lore integration policy.

**Status:** recommended lifecycle simplification, explored at the user's request. Not installed or
claimed production-ready. This refines the worktree direction; it does not silently adopt the
standalone-local-commit policy in `v46-lock-first-option.md`.

## Essence

One conversation has one durable Lore session UUID. For every Lore repository booted or attached
in that conversation, Python creates or recovers one worktree. All agents from that repository
share this session's worktree; independent conversations get different ones. Create it before
loading role/context, not on the first write. A read-only conversation may leave an unused worktree;
that small filesystem cost buys a uniform lifecycle without late path switching.

Use the existing convention:

```
.worktrees/lore-framework-dev/<session-uuid>/
.worktrees/lore-agents/<same-session-uuid>/
```

These are Git worktrees. An agent's existing `agents/<name>/workdir/` remains an ordinary directory
inside its worktree. Reuse `.worktrees` rather than introducing a confusingly similar `.workdir`
root. Git shares committed objects, but each checkout has its own files and index; disk usage is
not zero and grows with checked-out files, especially large workdir artifacts.

## Python owns lifecycle, not conversation memory

1. **Ensure session:** resolve a reliable native conversation key, look up/create its durable UUID
   under a serialized registry operation, and write the record atomically.
2. **Ensure repo:** canonicalize repository identity using Git's common directory. Under a creation
   lock, return the existing binding or create exactly one branch/worktree. Verify on-disk Git
   registration, branch and path; never equate a folder's existence with successful initialization.
3. **Boot:** return role/context paths inside the bound worktree. The host and attached agents load
   those files from the outset. Delegated workers inherit the host session identity explicitly;
   they do not create another session because they have a separate process/transcript.
4. **Checkpoint/publication:** retain the same branch/worktree, commit the selected ready batch,
   reconcile and publish through the deterministic helper. Store per-repo outcomes durably.
5. **Continue:** further edits and later finalizations reuse that worktree. Successful publication
   is a checkpoint, not termination of the conversation or permission to remove the worktree.
6. **Close explicitly:** remove a worktree only after verifying delivered history, no dirty/untracked
   work and no active operation. Conversation inactivity or a successful finalize is insufficient.

A process crash during creation may leave an intended record, branch or worktree without all three.
Re-entry inspects/reconciles that exact intention under the creation lock. It never deletes unknown
work or allocates another worktree merely because the last call lacked a success response.

## Stable identity across context loss

The registry key is an engine-owned conversation identifier, not “the most recently modified log,”
current working directory, agent name or the model's recollection. Repeated boots in the same
conversation recover the same UUID without the model remembering it. Independent forks get new
bindings by default; an explicit same-session worker/handoff inherits the existing binding.

This runtime exposes `CODEX_THREAD_ID` (presence verified, not a cross-engine guarantee). The
current framework's `preflight.py` does not bind worktrees. `summarize.md` currently generates a
fresh UUID at summarization time; `session-takeover` can fall back to the most recent log. That
heuristic is unsuitable for selecting a writable checkout. Claude/Cursor identity adapters still
need verification. If reliable identity is unavailable, require an explicit resume/session token;
do not guess another conversation's worktree.

Keep two logical identities:

- **session_uuid:** stable conversation/worktree identity.
- **checkpoint_uuid:** a particular finalize/summary/publication attempt; retry reuses it, a new
  finalization gets a new one.

Preserve the existing summary `uuid` as checkpoint identity and add `session_uuid` as a correlation
field. Otherwise repeated finalizations can overwrite summaries or misidentify completed deliveries.
A checkpoint has one outcome per repo; one successful repo does not erase another's pending result.
No cross-repository atomic transaction is promised.

## What the model still does

The model interprets knowledge, decides which content is ready, and reconciles eligible semantic
conflicts. Python supplies every directory, worktree/ref identity, checkpoint state and publication
result. Writing skills resolve the binding on each entry rather than relying on a remembered path.

To survive compaction, engine adapters should re-inject the session binding and set the task/tool
working directory to the isolated context where supported. The durable registry is authoritative.
A child shell's `cd` cannot change the parent agent's default working directory. A file naming the
correct path also cannot stop a raw editor tool from writing elsewhere.

**Residual boundary:** deterministic Git helpers protect the operations routed through them. To
prevent *all* accidental primary writes, use engine tool-path guards or a sandbox making primary
checkouts read-only for session writers, where supported. Primary refresh then runs through a
separate authorized helper. Without such enforcement, direct file edits remain a cooperative rule
that must be tested across engines; do not sell a JSON registry as an OS-level write barrier.

## Publishing without bypassing isolation

Boot and ordinary edits never publish. Finalize remains an explicit publication checkpoint, and
an explicit mid-session share uses the same helper. Neither operation writes directly into the
primary checkout. The helper publishes to the recorded branch; primary later fast-forwards safely.
Refresh failure due to existing primary WIP is separate from verified remote delivery.

A push publishes all unpublished ancestors. Therefore neither “share this one file” nor a narrow
pathspec commit can safely hide earlier private checkpoint commits. The simple first version
publishes an explicitly reviewed outgoing batch/history; mixed private/ready history stops for a
more deliberate export. Do not introduce automatic all-files commits or promise arbitrary partial
publication. Unfinished work can remain private between checkpoints, and cleanup must preserve it.

All shared-repository refreshes use their own bounded Git operation protection. Session worktrees
are not automatically pulled by boot/workspace refresh; the publisher integrates remote changes at
checkpoints. A long-lived session reads current files again after integration. A fresh conflict
resolver boots identity from a clean pre-merge snapshot, not conflict-marked role/context files.

## Evidence and implementation cost

A sequential real-Git fixture probe verified:

- repeated boot/another agent in the same repo reuses one worktree;
- two repositories bind two worktrees under the same session UUID;
- two commits/publications succeed from the same worktree;
- primary HEAD stays unchanged until an explicit refresh;
- primary fast-forwards to the second publication afterward.

The registry in that probe was in memory; it does not prove durable initialization, crash recovery,
concurrent ensure calls or engine context restoration. Those are the next deterministic/integration
tests, not already-passed gates.

The previous `v46-prototype/publish.py` allocates a new random ID per `begin` and treats `published`
as terminal. Its 41 tests prove useful Git mechanics but do not prove this revised multi-checkpoint
lifecycle. Refactor the storage model into a durable session binding plus publication attempts,
then test repeated boot, simultaneous ensure, restart after each creation step, repeated finalize,
failed retry, cross-repo partial success, inherited worker identity, independent forks and compaction.

**Assessment:** moderate deterministic lifecycle work, with engine binding/enforcement the main
integration risk. Eager boot binding is simpler than lazy first-write routing; reusing one worktree
is simpler than per-operation worktrees; explicit close is simpler and safer than automatic session
end detection. This is the preferred direction over a lock-only design if standalone edits should
remain uncommitted and conversations must not block each other's writing.
