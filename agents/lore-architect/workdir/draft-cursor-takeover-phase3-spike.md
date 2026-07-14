# Spike Report — Cursor Takeover Phase 3 (Tool-Result Pairing)

**Date:** 2026-07-14  
**Status:** Spike complete — algorithm validated; implemented in `scripts/session-takeover`  
**Related:** `draft-cursor-takeover-design.md`

---

## 1. Question

Can we pair Cursor `store.db` tool-result payloads with JSONL `tool_use` records to populate takeover digest tool `result` fields — without protobuf decode of the blob DAG?

---

## 2. Answer

**Yes.** Batch-window matching by tool name within each JSONL assistant record achieves **100% pairing** on all **364** listable Cursor sessions on the architect's machine (2026-07-14).

Protobuf / `latestRootBlobId` graph walk is **not required** for tool-result pairing.

---

## 3. What we tried

### 3.1 Blob DAG walk (rejected)

- `store.db` `meta` row (hex JSON) exposes `latestRootBlobId`.
- BFS/DFS following embedded 64-char SHA blob ids from root reached **1 / 1149** blobs on a large session.
- Confirms v24 assessment for **transcript ordering via store.db alone** — blocked.

### 3.2 Global sequential zip (insufficient)

- Tool results in `sqlite rowid` order vs JSONL `tool_use` order globally: **239/243** name matches on session `409f9e7d…`.
- Failures are **order swaps inside parallel tool batches** (e.g. JSONL `[Glob, Read]` vs results `[Read, Glob]`).

### 3.3 Batch-window name matching (shipped)

For each assistant JSONL line:

1. Collect `tool_uses = [tool_use, …]` in JSONL order (batch size 1–5 observed, max 5).
2. Take the next `len(tool_uses)` tool-result records from `store.db` (`ORDER BY rowid`).
3. For each `tool_use` in order, assign the first **unused** result in the window with matching `toolName`.

**Validation:** all 364 sessions → `OK`, zero failures, zero unconsumed results.

---

## 4. Algorithm (canonical)

```python
def pair_tool_batch(tool_uses, results, result_index):
    window = results[result_index : result_index + len(tool_uses)]
    used = set()
    paired = []
    for tool in tool_uses:
        name = tool["name"]
        match = None
        for idx, item in enumerate(window):
            if idx in used:
                continue
            if item["name"] == name:
                match = item
                used.add(idx)
                break
        paired.append(match["result"] if match else "")
    return paired, result_index + len(tool_uses)
```

Walk JSONL in file order; advance `result_index` by `len(batch)` after each assistant line with tools.

---

## 5. Edge cases

| Case | Behavior |
|------|----------|
| Parallel mixed-name batch (Glob + Read) | Window reordering handles it |
| Parallel same-name batch (Read + Read) | Name-only match within window; **assumes result window aligns 1:1 with batch** — validated 43 same-name batches on sample session, 364/364 overall |
| Missing `store.db` | Tool calls emitted with empty `result` |
| Missing JSONL | Cannot convert (list shows `no-transcript`) |
| `[REDACTED]` assistant text | Non-redacted fragments kept; redacted-only text blocks skipped |
| `meta` hex as `str` not `bytes` | `cursor_store_meta()` must `unhexlify` both |

### Same-name batch risk (residual)

If Cursor ever returns **more than `len(batch)` results** before the batch completes, or inserts unrelated tool results inside the window, pairing could drift. Not observed in 364 sessions. Mitigation: assert `len(tool_results) == total tool_uses` after parse (optional warning in meta).

---

## 6. Data sources (final)

| Need | Source |
|------|--------|
| Message order | `agent-transcripts/<uuid>/<uuid>.jsonl` |
| User prompts | JSONL `role:user` |
| Assistant visible text | JSONL `role:assistant` text items |
| Tool call name + args | JSONL `tool_use` |
| Tool results | `store.db` `blobs` table, `role:tool` JSON, `type:tool-result` |
| Title, model | `store.db` meta row (`name`, `lastUsedModel`) |
| cwd, isSubagent | `~/.cursor/chats/.../meta.json` |

Join key: **session UUID**.

---

## 7. Implementation landed (spike → code)

`lore-framework/scripts/session-takeover`:

- `parse_cursor()` — JSONL walk + batch pairing
- `_cursor_load_tool_results()`, `_cursor_pair_tool_batch()`
- `cursor_store_meta()` — hex meta decode (str or bytes)
- Listing enrichment (titles, model, status, JSONL paths)
- `resolve_session()` cursor UUID glob
- `.db` path redirects to sibling JSONL
- Digest footer reports `tool_results_paired / tool_calls_total`

**Smoke test (session `409f9e7d…`):**

```
wrote digest (35 conversation turns, 243 tool calls, engine: cursor)
tool_results_paired: 243/243
```

---

## 8. Explicit non-goals (per user)

- **No `--tail` flag** — not added; full transcript conversion only.

---

## 9. Remaining gaps (post Phase 3)

| Gap | Severity |
|-----|----------|
| `[REDACTED]` assistant prose at rest | Medium — digest incomplete for reasoning |
| Undocumented Cursor on-disk format | Medium — may break on upgrades |
| Same-name parallel mis-pair (theoretical) | Low — not seen empirically |
| Unit tests with synthetic fixtures | Medium — still needed before ship |
| `docs/takeover.md` engine table update | Low — doc pass |
| Lifecycle harness scenario | Low — P1 |

---

## 10. Recommendation

1. **Accept Phase 3 algorithm** — batch-window name matching is the canonical pairing strategy.
2. **Do not invest in protobuf blob DAG** unless batch pairing regresses on future Cursor versions.
3. **Proceed to tests + docs** (design doc Phases 3–5) without `--tail`.
4. Update `engine-session-log-formats.md` and close backlog item on finalize.

---

## 11. Appendix — counts from validation run

```
total chats with hasConversation: 364
total agent-transcript JSONL files: 375
chats with matching JSONL: 364 (100%)
batch-window validation: ok=364 warn=0 fail=0
```

Sample session `409f9e7d-749a-4c0a-bdf5-be3effdbc871`:

- 123 JSONL lines, 243 tool calls, 243 tool results
- 43 parallel batches with duplicate tool names
- 106 `[REDACTED]` markers in stored assistant text
