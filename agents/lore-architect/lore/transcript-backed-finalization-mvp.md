---
lore: 1
type: topic
summary: "The bounded opt-in design for recovering reflection evidence from native engine transcripts without creating a second finalization lifecycle."
parent: lore-context.md
---

# Transcript-Backed Finalization MVP

Long sessions can lose early decisions and lessons when engine compaction replaces model-visible
history with a lossy summary. Native engine transcripts remain a richer local evidence source, so
the framework has an opt-in transcript-backed reflection design. It is an alternate implementation
of reflection, not a second finalization lifecycle: it produces ordinary `reflections/` topics,
then the existing booted merge, summarize, commit, and push phases remain authoritative. The
implementation draft is preserved at
`agents/lore-architect/workdir/draft-transcript-backed-finalization.md`.

## Bounded MVP

The v1 surface is `finalize --transcript`, limited to host-only sessions. It:

1. reuses `scripts/session-takeover` and resolves the exact current log through a literal marker
   that is searchable in every supported engine transcript;
2. renders the parser-retained, normalized main-thread dialogue into bounded overlapping chunks;
3. sends those chunks to cold, read-only reflection workers;
4. mechanically validates and collects candidate topics; and
5. writes ordinary reflection files for the existing booted merge subagent to reduce semantically.

Raw transcripts and rendered chunks stay in ignored workspace `.tmp` scratch and are never
committed. Strict session selection and complete chunk reporting fail closed: an explicitly
requested high-fidelity mode must not silently fall back to partial evidence.

The fidelity claim is the full parser-retained normalized dialogue, not exhaustive raw tool output.
Existing takeover tool summaries define the v1 evidence boundary. Claude, Codex, and Cursor remain
Tier-1 targets through their existing transcript parsers and subagent bindings; Cursor redaction is
reported as evidence loss rather than hidden.

Workers are context-isolated evidence readers, while merge remains the only semantic reducer. The
host removes only mechanically identical overlap duplicates. Cost and context are bounded by 16
chunks, per-worker response limits, and an aggregate candidate budget. Atomic writes and exact
scratch cleanup are part of the procedure.

## Explicit Deferrals

Compaction counting, transcript-backed session summaries, guests, sidechains, automatic
activation, richer tool evidence, resume/checkpoints, and hierarchical reduction stay outside the
MVP.

## Open Implementation-Readiness Findings

Three consecutive design reviews are integrated into the draft. A fourth feedback-only review
rates implementation readiness at 68% and leaves four questions open:

- overlap can push a rendered chunk beyond the nominal size bound;
- read-only fresh-worker behavior is a procedural promise rather than a technically enforced
  least-privilege sandbox;
- the candidate-result contract has no formal machine grammar; and
- sensitive-data exclusion still depends on model judgment rather than an enforceable guarantee.

Before implementation, classify each finding as a ship blocker or an explicitly accepted MVP
limitation. Do not treat any of the four as resolved merely because earlier review rounds tightened
the draft.

## Relationships

This design advances the correctness concern in
[Session-as-Durable-Artifact](session-as-durable-artifact-cluster.md) without reviving automatic
transcript archival: source logs remain local, and the durable result is curated Lore. It reuses the
parsers and normalization boundary from [Takeover](takeover-feature.md), preserves the shipped
[four-phase finalization process](finalization-process.md), and changes the usual
[reflect-versus-merge asymmetry](reflect-merge-execution-asymmetry.md) only by giving reflection a
file-backed, context-isolated opt-in path.
