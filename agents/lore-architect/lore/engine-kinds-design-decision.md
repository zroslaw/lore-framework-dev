# Lore Beings engine `kind` — design decision

Decision: Lore Beings' single hardcoded claude-shaped `spawn_session` invocation is replaced by
per-engine **`kind`** (`ENGINE_KINDS = ("claude", "codex", "cursor")`), each with its own invocation argv and
result-parsing contract, selected at `lrb engines add` (defaults to the engine name if the name is
itself a known kind, else `claude`).

Rationale: Lore Beings' MVP design (`lore-beings-design.md`) explicitly deferred multi-engine
support until "a second engine ships" for *model tiers* — but the Keeper's `spawn_session`/
`_finish` were more tightly coupled than that: they assumed every engine speaks the exact
`claude -p ... --output-format json` argv/result shape. Codex's real contract
(`codex-exec-real-invocation-contract.md`) differs on every axis — subcommand vs flag, JSONL vs
single JSON, and critically **no USD cost field at all**. Treating this as "just another engine
config" would have silently broken the daily-usd budget gate (cost always reads 0, cap never
trips) — the exact `unenforceable-caps-are-prompt-theater.md` failure shape, just at the
engine-contract layer instead of the schema layer.

Settled shape: `kind` is a small closed enum, not a config-time full-invocation template — the
framework decides the argv contract per kind (keeps `lrb.py` a single source of truth and testable
against real per-kind stub fixtures), the user only supplies `--command`/`--permission-mode` and,
for cost-blind kinds, a mandatory flat `--session-cost-usd` charged per finished session
regardless of outcome (over-charge is the safe failure direction). This is deliberately narrower
than a generic "any CLI, any JSON shape" engine plugin system — no evidence yet that a third shape
is needed, and `ENGINE_KINDS`/the `kind` dispatch in `spawn_session`/`_finish` is the natural
extension point when one is.

Landed alongside the v28 Lore Beings release (`lore-framework` commit `5f7eea1` "codex engine
kind", on top of the PID-identity fix, below the v28 release commit `44bc57d`).

## Real-engine findings that sharpen the kind contracts (2026-07-20)

Two gaps surfaced building the Keeper lifecycle scenarios (`lifecycle-testing-harness.md`
§ Keeper coverage) — both are per-kind contract asymmetries the current `cmd_engines_add` schema
doesn't yet match:

- **`cursor` is empirically cost-blind too.** Real `cursor-agent` (2026.07.16, `composer-2.5`,
  `--output-format json`) returns **no `total_cost_usd`** — only token `usage`. So the flat
  `--session-cost-usd` fallback is load-bearing for cursor, exactly as for codex. **Fixed
  2026-07-20:** `cmd_engines_add` now requires `--session-cost-usd` for `cursor` too, mirroring
  codex, instead of leaving it optional. See `cursor-agent-real-invocation-contract.md`.
- **`claude` kind has no `--plugin-dir` mechanism at all.** `spawn_session` passes `--plugin-dir`
  only for `cursor`; a claude-kind being can therefore load `lr:` skills (which every spawn prompt
  assumes) **only if the configured engine `command` itself bakes in `--plugin-dir`** — i.e. a tiny
  wrapper script (`exec claude --plugin-dir <framework-dir> "$@"`) registered as the command. An
  operator following `docs/beings.md` literally would get a being that can never load Lore skills.
  Backlog: add an explicit `--plugin-dir` config field for the claude kind (mirroring cursor), or
  document the wrapper requirement. Both filed as findings, not silently patched into `lrb.py` —
  they are user-facing schema/design decisions.
- **`cursor`'s sandboxed shell tool escapes process-group kill (2026-07-20, confirmed real, fixed
  same day).** Real `cursor-agent` tool-invoked shell commands run inside a freshly `setsid`'d
  session — a new process group — so `_kill`'s original `killpg(pgid-of-the-direct-child)` alone
  could not reach a grandchild that escaped into it: confirmed live via the new B3 lifecycle
  scenario, which left an orphaned real process running on the test machine until manually
  SIGKILLed. Unlike the cost-blindness/plugin-dir findings above, this one is NOT a schema/config
  decision — it's a Keeper-internal correctness gap, so it was fixed directly: `_kill` now also
  walks the full ppid-descendant tree (`_descendant_pids`) and signals every descendant found,
  independent of process-group/session membership — enumerated BEFORE signaling the parent (killing
  the parent first risks the OS reparenting a surviving child to PID 1, breaking the very ppid chain
  the walk depends on). See `lore-beings-mvp-takeover-review.md` § Fifth pass,
  `cursor-agent-real-invocation-contract.md`, and the general ordering rule extracted to its own
  topic, `kill-tree-enumerate-before-signal-ordering.md`.

## See Also

- `codex-exec-real-invocation-contract.md` — the empirical contract this decision encodes
- `unenforceable-caps-are-prompt-theater.md` — the enforceability principle that shaped the flat-cost fallback
- `agent-being-consciousness-substrate-split.md` — judgment-vs-enforcement framing this decision follows
- `lore-beings-design.md` — the parent feature anchor
- `kill-tree-enumerate-before-signal-ordering.md` — general ordering rule for ancestry-based kill-tree code
- `testing-simulate-process-escape-without-setsid-binary.md` — macOS-portable technique for testing the setsid-escape scenario
