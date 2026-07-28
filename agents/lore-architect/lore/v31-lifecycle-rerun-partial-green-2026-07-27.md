# v31 Lifecycle Re-run After A7 — Re-Triaged (run 2026-07-27, triage corrected 2026-07-28)

First Codex/Cursor lifecycle against `lore-framework` `wip/lr-core-v31` @ `cd8ece1` after the A7
plugin-identity gate landed and engines were repointed (Codex marketplace → worktree; Cursor cloud
plugin moved aside — see `cursor-cloud-plugin-rehydrates-over-plugin-dir.md`).

> **Read this section first.** The run's original triage listed six model-fidelity failures. On
> 2026-07-28 the stored logs were read line by line and **four of the six were not what they looked
> like** — three were one environment bug and one was an undecidable assertion. Acting on the old
> list would have sent a session writing doc fixes for a harness/environment problem.

| Engine | Result | Standing |
|---|---|---|
| Codex | 6/7 modules | **Valid.** One genuine defect, one undetermined. |
| Cursor | nominally 4/7 | **Uninterpretable, not 4/7.** Ran against a v30 plugin. |

Result dirs: `tests/lifecycle/results/20260727T140740Z-standard/` (Codex),
`.../20260727T140949Z-standard/` (Cursor). Ground truth for the re-triage:
`results/20260727T140949Z-standard/logs/`.

## Corrected triage

**Genuine v31 defect — exactly one:**

- **Codex `test_07`** (repo-ahead skew) — `lr-core preflight` emitted a warning string that read
  like a finished message, so the model printed it instead of routing into `version-check.md`'s
  engine-specific remedy. Root cause and fix in
  `script-emits-data-doc-owns-the-words.md`; applied on branch `b824da5`.

**Undetermined, not failing:**

- **Codex `test_08`** (Script Fallback notify) — the notice is emitted mid-boot, but the Codex
  driver captured only `--output-last-message`, so a compliant run and a violating run are
  indistinguishable in the artifacts. Harness defect. Fixed by `RunResult.transcript` (`467b009`);
  the scenario must be re-run to get a verdict. See
  `transcript-vs-final-message-assertions.md`.

**Not fidelity failures at all — one environment bug, seen three times (Cursor):**

- `test_05` — `AssertionError: '30' != '31'`. The repo *was* stamped, to 30. The model executed the
  upgrade correctly against a v30 plugin.
- `test_08` — reply: *"the repo version (31) differs from the framework (30)"*, followed by a normal
  fast-path boot. The deliberately broken `lr-core` copy was never loaded, so no fallback triggered
  and there was nothing to notify about.
- `test_21` (update dry-run) — reports framework 30. Same cause.

Cursor's shard ran against an installed/cached v30 plugin despite the pre-run move-aside, because
the cloud plugin rehydrated 23 seconds after the move (`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`)
and A7's Cursor arm was a model self-report that could not see it
(`a-gate-cannot-be-a-model-self-report.md`). **Cursor has produced zero trustworthy v31 boot data.**

**Harness overhead, not a scenario failure:**

- `test_takeover` — 420s timeout. `run_matrix` probed once per engine, then every module subprocess
  re-probed. Fixed by inheriting the verdict via an `engine|realpath|VERSION` token while still
  running the deterministic filesystem check in each child.

## Ship gate as it now stands

1. Land the `test_07` fix (done on `b824da5`) and **re-run Codex `test_07` + `test_08`** — the
   latter now has a transcript to assert against.
2. **Re-run the whole Cursor shard** with the deterministic `check_cursor_plugin_sources()` gate in
   force. Its previous numbers carry no information.
3. Only then judge the gate green. Note that `b824da5` and the three dev-repo commits below are
   themselves ungated — see `v31-lr-core-parked-2026-07-25.md`.

## Standing lesson

**A failure list is a hypothesis until someone reads the transcripts.** Six assertion messages
produced six plausible stories; four were wrong, and the wrong ones were the *confident-sounding*
ones ("model didn't stamp the file", "model didn't notify"). An assertion message names what was
observed, never why. Re-triage from stored logs before planning fixes — it cost zero engine calls
here (`cursor-cloud-plugin-rehydrate-timing` evidence came from `stat` plus stored stderr).

## See Also

- `v31-lr-core-parked-2026-07-25.md` — parking record, resume list, ungated-commit ledger.
- `lifecycle-harness-plugin-identity-unverified.md` — the A7 gate, its two holes, and their fixes.
- `a-gate-cannot-be-a-model-self-report.md` — why Cursor's A7 arm passed while wrong.
- `cursor-cloud-plugin-rehydrates-over-plugin-dir.md` — the rehydration behavior and its timing.
- `script-emits-data-doc-owns-the-words.md` — the one confirmed defect.
- `transcript-vs-final-message-assertions.md` — why `test_08` was undecidable.
- `verify-before-acting-on-suspected-bugs.md` — the general reflex this run re-taught.
