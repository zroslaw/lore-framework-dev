---
lore: 1
type: topic
summary: "In a cmd_preflight-shaped docstring, a new step's correctly-appended number doesn't guarantee its textual position matches real execution order — renumber to match the code path."
parent: lore-context.md
---

# Appended Docstring Step Must Match Execution Position

When a new numbered step is appended to a multi-step docstring procedure — the shape
`cmd_preflight`'s own docstring uses, which `agent-boot.md`'s Manual Boot Procedure sends readers
straight to — the step's
*number* being correct ("append, don't renumber") does not guarantee its *textual position* is. For
a procedure read top-to-bottom by a fallback executor, position is what actually governs execution
order. Same root cause as
[instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md):
a reader pages or reads sequentially, and structural position wins over correct-but-misplaced
labeling.

## The concrete instance (v42 workspace-auto-refresh design, 2026-08-23)

Implementing the workspace-refresh leg for `lr-core preflight`
([workspace-auto-refresh-design.md](workspace-auto-refresh-design.md)), I appended it to
`cmd_preflight`'s docstring as "Step 8," placed textually *after* the existing Step 7 (teammate
detection) paragraph — matching the build order's "append, not renumber" guidance in isolation. But
the actual code runs the new leg *before* teammate detection. The docstring read "Step 8: ... before
Step 7's teammate detection" — self-contradicting its own step numbers.

Caught by a second read-through while writing the Manual Boot Procedure's "seven steps"
cross-reference in `agent-boot.md`, not by any test — this class of drift has no test surface, only
a careful reread against the real execution order.

## The fix

Renumbered so the workspace-refresh step became Step 7 and teammate detection became Step 8,
matching code order, and updated `agent-boot.md`'s Manual Boot Procedure step-count/description
accordingly.

## How to apply

When inserting a new step into an existing `cmd_preflight`-shaped literate docstring
([literate-accelerator-pattern.md](literate-accelerator-pattern.md)), always renumber to match true
execution order rather than defaulting to "append the highest number" — check the actual code path,
not just where in the docstring text is easiest to add a paragraph. Also grep sibling docs
(`agent-boot.md` here) for hardcoded step counts/descriptions of the same procedure before
considering the doc side done — a mismatched count there reproduces the same defect one layer out.

## See Also

- [instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)
  — the general rule this is an instance of: structural position, not correct labeling or emphasis,
  governs whether an executor finds an obligation.
- [literate-accelerator-pattern.md](literate-accelerator-pattern.md) — why `cmd_preflight`'s
  docstring is read as freestanding executable prose in the first place, which is what makes its
  internal step order load-bearing.
- [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md) — the feature whose
  implementation surfaced this.
- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — the sibling
  discipline of checking every site that *states* a step count, not only the one you just edited.
