# Design — Cursor Session Takeover (`/lr:takeover`)

**Status:** Implemented (Phases 1–3 shipped 2026-07-14)  
**Author:** lore-architect (exploration session 2026-07-14)  
**Target:** `lore-framework` — extend `scripts/session-takeover` and `docs/takeover.md`  
**Scope:** Cursor listing enrichment + JSONL-based digest conversion + `store.db` batch-window tool-result pairing.

---

## 1. Problem statement

`/lr:takeover` (BETA, v24) converts engine-native session logs into a markdown **takeover digest** so a new session on any engine can continue interrupted work. Codex and Claude Code are fully supported. Cursor sessions are **listed** but **not convertible** — the skill tells the user conversion is unsupported and stops.

The v24 blocker was accurate for the path we tried (`store.db` alone): Cursor's chat SQLite store is content-addressed with no recoverable message order. **Empirical re-exploration (2026-07-14) found a second, ordered transcript file** that v24 did not use:

```
~/.cursor/projects/<project-slug>/agent-transcripts/<session-uuid>/<session-uuid>.jsonl
```

On the architect's machine: **364/364** chats with `hasConversation: true` had a matching JSONL transcript (100% correlation). Conversion via JSONL is feasible at "good-enough takeover" fidelity; full parity with Claude/Codex (tool results + complete assistant prose) requires additional work.

### Goals

| Goal | Priority |
|------|----------|
| Convert Cursor sessions to takeover digests (JSONL path) | **P0** |
| Enrich Cursor listing (title, model, status, first prompt) | **P0** |
| Cross-engine takeover: Cursor → Claude/Codex and reverse | **P0** |
| Pair tool results from `store.db` into digests | **P0** (shipped) |
| Lifecycle-harness scenario for takeover + Cursor | P1 |
| Official Cursor API for session list (if one appears) | Out of scope |

### Non-goals

- Modifying Cursor's on-disk formats or requiring Cursor cooperation.
- Archiving / indexing all sessions (takeover remains on-demand, read-only).
- Recovering `[REDACTED]` assistant text Cursor strips at rest.
- Replacing Cursor's native `--resume` / `--continue` UX.

---

## 2. Current state

### 2.1 Architecture (unchanged)

```
User invokes /lr:takeover [<id>]
        │
        ▼
docs/takeover.md  (orchestration: list → ask, or direct convert → boot → verify → continue)
        │
        ▼
scripts/session-takeover  (python3, stdlib-only)
   ├── list_<engine>()   → stdout table
   ├── parse_<engine>()  → (meta, messages[])
   └── render_markdown() → digest
```

Unified message shape (internal):

```python
{"role": "user"|"assistant", "content": str}
{"role": "assistant", "tool": name, "args": str, "result": str}
```

### 2.2 Cursor code today

`list_cursor()` scans `~/.cursor/chats/*/*/meta.json`, filters `hasConversation`, sorts by `updatedAtMs`, returns placeholder title `(cursor chat — conversion not yet supported)`.

`main()` exits early:

```python
if args.engine == "cursor" or path.suffix == ".db":
    sys.exit("error: cursor session conversion is not supported yet")
```

### 2.3 What we learned (ground truth)

#### Storage layout — two complementary stores

