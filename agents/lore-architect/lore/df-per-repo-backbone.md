# DF Repo — Per-Repo Backbone the Dark Factory Runs On (leading lr-dev artifact-store direction)

A major lr-dev design direction. The per-repo artifact + knowledge store for a source repo is the **`<repo>-df`** repo (DF = **Dark Factory**). It started (2026-06-03) as the quality-only `<repo>-aiqa` repo, generalized into a broader "codex," was **renamed and elevated 2026-06-05** to `<repo>-df` with its purpose raised from "artifact mirror" to "the storage layer / backbone the Dark Factory runs on," and the layout was **finalized + locked 2026-06-07** (top dir `repo-lore/`, per-file `file-lore.md` landing, per-file grouped artifacts). This supersedes both the `-aiqa`-only framing and the interim `codex` name, and demotes the earlier "context agent" framing (see `lr-dev-direction.md`). The rename **landed in the plugin 2026-06-07** (staged BETA — `df-repo-init` scaffolds exactly this; see `aiqa-ula-feature.md`, `df-module-conventions.md`).

> **Naming history.** `<repo>-aiqa` (quality-only) → `<repo>-codex` (2026-06-03, generalized) → **`<repo>-df`** (2026-06-05, renamed + purpose-elevated). Top dir `sources/`/`artifacts/` → **`repo-lore/`** (2026-06-07). The per-file-mirror design survived each step wholesale; only the name and the framing changed. The `codex` term is retired.

## Purpose: backbone, not just a mirror

The repo is **not** merely a per-file artifact mirror of the source. It is the **storage layer / backbone the Dark Factory runs on**: *all* the context, lore, knowledge, and artifacts the DF and its AI coding agents need that **don't live in the source repo itself**. ULA/AIQA (automated bug-finding + test coverage) are just the **first steps**; the per-file folder structure is the **fundament** the more sophisticated DF accretes onto, not the whole thing.

