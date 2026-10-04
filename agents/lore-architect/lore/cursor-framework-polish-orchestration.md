---
lore: 1
type: topic
summary: "When continuing a Codex-style review/fix loop inside Cursor, spawn Composer 2.5 Task subagents in parallel implementer-plus-reviewer waves — not Terra — and leave polish committed locally until an explicit ship."
parent: lore/cursor-engine-capabilities.md
---

# Cursor Framework Polish Orchestration

When a framework change already went through Codex-orchestrated design review and the work continues
inside **Cursor** for implementation polish, use Cursor's native **`Task`** subagents with
**Composer 2.5** (`composer-2.5`, not `-fast`) unless the user asks for Terra or another model.

## Pattern that worked (v47 polish, 2026-10-04)

1. **Parallel wave** — one implementer Task plus one cold reviewer Task on the same change set.
2. **Follow-up fixer** — a third Task for SHOULD-FIX leftovers the reviewer named.
3. **Final cold review** — one more reviewer Task on the polished tree before session finalize.

Do **not** treat polish as ship: keep the feature worktree committed locally until an explicit ship
step (tag, merge to `main`, publish). Polish commits are evidence for finalize, not release.

## See Also

- [feedback-composer-25-subagent-reviews.md](feedback-composer-25-subagent-reviews.md) — default model
  for design-review subagents.
- [parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md) — TriLens judgement layer;
  polish loops here are lighter-weight Task fan-out, not `/lr:trilens-loop`.
- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) — polish
  edits after a converged review are ungated until re-run or ship freeze.
