# Engine Session-Log Formats (empirical, 2026-07-08)

Ground-truth findings from building `scripts/session-takeover` (`takeover-feature.md`). Useful for any future session-introspection work: takeover, harness assertions, benchmarks, transcript-backed state recovery.

## Codex (`~/.codex/`)

- Rollouts: `sessions/YYYY/MM/DD/rollout-<ts>-<uuid>.jsonl`; archived copies move to `archived_sessions/`.
- `session_index.jsonl` holds only **named** threads (`{id, thread_name, updated_at}`); the sessions tree also contains many unnamed rollouts — automated sub-runs, bursts sharing one timestamp.
- Record types: `session_meta` (id, cwd, originator, cli_version), `turn_context` (model — e.g. `gpt-5.4`), `response_item` (the payload: `message` roles user/assistant/developer, `function_call`/`custom_tool_call` + `*_output` paired by `call_id`, `reasoning` is **encrypted**), `event_msg` (redundant UI events).
- Engine-injected context arrives as user-role messages wrapped in tags (`<environment_context>`, `<user_instructions>`); developer-role carries permissions/collaboration plumbing. Filter both.
- `codex mcp-server` runs Codex as a stdio MCP server exposing `codex`/`codex-reply` tools — a Claude session could drive Codex directly.

## Claude Code (`~/.claude/projects/`)

- `<cwd-slug>/<session-uuid>.jsonl`. Records: `user`/`assistant` (with `message` in API shape, plus `sessionId`, `cwd`, `timestamp`, `isSidechain` — sidechains are subagents, skip), `ai-title` (canonical session title, appears late in file), `file-history-snapshot`, `queue-operation`, etc.
- Assistant content items: `text` / `thinking` / `tool_use`; tool results come back inside **user** records as `tool_result` items paired by `tool_use_id`. Synthetic assistant messages have `model: "<synthetic>"`.
- Command invocations and harness injections appear as user-content strings starting with tags (`<command-name>`, `<local-command-caveat>`) — filter on leading `<`.
- Earlier location/format notes (encoded-cwd slug rules, sessionId resolution mechanisms, and why the framework avoids *archiving* this format) live in `jsonl-session-files-investigation.md`.

## Cursor (`~/.cursor/chats/`)

- `<workspace-md5>/<chat-uuid>/{store.db, meta.json}`. `meta.json`: `createdAtMs`, `updatedAtMs`, `cwd`, `hasConversation`.
- `store.db` is SQLite with `blobs(id, data)` + empty `meta`: a **content-addressed** store (blob id = SHA-256 of content). System/user messages are plaintext JSON in API shape; assistant/tool records are binary (protobuf-ish); no ordering info recoverable without reverse-engineering. This blocks transcript reconstruction — Cursor takeover conversion is unsupported for now.

## Operational lesson

When skimming a session log, don't conclude from a truncated read — a `head`-limited extraction of the health-advisor session made it look like it stopped early when it had actually run to full finalization. Extract user messages + the last agent message, or convert with the takeover script, before characterizing a session's end state. (A `verify-before-acting` instance — `verify-before-acting-on-suspected-bugs.md`.)

## See Also

- `takeover-feature.md` — the feature these findings fed.
- `jsonl-session-files-investigation.md` — prior Claude-format investigation (location encoding, sessionId resolution, archiving concerns).
- `claude-engine-capabilities.md`, `codex-engine-capabilities.md`, `cursor-engine-capabilities.md` — the per-engine hubs.
- `session-as-durable-artifact-cluster.md` — the raw-transcript durability thread.
