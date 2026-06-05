# Provenance Header — Self-Describing ULA Artifacts

**Provenance Header** is an agreed named term (the user adopted it explicitly, 2026-06-05). It is the **load-bearing mechanism** that lets ULA avoid run-folders and use git history as the run store (see `ula-designed-for-multiple-runs.md`).

## What it is

A small metadata block at the **top of each ULA artifact** (`bugs.yaml`, `scenarios.yaml`, `gap.yaml`) that records **how this result was produced** — which source version, which config. Like a label on a lab sample. Because artifacts are overwritten each run (no run-folders) and git history holds the past runs, **each saved version must describe itself**, or an old artifact in git is just floating results.

## Field set (discussed; mostly decided, not yet locked into a schema)

```yaml
source-sha: a1b2c3d          # git BLOB SHA = content hash of the analyzed file
ula-version: 1               # process/schema version (kept OUTSIDE config)
config:
  id: opus-deep              # short handle; the half used in the dedupe key
  model: claude-opus-4-8
  approach: deep
  # …arbitrary, extensible
---
bugs: [...]
```

Decisions:
- **Drop `source` (path).** Redundant — the artifact's location in the tree already encodes the source file path (`artifacts/<file>/ula/bugs.yaml`).
- **`source-sha` = git blob SHA (content hash), NOT a commit id.** A commit id names a whole-repo snapshot and changes on every commit; the blob SHA changes only when the file's bytes change — exactly "did the content change?" Obtain via `git rev-parse HEAD:<path>`. (Optionally also stash the commit id for human readability; the blob SHA is the functional one.) This is the content half of the `(source-sha × config-id)` dedupe key.
- **`config` = an extensible bag**, not a flat string — the set of configs can be broad. `config.id` is a short handle (doubles as the dedupe handle); everything else under `config:` is open-ended expansion (model, approach, …).
- **`ula-version` stays outside `config`.** It is the *process/schema* version ("did the method change") vs config = the *run's tunable choices* ("did the settings change") — different questions, don't mix. (Small call; flagged as the user's to confirm.)

## Status

In progress — field set mostly decided, but **locking it into a schema is the next step** (see `df-ula-design-in-progress.md`). Per `single-canonical-source-discipline.md`, the locked header schema belongs in the JSON Schema (machine-enforced), with prompts for semantics — don't restate it across docs.

## See Also

- `ula-designed-for-multiple-runs.md` — why the header exists (no run-folders + git-history run store + dedupe key).
- `df-per-repo-backbone.md` — the DF repo the artifacts (and this header) live in.
- `df-ula-design-in-progress.md` — the in-progress thread; locking this schema is an open item.
- `aiqa-ula-feature.md` — artifacts already carried a `unit`+`signature` header; the Provenance Header generalizes that.
- `single-canonical-source-discipline.md` — keep the header schema in the JSON Schema, prompts for semantics; don't restate.
