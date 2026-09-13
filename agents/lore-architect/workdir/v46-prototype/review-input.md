# V46 concurrency design review — 2026-09-13

Verdict: keep the direction and the single-release scope, but revise the design before implementing its publication procedure. The remaining problems concern transaction ownership and failure-state semantics, not just wording.

Reviewed the combined spec, including round 7's amendments and the marker/reader/C8 cluster. The former A/B/C tiers are historical groupings under the current § 0; this review does not propose separate releases.

Evidence: live framework `90da5b3f1ecd25f8e4fb6ebeea8163e51a8911dd` (v45), design repository `ebaed0f5431c9a03feb339e82de279dac3f0f32c`. Both repositories were clean before and after inspection. The v46 changes are not implemented in that framework tree. Read the proposed algorithms against the current update, conflict-resolution, scanner, refresh, workspace-pull, common-runtime and Keeper status implementations. Executed isolated local Git probes with Apple Git 2.50.1; no network remotes or product files were changed. This is a single review, not a TriLens or lifecycle gate.

## Findings

### 1. Blocker — rollback does not establish ownership of the branch tip

Spec § 4 Step 5b, lines 430–449. The guards require PRE_HEAD to be an ancestor and no intervening merge commits. Neither proves the tip is this operation's commit.

Reproduced: record PRE_HEAD, commit A, let session B commit a different file, then evaluate both guards. Both pass. `reset --soft PRE_HEAD` removes **both** commits from the branch and leaves both files staged. The bytes survive, but B's durable branch history is undone without B's authorization; a later publication can absorb it. T35 currently assumes external movement fails the ancestry check, which is false for the ordinary linear-commit case.

Step 3 has a related race: `git show HEAD` can inspect another session's commit, and `reset --soft HEAD^` can then undo it. Git's individual index/ref locks do not cover the sequence between these commands.

Required change: record and verify the exact operation commit and branch identity; refuse destructive recovery after any unowned tip movement. Verification and mutation must be protected by a transaction ownership mechanism, not a check followed by an unprotected reset. All cooperating mutators, including automatic pulls, must respect it. An advisory lock does not protect against arbitrary external Git commands or same-file edits; document that limit.

### 2. Blocker — the merge-resolution commit reopens the unrelated-staging hole

Spec § 4 Step 4a, line 404, uses `git commit --no-edit` after resolving conflicts.

Reproduced: start a conflicted merge, resolve and stage its topic, then let another session stage an unrelated unfinished file before the merge commit. That file is committed with the merge. The initial pathspec commit and its verification do not protect this later commit. I2 is therefore not satisfied end-to-end.

Required change: protect the whole index/merge transaction, or reconcile in an isolated checkout/index with an explicit expected merge tree. A post-commit path check alone cannot safely undo a result once another writer has advanced the shared branch. Also distinguish legitimately incoming remote changes from unrelated local staged changes when validating a merge.

### 3. High — C3 confuses a narrow commit with a narrow push

Spec § 6, especially line 748, claims deleting the zero-ahead guards still prevents unrelated commits riding along because staging and verification are narrow. The live `docs/update.md` explicitly prohibits automatic publication of unrelated user commits.

Reproduced: one unrelated local commit followed by a commit touching only `lore-repo.md`. The update commit passes path verification, but pushing it publishes the unrelated ancestor too. This is intrinsic to Git history, not an implementation detail.

Required change: settle the actual policy. Either automatic update publication may publish the complete existing branch ancestry, and all contrary promises must be removed, or keep the conservative gate and handle pending updates explicitly. My recommendation is to keep boot-time update publication conservative and reserve broader reconciliation/publication for an explicit finalize. The current design cannot truthfully promise both behaviors.

### 4. High — successful bare push does not prove publication to the recorded upstream

Spec § 4 precondition 4 resolves an upstream, but Step 4, line 332, executes bare `git push`.

Reproduced: the branch tracks `origin/main`, while `remote.origin.push` is `HEAD:refs/heads/elsewhere`. Bare push exits successfully and updates `elsewhere`; `origin/main` does not receive the commit. The procedure would nevertheless report success and clear its marker. Push remote/configuration can differ from the fetch upstream.

Required change: resolve the remote and full destination ref explicitly, push the recorded commit to that destination, and base success handling on that exact publication. Retain normal non-force fast-forward protection. Revalidate identity under the same transaction protection as finding 1.

### 5. High — the rollback erases the condition the marker uses as evidence

Spec § 4 Step 5c and § 7 C4, particularly lines 476–516 and 876. The reader treats absence of ahead commits/MERGE_HEAD as recovery; R16 cannot fire from the marker alone.

