# V46 design prototype

An executable reference for [the revised design](../draft-lore-sync-hardening.md). This is **not an
installed framework command**. It validates the choice to isolate session authoring and publication
before wiring that choice into the framework's writing entry points.

## Run

From this directory, with Python 3 and Git on macOS or Linux:

```sh
python3 test_publish.py -v
python3 run_mutations.py
```

No dependencies beyond the standard library. Tests create disposable repositories with local bare
remotes; they never use the user's configured origin or launch an AI engine. The prototype itself
accepts local fixture remotes only. Successful fixtures and failed assertions both remove their
scratch repositories through unittest cleanup.

## What is implemented here

- Fresh remote-based private worktree creation with unique session branches and records.
- Literal, deletion-aware commit paths, preserved executable/symlink modes, ordinary Git hooks.
- A nonblocking kernel-owned session lock and exact worktree/branch/HEAD checks.
- Explicit commit/destination publication, bounded retries and private merges.
- Owning-agent conflict-path restrictions and verification of the nonconflicted index.
- Durable intent before Git mutation; retained snapshots and read-only per-session status.
- Explicit resume after an uncertain push, including delivery verification after lost acknowledgments.
- Conservative update gating; no automatic publication of primary's unrelated ancestry.
- An independent reference function for outcome-based refresh scheduling.

Git subprocesses have a timeout and an isolated process group; timeout kills ordinary descendants
before releasing command ownership. No operation resets the primary checkout, deletes a Git index
lock, or force-pushes. JSON writes use a unique temporary file and fsync before/after replacement.

## Validation

The current suite has **41 tests**. [test-results.txt](test-results.txt) records the latest complete
run. The final numeric-bound adjustment was then checked with all six refresh tests;
[refresh-results.txt](refresh-results.txt) records that targeted rerun. The tests cover same-file concurrent authoring, primary branch/index preservation, unexpected
private changes, exact destinations, no-merge updates, foreign conflicts with primary ahead=0,
worktree-independent status, malformed/tampered records, interrupted commit/push, Git hooks/timeouts,
three actual rejected pushes, snapshot retry, next-session usability, and refresh edge cases.

[run_mutations.py](run_mutations.py) makes five disposable broken variants and runs one targeted
test against each. A detection counts only as an assertion failure, not a syntax/import/runtime
error. [mutation-results.json](mutation-results.json) records the results. The variants remove the
exact-HEAD guard, allow unrelated index changes, remove setup-required cooldown, use an implicit
push destination, and delete another branch's operation record.

These controls establish that the chosen tests detect their intended regressions. They do not
establish full state-space coverage, production integration, or semantic correctness of LLM merges.

## Production work remains explicit

The prototype deliberately has no production CLI wiring, engine session-directory propagation,
offline/local-only session creation, legacy WIP adoption, cleanup API, legacy update-marker reader,
repo-scan/R16 integration, Keeper JSON integration, or real-engine tests. `resolve()` demonstrates
one owning agent; production orchestration must gather all owner handoffs before committing a
multi-agent resolution. The scheduling function uses numeric timestamps to isolate the algorithm;
production must preserve the framework's offset-aware ISO serialization and all state-write sites.

The revised spec inventories these integration changes. None may be treated as already shipped
because this prototype passes. A record with an interrupted unrecorded commit intentionally stops
for inspection; resume never guesses ownership from ancestry. Git signing is honored by using
ordinary commit commands, but no signing-key fixture or real remote authentication is tested here.

The safety boundary is **one cooperating writer per private session worktree**. This helper is not
an OS sandbox against arbitrary tools editing that directory. It detects known identity/index
changes and stops without undoing them; all framework writers must honor the session binding.

## Design changes from the reviewed draft

| Review finding | Revised mechanism |
|---|---|
| Another session's commit can be reset | Publication never moves primary HEAD; private unexpected HEAD is refused |
| Merge commit absorbs another session's staging | Independent indexes; host-only Git plus resolution-index verification |
| Narrow update commit pushes unrelated ancestors | Fresh destination base plus conservative primary update gates |
| Bare push succeeds at another destination | Exact SHA and explicit URL/full ref, followed by reachability verification |
| Rollback erases marker evidence | No rollback; private snapshot persists and is independent of primary ahead count |
| Worktree readers erase other branches' markers | One record per session, read-only discovery, exact-operation acknowledgment |
| Setup-required loses its cooldown | Separate persisted outcome and last-attempt cooldown; no fabricated last-success |

The source [review-input.md](review-input.md) preserves the diagnosis. The obsolete draft and prior
review history remain in Git; the current design contains one set of executable requirements.
