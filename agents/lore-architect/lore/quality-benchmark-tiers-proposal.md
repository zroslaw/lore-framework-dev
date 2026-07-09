# Quality Benchmark Tiers — Regular vs Deep (PROPOSAL, not yet built)

**Status: upcoming task, uncommitted local note (2026-07-08). Do not treat as shipped. Delete this topic and remove the `lore-context.md` pointer once implemented.**

User wants the quality benchmark (`tests/quality/`) restructured so each release covers a representative model per engine, and a full engine×model matrix is available on demand for comparison.

## The two tiers

**Regular check — runs for every release.** Each engine at its *cheapest usable* model (the representative config a real user would run):

| Engine | Regular model |
|---|---|
| Claude | sonnet |
| Codex | gpt-5.4-mini |
| Cursor | composer-2.5 |

Notes: haiku is deliberately *excluded* from the regular Claude check — it's too weak for this kind of development ("not intended for it"), so it is not the cheapest *usable* model; sonnet is. Cursor's regular model is its native **composer-2.5**, not sonnet — composer-2.5 is the representative Cursor config and empirically the stronger one (see § Motivating data).

**Deep check — explicit user request only, never automatic.** The full matrix, run to compare model tiers within and across engines:

| Engine | Deep models |
|---|---|
| Claude | haiku, sonnet, opus-4.8 |
| Codex | gpt-5.4-mini, gpt-5.4 |
| Cursor | composer-2.5, sonnet |

Rationale for including weak/expensive tiers: the user explicitly wants Claude-on-haiku results *even though haiku is not a dev-grade model*, purely to compare against sonnet and opus-4.8 on the same catalog. Same spirit for gpt-5.4 alongside gpt-5.4-mini on Codex, and sonnet alongside composer-2.5 on Cursor.

## Design points to settle when building

- **Gating:** regular is a **ship gate** (folds into the pre-ship empirical-verification discipline in `role.md`); deep is invoked only on explicit user ask. Likely a second env flag, e.g. keep `LR_QUALITY=1` for regular and add `LR_QUALITY_DEEP=1` (or a `--deep` mode) for the full matrix.
- **Matrix runner:** the harness today runs **one model per invocation** — `harness.py` sets `MODEL = LR_TEST_MODEL or ("gpt-5.4-mini" if codex else "sonnet")`. Both tiers need a loop over an (engine, model) list rather than a single run. The per-engine *regular* default should also change so a bare `LR_ENGINE=cursor` run picks composer-2.5, not sonnet (mirror how codex already defaults to its native gpt-5.4-mini).
- **Cost:** deep is the expensive one (6 configs × probe set × judge). Keep it opt-in; log which configs ran so partial matrices (e.g. an engine out of tokens) are visible, not silent.
- **Codex caveat:** the v24 Codex quality leg is still unrun (tokens exhausted); whatever we build, the Codex regular leg inherits that pending state until tokens return.
- **Blocked on the v2 probe-gap fix (2026-07-09):** the catalog this restructure would lock in is
  the v2 catalog (`quality-benchmark-v2-catalog.md`), and two of its probes
  (P12-banned-library-avoidance, P16-workdir-tool-reuse) still show a ceiling effect with zero
  discrimination — see `quality-benchmark-v2-known-probe-gaps.md`. Don't build the tier
  restructure on top of the catalog until those two are reworked and re-run.

## Motivating data (2026-07-08 and prior runs, haiku judge)

- Claude + sonnet: behavior uplift **+62.5%** (treatment S3 100%, control 37.5%).
- Cursor + composer-2.5 (07-07): **+75.0%** — the strongest result.
- Cursor + sonnet (07-08): **+37.5%** — same model as Claude, much weaker on Cursor.
- composer-2.5 beating sonnet *on Cursor* is a concrete instance of **model–engine fit beats model tier** (see `benchmark-findings-engines-models.md`, `quality-benchmark-feature.md`) — the reason Cursor's regular model must be its native one.

## See Also

- `quality-benchmark-feature.md` — the benchmark's design and gating.
- `benchmark-findings-engines-models.md` — the model–engine fit finding.
- `quality-benchmark-v2-known-probe-gaps.md` — the open blocker on building this.
- `framework-improvements-backlog.md` — where this lands once picked up.
