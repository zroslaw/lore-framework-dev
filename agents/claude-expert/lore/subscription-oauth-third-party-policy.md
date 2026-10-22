---
lore: 1
type: topic
summary: "Third-party report (2026-10-22): Free, Pro, and Max OAuth tokens are for Claude Code and claude.ai only, not other products or the Agent SDK; enforcement dates and an unverified May 2026 re-opening. Verify at Anthropic before relying on it."
parent: lore/plans-and-models.md
---

# Subscription OAuth in third-party tools

**Label: third-party report** (news sources, checked 2026-10-22). I did not check the primary
Anthropic legal or compliance page. Verify the rule there before you rely on it.

## The rule

- In February 2026, the Anthropic docs said that OAuth tokens from the Free, Pro, and Max plans
  are for use only with Claude Code and claude.ai. Use in other products, including the Agent
  SDK, breaks the consumer terms. The sources disagree on the date: 18, 19, or 20 February.
- A Claude Code team member said: if you build a business on the Agent SDK, use an API key.

## Enforcement

- One source says that blocks of Max OAuth in third-party clients started on 2026-01-09.
- Another source says that subscription access for third-party harnesses such as OpenClaw stopped
  on 2026-04-04.
- **Unverified, one source** (tech-insider.org): in May 2026 Anthropic gave third-party access
  again through "programmatic credits" that are billed at API rates.

## Practical rule

- A product that runs Claude for other users needs API keys or a cloud provider (Bedrock, Vertex,
  Foundry).
- Personal use of the official Claude Code with your own subscription login is allowed.
- How a gateway changes which credential (subscription or API key) Claude Code sends:
  [Claude Code and LLM gateways](claude-code-llm-gateway.md). Building on the SDK:
  [Agent SDK](agent-sdk.md).

## Sources

- https://winbuzzer.com/2026/02/19/anthropic-bans-claude-subscription-oauth-in-third-party-apps-xcxwbn/
- https://gigazine.net/gsc_news/en/20260220-anthropic-third-party-block
- https://tech-insider.org/claude-code-agent-pricing-split-2026/
