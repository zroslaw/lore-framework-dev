---
lore: 1
type: area
summary: "ChatGPT plans and OpenAI models: plan tiers and list prices, shared Work and Codex usage, plan-gated features, and the model lineup in Chat, Work, Codex, and the API. Open before answering which plan or model; always recheck prices."
parent: lore-context.md
---

# Plans and models

Scope: the consumer and business plans (Free, Go, Plus, Pro 100/200/500, Business, Enterprise,
Edu), what each plan unlocks, how Work and Codex usage is counted, and the model lineup with API
IDs and prices.

**Never quote a price, limit, or model ID from memory.** Recheck https://learn.chatgpt.com/docs/pricing
(readable), https://chatgpt.com/pricing (blocks fetches; use a browser), and
https://developers.openai.com/api/docs/models. Models retire every few weeks.

## Plan-gated features seen in the docs

Collected across areas, checked 2026-10-14 (documented unless marked):

- **Codex**: Free and Go get Codex only in the desktop app with GPT-6 Luna (subject to rollout).
  Plus and higher: Codex on web, CLI, IDE, iOS, Codex Cloud, code review, Slack.
- **ChatGPT Work on the web**: Plus, Pro, Business, Enterprise (the matrix has no Free or Go
  column).
- **MCP, Connectors, Plugins, plugin sharing, Skills, Sites, mobile remote control**: Plus, Pro,
  Business, Enterprise (Codex and Work matrix).
- **Custom MCP server in ChatGPT**: plan list not documented; see the conflict in
  [remote MCP per surface](remote-mcp-per-surface.md).
- **Computer History**: Pro, Business, Enterprise (not Plus).
- **Ultrafast mode**: Pro 500 and eligible Enterprise and Edu.
- **Dots**: Pro 100/200/500, Business Premium, Enterprise (rolling out).
- **Security Review** (research preview): Enterprise, Business, Edu, Pro; not Plus.
- **GPT-6 Pro in the Chat picker** (help snippets): Pro 100, Pro 200, Business, Enterprise; Plus
  gets Astra only in Work and Codex.
- **API-key sign-in** for Codex: CLI, SDK, IDE, desktop local chats; no cloud features.

## Children

- [Plans and pricing](plans-and-pricing.md) — each plan's price, Work and Codex usage, credits,
  speed multipliers, Business seats.
- [Local Codex quota probe](local-codex-quota-probe.md) — inference: local `auth.json` fields and
  `GET …/wham/usage` headers/response shape for rate-limit windows (method only).
- [Models lineup](models-lineup.md) — models in Chat, Work, Codex, and the API, with IDs, prices,
  and retirements.
