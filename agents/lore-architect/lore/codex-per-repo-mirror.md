# Codex — Per-Repo Artifact Mirror (leading lr-dev artifact-store direction)

A major lr-dev design evolution (2026-06-03, design-exploration session). The per-repo artifact store evolves from a quality-only `<repo>-aiqa` repo into a broader **codex**. This supersedes the `-aiqa`-only framing for the artifact side and demotes the earlier "context agent" framing (see `lr-dev-direction.md`).

## Decision

- **`<repo>-codex`** is the name/scope (chosen over `-atlas`, `-mirror`, `-shadow`). `-aiqa` was too quality-flavored once QA became just *one* aspect. AIQA/ULA is now one discipline among future ones.
- **One codex repo per source repo.** It mirrors the source tree — a directory per source file, at the file's repo-relative path.
- **Lazy directory creation = coverage map.** A file's directory exists only once there is something worth preserving about it. Absence of a dir means "not yet discovered/analyzed." The filesystem itself becomes a sparse, honest map of what is known. (The property the user valued most — it falls straight out of the existing ULA `ula/<file>/<unit>/` layout.)

## Per-file layout

```
<repo>-codex/
  SystemCommands.m/
    index.md                       ← narrative landing: summary, key knowledge,
                                       design/product/tech decisions, tribal knowledge, links
    aiqa/ula/run-task-as-admin/    ← structured QA artifacts (one aspect)
      bugs.yaml  scenarios.yaml  gap.yaml
    <future-aspect>/
```

- **`index.md` is the "context" aspect itself** — narrative, human-oriented. No separate `context/` subdir needed. This dissolves the earlier naming collision (context-the-aspect vs context-the-summary) and the earlier tension (quality-in-aiqa vs knowledge-in-agent-lore): both aspects now co-locate in the codex. The narrative content is exactly the second ULA output kind (see `ula-narrative-vs-structured-output.md`).
- **Subdirs = structured disciplines**, machine-oriented (`aiqa/` today). Quality goes deep to the unit; context lives at the file level.
- Clean split mirrors the framework's existing **narrative-vs-structured** instinct: main file = human/narrative, subdirs = machine/structured.

## No agent — skills only

The user worked through "specialized quality agent + context agent" and **landed on: no agents.** Reasoning: if persistence is external (the codex) and the procedures live in skills, an agent would have no real function or lore of its own. So:

- **lr-dev standardizes** the storage layout + the procedures (ULA pass, context capture) at the **framework level**.
- The **per-repo "instance" is the codex repo + its small config** (today's `aiqa.config.yaml` seed), NOT an agent instance. This replaces the earlier "agent type → agent instance" framing with "framework procedure → per-repo codex instantiation."
- **Skills are aspect-scoped:** a QA-only pass writes under `aiqa/` (and may append to `index.md`); a context-only update touches just `index.md`. Aspects share the directory, not the operation — used together or separately depending on the task.
- **Keep existing AIQA skills/workflows in place** — this generalizes them, doesn't replace them. `dev-aiqa-repo-init` becomes (or is joined by) an aspect-agnostic codex-init.

This "no agent" landing is consistent with `agent-split-only-when-forced.md`: don't introduce an agent without a forcing pressure. With persistence externalized to the codex and procedures in skills, no such pressure exists. It also retires the `framework-defined-role-pattern.md` context-agent application as lr-dev's chosen path (the pattern itself stands; lr-dev just no longer instantiates it).

## Parked

- Repo-level high-level lore topics (a codex-wide layer above per-file). Hook left: `index.md` can link "out to repo-level topics." Revisit later.
- Exact migration of the existing `My-Turbo-Boost-Switcher-aiqa` → `…-codex/SystemCommands.m/aiqa/ula/…` + `index.md`. Small, deferred.

## See Also

- `quality-repo-architecture.md` — the three-repo split; the codex *is* what that topic called the "quality repo," now generalized beyond quality (and the context-agent repo collapses into skills + codex).
- `lr-dev-direction.md` — anchor; the context-agent framing is now demoted in favor of skills + the codex.
- `aiqa-ula-feature.md` — AIQA/ULA, now framed as one aspect (`aiqa/`) of the codex.
- `dev-module-conventions.md` — the plugin-side module layout the codex skills live in.
- `ula-narrative-vs-structured-output.md` — the two ULA output kinds; the narrative kind motivates `index.md`.
- `agent-split-only-when-forced.md` — the "no agent" landing is an instance of this rule.
- `knowledge-vs-skills-distinction.md` — knowledge (codex artifacts + `index.md`) vs skills (the procedures); externalized persistence is why no agent is needed.
