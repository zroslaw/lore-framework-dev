# Cursor Merge via `Task` (Not Host-Side)

**Decision (2026-07-28):** `docs/engines/cursor.md` runs **merge** through Cursor `Task`
subagents — one write-capable `Task` per active agent, free-text brief to boot + run
`process-merge.md`, parallel when multi-agent. Same shape as Claude `Agent` / Codex
`spawn_agent`/`wait_agent`.

**Still serial host-side:** recall / lore-search, consult, attach version-reconcile, conflict
resolution — left alone until separately upgraded.

**If `Task` is missing** (old CLI build): stop and say so. Do **not** silently merge in the host
and call that the Cursor merge path.

**Why now:** a live Cursor session exposed that merge was still host-only in the profile while the
engine had native subagents; the same session's `Task` probe closed the free-text-brief unknown
(`cursor-task-free-text-brief-validated.md`). Framework edit lives in
`lore-framework/docs/engines/cursor.md` — ship separately from lore finalize.

Merge remains **optimization-class** (`subagent-as-optimization-vs-subagent-as-semantics.md`) — the
upgrade buys parallelism and context isolation, not reviewer independence. That is why it could
move to `Task` without the semantics-class stop-and-report rule that binds `/lr:trilens-loop`.

## See Also

- `cursor-task-free-text-brief-validated.md` — the probe that unblocked this upgrade
- `merge-in-booted-subagents.md` — engine-neutral merge execution model
- `cursor-engine-capabilities.md` — Cursor hub
- `docs-engines-convention.md` — v30+ profile corrections and binding values
- `subagent-as-optimization-vs-subagent-as-semantics.md` — why merge and trilens share `Task` but differ in class
