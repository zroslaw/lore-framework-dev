# DF / ULA Design — In Progress (Continuation State + Glossary)

The 2026-06-05 session was a **design-exploration** of the DF repo and ULA artifact structure, run in **follow-me mode** (user-driven; small suggestions only — see `soft-skill-follow-me-mode.md`). The user explicitly asked to **preserve all findings** and **continue later** — this thread is **NOT concluded**. No code/plugin changes were made; this was conceptual design captured to lore. This topic is the carry-forward state for resuming the thread.

## Open items to resume with

- **Provenance Header field set** — mostly decided (`source-sha` blob hash, extensible `config` bag, `ula-version` outside config, drop `source`), but not locked into a schema. Next: lock it (into the JSON Schema per `single-canonical-source-discipline.md`). See `provenance-header-concept.md`.
- **Incremental run algorithm** — the SHA-compare + per-unit merge flow was sketched, not detailed. See `ula-designed-for-multiple-runs.md` + `ula-artifact-granularity.md`.
- **Granularity** — leaning per-file (unit as a field), user said "not sure." Decide next time. See `ula-artifact-granularity.md`.
- **Plugin-side naming ripple** — the plugin module `dev/aiqa/` + the `/lr:dev-aiqa-repo-init` skill name are now out of step with the flattened `ula/` tree (no `aiqa/` dir level) and the `-df` repo rename (was `-aiqa`/`-codex`). Parked — the artifact layout was what mattered this session. See `df-per-repo-backbone.md`.
- **Glossary persistence (pending, not yet created)** — the user proposed `workdir/draft-df-glossary.md` as the working home for the running glossary, but **held approval before it was created**. The starter glossary lives in this topic (below); create the workdir draft when the thread resumes and the user confirms.

## Terminology glossary (requested by the user — track DF/ULA terms for unambiguous shared language)

The user wants an explicit running glossary. Starter set coined this session:

- **Dark Factory (DF)** — autonomous software-engineering factory run by AI agents, no human engineers (north star). See `autonomous-agents-vision.md` for the shared end state.
- **DF repo / `<repo>-df`** — per-source-repo backbone: all context/knowledge/artifacts the DF needs that aren't in the source repo. See `df-per-repo-backbone.md`.
- **`artifacts/`** — DF-repo top-level dir holding the per-source-file tree (lazy dirs = coverage map). Top level otherwise reserved for above-file layers.
- **tracked artifact** — a source file tracked in the DF (≠ *generated artifact*, the YAML outputs — keep senses distinct in prose).
- **aspect** — a category of analysis about a file (`ula/` today); subdir beside `index.md`.
- **index.md** — the file's narrative "context" aspect.
- **AIQA** — umbrella concept (not a dir) for AI-based QA, organized by testing *level*.
- **ULA** — Unit-Level Analysis; first AIQA level. Pass = split → bugs(A) → scenarios clean-room(B) → gap(C).
- **unit** — unit-of-testing in a file (e.g. a method); now a *field*, not a folder (if per-file granularity is adopted).
- **Provenance Header** — self-describing metadata block atop each artifact (how/from-what it was produced).
- **source-sha** — content hash (git blob SHA) of the analyzed file version.
- **config (id + params)** — the run's extensible parameter bag; `config.id` is the dedupe handle.
- **(source-sha × config-id)** — the "have we already done this?" dedupe key.

## See Also

- `lr-dev-direction.md` — anchor for the whole SDLC/DF direction; its "Open decisions" mirror these open items.
- `df-per-repo-backbone.md` — the renamed/elevated DF repo design (the rename + layout findings from this session are folded into it; it superseded the topic formerly named codex-per-repo-mirror).
- `ula-designed-for-multiple-runs.md`, `provenance-header-concept.md`, `ula-artifact-granularity.md` — the concrete findings from this session.
- `soft-skill-follow-me-mode.md` — the posture this session ran in (default for open-ended design).
- `feedback-confirm-before-writing-lore.md` — why the glossary draft was held, not auto-created.
