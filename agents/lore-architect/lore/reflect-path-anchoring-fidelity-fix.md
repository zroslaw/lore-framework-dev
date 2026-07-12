# Reflect Path-Anchoring Doc Fix (v25 lifecycle, 2026-07-12)

A detailed doc-fidelity case study — the second concrete instance of the bug class in
`execution-testing-catches-blind-ambiguity.md`, in a *different* doc from the `agent-boot.md` cases
(`agent-boot-doc-fidelity-fixes.md` is the first).

## The bug

`docs/process-reflection.md` told the model to write reflection topics into "the current agent's
`reflections/` directory" but **never stated the path**. A strong model infers
`agents/<agent-name>/reflections/`; the Codex lifecycle run on `gpt-5.4-mini` took it literally and
wrote the reflection to `<repo>/reflections/` (repo root). The merge step, `/lr:check` #12, and the
reflect lifecycle test all look **only inside the agent directory**, so the file was silently
orphaned — the test reported "no `reflections/` created" even though the model believed it had
succeeded.

## How it was found — rollout-log tracing, not guessing

The takeover digest only said "engine exited 0, no reflections/ created." Root-causing it meant
reading the actual Codex rollout log for that harness sub-run
(`~/.codex/sessions/2026/07/12/rollout-*.jsonl`). The `apply_patch` call and its `patch_apply_end`
event showed `success: true` writing to `…/test-lore/reflections/fixture-deployment-tool-update.md`
— repo root, not `…/test-lore/agents/test-agent/reflections/`. That one line turned a vague "model
skipped the write" into a precise "doc never anchored the path." This is the
`codex-testing-methodology.md` discipline (ground-truth tool calls in rollout logs) applied to a
lifecycle failure, and `verify-before-acting-on-suspected-bugs.md` paying off — the suspected bug
(missing write) was not the actual bug (wrong path).

## The fix

`process-reflection.md` § "How to Write Reflection Topics" now spells out
`<lore-agent-repo>/agents/<agent-name>/reflections/` (sibling of `lore/`, `lore-context.md`,
`workdir/`), states it is **not** at repo/workspace root, and warns that a misplaced reflection is
silently lost. Verified green afterward on Claude Code + `haiku` (the weak-model tier).

## Curation takeaway

**When a procedure doc tells the model to write to a named directory, anchor the explicit path** —
weak models and non-Claude engines don't share the author's charitable inference. Sweep sibling
read/write docs when doing this: `process-merge.md` also says "the agent's `reflections/`", but it
*reads* the same location, so it inherits the anchor once reflect writes correctly. Evidence the
bug class recurs anywhere a procedure doc names a filesystem location by role ("the agent's X
directory") without an absolute-vs-relative path.

See `execution-testing-catches-blind-ambiguity.md` (the generalizing principle),
`agent-boot-doc-fidelity-fixes.md` (the first case study), `haiku-ambiguity-detector.md`,
`codex-testing-methodology.md`, `verify-before-acting-on-suspected-bugs.md`,
`lifecycle-testing-harness.md`, `v25-lifecycle-scenario-fixes.md`.
