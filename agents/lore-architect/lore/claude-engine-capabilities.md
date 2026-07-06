# Claude Engine Capabilities

The Claude Code profile is the reference engine path for Lore Framework: the shared procedure docs
are written in Claude terms first, and other engines override only the binding points named in
`docs-engines-convention.md`.

## Operational shape

- **Plugin loading** — either marketplace install (`/plugin marketplace add ...`, `/plugin install
  lr@...`) or local development via `claude --plugin-dir ./lore-framework`.
- **Invocation surface** — plugin skills appear as `/lr:<skill>`; per-agent shortcuts are generated
  into `.claude/commands/lr-<agent>-agent.md`.
- **Subagent model** — the shared procedure docs' default fan-out language describes Claude's
  `Agent` path; Codex and Cursor override from there.
- **Memory file** — `CLAUDE.md`.
- **Plugin cache** — stale-cache behavior and the manifest-version/cache-clear disciplines are real
  Claude operational concerns; see `plugin-manifest-versioning.md`, `cache-clear-footer-convention.md`,
  and `doctor-stale-plugin-cache.md` in the framework.

## Why this hub exists

Claude is no longer "the only engine" in the lore graph. Treat this topic as the durable entry
point for Claude-specific install, invocation, plugin-cache, and subagent assumptions, with atomic
details living in the linked topics below rather than scattered through multi-engine port notes.

## See Also

- `docs-engines-convention.md`
- `plugin-distribution.md`
- `slash-command-system.md`
- `plugin-manifest-versioning.md`
- `cache-clear-footer-convention.md`
- `claude-coupling-inventory-and-port-tiers.md`
