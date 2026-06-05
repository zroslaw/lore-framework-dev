# AIQA / ULA — First In-Plugin lr-dev Module

**AIQA** = umbrella for AI-based quality assurance, organized by testing *level*. First level shipped: **ULA = Unit-Level Analysis**. Future levels: integration (ILA), e2e, feature/flow. Committed locally to `lore-framework` as commit `2f1e788`; v16 ship deferred while AIQA is in BETA.

**DF-backbone framing (2026-06-03, renamed 2026-06-05):** AIQA is now positioned as **one aspect** of the per-repo DF backbone (`<repo>-df`) — its structured artifacts live under `<repo>-df/artifacts/<file>/ula/…` (the `aiqa/` dir level was flattened away 2026-06-05), alongside (eventually) other aspects and the per-file narrative `index.md`. `dev-aiqa-repo-init` becomes (or is joined by) an aspect-agnostic DF-repo-init. The skills/workflows stay; the framing generalizes. See `df-per-repo-backbone.md`.

## Two BETA Skills

`dev-` prefix is required for all lr-dev/SDLC tools — `lr:init` already exists, so `dev-` is not just grouping, it's necessary disambiguation.

- **`/lr:dev-aiqa-repo-init`** — creates a sibling `<repo>-aiqa` repo (config + `ula/` tree). Asks before creating. Holds all AIQA config, artifacts, and AI-generated tests.
- **`/lr:dev-ula-file <file>`** — the ULA single-file pass.

## ULA Single-File Pass Flow

Split file → units (unit = unit-of-testing, e.g. a method; slug id fixed at split, becomes its dir) → per unit, **one agent** runs three ordered steps:

- **Step A — Find bugs** → `bugs.yaml`. Fields: id / title (what+impact) / description (repro + components). Excludes bugs encoded as "expected" behavior (those land in gap analysis).
- **Step B — Generate scenarios** (CLEAN-ROOM — must not read existing tests; excludes any behavior tied to a step-A bug) → `scenarios.yaml`. Fields: id / title / description / `coverage-intent[]` of `{kind∈statement|branch|condition|path, target}`.
- **Step C — Gap analysis** (may read tests now) → `gap.yaml`. Two-directional: `not-implemented` = ULA scenarios with no matching test; `ula-missed` = existing tests no scenario anticipated. **The mismatch is the quality signal, not the match.** `considered-tests` lists what was scanned.

Steps are ordered (B needs A's bug list to exclude; C needs B's scenarios). One agent for cost control, but written as three separable prompt blocks (`prompts/step-{a,b,c}-*.md`) so they split into independent parallel agents trivially — the seam is "steps communicate only via written artifacts, never in-context memory."

## Artifact Conventions

- Format: YAML, machine-readable.
- No SHAs or line ranges (dropped deliberately; coarse resumability for now).
- No file-level manifest — the directory tree IS the record (`file→dir`, `unit-slug→subdir`). Reports carry their own `unit`+`signature` header.
- Single-source discipline: structure → `schemas/*.json` (JSON Schema, machine-enforced); authoring semantics → `prompts/*.md`; `artifact-specs.md` is a pointer only — no restating, no drift.

## End-to-End Validation (2026-06-03)

Simulated via Sonnet subagents (dynamic Workflow runtime not available in this session — see `workflow-primitive-operational-notes.md` § Dynamic Workflow availability). Tested on `My-Turbo-Boost-Switcher/Turbo Boost Disabler/SystemCommands.m`, unit `readCurrentCpuFreq`:

- 4 bugs produced, 3 confirmed real against source (off-by-one NSRange, NSUInteger underflow crash, discarded sudo failure).
- 9 scenarios, consistent gap analysis.
- Bug/scenario separation held: no scenario encoded buggy behavior as expected.

A second single-unit pass on the same file's `run-task-as-admin` unit surfaced **six bugs** (incl. an always-returns-YES error-swallowing chain and a macOS-14+ deprecated-API break) and demonstrated the narrative-vs-structured output split firsthand. Full account: **`ula-validated-turbo-boost-switcher.md`**; the narrative-output insight: **`ula-narrative-vs-structured-output.md`**. Takeaway: a single well-chosen unit is already worth a pass.

## Plugin Layout

`lore-framework/dev/aiqa/`: README, `repo-init.md`, `ula-file.md`, `artifact-specs.md`, `prompts/`, `schemas/`, `workflows/ula-file-pass.js`. See `dev-module-conventions.md` for the structural pattern.

## See Also

- `dev-module-conventions.md` — how `dev/` modules are structured in the plugin.
- `lr-dev-direction.md` — the broader SDLC direction this is the first shipped feature of.
- `workflow-primitive-operational-notes.md` — operational lessons from the ULA prototype; dynamic Workflow availability caveat.
- `df-per-repo-backbone.md` — the per-repo DF backbone; AIQA/ULA is one aspect (`ula/`) of it.
- `ula-validated-turbo-boost-switcher.md` — real single-unit validation (six bugs).
- `ula-narrative-vs-structured-output.md` — the two ULA output kinds; narrative motivates `index.md`.
- `ula-designed-for-multiple-runs.md`, `provenance-header-concept.md`, `ula-artifact-granularity.md` — the ULA-as-repeated design (self-describing artifacts, git-history run store, granularity lean).
- `quality-repo-architecture.md` — the three-repo artifact side; the quality repo is now generalized into the DF repo.
- `skill-doc-pattern.md` — the base pattern; `dev-module-conventions.md` adds the module-subtree variant.
