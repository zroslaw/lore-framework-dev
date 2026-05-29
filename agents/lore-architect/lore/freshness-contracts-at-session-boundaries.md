**Whenever an agent's working memory is being newly seeded from disk, the disk state must match the team's latest pushed state.** Each such seeding moment is a **session-context boundary** — and the freshness contract belongs there, automatic, with a manual override.

A foundational principle of team-shared lore agents (see `team-shared-knowledge-principle.md`). Crystallized by v13's auto-pull design but applies to every framework feature that touches lore. Named per the meta-rule in `naming-foundational-principles.md`.

## The Failure Mode

Stale lore is most damaging at the moments when an agent's working memory is being constructed from disk. The motivating example: integrating reflections into days-old lore can re-introduce decisions the team has already revised. The agent runs the merge correctly — but the input is wrong. Every subsequent decision in the session compounds on that staleness.

Disk being out of date is not by itself a problem. *Reading from out-of-date disk into working memory* is the problem, because everything downstream then operates on stale assumptions.

## Three Boundary Types (v13)

1. **Session entry — boot.** The host repo is read into context at the start of every session. Refresh before the first decision is made. Implemented at `agent-boot.md` step 2.
2. **Perspective load — attach.** A guest agent's role and lore-context join the session. Refresh before importing them. Implemented at `attach.md` step 2.
3. **Pre-write — pre-merge.** Reflections are about to be integrated into lore — the highest-stakes write the framework does. Refresh before the integration so reflections land on top of the team's latest state. Implemented at `process-merge.md` step 0.

Boot pull alone covers most cases. The pre-merge defense-in-depth pull exists because (a) boot may have skipped (no remote, network blip, etc.), and (b) the freshness contract belongs visible at the merge site itself — that's where stale lore is most damaging, so the explicit step makes the contract auditable from the merge doc alone, not transitively through the boot doc.

## The Complementary User Surface

Boundaries fire automatically. Between boundaries, the user may know something pushed (a teammate said so, a parallel session ran, a review just landed). For these moments, **`/lr:pull-lore`** makes the boundary refresh manually triggerable.

The split is intentional: automatic at boundaries (safe default, no friction), manual on demand (user knowledge of pushed state). Don't over-automate the mid-session case — `/lr:pull-lore` is rare in practice.

## Generalization to Future Features

When designing a new framework operation that reads lore, ask:

- **Does this cross a session-context boundary?** I.e., is the operation seeding fresh state into the agent's working memory?
- **Does it bake in a freshness assumption?** I.e., does correctness depend on the read seeing the team's latest pushed state?

If both answers are yes, the freshness contract belongs at the boundary — automatic, with a manual override. Add the contract before shipping the feature, not after the first staleness bug.

If only the second is yes (the operation reads lore but is not itself a context-boundary), the existing boundary refreshes upstream typically suffice. Don't redundantly pull mid-flow.

## What This is *Not*

- **Not a continuous sync mechanism.** The framework does not poll or background-refresh. Refresh is bounded to discrete moments where the cost of staleness is high.
- **Not a write-side commit-on-change mechanism.** The freshness contract is about reads. Writes are handled by finalize phase 4 (commit + push) and `resolve-conflicts.md` (when push is rejected).
- **Not a substitute for `resolve-conflicts.md`.** Auto-pull *prevents* the common case of stale-merge collisions; resolve-conflicts heals after a concurrent finalize collided despite the prevention. They compose.

## Operational Guidance

When evaluating a design decision touching lore reads:

1. Identify whether the operation is at a session-context boundary or between boundaries.
2. If at a boundary: the freshness contract belongs in the operation, automatic, best-effort.
3. If between boundaries: rely on the upstream boundary refresh; don't add redundant pulls. Make the manual surface (`/lr:pull-lore`) discoverable for the user-knowledge case.
4. If the operation *writes* lore as a primary effect: pre-write refresh applies, plus the dirty-tree gate question (see `dirty-tree-gates-write-vs-read-distinction.md`).

When writing the surrounding framework doc, the freshness contract should be explicit, not transitive. A reader of `process-merge.md` should see the pre-merge refresh step at step 0 — they shouldn't have to chase through boot's auto-pull invocation to know the merge subagent reads fresh state.

## Diagnostic Signals (misframing)

- "We pull at boot, that's enough" — true for most paths, but ignores the explicit-contract value at high-stakes write sites.
- "Pulling mid-session is too noisy" — correct for between-boundary cases; incorrect for boundary cases. The verbosity table in `auto-pull.md` handles the noise problem (silent on no-op for boot/attach/merge; verbose for `/lr:pull-lore`).
- "The user can pull manually if they want fresh state" — pushes the freshness burden to the user. The framework should default to fresh on every boundary; manual is the override, not the primary mechanism.

## See Also

- `auto-pull-mechanism.md` — the v13 implementation that crystallized this principle. Three automatic boundaries plus `/lr:pull-lore` for the in-between case.
- `team-shared-knowledge-principle.md` — the underlying motivation: shared repos accumulate team knowledge; staleness is the primary failure mode.
- `agents-are-executors-first.md` — execution decisions made on stale lore are the worst kind, because the agent acts on them.
- `reflect-merge-execution-asymmetry.md` — merge is file-driven and runs in subagents; the freshness contract there is "the files you read are the freshest the team has."
- `naming-foundational-principles.md` — the meta-rule that prompted naming this principle as its own topic.
- `system-design-principles.md` — where this principle is indexed alongside other foundational framings.
- `dirty-tree-gates-write-vs-read-distinction.md` — adjacent: the read-vs-write question for safety gates around the same operations.
