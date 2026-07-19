# Lore Beings engine `kind` — design decision

Decision: Lore Beings' single hardcoded claude-shaped `spawn_session` invocation is replaced by
per-engine **`kind`** (`ENGINE_KINDS = ("claude", "codex")`), each with its own invocation argv and
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

## See Also

- `codex-exec-real-invocation-contract.md` — the empirical contract this decision encodes
- `unenforceable-caps-are-prompt-theater.md` — the enforceability principle that shaped the flat-cost fallback
- `agent-being-consciousness-substrate-split.md` — judgment-vs-enforcement framing this decision follows
- `lore-beings-design.md` — the parent feature anchor
