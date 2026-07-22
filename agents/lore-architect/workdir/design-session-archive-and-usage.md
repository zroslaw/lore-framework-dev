# Design: Session Archive + Session Usage Tracking

Status: DRAFT — round 2, post-review (2 parallel lenses: correctness/feasibility verified against the real codebase and live logs; scope/framework-fit checked against convention lore). Both rounds' findings are folded in below; nothing is left unresolved except where explicitly marked as a deferred seam.
Worktrees: `<workspace>/.worktrees/lore-framework/session-archive-cost` (branch `lore-architect/session-archive-cost`, based on `lr--v1.27.0`), `<workspace>/.worktrees/lore-framework-dev/session-archive-cost-dev` (branch `lore-architect/session-archive-cost-dev`, based on `lore-framework-dev` `main`). Deliberately isolated from the unpushed v28 (Lore Beings) work per user instruction — do not merge into v28.

## Problem

Today `/lr:finalize` only preserves a *summary* (`docs/summarize.md`) of a session — a human-written narrative. The full conversation, including every tool invocation and its output, exists only in the engine's native session log (`~/.claude/projects/...`, `~/.codex/sessions/...`, `~/.cursor/...`), which is not committed anywhere, not partitioned, not durable, and not portable across machines. We're losing the detail needed to later teach future agents, regenerate lore from raw history, or audit what actually happened.

Two features, designed together because they share the same underlying mechanism (parsing an engine-native session log):

- **Feature A — Session Archive.** At finalize time, convert the current session's native log into a lossless, engine-agnostic representation (all messages, all tool calls with full args/results) and commit it to a month-partitioned archive directory, pushed alongside the summary.
- **Feature B — Session Usage.** At finalize time, capture total tokens, cost (USD, when derivable), and the list of distinct models used, and fold it into the summary's frontmatter.

## Non-goals (v1)

- No new user-facing skill/command. Both features are automatic sub-steps of `/lr:finalize` (specifically, phase 3 — summarize). No changes to `/lr:takeover`'s user-facing behavior.
- No retroactive backfill of archives/usage for past sessions.
- No cost computation for Codex or Cursor models (neither engine reliably exposes cost; see Feature B). Tokens and models yes, cost no — reported honestly as `unavailable`, not guessed.
- No new git remote. The archive lives in the same agent repo as `sessions/`, riding the existing commit+push in finalize phase 4.
- No repo-size mitigation beyond gzip (no truncation, no retention/pruning policy). Flagged as an accepted tradeoff, not solved here.

## Existing building blocks (from research)

