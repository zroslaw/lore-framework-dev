# DF / ULA Terminology Glossary (working draft)

Scope: the **Dark Factory (DF)** backbone and **ULA** (Unit-Level Analysis). Working home for the running glossary while the DF/ULA design thread is in progress. This is a *draft*, not lore — fold the locked terms into the canonical schema + prompts (single-canonical-source) when the design ships.

Several terms locked **2026-06-07** (follow-me design session). Continuation state: `df-ula-design-in-progress.md`.

## Shape at a glance

```
<repo>-df/                          ← DF repo (backbone; skills, no agent)
  repo-lore/                        ← all lore for the repo
    <source-file>/                  ← a "Source File Lore" dir (per-file lore)
      file-lore.md                  ← the file's lore landing (≈ agent lore-context.md)
      ula/                          ← an aspect (a category of the file's lore)
        bugs.yaml                   ← generated artifacts
        scenarios.yaml
        gap.yaml
    (future above-file / repo-level lore layers also live under repo-lore/)
  (DF-repo root free for non-lore: config, etc.)
```

## Factory / north star

- **Dark Factory (DF)** — autonomous, AI-run SDLC with no human engineers; the north star. See `autonomous-agents-vision.md`.

## Storage backbone

- **DF repo / `<repo>-df`** — per-source-repo backbone: all context/knowledge/artifacts the DF needs that aren't in the source repo. Skills, not an agent. See `df-per-repo-backbone.md`.
- **`repo-lore/`** — DF-repo top-level dir: all lore for the repo. Holds the per-source-file tree (a present `<source-file>/` dir = that file is covered → the tree is a sparse coverage map); future above-file / repo-level lore layers live here too. *(Renamed from `artifacts/`; `sources/` was considered and rejected — ambiguous, collides with the source repo's `src/`.)*
- **Source File Lore** — the per-source-file dir (`repo-lore/<source-file>/`): everything DF knows about one source file. "Source File Lore dir" = the folder on disk; "Source File Lore" = the concept (mirrors "the agent's lore" vs "the `lore/` dir").
- **`file-lore.md`** — the file's lore *landing*: a compacted narrative summary that points into the aspects. File-level analogue of an agent's `lore-context.md`. (We deliberately do **not** reuse "context": for agents that word marks "loaded into the context window," which doesn't apply to a file's landing.)
- **aspect** — a category of a file's lore (`ula/` today); a subdir beside `file-lore.md`. Aspects ≈ an agent's lore-topic categories.

## "artifact" — the one collision to keep straight

- **artifact** — always a *generated output* (the YAMLs, and `file-lore.md`). Never the source file. Bare "artifact" is safe = generated; no qualifier needed.
- **source file** — the *input* under analysis; lives in the source repo. Never called an artifact.

## Lore senses

- **agent lore** vs **file lore** — "lore" generalizes to "persisted accumulated knowledge about a subject": an agent's domain (agent lore) or a source file (file lore). A clean generalization, not a muddy collision — but qualify in prose; never bare "lore" where the scope is ambiguous.

## Analysis layers

- **AIQA** — umbrella *concept* (not a dir) for AI-based QA, organized by testing level. Future levels beyond ULA: integration, e2e, feature/flow.
- **ULA** — Unit-Level Analysis; the first AIQA level.
- **unit** — unit-of-testing in a file (e.g. a method). A *field* on each entry now, not a folder (per-file granularity).

## ULA pass

- **ULA pass** — one single-file run: split → **bugs (A)** → **scenarios (B)** → **gap (C)**. Steps communicate only via written artifacts, never in-context memory.
- **clean-room** — step-B rule: generate scenarios *without* reading existing tests (and excluding any behavior tied to a step-A bug).
- **gap analysis** — step C; two-directional (`not-implemented` = scenarios with no matching test; `ula-missed` = tests no scenario anticipated). The mismatch is the quality signal, not the match.

## Run model

- **Provenance Header** — self-describing metadata block atop each artifact; what lets git history be the run store (no run-folders). See `provenance-header-concept.md`.
- **source-sha** — git blob SHA (content hash) of the analyzed file, whole-file. Obtain via `git hash-object <path>` (the working-tree bytes actually analyzed; **not** `rev-parse HEAD:<path>`, which records the committed version).
- **config / config.id** — extensible run-parameter bag (model, approach, …); `config.id` is the short dedupe handle.
- **dedupe key** — `(source-sha × config-id)`: "have we already run this?"
- **run store = git history** — no run-folders; artifacts are overwritten each run, past runs live in git history.
- **whole-file rerun (PoC)** — when a file's `source-sha` changes, rerun all its units (no per-unit incrementality yet — deferred until ULA's efficiency is proven). See `ula-designed-for-multiple-runs.md`.

## Retired terms (don't reintroduce)

- `index.md` → **`file-lore.md`**
- `artifacts/` (top dir) → **`repo-lore/`** (not `sources/` — ambiguous, collides with `src/`)
- "tracked artifact" → **source file** (and "artifact" is now generated-only)
- header field `source` (path) → dropped (encoded by artifact location)
- header field `ula-version` → dropped (lean on `config.id` / prompt git history)
- `git rev-parse HEAD:<path>` for `source-sha` → **`git hash-object <path>`** (hash the analyzed working-tree bytes, not the committed version)
