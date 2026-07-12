# Cursor Engine Capabilities

Cursor is a shipped Tier-1 engine path for Lore Framework with a deliberately conservative profile.
This topic is the durable entry point for Cursor-specific operational assumptions; keep the detailed
validation and probe notes in the linked topics below.

## Operational shape

- **Plugin loading** — verified path: local checkout via `cursor-agent --plugin-dir
  /absolute/path/to/lore-framework`. Post-clone helper: `scripts/install-cursor-plugin` (v25).
  Symlink under `~/.cursor/plugins/local/` is **opt-in** (`--symlink`) until D2 confirms IDE
  loads without `--plugin-dir`; see `workdir/cursor-marketplace-probe-notes.md`.
- **Plugin refresh** — `scripts/cursor-refresh-plugin` (git pull + VERSION diff + fresh-session
  reminder), then new `cursor-agent --plugin-dir` session; no hot-reload.
- **Mid-session fallback** — when plugin skills are unavailable, file-driven execution via
  `.cursor-skills/lr-*/SKILL.md`; canonical contract in `docs/engines/cursor.md`. Empirically
  validated 2026-07-10 (`cursor-mid-session-fallback-validated.md`).
- **Invocation surface** — skill wrappers under `.cursor-skills/lr-<skill>/` → `/lr-<skill>`;
  per-agent shortcuts `/lr-<agent>-agent` under `.cursor/skills/` after registration.
- **Subagent model** — conservative serial host-side execution in shipped profile.
- **Memory file** — `AGENTS.md`.
- **Doctor** — `doctor-cursor-session-without-plugin` for missing skills entirely (v25).
- **Three-manifest discipline** — `.cursor-plugin/plugin.json` bumped with Claude manifests;
  check #19 enforces; hygiene only — not a verified Cursor cache lever.

## Why this hub exists

Cursor-specific facts were previously split across probe notes, port validation, and dual-tree docs.
This hub is the starting map for install, refresh, fallback, invocation, and constraints.

## See Also

- `v25-cursor-ops-parity-design.md`
- `cursor-mid-session-fallback-validated.md`
- `cursor-port-validated-end-to-end.md`
- `cursor-cli-and-harness-operational-notes.md`
- `cursor-dual-skill-tree-one-repo.md`
- `docs-engines-convention.md`
- `multi-engine-portability-direction.md`
- `engine-session-log-formats.md`
