---
lore: 1
type: area
summary: "Hub for Codex-specific plugin install/refresh, invocation, subagent, sandbox, headless-exec, and lifecycle-harness operational facts."
parent: lore-context.md
---

# Codex Engine Capabilities

Codex is a shipped Tier-1 engine path for Lore Framework, but its operational model differs from
Claude in several important ways. This topic is the durable entry point; keep atomic findings in
the linked topics below.

## Operational shape

- **Plugin loading** — persistent installed plugin, not `--plugin-dir`. Register a marketplace with
  `codex plugin marketplace add ...`, then install or refresh with `codex plugin add
  lr@lore-framework`. Legacy `.claude-plugin/marketplace.json` fallback still works, but v25 native
  packaging uses `.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json`; Codex prefers the
  native marketplace file when present.
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
  which installed plugin version Codex will actually load before trusting the result. Because Codex
  has no `--plugin-dir`, **refreshing the plugin cache is a required pre-gate step at every VERSION
  bump**; skip it and every module reports `0.0s` as the identity gate correctly refuses to run
  (`lifecycle-testing-harness.md` § Running the gate). The marketplace `upgrade` subcommand fails for
  a non-Git-configured marketplace; re-adding the plugin updates the cache.
- **The shell tool does hold long blocking calls** (probed 2026-08-17, `gpt-5.4-mini`) — a plain 45s
  sleep held 54s wall, and a background-and-wait construction held 101s for a 90s sleep. So a Keeper
  timeout scenario finishing early is **model-compliance variance at the cheap tier**, not a shell
  limitation. Don't reshape a test around a shell constraint that isn't there; see
  `verify-before-acting-on-suspected-bugs.md` § Probe the hypothesis before reshaping a test.
- **`codex exec` headless contract** — `codex exec --json --skip-git-repo-check -m <model> <prompt>`
  streams JSONL events (`thread.started` → `turn.started` → `item.completed`* → `turn.completed`/
  `turn.failed`), carries a token `usage` object but **no USD cost field at all**, and writes
  spurious warnings to stderr even on success — gate success on the terminal event type, never on
  empty stderr. Empirical detail (probed for Lore Beings' `codex` engine kind): see
  `codex-exec-real-invocation-contract.md`. Distinct from the rollout-JSONL session-log artifact
  below.

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
- `engine-session-log-formats.md` — rollout JSONL record types, session index, `codex mcp-server` (empirical, v24 takeover work)
- `codex-exec-real-invocation-contract.md` — the `codex exec` headless stdout JSONL contract (empirical, v28 Lore Beings work)
