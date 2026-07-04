# Codex First Real Lore Session Audit

Date: 2026-07-04
Codex thread: `019f2a7d-eed7-79c0-8a3c-b9936e07f4f8`
Host agent: `health-advisor`
Guest agent: `lore-architect`

## Verdict

The first real Codex session succeeded functionally: skills loaded, the host
booted, real phone data was pulled and analyzed, lore was finalized, unrelated
repository changes were preserved, and the finalize commit reached the remote.
It was not yet smooth or faithful enough to claim Codex lifecycle parity.

## What Worked

- Codex loaded the installed Lore plugin and invoked `lr:boot`, `lr:finalize`,
  and `lr:attach` without packaging changes.
- Boot found the correct agent repo, checked framework version 18, and loaded
  `role.md` plus `lore-context.md`.
- The health agent executed real work rather than only advising: it refreshed
  the iPhone export, analyzed the sleep trace, corrected the Watch cutoff using
  raw heart-rate data, and updated the manual trial dataset.
- Finalization ultimately produced a correctly scoped commit (`73c40ec`) while
  leaving the unrelated `lore-repo.md` edit uncommitted.
- The health-data push safety gate required explicit approval before private
  health/session data was sent to the configured GitHub remote.

## Confirmed Lifecycle Findings

### 1. Compaction lost active-agent state

`lore-architect` was successfully attached at 01:54. Codex compacted the
conversation at 01:56, but the replacement history omitted both the user's
confirming `yes, lore-architect` message and the successful attach confirmation.
The compacted handoff therefore said the guest was not attached. The resumed
model trusted that handoff and repeated the attach.

This is a framework-level correctness problem because attach currently treats
conversation history as the only active-agent state store. A lossy engine
compactor can silently change host/guest state.

### 2. Finalize silently stopped before Phase 4

The first finalize turn reflected, merged, and summarized, then Codex marked the
turn complete immediately after the final diff check. It had announced that it
would stage, commit, and push, but did none of those operations. The user had to
ask whether finalization had completed before it resumed.

Finalization therefore needs explicit phase checkpoints and resumability rather
than relying on one model turn to retain procedural momentum.

### 3. Merge ran inline instead of in a booted subagent

`process-merge.md` requires one booted merge subagent per active agent, including
single-agent sessions. Codex performed the merge directly in the host context.
The resulting lore happened to be reasonable, but the required context
isolation and execution model were skipped.

Codex needs an engine-specific subagent binding, with a deterministic
`codex exec` fallback if prose-triggered subagent spawning is unreliable.

### 4. Ordered operations were incorrectly parallelized

During attach, Codex started auto-pull, version reads, and guest context reads in
parallel. Context could therefore be read before the refresh completed. During
finalize, it launched `git add agents/` and `git status --short` concurrently;
status raced ahead and falsely appeared unstaged.

Procedure docs need explicit dependency barriers that override a coding
engine's generic preference to parallelize tool calls:

- pull must complete before version/context reads;
- reflect must complete before merge;
- merge must complete before summarize;
- add must complete before status/commit;
- commit must complete before push.

### 5. Network sandbox behavior was repetitive and inconsistent

Codex ran with network disabled in its sandbox. Required pulls and pushes first
failed on DNS and then sometimes retried with escalation. The initial attach,
however, accepted degraded mode without trying the available escalation path.

The Codex adapter should detect the network-disabled environment and follow one
consistent policy: request escalation for required freshness operations, or
document/configure network access for trusted Lore workspaces.

### 6. Codex safety prompts conflict with the no-prompt finalize invariant

The framework says finalize commits and pushes without an approval prompt.
Codex blocked the first escalated push because it contained newly recorded
private health and session data. Explicit user approval was then required.

This platform safety boundary should be documented as an engine-specific
exception. The framework should not promise fully promptless finalization on
engines whose policy may require informed approval for sensitive data transfer.

### 7. Current lifecycle tests are blind to these failures

The lifecycle harness has no Codex driver. Its finalize scenario checks final
filesystem and git state, but does not assert that merge used a subagent, that
dependent operations were ordered, or that a partially completed finalize can
resume. A run can therefore reach the correct end state while violating the
intended process.

### 8. Smaller usability friction

- Agent argument handling was inconsistent. A trailing `agent` was tolerated
  for boot, while `lore-framework-architect` required a manual correction to
  `lore-architect`. Normalize optional trailing words and offer a unique fuzzy
  suggestion.
- Running from `/Users/yaroslav` made discovery scan a broad home directory and
  encounter unreadable paths. Recommend starting Codex from the actual workspace
  or improve discovery pruning/registry behavior.
- Progress reporting was useful but verbose during boot and repeated expected
  network failures.

## Compaction Options

Two approaches should be evaluated together:

1. **Disable automatic compaction for Lore sessions when the engine exposes a
   supported control.** If Lore cannot disable it programmatically, the Codex
   setup/onboarding documentation should at least recommend that users disable
   auto-compaction for long Lore sessions. This reduces risk but should not be
   the only correctness mechanism.
2. **Recover from the raw, uncompacted engine transcript.** Codex exposes
   `CODEX_THREAD_ID`, and the session JSONL under `~/.codex/sessions/` retained
   the successful attach even though the compacted replacement history lost it.
   A helper can reconstruct host, guests, finalize phase, approvals, and outputs
   after compaction or model switching.

Raw-transcript recovery should be designed as an engine-neutral capability:
each engine adapter identifies its native session ID and raw transcript source,
while the framework consumes a common normalized event/state representation.
This would improve finalization accuracy, reflection quality, session summaries,
and interruption recovery across all engines, not only Codex.

Important design constraints:

- Raw transcripts may contain secrets, health data, private links, and large
  tool outputs. Read locally by default; do not commit raw logs automatically.
- Record engine and transcript schema version.
- Prefer extracting a minimal lifecycle state capsule over repeatedly loading
  an entire transcript into model context.
- Treat compacted summaries as hints, not authoritative lifecycle state.
- Define behavior when the raw transcript is unavailable or rotated.

## Recommended Work Order

1. Add Codex lifecycle-state recovery keyed by `CODEX_THREAD_ID`.
2. Add `docs/engines/codex.md` with bindings for framework root, subagents,
   runtime bounds, network escalation, memory files, invocation syntax, and
   transcript recovery.
3. Add explicit sequencing barriers to ordered lifecycle procedures.
4. Make finalize checkpointed/resumable; move mechanical Phase 4 work into a
   deterministic script where practical.
5. Add a Codex driver to the lifecycle harness.
6. Add trace assertions for subagent use and ordered operations.
7. Add compaction/resume, interrupted-finalize, network-denied, sensitive-push,
   and attach-idempotency scenarios.
8. Add argument normalization, fuzzy agent suggestions, and safer discovery.

## Evidence

The uncompacted Codex transcript is currently at:

`~/.codex/sessions/2026/07/04/rollout-2026-07-04T07-18-44-019f2a7d-eed7-79c0-8a3c-b9936e07f4f8.jsonl`

Existing architectural anchors:

- `lore/attach-pattern.md`
- `lore/multi-engine-portability-direction.md`
- `lore/lifecycle-testing-harness.md`
- `lore/execution-testing-catches-blind-ambiguity.md`
- `workdir/draft-port-codex.md`

