# lr-dev — SDLC Extension (active design direction)

Opened 2026-05-31 with the user. A major new direction: **`lr-dev`**, a module/mode of the `lr` plugin dedicated to development & SDLC automation. North star (user): convert the SDLC into a **dark factory** — software built internally and autonomously by lore agents, fed only inputs plus occasional follow-ups. Same family as `autonomous-agents-vision.md`: autonomous-agents is the *substrate/process* direction (always-on background workers); lr-dev is the *what-they-do-in-software-development* direction. They converge on the dark-factory end state.

**Status: active exploration; first prototype validated 2026-06-02; first in-plugin BETA feature shipped 2026-06-03 (AIQA/ULA, local commit `2f1e788` — v16 ship deferred); artifact-store direction evolved to the per-repo codex 2026-06-03, then renamed + purpose-elevated to the per-repo DF backbone 2026-06-05. The DF/ULA design thread is currently IN PROGRESS, held for continuation (see Open decisions and `df-ula-design-in-progress.md`).** This topic is an orienting pointer. The detailed design lives in the drafts and backlog listed under *Where the detail lives* — do not duplicate that detail here. This file is the anchor (analogous to how `autonomous-agents-vision.md` anchors the parked autonomous direction).

## Current leading direction (2026-06-05): the per-repo DF backbone, skills not agents

The artifact + knowledge store for a source repo is a **`<repo>-df`** repo (DF = **Dark Factory**) — the backbone/storage layer the Dark Factory runs on, holding *all* the context/knowledge/artifacts the DF needs that aren't in the source repo. It is a per-file-directory mirror of the source tree under a top-level **`artifacts/`** dir, lazily created (an absent dir means "not yet analyzed," so the tree is a sparse coverage map). Each file dir holds a narrative `index.md` (the "context" aspect) plus flat structured aspect subdirs (`ula/…` today — `aiqa/` is no longer a dir level). **No agent** — persistence is external (the DF repo) and procedures live in framework-level, aspect-scoped skills; an agent would have nothing of its own to custody. lr-dev standardizes the DF-repo layout + the procedures; the per-repo "instance" is the DF repo + its small config, not an agent instance. Full design: **`df-per-repo-backbone.md`**, with `ula-narrative-vs-structured-output.md` (why `index.md` exists). This **demotes the context-agent framing below** (now a prior step in the reasoning trail) and generalizes `quality-repo-architecture.md`'s quality repo into the DF repo. (The `<repo>-codex` name from 2026-06-03 is superseded by `<repo>-df`; design unchanged, only name + framing.)

**Prototype milestone (2026-06-02):** the §2 file-by-file quality workflow ran end-to-end against a real source file as a Claude Code dynamic Workflow script (`workdir/draft-lr-dev-file-quality-workflow.js`). Two iterations confirmed the pipeline shape and produced the §4 schema-conformant artifacts. Operational case validating the reframe: lore-aware bug verifiers killed 3 of 9 bugs as false-positives — including a "typo" that was actually a non-standard supplier-specific code — by tracing the actual caller graph. Without booting the per-repo context agent inside workflow subagents, the workflow would have generated "fixes" that broke real integration. Context-agent attach is therefore **not a nice-to-have**. Full lessons in `workflow-primitive-operational-notes.md` and `quality-repo-architecture.md`.

## Prior framing (2026-06-01 reframe): context agents on existing primitives — now demoted

> **Demoted 2026-06-03** by the DF-backbone direction above (then `codex`). The context-agent framing was a step in the reasoning, not the destination: once persistence is externalized to the DF repo and procedures live in skills, the agent has nothing of its own to custody (see `df-per-repo-backbone.md` § No agent — skills only, and `agent-split-only-when-forced.md`). Kept here for the trail and because several of its framings survive (objective/subjective cut as reflection-vs-skill discipline; one-store-per-repo; the QA-as-beachhead rationale below is unaffected). `framework-defined-role-pattern.md` stands as a pattern; lr-dev simply no longer instantiates it.

This 2026-06-01 reframe **expressed per-repo artifact knowledge as ordinary tailored agents — context agents — built entirely on primitives the framework already had.** It superseded the original three-tier / new-repo-kind / two-gate design (kept below as a labeled heavier alternative). Full detail: `workdir/draft-lr-dev.md` §1A; quality-feature alignment in `workdir/draft-lr-dev-quality.md`.

