---
lore: 1
type: topic
summary: "How Cursor bills usage (2026-10-14): Cursor Models vs Other Models pools, on-demand usage, the Cursor Token Rate on Teams and Enterprise, BYOK, Auto billing, subagent billing, Max Mode on legacy request plans, and Bugbot billing."
parent: lore/plans-and-models.md
---

# Usage pools and billing

Checked 2026-10-14. Documented unless a line says otherwise. This describes the Cursor plan family
in the docs. The X Subscription uses one weekly pool shared with Grok
([plans and pricing](plans-and-pricing.md)).

## Two pools

- **Cursor Models**: Grok 4.7, Grok 4.6, Grok 4.5, Composer 2.5. "Significantly more included
  usage" than third-party models.
- **Other Models**: third-party models at each model's API price. Pro, Pro+, Ultra, and Teams
  include it; Start does not.
- Both reset monthly. The Spending tab at cursor.com/dashboard shows both pools and on-demand
  charges.

## After the included usage

- **On-demand usage**: pay as you go at the same API rates, billed monthly. "Requests are never
  downgraded in quality or speed." Or upgrade the plan.
- Spend limits and spend alerts are on the dashboard. Teams have on-demand enabled by default for
  Grok Bot usage.

## Cursor Token Rate (Teams and Enterprise)

- $0.25 per million tokens (input, output, and cached) on top of the API price for **third-party**
  model requests: included, on-demand, and BYOK usage, and when Auto routes to a third-party model.
- Cursor's own models (Grok, Composer) are exempt.

## Auto, subagents, BYOK

- All Auto modes (Cost, Balance, Intelligence) bill at the list price of the model each request is
  routed to. A third-party route draws from Other Models.
- A subagent bills at the model that ran it; a named third-party model draws from Other Models
  even when the parent chat is on Auto, Grok, or Composer.
- **BYOK** (own provider API key; AWS Bedrock via IAM role or `agent bedrock`): on individual plans
  it draws from no pool; the provider bills the user. On Teams and Enterprise the Cursor Token Rate
  still applies. Admins can restrict personal keys. ZDR does not cover BYOK traffic.

## Legacy request-based plans

- Older plans counted requests instead of tokens. **Max Mode** exists only there: larger context,
  subagents, image generation, and the newest models, at API rate plus 20%. Current usage-based
  plans have no Max Mode; many models are marked "Requires Max Mode on legacy request-based plans".
- On legacy plans without Max Mode, subagents run on Composer.

## Product-specific billing

- **Cloud agents and Automations**: API rate of the chosen model; automations use the maximum
  context. "Run as Service account" bills the team pool.
- **Bugbot**: usage-based since mid-2026 (average run $1.00–$1.50). Individuals: included usage
  first, then on-demand; Teams: on-demand. Seat-based legacy Bugbot ($40/seat) ends at the first
  renewal after 2026-06-08 ([Bugbot and Automations](bugbot-and-automations.md)).
- **SDK**: same pools and rules as the IDE; shown under an SDK tag on the usage dashboard.
- **Data residency**: 10% uplift on eligible model prices.

Sources: https://cursor.com/docs/models-and-pricing.md ; https://cursor.com/help/models-and-usage/usage-limits.md ;
https://cursor.com/help/models-and-usage/token-rate.md ; https://cursor.com/docs/cursor-router.md ;
https://cursor.com/docs/subagents.md ; https://cursor.com/help/ai-features/max-mode.md ;
https://cursor.com/docs/account/pricing/request-based-legacy.md ;
https://cursor.com/help/account-and-billing/bugbot-usage-based-billing.md ; https://cursor.com/docs/sdk/typescript.md ;
https://cursor.com/help/security-and-privacy/privacy.md ; https://cursor.com/help/grok-bot/plans.md
