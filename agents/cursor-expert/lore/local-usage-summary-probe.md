---
lore: 1
type: topic
summary: "Inference (2026-10-16): how a local tool can read Cursor plan usage via GET /api/usage-summary with a WorkosCursorSessionToken cookie built from the desktop app token in state.vscdb — method only; not a documented public API."
parent: lore/plans-and-models.md
---

# Local usage-summary probe

**Inference**, untested as a public contract (2026-10-16). Observed from
`workstation-observe/tools/engine_usage.py`. Not a Cursor-documented public API. Recheck if Cursor
changes auth storage or `/api/usage-summary`. Machine collection and scripts belong to
workstation-keeper; this topic keeps only the product-side method.

**Public-repo rule:** store endpoints, credential *locations*, and cookie construction — never
tokens or personal usage numbers.

## Credential location (macOS desktop app)

- Read-only SQLite:
  `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`
- Key: `cursorAuth/accessToken` (string; may be JSON-quoted).
- Decode the JWT payload; take `sub` as the WorkOS subject.

## Request

- `GET https://cursor.com/api/usage-summary`
- Header: `Cookie: WorkosCursorSessionToken={sub}::{accessToken}`
- Also `Accept: application/json` and a local User-Agent (example:
  `local-engine-usage/1.0`).

## Useful response fields (shape only)

- `membershipType`, `billingCycleStart` / `billingCycleEnd`
- `individualUsage.plan`: percent-used fields, used/limit/remaining, breakdown
- `individualUsage.onDemand`: enabled, used, remaining

Documented product billing (pools, on-demand, CTR) stays in
[usage pools and billing](usage-pools-and-billing.md).
