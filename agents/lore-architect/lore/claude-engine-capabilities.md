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
  `Agent` path; Codex and Cursor override from there. Fan-out = N parallel `Agent` calls in a single
  message. Three types: `general-purpose` (write), `Explore` (read-only but excerpt-based — it
  *locates* material rather than reviewing it in depth), and `fork` (**inherits the caller's full
  conversation context**). Two traps, both documented in the profile binding since v30 because both
  change what an executor types: (1) `fork` is unusable wherever a subagent must be *independent* of
  the caller's reasoning — it carries the caller's context by design; (2) passing a **`name`** makes
  the call an Agent-Teams teammate, and **a teammate does not auto-return its final report** — spawn
  unnamed when you need the result back, or instruct the teammate to `SendMessage` its report before
  going idle. See `docs-engines-convention.md` § v30 profile corrections and § Engine traps belong in
  the binding.
- **MCP tool idle timeout** — a single MCP tool call is killed after
  `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` (default **1 800 000 ms = 30 min**) without a response or
  progress. This caps `lr-wait`'s `sleep`/`wait_for_event` in practice, and the abort leaves the
  server's single-request lock held. Practical ceiling ~29 minutes per call unless the per-server
  `timeout` is raised in MCP settings; the fallback for genuinely long waits is a backgrounded shell
  timer. Full mechanics in `wait-primitive-feature.md` § Long-wait operational limits.
- **Memory file** — `CLAUDE.md`. On case-insensitive APFS (the macOS default), this collides with any lowercase `claude.md` under a directory Claude reads — the memory auto-injection matches filenames case-insensitively. See `macos-case-insensitive-filename-collision-with-memory-files.md`.
- **Plugin cache** — stale-cache behavior and the manifest-version/cache-clear disciplines are real
  Claude operational concerns; see `plugin-manifest-versioning.md`, `cache-clear-footer-convention.md`,
  and `doctor-stale-plugin-cache.md` in the framework.
- **Host-environment ailment (macOS)** — TCC access to `~/Documents` can be revoked mid-session,
  which blocks every read of a workspace living there while `~` stays fine. Not a repo or code
  problem, and not agent-repairable. See `macos-documents-permission-loss-mid-session.md`.
- **Lifecycle quota signature** — account/session limit exhaustion in headless lifecycle runs can
  look like broad scenario failure: quick exit code 1, zero cost, and a final "session limit" message
  after earlier normal scenarios. Treat that as quota exhaustion and inspect `LR_DEBUG_DIR` before
  debugging framework behavior. See `lifecycle-testing-harness.md`.

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
- `lifecycle-testing-harness.md` — Claude lifecycle quota signature and debug discipline
- `macos-case-insensitive-filename-collision-with-memory-files.md` — the case-insensitive collision between the memory file and `docs/engines/claude.md`
- `docs-engines-convention.md` § Engine traps belong in the binding — why the `fork` / named-teammate traps live in the profile rather than only in lore
- `subagent-as-optimization-vs-subagent-as-semantics.md` — when `fork` is not merely suboptimal but invalid
- `wait-primitive-feature.md` — the MCP idle-timeout ceiling and the long-wait fallback
- `macos-documents-permission-loss-mid-session.md` — the mid-session TCC ailment
