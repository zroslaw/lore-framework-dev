---
lore: 1
type: topic
summary: "Codex 0.160.0 session logs and resume: rollout records, selective persistence, app-server history and live events, multi-agent records, and resume limits; checked 2026-11-06."
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
- Plain text: tool calls, tool outputs, visible assistant messages, and the final answer.
- Encrypted (`encrypted_content`): model reasoning items, and the text of hub-to-child and
  child-to-hub messages. Only the model can read them, through a resume.

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

## Agent messages (observed 2026-10-24)

- A message from another agent arrives in the receiver's rollout as a response item
  `agent_message` with an author path and a recipient path (for example `/root/peer_a` to
  `/root/peer_b`).
- Its header gives the kind. "Message Type: NEW_TASK" is a new task: the start of a child, or a
  `followup_task` continue (same rollout file, later timestamp). "Message Type: MESSAGE" is a
  message to an agent that is already running (`send_message`, from the parent or from a peer).
- A tool that reads transcripts must not count a MESSAGE as a new turn. Peer-message test:
  [Codex multi-agent coordination](codex-multi-agent-coordination.md).

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
