---
lore: 1
type: topic
summary: "User preference: lore design-review subagents use Composer 2.5 (regular, not fast) by default, not Sonnet."
parent: lore-context.md
---

# Feedback — Composer 2.5 for design-review subagents

User preference (2026-07-12): lore design-review subagents should use **Composer 2.5** (regular,
not fast). Do not default to Sonnet 4.6 High for parallel review fan-out unless user requests it.

**Engine limit (2026-10-04):** Composer 2.5 is a Cursor model and is unavailable to Claude Code
subagents. On Claude Code, review subagents run on the session's default model — say so once at the
start of the review cycle rather than silently substituting.

## See Also

- [cursor-framework-polish-orchestration.md](cursor-framework-polish-orchestration.md) — Task fan-out
  for implementation polish inside Cursor (v47).
- `settle-conflicting-reviewer-claims-in-the-source.md`
- `workspace-design-review-discipline.md`
- `parallel-reviewer-fanout-pattern.md`
