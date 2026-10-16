---
lore: 1
type: topic
summary: "Inference (2026-10-16): local Claude Code OAuth usage probe — credential locations, GET /api/oauth/usage, headers, response field names. Method only; no tokens or personal numbers; machine ops to workstation-keeper."
parent: lore/plans-and-models.md
---

# Claude Code OAuth usage probe

**Label: inference** (2026-10-16). Derived from local reverse engineering of Claude Code
credentials and a usage request — not an Anthropic-documented stable public API. Recheck if
Anthropic changes OAuth or the path. This public Lore keeps only the **method** (endpoints,
credential *locations*, headers, useful response field names). Do not store tokens or personal
utilization numbers here. Machine install and collection (for example launchd) belong to
**workstation-keeper**, not this agent.

## Credential source (local only)

- Prefer `~/.claude/.credentials.json` (or `$CLAUDE_CONFIG_DIR`).
- On macOS, if that file is missing: Keychain generic password service
  `Claude Code-credentials`, JSON with `claudeAiOauth.accessToken`.

## Request

- `GET https://api.anthropic.com/api/oauth/usage`
- Headers: `Authorization: Bearer <accessToken>`, `anthropic-beta: oauth-2025-04-20`,
  `Accept: application/json`, and a local User-Agent string (example used in probe:
  `local-engine-usage/1.0`).

## Useful response fields

- Windows: `five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet` — each with
  `utilization`, `resets_at`, and optional `locked_reason`.
- `extra_usage` (enabled, credits, utilization).
- `seven_day_breakdown` (weekly breakdown blob).

Related plan tiers and marketed usage multipliers live in [plans and pricing](plans-and-pricing.md).
