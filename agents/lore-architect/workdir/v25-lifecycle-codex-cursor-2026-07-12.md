# v25 Lifecycle Check — Codex and Cursor

Run date: 2026-07-12 15:55 +07

Framework under test: `/Users/yaroslav/Documents/agent-workspace/lore-framework`

Scope: lifecycle harness only. Quality benchmark was not run.

## Commands

```bash
LR_LIFECYCLE=1 LR_ENGINE=codex LR_TEST_MODEL=gpt-5.4-mini LR_FRAMEWORK_DIR=/Users/yaroslav/Documents/agent-workspace/lore-framework python3 -m unittest discover -s tests/lifecycle -v
```

```bash
LR_LIFECYCLE=1 LR_ENGINE=cursor LR_TEST_MODEL=composer-2.5 LR_FRAMEWORK_DIR=/Users/yaroslav/Documents/agent-workspace/lore-framework python3 -m unittest discover -s tests/lifecycle -v
```

Both real-engine runs required running outside the Codex sandbox. The first in-sandbox Codex attempt failed before model execution because Codex could not write `~/.codex/state_5.sqlite`.

## Summary

| Engine | Model | Result | Runtime | Notes |
|---|---:|---:|---:|---|
| Codex | `gpt-5.4-mini` | 17 pass, 2 fail, 1 error, 4 skip | 2894s | Failures below; registration scenarios skipped by harness. |
| Cursor | `composer-2.5` | 22 pass, 1 fail, 1 skip | 1386s | Only failure is stale harness expectation for legacy init marker. |

## Codex Details

Passed:

- Boot happy path
- Boot pulls fresh commits
- Boot degraded remote unreachable
- Boot unknown agent
- Boot version mismatch release-notes-only
- Boot upgrade gate on dirty tree
- Repo newer than framework Codex guidance
- Consult
- Attach
- Merge
- Summarize
- Finalize end-to-end
- Recall with hint
- Create repo
- Create agent
- Workspace pull/sync scenario
- Update dry-run

Skipped:

- Register agent
- Register repo
- Unregister agent
- Unregister repo

Failures:

- `test_10_reflect`: engine exited 0, but no `reflections/` directory was created.
- `test_18_init`: engine produced the new v25 `<!-- lr:workspace-init:start -->` marker, while the test still asserts the pre-v25 `<!-- lr:init:start -->` marker.
- `test_20_check_catches_seeded_violation`: timed out after 420s while running the full check report through `codex exec`.

Interpretation:

- The init failure is a harness expectation that needs to be updated for v25 hard rename semantics.
- The check timeout may need either a longer timeout for Codex, a narrower assertion prompt, or a deterministic check runner instead of asking the model to produce the full report.
- The reflect failure is the only substantive Codex lifecycle behavior failure from this pass.

## Cursor Details

Passed:

- Boot happy path
- Boot pulls fresh commits
- Boot degraded remote unreachable
- Boot unknown agent
- Boot version mismatch release-notes-only
- Boot upgrade gate on dirty tree
- Consult
- Attach
- Reflect
- Merge
- Summarize
- Finalize end-to-end
- Recall with hint
- Create repo
- Create agent
- Workspace pull/sync scenario
- Check catches seeded violation
- Update dry-run
- Register agent
- Register repo
- Unregister agent
- Unregister repo

Skipped:

- Repo newer than framework Codex guidance

Failure:

- `test_18_init`: engine produced the new v25 `<!-- lr:workspace-init:start -->` marker, while the test still asserts the pre-v25 `<!-- lr:init:start -->` marker.

Interpretation:

- Cursor lifecycle is effectively green for v25 behavior; the single failure is a harness update required by the hard rename.

## Follow-Ups

1. Update lifecycle scenario 18 to assert v25 `workspace-init` markers and command text.
2. Consider renaming the historical `workspace_sync` lifecycle prompt/test labels to `workspace_pull` while preserving backwards-compatibility coverage where intentional.
3. Investigate Codex `reflect` behavior on `gpt-5.4-mini`.
4. Adjust Codex `/lr:check` lifecycle coverage so it does not time out on the full report path.

## Resolution — 2026-07-12 (takeover session, Claude Code / Opus)

