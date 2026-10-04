---
lore: 1
type: topic
summary: "The plugin/domain/workspace layer split and the file anatomy of each: plugin skills/docs/scripts/migrations, agent repo lore-repo.md and agents/<name>/ layout, boot flow, repo discovery, and the version chain."
parent: lore-context.md
---

# Architecture Overview

The lore system is split across a plugin and one or more agent repos within a workspace. As of v11, three discrete layers are explicit and named:

1. **Plugin layer** (`lore-framework/`) — what's distributed via the marketplace. Universal across all installs.
2. **Domain layer** (each agent repo) — the conceptual scope of a single agent repo. `lore-repo.md` carries its descriptor + `repos:` declarations.
3. **Workspace layer** (the filesystem parent) — the dir Claude is run from. May host one or more agent repos plus their declared sibling repos.

When extending the framework, identify which layer a change belongs to before touching files. See `workspace-vs-domain-vocabulary.md`.

**Plugin** (`lore-framework` — installed as `lr`):
- `.claude-plugin/plugin.json` — plugin manifest
- `.claude-plugin/marketplace.json` — self-hosted marketplace manifest
- `skills/<name>/SKILL.md` — skill definitions, one thin pointer per `docs/<name>.md` (the current set is the `skills/` directory; `/lr:doctor` and `/lr:workspace-status` were replaced by `/lr:check` in v45)
- `docs/` — detailed instructions referenced by skills via `${CLAUDE_PLUGIN_ROOT}/docs/`. Includes `check.md` (orchestrator) and the `fix-*.md` ailment docs (catalog members, see `ailment-catalog-pattern.md`). `conventions.md` carries the v12 cache-clear footer convention (see `cache-clear-footer-convention.md`).
- `scripts/workspace-pull` / `scripts/lr_core/` — workspace clone+pull orchestration and the deterministic `lr-core` substrate
- `migrations/<N>.md` — per-version migration instructions consumed by `/lr:update`
- `release-notes/<N>.md` — per-version informational release notes; cache-affecting versions must include the Clear Plugin Cache footer
- `VERSION` — single source of truth for the current framework version (read it; never trust a number recorded here)

**Agent repo** (e.g., `lore-agents/`):
- `lore-repo.md` — repo descriptor at the root; marks the directory as a lore agent repo. YAML frontmatter: `description` and `version` (framework version string). This is the **only** place a framework version is stamped.
- `agents/<name>/role.md` — agent identity. YAML frontmatter: `description` only. Body: role definition.
- `agents/<name>/lore-context.md` — compacted working knowledge (≤50K tokens)
- `agents/<name>/lore/` — knowledge graph of atomic topics
- `agents/<name>/reflections/` — temporary, finalization step 1 output
- `agents/<name>/workdir/` — persistent workspace for artifacts

**Boot flow:** the caller reads `${CLAUDE_PLUGIN_ROOT}/docs/agent-boot.md` (or `lore-framework/docs/agent-boot.md` for per-agent commands) and passes the agent name. `agent-boot.md` contains both the boot procedure (discover agent → read `role.md` + `lore-context.md` → confirm) and the operating instructions. Single source of truth — both `/lr:boot` and the registered `/lr-<name>-agent` commands are one-line delegations to this file. See `slash-command-system.md`.

**Repo discovery:** skills scan for `lore-repo.md` at the directory root — not for `agents/` subdirectories. This prevents false positives from other repos that happen to have an `agents/` directory.

**Version chain (v2+):** `VERSION` → `lore-repo.md` frontmatter `version`. One identifier per repo, no per-agent stamping. `/lr:check` validates this. `/lr:update` migrates repos forward by applying `migrations/<N>.md` docs sequentially, then stamping the new version on success. See `consistency-checks.md`, `update-process.md`.

The domain directory contains only agent repos — `lore-framework/` no longer needs to be a sibling. The plugin is installed via `/plugin marketplace add zroslaw/lore-framework` + `/plugin install lr@lore-framework`, or loaded locally via `claude --plugin-dir ./lore-framework`. See `plugin-distribution.md`.
