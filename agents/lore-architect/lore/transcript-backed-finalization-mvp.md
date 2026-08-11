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

## v39 Implementation and Residual Limits

Implemented locally in framework v39 (pending push, 2026-08-11):

- `session-takeover reflection-input` reuses the three parsers, groups visible dialogue, creates
  `0700` private chunk directories through exclusive writes, records a schema-1 manifest, and cleans
  exact files on a write failure;
- `--require-verified` prevents transcript reflection from selecting the usual heuristic recent log;
- Cursor counts omitted `[REDACTED]` assistant turns; and
- `process-transcript-reflection.md` routes a verified host-only run through fresh read-only workers,
  contract validation, retry, bounded consolidation, and exact scratch cleanup before normal merge.

The former readiness questions are now explicit v1 limits, not silently implied guarantees:

1. Required overlap can make a chunk exceed its nominal bound even when either source unit alone
   fits. The manifest flags every such `oversize` chunk rather than truncating evidence. This is
   safe and visible; a future alternative needs a different overlap policy.
2. Fresh/read-only worker isolation is supplied by the active engine's subagent mechanism and
   procedure contract, not a framework-owned capability sandbox. Transcript mode fails when that
   engine capability is absent; it does not claim technical least privilege beyond the engine.
3. Candidate validation is deliberately a host procedure, because candidates are natural-language
   Lore. The strict structured return contract makes malformed results fail closed, but a parser is
   a growth seam if real runs show host validation is inconsistent.
4. Sensitive-data eligibility remains a judgment gate. Literal credentials and raw private URLs are
   forbidden; ambiguous sensitive material is omitted. A deterministic detector would be a separate
   privacy design, not an honest claim for this v1.

The deterministic suite covers the parser, bounds, overlap, strict resolver, redactions, and safe
write behavior. Real-engine lifecycle and quality verification were waived by the user for v39, so
the release does not claim model-execution fidelity for the procedure.

## Relationships

This design advances the correctness concern in
[Session-as-Durable-Artifact](session-as-durable-artifact-cluster.md) without reviving automatic
transcript archival: source logs remain local, and the durable result is curated Lore. It reuses the
parsers and normalization boundary from [Takeover](takeover-feature.md), preserves the shipped
[four-phase finalization process](finalization-process.md), and changes the usual
[reflect-versus-merge asymmetry](reflect-merge-execution-asymmetry.md) only by giving reflection a
file-backed, context-isolated opt-in path.
