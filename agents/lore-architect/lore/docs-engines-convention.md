# The `docs/engines/` Engine-Profile Convention — Shipped in v19

The multi-engine port's adapter layer is **shipped in canonical `lore-framework` as v19** (commit
`72b1b2a`) — folded in from the `lore-framework-codex` sibling build where it was first built and
validated (see `codex-port-validated-end-to-end.md`, `landing-via-working-tree-diff.md`). It is the
concrete realization of the "`docs/engines/` adapter" lever named in
`multi-engine-portability-direction.md` § Architectural levers.

## Shape

- One profile per engine: canonical v19 ships `docs/engines/claude.md` (reference) +
  `docs/engines/codex.md`; a validated local near-landing Cursor build adds `docs/engines/cursor.md`.
  Every profile fills the **same five bindings** — framework-root, invocation-syntax,
  subagent-spawn, memory-file, runtime-bounding — plus capability gates. Only the values differ.
- **Boot Step-0** (new, top of `agent-boot.md`): (1) resolve `<framework-root>` by self-location
  (the dir containing `VERSION`); (2) infer the engine — strongest signal first: non-empty
  `${CLAUDE_PLUGIN_ROOT}` → claude; else `~/.codex/` present or root under it → codex; else
  default claude — then read `docs/engines/<engine>.md` and keep its values as standing session
  context. **Profile wins on conflict** with any later step.
- **Shared procedure docs stay engine-agnostic.** They describe the Claude mechanism; each spawn
  site (merge/recall/lore-search/consult) carries a one-line "Engine note" pointing at the
  profile's subagent-spawn override. Low churn, and the override wins at execution time.

## Cursor status (validated locally, not yet landed)

The local near-landing Cursor build validated a third profile:

- **framework-root:** self-location, `${CLAUDE_PLUGIN_ROOT}` empty
- **invocation-syntax:** slash skills work under `cursor-agent --plugin-dir`
- **subagent-spawn:** conservative **serial host-side** override for v1, rather than claiming an
  unverified native Cursor subagent mechanism
- **memory-file:** `AGENTS.md`
- **runtime-bounding:** rely on Cursor job controls / approvals, not a Claude-style Bash timeout

That profile, plus targeted doc updates, was enough for the full currently-implemented lifecycle
catalog to pass on the real local Cursor installation (`19/19`). The important design lesson is
that the `docs/engines/` convention is broad enough to host a **conservative serial profile** as
well as a native-fan-out one — "engine profile" does not imply parallel subagents.

## Codex binding values (`docs/engines/codex.md`)

- **framework-root:** `${CLAUDE_PLUGIN_ROOT}` is empty → self-locate; inline the resolved absolute
  path into subagent briefs.
- **invocation-syntax:** skills invoked by **reading `docs/<skill>.md` directly** when
  agent-initiated (the slash form falls through to shell — see `codex-cli-plugin-loading-findings.md`).
- **subagent-spawn:** native `spawn_agent` (`worker` = write, `explorer` = read-only), **in-session
  model action, not a shell command** (see `codex-native-multi-agent-subsystem.md`). For
  host-reads-steps procedures like merge, the **host reads the procedure doc and passes the steps
  inline** to the spawned worker (the worker does not re-read the doc) — validated as designed.
- **memory-file:** `AGENTS.md` (not `CLAUDE.md`).
- **runtime-bounding:** sandbox; no Bash-tool timeout parameter.
- **Capability gate:** the boot-time `ps -o args= -p $PPID` teammate probe is sandbox-blocked
  (`operation not permitted`) → degrade to host-session assumption. `.git/`-writes are also
  sandbox-blocked (see `codex-git-sandbox-blocks-dotgit.md`).

## Where it lives

Canonical `lore-framework/docs/engines/{claude,codex}.md` shipped in v19. The Codex profile was
first built in the `lore-framework-codex` sibling build (no git remote) — now **superseded and
deletable**, its work folded into canonical v19. The Cursor profile currently lives in a separate
local near-landing build (`lore-framework-cursor/`), validated but not yet landed. Design record:
workdir `codex-binding-design.md`. Still deferred (carry `${CLAUDE_PLUGIN_ROOT}`, out of core
scope): `.mcp.json` / lr-wait, `migrations/*`, `df`/`aiqa` — see `port-landing-next-steps.md`
§ Remaining follow-ups.

## See Also

- `multi-engine-portability-direction.md` — the anchor; § Architectural levers names the five bindings.
- `codex-port-validated-end-to-end.md` — this convention exercised end-to-end on real Codex.
- `cursor-port-validated-end-to-end.md` — the validated local Cursor build on the same convention.
- `codex-native-multi-agent-subsystem.md` — the subagent-spawn binding's underlying mechanism.
- `codex-git-sandbox-blocks-dotgit.md` — the `.git`-write capability gate.
- `framework-root-self-location-validated.md` — the framework-root binding, validated separately.
- `claude-coupling-inventory-and-port-tiers.md` — the five bindings as the whole port surface.
- `port-landing-next-steps.md` — landing this build onto the real `lore-framework`.
