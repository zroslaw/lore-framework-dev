# Draft — Automated Testing Pipeline (all engines)

Status: DRAFT, written 2026-07-03. Companion to `draft-port-codex.md` and `draft-port-cursor.md`.
Purpose: one shared test harness for the framework, run against every engine (Claude Code first,
then Codex and Cursor in their dedicated port sessions).

## Core idea

The framework is prose executed by a model, so testing = run the engine for real, then check
what it did to the files. Every procedure's output is files + git state with a defined shape,
so a script can verify the result. No judging of model prose needed for most checks.

## Three layers

1. **Script tests** — deterministic Python (stdlib only), for framework scripts.
   Exists: `tests/test_wait.py`. Free, per-commit CI.
2. **Lint checks** — a script version of the static `/lr:check` subset: SKILL.md frontmatter
   conforms to the agentskills.io standard, doc cross-references resolve, manifests match
   `VERSION`, placeholder vocabulary consistent. Plus a **leakage linter**: grep procedure docs
   for Claude-specific phrases that belong behind the `docs/engines/` adapter (turns the port
   plans' Phase 0 one-time sweep into a permanent regression guard). Free, per-commit CI.
3. **Lifecycle scenarios** — the substance. Headless engine runs against a fixture workspace,
   scripted assertions afterwards. Costs API money; run manually / nightly, not per-commit.

## Layer 3 harness = shared scenarios + thin per-engine drivers

**Scenarios are engine-neutral.** One list, one set of assertions. Each scenario has exactly
three parts — that's the whole spec, no long prose:

- **fixture** — what the throwaway test workspace looks like
- **prompt** — what we tell the engine
- **assertions** — a script checking files/git afterwards

**Fixture:** a temp workspace built by script — synthetic agent repo (small known lore graph,
~10 cross-referenced topics), a **local bare repo as `origin`** (pull/push tested with zero
network), pinned framework checkout installed per engine.

**Driver (per engine)** binds only:
- skill install (plugin / `.agents/skills/` symlink / GitHub-install)
- headless invocation (`claude -p` / `codex exec` / `cursor-agent`)
- skill-name syntax in prompts (`/lr:boot` / `$lr-boot` / `/lr-boot`)

This mirrors the `docs/engines/` five-bindings adapter convention — same seam, code-side.

**Scoring: graded, not boolean.** Each scenario runs N trials (3–5); report pass rate per
procedure per engine/model. Output = the **fidelity scorecard** — the mechanized, repeatable
form of the "model-fidelity report" both port drafts call for in Phase 3. Low scores feed the
parked simplification theme (`framework-improvements-backlog.md`).

## Scenario catalog v1

### Boot & freshness
| # | Scenario | Key check |
|---|---|---|
| 1 | Boot happy path | agent confirms role; read role.md + lore-context.md |
| 2 | Boot pulls fresh commits | remote ahead → local updated after boot |
| 3 | Boot degraded (no remote / pull fails) | boot completes, warning shown |
| 4 | Boot unknown agent | clean error + list of available agents |
| 5 | Boot with version mismatch | migrations applied, repo stamped |
| 6 | Upgrade gate on dirty tree | upgrade defers, nothing overwritten |

### Lore operations
| # | Scenario | Key check |
|---|---|---|
| 7 | Recall with hint | relevant fixture topic named |
| 8 | Consult another agent | answer + file pointers; consultant not left loaded |
| 9 | Attach a guest | guest lore reachable; recall covers both agents |

### Finalization
| # | Scenario | Key check |
|---|---|---|
| 10 | Reflect | `reflections/` files exist, right shape |
| 11 | Merge | reflections integrated into `lore/` + `lore-context.md`; reflections removed; nothing outside agent subtree touched |
| 12 | Summarize | session summary file written |
| 13 | Finalize end-to-end | one commit per touched repo, pushed to remote |
| 14 | Concurrent finalize collision | push rejected → resolved; both sessions' lore survives |
| 15 | Finalize with guest attached | both agents reflected + merged, host first |

### Repo & workspace
| # | Scenario | Key check |
|---|---|---|
| 16 | create-repo | valid scaffold (`lore-repo.md`, dirs) |
| 17 | create-agent | valid agent dir (role.md, lore-context.md, lore/, workdir/) |
| 18 | init | marker block written to CLAUDE.md/AGENTS.md |
| 19 | workspace-sync | missing declared repo cloned; existing repos pulled |
| 20 | check | seeded violation caught |
| 21 | update | version walk runs, stamps correctly |

### Tier 2 — Claude Code only
wait/emit round-trip, spawn-teammate, df-repo-init, df-ula-file.

Note: same scenario may pass differently *inside* per engine (e.g. merge via parallel
subagents on Claude/Cursor, inline on Codex). Fine — assertions check outcome, not method.

Not covered by design: each engine's skill-invocation UX (pickers, prefixes, implicit
invocation). That stays a thin manual per-engine checklist.

## Tracking rules

1. Catalog lives in `tests/scenarios/` — one dir per scenario; catalog table in `tests/README.md`.
2. **Ship discipline:** any release that changes behavior adds or updates a scenario.
   No scenario → not shipped. (Joins the VERSION-bump checklist in `role.md`.)
3. Later: `/lr:check` coverage check — every Tier-1 skill maps to ≥1 scenario.

## Sequencing

Slots in as **Phase 0.5** of the port plans — after shared engine-neutral groundwork, before
either port. Build fixture + harness + **Claude Code driver first** + 3–4 core scenarios
(boot, reflect+merge, finalize, update); baseline on Claude. Reasons Claude goes first:
- Codex/Cursor scores mean nothing without Claude's baseline (merge fidelity is unverified
  even on Claude).
- Gives the framework release-time regression testing it never had — rerun before every
  `VERSION` bump.

Each port's Phase 1 acceptance criterion then becomes "scorecard acceptable on engine X"
instead of manual lifecycle walks.

## Placement & cost

- Everything lives in `lore-framework-dev/tests/` — plugin stays slim.
- Layers 1–2: per-commit CI, free.
- Layer 3: local runner first (`tests/run-lifecycle.sh --engine claude --scenario merge`),
  nightly/scheduled CI later if auth allows.

## Open questions

- Codex / Cursor CLI auth in CI — feasible headless? (Worst case Layer 3 stays a local
  pre-release gate; still a big step up.)
- LLM-as-judge for content quality (is a merged topic coherent?) — only where structural
  checks can't answer; keep minimal.
- N trials per scenario vs cost — start with 3.
- Fixture lore graph contents — needs deliberate recall-able facts and cross-references.

## See also

- `draft-port-codex.md`, `draft-port-cursor.md` — the port plans this gates.
- `multi-engine-portability-direction.md` — anchor topic.
- `graduated-verification-confidence.md` — graded-scoring precedent.
- `parallel-reviewer-fanout-pattern.md` — the (model-review) pre-ship discipline this
  complements with empirical regression testing.
