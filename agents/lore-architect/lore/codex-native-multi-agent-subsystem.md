# Codex Has a Native Multi-Agent Subsystem

Corrects an earlier wrong read ("Codex has no native subagents"; "explicit-request-only, no
declarative agent files → merge fan-out likely needs a `codex exec`-based script fallback").
`codex-cli 0.142.5` ships a first-class multi-agent subsystem, exposed as **model-facing tools
inside a session**, not as a CLI subcommand — which is why an early headless probe missed it.

Ground truth (binary + `codex features list` + live session rollout logs), 2026-07-05:

- Feature `multi_agent` = **stable, ON by default**. `multi_agent_v2` / `enable_fanout` are
  under development and OFF — design against stable only.
- Tools (namespace `multi_agent_v1`): `spawn_agent`, `wait_agent`, `send_message`/`send_input`,
  `followup_task`, `interrupt_agent`, `close_agent`, `resume_agent`, `list_agents`. Hierarchical
  task tree (`/root/task1/task_3`). Inter-agent messaging (`InterAgentCommunication`: author +
  multiple recipients addressed by nickname/role, `trigger_turn` wakes the recipient) + handoff.
- **spawn is ad-hoc**: `spawn_agent` takes an inline `message` + `agent_type` (`worker` = write,
  `explorer` = read-only, `default`). No pre-authored file required — a `.codex/agents/<name>.md`
  def is optional, for reusable *named* agents (like Claude's `subagent_type`).
- Caps: `agents.max_threads` ≈ 6, `agents.max_depth` = 1 (host spawns; subagents don't re-spawn).
- **Hard constraint:** these tools are in-session model actions — they **cannot be called from a
  shell command** (`functions.exec`). Fan-out must be expressed as model instructions, which is
  exactly what the `docs/engines/codex.md` subagent-spawn binding does (see
  `docs-engines-convention.md`).

Net: Codex is roughly at parity with Claude for what lore's fan-out needs (recall, consult,
attach, merge, finalize). Native `spawn_agent` **supersedes** the "emulate via nested `codex exec`"
fallback as the primary path — it is real and was exercised end-to-end (see
`codex-port-validated-end-to-end.md`). Full detail in workdir
`codex-multiagent-live-capture.md` and `codex-multiagent-research.md`.

Distinct from Agent Teams / `/lr:spawn-teammate` (`spawn-teammate-feature.md`): that is a
Claude-Code multi-pane UX; this is Codex's in-session subagent fan-out that the Tier-B
subagent-spawn binding targets.

## See Also

- `docs-engines-convention.md` — the `docs/engines/codex.md` subagent-spawn binding that expresses
  fan-out as model instructions to `spawn_agent`.
- `codex-port-validated-end-to-end.md` — recall + merge fan-out proven via `spawn_agent` on real Codex.
- `claude-coupling-inventory-and-port-tiers.md` — the Tier-B subagent-spawn nucleus this de-risks.
- `multi-engine-portability-direction.md` — the anchor direction.
- `codex-testing-methodology.md` — how the tool use was ground-truthed (rollout logs).
