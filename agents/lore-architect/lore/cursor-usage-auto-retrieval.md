# Cursor usage auto-retrieval (investigation, 2026-07-25)

Empirical investigation into whether Cursor sessions can **automatically** report usage
statistics — plan quota, session context fill, and per-turn tokens — and what a Lore-side probe
would look like. Distinct from finalize-time session archiving (`STATUS-session-archive-and-usage.md`
in workdir; shipped Feature B records tokens from session logs, not live quota).

## Two different metrics (do not conflate)

| Metric | Question it answers | Cursor IDE chat | `cursor-agent` CLI |
|---|---|---|---|
| **Plan quota** | How much of my monthly Pro/Team allowance is used? | Dashboard only (no agent API) | Yes — scriptable |
| **Session context** | How full is *this chat's* context window right now? | Ring/hover UI only | Yes — interactive CLI only |
| **Per-turn tokens** | What did the last API call cost in tokens? | Not exposed to agent | Yes — headless `-p` JSON |

Plan quota and session context are **orthogonal**. Community tools and our probe treat them as
separate data sources.

## Plan quota — buildable today (undocumented API)

**No official public API** for individual Pro accounts. Enterprise has Admin API (`cursor.com/docs/api`).

**What works (verified 2026-07-25 on Pro):**

1. Read `cursorAuth/accessToken` from Cursor's local SQLite DB:
   `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` (same path on all OSes;
   see community `cursor-usage`, CursorBar, CursorMeter).
2. Build session cookie as **`WorkosCursorSessionToken=<sub>::<jwt>`** — decode JWT payload for
   `sub`, concatenate with `::`. **Bare Bearer token or raw cookie value returns 401** (common
   integration mistake; documented in [javaisbetterthanpython/cursor-usage HOW_THIS_WAS_BUILT](https://github.com/javaisbetterthanpython/cursor-usage/blob/main/docs/HOW_THIS_WAS_BUILT.md)).
3. `GET https://cursor.com/api/usage-summary` → `individualUsage.plan.totalPercentUsed`,
   `autoPercentUsed`, `apiPercentUsed`, billing cycle dates, request counters.

**Fragility:** undocumented dashboard endpoint; response shape can change. Same class of risk as
all community usage tools.

**Also available (richer):** `POST api2.cursor.sh/.../GetCurrentPeriodUsage`, filtered usage events
on `cursor.com/api/dashboard/*` — see ClearMeasureLabs/Cursor-Usage-Status extension merge logic.

## Session context % — CLI only, interactive only

Cursor CLI exposes context window state via the **statusline** hook (`docs/engines/cursor.md` does
not yet document this; canonical spec lives in Cursor's `statusline` skill / `use-status-line.ts`
payload).

**Config:** `statusLine` in **`~/.cursor/cli-config.json`** only — **not** project
`.cursor/cli.json` (schema rejects `statusLine`; breaks `cursor-agent` if placed there).

**Payload fields (stdin JSON each turn):** `context_window.used_percentage`,
`total_input_tokens`, `context_window_size`, `remaining_percentage`, `current_usage`.

**Headless `-p` does not invoke statusline** — verified 2026-07-25: `cursor-agent -p --output-format json`
returns per-turn `usage` but writes no statusline snapshot. Context % requires **interactive**
`cursor-agent` (prompt footer).

**IDE agent chat:** context ring (Cursor 3.3+) is UI-only — not exposed to the running agent, not
found in `agent-transcripts/*.jsonl` or `store.db` blobs during this investigation. Per-chat token
counters in IDE: confirmed absent (Cursor forum, 2026).

## Per-turn tokens — headless CLI

`cursor-agent -p ... --output-format json` → top-level `usage`:
`inputTokens`, `outputTokens`, `cacheReadTokens`, `cacheWriteTokens`. No `total_cost_usd`
(empirical; see `cursor-agent-real-invocation-contract.md`). Harness and Lore Beings already depend
on this shape.

## IDE vs CLI self-awareness

An agent is **not** self-aware of limits unless given tools/scripts:

| Source | Wired how |
|---|---|
| Plan quota | Agent runs probe script or reads cached JSON |
| Session context % | Statusline writes `~/.cursor/context-usage.json`; agent reads file |
| Per-turn tokens | Parse last `cursor-agent` JSON output in the same process |

**This IDE session** cannot auto-read context % or plan quota without those tools. Mid-session
fallback: user reports ring % or runs probe externally.

## Draft implementation (workdir)

`workdir/cursor-cli-usage/` — no secrets committed; runtime reads `state.vscdb` only.

| Script | Role |
|---|---|
| `lr-cursor-usage.sh` | Unified probe: plan quota (live) + session context (snapshot); `--json` |
| `lr-context-statusline.sh` | Statusline hook → writes snapshot + prints bar |
| `README.md` | Setup, limits, auth note |

Candidate future Lore skill: `/lr-cursor-usage` wrapping `lr-cursor-usage.sh --json`.

## Community prior art (same mechanisms)

- **Menu bar:** CursorBar, CursorMeter, MeterBar, AIMeter — `state.vscdb` + dashboard API.
- **CLI:** `cursor-usage` (pip), `vladykos1/cursor-usage` — cookie `sub::jwt` + `usage-summary`.
- **Extension:** `tansdf/cursor-usage-meter`, ClearMeasureLabs/Cursor-Usage-Status — status bar +
  `api2.cursor.sh` merge.
- **Reverse-engineered API catalog:** [dmwyatt gist](https://gist.github.com/dmwyatt/1e9359b1862e7cbfe1e754fe4c8db764).

## Open gaps / non-goals

- **IDE session context %** — no stable automated path; would need Cursor-native tool or UI scrape.
- **Unified cross-engine probe** — Claude OAuth usage API and Codex `app-server account/rateLimits/read`
  are separate adapters (see session investigation arc 2026-07-25); no single vendor API.
- **Lore finalize integration** — live quota probe is orthogonal to Feature B session summary
  `usage:` frontmatter (post-hoc from logs).

## See Also

- `cursor-engine-capabilities.md` — engine hub; usage retrieval → `cursor-usage-auto-retrieval.md`
- `cursor-agent-real-invocation-contract.md` — headless JSON, no USD cost
- `cursor-cli-and-harness-operational-notes.md` — `--output-format json` usage parsing
- `cursor-agent-cli-probe-findings.md` — account quota exhaustion signature
- `workdir/cursor-cli-usage/README.md` — draft probe setup
