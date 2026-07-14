# Cursor Takeover — Batch-Window Tool-Result Pairing

How `scripts/session-takeover` pairs Cursor `store.db` tool results to JSONL `tool_use` records for `/lr:takeover` digests. Shipped and pushed as part of v26 (2026-07-14): `lore-framework` main commit `ce90f9a` (on top of `3909129` "Release v26: Cursor takeover conversion"), tagged `lr--v1.26.0`.

## Problem

- Ordered transcript: `~/.cursor/projects/.../agent-transcripts/<uuid>/<uuid>.jsonl`
- Tool results: `~/.cursor/chats/.../<uuid>/store.db` (`role:tool`, `type:tool-result`)
- JSONL `tool_use` items have **no** `toolCallId` — cannot pair by ID

`store.db` alone cannot reconstruct message order (content-addressed blob DAG); JSONL provides order.

## Algorithm

For each assistant JSONL line with a tool batch of size N:

1. Take the next N tool-result rows from `store.db` (`ORDER BY rowid`).
2. For each `tool_use` in JSONL order, assign the first unused result in that window with matching `toolName`.

Handles parallel completion-order swaps (e.g. JSONL `[Glob, Read]` vs results `[Read, Glob]`).

## Validation

- 364/364 listable Cursor sessions on architect machine (2026-07-14) — zero pairing failures when counts match.
- Unit fixture with intentional parallel reorder; lifecycle scenario on Claude haiku.

## Residual risks

- **Same-name parallel batch** — two `Read` calls in one JSONL batch are paired by name only; results may be swapped even when counts match. `meta["pairing_uncertain"]` is set when a batch contains duplicate tool names.
- **Interrupted session** — missing trailing tool results → `meta["pairing_uncertain"]` when `len(store results) != tool_use count`; digest still renders with empty results for orphaned calls.
- **Format changes** — undocumented Cursor on-disk schema.

## Rejected alternatives (spike)

- **Blob DAG walk** — `latestRootBlobId` BFS reached 1/1149 blobs on a large session; cannot recover transcript order from `store.db` alone.
- **Global sequential zip** — tool results in sqlite `rowid` order vs all JSONL `tool_use` records globally: 239/243 matches on a sample session; failures are order swaps inside parallel batches only.

See `workdir/draft-cursor-takeover-phase3-spike.md` for full spike report.

## See Also

- `engine-session-log-formats.md` — per-engine storage layout
- `takeover-feature.md` — `/lr:takeover` feature overview
- `workdir/draft-cursor-takeover-phase3-spike.md` — spike report with rejected alternatives (blob DAG, global sequential zip)