Reproduced a foreign conflict followed by abort and soft rollback. Final state: behind=1, ahead=0, no MERGE_HEAD, unpublished staged content, and the next `pull --ff-only` still fails. This is the designed rollback outcome, not an exotic external repair.

Under the specified reader predicate, the marker is deleted and C8 reports no fault. Therefore T21/T22's marker expectations do not compose with T27's cleanup rule. No-upstream failures also lack the ahead evidence needed by the reader. A killed merge before Step 5c is another gap: C4's algorithm emits only for ahead>0 although its catalog mentions MERGE_HEAD, and C8 requires an existing marker.

Required change: model separate states for committed-but-unpublished work, blocked uncommitted work, and an interrupted Git operation. Revalidate each against evidence appropriate to that state. Zero ahead commits cannot by itself acknowledge publication or resolution. Include attempted content identity if the system needs to distinguish later edits from the blocked payload.

### 6. High — shared marker storage conflicts with branch-local validation

Spec § 4 marker rules 1–3, lines 499–514. Every checkout shares one marker in the common Git directory, yet a reader deletes a marker whose branch differs from its current branch.

Verified with linked worktrees: main and feature have different branches but the same common directory. A failure recorded by feature will be deleted when C4/C8 reads the primary main checkout. T29 and T31 demand incompatible behavior as written. Likewise, success on one branch must not acknowledge a failure on another.

Required change: scope records by full branch/ref and, where dirty files or MERGE_HEAD matter, by checkout identity. Read and validate the recorded target rather than substituting the reader's HEAD. Unknown branch/schema is not proof the fault is repaired.

Concurrency also remains in the marker protocol: ignoring writes when only the reason is unchanged can retain obsolete blocking paths; a reader's stale-file unlink can delete a concurrently replaced marker. The borrowed `workspace_refresh.write_state` uses a fixed `.tmp` path under a separate refresh lock. That pattern is unsafe to copy into an unlocked concurrent publisher. Use unique temporary files and protect record replacement/acknowledgment with explicit identity and synchronization.

### 7. Medium — C5 removes the existing setup-required message suppression

Spec § 8, especially line 992, says setup-required has no failure backoff because it already suppresses repeat messaging. In the current `run_workspace_refresh`, the suppression is exactly the last-attempt TTL that C5 replaces. The setup-required branch does not establish a last-success or record a distinct result.

A local mocked execution of that branch persisted only `last-attempt`. Under the proposed rules, every subsequent boot is due because last-success is missing, and there is no failure backoff. The setup-required message therefore repeats on every boot.

Required change: give setup-required its own persisted outcome and retry/message policy without pretending repositories were successfully refreshed. Test initial setup-required and a transition from prior failures, not just successful and failed network attempts. Bound exponential-backoff computation before exponentiating an untrusted large counter.

## Spec cleanup and test gaps

- T13 still requires the unconditional boot-failure sentence that T36 prohibits for an unreachable remote with ahead-only state. C7 rule 4 also retains the unconditional claim. Remove superseded requirements from the executable spec instead of appending more overrides.
- Step 5b still lacks a disposition for the merge/configuration failures listed in Step 4a. Step 4's index-lock stop can bypass failure recording after a commit already exists. Define every exit using one outcome table.
- Same-checkout interleavings are essential. Two clones model a moving remote but have independent indexes and cannot exercise findings 1–2. Add tests with two controlled writers in one checkout, plus linked-worktree readers/writers.
- Marker-reader, refresh-state, and status JSON behavior are deterministic and should have direct unit tests. Most marker tests currently sit in the costly lifecycle section even though they need no language-model judgment.
- Keep separate tests for semantic conflict reconciliation by real agents; that is where model-execution evidence is useful.

## Recommendation

Keep narrow initial staging, conservative conflict ownership, bounded non-force retries, upstream divergence visibility, last-success freshness, and file-granular pull attempts. These address real defects.

Replace the long prose Git transaction with a small deterministic helper inside the existing runtime. Let agents supply the explicit write-set and semantic resolutions; let code own transaction identity, Git transitions, exact push targets, and machine-readable outcomes. Define the supported shared-checkout/single-writer boundary first. A publication lock alone cannot prevent two sessions overwriting the same lore file before publication; concurrent editing needs session-isolated worktrees or an explicit same-file ownership rule.

Keep one v46 release if that remains the chosen scope. Build a small executable transaction prototype and validate the failing interleavings before expanding the implementation. Move historical tiers and old alternatives out of the active spec, leaving one current contract and one current test matrix. Another prose-only amendment cycle is unlikely to resolve the underlying model.

## Reproduction

The original probes used isolated scratch repositories with local bare remotes. Their important
failure sequences are now covered by the executable reference tests in [test_publish.py](test_publish.py).
This document preserves the input review; the revised design and current validation status are
linked from [README.md](README.md).
