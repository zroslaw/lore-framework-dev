# Provenance Header — Self-Describing ULA Artifacts

**Provenance Header** is an agreed named term (the user adopted it explicitly, 2026-06-05). It is the **load-bearing mechanism** that lets ULA avoid run-folders and use git history as the run store (see `ula-designed-for-multiple-runs.md`).

## What it is

A small metadata block at the **top of each ULA artifact** (`bugs.yaml`, `scenarios.yaml`, `gap.yaml`) that records **how this result was produced** — which source version, which config. Like a label on a lab sample. Because artifacts are overwritten each run (no run-folders) and git history holds the past runs, **each saved version must describe itself**, or an old artifact in git is just floating results.

## Field set (LOCKED 2026-06-07; schema is `df/aiqa/schemas/provenance.schema.json`)

```yaml
source-sha: a1b2c3d          # git BLOB SHA of the ANALYZED WORKING-TREE bytes
ula-version: 1               # process/schema version (kept OUTSIDE config)
config:
  id: default                # short handle; the half used in the dedupe key
  model: claude-opus-4-8     # …extensible
  approach: deep
---
bugs: [...]
```

Decisions:
- **Drop `source` (path).** Redundant — the artifact's location in the tree already encodes the source file path (`repo-lore/<file>/ula/bugs.yaml`).
- **`source-sha` = git blob SHA of the *bytes actually analyzed*** — i.e. the **working-tree file**, obtained via **`git -C <abs-source-repo> hash-object <path>`**. **NOT `git rev-parse HEAD:<path>`** (the *committed* version), which **lies whenever the working tree is dirty** — and dirty is the *common* case for ULA (you just edited the file and re-run it). `hash-object` also works on dirty/untracked files; `rev-parse HEAD:<path>` fails on untracked. A commit id is wrong for a different reason: it names a whole-repo snapshot and changes on every commit, whereas the blob SHA changes only when the file's bytes change — exactly "did the content change?" This is the content half of the `(source-sha × config-id)` dedupe key. *(Correction: earlier versions of this topic said `rev-parse HEAD:<path>` — wrong. The plugin doc, the schema description, and the workflow all use `hash-object`; validated 2026-06-07 that the written `source-sha` == live `git hash-object`.)*
- **`config` = an extensible bag**, not a flat string — the set of configs can be broad. `config.id` is a short handle (doubles as the dedupe handle); everything else under `config:` is open-ended expansion (model, approach, …).
- **`ula-version` stays outside `config`.** It is the *process/schema* version ("did the method change") vs config = the *run's tunable choices* ("did the settings change") — different questions, don't mix.

## Status

**Locked.** The field set is captured in `df/aiqa/schemas/provenance.schema.json` (machine-enforced). Per `single-canonical-source-discipline.md`, the header schema lives in that one JSON Schema, with prompts for semantics — don't restate it across docs.

## See Also

- `ula-designed-for-multiple-runs.md` — why the header exists (no run-folders + git-history run store + dedupe key).
- `df-per-repo-backbone.md` — the DF repo the artifacts (and this header) live in.
- `df-module-conventions.md` — the DF workflow-authoring checklist (incl. `source-sha` via `git hash-object`).
- `aiqa-ula-feature.md` — artifacts already carried a `unit`+`signature` header; the Provenance Header generalizes that.
- `single-canonical-source-discipline.md` — keep the header schema in the JSON Schema, prompts for semantics; don't restate.
