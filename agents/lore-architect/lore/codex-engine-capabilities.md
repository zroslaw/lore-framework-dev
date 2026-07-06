# Codex Engine Capabilities

Codex is a shipped Tier-1 engine path for Lore Framework, but its operational model differs from
Claude in several important ways. This topic is the durable entry point; keep atomic findings in
the linked topics below.

## Operational shape

- **Plugin loading** — persistent installed plugin, not `--plugin-dir`. Register a marketplace with
  `codex plugin marketplace add ...`, then install or refresh with `codex plugin add
  lr@lore-framework`.
- **Plugin refresh** — on verified current builds there is no separate `codex plugin update`
  subcommand; `plugin add` is the refresh path. If the marketplace is Git-backed, run `codex
  plugin marketplace upgrade lore-framework` first. A mid-session refresh affects future sessions,
  not the one already running.
- **Invocation surface** — user-facing skills are native to Codex, but the reliable
  agent-initiated path is to read `docs/<skill>.md` directly. Per-agent shortcuts are personal
  skills in `~/.codex/skills/`, invoked as `$lr-<agent>-agent`.
- **Subagent model** — native in-session `spawn_agent` / `wait_agent`; the Codex engine profile's
  host-reads-steps override is real, not speculative.
- **Memory file** — `AGENTS.md`.
- **Sandbox/gits state** — default sandbox blocks `.git` writes; supported finalization path
  requires `.git` writable through launch or configuration. Network denial is expected and Lore
  degrades around it.
- **Lifecycle-harness caveat** — when a test is meant to validate newly-shipped plugin docs, verify
  which installed plugin version Codex will actually load before trusting the result.

## Why this hub exists

Codex details were spread across probe notes, port-validation topics, sandbox findings, and update
notes. This hub gives future work one starting place for install/update, invocation, subagents,
MCP/plugin loading assumptions, and harness preflight.

## See Also

- `codex-cli-plugin-loading-findings.md`
- `codex-local-plugin-update.md`
- `codex-port-validated-end-to-end.md`
- `codex-native-multi-agent-subsystem.md`
- `codex-git-sandbox-blocks-dotgit.md`
- `codex-testing-methodology.md`
- `docs-engines-convention.md`
- `multi-engine-portability-direction.md`
