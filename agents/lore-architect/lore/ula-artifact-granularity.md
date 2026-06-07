# ULA Artifact Granularity — Per-File, Grouped (LOCKED 2026-06-07)

Resolved design question. Per-unit folders (the original AIQA layout) were **too granular / noisy**. Artifacts are **per-file**, not per-unit. (Was "leaning per-file, not locked" 2026-06-05; **LOCKED 2026-06-07** when the DF/ULA thread closed.)

## The locked shape

**Per-file artifacts, grouped, with `unit` as a field inside each entry.** One `bugs.yaml` / `scenarios.yaml` / `gap.yaml` per *file*:

```yaml
source-sha: <git hash-object of the file>
config: { id: default }
units:
  - unit: <slug>
    signature: <unit signature>
    # …per-unit bugs | scenarios | gap fields (the existing per-unit schema as the list element)
```

- The existing per-unit schemas are **reused as the list element**; one Provenance Header per *file*, not repeated per unit.
- The unit is a **field**, not a folder. No `ula/<unit>/` directories.
- Alt considered and **rejected**: a flat list with `unit` stamped on every entry. Grouped (`units: [...]`) keeps each unit's findings together and reads cleaner.

Reasons per-file won:
- Kills the folder noise (a 20-method file ≠ 60 files).
- Unit attribution isn't lost — it moves from *structure* to *data*.
- Fits "**persistence is the parent's job**" (`workflow-primitive-operational-notes.md`): per-unit agents return data; the parent aggregates into the file artifact.
- Sits naturally beside the file-level `file-lore.md`; one Provenance Header per artifact.

## The key insight that makes it safe

**Tracking-grain and storage-grain are separable** (tracking-grain ≠ storage-grain). You can still *run and track* incrementally **per unit** (rerun only changed units) while *storing* **per file** — the parent merges changed units' entries back into the file artifact and leaves the rest untouched. So you keep incremental efficiency without directory sprawl.

The only thing per-unit folders bought was dead-simple partial rewrites (rewrite one unit's dir). With grouped/keyed YAML the per-file diff stays localized, so it wasn't worth the noise.

## Validated

The grouped per-file shape was confirmed against real output 2026-06-07: a `df-ula-file` run on `CheckUpdatesHelper.m` produced `repo-lore/<file>/ula/{bugs,scenarios,gap}.yaml` with the `units: []` shape and gap invariants holding per element. See `ula-validated-turbo-boost-switcher.md`.

## See Also

- `df-per-repo-backbone.md` — the `ula/` aspect dir this lives inside; layout locked there.
- `provenance-header-concept.md` — one header per file artifact (cheaper under per-file).
- `ula-designed-for-multiple-runs.md` — tracking-grain ≠ storage-grain enables per-unit rerun with per-file storage.
- `aiqa-ula-feature.md` — the per-file grouped artifact conventions.
- `workflow-primitive-operational-notes.md` — persistence-is-the-parent's-job, which favors parent-aggregated per-file artifacts.
