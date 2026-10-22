---
lore: 1
type: topic
summary: "Documented (2026-10-22): Claude Code behind an LLM gateway — supported API formats, no support for non-Claude models, the Claude apps gateway, managed-settings lock to one endpoint, and how a gateway changes subscription billing and limits."
parent: lore/claude-apps-and-surfaces.md
---

# Claude Code and LLM gateways

**Label: documented.** Source: https://code.claude.com/docs/en/llm-gateway, checked 2026-10-22.
Recheck it before relying on version numbers or setting names.

## What Claude Code accepts

- Claude Code works with any gateway that exposes a supported API format: the Anthropic Messages
  format, or the provider formats for Bedrock, Vertex, and Foundry. The gateway compatibility
  guide gives the details: https://code.claude.com/docs/en/llm-gateway-protocol.
- Anthropic does not endorse, maintain, or audit third-party gateways. **Anthropic does not
  support routing Claude Code to non-Claude models through any gateway.**
- Anthropic has its own self-hosted gateway, the **Claude apps gateway** (SSO, OTLP telemetry):
  https://code.claude.com/docs/en/claude-apps-gateway.

## What a gateway gives

- Central credentials, usage attribution, budgets and rate limits, audit logs, and provider
  switching.
- You can switch the provider without a change on the developer machines only when the gateway
  exposes one Anthropic-format endpoint.
- Keep the gateway updated as Claude Code adds features. If the gateway does not forward a
  feature, that feature breaks.

## Lock Claude Code to the gateway

Set `allowedProviders: ["customEndpoint"]` in managed settings, and put the gateway
`ANTHROPIC_BASE_URL` in the `env` of the same file. Then the gateway is the only destination that
Claude Code accepts. This needs Claude Code v2.1.285 or later.

## Subscriptions and gateways

- When a gateway credential variable or `apiKeyHelper` is active, requests carry that credential,
  not the claude.ai login. The subscription limits do not apply, and the credential owner pays
  per token.
- If you set only `ANTHROPIC_BASE_URL`, with no credential, the saved claude.ai login stays
  active. Requests go through the gateway, but the subscription limits and billing still apply.
- A gateway that passes this subscription traffic on to Anthropic must forward the OAuth
  capability in the `anthropic-beta` header.

Which products may use a subscription OAuth login at all is in
[subscription OAuth in third-party tools](subscription-oauth-third-party-policy.md).
