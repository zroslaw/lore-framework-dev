# Codex First Real Session: Lifecycle Fidelity Findings

The first real Lore session on Codex (2026-07-04) succeeded functionally but
did not achieve lifecycle parity. Skills loaded, real agent work completed, and
finalization eventually pushed a correctly scoped commit. The failures were in
state continuity and procedure fidelity, not in the knowledge substrate.

The detailed evidence is preserved in
`workdir/codex-first-session-audit.md`. This topic keeps the durable
architectural conclusions and work order.

> **Update (2026-07-05) — several gaps now closed by the validated `docs/engines/` build.** A
> later end-to-end Codex run with the engine-profile binding in place **resolved the
> merge-execution-contract gap**: merge ran in a native `spawn_agent` worker (not inline), because
> the `docs/engines/codex.md` subagent-spawn binding instructed the spawn — the earlier inline merge
> was an *un-instructed* model, not an absent capability, and Codex in fact has a native multi-agent
> subsystem (`codex-native-multi-agent-subsystem.md`). Work-order item 2 (Codex adapter bindings for
> subagents / runtime bounds / memory files / invocation syntax) is likewise **built and validated**
> — see `docs-engines-convention.md`, `codex-port-validated-end-to-end.md`. Still open from the list
> below: transcript-backed lifecycle-state recovery (compaction), atomic/resumable finalize,
> explicit sequencing barriers, the network/sandbox escalation policy, and the automated harness
> driver with trace-level assertions. The `.git`-sandbox block is now a named constraint
> (`codex-git-sandbox-blocks-dotgit.md`).

## Confirmed gaps

- **Compaction changed lifecycle state.** Codex's compacted replacement history
  omitted a successful guest attachment and its confirming user turn. The
  resumed model trusted the summary and repeated the attach. Conversation
  history alone is therefore not an authoritative active-agent store on an
  engine with lossy compaction.
- **Finalize was not atomic or resumable.** Codex ended the first finalize turn
  after summarize and diff review but before add, commit, or push. The user had
  to notice and request continuation.
- **The merge execution contract was skipped.** Merge ran inline instead of in
  a booted subagent, losing the intended context isolation even though the
  resulting lore happened to be acceptable.
- **Generic parallelism violated dependencies.** Attach read context while
  auto-pull was still running, and finalize raced `git status` against
  `git add`. Lifecycle docs need explicit sequencing barriers.
- **Sandbox and safety behavior needs an adapter policy.** Network-disabled
  execution produced repeated pull/push failures and inconsistent escalation.
  A sensitive health-data push also required explicit user approval, so the
  framework cannot promise promptless finalization on every engine.
- **End-state-only tests miss procedural failures.** The lifecycle harness has
  no Codex driver and does not assert subagent use, ordering, compaction
  recovery, or interrupted-finalize resumption.
- **Smaller friction remains.** Agent arguments need normalization and unique
  fuzzy suggestions; broad home-directory discovery should be avoided or
  pruned.

## Compaction strategy

Use two mitigations together:

1. Reduce exposure by automatically disabling auto-compaction for Lore
   sessions when an engine provides a supported control. Where the framework
   cannot set it, recommend disabling it in setup guidance for long sessions.
   This is a usability mitigation, not the correctness mechanism.
2. Recover lifecycle state from the raw uncompacted engine transcript. Codex
   exposes `CODEX_THREAD_ID`, and its JSONL retained the attachment lost by
   compaction. Generalize transcript discovery behind engine adapters and feed
   a common normalized state capsule to attach, reflection, summarize,
   finalization, and interruption recovery.

Compacted summaries are hints, never authoritative lifecycle state. Raw logs
stay local by default because they can contain secrets, private links, health
data, and large tool outputs. Extract the minimum capsule needed: engine and
schema version, host, guests, finalize phase/checkpoints, approvals, and
relevant outputs. Define a degraded fallback for unavailable or rotated
transcripts; do not commit complete logs automatically.

This recovery mechanism should be engine-neutral. Codex provides the first
evidence, but every adapter can bind its native session identifier and
transcript source to the same normalized representation.

## Recommended work order

1. Transcript-backed lifecycle-state recovery keyed by the engine session ID.
2. Codex adapter bindings for subagents, runtime bounds, network escalation,
   memory files, invocation syntax, and transcript recovery.
3. Explicit sequencing barriers in lifecycle procedures.
4. Checkpointed, resumable finalize with deterministic Phase 4 mechanics.
5. Codex lifecycle-harness driver plus trace-level assertions.
6. Compaction/resume, interrupted-finalize, network-denied, sensitive-push,
   and attach-idempotency scenarios.
7. Argument normalization, fuzzy agent suggestions, and discovery polish.

## Related topics

- `multi-engine-portability-direction.md` — port architecture and adapter model
- `attach-pattern.md` — current conversation-only active-agent state
- `lifecycle-testing-harness.md` — current engine and assertion coverage
- `session-as-durable-artifact-cluster.md` — transcript and session durability
- `session-summaries-feature.md` — existing compaction-sensitive finalization
- `docs-engines-convention.md` — the engine-profile build that closed the subagent/binding gaps
- `codex-port-validated-end-to-end.md` — the later run where merge ran in a spawned worker
- `codex-native-multi-agent-subsystem.md` — Codex's native subagent tools
- `codex-git-sandbox-blocks-dotgit.md` — the named `.git`-write sandbox constraint
