# Claude Engine Capabilities

The Claude Code profile is the reference engine path for Lore Framework: the shared procedure docs
are written in Claude terms first, and other engines override only the binding points named in
`docs-engines-convention.md`.

## Operational shape

- **Plugin loading** — either marketplace install (`/plugin marketplace add ...`, `/plugin install
  lr@...`) or local development via `claude --plugin-dir ./lore-framework`.
- **Plugin refresh** — the CLI has dedicated update subcommands (verified against the live CLI
  2026-07-17); use them, **not** a re-`add`/re-`install`. The canonical refresh sequence is
  `claude plugin marketplace update lore-framework` then `claude plugin update lr@lore-framework`.
  `claude plugin update`'s own help states "restart required to apply", which independently
  validates the "start a fresh session" instruction install docs give after it. Re-running
  `marketplace add` + `plugin install` as a refresh path is at best unspecified, at worst a silent
  no-op — exactly the failure a refresh section exists to prevent (fixed in INSTALL-CLAUDE.md,
  commit `84948e8`).
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
- `engine-session-log-formats.md` — session JSONL location/record types (empirical, v24 takeover work)
