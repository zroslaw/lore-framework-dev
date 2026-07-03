# Multi-Engine Portability (Codex, Cursor) — Major Direction

User-raised 2026-07-02. A major new direction: Tier-1-parity ports of the lore framework to **OpenAI Codex** and **Cursor**, alongside Claude Code. Claude Code remains the major version — this is not a migration, it's giving mixed-engine teams a way to **share one team-shared agent repo** regardless of which coding agent each member runs (see `similar-projects-landscape.md` for why this is a real differentiator, not just nice-to-have). Two detailed workdir drafts exist for dedicated future design sessions: `workdir/draft-port-codex.md` and `workdir/draft-port-cursor.md`. This topic is the anchor pointer + key findings — the same relationship the drafts have to it that `workdir/draft-lr-dev.md` has to `lr-dev-direction.md`. Do not duplicate the phased plans here.

## Why the timing is right

The industry converged on lore-framework's own primitives since the framework's early design. **SKILL.md** is now an open standard (agentskills.io), and Codex, Cursor, and Claude Code all support it (reportedly 30+ tools total). Codex has *deprecated* its old custom-prompts mechanism in favor of skills. **AGENTS.md** is natively read by both Codex and Cursor. **MCP** is supported by both — `lr-wait` (v18, see `wait-primitive-feature.md`) ports with no redesign. This means the port is mostly **packaging, not redesign** — a year ago it would have been much harder.

## What's already engine-agnostic

The knowledge substrate itself — agent repos, `lore-repo.md`, `role.md`, `lore/`, `lore-context.md`, `sessions/`, git as the metadata/conflict-resolution layer — has no Claude Code dependency at all. A repo written entirely from Claude Code sessions is already readable and writable from Codex or Cursor today, by hand. The port work is entirely about giving each engine the same *procedural* affordances (boot, reflect, merge, finalize) that Claude Code gets via skills.

## Architectural levers (apply to both ports, and to Claude Code doc hygiene now)

- **`docs/engines/` adapter convention** — one file per engine declaring exactly five bindings: skill-invocation syntax, how to spawn a subagent (or "inline fallback"), how to bound a command's runtime, the memory-file target, and framework-root resolution. Procedure docs stop hardcoding Claude-specific phrases ("your Bash tool's timeout parameter," "spawn a `general-purpose` subagent") and reference the adapter instead. This is a **now-visible category of Claude-Code-specific leakage in otherwise-portable prose**, worth fixing even before any port ships, purely for doc hygiene — roughly 10-15 sites found by grep.
- **`<framework-root>`** replaces `${CLAUDE_PLUGIN_ROOT}` as the doc-level term; each engine adapter binds it to whatever that engine calls its equivalent (Claude: the plugin install path; Codex/Cursor: the skill-tree checkout location).
- **AGENTS.md becomes the canonical `/lr:init` target** (all three engines read it); CLAUDE.md compatibility for Claude Code decided per-session, likely a thin pointer.
- **Explicit Tier 1 / Tier 2 split** — Tier 1 portable core: boot, recall, consult, reflect, merge, summarize, finalize, check, update, workspace-sync, list-*, create-*, init, pull-lore. Tier 2 Claude-first: attach (verify per-engine before promising), spawn-teammate, wait, df-*, register-repo shortcuts. Agent Teams, the Workflow primitive (DF/ULA), and hooks stay Claude-only for now — no redesign attempted there.

## Per-engine specifics (detail lives in the drafts)

- **Codex** — default sandbox denies network by default, which directly threatens the freshness contracts (auto-pull, finalize push, workspace-sync are all network operations). Mitigated by the framework's existing degraded-mode design, but needs explicit setup documentation. Subagents are explicit-request-only (no declarative agent files) — merge fan-out likely needs a `codex exec`-based script fallback if prose-triggered subagent requests prove unreliable. See `workdir/draft-port-codex.md`.
- **Cursor** — the best-equipped target of the two. `disable-model-invocation: true` in skill frontmatter gives exact slash-command semantics for lifecycle skills. Declarative `.cursor/agents/*.md` subagent definitions map onto the merge-in-booted-subagents pattern *more cleanly* than Claude Code's own prompt-assembled general-purpose subagent — flagged as a possible back-port candidate once validated. One real risk to verify before advertising Cursor's parallel-agent support: Cursor auto-manages its own git worktrees for parallel agents, which may interact with the framework's existing worktree convention (`worktrees-convention.md`) in ways that aren't yet checked. See `workdir/draft-port-cursor.md`.

## Dominant shared risk

Both drafts converge on the same top risk: **the framework is prose executed by the model.** Merge alone is a 96-line procedure (`process-merge.md`) assuming faithful multi-step instruction-following. Fidelity on non-Claude models is unverified. Both plans end their phased work with an empirical fidelity report, explicitly framed as feeding the already-parked simplification/subtraction theme (`framework-improvements-backlog.md` § Architecture-Review Follow-Ups) — if a procedure degrades badly on another engine's models, that's a signal to simplify the procedure itself, not just to patch around it per-engine.

## Positioning implication

Every surveyed competitor is bound to one engine (Claude Code) or to a vendor-hosted service — none federate knowledge across *different* coding agents sharing one git substrate. Once a port ships, "a team with members on different AI coding tools shares one knowledge base" becomes a differentiator no surveyed competitor can match, because they're all engine-bound by construction. This is the sharpest answer yet to "how do we stand out" and should inform README/positioning language once a port ships. See `similar-projects-landscape.md`.

## Status

Parked vision with two full workdir drafts, not yet started. Each port is intended as its own dedicated design session. See `workdir/draft-port-codex.md`, `workdir/draft-port-cursor.md`.

## See Also

- `workdir/draft-port-codex.md`, `workdir/draft-port-cursor.md` — the phased per-engine plans; this topic is the anchor, not a restatement.
- `similar-projects-landscape.md` — the competitive survey this direction's positioning case rests on.
- `wait-primitive-feature.md` — the MCP-based primitive that ports with no redesign, evidence for "packaging not redesign."
- `framework-scope-vs-agent-scope.md` — the layer-ownership test the `docs/engines/` adapter lever will need to pass.
- `worktrees-convention.md` — the Cursor auto-worktree interplay flagged to verify.
- `skill-doc-pattern.md` — what the thin-pointer skill/doc packaging maps onto per engine.
- `plugin-mcp-server-convention.md` — the MCP registration convention that ports unchanged.
- `framework-improvements-backlog.md` § Architecture-Review Follow-Ups — the simplification/subtraction theme this direction's fidelity report feeds.
- `lr-dev-direction.md`, `autonomous-agents-vision.md` — sibling major directions (different axes: SDLC activity, process/substrate, and now engine portability).
