# Claude-Specific Coupling Inventory + Port Tiering

The "real list" behind the Phase-0 estimate for `multi-engine-portability-direction.md`. Full detail lives in `workdir/claude-specific-inventory.md`; this is the durable summary.

## Grep counts (2026-07-04, `lore-framework/docs` + `skills`)

| Coupling | Sites | Tier | Nature |
|---|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | 103 (23 SKILL.md + 80 docs) | A | mechanical → `<framework-root>` |
| Subagent spawning | 66 across 12 docs | **B** | semantic, high fidelity-risk |
| "Claude"/"Claude Code" prose | 43 / 14 files | C/A | fold into other passes |
| `CLAUDE.md` memory file | 12 / 4 files | A | → `AGENTS.md` (init-centered) |
| teammate detect (`ps`/`--agent-id`) | 7 / 3 files | C | engine-gate, don't port |
| Bash-tool timeout | 3 / 2 files | A | → "bound the command's runtime" |
| `--plugin-dir` cache prose | 2 | C | per-engine, not neutralized |
| skill invocation `/lr:` | pervasive | B | naming map (`lr:` → `lr-`) |

Tier A = mechanical find/replace or near-it. Tier B = semantic binding where model fidelity actually lives. Tier C = engine-gated, deliberately *not* ported (stays Claude-only).

## The load-bearing insight

The whole port surface is **5 adapter bindings** (framework-root, subagent-spawn, runtime-bounding, memory-file, invocation-syntax — the same five listed in `multi-engine-portability-direction.md` § Architectural levers). The *count* is dominated by Tier A mechanical work (framework-root alone ≈55% of hits) plus **one hard Tier B nucleus: subagent spawning.** That nucleus is where model fidelity actually lives (the ~96-line merge fan-out in `process-merge.md`) and it's not a find-replace — Claude fires N parallel Agent calls, Codex is explicit-request-only, Cursor uses declarative `.cursor/agents/`.

## De-risking already done

- **Framework-root (Tier A): validated** — see `framework-root-self-location-validated.md`.
- **Subagent path-substitution: validated on haiku** — the fan-out docs embed `<framework-root>/docs/agent-boot.md` inside the subagent brief and haiku correctly substitutes the resolved absolute path. So the *path* half of Tier B is fine; the remaining Tier B work is purely the **spawn-mechanism binding** (`docs/engines/`).

## Entanglement found

`CLAUDE.md` → `AGENTS.md` is entangled with `test_18_init` (it asserts `CLAUDE.md`); that binding must be applied **with the test updated in lockstep** — it belongs in the adapter pass, not the mechanical sweep. See `port-landing-next-steps.md`.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction; § Architectural levers names the same five bindings.
- `framework-root-self-location-validated.md` — the biggest Tier A slice, already validated.
- `port-landing-next-steps.md` — how the tiered work lands across the next sessions.
- `workdir/claude-specific-inventory.md` — the full per-site inventory.
- `workdir/draft-port-codex.md`, `workdir/draft-port-cursor.md` — the per-engine phased plans the tiering feeds.
