---
lore: 1
type: topic
summary: "Codex 0.160.0 session logs and resume: rollout records, what persists, app-server history and live events, subagent records, discovery and status, agent messages, token usage records and cost fields, and resume limits; checked 2026-11-09."
parent: lore/openai-apps-and-surfaces.md
---

# Codex session logs and resume

Checked 2026-10-22 on the local Mac with codex-cli 0.160.0. Label: **observed locally**
(verified). This is not a documented storage contract. Recheck it after a Codex upgrade. Lore's
own parsing of engine logs belongs to lore-architect (its `engine-session-log-formats.md` topic).

## Rollout files

- Path: `~/.codex/sessions/YYYY/MM/DD/rollout-<local time>-<thread id>.jsonl`. The file name uses
  local time. Event timestamps inside the file are UTC.
- `session_meta` gives `cwd`, `source`, `base_instructions`, and `cli_version`. `source` is
  `exec`, `vscode`, or, for a multi-agent child,
  `{subagent: {thread_spawn: {parent_thread_id, depth, ...}}}`.
- `turn_context` gives the model, the reasoning effort, the sandbox policy, and the approval
  policy.
- Plain text: most tool calls, tool outputs, visible assistant messages, and the final answer.
- Encrypted (`encrypted_content`): model reasoning items, and the body of every agent-to-agent
  message (hub to child, child to hub, peer to peer). The sender's message tool arguments are
  encrypted too (observed 2026-11-07). Only the model can read them, through a resume.

## History and live events (checked 2026-11-06)

