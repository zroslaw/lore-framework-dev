# DF Repo — Per-Repo Backbone the Dark Factory Runs On (leading lr-dev artifact-store direction)

A major lr-dev design direction. The per-repo artifact + knowledge store for a source repo is the **`<repo>-df`** repo (DF = **Dark Factory**). It started (2026-06-03) as the quality-only `<repo>-aiqa` repo, generalized into a broader "codex," and was **renamed and elevated 2026-06-05** to `<repo>-df` with its purpose raised from "artifact mirror" to "the storage layer / backbone the Dark Factory runs on." This supersedes both the `-aiqa`-only framing and the interim `codex` name, and demotes the earlier "context agent" framing (see `lr-dev-direction.md`).

> **Naming history.** `<repo>-aiqa` (quality-only) → `<repo>-codex` (2026-06-03, generalized) → **`<repo>-df`** (2026-06-05, renamed + purpose-elevated). The per-file-mirror design survived each step wholesale; only the name and the framing changed. The `codex` term is retired.

## Purpose: backbone, not just a mirror

The repo is **not** merely a per-file artifact mirror of the source. It is the **storage layer / backbone the Dark Factory runs on**: *all* the context, lore, knowledge, and artifacts the DF and its AI coding agents need that **don't live in the source repo itself**. ULA/AIQA (automated bug-finding + test coverage) are just the **first steps**; the per-file folder structure is the **fundament** the more sophisticated DF accretes onto, not the whole thing.