All four follow-ups addressed. Root causes were confirmed by tracing the actual Codex
rollout logs (`~/.codex/sessions/2026/07/12/`), not by re-running the suite (rerun was
deliberately deferred per user instruction — fixes below are trace-grounded but not yet
empirically re-verified against a live engine).

**1 — Codex `reflect` failure was a real doc bug, not a model miss.** Rollout
`019f5555` shows `gpt-5.4-mini` booted, read `process-reflection.md`, and *successfully*
`apply_patch`-wrote the reflection — but to `test-lore/reflections/…` (repo root) instead
of `test-lore/agents/test-agent/reflections/…` (inside the agent dir). `patch_apply_end`
reported success; the model reported "wrote one topic"; the test/merge/`/lr:check` #12 all
look only inside the agent dir, so the file was silently orphaned. Cause: the doc said
"the current agent's `reflections/` directory" but **never anchored the path**. A strong
model infers `agents/<name>/reflections/`; the weak model took it literally.
- **Fix:** `lore-framework/docs/process-reflection.md` § "How to Write Reflection Topics"
  now spells out the explicit path (`<lore-agent-repo>/agents/<agent-name>/reflections/`,
  sibling of `lore/`/`lore-context.md`/`workdir/`), states it is **not** at repo/workspace
  root, and warns that a misplaced reflection is silently lost. Classic
  `execution-testing-catches-blind-ambiguity`.

**2 — `test_18` stale (both engines).** Fixed for the v25 hard rename:
`INIT_PROMPT` → `lr:workspace-init` skill; Codex translation → `docs/workspace-init.md`;
marker assertions → `<!-- lr:workspace-init:start/end -->`; test renamed
`test_18_init` → `test_18_workspace_init`.

**3 — `test_19` stale (passed only by model recovery).** `WORKSPACE_SYNC_PROMPT` pointed
at the renamed `lr:workspace-sync` skill and a non-existent `docs/workspace-sync.md`.
Renamed constant → `WORKSPACE_PULL_PROMPT`, skill → `lr:workspace-pull`, Codex translation
→ `docs/workspace-pull.md`, test → `test_19_workspace_pull` (plus doc-comments).

**4 — Codex `test_20` "timeout" was over-work, not a hang.** Rollout `019f5566` shows the
model faithfully executing all 23 checks and grinding check #21 (cursor-tree parity, 30
wrapper diffs against the *framework* tree) at the 420s mark — work irrelevant to the
scenario's only assertion (that check flags the seeded broken cross-reference). Narrowed
`CHECK_PROMPT` (both Claude and Codex paths) to run checks on the workspace's own agent
repos and explicitly list broken cross-references by filename, dropping the "print the full
report verbatim" burden. Preserves the assertion; removes the framework-wide grind.

Files touched: `lore-framework/docs/process-reflection.md`,
`lore-framework-dev/tests/lifecycle/harness.py`,
`lore-framework-dev/tests/lifecycle/test_repo_workspace.py`.

Deterministic suite re-run green after edits (`47 run, 24 lifecycle-skipped`, clean
imports, zero residual stale references).

**Empirical re-verification — Claude Code / `haiku`, 2026-07-12 (takeover session).** Ran the
four touched scenarios live against the v25 tree; all four **pass** (`Ran 4 tests in 268s, OK`):

| Scenario | Result | Time | Cost |
|---|---|---:|---:|
| `test_10_reflect` | ok | 78s | $0.14 |
| `test_18_workspace_init` | ok | 43s | $0.07 |
| `test_19_workspace_pull` | ok | 11s | $0.03 |
| `test_20_check_catches_seeded_violation` | ok | 125s | $0.20 |

`haiku` was chosen deliberately as a weak model to re-trigger the reflect path ambiguity; it
wrote to the correct `agents/<name>/reflections/` location, confirming the doc fix. The check
scenario finished in 125s (vs the 420s Codex timeout), confirming the narrowed prompt. Note:
the original reflect failure surfaced on Codex `gpt-5.4-mini` specifically — the
`process-reflection.md` fix is on the same doc Codex reads, and `haiku` corroborates it, but a
Codex-native rerun would be the definitive same-engine confirmation (deferred per user).