- **Documented:** The [app server](https://learn.chatgpt.com/docs/app-server) provides thread
  history and live JSON-RPC events. Local rollout JSONL, app-server history, live notifications,
  and exec or SDK streams are distinct surfaces; do not assume they carry the same records.
- **Source and schema, Codex 0.160.0:** Its experimental schema directs paginated-history
  clients from full `thread/read` hydration to `thread/turns/list` and `thread/items/list`.
  Follow the opaque cursors and request ordering explicitly. `itemsView: full` means the
  persisted app-server items available for that view, not every live event or rollout line.
  The [pinned history projection](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/app-server-protocol/src/protocol/thread_history_projection.rs)
  and [persistence policy](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/rollout/src/policy.rs)
  are version-specific. The policy filters live deltas, approval requests, errors and other
  transient events; absence of an event does not prove the action did not happen.
- **Observed, controlled test:** A completed assistant item and raw response item held the
  same answer ID and text; combining them as separate messages duplicated the answer. A child
  had a separate thread, with its parent ID in `thread/read`; read both threads for their
  respective records. This narrow test does not establish complete replay, pagination behavior
  in every case, or cross-machine portability. Recheck the version: the CLI, SDK runtime, and
  desktop app can differ.

## Subagent records, discovery and status (checked 2026-11-07)

Codex CLI 0.160.0 rollouts (**observed locally**) and the protocol source at tag `rust-v0.160.0`
(**documented in source**; the newest tag on that date was `rust-v0.167.0`, so recheck).

- **What persists (documented in source, confirmed locally).** Paginated rollouts persist all
  completed items, including `SubAgentActivity` and `CollabAgentToolCall`. The legacy collab
  `*End` events are transient and are not persisted (`rollout/src/policy.rs`). I stated the
  opposite once, in a consult on 2026-11-07; read `policy.rs` at the installed tag before you
  state a persistence rule.
- **Each subagent is its own thread and rollout (observed).** Its `session_meta` holds
  `parent_thread_id`, `forked_from_id`, `thread_source: "subagent"`,
  `subagent_history_start_ordinal`, and `source.subagent.thread_spawn {parent_thread_id, depth,
  agent_path, agent_nickname, agent_role}`.
- **Only `thread_spawn` is a spawned subagent (documented in source).** `review`, `compact` and
  `memory_consolidation` threads also use SubAgent sources. Filter on `thread_spawn`.
- **The parent-to-child link (observed).** The parent rollout holds `SubAgentActivity` items with
  `agent_thread_id`, `agent_path` and `kind` (started, interacted, interrupted, completed). In one
  case the started item ID equalled the `spawn_agent` call ID, and the completed item ID was
  `subagent-completed-<child turn id>`.
- **Tool returns carry almost nothing (observed).** `spawn_agent` returns only
  `{"task_name": "/root/<name>"}`. `wait_agent` returns only "Wait completed." or a timeout, and
  its items had empty `receiver_thread_ids` and `agents_states`. Do not use them as a status source.
- **Discovery through the app server (documented in source; combination not tested).**
  `thread/list` with `ancestorThreadId` and `sourceKinds: ["subAgentThreadSpawn"]` lists the
  spawned descendants of a thread. Both filters are experimental and need the `experimentalApi`
  opt-in. This is a client-side query, not a tool that a child can call
  ([open verification items](open-verification-items.md), items 10 and 11).
- **Model per turn (documented in source, observed).** `Thread.model` and
  `Thread.reasoningEffort` are the current configured values, not per-turn telemetry, and `Turn`
  has no model field. The model and effort that a turn used are only in the rollout
  `turn_context` (`model`, `effort`).
- **Turns.** `thread/turns/list` gives turn status and times. A child made with `fork_turns`
  holds copied parent turns. Exclude them, probably by `subagent_history_start_ordinal`
  (not verified, item 11).
- **Status (documented in source, observed).** `CollabAgentStatus` values: pendingInit, running,
  interrupted, completed, errored, shutdown, notFound. In v2, `agents_states` was empty, so derive
  a child's status from its `ThreadStatus`, its last own turn, and the last `SubAgentActivity`
  kind. `thread/start` returns `multiAgentMode`.
- **Sensitive native fields.** `base_instructions`, `world_state` (the full `AGENTS.md`), the
  spawn message and prompt text, `encrypted_content`, and account fields. A monitor or exporter
  must not copy them by default.

## Agent messages (observed 2026-10-24, rechecked 2026-11-07)

- Agents address each other by path: `/root` for the main thread, `/root/<task_name>` for a child.
- A message from another agent arrives in the receiver's rollout as a response item
  `agent_message` with `id`, `author` and `recipient` paths (for example `/root/peer_a` to
  `/root/peer_b`). It is **not** plain text: only a short header (`Message Type`, `Task name`,
  `Sender`) is readable, and the body is in `encrypted_content`.
- The header gives the kind. "Message Type: NEW_TASK" is a new task: the start of a child, or a
  `followup_task` continue (same rollout file, later timestamp). "Message Type: MESSAGE" is a
  message to an agent that is already running (`send_message`, from the parent or from a peer).
- A tool that reads transcripts must not count a MESSAGE as a new turn. Peer-message test:
  [Codex multi-agent coordination](codex-multi-agent-coordination.md).

## Usage records (checked 2026-11-09)

Codex 0.160.0 rollouts and app-server schema (**observed locally**, 103 rollout files) and the
openai/codex source on `main` (**documented in source**). Prices to apply to these records:
[plans and pricing](plans-and-pricing.md), "Codex credits rate card".

- **Use `token_usage_record`.** There is one per model response, with `thread_id`, `turn_id`,
  `response_id` and `usage`. Sum these records for a session total.
- **Do not use `event_msg token_count` as the session total.** It is not one per response, and it
  was missing in 13 of 103 local files. Its last cumulative value can be lower than the real total.
- **Model and effort per turn** are in `turn_context` (`model`, `effort`). It has no service tier.
  The tier is only in `thread_settings_applied`. App-server `model/list` names the Fast tier
  `id: "priority"` (the old name of Fast).
- **App-server cost estimate.** `account/usage/read` returns `threadUsage`
  (`estimatedUsageCreditsMicros`, `estimatedUsageUsdMicros`, groups by model, effort and speed).
  It is gated to Business and Enterprise credit or usage-based plans
  (`thread_usage_is_available()` in the TUI source). It is `null` on Plus, and it is not available
  with API-key or Bedrock auth. On other plans, compute the cost from `token_usage_record`.
- **Tool-billed items persist.** `web_search_call` and `image_generation_call` items are in the
  rollout, so web-search calls can be counted for the per-call charge.

## Resume

- `codex exec resume <thread-id> "<prompt>"` continues a session. Use `-` in place of the prompt
  to read it from stdin.
- Config overrides apply to the new turn. A safe read-only inquiry into a past session:
  `-c sandbox_mode='"read-only"' -c approval_policy='"never"'`.
- A multi-agent v2 child thread cannot resume alone. The error is: "cannot resume an unloaded
  multi-agent v2 sub-agent through its parent; resume the parent first, or use thread/read to
  inspect it". Resume the parent. The parent can reach its children with `followup_task` or
  `send_message` and relay their answers. Hub and child bindings:
  [Codex multi-agent v2 bindings](codex-multi-agent-v2-bindings.md).

## Version check

- In one consult subagent, `codex --version` printed nothing in 25 seconds. The same command
  worked in the host shell. The rollout `cli_version` field also gives the version.

Related: [Codex surfaces](codex-surfaces.md), "Local session observation" — local session records
are the source of truth for a monitor; this topic says where they are and what they hold.
