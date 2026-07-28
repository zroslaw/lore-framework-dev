# Cursor `Task` Free-Text Briefs — Validated

**When:** 2026-07-28, live Cursor IDE session (lore-architect boot).

**Finding:** Cursor's `Task` tool accepts a free-text `prompt` plus a `subagent_type` enum
(e.g. `generalPurpose`). A one-line probe returned its result to the caller. Pre-defined agent
files under `.cursor/agents/` are optional for composing per-invocation briefs — not required for
merge or trilens briefs.

**Consequence:** The throwaway-definition workaround in `docs/engines/cursor.md` (§ Native
subagents) is obsolete for those brief shapes. Trust tool-call evidence / schema over the older
"name-only?" unknown.

**Scope limit:** This validates brief *shape* only — not end-to-end proof that every fan-out
procedure (`merge`, `trilens-loop`, future upgrades) satisfies its contract when dispatched via
`Task`. Upgrade claims still need tool-call logs or lifecycle evidence, not a passing scenario
alone.

## See Also

- `cursor-merge-via-task.md` — merge upgraded to `Task` the same day, once brief shape was known
- `cursor-engine-capabilities.md` — Cursor hub; subagent model summary
- `docs-engines-convention.md` — profile binding that carried the unknown until this probe
- `trilens-loop-feature.md` — semantics-class procedure that depends on free-text briefs
