---
lore: 1
type: topic
summary: "OpenAI models as of 2026-10-14: GPT-6 Astra, GPT-6.1 Sol, GPT-6 Sol, GPT-6 Luna, GPT-5.6 family; where each runs (Chat, Work, Codex, API), API IDs and prices, reasoning levels, and retirements."
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

- Prompts over 272K input tokens cost 2x input and 1.5x output. Cache writes cost 1.25x input.
  Batch and Flex are 50% off; Fast mode is 2x. Ultrafast is a `service_tier` for Astra and 6.1 Sol.
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
  `gpt-5.4-mini` (2026-08-31), **GPT-5.5 from ChatGPT, Work, and Codex on 2026-10-14** (today). The
  API is not affected; API-key Codex sessions follow API availability.

Sources: https://developers.openai.com/api/docs/models ; https://learn.chatgpt.com/docs/models ;
https://learn.chatgpt.com/docs/whats-new ; https://help.openai.com/en/articles/20001354 (snippets)
