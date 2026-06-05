# Quality Repo as a Distinct Companion to the Source Repo

> **Evolved 2026-06-03, renamed + elevated 2026-06-05 — see `df-per-repo-backbone.md`.** This topic's "quality repo" (repo #3 below) generalized into the per-repo **DF backbone** (`<repo>-df`, DF = Dark Factory; interim name `<repo>-codex`): a per-file-directory mirror (under `artifacts/`) holding *all* artifact aspects (quality under `ula/`, narrative context in `index.md`), not just quality, and framed as the storage layer the Dark Factory runs on. And the separate "context agent" (repo #2 below) was **dissolved** — its knowledge moved into the DF repo's `index.md`, custodied by aspect-scoped *skills* rather than an agent. So the live shape is **two repos** (source + DF repo), not three. The two-vs-three reasoning below remains useful background — but read it knowing the artifact side and the knowledge side now co-locate in the one DF repo.

When automated quality artifacts (per-file analysis reports, bug catalogs, scenario catalogs, AI-generated tests) cannot land in the source repo — typical causes are strict review/compliance regimes (SOX-style mandatory human review, audit trails), code-ownership constraints, package-publishing constraints, or third-party code — the original separation was a **three-repo architecture**:

1. **Source repo** — the system under analysis. Untouched by lr-dev. Has its own human-written tests.
2. **Per-repo context agent** — lives in a shared per-source-repo agent repo (a domain), housed alongside its peers per `plugin-vs-agent-repo-separation.md`. Holds accumulated knowledge about the source repo: caller patterns, supplier/integration quirks, known issues, test conventions, lessons from prior sweeps. (See `lr-dev-direction.md`, `framework-defined-role-pattern.md`.)
3. **Quality repo** — a new, separate, non-restricted repo holding all quality artifacts: per-file reports, bug catalog, scenario catalog, gap analyses, AI-generated tests, manifest of analysis state. Composite-builds against the source repo so generated tests can exercise real code without copying it.

## Why three, not two

The instinct to combine "context agent" + "quality repo" into one repo is wrong. They have different lifecycles and different audiences:

- The context agent's lore is **knowledge** — what the system knows. It belongs with the agent's peers in agent-repo conventions; written via reflect/merge.
- The quality repo holds **artifacts and runnable tests** — what the system *produced*. It is not lore; it is output. Mixing them confuses the agent-repo schema and pollutes lore with run snapshots.

This is the same axis as `plugin-vs-agent-repo-separation.md`, applied at a different level: separate repos by lifecycle, not by topical proximity.

## Why the quality repo is not lore

A lore agent repo holds `lore/`, `workdir/`, `sessions/` — knowledge structures meant to evolve through reflection/merge. The quality repo holds File Reports, bug entries, generated test files — produced mechanically by the workflow, curated by humans through triage. None of those go through reflection. Treating them as lore would force them through a process they don't fit.

## Generated tests as a permanent safety net, not a replacement

When the source repo already has a human-written test suite (the common case), AI-generated tests should NOT be migrated into it after review. They live permanently in the quality repo:

- **Drift between the two suites is information.** A test that fails only in the AI suite is either a missing human test (gap to close in the source repo) or an AI hallucination (gap to fix in the quality system). The signal lives at the boundary between the suites — preserved by keeping them separate.
- **Migration is busywork.** Re-writing AI tests in the source repo's idiom adds review burden without changing behavior.
- **Quality CI runs the AI suite via composite build.** The compliance bottleneck only applies when a *fix* lands in the source repo; generated tests in their own CI are unrestricted.

## What still goes through review

The compliance / SOX-style bottleneck applies to **fixes**, not to analysis. The architecture moves analysis, scenario-authoring, gap-analysis, and prioritization upstream of the bottleneck — they happen entirely in the quality repo and the context agent. The bottleneck stays exactly where it should: at the moment a fix is applied to the source repo, where human review legitimately gates correctness.

## Resumability via manifest

A whole-repo sweep is a workflow that reads `manifest.yaml` (per-file: `path`, `lastAnalyzedSha`, `status`, `lastRunId`), picks N files where `currentSha != lastAnalyzedSha`, runs the per-file workflow on each, writes a new run snapshot, updates the manifest. Cheap to resume; the manifest is the source of truth, not the workflow journal. Daily cron over the bottom-N can roll the whole repo through analysis on a budget.

## Composing the workflow with the architecture

A worker agent (a future skill like `lr:dev-quality-sweep`) orchestrates over all three repos:

- Reads source repo (read-only)
- `/lr:attach`es the context agent for sustained co-work
- Reads/writes the quality repo (manifest, reports, catalog, generated tests)
- Spawns the per-file workflow as a background workflow; for each unit, the workflow's subagents `boot` the context agent (per `workflow-primitive-operational-notes.md`)

This is the lr-dev reframe direction concretized: context agents on existing primitives, no new repo kind required for the agent side, and the quality repo is just a regular non-lore repo.

## Generality

The pattern is not specific to one regime. Any time the source repo cannot accept AI-generated artifacts directly — compliance, ownership, package-publishing constraints, third-party code, generated-output volume — the same three-repo split applies. Worth promoting further (e.g., to identity-layer status alongside `team-shared-knowledge-principle.md`) if a second user with different constraints adopts the same shape. Today: an architectural pattern, not yet a foundational principle.

## See Also

- `df-per-repo-backbone.md` — **the evolution of this topic**: the quality repo generalizes into the DF backbone, the context agent dissolves into skills + `index.md`.
- `lr-dev-direction.md` — anchor; the artifact side now lives in the DF repo.
- `plugin-vs-agent-repo-separation.md` — parallel separation-by-lifecycle principle, different axis.
- `workflow-primitive-operational-notes.md` — the workflow shape this architecture composes with.
- `team-shared-knowledge-principle.md` — the DF repo is also team-shared, but as artifacts not knowledge.
