# Engine Session-Log Formats (empirical, 2026-07-14)

Ground-truth findings from building `scripts/session-takeover` (`takeover-feature.md`). Useful for any future session-introspection work: takeover, harness assertions, benchmarks, transcript-backed state recovery. The Cursor findings below fed the v26 Cursor takeover conversion, shipped and pushed as `lore-framework` main commit `ce90f9a` (on top of `3909129` "Release v26: Cursor takeover conversion"), tagged `lr--v1.26.0`.

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

## Cursor (`~/.cursor/`)

### Discovery — `~/.cursor/chats/`

- `<workspace-hash>/<session-uuid>/meta.json` — `createdAtMs`, `updatedAtMs`, `cwd`, `hasConversation`, optional `isSubagent`.
- Same directory holds `store.db` (see Secondary below). Listing uses `meta.json`; `--list` shows times in the **local timezone**.

### Conversion — `~/.cursor/projects/.../agent-transcripts/`

- `<project-slug>/agent-transcripts/<session-uuid>/<session-uuid>.jsonl` — **ordered** transcript.
- Records: `role:user` / `role:assistant` (with `message.content` text + `tool_use` items), `type:turn_ended`.
- Join to the chat index by session UUID. This is the primary source for takeover digest message order.

### Secondary — `store.db`

- Content-addressed SQLite (`blobs` + hex-encoded `meta` row with `name`, `lastUsedModel`, etc.).
- Tool **results** live here as JSON `role:tool` blobs (`type:tool-result`). Not used for message ordering.
- `scripts/session-takeover` pairs results to JSONL `tool_use` batches via **batch-window name matching** (parallel calls may complete out of JSONL order). See `cursor-takeover-batch-pairing.md`.

### Limitations

- Assistant text is often `[REDACTED]` at rest.
- JSONL `tool_use` items lack `toolCallId`; pairing is by tool name within each batch window — same-name parallel batches set `pairing_uncertain`.
- Undocumented on-disk format; CLI-heavy validation (364/364 on one machine, 2026-07-14). IDE-only parity not separately verified.
- No official list API; filesystem scan only (`CURSOR_HOME` override for tests).

## Operational lesson

When skimming a session log, don't conclude from a truncated read — a `head`-limited extraction of the health-advisor session made it look like it stopped early when it had actually run to full finalization. Extract user messages + the last agent message, or convert with the takeover script, before characterizing a session's end state. (A `verify-before-acting` instance — `verify-before-acting-on-suspected-bugs.md`.)

## See Also

- `takeover-feature.md` — the feature these findings fed.
- `cursor-takeover-batch-pairing.md` — Cursor tool-result pairing algorithm.
- `jsonl-session-files-investigation.md` — prior Claude-format investigation (location encoding, sessionId resolution, archiving concerns).
- `claude-engine-capabilities.md`, `codex-engine-capabilities.md`, `cursor-engine-capabilities.md` — the per-engine hubs.
- `session-as-durable-artifact-cluster.md` — the raw-transcript durability thread.
