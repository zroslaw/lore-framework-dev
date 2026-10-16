---
lore: 1
type: topic
summary: "Inference (2026-10-16): how a local host can read ChatGPT/Codex rate-limit windows via auth.json tokens and GET chatgpt.com/backend-api/wham/usage — method only, not a documented public API."
parent: lore/plans-and-models.md
---

# Local Codex quota probe (wham/usage)

**Inference**, checked 2026-10-16 from the workstation-observe `engine_usage` path. This is **not**
an OpenAI-documented stable public API. Recheck if OpenAI changes `auth.json` shape or the wham
usage path. Documented UI/CLI checks remain [chatgpt.com/codex/settings/usage](https://chatgpt.com/codex/settings/usage)
and Codex CLI `/status` — see [Plans and pricing](plans-and-pricing.md).

Machine collection and dashboards belong to **workstation-keeper**. This public topic keeps only
the method: endpoints, field names, and headers. Do not store tokens or personal usage numbers
here.

## Credential source (local)

- Path: `~/.codex/auth.json`, or `$CODEX_HOME/auth.json` when that env is set.
- Fields used: `tokens.access_token`, `tokens.account_id`.

## Request

- Method and URL: `GET https://chatgpt.com/backend-api/wham/usage`
- Headers:
  - `Authorization: Bearer <access_token>`
  - `ChatGPT-Account-Id: <account_id>`
  - `originator: local-engine-usage`
  - `Accept: application/json`

## Useful response fields

- Account/plan: `plan_type`
- Gate: `rate_limit.allowed`, `rate_limit.limit_reached`
- Windows: `rate_limit.primary_window` and `rate_limit.secondary_window`, each with
  `used_percent`, `limit_window_seconds`, `reset_at` (unix)
- Credits: `credits`, `rate_limit_reset_credits`

## Window → pool mapping (local tooling)

Workstation-observe maps window duration ≈5 hours → pool `five_hour`, ≈7 days → pool
`seven_day` for storage and dashboard series. That mapping is local tooling convention, not an
OpenAI field name.
