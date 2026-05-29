The lore system is split across a plugin and one or more agent repos within a workspace. As of v11, three discrete layers are explicit and named:

1. **Plugin layer** (`lore-framework/`) — what's distributed via the marketplace. Universal across all installs.
2. **Domain layer** (each agent repo) — the conceptual scope of a single agent repo. `lore-repo.md` carries its descriptor + `repos:` declarations.
3. **Workspace layer** (the filesystem parent) — the dir Claude is run from. May host one or more agent repos plus their declared sibling repos.

When extending the framework, identify which layer a change belongs to before touching files. See `workspace-vs-domain-vocabulary.md`.

**Plugin** (`lore-framework` — installed as `lr`):
- `.claude-plugin/plugin.json` — plugin manifest
- `.claude-plugin/marketplace.json` — self-hosted marketplace manifest
- `skills/<name>/SKILL.md` — skill definitions (boot, reflect, merge, summarize, finalize, register-repo, unregister-repo, create-repo, create-agent, list-agents, list-repos, check, workspace-sync, update, recall, attach, consult, init, spawn-teammate)
- `docs/` — detailed instructions referenced by skills via `${CLAUDE_PLUGIN_ROOT}/docs/`
- `scripts/workspace-sync` — workspace clone+pull orchestration (parallel)
- `migrations/<N>.md` — per-version migration instructions consumed by `/lr:update`
- `release-notes/<N>.md` — per-version informational release notes
- `VERSION` — single source of truth for the current framework version (currently `11`)

**Agent repo** (e.g., `lore-agents/`):
- `lore-repo.md` — repo descriptor at the root; marks the directory as a lore agent repo. YAML frontmatter: `description` and `version` (framework version string). This is the **only** place a framework version is stamped.
- `agents/<name>/role.md` — agent identity. YAML frontmatter: `description` only. Body: role definition.
- `agents/<name>/lore-context.md` — compacted working knowledge (≤50K tokens)
- `agents/<name>/lore/` — knowledge graph of atomic topics
- `agents/<name>/reflections/` — temporary, finalization step 1 output
- `agents/<name>/workdir/` — persistent workspace for artifacts

**Boot flow:** the caller reads `${CLAUDE_PLUGIN_ROOT}/docs/agent-boot.md` (or `lore-framework/docs/agent-boot.md` for per-agent commands) and passes the agent name. `agent-boot.md` contains both the boot procedure (discover agent → read `role.md` + `lore-context.md` → confirm) and the operating instructions. Single source of truth — both `/lr:boot` and the registered `/lr-<name>-agent` commands are one-line delegations to this file. See `slash-command-system.md`.

**Repo discovery:** skills scan for `lore-repo.md` at the directory root — not for `agents/` subdirectories. This prevents false positives from other repos that happen to have an `agents/` directory.

**Version chain (v2+):** `VERSION` → `lore-repo.md` frontmatter `version`. One identifier per repo, no per-agent stamping. `/lr:check` validates this at check 3. `/lr:update` migrates repos forward by applying `migrations/<N>.md` docs sequentially, then stamping the new version on success. See `consistency-checks.md`, `update-process.md`.

The domain directory contains only agent repos — `lore-framework/` no longer needs to be a sibling. The plugin is installed via `/plugin marketplace add zroslaw/lore-framework` + `/plugin install lr@lore-framework`, or loaded locally via `claude --plugin-dir ./lore-framework`. See `plugin-distribution.md`.
