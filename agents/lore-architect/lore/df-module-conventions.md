# `df/` Module Conventions (BETA SDLC Features in the Plugin)

Conventions for housing lr-dev / SDLC features inside the `lr` plugin. First applied to the AIQA subsystem. (Topic renamed from `dev-module-conventions.md` 2026-06-07 when the module dir + skill prefix went `dev-` → `df-`.)

## Skill Prefix: `df-`

All lr-dev/SDLC tools use the **`df-`** prefix (DF = Dark Factory): `lr:df-ula-file`, `lr:df-repo-init`. This is **required, not just grouping** — plain names collide (`lr:init` already exists). The `df-` prefix **supersedes the earlier `dev-` prefix** (`/lr:dev-aiqa-repo-init`, `/lr:dev-ula-file` are gone). The prefix anchors the tools to the DF north star, not a generic "dev" bucket.

## Directory Structure

- **Top-level `df/` dir** in the plugin holds all DF artifacts (renamed from `dev/`).
- **`df/repo-init.md`** is **DF-core, aspect-agnostic** — it stands up the whole `<repo>-df` backbone (config + `repo-lore/` + README), not just QA, so it lives at the `df/` top level, not under an aspect.
- **`df/aiqa/`** is the AIQA aspect subsystem. Future aspects/subsystems get sibling subtrees under `df/`. (DF ⊃ AIQA ⊃ ULA; AIQA stays as the umbrella concept and the `aiqa/` dir, but only the repo + skills + module dir went `df-`.)

## Placement: Skill-Doc-Pattern + Module Subtree

`SKILL.md` files stay in `skills/` (plugin requirement) as thin pointers, but they point into the **module subtree** (`${CLAUDE_PLUGIN_ROOT}/df/<doc>.md` for DF-core, `${CLAUDE_PLUGIN_ROOT}/df/aiqa/<doc>.md` for the aspect) rather than the global `docs/`.

This is a variant of `skill-doc-pattern.md`: keeps a sizable module's docs + assets (prompts, schemas, workflows) cohesive in one place rather than scattered into the global `docs/` dir. Worth naming as a pattern if more modules adopt it.

## BETA Marking

Follows the `spawn-teammate` precedent:
- `description` field starts with `BETA —`.
- README gets a "Development (BETA)" group.

## Ship Discipline: Plugin ≠ VERSION Bump

Moving a feature into the plugin **does not require cutting a VERSION**. The v16 ship (VERSION 15→16, manifests→`1.16.0`, `release-notes/16.md`, history backfill) **landed 2026-06-08** — but only after DF/AIQA iterated as a BETA *inside* the plugin with no version bump, and the whole dev→df rename rode in that same window (built on local commit `2f1e788`, then renamed; the rename needed no separate version).

Skills are discovered locally via `claude --plugin-dir ./lore-framework` without a manifest bump — the manifest bump only matters for marketplace propagation. So: a BETA module can live in the plugin, be locally usable, and iterate (including a wholesale rename) before its formal version ship.

## DF Workflow-Authoring Checklist

Authoring rules for any dynamic-Workflow script under `df/<aspect>/workflows/` that drives `agent()` calls — confirmed by real runs (`df/aiqa/workflows/ula-file-pass.js`). Treat as a checklist:

1. **Guard `args` against string coercion.** `args` can arrive as a JSON *string*, not a parsed object — destructuring then yields all-undefined and the input guard throws. Defend at the top:
   `const {...} = (typeof args === 'string' ? JSON.parse(args) : args) ?? {}`
   This is *confirmed*, not suspected (see `workflow-primitive-operational-notes.md`). Shrinking `args` does **not** fix it — the cause is coercion, not size (`confirm-root-cause-before-fix` lesson, folded into `verify-before-acting-on-suspected-bugs.md`).
2. **Strip `$schema` before `agent({schema})`.** The runtime validator is draft-07-era and rejects the draft-2020-12 meta-URL (`no schema with key or ref …`). Strip at the `agent()` boundary:
   `const noMeta = (s) => { const { $schema, ...rest } = s; return rest }`
   Keep `$schema` in the `.json` files (editor tooling) and keep schemas **draft-07-compatible** (no 2020-12-only keywords). Strip only when handing to `agent()`.
3. **Don't inject the file contents.** Let each subagent (split + units) read the target file itself, so `args` stays small (large-payload was a separate failure mode) *and* every agent + the `source-sha` hash read the same on-disk bytes → honest provenance.
4. **`source-sha` = `git hash-object <path>`**, not `rev-parse HEAD:<path>` — the working-tree bytes actually analyzed (see `provenance-header-concept.md`).
5. The general workflow defect classes still apply — see `workflow-primitive-operational-notes.md` § Reviewing AI-Generated Workflow Code (result/unit misalignment, silent drops, inject-then-undefined, schema strictness coupling, per-unit full-file embedding).
6. **Pass `args` from the skill as a structured object, never a hand-serialized JSON string.** Complements item 1 (the workflow's *receiving* guard): a hand-built arg string lets a single typo (e.g. a missing `:` in an injected schema) crash the run at the `JSON.parse(args)` guard *before any agent starts*. The runtime serializes a real object correctly every time. **Symptom→cause:** a parse error at that guard means a hand-serialized arg string was passed. Codified in `df/aiqa/ula-file.md` step 4 (confirmed by a real v16-era run failure).

## See Also

- `skill-doc-pattern.md` — the base thin-pointer pattern; this is its module-subtree variant.
- `aiqa-ula-feature.md` — the first module to use this layout (now DF-renamed).
- `df-per-repo-backbone.md` — the per-repo DF backbone these skills write into; `df-repo-init` scaffolds it, AIQA/ULA is one aspect.
- `workflow-primitive-operational-notes.md` — the full operational catalog the checklist above distills the DF-specific rules from.
- `provenance-header-concept.md` — `source-sha` via `git hash-object`.
- `versioning-release-types.md` — v16 shipped 2026-06-08 (history backfilled).