**The move.** Don't introduce "repo lore" as a new knowledge *tier* with its own repo kind and a two-gate write capability. Instead, one **context agent per source repo** (`<repo>-context`, e.g. `turbo-boost-context`) custodies that repo's artifact knowledge, and worker/specialist agents reach it via `/lr:attach` / `/lr:consult`.

**Why it dissolves the machinery.** The two-gate write capability was *reinventing, for the new tier, the write-isolation agents already have natively* — an agent's lore is written only by that agent, through reflect/merge. Drop the tier and the gate isn't simpler, it's unnecessary. Also gone: the `dev-repo-lore.md` descriptor + new repo kind, the cross-cutting migration work (no new repo kind for `/lr:update`/boot/version-check/auto-pull to walk — a context agent's normal `lore-repo.md` is already walked), the `role.md` `extensions` schema bump, and Gate A's bespoke enablement resolution. This is `framework-scope-vs-agent-scope.md` applied: reach for existing agent primitives before minting framework machinery.

**More on-identity.** "Repo lore" was a passive KB bound to a repo — in tension with `framework-as-engine-not-kb.md` and `agents-are-executors-first.md`. A context agent is an executor that *carries* knowledge.

**Team-shared property preserved by housing.** The one property worth protecting — repo knowledge being agent-agnostic (survives onboarding a fresh agent; eventually mergeable into the source repo) — is recovered by housing the context agent in a **per-source-repo agent repo (a domain)**: team-shared, cloned by anyone working on the repo, declared via `repos:` and pulled by `/lr:workspace-sync`. Condition: a *shared* per-repo agent repo, not a personal collection. Enablement/discovery stays a soft pointer in the source repo's `CLAUDE.md` → the context agent's repo remote (reusing `repos:` / workspace-sync, not bespoke gate resolution).

