# Claude-Specific Coupling — Inventory (Phase 0 groundwork)

Where the plugin (`lore-framework/docs/` + `skills/`) hardcodes Claude Code specifics, and what
each maps to under the engine-adapter approach. Counts from grep on 2026-07-04. This is the
"real list" behind the draft's "~5 bindings, ~10–15 sites" estimate — the true number is higher
because `${CLAUDE_PLUGIN_ROOT}` is everywhere, but most of it is mechanical.

The 5 adapter bindings (from `draft-port-codex.md` Phase 0): (1) framework-root, (2) subagent
spawn, (3) runtime bounding, (4) memory file, (5) skill invocation syntax.

## Tier A — mechanical, high-count, low-risk (find→replace + one binding)

### 1. `${CLAUDE_PLUGIN_ROOT}` — 103 sites
- 23 in `skills/*/SKILL.md` — pure boilerplate (`Read ${CLAUDE_PLUGIN_ROOT}/docs/<name>.md and
  follow it`). Every skill's thin pointer.
- 80 in `docs/*.md` — cross-references between procedure docs.
- **Target:** define `<framework-root>` = "the directory containing `VERSION`, resolved relative
  to the invoked SKILL.md (two levels up)". Bind per engine: Claude → `${CLAUDE_PLUGIN_ROOT}`;
  Codex/Cursor → install path. Confirmed empirically: this var resolves **empty** on Codex.
- **Effort:** high count, trivial per-site. Biggest single sweep; lowest risk.

### 2. Memory file `CLAUDE.md` — 12 sites, 4 files
- `docs/init.md`, `skills/init/SKILL.md` (the `/lr:init` payload target), `docs/doctor.md`,
  `docs/workspace-sync.md`.
- **Target:** `AGENTS.md` is native to Codex + Cursor and supported by Claude Code. Make it the
  canonical init target; Claude keeps a CLAUDE.md pointer for back-compat. Binding (4).
- **Effort:** low, contained in init.

### 3. Runtime bounding — 3 sites, 2 files
- `docs/auto-pull.md`, `docs/conventions.md` ("your Bash tool's timeout parameter").
- **Target:** "bound the command's runtime." Already has a documented fallback (fail-fast env
  vars in `conventions.md`). Binding (3).
- **Effort:** trivial.

## Tier B — hard, medium-count, HIGH-risk (semantic, per-engine, fidelity-sensitive)

### 4. Subagent spawning — 66 sites, 12 docs
- `process-merge.md`, `recall.md`, `consult.md`, `attach.md`, `finalize.md`,
  `resolve-conflicts.md`, `lore-search.md`, `summarize.md`, `pull-lore.md`, `auto-pull.md`,
  `agent-boot.md`, `spawn-teammate.md`.
- Phrasing varies: "single message with multiple Agent tool calls", "general-purpose subagent",
  "spawn one subagent per active agent". This is the fan-out machinery (merge/recall/consult).
- **Target:** binding (2) — "spawn a subagent" with an explicit inline-fallback. Per engine:
  Claude = parallel Agent calls; Codex = explicit-only request or `codex exec` script; Cursor =
  declarative `.cursor/agents/*.md`.
- **This is the real work and the real risk.** Not a find-replace — the merge fan-out (~96-line
  procedure) is exactly where non-Claude model fidelity is unverified. Neutralize the vocabulary
  here, but expect to also *test* it, not just rewrite it.

### 5. Skill invocation syntax — pervasive, implicit
- Every `/lr:<skill>` reference across docs. Not counted as one grep (it's the whole command
  vocabulary), but it's a real binding.
- **Target:** binding (5). Claude `/lr:boot`; Codex `$lr-boot` / picker; Cursor `/lr-boot` +
  `disable-model-invocation`. The `:` colon is likely invalid in Codex/Cursor skill names →
  `lr:` → `lr-` rename map lives in the adapter, docs refer to skills by role not literal syntax
  where possible.
- **Effort:** medium; mostly a naming/adapter concern, not procedure logic.

## Tier C — leave alone (Tier 2 / genuinely engine-gated)

### 6. Teammate detection `ps $PPID` / `--agent-id` — 7 sites, 3 files
- `agent-boot.md` (the detection step), `spawn-teammate.md`, `teammate-conventions.md`.
- Agent Teams is Claude-only. **Gate the agent-boot detection step by engine** (skip on
  Codex/Cursor); leave spawn-teammate/teammate-conventions untouched (Tier 2).

### 7. `--plugin-dir` / plugin-cache prose — 2 sites
- `docs/check.md`, `docs/doctor-stale-plugin-cache.md`. About Claude's install/cache model.
- Engine-specific by nature; each engine's install story differs. Adapter/per-engine doc, not a
  neutralization target.

### 8. "Claude Code" / "Claude" prose — 43 sites, 14 files
- Mixed. Some are Tier-2 feature docs (spawn-teammate, teammate-conventions) → leave. Some are
  incidental ("Claude Code loads this when the user runs...") → generalize to "the engine" during
  the relevant doc's pass. Not a standalone sweep; fold into the passes above.

## Summary

| Coupling | Sites | Tier | Nature |
|---|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | 103 | A | mechanical sweep + binding (1) |
| Subagent spawning | 66 | **B** | **semantic, high fidelity-risk**, binding (2) |
| "Claude"/"Claude Code" prose | 43 | C/A | fold into other passes |
| CLAUDE.md memory file | 12 | A | binding (4), init-centered |
| teammate detect (ps/agent-id) | 7 | C | engine-gate, don't port |
| Bash-tool timeout | 3 | A | binding (3) |
| `--plugin-dir` cache prose | 2 | C | per-engine, not neutralized |
| skill invocation `/lr:` | pervasive | B | binding (5), naming map |

**Read:** the count is dominated by Tier A (mechanical: `CLAUDE_PLUGIN_ROOT` alone is ~55% of all
hits) and one hard Tier B nucleus (subagent spawning, 66 sites, where fidelity risk actually
lives). Tier C is small and mostly stays Claude-only by design. The engine-adapter's 5 bindings
map 1:1 onto items 1–5 above — the whole port surface really is those five concepts, it's just
that concept (1) appears 103 times.

## See also
- `draft-port-codex.md` / `draft-port-cursor.md` — the port plans; Phase 0 owns this work.
- `multi-engine-portability-direction.md` — anchor direction.