- **Dark Factory (DF)** = the north-star end state: an autonomous software-engineering factory that produces software with AI agents instead of human engineers, fed only inputs plus occasional follow-ups. Same end state as `autonomous-agents-vision.md` — lr-dev is the SDLC-activity axis; autonomous-agents is the substrate axis. The `-df` suffix anchors the repo to that mission rather than to a generic "book of knowledge" (the rationale for renaming away from `codex`: the name should advertise the repo's role in the system).

## Decision

- **`<repo>-df`** is the name/scope. One DF repo per source repo. It mirrors the source tree — a directory per source file, at the file's repo-relative path — **under a top-level `repo-lore/` dir** (see Layout).
- **Lazy directory creation = coverage map.** A file's directory exists only once there is something worth preserving about it. Absence of a dir means "not yet discovered/analyzed." The filesystem itself becomes a sparse, honest map of what is known. (The property the user valued most — it falls straight out of the existing ULA per-file/per-unit layout.)

## Layout: `repo-lore/` top level, per-file `file-lore.md` landing, flat aspects (LOCKED 2026-06-07)

The per-source-file mirror lives under a top-level **`repo-lore/`** directory — **not** at the repo root, and **not** named `sources/` or `artifacts/`. This reserves the repo's top level for non-lore (config) and for future **above-file layers**: repo-wide context, cross-cutting aspects, and (later) the agents' run/task state — the "roof above the file level" the user wants.

```
<repo>-df/
  df.config.yaml                     ← repo config (root stays free for non-lore)
  README.md
  repo-lore/                         ← all lore for the repo; per-source-file tree (lazy dirs = coverage map)
    CheckUpdatesHelper.m/            ← a "Source File Lore" dir (repo-lore/<source-file>/)
      file-lore.md                   ← the file's compacted lore landing (≈ an agent's lore-context.md);
                                         narrative "context" aspect. ULA does NOT write it.
      ula/                           ← structured QA aspect; per-file grouped artifacts (no unit dir)
        bugs.yaml  scenarios.yaml  gap.yaml
      <future-aspect>/
    …                                ← room for above-file layers later (parked, hook only)
```

The locked naming (2026-06-07, decided one term at a time in follow-me mode):

1. **Top dir = `repo-lore/`.** Not `sources/` (collides with the source repo's `src/`), not `artifacts/` (the dir holds *lore*, of which generated artifacts are only a part). Holds the per-source-file tree + future above-file layers.
2. **Per-file dir = "Source File Lore"** (`repo-lore/<source-file>/`). A plain term, not a metaphor — dossier / subject / profile were considered and rejected.
3. **Landing file = `file-lore.md`** — the file's compacted lore landing, the **file-level analogue of an agent's `lore-context.md`**. Deliberately NOT `context.md`/`index.md`: "context" in `lore-context.md` marks "loaded into the agent's context window," which doesn't apply to a static file landing. `file-lore.md` is the future "context" aspect; **ULA does not write it** (ULA writes only under `ula/`).
4. **aspect = a category of a file's lore** (`ula/` today; later `ila/`, `e2e/`); a subdir beside `file-lore.md`. Aspects ≈ an agent's lore-topic categories. **AIQA stops being a directory level** and stays a conceptual umbrella (the family of analysis *levels*). The `aiqa/ula/` nesting was flattened to `ula/` (2026-06-05).
5. **Per-file artifacts are grouped (LOCKED):** `ula/{bugs,scenarios,gap}.yaml`, each `{ source-sha, config, units: [...] }` — the unit is a *field*, not a folder; no `ula/<unit>/` dirs. See `ula-artifact-granularity.md`.

### "lore" generalizes; "artifact" narrows

- **"lore" generalizes cleanly** — there is **agent lore** (an agent's domain knowledge, in its `lore/`) and **file lore** (a source file's knowledge, in `repo-lore/<file>/`). A clean generalization, not a collision; qualify in prose ("agent lore" vs "file lore") on first use. `file-lore.md` is to a Source File Lore dir what `lore-context.md` is to an agent.
- **"artifact" = generated output only** — the YAMLs and `file-lore.md`. The *input* is the **"source file,"** never an "artifact." This resolves the one real terminology collision (the earlier "tracked artifact" vs "generated artifact" double-sense): rather than qualify both senses, the input-side sense was dropped. A source file is a source file; an artifact is something the DF produced.

- **`file-lore.md` is the "context" aspect itself** — narrative, human-oriented. No separate `context/` subdir. Dissolves the earlier naming collision (context-the-aspect vs context-the-summary) and the earlier tension (quality-in-aiqa vs knowledge-in-agent-lore): both aspects co-locate in the DF repo. The narrative content is exactly the second ULA output kind (see `ula-narrative-vs-structured-output.md`).
- **Aspect subdirs = structured disciplines**, machine-oriented (`ula/` today). Quality goes deep to the unit (unit-as-a-field); context lives at the file level. Clean split mirrors the framework's existing **narrative-vs-structured** instinct: landing file = human/narrative, subdirs = machine/structured.

## No agent — skills only

The user worked through "specialized quality agent + context agent" and **landed on: no agents.** Reasoning: if persistence is external (the DF repo) and the procedures live in skills, an agent would have no real function or lore of its own. So:

- **lr-dev standardizes** the storage layout + the procedures (ULA pass, context capture) at the **framework level**.
- The **per-repo "instance" is the DF repo + its small config** (today's `df.config.yaml` seed), NOT an agent instance. This replaces the earlier "agent type → agent instance" framing with "framework procedure → per-repo DF instantiation."
- **Skills are aspect-scoped:** a QA-only pass writes under `ula/` (and may append to `file-lore.md`); a context-only update touches just `file-lore.md`. Aspects share the directory, not the operation — used together or separately depending on the task.
- **Keep existing AIQA skills/workflows in place** — this generalizes them, doesn't replace them. The aspect-agnostic **`df-repo-init`** skill (graduated out of `aiqa/`) scaffolds the backbone; `df-ula-file` writes the `ula/` aspect.

This "no agent" landing is consistent with `agent-split-only-when-forced.md`: don't introduce an agent without a forcing pressure. With persistence externalized to the DF repo and procedures in skills, no such pressure exists. It also retires the `framework-defined-role-pattern.md` context-agent application as lr-dev's chosen path (the pattern itself stands; lr-dev just no longer instantiates it).

## Parked

- **Above-file layers** — repo-wide context, cross-cutting aspects, run/task state at the DF-repo top level (beside `repo-lore/`). Hook left: `file-lore.md` can link "out to repo-level topics." Revisit later.
- **Migration of the existing `My-Turbo-Boost-Switcher-aiqa`** → the new `…-df/repo-lore/<file>/ula/…` layout. Small, deferred. (A fresh `df-ula-file` run on `CheckUpdatesHelper.m` already produced the correct new layout end-to-end — see `ula-validated-turbo-boost-switcher.md`.)

(Resolved 2026-06-07 — no longer parked: the **plugin-side naming ripple** is done. The plugin module is now `df/aiqa/`, the skills are `df-repo-init` + `df-ula-file`, the on-disk tree uses `repo-lore/` with no `aiqa/` level. See `aiqa-ula-feature.md`, `df-module-conventions.md`.)

## Status

DF/ULA design thread **CLOSED 2026-06-07** — all five formerly-open items resolved (layout/naming locked here; granularity locked in `ula-artifact-granularity.md`; provenance `source-sha` corrected to `git hash-object` in `provenance-header-concept.md`; incremental-run shape + git-history run store in `ula-designed-for-multiple-runs.md`; plugin-side ripple landed). The working **glossary** of DF/ULA terms is persisted at `workdir/draft-df-glossary.md` (created this session; current with the locked decisions).

## See Also

- `ula-designed-for-multiple-runs.md` — ULA is repeated, not one-shot; git history is the run store, no run-folders.
- `provenance-header-concept.md` — the self-describing header that makes git-history-as-run-store work (`source-sha` = `git hash-object`).
- `ula-artifact-granularity.md` — per-file granularity LOCKED; the grouped shape of what sits under `ula/`.
- `quality-repo-architecture.md` — the three-repo split; the DF repo *is* what that topic called the "quality repo," now generalized beyond quality (and the context-agent repo collapses into skills + DF repo).
- `lr-dev-direction.md` — anchor; the context-agent framing is now demoted in favor of skills + the DF repo.
- `aiqa-ula-feature.md` — AIQA/ULA, now framed as one aspect (`ula/`) of the DF repo; the DF rename landed there.
- `df-module-conventions.md` — the plugin-side module layout the DF skills live in (+ DF workflow-authoring checklist).
- `ula-narrative-vs-structured-output.md` — the two ULA output kinds; the narrative kind motivates `file-lore.md`.
- `ula-validated-turbo-boost-switcher.md` — the end-to-end run that validated this layout against real output.
- `autonomous-agents-vision.md` — the shared DF north star; lr-dev is the SDLC-activity axis.
- `agent-split-only-when-forced.md` — the "no agent" landing is an instance of this rule.
- `knowledge-vs-skills-distinction.md` — knowledge (DF artifacts + `file-lore.md`) vs skills (the procedures); externalized persistence is why no agent is needed.
- `soft-skill-follow-me-mode.md` — the posture the naming was locked in (user drove one decision at a time).
