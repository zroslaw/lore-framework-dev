---
lore: 1
type: topic
summary: "OpenAI models (2026-10-14; API prices rechecked 2026-11-09): GPT-6 Astra, 6.1 Sol and Terra, 6 Sol, 6 Luna, GPT-5.6 family; surfaces, API IDs, prices, cache-write and long-context rules, retirements."
parent: lore/plans-and-models.md
---

# Models lineup

Checked 2026-10-14. Sources: https://developers.openai.com/api/docs/models and
https://learn.chatgpt.com/docs/models (documented unless marked).

## API flagship models

| Model | API ID | Price in / cached / out per MTok | Context, output | Knowledge cutoff |
|---|---|---|---|---|
| GPT-6 Astra | `gpt-6-astra` | $10 / $1 / $50 | 1.05M, 128K | 2026-04-30 |
| GPT-6.1 Sol | `gpt-6.1-sol` | $2 / $0.10 / $10 | 1.05M, 128K | 2026-04-30 |
| GPT-6 Sol | `gpt-6-sol` | $2 / $0.20 / $10 | 1.05M, 128K | 2026-04-20 |
| GPT-6 Luna | `gpt-6-luna` | $0.10 / $0.01 / $0.50 | 1.05M, 128K | 2026-05-18 |
| GPT-5.6 Sol | `gpt-5.6-sol` | $4 / $0.40 / $20 | 1.05M, 128K | 2026-02-16 |

More Standard prices from https://developers.openai.com/api/docs/pricing (checked 2026-11-09,
per MTok in / cached / out, up to 272K input): `gpt-6.1-terra` $1 / $0.05 / $5; `gpt-5.6-terra`
$2 / $0.20 / $12; `gpt-5.6-luna` $0.20 / $0.02 / $1.20. The `gpt-5.6-sol` price above is a
promotion until 2026-11-30. The other rows above were unchanged on 2026-11-09.

- A request with more than 272K input tokens is billed entirely at the long-context column
  (2x input, 1.5x output) — the whole request, not only the tokens above 272K.
- Cache writes: a 30-minute write costs 1.25x input; a 12-hour write costs 2.5x input. Codex
  credits have no cache-write charge ([plans and pricing](plans-and-pricing.md)).
- Batch and Flex are 50% off; Fast (named Priority until 2026-07-30) is 2x; Ultrafast is 6x and a
  `service_tier` only for Astra and 6.1 Sol. Web search: $10 per 1,000 calls. Data residency and
  FedRAMP: +10%.
- `reasoning.effort`: `low` to `max` (Luna also `none`). GPT-6.1 Sol was released at DevDay
  2026-09-29; it supports Responses Multi-agent (beta) and EU data residency.
- Others in the catalog: GPT-5.6 Terra and Luna, `chat-latest` (the Instant model used in ChatGPT),
  GPT-Image-2 and 2.5, GPT-Live 1 (voice), GPT-Realtime-2.1, gpt-oss-120b and 20b (open weight),
  Daybreak Blue and Red (cyber, Trusted Access only), GPT-Rosalind (life sciences).

## In ChatGPT Chat

- GPT-6.1 Sol, GPT-6 Sol, and GPT-6 Luna are in **Work and Codex, not Chat**.
- **GPT-6 Pro** (powered by Astra) is in the Chat picker for Pro 100, Pro 200, Business, and
  Enterprise; Plus gets Astra only in Work and Codex (help article 20001354, via search snippets).
- GPT-5.6 Luna is the default Chat model on Free and Go; Plus and Pro set GPT-5.6 Sol's thinking
  with a slider (What's new, 2026-08-03 to 07).

## In Work and Codex

- Recommended: GPT-6.1 Sol for complex work (Plus, Pro, Business, Enterprise, Edu; off by default
  in Enterprise and Edu); GPT-6 Astra for the hardest work; Luna for repeatable tasks. Free and Go:
  GPT-6 Luna in the desktop app.
- Desktop and web use **Power** presets (Faster to Smarter) plus **Advanced**; the CLI uses `/model`
  or `codex -m gpt-6.1-sol`. **Max** gives one model more time; **Ultra** runs subagents (not on
  Luna).
- Codex Cloud picks its model automatically.
- Retirements with ChatGPT sign-in: `gpt-5.3-codex-spark` (2026-09-14), `gpt-5.4` and
  `gpt-5.4-mini` (2026-08-31), **GPT-5.5 from ChatGPT, Work, and Codex on 2026-10-14**. The
  API is not affected; API-key Codex sessions follow API availability.

Sources: https://developers.openai.com/api/docs/models ; https://developers.openai.com/api/docs/pricing ; https://learn.chatgpt.com/docs/models ;
https://learn.chatgpt.com/docs/whats-new ; https://help.openai.com/en/articles/20001354 (snippets)
