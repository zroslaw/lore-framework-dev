---
lore: 1
type: topic
summary: "Managed Agents pricing (2026-10-18): tokens plus $0.08 per active session-hour and $10 per 1,000 web searches, USD session budgets, early users, and third-party prices of AWS, Google, Microsoft, E2B, and Daytona alternatives."
parent: lore/managed-agents.md
---

# Managed Agents — pricing, adoption, and alternatives

Checked 2026-10-18. Recheck prices on the official pages before quoting them.

## Pricing

**Documented** — the bundled `claude-api` skill, `shared/managed-agents-core.md` § Session
budgets.

- Model tokens at the served model's list price ([models lineup](models-lineup.md)). Tokens are
  the bulk of any bill.
- Session running time: **$0.08 per hour**, counted only while the session is active
  (`active_seconds`; overlapping threads count once).
- Web search: **$10 per 1,000** searches. Web fetch is not metered.
- Optional per-session budget in USD (given in minor units). At the cap the session pauses with
  `stop_reason: budget_reached`, and the history and sandbox are kept.

## Adoption

**Third-party reports.**

- Launch-period coverage names Notion, Asana, Rakuten, Sentry, and Allianz as early users.
  Anthropic's ABC Legal story is the most detailed case study:
  https://claude.com/blog/how-abc-legal-turned-every-employee-into-a-builder-with-claude-managed-agents
- I found no public aggregate usage numbers. One survey (cited in
  https://trilogyai.substack.com/p/the-plumbing-wars-are-claude-managed) puts Anthropic's agent
  tooling far behind Microsoft Copilot Studio / Azure.

## Alternatives

**Third-party reports; the numbers disagree between sources.** Sources:
https://www.ud.hk/en/insight/article/agent-platform-cost-compared-2026-09-04,
https://aimultiple.com/ai-agent-platforms.

- **AWS Bedrock AgentCore:** about $0.0895 per vCPU-hour + $0.00945 per GB-hour (a v2 runtime is
  about $0.1276).
- **Google Vertex AI Agent Engine** (rebranded Gemini Enterprise Agent Platform): about $0.086 per
  vCPU-hour.
- **Microsoft Foundry Agent Service:** no service fee; tokens and tool calls are billed.
- **E2B, Daytona:** sandbox only (about $0.05–0.17 per hour); you bring your own loop, for
  example the [Agent SDK](agent-sdk.md). Daytona can be self-hosted.
- **OpenAI Agents SDK** added a hosted multi-agent beta in July 2026. Detail belongs to
  openai-expert.

## How to apply

When asked "is it expensive", say that the platform fee is small and tokens dominate on every
option. The real reasons to choose another option are models from more than one vendor, an
existing cloud commitment, the sandbox limits (10 GB disk, no custom image —
[environments](managed-agents-environments-and-data.md)), or beta risk.
