---
lore: 1
type: topic
summary: "ChatGPT plans (2026-10-14): Free, Go $8, Plus $20, Pro $100-500, Business, Enterprise, Edu; shared Work and Codex usage, Codex credits rate card (2026-11-09; 1 credit = $0.04 API price, inference), speeds."
parent: lore/plans-and-models.md
---

# Plans and pricing

Checked 2026-10-14. Primary source: https://learn.chatgpt.com/docs/pricing (documented). List
prices in USD; recheck before use.

## Plans

| Plan | Price | Codex and Work notes |
|---|---|---|
| Free | $0 | Codex in the desktop app with GPT-6 Luna, Standard speed, subject to rollout |
| Go | $8/month | Same Codex scope as Free |
| Plus | $20/month | Codex on web, CLI, IDE, iOS; Codex Cloud, code review, Slack; GPT-6.1 Sol and GPT-6 Luna; buy extra credits |
| Pro | $100, $200, or $500/month | Everything in Plus; Ultrafast on Pro 500; no five-hour limit |
| Business | $20/user/month annual, $25 monthly, 2+ users | Desktop and mobile Codex, larger cloud VMs, SAML SSO, MFA, no training on business data by default |
| Enterprise and Edu | Contact sales | SCIM, EKM, RBAC, domain verification, Compliance API, retention and residency, priority processing |
| API key (Codex) | API rates | CLI, SDK, IDE only; no cloud features |

- Business **Premium seat**: $100/user/month annual or $125 monthly, 5x Standard usage, no
  five-hour limit; Standard and Premium seats mix in one workspace (OpenAI announcement, seen in
  search results).
- Pro tiers (third-party reports, not confirmed): Pro 500 was announced at DevDay 2026 with about
  25x Plus usage; new Pro 200 subscribers get about 10x Plus (was 20x).
- Free and Go show ads (third-party report).

## Enterprise-only and data training

- Enterprise and Edu only (plan matrix and pricing card): analytics dashboard, Analytics API,
  SCIM, EKM, RBAC, domain verification, Compliance API audit logs, data retention and residency
  controls, priority processing. Enterprise owners also export the public plugin catalog.
- Training: Business, Enterprise, and Edu do not train on business data by default, and data
  accessed through apps is not used for training on those plans (documented). Consumer plans use
  the account's data controls (not rechecked on 2026-10-14).

## How Work and Codex usage is counted

- **ChatGPT Work and Codex share the same usage limits and credits.** Chat in ChatGPT is
  separate.
- Local messages per five hours, Plus and Standard Business (estimates): GPT-6 Astra 5–45, GPT-6.1
  Sol 15–160, GPT-6 Sol 15–150, GPT-6 Luna 350–3,000. Cloud tasks use more. Weekly limits may
  apply. Pro has no five-hour limit.
- Enterprise and Edu with flexible pricing: no fixed limits; usage draws credits. Without flexible
  pricing: about Plus limits per seat.
- Speed multipliers on included usage: Fast 2.5x, Ultrafast 8x (credits: 2x and 6x). See the
  credits rate card below.
- Desktop ChatGPT Voice: $0.05 per minute of Codex budget (1.25 credits per minute on credit
  plans). Image generation uses limits 3–5x faster. Sites is included during the public beta.
- When the limit is reached mid-turn, the turn finishes. Plus and Pro can buy credits; any user can
  run local chats with an API key. Check usage at chatgpt.com/codex/settings/usage or `/status`
  in the CLI. For a local host that already has Codex OAuth on disk, an inferred
  `wham/usage` probe method (field names and headers only) is in
  [Local Codex quota probe](local-codex-quota-probe.md).
- Every enabled MCP server adds context and uses more of the limit.

## Codex credits rate card (checked 2026-11-09)

Source: https://learn.chatgpt.com/docs/pricing (documented). The help-center rate-card article
still returns HTTP 403 to fetches.

Credits per 1M tokens, Standard speed (input / cached input / output):

| Model | Credits |
|---|---|
| gpt-6-astra | 250 / 25 / 1,250 |
| gpt-6.1-sol | 50 / 2.5 / 250 |
| gpt-6.1-terra | 25 / 1.25 / 125 |
| gpt-6-sol | 50 / 5 / 250 |
| gpt-6-luna | 2.5 / 0.25 / 12.5 |
| gpt-5.6-sol | 100 / 10 / 500 |
| gpt-5.6-terra | 50 / 5 / 300 |
| gpt-5.6-luna | 5 / 0.5 / 30 |

- **1 credit = $0.04 of API list price (inference).** Every row equals the API Standard price
  ([models lineup](models-lineup.md)) divided by $0.04, and voice agrees ($0.05 per minute =
  1.25 credits). OpenAI publishes no credit purchase price: it "depends on your plan or
  agreement". Use $0.04 only to convert credits to an API-equivalent cost, not as a bill.
- **Credits have no cache-write charge.** The API has one (see models lineup). So a
  credit-to-dollar conversion of a cache-heavy session is not the same as its API cost.
- Speed multipliers on credits and the API: **Fast** 2x (the tier was called **Priority** until
  the rename on 2026-07-30), **Ultrafast** 6x (only gpt-6-astra and gpt-6.1-sol). On included plan
  usage: Fast 2.5x, Ultrafast 8x. Batch and Flex: 0.5x (API).
- Extras: web search $10 per 1,000 calls; data residency and FedRAMP add 10%.
- GPT-5.6 Sol promotion: the pricing page said at least to 2026-11-21 (checked 2026-10-14); the
  API pricing page says until 2026-11-30 (checked 2026-11-09). The newer date is from the API page;
  recheck both after 2026-11-21.
- Per-session usage and cost data in local Codex records:
  [Codex session logs and resume](codex-session-logs-and-resume.md), "Usage records".

Sources: https://learn.chatgpt.com/docs/pricing ; https://developers.openai.com/api/docs/pricing ;
https://learn.chatgpt.com/docs/dots ;
https://openai.com/index/premium-seats-chatgpt-business (search snippet) ; third-party:
https://letsdatascience.com/news/openai-introduces-500-chatgpt-pro-500-tier-329fe640 ;
https://www.cometapi.com/chatgpt-pricing-2026-free-vs-go-vs-plus-vs-pro/
