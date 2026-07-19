# Codex `exec` real invocation contract (empirical)

Empirically probed the real `codex-cli 0.142.5` non-interactive contract — `codex exec --json
--skip-git-repo-check -m <model> <prompt>` — while building Lore Beings' `codex` engine kind
(`engine-kinds-design-decision.md`). This is a different artifact from the rollout-JSONL session
logs in `engine-session-log-formats.md`: that's the on-disk session record, this is the live stdout
stream of a headless `exec` run.

- Stdout is JSONL events, one per line: `thread.started` → `turn.started` → zero or more
  `item.completed` (assistant messages etc.) → a terminal `turn.completed` (success) or
  `turn.failed` (error). A model/config error can also emit a standalone `item.completed` with
  `type: "error"` before `turn.failed`.
- `turn.completed` carries a `usage` object (`input_tokens`, `cached_input_tokens`,
  `output_tokens`, `reasoning_output_tokens`) — **no USD cost anywhere in the stream.** Anything
  billing against Codex sessions must get cost from elsewhere (a configured flat rate, a separate
  billing API) — never assume a `total_cost_usd`-shaped field exists. This is *why* Lore Beings'
  codex engine kind charges a mandatory flat `--session-cost-usd` per finished session
  (`engine-kinds-design-decision.md`).
- Codex writes to stderr even on a fully successful run (observed: `ERROR codex_models_manager::
  cache: failed to load models cache: missing field ...`) — a spurious warning, not a fatal error.
  Any code that gates success on "stderr is empty" will misfire; gate on the terminal JSONL event
  type instead.
- `--skip-git-repo-check` is required to run `codex exec` outside a git repo (or in an unrelated
  one) — otherwise it errors before starting.
- A bad `-m <model>` value degrades to fallback metadata with a stderr warning, then fails the
  turn with a `turn.failed` naming the real API rejection (`"The '<model>' model is not supported
  ..."`) — not a hard crash, so failure handling built on the JSONL contract catches it cleanly.

Landed in Lore Beings' `docs/beings.md` § Engine kinds and `scripts/lrb.py`'s codex-kind spawn/
finish logic (v28).

## See Also

- `engine-kinds-design-decision.md` — the design decision this contract feeds
- `engine-session-log-formats.md` — the separate rollout-JSONL artifact (on-disk, not stdout)
- `codex-engine-capabilities.md` — the durable Codex hub topic
- `lore-beings-design.md` — the parent feature