| Store | Path | Role |
|-------|------|------|
| **Chat index** | `~/.cursor/chats/<ws-hash>/<uuid>/meta.json` | Discovery: cwd, timestamps, `hasConversation`, `isSubagent` |
| **Chat blobs** | `…/store.db` | Content-addressed SQLite: user/system/assistant/tool JSON blobs + binary DAG nodes |
| **Ordered transcript** | `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | **Ordered** user/assistant/tool_use records |

Join key: **session UUID** (directory name under `chats/` equals JSONL filename stem).

#### `meta.json` fields (chat index)

```json
{
  "schemaVersion": 1,
  "createdAtMs": 1783860082620,
  "updatedAtMs": 1783860114731,
  "cwd": "/path/to/workspace",
  "hasConversation": true,
  "isSubagent": true   // optional; subagents often lack cwd
}
```

#### `store.db` meta row (hex-encoded JSON, key `0`)

```json
{
  "agentId": "<uuid>",
  "latestRootBlobId": "<sha256>",
  "name": "Lore Framework",
  "mode": "default",
  "isRunEverything": true,
  "lastUsedModel": "composer-2.5",
  "approvalMode": "unrestricted",
  "createdAt": 1783256230147
}
```

#### JSONL record types

| Record | Shape | Notes |
|--------|-------|-------|
| User turn | `{"role":"user","message":{"content":[{"type":"text","text":"…"}]}}` | Often wrapped in `<timestamp>`, `<user_query>` |
| Assistant turn | `{"role":"assistant","message":{"content":[…]}}` | `text` + `tool_use` items; many `text` values are `[REDACTED]` |
| Turn end | `{"type":"turn_ended","status":"success"}` | Absence ⇒ possibly in-progress / interrupted |

**JSONL does not contain `tool_result` records.** Tool results live in `store.db` as `{"role":"tool","content":[{"type":"tool-result","toolCallId":"tool_…","toolName":"…","result":"…"}]}`.

#### Fidelity sample (real session `409f9e7d…`, 123 JSONL lines)

- 16 user turns, 106 assistant records, 243 tool calls
- 106 `[REDACTED]` markers in assistant text
- 243 tool-result blobs in `store.db` (count matches tool calls)
- JSONL `tool_use` items **lack `id` / `toolCallId`** → cannot pair results by ID without heuristics or blob-graph walk

#### Active vs completed

| Signal | Interpretation |
|--------|----------------|
| `turn_ended` present | Completed (check `status`) |
| No `turn_ended` | Possibly active or crashed mid-turn |
| `updatedAtMs` recent | Recently touched (listing sort already uses this) |
| No Cursor "suspended" artifact | Unlike Lore's planned suspend feature |

#### CLI surface

- `cursor-agent --resume [chatId]` — resume by id (interactive; Ink UI, needs TTY)
- `cursor-agent --continue` — continue previous
- **No** stable non-interactive list command → filesystem scan remains the discovery mechanism

---

## 3. Design decisions

### D1 — Primary conversion source is JSONL, not `store.db`

**Rationale:** JSONL is ordered, plain JSON, and present for every listable chat on tested machines. `store.db` alone cannot reconstruct order; it remains a **secondary** source for Phase 3 tool results.

**Implication:** `parse_cursor(path)` accepts a `.jsonl` path. Session resolution accepts UUID → find JSONL via glob, not `store.db`.

### D2 — Degraded fidelity is acceptable for v1 Cursor conversion

Align with existing takeover philosophy: digest consumer is an LLM; tool calls are one-line summaries; trust on-disk state over digest.

Cursor-specific degradations we document honestly:

- Assistant intermediate prose often `[REDACTED]` at rest
- Tool calls included; tool **results** empty in Phase 1–2
- Subagent sessions may lack `cwd`

This is still sufficient for cross-engine handoff (user saw the v24 Codex→Claude ship with similar tool-summary digests).

### D3 — Listing resolves JSONL + enriches from `store.db` meta

`list_cursor()` continues to scan `meta.json` (stable index across workspaces). For each session:

1. Glob JSONL: `~/.cursor/projects/*/agent-transcripts/<uuid>/<uuid>.jsonl`
2. Read title from `store.db` meta `name` (fallback: first `<user_query>` from JSONL, then `(untitled)`)
3. Read `lastUsedModel`, derive `status` from JSONL (`completed` / `in-progress` / `no-transcript`)
4. Flag `isSubagent` from `meta.json`

### D4 — Session resolution order

When user passes `<token>`:

```
1. If token is existing file path (.jsonl) → use directly
2. If token matches UUID (full or prefix) → resolve across engines:
   a. Codex rollout JSONL (existing)
   b. Claude project JSONL (existing)
   c. Cursor agent-transcript JSONL (NEW) — glob by uuid prefix
3. If token is .db path → resolve sibling JSONL by parent dir name (uuid), not parse .db
4. Ambiguous prefix → list candidates, exit 1 (existing behavior)
```

Remove the hard `path.suffix == ".db"` rejection for Cursor; instead redirect to JSONL.

### D5 — No new dependencies

Stay python3 stdlib-only (`sqlite3`, `json`, `glob`, `re`, `pathlib`). Phase 3 protobuf decode is optional future work; no `protobuf` pip dep in v1.

### D6 — Docs and lore updates ship with code

- `docs/takeover.md` — engine table, remove "not yet" for Cursor convert
- `engine-session-log-formats.md` — add JSONL section; correct `store.db`-only blocker
- `takeover-feature.md` + `framework-improvements-backlog.md` — close/redate gap
- `release-notes/<N>.md` — if shipped as versioned release

### D7 — Filter policy unchanged

Temp-dir cwd filter (`--all` to include) applies to Cursor listing same as Claude. Lifecycle/quality fixtures under `/var/folders/.../T/lr-*` remain hidden by default.

---

## 4. Technical design

### 4.1 New constants and helpers

```python
CURSOR_CHATS = Path.home() / ".cursor" / "chats"
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"

def cursor_jsonl_for_uuid(session_uuid: str) -> Path | None:
    """Glob ~/.cursor/projects/*/agent-transcripts/<uuid>/<uuid>.jsonl"""
    hits = glob.glob(str(CURSOR_PROJECTS / "*" / "agent-transcripts" / session_uuid / f"{session_uuid}.jsonl"))
    return Path(hits[0]) if len(hits) == 1 else None

def cursor_store_meta(chat_dir: Path) -> dict:
    """Decode hex JSON from store.db meta key 0. Best-effort; {} on failure."""

def cursor_session_status(jsonl_path: Path) -> str:
    """'completed' | 'in-progress' | 'unknown'"""
```

### 4.2 `list_cursor()` enrichment

**Output fields** (internal dict, same as other engines):

```python
{
    "engine": "cursor",
    "id": "<uuid>",
    "title": "<name or first prompt>",
    "cwd": "<cwd or None>",
    "updated": "<iso8601>",
    "path": "<absolute jsonl path>",      # CHANGE: point to JSONL, not store.db
    "model": "<lastUsedModel or None>",    # NEW
    "status": "completed|in-progress",     # NEW
    "is_subagent": bool,                   # NEW
}
```

**Title resolution:**

```
1. store.db meta.name if present and not "New Agent"
2. Else first user <user_query> text from JSONL (clipped 60 chars)
3. Else "(untitled)"
```

**Print format** (`cmd_list`): extend one line when model/status present:

```
2026-07-05 06:17  409f9e7d-749  Lore Framework  [composer-2.5, completed]  cwd: /Users/.../git-repos
    /Users/yaroslav/.cursor/projects/Users-yaroslav-Documents-git-repos/agent-transcripts/409f9e7d-.../409f9e7d-....jsonl
```

### 4.3 `parse_cursor(jsonl_path) -> (meta, messages)`

#### Meta extraction

Scan JSONL once (or first pass):

- `engine`: `"cursor"`
- `session_id`: stem of jsonl file
- `source`: absolute jsonl path
- `started` / `ended`: from first/last timestamp in user messages if present, else file mtime
- `cwd`: from sibling `~/.cursor/chats/*/<uuid>/meta.json` if found
- `title`, `model`: from `cursor_store_meta()` via chat dir lookup
- `status`: from `cursor_session_status()`

#### Message extraction

For each JSONL line:

| Record | Action |
|--------|--------|
| `type == turn_ended` | Skip (capture status in meta only) |
| `role == user` | Extract text items; strip `<timestamp>`, unwrap `<user_query>`; skip empty |
| `role == assistant` | For each content item: `text` → assistant message if not `[REDACTED]`-only; `tool_use` → tool summary via `_cursor_call_summary()` |

**Filtering rules:**

- Skip user messages that are pure engine injection (leading `<` tag heuristic, same as Claude parser)
- `[REDACTED]`-only assistant text blocks: skip the text item but still emit subsequent `tool_use` items on that line
- Concatenate multiple non-redacted `text` items on one assistant line into one message (preserve paragraph breaks)

#### Tool summary helper

Mirror `_claude_call_summary` / `_claude_arg_keys` pattern:

```python
_CURSOR_ARG_KEYS = {
    "Shell": ["command"],
    "Read": ["path"],
    "Grep": ["pattern"],
    "Glob": ["glob_pattern"],
    "Write": ["path"],
    "StrReplace": ["path"],
    "Task": ["description"],
    "CallMcpTool": ["toolName"],
    ...
}
```

`result` field: empty string in Phase 1–2.

#### Register parser

```python
PARSERS = {"codex": parse_codex, "claude": parse_claude, "cursor": parse_cursor}

def detect_engine(path):
    ...
    if path.suffix == ".jsonl" and "agent-transcripts" in str(path):
        return "cursor"
```

### 4.4 `resolve_session(token)` extension

```python
# After existing codex + claude globs:
cursor_hits = glob.glob(
    str(CURSOR_PROJECTS / "*" / "agent-transcripts" / f"*{token}*" / f"*{token}*.jsonl")
)
# Normalize: keep paths where parent dir name == jsonl stem
```

Ambiguity: multiple UUID prefixes match → same error as today.

### 4.5 Digest footer — Cursor-specific note

Append to rendered digest when `meta["engine"] == "cursor"`:

```markdown
> **Cursor transcript note.** Some assistant turns were stored as `[REDACTED]` by Cursor.
> Tool results are paired via store.db batch-window matching when available.
```

### 4.6 Phase 3 — tool result pairing (**spiked 2026-07-14, implemented**)

**Problem:** JSONL `tool_use` items lack `toolCallId`; tool results live in `store.db`.

**Rejected:** Blob-DAG / protobuf decode from `latestRootBlobId`.

**Shipped:** Batch-window name matching — see `draft-cursor-takeover-phase3-spike.md`. Validated **364/364** sessions. Implemented in `parse_cursor()` with digest meta `tool_results_paired` / `tool_calls_total`.

---

## 5. Documentation changes

### 5.1 `docs/takeover.md`

Update engine table:

| Engine | Discover | Convert |
|--------|----------|---------|
| Cursor | yes | yes (via `agent-transcripts` JSONL; tool results omitted; some text redacted) |

Step 2 (bare flow): remove "Cursor sessions can be listed but not yet converted."

### 5.2 `engine-session-log-formats.md`

Replace Cursor section:

```markdown
## Cursor (`~/.cursor/`)

### Discovery — `~/.cursor/chats/`
<workspace-hash>/<session-uuid>/meta.json — cwd, timestamps, hasConversation, isSubagent

### Conversion — `~/.cursor/projects/.../agent-transcripts/`
<project-slug>/agent-transcripts/<session-uuid>/<session-uuid>.jsonl
Ordered records: user, assistant (text + tool_use), turn_ended.
Join to chat index by session UUID.

### Secondary — `store.db`
Content-addressed blob store. Holds full tool-result payloads and store meta (name, model).
Not used for ordering. Phase 3 may pair tool results into digests.

### Limitations
- `[REDACTED]` assistant text at rest
- tool_use in JSONL lacks toolCallId (pairing hard)
- No official list API; filesystem scan only
```

### 5.3 Lore topics (on ship via finalize)

- Update `takeover-feature.md` § Known gaps
- Update `framework-improvements-backlog.md` § Takeover
- Optional new topic: `cursor-takeover-jsonl-path.md` (atomic finding) — only if we want a standalone canonical source per naming discipline

---

## 6. Implementation plan

### Phase 1 — Listing enrichment (≈半 day)

| Step | File | Work |
|------|------|------|
| 1.1 | `scripts/session-takeover` | Add `CURSOR_PROJECTS`, `cursor_jsonl_for_uuid()`, `cursor_store_meta()`, `cursor_session_status()` |
| 1.2 | `scripts/session-takeover` | Rewrite `list_cursor()` — JSONL path, title/model/status |
| 1.3 | `scripts/session-takeover` | Extend `cmd_list()` print format for optional model/status |
| 1.4 | — | Manual: `session-takeover --list --engine cursor --limit 15` on dev machine |

**Acceptance:** Titles show real names; paths end in `.jsonl`; status column correct for completed vs in-progress samples.

### Phase 2 — JSONL conversion (≈1 day)

| Step | File | Work |
|------|------|------|
| 2.1 | `scripts/session-takeover` | Implement `parse_cursor()`, `_cursor_call_summary()`, user-query unwrapping |
| 2.2 | `scripts/session-takeover` | Register in `PARSERS`; extend `detect_engine()` |
| 2.3 | `scripts/session-takeover` | Extend `resolve_session()` for Cursor UUID / JSONL paths |
| 2.4 | `scripts/session-takeover` | Remove `.db` hard reject; add redirect: `.db` → sibling JSONL by uuid |
| 2.5 | `scripts/session-takeover` | Cursor-specific digest footer in `render_markdown()` |
| 2.6 | `docs/takeover.md` | Update engine table + procedure notes |
| 2.7 | `docs/engine-session-log-formats.md` | N/A in framework — lives in dev lore; update `lore-framework-dev/.../engine-session-log-formats.md` at finalize OR add `docs/` pointer if we add framework doc |

**Note:** `engine-session-log-formats.md` currently lives in **dev lore**, not `lore-framework/docs/`. Update the dev lore topic at finalize; optionally add a short Cursor transcript subsection to a framework doc if `/lr:check` expects symmetry.

**Acceptance:**

```bash
session-takeover 409f9e7d-749 -o /tmp/cursor-digest.md
# → writes digest, prints turn/tool counts

session-takeover /path/to/store.db -o /tmp/digest.md
# → resolves to JSONL, succeeds

session-takeover <cursor-uuid> --engine cursor -o /tmp/digest.md
# → succeeds
```

### Phase 3 — Tests (≈半 day)

| Step | File | Work |
|------|------|------|
| 3.1 | `lore-framework-dev/tests/` or `lore-framework/scripts/` | Unit tests with **fixture JSONL** (synthetic, committed — no user PII) |
| 3.2 | Fixtures | `tests/fixtures/cursor-transcript-minimal.jsonl` — 2 user, 3 assistant, 2 tool_use, turn_ended |
| 3.3 | Tests | `parse_cursor` message counts, user_query unwrap, REDACTED skip, tool summary |
| 3.4 | Tests | `list_cursor` with temp dir layout (tmpdir meta + jsonl) |
| 3.5 | `tests/lifecycle/` | New scenario `takeover-cursor` (optional P1) — boot → invoke `/lr-takeover` with fixture path |

**Fixture policy:** Do not commit real `~/.cursor` transcripts. Synthetic fixtures only.

### Phase 4 — Validation (≈半 day)

| Step | Work |
|------|------|
| 4.1 | Convert real local session (user-chosen); inspect digest readability |
| 4.2 | Haiku ambiguity-detector subagent: bare `/lr:takeover` flow includes Cursor with real titles |
| 4.3 | Cross-engine: Cursor session → continue in Claude (or current engine) per `docs/takeover.md` steps 3–5 |
| 4.4 | Edge cases: subagent (`isSubagent`), in-progress (no `turn_ended`), missing JSONL (degraded list entry) |

### Phase 5 — Ship (version decision)

**Option A — Patch within BETA:** Docs + script only, no `VERSION` bump (takeover already BETA in v24).

**Option B — Minor release (v26):** If we want release-notes + manifest bump + cache-clear footer (script changed).

**Recommendation:** Option A unless bundled with other framework changes; script changes are cache-affecting if we do bump.

| Step | Work |
|------|------|
| 5.1 | `release-notes/` if VERSION bump |
| 5.2 | Finalize lore-architect: update `takeover-feature.md`, `engine-session-log-formats.md`, backlog |
| 5.3 | Run targeted tests; full lifecycle only if VERSION bump |

---

## 7. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| JSONL path changes in future Cursor versions | Medium | High | Detect via schema probes; degrade gracefully; document empiricism |
| JSONL missing for some sessions (other machines) | Low | Medium | List with `status: no-transcript`; convert fails with clear error |
| `[REDACTED]` leaves thin context | High | Medium | Document; footer warning; user expects verify-on-disk |
| No tool results in digest | High | Medium | Accept for v1; Phase 3 spike |
| Large sessions blow token budget | Medium | Medium | Existing issue for Claude/Codex; optional `--tail N` future |
| Privacy: transcripts contain secrets | Medium | High | Read-only; temp digest; don't commit real logs; warn in docs |
| `store.db` meta decode breaks | Low | Low | Best-effort; fall back to JSONL title |
| Subagent sessions lack cwd | Medium | Low | Show `is_subagent` in list |

---

## 8. Open questions

1. **Ship as VERSION bump or silent BETA improvement?** — Lean silent unless user wants release fanfare.
2. **Phase 3 priority** — Worth a dedicated spike after v1 ships, or wait for user pain?
3. **`--tail N` flag** — Truncate to last N user turns for huge Cursor sessions? (Codex/Claude could use it too.)
4. **Filter subagents in default list?** — Probably show them but mark `[subagent]`; user may want to take over subagent work.
5. **IDE vs CLI transcript parity** — Explored on CLI-heavy machine (100% JSONL match). Re-verify on IDE-only workflows before claiming universal support.

---

## 9. Task checklist (copy-paste for implementation session)

**Status (2026-07-14):** Phases 1–3 implemented; unit + haiku lifecycle tests green. **v26 release prepared locally** (Option B: `VERSION=26`, manifests `1.26.0`, `release-notes/26.md`) — not yet committed/pushed. Remaining optional: list-and-ask lifecycle, boot-from-digest step 3.

```
[x] Phase 1: listing helpers + enriched list_cursor
[x] Phase 2: parse_cursor + resolve + remove .db block
[x] Phase 2: docs/takeover.md update
[x] Phase 3: synthetic fixtures + unit tests + store.db batch-window pairing
[x] Phase 4: real-session conversion smoke test (architect machine 364/364)
[x] Phase 5: lore finalize (engine-session-log-formats, takeover-feature, backlog, cursor-takeover-batch-pairing.md)
[x] Lifecycle scenario: test_takeover.py (Cursor direct path, haiku)
[ ] Optional: list-and-ask lifecycle, interrupted-session haiku, boot-from-digest continuation
```

---

## 10. Appendix — File touch list

| Path | Change |
|------|--------|
| `lore-framework/scripts/session-takeover` | Main implementation |
| `lore-framework/docs/takeover.md` | Engine table + procedure |
| `lore-framework-dev/tests/fixtures/cursor-transcript-minimal.jsonl` | New fixture |
| `lore-framework-dev/tests/test_session_takeover.py` (or similar) | New tests |
| `lore-framework-dev/agents/lore-architect/lore/engine-session-log-formats.md` | Cursor section rewrite |
| `lore-framework-dev/agents/lore-architect/lore/takeover-feature.md` | Close gap |
| `lore-framework-dev/agents/lore-architect/lore/framework-improvements-backlog.md` | Close/redate item |
| `lore-framework/release-notes/<N>.md` | If VERSION bump |

---

## 11. Appendix — Minimal fixture sketch

`tests/fixtures/cursor-transcript-minimal.jsonl`:

```jsonl
{"role":"user","message":{"content":[{"type":"text","text":"<user_query>\nBoot lore-architect\n</user_query>"}]}}
{"role":"assistant","message":{"content":[{"type":"text","text":"Booting lore-architect."},{"type":"tool_use","name":"Read","input":{"path":"/tmp/lore-framework/docs/agent-boot.md"}}]}}
{"role":"assistant","message":{"content":[{"type":"text","text":"Loaded as **lore-architect**."}]}}
{"type":"turn_ended","status":"success"}
```

Expected digest: 1 user turn, 2 assistant turns (or 1 assistant + 1 tool bullet), session metadata, footer.
