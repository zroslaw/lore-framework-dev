# `dev/` Module Conventions (BETA Features in the Plugin)

Conventions for housing lr-dev / SDLC features inside the `lr` plugin. First applied to the AIQA subsystem.

## Skill Prefix: `dev-`

All lr-dev/SDLC tools use the `dev-` prefix: `lr:dev-ula-file`, `lr:dev-aiqa-repo-init`. This is **required, not just grouping** — plain names collide (`lr:init` already exists).

## Directory Structure

- **New top-level `dev/` dir** in the plugin holds all dev artifacts.
- **`dev/aiqa/`** is the AIQA subsystem. Future subsystems get sibling subtrees under `dev/`.

## Placement: Skill-Doc-Pattern + Module Subtree

`SKILL.md` files stay in `skills/` (plugin requirement) as thin pointers, but they point into the **module subtree** (`${CLAUDE_PLUGIN_ROOT}/dev/aiqa/<doc>.md`) rather than the global `docs/`.

This is a new variant of `skill-doc-pattern.md`: keeps a sizable module's docs + assets (prompts, schemas, workflows) cohesive in one place rather than scattered into the global `docs/` dir. Worth naming as a pattern if more modules adopt it.

## BETA Marking

Follows the `spawn-teammate` precedent:
- `description` field starts with `BETA —`.
- README gets a "Development (BETA)" group.

## Ship Discipline: Plugin ≠ VERSION Bump

Moving a feature into the plugin **does not require cutting a VERSION**. The v16 ship (VERSION 15→16, manifests→`1.16.0`, `release-notes/16.md`, history backfill) was deferred while AIQA is BETA/iterating.

Skills are discovered locally via `claude --plugin-dir ./lore-framework` without a manifest bump — the manifest bump only matters for marketplace propagation. So: a BETA module can live in the plugin, be locally usable, and iterate before its formal version ship.

## See Also

- `skill-doc-pattern.md` — the base thin-pointer pattern; this is its module-subtree variant.
- `aiqa-ula-feature.md` — the first module to use this layout.
- `versioning-release-types.md` — v16 will be the formal ship with history backfill.
