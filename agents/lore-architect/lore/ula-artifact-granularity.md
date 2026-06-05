# ULA Artifact Granularity — Per-File (Leaning), Tracking-Grain ≠ Storage-Grain

Open design question (2026-06-05): per-unit folders (the current AIQA layout) feel **too granular / noisy**. Should artifacts be per-file instead (all bugs of a file in one `bugs.yaml`)?

## Leaning (NOT yet locked — user said "not sure")

**Per-file artifacts, with `unit` as a field inside each entry.** `ula/bugs.yaml` holds all bugs for the file, each tagged with its unit. Reasons:
- Kills the folder noise (a 20-method file ≠ 60 files).
- Unit attribution isn't lost — it moves from *structure* to *data*.
- Fits "**persistence is the parent's job**" (`workflow-primitive-operational-notes.md`): per-unit agents return data; the parent aggregates into the file artifact.
- Sits naturally beside the file-level `index.md`; one Provenance Header per artifact, not repeated per unit.

## The key insight that makes it safe

**Tracking-grain and storage-grain are separable** (insight: tracking-grain ≠ storage-grain). You can still *run and track* incrementally **per unit** (rerun only changed units) while *storing* **per file** — the parent merges changed units' entries back into the file artifact and leaves the rest untouched. So you keep incremental efficiency without directory sprawl.

The only thing per-unit folders buy is dead-simple partial rewrites (rewrite one unit's dir). With ordered/keyed YAML the per-file diff stays localized, so it's likely not worth the noise.

## Status

A **lean, not a decision** — revisit when the ULA thread resumes (see `df-ula-design-in-progress.md`). If adopted, it changes the tree under `ula/` from `ula/<unit>/{bugs,scenarios,gap}.yaml` to `ula/{bugs,scenarios,gap}.yaml` (entries tagged by unit).

## See Also

- `df-per-repo-backbone.md` — the `ula/` aspect dir this question lives inside; the granularity here is the open detail noted there.
- `provenance-header-concept.md` — one header per artifact (cheaper under per-file).
- `ula-designed-for-multiple-runs.md` — tracking-grain ≠ storage-grain enables per-unit rerun with per-file storage.
- `aiqa-ula-feature.md` — current per-unit layout ("the directory tree IS the record").
- `workflow-primitive-operational-notes.md` — persistence-is-the-parent's-job, which favors parent-aggregated per-file artifacts.
