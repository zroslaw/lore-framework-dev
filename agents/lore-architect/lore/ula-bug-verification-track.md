# ULA bug-verification track (Steps D/E + aggregation re-verify)

Added v16 (2026-06-08). The ULA unit pass gained a **verification layer** on top of find/scenarios/gap. The unit pass is now **A→B→C→D→E**.

## Two levels

**Per-unit (in the unit agent), Steps D→E** — appended after A/B/C in the *same single agent context*:
- **D — verify bugs:** for each Step A bug, a thorough real-ness + *real system impact* investigation (past the clean-room constraint — may read the whole repo). Outcome per bug: real+impactful → keep, set true `severity`; real-but-harmless → keep at `severity: negligible`; not-a-bug → move to `dismissed[]` (never delete).
- **E — guardrail:** re-list every Step A bug, confirm each was verified, ensure each lands in **exactly one** of `bugs[]` / `dismissed[]`. A completeness safety-net.

**Aggregation-level (the skill, after persist)** — `ula-file.md` step 6: an **independent fresh subagent** re-applies the D/E checks across ALL units' `bugs[]` with whole-file context (catching cross-unit discharges/confirmations a single unit agent can't see), reports per-bug keep/dismiss; the aggregator updates `bugs.yaml`, moving rejects to `dismissed[]` with `dismissed-by: aggregator`.

## Why two passes

The finder is deliberately **high-recall** ("potential, don't confirm — a separate track confirms"). D/E + aggregation ARE that track. Per-unit D/E is *self*-verification (same agent grades its own work → anchoring/independence weakness); the aggregation subagent is the **independent second opinion**, and `dismissed-by` (unit vs aggregator) records which stage caught each false positive. This is `graduated-verification-confidence.md` applied to ULA.

## Mechanism choice (user-driven)

The user rejected a heavier per-bug multi-agent fan-out as too complicated; chose "extend the one unit agent's step list" + one aggregation subagent. Lighter, fits the existing one-agent-per-unit flow, no new orchestration; prompts stay dual-mode (workflow or plainly-spawned subagents). Aggregation lives in `ula-file.md` (skill orchestration), not the workflow.

## See Also

- `aiqa-ula-feature.md` — the ULA pass this extends (A→B→C→D→E).
- `ula-finding-schema.md` — the finding fields D/E set/revise; `dismissed[]` + `dismissed-by`.
- `graduated-verification-confidence.md` — verification as a confidence assessment, not a boolean.
