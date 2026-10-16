---
lore: 1
type: topic
summary: "Inference (2026-10-16): privacy-preserving local Claude Code monitoring must identify a durable conversation separately from intermittent CLI processes."
parent: lore/claude-apps-and-surfaces.md
---

# Claude Code local session observation

**Label: inference** (2026-10-16). This is a local monitoring design conclusion, not a documented
Anthropic API contract. Recheck the local session-data format after a Claude Code update. It
contains no personal session content, credentials, or utilization data.

## Identity model

Treat a Claude Code conversation session and a `claude` process as different identities. A later
CLI invocation can resume the same session, so the stable session identifier is the dashboard
identity; a process is only an intermittent signal that work is currently running.

## Safe local observer

Use local Claude session metadata to discover sessions. Reconcile it with currently running
`claude` processes at a short interval. Store only the metadata required for operational status:
session identifier, workspace when available, timestamps, process state, and source confidence.
Do not collect prompts, replies, tool input or output, or credentials.

This preserves an idle but resumable session after its command process exits, and it prevents a
resume from being shown as a new conversation. The installed engine and the monitor service remain
the responsibility of **workstation-keeper**.

## Sources and limits

Source: local design review on 2026-10-16. No Anthropic public source was checked for this
implementation detail, so do not present it as a stable product guarantee.
