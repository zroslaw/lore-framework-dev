---
lore: 1
type: topic
summary: "ChatGPT plans as of 2026-10-14: Free, Go $8, Plus $20, Pro $100/$200/$500, Business $20-25 (Premium seat $100-125), Enterprise and Edu; shared Work and Codex usage, local message estimates, credits, speed multipliers."
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
- Speed multipliers on included usage: Fast 2.5x, Ultrafast 8x (credits: 2x and 6x).
- Credit rates per 1M tokens (input / cached / output): GPT-6 Astra 250 / 25 / 1,250; GPT-6.1 Sol
  50 / 2.5 / 250; GPT-6 Luna 2.5 / 0.25 / 12.5. GPT-5.6 Sol promotional pricing runs at least to
  2026-11-21.
- Desktop ChatGPT Voice: $0.05 per minute of Codex budget (1.25 credits per minute on credit
  plans). Image generation uses limits 3–5x faster. Sites is included during the public beta.
- When the limit is reached mid-turn, the turn finishes. Plus and Pro can buy credits; any user can
  run local chats with an API key. Check usage at chatgpt.com/codex/settings/usage or `/status`
  in the CLI.
- Every enabled MCP server adds context and uses more of the limit.

Sources: https://learn.chatgpt.com/docs/pricing ; https://learn.chatgpt.com/docs/dots ;
https://openai.com/index/premium-seats-chatgpt-business (search snippet) ; third-party:
https://letsdatascience.com/news/openai-introduces-500-chatgpt-pro-500-tier-329fe640 ;
https://www.cometapi.com/chatgpt-pricing-2026-free-vs-go-vs-plus-vs-pro/
