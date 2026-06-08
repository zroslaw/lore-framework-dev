# AIQA / ULA — First In-Plugin lr-dev Module

**AIQA** = umbrella for AI-based quality assurance, organized by testing *level*. First level shipped: **ULA = Unit-Level Analysis**. Future levels: integration (ILA), e2e, feature/flow. The module is a **BETA** in `lore-framework` (built on local commit `2f1e788`, renamed dev→df, then **shipped in v16**, 2026-06-08, manifests `1.16.0`). Still BETA — schemas may change without migration.

**DF-backbone framing (2026-06-03, rename landed 2026-06-07):** AIQA is **one aspect** of the per-repo DF backbone (`<repo>-df`, DF = Dark Factory) — its structured artifacts live under `<repo>-df/repo-lore/<file>/ula/…` (the `aiqa/` dir level was flattened away 2026-06-05; top dir is now `repo-lore/` not `artifacts/`), alongside (eventually) other aspects and the per-file narrative landing `file-lore.md`. The skills/workflows stay; the framing generalizes. See `df-per-repo-backbone.md`.

## DF Rename (shipped in v16, 2026-06-08)

The whole module was rebranded to the **DF (Dark Factory)** north star, shipped in v16 (`lore-framework` commit `005f18a`):

- module dir **`dev/` → `df/`**; skill prefix **`df-`** supersedes `dev-` (still disambiguates from `lr:init`). See `df-module-conventions.md`.
- skills: `/lr:dev-aiqa-repo-init` → **`/lr:df-repo-init`**; `/lr:dev-ula-file` → **`/lr:df-ula-file`**.
- output repo `<repo>-aiqa` → **`<repo>-df`**; config `aiqa.config.yaml` → **`df.config.yaml`**.
- **`repo-init` graduated** out of `aiqa/` to `df/repo-init.md` — it stands up the *whole* `<repo>-df` backbone (config + `repo-lore/` with `.gitkeep` + `README.md`), not just QA, so it's DF-core and aspect-agnostic.
- **AIQA stays** as the umbrella concept and the aspect subdir `df/aiqa/` (DF ⊃ AIQA ⊃ ULA). Only the repo + skills + module dir went `df-`.

## Two BETA Skills

`df-` prefix is required for all lr-dev/SDLC tools — `lr:init` already exists, so the prefix is not just grouping, it's necessary disambiguation.

- **`/lr:df-repo-init`** — scaffolds the sibling `<repo>-df` backbone repo (`df.config.yaml` + `README.md` + empty `repo-lore/`). Asks before creating. Aspect-agnostic (DF-core, not QA-specific).
- **`/lr:df-ula-file <file>`** — the ULA single-file pass.

## ULA Single-File Pass Flow

