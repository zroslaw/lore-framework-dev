# ULA Is Repeated, Not One-Shot — Designed for Repetition

Core reframe for ULA (2026-06-05): in DF mode it **runs many times** as development progresses. The artifacts and the pass must be designed for repetition from the start — not as a one-shot analysis.

## Two kinds of repeated run

1. **Incremental over time** — re-run as the source evolves. Decide "should we (re)run ULA for this file?" by the file's **content signature** (git blob SHA), not the head commit id: blob SHA changes only when the file's bytes change, so commits that don't touch the file correctly read as "no rerun." Get it with `git rev-parse HEAD:<path>`. See `provenance-header-concept.md` for `source-sha`.
2. **Different configs on the same version** — run ULA with different params (model, approach) on the *same* file version, to compare which model/approach is better. A dev/experimentation activity; in production this is rare.

## No run-folders — git history is the run store

Decision: **do not** create a per-run folder structure. Instead, **embed the run's config/params inside the artifact** (the Provenance Header) and let **git history** hold the past runs. Rationale: a run-folder structure is only useful at dev time (heavy experimentation); baking it into the layout permanently is wrong. This is a clean fit with the framework's **git-as-metadata** principle — git history *is* the run-history store.

- On-disk artifact = the latest run (production case: one config, always-latest).
- Past/alternative runs = `git log -p` on the artifact, which shows **config + results together** (because config travels in the header).

## The dedupe key unifies both concerns

"Have we already done this?" key = **(source-content-SHA × config-id)**:
- new content SHA → rerun (incremental);
- same content SHA, new config → also a run (config comparison), same file version.

On-disk header answers the common production case; git history answers dev-time multi-config queries. No run-folders needed — confirmed the instinct holds.

## Status

In progress: the SHA-compare + per-unit merge flow (the incremental run *algorithm*) was sketched, not detailed — an open item to resume with. See `df-ula-design-in-progress.md`.

## See Also

- `provenance-header-concept.md` — the mechanism (self-describing header) that makes git-history-as-run-store work.
- `ula-artifact-granularity.md` — per-file vs per-unit storage; tracking-grain ≠ storage-grain (you can track/rerun per unit while storing per file).
- `df-per-repo-backbone.md` — the DF repo holding the artifacts; git history of that repo is the run store.
- `aiqa-ula-feature.md` — the ULA pass (A→B→C); note earlier "no SHAs" was about code-pointer SHAs, distinct from `source-sha` provenance.
- `system-design-principles.md` — git-as-metadata, the principle this leans on.
