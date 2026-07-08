# Cursor Engine Capabilities

Cursor is a shipped Tier-1 engine path for Lore Framework with a deliberately conservative profile.
This topic is the durable entry point for Cursor-specific operational assumptions; keep the detailed
validation and probe notes in the linked topics below.

## Operational shape

- **Plugin loading** — the verified path is a local checkout via `cursor-agent --plugin-dir
  /absolute/path/to/lore-framework`.
- **Plugin refresh** — update the checkout Cursor points at, then start a fresh session with the
  same `--plugin-dir`; the running session keeps the plugin tree it already loaded.
- **Invocation surface** — skill wrappers live under `.cursor-skills/lr-<skill>/`, so user-facing
  commands are `/lr-<skill>` and per-agent shortcuts stay `/lr-<agent>-agent`.
- **Subagent model** — shipped profile is conservative serial host-side execution, not a claimed
  native parallel subagent mechanism.
- **Memory file** — `AGENTS.md`.
- **Operational constraints** — approvals/network/git writes still depend on how Cursor is
  launched; Lore degrades cleanly rather than treating denial as a framework failure.

## Why this hub exists

Cursor-specific facts were previously split between the local probe notes, the validated port note,
and the dual skill tree topic. This hub gives future Cursor work one starting map for install,
refresh, invocation, subagent behavior, and known constraints.

## See Also

- `cursor-agent-cli-probe-findings.md`
- `cursor-port-validated-end-to-end.md`
- `cursor-cli-and-harness-operational-notes.md`
- `cursor-dual-skill-tree-one-repo.md`
- `docs-engines-convention.md`
- `multi-engine-portability-direction.md`
- `engine-session-log-formats.md` — `store.db` content-addressed chat store blocks transcript reconstruction (empirical, v24 takeover work)
