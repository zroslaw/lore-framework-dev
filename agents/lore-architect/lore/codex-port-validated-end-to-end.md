# Codex Port Validated End-to-End (with ground truth)

The ported framework (`lore-framework-codex`, the `docs/engines/` build — see
`docs-engines-convention.md`) was run on real Codex (`codex exec`, default model `gpt-5.4-mini`,
2026-07-05) across the full lifecycle. Result: **works** — including the hardest part (the Tier-B
subagent-spawn nucleus), **proven not predicted**. This flipped the port from "staged in a tierA
copy" to "engine-profile binding implemented and validated" — and the validated build then **shipped
into canonical `lore-framework` as v19** (commit `72b1b2a`; see `port-landing-next-steps.md`,
`landing-via-working-tree-diff.md`).

## Verified

- Boot Step-0 selected the **codex** profile; `<framework-root>` self-located; **zero
  `${CLAUDE_PLUGIN_ROOT}` leak**. (Framework-root was already validated on Claude/haiku — now also
  on real Codex; see `framework-root-self-location-validated.md`.)
- **Recall** ran via native `spawn_agent` (`agent_type=explorer`) + `wait_agent`, host-read-steps
  brief passed inline. Correct topics surfaced.
- **Merge** ran via native `spawn_agent` (`agent_type=worker`); the **host read `process-merge.md`
  and passed the steps inline** to the worker (the worker did NOT read the doc) — the fan-out
  override working exactly as designed. On disk: 5 lore topics updated, 1 new topic created,
  `reflections/` cleaned up. Merge lore quality was good.

## Observed environment gate

`git commit` blocked by Codex's `.git`-sandbox (see `codex-git-sandbox-blocks-dotgit.md`). This is
**not** a design fault: merge *work* completed on disk; only the commit couldn't run under the
default sandbox. The supported product path now requires `.git` writable through Codex
launch/configuration; default-sandbox output that stops before commit is a degraded fallback, not
a merge failure.

## Why this is trustworthy

Do **not** trust the model's self-report of which tool it used. Every `spawn_agent` claim was
confirmed against Codex's session rollout logs (`~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`),
which record real `function_call` items with `name: spawn_agent`, `namespace: multi_agent_v1`,
arguments. That turned "the model says it spawned" into "it demonstrably spawned." (An earlier
inline-merge run was NOT the tool being absent — nothing had instructed the model to spawn; the
profile's subagent-spawn instruction fixed it.) Full methodology in `codex-testing-methodology.md`.

## See Also

- `docs-engines-convention.md` — the build that this validates.
- `codex-native-multi-agent-subsystem.md` — the `spawn_agent` mechanism proven here.
- `codex-git-sandbox-blocks-dotgit.md` — the observed gate and supported finalization contract.
- `codex-testing-methodology.md` — the rollout-log ground-truthing that made this credible.
- `framework-root-self-location-validated.md` — the framework-root binding, now also codex-proven.
- `claude-coupling-inventory-and-port-tiers.md` — the Tier-B nucleus this closes empirically.
- `multi-engine-portability-direction.md`, `port-landing-next-steps.md` — anchor + landing plan.