Split file → units (unit = unit-of-testing, e.g. a method; slug id fixed at split — it *tags each unit's entry* in the per-file artifacts, it is NOT a directory) → per unit, **one agent** runs five ordered steps (A→B→C→D→E):

- **Step A — Find bugs** → `bugs.yaml`. Per finding: `id` / `title` / `impact-summary` (plain-language) / `description` (deep technical) / `nature` (product|technical) / `severity` / `confidence` (+ optional `category`/`tags`); plus `crossUnit[]` for bugs noticed in other units/interactions. Excludes bugs encoded as "expected" behavior (those land in gap analysis). Full model: `ula-finding-schema.md`.
- **Step B — Generate scenarios** (CLEAN-ROOM — must not read existing tests; excludes any behavior tied to a step-A bug) → `scenarios.yaml`. Fields: id / title / description / `coverage-intent[]` of `{kind∈statement|branch|condition|path, target}`.
- **Step C — Gap analysis** (may read tests now) → `gap.yaml`. Two-directional: `not-implemented` = ULA scenarios with no matching test; `ula-missed` = existing tests no scenario anticipated. **The mismatch is the quality signal, not the match.** `considered-tests` lists what was scanned.
- **Step D — Verify bugs** (v16; past clean-room, may read the whole repo). Re-investigate each Step A bug for real-ness + *real system impact*; revise `severity` (→ `negligible` if real-but-harmless), or move non-bugs to `dismissed[]` (never delete).
- **Step E — Verification guardrail** (v16). Confirm every Step A bug ended up in exactly one of `bugs[]` / `dismissed[]`.

After persist, the skill runs an **independent aggregation-level re-verification**: a fresh subagent re-applies D/E across all units with whole-file context; rejects move to `dismissed[]` with `dismissed-by: aggregator`. See `ula-bug-verification-track.md`.

Steps are ordered (B needs A's bug list to exclude; C needs B's scenarios). One agent for cost control, but written as five separable prompt blocks (`prompts/step-{a,b,c,d,e}-*.md`) so they split into independent parallel agents trivially — the seam is "steps communicate only via written artifacts, never in-context memory."

## Artifact Conventions

- Format: YAML, machine-readable.
- **Per-file, grouped (LOCKED 2026-06-07):** one `bugs.yaml` / `scenarios.yaml` / `gap.yaml` per *file*, each a `{ source-sha, config, units: [ {unit, signature, …} ] }` shape — the unit is a *field*, not a folder. One Provenance Header per file (see `provenance-header-concept.md`). No per-unit directories. See `ula-artifact-granularity.md`.
- **Provenance Header atop each artifact** — `source-sha` (= `git hash-object` of the analyzed working-tree bytes) + extensible `config` bag. Replaces the earlier per-report `unit`+`signature` header. Makes git-history-as-run-store work; see `provenance-header-concept.md`, `ula-designed-for-multiple-runs.md`.
- No file-level manifest — the lazy per-file directory tree under `repo-lore/` IS the coverage map.
- Single-source discipline: structure → `schemas/*.json` (JSON Schema, machine-enforced — incl. `provenance.schema.json`); authoring semantics → `prompts/*.md`; `artifact-specs.md` is a pointer only — no restating, no drift.

## End-to-End Validation (2026-06-03)

Simulated via Sonnet subagents (dynamic Workflow runtime not available in this session — see `workflow-primitive-operational-notes.md` § Dynamic Workflow availability). Tested on `My-Turbo-Boost-Switcher/Turbo Boost Disabler/SystemCommands.m`, unit `readCurrentCpuFreq`:

- 4 bugs produced, 3 confirmed real against source (off-by-one NSRange, NSUInteger underflow crash, discarded sudo failure).
- 9 scenarios, consistent gap analysis.
- Bug/scenario separation held: no scenario encoded buggy behavior as expected.

A second single-unit pass on the same file's `run-task-as-admin` unit surfaced **six bugs** (incl. an always-returns-YES error-swallowing chain and a macOS-14+ deprecated-API break) and demonstrated the narrative-vs-structured output split firsthand. Full account: **`ula-validated-turbo-boost-switcher.md`**; the narrative-output insight: **`ula-narrative-vs-structured-output.md`**. Takeaway: a single well-chosen unit is already worth a pass.

**Real end-to-end run (2026-06-07, post-restructure):** the actual `df-ula-file` workflow (not simulated) ran clean on `My-Turbo-Boost-Switcher/CheckUpdatesHelper.m` after the two workflow fixes, producing the exact `repo-lore/<file>/ula/{bugs,scenarios,gap}.yaml` per-file/grouped layout with valid Provenance Headers (`source-sha` == live `git hash-object`). 5 units, ~20 Objective-C bugs. Caveat: that file has *no existing tests*, so gap Direction B (`ula-missed`) and the clean-room comparison path are still unstressed — re-validate on a file with tests. See `ula-validated-turbo-boost-switcher.md`.

## Plugin Layout

`lore-framework/df/`: `repo-init.md` (DF-core), `README.md`, and the `aiqa/` aspect subtree — `df/aiqa/`: README, `ula-file.md`, `artifact-specs.md`, `prompts/`, `schemas/` (incl. `provenance.schema.json`), `workflows/ula-file-pass.js`. See `df-module-conventions.md` for the structural pattern.

**Workflow runtime gotchas baked into `ula-file-pass.js`:** the `args`-string parse guard and the `$schema`-strip (`noMeta`) — see `df-module-conventions.md` § DF Workflow-Authoring Checklist and `workflow-primitive-operational-notes.md`.

## See Also

- `df-module-conventions.md` — how `df/` modules are structured in the plugin (+ DF workflow-authoring checklist).
- `lr-dev-direction.md` — the broader SDLC direction this is the first shipped feature of.
- `workflow-primitive-operational-notes.md` — operational lessons from the ULA prototype; dynamic Workflow availability caveat.
- `df-per-repo-backbone.md` — the per-repo DF backbone; AIQA/ULA is one aspect (`ula/`) of it.
- `ula-validated-turbo-boost-switcher.md` — real single-unit + end-to-end validation.
- `ula-narrative-vs-structured-output.md` — the two ULA output kinds; narrative motivates `file-lore.md`.
- `ula-designed-for-multiple-runs.md`, `provenance-header-concept.md`, `ula-artifact-granularity.md` — the ULA-as-repeated design (self-describing artifacts, git-history run store, per-file granularity LOCKED).
- `quality-repo-architecture.md` — the three-repo artifact side; the quality repo is now generalized into the DF repo.
- `skill-doc-pattern.md` — the base pattern; `df-module-conventions.md` adds the module-subtree variant.