**One agent per repo, not two.** Product and technical are *filing categories, not identities* — a senior engineer holds both. So one context agent per repo, with `product/` ÷ `technical/` (+ a per-artifact file mirror) as category dirs in its single `lore/`, interlinked but separated (one home per fact, cross-link don't duplicate). See `agent-split-only-when-forced.md`.

**Activity breadth lives elsewhere.** The context agent is *pure knowledge custody, not a workflow orchestrator*. QA/coverage/bug-finding/review workflows travel with **separate specialist agents** (skills travel with them, per `knowledge-vs-skills-distinction.md`); ephemeral file/unit quality-analyst subagents do the labor. Specialist agents *attach* the context agent for understanding, do the work, and *feed discoveries back*.

**Role triad.** **hold** (product meaning+value, technical implementation, architecture→file) / **provide** (attach/consult) / **learn** (free — when a worker attaches it, per-agent finalization already makes the context agent reflect+merge its own session learnings; no new mechanism). The behavior of this recurring role is itself a framework-defined, thin-role-pointer construct — see `framework-defined-role-pattern.md`.

**Objective/subjective cut survives — as discipline, not a wall.** The original's most valuable idea (artifact-knowledge vs worker-experience) is kept, but enforced by **reflection discipline**: the context agent reflects what it learned *about the artifact*; worker agents reflect what they learned *doing the work*. Same line, drawn by role rather than by a permission boundary. General lesson: prefer enforcing a distinction by role-discipline over building mechanism when the framework's agent-driven nature already supplies the isolation.

**"Mode" decomposed away.** The original "lr-dev mode" conflated four things: (1) unlock writes, (2) extend finalization, (3) expose skills, (4) a centralized loaded operating doc. The reframe drops 1–3 (native ownership / normal reflect-merge / skills-with-specialists) and keeps only (4) — the framework-defined-role doc. See `framework-defined-role-pattern.md`.

Two reusable framings generalized out of this reframe (they apply beyond lr-dev): `framework-defined-role-pattern.md` and `agent-split-only-when-forced.md`.

## Why QA is the beachhead

First concrete, intentionally-safe feature: **automatically find bugs/inconsistencies and raise unit-test coverage**. QA is the correct beachhead, not just the easy one: a dark factory needs *trustable autonomy*, which needs *cheap automatic verification*. QA is the one SDLC activity that carries its own oracle (tests pass/fail, coverage moves, bugs reproduce) and has near-zero blast radius (tests additive, bug reports advisory). Bootstrap autonomy on the activity that checks itself.

## Heavier alternative (superseded): three-tier / new-repo-kind / two-gate

The original framing, now demoted. Kept for the reasoning trail and because individual pieces (the objective/subjective cut, the per-artifact mirror, the feature-catalog accretion shape) survive into the leading direction in lighter form. **Full superseded detail: `workdir/draft-lr-dev.md` §1A.** In brief, it proposed:

- **Three-tier knowledge model** — framework / **repo** / agent, lr-dev adding the middle tier; cut is objective-vs-subjective (repo lore = what's true about the artifact, agent lore = what the worker learned).
- **lr-dev as mode + two-gate write capability** — writing repo lore required (Gate A: repo lr-dev-enabled) ∧ (Gate B: agent in lr-dev mode), else read-only; mode = loaded context, by-convention enforcement.
- New **`dev-repo-lore.md`** descriptor + new repo *kind* (separate now → mergeable into the source repo later), 2-level product/technical taxonomy stored separately, per-artifact `.lore.md` mirror.
- Cross-cutting: migrations/auto-pull/version-check had to learn to walk the new repo kind.

Surviving framings that are *not* superseded (carried into the leading direction): **test scenarios as a bidirectional IR** (what-to-test decoupled from how; coverage ≠ meaningfulness — every "expected" must cite product-lore intent or tests merely canonize current/buggy behavior); **lr-dev as a growing feature catalog** (accretion discipline, same shape as `ailment-catalog-pattern.md`); **multi-lens review promoted to a reusable skill** (`lr:dev-review`, the user independently reinvented `parallel-reviewer-fanout-pattern.md`); **standardized deliverable-format rules** (stable IDs, `class: product|technical`, intent-source citation, confidence/status, real dry-run counts not zeros).

## Artifact + knowledge store: the DF repo (was three-repo, now two)

Under the DF-backbone direction the artifact side and the knowledge side **co-locate in one `<repo>-df` repo**, so the shape collapses to **two repos**:

1. **Source repo** — system under analysis; untouched.
2. **`<repo>-df`** — the per-file-directory mirror (under `artifacts/`) holding both the narrative `index.md` (knowledge/context aspect) and structured artifact aspects (`ula/`, future aspects). Composite-builds against the source so generated tests can exercise real code without copying it. Full pattern: **`df-per-repo-backbone.md`**.

(The earlier three-repo split — source / context-agent-repo / quality repo — is the prior framing; the context-agent repo dissolved and the quality repo generalized into the DF repo. Reasoning trail: **`quality-repo-architecture.md`**.)

Generated tests live **permanently** in the DF repo, not migrated into the source suite — drift between the two suites is information (missing human test or AI hallucination). The compliance bottleneck applies to *fixes*, not analysis. Resumability: lazy per-file dirs as a coverage map (the DF repo), or a per-file manifest with `lastAnalyzedSha` (quality-repo pattern).

## Where the detail lives

- `workdir/draft-lr-dev.md` — general concept. **§1A carries the leading-direction reframe** (context agents on existing primitives); the rest carries the superseded knowledge model, mode/capability mechanism, review skill, integration seams.
- `workdir/draft-lr-dev-quality.md` — first feature: file-by-file workflow (file/unit quality-analyst roles), the three schemas, format rules. Already aligned with the reframe.
- `framework-improvements-backlog.md` § lr-dev — backlog home.

> Note (2026-06-01): the drafts were updated this session with the reframe — `lr-dev-direction.md` references them, it does not restate them.

## Open decisions (carry to next session)

**DF/ULA thread (IN PROGRESS, 2026-06-05 — held for continuation; full state in `df-ula-design-in-progress.md`):**
- **Provenance Header field set** — mostly decided, not yet locked into a schema. Next: lock it (into the JSON Schema). See `provenance-header-concept.md`.
- **Incremental run algorithm** — SHA-compare + per-unit merge flow sketched, not detailed. See `ula-designed-for-multiple-runs.md`.
- **ULA artifact granularity** — leaning per-file (unit as a field), user said "not sure." Decide next time. See `ula-artifact-granularity.md`.
- **Plugin-side naming ripple** — `dev/aiqa/` module + `/lr:dev-aiqa-repo-init` skill name now out of step with the flattened `ula/` tree and the `-df` repo rename. Parked. See `df-per-repo-backbone.md`.
- **DF glossary persistence** — `workdir/draft-df-glossary.md` proposed as the working home but **not created** (user held approval); starter glossary kept in `df-ula-design-in-progress.md` for now.

**Carried from the demoted context-agent framing (mostly moot under the DF direction, kept for the trail):**
- ~~Generator path for context agents~~ — moot; no context agent. The per-repo instance is a DF repo + config, emitted by an aspect-agnostic DF-repo-init skill.
- Scenario→code binding; generated-vs-human test de-dup — still open under any framing.

## Operational note

The user has a **second, concurrent idea** to explore in a separate session that should carry the essential points from this one — these drafts + this topic are that carry-forward. Next natural concrete move on *this* thread: ground the test-scenario schema on the `My-Turbo-Boost-Switcher` mouse repo, using its context agent as the knowledge custodian.

## First In-Plugin BETA Feature: AIQA/ULA (2026-06-03)

Two BETA skills committed to `lore-framework` locally (`2f1e788`; v16 ship deferred):
- `/lr:dev-aiqa-repo-init` — creates a sibling `<repo>-aiqa` quality repo.
- `/lr:dev-ula-file <file>` — single-file unit-level analysis: split → find bugs (step A) → generate scenarios clean-room (step B) → gap analysis (step C).

Key design decisions: `dev-` skill prefix required (not just grouping); module subtree layout (`dev/aiqa/` for docs/prompts/schemas/workflows) rather than global `docs/`; artifacts are machine-readable YAML; single-source discipline — schemas enforce structure, prompts enforce semantics, `artifact-specs.md` is a pointer only. See `aiqa-ula-feature.md`, `dev-module-conventions.md`.

## See Also

- `df-per-repo-backbone.md` — **current leading direction** for the artifact + knowledge store; the DF backbone, skills not agents.
- `df-ula-design-in-progress.md` — the DF/ULA thread's in-progress continuation state + working glossary.
- `provenance-header-concept.md`, `ula-designed-for-multiple-runs.md`, `ula-artifact-granularity.md` — the 2026-06-05 ULA design findings (self-describing artifacts, git-history run store, per-file granularity lean).
- `ula-narrative-vs-structured-output.md` — the two ULA output kinds; the narrative kind is the DF repo's `index.md` aspect.
- `framework-defined-role-pattern.md` — the recurring-role / thin-role-pointer pattern; stands, but lr-dev no longer instantiates it (the DF repo needs no agent).
- `agent-split-only-when-forced.md` — the "no agent" landing is an instance: no forcing pressure once persistence is in the DF repo.
- `quality-repo-architecture.md` — prior three-repo framing; the quality repo generalized into the DF repo, the context-agent repo dissolved.
- `workflow-primitive-operational-notes.md` — operational lessons from the first working file-by-file quality prototype (boot-not-attach in workflow subagents, right-size the verify fan-out, persistence is parent's job).
- `autonomous-agents-vision.md` — sibling major direction; same dark-factory end state, different axis (process/substrate vs SDLC activity).
- `framework-scope-vs-agent-scope.md` — the rule the reframe applies (reach for existing agent primitives before minting framework machinery).
- `framework-as-engine-not-kb.md`, `agents-are-executors-first.md` — why a context agent (executor carrying knowledge) is more on-identity than a repo-bound passive KB.
- `team-shared-knowledge-principle.md` — the agent-agnostic property the context agent preserves by being housed in a shared per-repo agent repo.
- `knowledge-vs-skills-distinction.md` — skills travel with specialist agents; the context agent is knowledge custody only.
- `parallel-reviewer-fanout-pattern.md` — the review pattern promoted into the `lr:dev-review` skill.
- `ailment-catalog-pattern.md` — accretion discipline modeled for the lr-dev feature catalog.
- `framework-improvements-backlog.md` § lr-dev — running backlog.
