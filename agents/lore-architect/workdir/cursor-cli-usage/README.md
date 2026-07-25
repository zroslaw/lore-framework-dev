# Cursor CLI usage probe (draft)

One place to read **plan quota** + **session context** for `cursor-agent` CLI sessions.

## What it returns

| Field | Meaning | Source |
|---|---|---|
| `plan_quota` | Monthly plan % (total / auto / API) | `cursor.com/api/usage-summary` |
| `session_context` | Context window % for current CLI chat | Statusline snapshot |
| Per-turn tokens | Last API call only | `cursor-agent -p --output-format json` |

**IDE chat:** not covered. Context ring is manual only.

## Scripts

| Script | Role |
|---|---|
| `lr-cursor-usage.sh` | Unified probe (`--json` for machines) |
| `lr-context-statusline.sh` | Statusline hook (writes `~/.cursor/context-usage.json`) |

## Setup

```bash
chmod +x workdir/cursor-cli-usage/*.sh
```

Add to `~/.cursor/cli-config.json`:

```json
"statusLine": {
  "type": "command",
  "command": "/absolute/path/to/workdir/cursor-cli-usage/lr-context-statusline.sh",
  "updateIntervalMs": 300
}
```

**Do not** put `statusLine` in project `.cursor/cli.json` — schema rejects it.

## Run

```bash
# Plan quota (always works when logged in)
./lr-cursor-usage.sh
./lr-cursor-usage.sh --json

# Per-turn tokens (headless)
cursor-agent -p 'ok' --output-format json -f </dev/null | jq .usage
```

Session context % appears only after an **interactive** `cursor-agent` session updates the statusline snapshot.

## Auth note

Plan quota uses `WorkosCursorSessionToken=<sub>::<jwt>` — not bare Bearer token. Derived from `state.vscdb` → `cursorAuth/accessToken`.

## Future

Candidate Lore skill: `/lr-cursor-usage` wrapping `lr-cursor-usage.sh --json`.