- **Dark Factory (DF)** = the north-star end state: an autonomous software-engineering factory that produces software with AI agents instead of human engineers, fed only inputs plus occasional follow-ups. Same end state as `autonomous-agents-vision.md` — lr-dev is the SDLC-activity axis; autonomous-agents is the substrate axis. The `-df` suffix anchors the repo to that mission rather than to a generic "book of knowledge" (the rationale for renaming away from `codex`: the name should advertise the repo's role in the system).

## Decision

- **`<repo>-df`** is the name/scope. One DF repo per source repo. It mirrors the source tree — a directory per source file, at the file's repo-relative path — **under a top-level `artifacts/` dir** (see Layout).
- **Lazy directory creation = coverage map.** A file's directory exists only once there is something worth preserving about it. Absence of a dir means "not yet discovered/analyzed." The filesystem itself becomes a sparse, honest map of what is known. (The property the user valued most — it falls straight out of the existing ULA per-file/per-unit layout.)

## Layout: `artifacts/` top level, flattened aspects

The per-source-file mirror lives under a top-level **`artifacts/`** directory — **not** at the repo root. This reserves the repo's top level for future **above-file layers**: repo-wide context, cross-cutting aspects, and (later) the agents' run/task state — the "roof above the file level" the user wants.

```
<repo>-df/
  artifacts/                         ← per-source-file tree (lazy dirs = coverage map)
    SystemCommands.m/
      index.md                       ← narrative landing: summary, key knowledge,
                                         design/product/tech decisions, tribal knowledge, links
      ula/<unit>/                    ← structured QA artifacts (one aspect; granularity under review)
        bugs.yaml  scenarios.yaml  gap.yaml
      <future-aspect>/
  …                                  ← room for above-file layers later (parked, hook only)
```

Two structural decisions (2026-06-05):

1. **Per-file tree under `artifacts/`.** Naming chosen by the user over `files/` / `map/` / `dossiers/`. **Terminology watch:** "artifact" now has two senses — a *tracked artifact* (a source file under `artifacts/`) vs a *generated artifact* (the YAML outputs inside). Structurally fine; keep the two senses distinct **in prose**.
2. **Flatten `aiqa/ula/` → `ula/`.** The `aiqa/` directory level is dropped. `ula/` (and later `ila/`, `e2e/`) sit **flat as aspect dirs** directly under the file dir, beside `index.md`. **AIQA stops being a directory level** and stays a conceptual umbrella (the family of analysis *levels*). Matches "index.md + aspect subdirs at the file level."

- **`index.md` is the "context" aspect itself** — narrative, human-oriented. No separate `context/` subdir. This dissolves the earlier naming collision (context-the-aspect vs context-the-summary) and the earlier tension (quality-in-aiqa vs knowledge-in-agent-lore): both aspects co-locate in the DF repo. The narrative content is exactly the second ULA output kind (see `ula-narrative-vs-structured-output.md`).
- **Aspect subdirs = structured disciplines**, machine-oriented (`ula/` today). Quality goes deep to the unit; context lives at the file level. Clean split mirrors the framework's existing **narrative-vs-structured** instinct: main file = human/narrative, subdirs = machine/structured.
- **Granularity under `ula/` is not locked** — leaning per-file (`ula/{bugs,scenarios,gap}.yaml` with `unit` as a field) over per-unit folders (`ula/<unit>/…`). See `ula-artifact-granularity.md`.

## No agent — skills only

The user worked through "specialized quality agent + context agent" and **landed on: no agents.** Reasoning: if persistence is external (the DF repo) and the procedures live in skills, an agent would have no real function or lore of its own. So:

- **lr-dev standardizes** the storage layout + the procedures (ULA pass, context capture) at the **framework level**.
- The **per-repo "instance" is the DF repo + its small config** (today's `aiqa.config.yaml` seed), NOT an agent instance. This replaces the earlier "agent type → agent instance" framing with "framework procedure → per-repo DF instantiation."
- **Skills are aspect-scoped:** a QA-only pass writes under `ula/` (and may append to `index.md`); a context-only update touches just `index.md`. Aspects share the directory, not the operation — used together or separately depending on the task.
- **Keep existing AIQA skills/workflows in place** — this generalizes them, doesn't replace them. `dev-aiqa-repo-init` becomes (or is joined by) an aspect-agnostic DF-repo-init.

This "no agent" landing is consistent with `agent-split-only-when-forced.md`: don't introduce an agent without a forcing pressure. With persistence externalized to the DF repo and procedures in skills, no such pressure exists. It also retires the `framework-defined-role-pattern.md` context-agent application as lr-dev's chosen path (the pattern itself stands; lr-dev just no longer instantiates it).

## Parked

- **Above-file layers** — repo-wide context, cross-cutting aspects, run/task state at the DF-repo top level (beside `artifacts/`). Hook left: `index.md` can link "out to repo-level topics." Revisit later.
- **Plugin-side naming ripple** — the plugin module `dev/aiqa/` and the `/lr:dev-aiqa-repo-init` skill name are now slightly out of step with the on-disk tree (which has no `aiqa/` level, and the repo is `-df` not `-aiqa`/`-codex`). Revisit plugin-side naming later; the artifact layout is what mattered. See `df-ula-design-in-progress.md` (open items).
- **Migration of the existing `My-Turbo-Boost-Switcher-aiqa`** → `…-df/artifacts/SystemCommands.m/ula/…` + `index.md`. Small, deferred.

## See Also

- `df-ula-design-in-progress.md` — the DF/ULA thread is **in progress**; continuation state + the working glossary of DF/ULA terms.
- `ula-designed-for-multiple-runs.md` — ULA is repeated, not one-shot; git history is the run store, no run-folders.
- `provenance-header-concept.md` — the self-describing header that makes git-history-as-run-store work.
- `ula-artifact-granularity.md` — the per-unit-vs-per-file question for what sits under `ula/`.
- `quality-repo-architecture.md` — the three-repo split; the DF repo *is* what that topic called the "quality repo," now generalized beyond quality (and the context-agent repo collapses into skills + DF repo).
- `lr-dev-direction.md` — anchor; the context-agent framing is now demoted in favor of skills + the DF repo.
- `aiqa-ula-feature.md` — AIQA/ULA, now framed as one aspect (`ula/`) of the DF repo.
- `dev-module-conventions.md` — the plugin-side module layout the DF skills live in.
- `ula-narrative-vs-structured-output.md` — the two ULA output kinds; the narrative kind motivates `index.md`.
- `autonomous-agents-vision.md` — the shared DF north star; lr-dev is the SDLC-activity axis.
- `agent-split-only-when-forced.md` — the "no agent" landing is an instance of this rule.
- `knowledge-vs-skills-distinction.md` — knowledge (DF artifacts + `index.md`) vs skills (the procedures); externalized persistence is why no agent is needed.