- `lore-framework/scripts/session-takeover` (923-line stdlib-only Python) already has, per engine (codex/claude/cursor): log discovery (`list_<engine>`), log parsing (`parse_<engine>` → `(meta, messages)`), and a markdown digest renderer (`render_markdown`). This is the reusable core for Feature A.
- **Clipping happens at parse time**, not render time: `_claude_call_summary`/`_claude_result_text` (and the codex/cursor equivalents) truncate and reformat args/results *inside* `parse_claude`/`parse_codex`/`parse_cursor` before the message even reaches `render_markdown`. The existing `--json` dump option serializes this already-clipped message list — it is not a lossless dump today. Feature A must capture raw values at the same point in the parse loop, as new additive fields, not by modifying the existing clipped `args`/`result` fields (keeps `/lr:takeover`'s digest behavior byte-for-byte unchanged — zero regression risk to a BETA feature already in production use).
- `docs/summarize.md` Step 1 generates a fresh session UUID (`python3 -c "import uuid; print(uuid.uuid4())"`) — a **different value** from the engine's own native session id. Step 12 already documents the correlation trick: `grep -rl "<full-uuid>" ~/.claude/projects/` finds the native JSONL because running that UUID-generation command is itself a tool call that gets written into the transcript. **Feature A reuses this exact mechanism** to solve session self-identification (see below) instead of inventing new machinery.
- `docs/finalize.md` phase 4 (commit+push) already does `git -C <repo> add agents/` per touched repo — scoped to the whole `agents/` subtree. If the archive lives at `agents/<agent>/archive/...`, it rides this existing `git add` with **zero changes needed** to phase 4.
- Cost precedent: `scripts/lrb.py` (Being Keeper) documents that Claude reports `total_cost_usd` in its own CLI result envelope (a vantage point *external* to a running session — not available to us, since finalize runs *inside* the live session and only has the JSONL transcript, not a wrapping process's stdout), while Codex/Cursor don't reliably report cost at all and Keeper falls back to a configured flat rate. We adopt the *labeling* convention (`cost_source: reported|computed|unavailable`) but not the flat-rate mechanism — see Feature B.

## Feature A — Session Archive

### Storage layout

```
<lore-agent-repo>/agents/<agent>/archive/<YYYY>/<MM>/<YYYY-MM-DD>-<short-uuid>.jsonl.gz
```

Identical partitioning to `sessions/`, same `<short-uuid>` as the paired summary (first 8 hex chars of the session UUID) — trivial 1:1 correlation by filename stem, no extra bookkeeping. Lives under `agents/<agent>/`, so it's automatically included by finalize phase 4's existing `git add agents/`.

Only the **host** agent gets an archive (there is exactly one native session log per running process, regardless of how many guest agents are attached). Guests are unaffected — no schema change to guest summaries in v1.

### Format

Gzipped JSONL. Line 1 is a header object; each following line is one generalized conversation turn.

```json
{"schema_version": 1, "engine": "claude", "native_session_id": "...", "lore_uuid": "<full session uuid>", "cwd": "...", "generated_at": "2026-07-20T12:00:00Z"}
{"seq": 1, "role": "user", "ts": "2026-07-20T11:40:03Z", "text": "..."}
{"seq": 2, "role": "assistant", "ts": "2026-07-20T11:40:12Z", "model": "claude-sonnet-5", "text": "...", "tool_calls": [{"id": "toolu_01", "name": "Bash", "args": {"command": "..."}, "result": {"text": "...", "is_error": false}}], "usage": {"input_tokens": 123, "output_tokens": 45, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}
```

`schema_version` is a hard requirement — this is meant to be consumed by future tooling (lore regeneration, agent training), so the shape must be versioned from day one. Fields are omitted (not null-padded) when an engine doesn't expose them — never fabricate `ts`/`usage`/`model` when the source log doesn't have it. No truncation of args/results in v1 (see Non-goals) — gzip is the only size mitigation.

### Session self-identification (the hard part)

Problem: to build the archive, we need to know *which* native log file on disk is *this* running session's log — there's no session-id environment variable to read, and multiple recent logs may exist for the same project directory.

Solution: reuse the UUID-grep correlation already documented in `summarize.md` Step 12, but proactively instead of after-the-fact:

1. New summarize sub-step runs **after** Step 1 (UUID generation) — call it **Step 1.5**. By this point the freshly generated UUID has already appeared in the transcript (the bash command that printed it *is* the transcript).
2. List candidate native logs for the current engine + project, most-recently-modified first (reuse `list_<engine>` / the same discovery logic `--list` already uses).
3. Grep each candidate for the UUID string, most-recent first; the first match is the native log for this session.
4. **Fallback, not a hard failure**: if no candidate matches (edge case — e.g. an engine whose transcript hasn't flushed the UUID line yet), fall back to "most recently modified log for this project" and print a one-line warning (no persisted confidence field — see the "Cut from round 1" note under Feature B). Never abort finalize over this — matches summarize's own "additive, non-blocking" philosophy.

### Script changes

All changes are **additive** to `scripts/session-takeover` — no existing function's return shape for the digest path changes. Verified safe against the live code: `render_markdown` (759-799) reads only its existing named keys, and the `pending`-dict tool/result correlation logic is untouched by adding new keys alongside the ones it already sets. Confirmed against a real `~/.claude/projects/*.jsonl`: `message.usage` has exactly `input_tokens`/`output_tokens`/`cache_creation_input_tokens`/`cache_read_input_tokens`, `message.model` = e.g. `claude-sonnet-5`.

- `parse_codex`, `parse_claude`, `parse_cursor`: alongside the existing clipped `args`/`result` fields, unconditionally also capture `raw_args` (the untruncated, unreformatted original value — e.g. the raw dict for Claude/Cursor tool input, the raw JSON-decoded args for Codex), `raw_result` (untruncated result content, no line-filtering), and `ts` (per-record timestamp, when the record carries one). Cheap — no extra file I/O, just capturing values already in hand instead of discarding them.
- **`meta["models"]` is a brand-new key, not a repurposing of `meta["model"]`.** `render_markdown:785` prints `meta["model"]` (singular, first-seen) for the digest — that must stay byte-for-byte unchanged. Add a fully separate `meta["models"]`: an ordered-unique list, appended to every time a model field is observed. For Cursor, only a session-level `lastUsedModel` is available (no per-message granularity in the currently-read data path) — report it as a single-element list with `models_source: "session-level-last-used"` vs `"per-message"` for Claude/Codex, so consumers know the completeness level. Do not claim per-message fidelity Cursor doesn't have.
- **Claude sidechain (subagent) records must be included, not skipped, on the archive path.** `parse_claude` currently does `if rtype not in ("user","assistant") or record.get("isSidechain"): continue` (session-takeover:211) — this drops subagent/Task transcripts entirely from both the digest *and*, if left as-is, the archive and token totals. Since real tokens/cost were spent on that work, silently excluding it would make Feature B actively misleading, not just incomplete.
  **Exact mechanism** (symmetric with how clipping was moved from render-time to parse-time-additive): stop dropping sidechain records inside `parse_claude`'s loop — only filter truly irrelevant `rtype`s there. Instead, tag every emitted message `"sidechain": bool(record.get("isSidechain"))` (plus whatever thread-identifying field the record carries, e.g. `parentUuid`, if present — verify exact field name against a real fixture during implementation). Move the sidechain exclusion into `render_markdown` as one added skip condition (`if msg.get("sidechain"): continue` when building the digest). Net effect: `render_markdown`'s output is byte-identical to today for every existing fixture (it now filters at render time exactly what used to be filtered at parse time — same messages excluded, same digest), while the archive renderer (new, consumes the same `messages` list) includes everything. **Verify byte-identical digest output against existing fixtures as part of implementation, not just by inspection.**
  Usage aggregation: sum sidechain usage into the same session-wide token/cost totals — those tokens were genuinely spent regardless of thread.
- `meta["usage"]`:
  - **Claude**: sum `message.usage` across all assistant records (main-thread and sidechain, per above).
  - **Codex**: confirmed available via a record type `parse_codex` doesn't currently handle — `{"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": ..., "cached_input_tokens": ..., "output_tokens": ..., "reasoning_output_tokens": ..., "total_tokens": ...}}}}`. **This is cumulative, not per-turn** — take the *last* such record's `total_token_usage`, don't sum across records. Add handling for `rtype == "event_msg"` with `payload.type == "token_count"`.
  - **Cursor**: confirmed unavailable — spot-checked a real `store.db`; its meta keys are `[agentId, createdAt, isRunEverything, latestRootBlobId, mode, name]` and the first 200 blobs carry no token/usage/cost field. `usage: unavailable` for Cursor, not a fabricated zero.
- **One combined CLI verb, not two.** `session-takeover archive <session-id|path> -o <archive.jsonl.gz> --stats <stats.json>` — writes the full-fidelity gzipped JSONL *and* emits the Feature B usage/cost/model JSON in the same invocation (the normal finalize path always needs both; a standalone `stats`-only verb was speculative flexibility nobody asked for). Deferred seam: split into two verbs later if a caller ever needs stats without writing an archive — not needed for v1.
- New `--find-by-uuid <uuid> --engine <engine> [--limit N]` discovery mode implementing the grep-based resolution above, reusing `list_<engine>`.
- **Archive is an inherent mid-finalize snapshot.** Step 1.5 (below) runs before the rest of finalize completes, so the archive can never capture finalize's own tail end (the remaining summarize/commit/push steps). This is a fundamental limitation of archiving from inside the live session, not a bug — document it plainly rather than implying full losslessness.

## Feature B — Session Usage

### Frontmatter addition to `docs/summarize.md`'s host schema

```yaml
usage:
  models: [claude-sonnet-5]
  models_source: per-message   # per-message | session-level-last-used | unavailable
  tokens:
    input: 123456
    output: 45678
    cache_read: 90000
    cache_creation: 12000
  cost_usd: 4.32
  cost_source: computed        # reported | computed | unavailable
archive:
  path: agents/lore-architect/archive/2026/07/2026-07-20-<short-uuid>.jsonl.gz
  schema_version: 1
```

Additive only — matches the existing "unknown fields are tolerated by design" schema philosophy in `summarize.md`. No guest-schema change in v1 (guests can follow `host_summary_path` to find usage/archive info; not duplicating it).

**Cut from round 1**: a `native_session_id_confidence: verified|heuristic` field was dropped per MVP-minimalism review — nothing in v1 consumes it, it's a provenance breadcrumb with no reader. The heuristic-fallback *behavior* (see below) is kept; when it triggers, finalize just prints a one-line warning (matches the "non-blocking, warn and continue" pattern used elsewhere in summarize) instead of persisting a field nobody reads yet. Reintroduce as a real field if a future consumer needs to branch on it.

### Cost computation

- **Claude**: no dollar-cost field is confirmed present in the transcript itself (Keeper's `total_cost_usd` comes from an external CLI-invocation vantage point we don't have here) — so v1 computes cost from aggregated tokens × a small `PRICING` table for known Claude model ids. **Round-2 correction**: the bundled `claude-api` reference skill (`shared/models.md`) only has a confirmed price for one model (Fable 5, $10/$50 per MTok) — Sonnet 5/Opus 4.8/Haiku 4.5 prices are not present in that doc, and hardcoding remembered numbers would be exactly the kind of fabrication this design otherwise refuses to do for Codex/Cursor. Implementation must fetch current authoritative per-model pricing (e.g. Anthropic's published pricing page) at build time and cite the source URL + fetch date in a script comment next to `PRICING`, so a future maintainer knows when to refresh it. **If that fetch isn't possible or a model's price can't be confirmed, `cost_source: unavailable` for that model — same honesty bar as Codex/Cursor, no guessed numbers ship.** `cost_source: computed` only applies to models with a confirmed, cited price.
- **Codex / Cursor**: `cost_source: unavailable` in v1, full stop — no flat-rate fallback, no pricing table. Neither engine's currently-parsed log data gives token-level pricing inputs we trust, and per the Non-goals section, guessing invites silent staleness. This can be revisited once there's a concrete, engine-appropriate pricing source (out of scope here).

### Per-engine capability matrix (what's honestly achievable in v1)

| | Claude | Codex | Cursor |
|---|---|---|---|
| Archive (lossless conversation, incl. sidechains for Claude) | yes | yes | yes (existing store.db tool-result pairing reused) |
| Tokens | yes (per-message `usage`, summed incl. sidechains) | yes (`event_msg`/`token_count`, cumulative — take last) | unavailable (confirmed: no token/usage field in `store.db`) |
| Models list | yes (per-message) | yes (per turn_context) | single value only (`lastUsedModel`) |
| Cost | computed (pricing table) | unavailable | unavailable |

All four rows verified against real on-disk logs on this machine during review, not assumed from documentation.

## Finalize integration

`docs/summarize.md` gains one new sub-step, **Step 1.5 — Resolve and archive the native session log**, inserted between existing Step 1 (generate UUID) and Step 2 (resolve host/participants). Runs the combined `session-takeover archive ... --stats ...` verb against the resolved native log; stores the returned usage JSON for use when assembling frontmatter in Step 8, and writes the `.jsonl.gz` archive file directly to its final path (directories created on demand, same as Step 10 already does for summaries).

**Applies to standalone `/lr:summarize` too, not just finalize.** Step 1.5 lives inside `summarize.md` itself, which both `/lr:finalize` and standalone `/lr:summarize` execute — so a standalone summarize also produces an archive. This is deliberate, not an oversight: the mechanism lives in one place, behaves the same regardless of caller, and standalone summarize already writes committable files the user is expected to review before committing themselves (see `summarize.md` Step 11).

**Bonus, essentially free given the design**: Step 2's `start` timestamp is normally "best-effort from session memory, rounded to nearest 5 minutes." Since Step 1.5 already computes the archive's earliest message timestamp as a side effect, Step 2 should prefer that value when Step 1.5 succeeded — strictly more accurate, no new computation, no scope added.

**Idempotency**: Step 1 already generates a fresh UUID on every summarize run, so running finalize twice in one session was already producing a second, independent summary file today — this is existing, accepted behavior, not something this design introduces. The archive follows the same pattern: a second run produces a second archive under a different `<short-uuid>` stem, and both are retained. No dedup/detection logic is added — consistent with how repeat summaries already work.

Failure handling matches existing summarize philosophy: **non-blocking**. If session resolution fails, or the script errors, log a one-line warning and proceed without the `usage`/`archive` frontmatter keys — the summary still gets written. This must never be able to fail finalize.

No changes needed to `docs/finalize.md` phase 4 (commit+push) — archive files under `agents/<agent>/archive/` ride the existing `git add agents/` scoping automatically, one commit per repo, same as today.

## Versioning & Cache (added per scope-fit review — was missing entirely in round 1)

This ships as the next framework version after v27 (**not** v28 — v28/Lore Beings is unpushed, unrelated, and explicitly out of scope per the user's isolation instruction; this work is branched off the `lr--v1.27.0` tag and will need to be sequenced by whoever merges it relative to whichever of v28/this lands first). At ship time:

- Bump all four version-bearing plugin manifests to `1.<N>.0` (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json`).
- Add `release-notes/<N>.md`. This is a **release-notes-only** change (no migration) — no on-disk change to existing agent repos is required; `sessions/` layout is untouched, `archive/` is a purely additive new directory going forward.
- **Cache-affecting: yes.** This touches `scripts/session-takeover` and `docs/summarize.md` — a SKILL.md-referenced doc whose runtime behavior changes (summarize gains Step 1.5). Include the Clear Plugin Cache footer per `conventions.md`, hoisted near the top of the release notes.
- Backfill `versioning-release-types.md` with this version's entry (kind: release-notes only; cache-affecting: yes) in the same finalization that ships it — not deferred.

## Testing plan

- **Unit** (extend `lore-framework-dev/tests/test_session_takeover.py`'s existing pattern). **Fixture-gap correction from round-1 review**: the existing `stub_*_engine.py` fixtures emit CLI-*stdout* envelope JSON (`total_cost_usd`/`usage` from the external `lrb.py` wrapper vantage) — they do not exercise the parse/archive path at all and don't confirm anything about transcript shape. Only `cursor_takeover_fixture.py` is a real parse-path fixture precedent, and it carries no token fields (consistent with Cursor's confirmed "unavailable"). **New Claude and Codex parse-fixtures must be built from scratch** — synthetic JSONL shaped like real transcripts, including at least one sidechain record (Claude) and one `event_msg`/`token_count` record (Codex) — there is nothing to "reuse" for those two engines today. Cover: raw field capture (`raw_args`/`raw_result` not truncated where clipped `args`/`result` would be), sidechain inclusion + tagging, Codex cumulative-token-count last-wins logic, combined `archive` verb JSONL schema conformance + gzip roundtrip, stats output shape (models list, token sums, `cost_source` enum correctness including "unavailable" paths and unknown-model Claude), and the UUID-grep resolution logic (including the heuristic fallback path) against a synthetic multi-session-log directory.
- **E2E / lifecycle** (extend `lore-framework-dev/tests/lifecycle/test_takeover.py`'s pattern + the finalize lifecycle scenarios): a full `/lr:finalize` run per engine (claude/codex/cursor) asserting: archive file exists at the expected path, is valid gzip, its header has `schema_version`/`engine`/`lore_uuid` matching the summary's `uuid`; summary frontmatter has a well-formed `usage` block (models non-empty, `cost_source` a valid enum value even when `cost_usd` is absent); phase 4 commit includes the archive file (`git show --stat` on the finalize commit).
- All new tests must pass on all three engines before this is ready to ship, per the user's explicit requirement — this is the biggest time/budget risk in the plan and should be validated early (small smoke fixture first) rather than only at the end.

## Resolved from round-1 open questions

1. ~~Step 1.5 ordering hazard with Step 2's `start`~~ — reviewed and cleared: Step 1.5 touches no timestamps Step 2 depends on; it *feeds* Step 2 a better value (see Bonus above), it doesn't conflict with it.
2. Gzip-only, no truncation/retention policy: kept as the v1 tradeoff — accepted, not solved here (see Non-goals).
3. `archive/` committed by default, no opt-out: kept — matches "summaries are automatic, not opt-in" precedent.
4. **Closed**: new verbs stay on `scripts/session-takeover` as one canonical script. `single-canonical-source-discipline` argues against a second script re-implementing per-engine parse/discovery; splitting would force the script into an importable module the MVP doesn't need. Additive verbs on the one canonical parser is the in-convention call.
