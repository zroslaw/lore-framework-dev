---
lore: 1
type: topic
summary: "Current Claude models (2026-10-13): Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5 with API IDs, effort, and specs; full API price table with cache, fast mode, US-only, and tool fees (2026-11-09); legacy models."
parent: lore/plans-and-models.md
---

# Models lineup

Source: https://platform.claude.com/docs/en/about-claude/models/overview, checked 2026-10-13
(documented). Third-party price lists were out of date or wrong; always check this page.

| Model | API ID | Price in/out per MTok | Default effort | Use |
|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | $10 / $50 | high | Demanding reasoning, long-horizon agentic work; slowest |
| Claude Opus 5.5 | `claude-opus-5-5` | $4 / $20 | medium | Recommended default for most workloads; agentic coding and knowledge work |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10 | high | Best balance of speed and intelligence |
| Claude Haiku 5.5 | `claude-haiku-5-5` | $0.10 / $0.50 (prompt ≤100K tokens); $0.50 / $2.50 above | medium | High-volume, latency-sensitive tasks; fastest |

## Shared specs

- All four: 1M-token context, 128K max output (300K on the Batches API with the
  `output-300k-2026-03-24` beta header, for some models), adaptive thinking (always on for Fable
  5.1 and Opus 5.5), reliable knowledge cutoff June 2026. Retirement not sooner than
  September–October 2027.
- No long-context premium on 4.6 and later models; Haiku 5.5 is the exception above 100K-token
  prompts (checked 2026-10-18; see [long-context cost](long-context-cost.md)).
- Extended thinking with a manual `budget_tokens` is not accepted on current models. Use adaptive
  thinking with the effort parameter.
- Dateless IDs are pinned snapshots (since the 4.6 generation). The same IDs work on the Claude
  API, Google Cloud, Microsoft Foundry, and Claude Platform on AWS; Bedrock uses the `anthropic.`
  prefix.
- The Models API returns `max_input_tokens`, `max_tokens`, `line`, and a `capabilities` object
  (thinking, server tools) for each model. Read `line` rather than parsing the ID.

## API prices with cache (checked 2026-11-09)

Source: https://platform.claude.com/docs/en/about-claude/pricing and
https://code.claude.com/docs/en/fast-mode (documented). USD per million tokens.

| Model | Input | 5m cache write | 1h cache write | Cache read | Output |
|---|---|---|---|---|---|
| Fable 5.1 | 10 | 12.50 | 20 | 0.25 | 50 |
| Opus 5.5 | 4 | 5 | 8 | 0.20 | 20 |
| Opus 5, Opus 4.8 | 5 | 6.25 | 10 | 0.50 | 25 |
| Sonnet 5.5 | 2 | 2.50 | 4 | 0.10 | 10 |
| Sonnet 5 | 2 | 2.50 | 4 | 0.20 | 10 |
| Haiku 5.5 (prompt ≤100K) | 0.10 | 0.125 | 0.20 | 0.01 | 0.50 |

- Cache writes: 1.25× input (5-minute TTL), 2× input (1-hour TTL).
- Cache reads: 0.1× input by default; 0.05× on Opus 5.5 and Sonnet 5.5; 0.025× on Fable 5.1 and
  Claude Mythos 5.1 (Mythos appears only in the pricing notes).
- Sonnet 5: its introductory price is now the standard price.
- Haiku 5.5: 5× every price when the prompt is over 100K tokens, cache tokens included
  ([long-context cost](long-context-cost.md)).
- **Fast mode:** Opus 5.5 $8 / $40; Opus 5 and Opus 4.8 $10 / $50 (input / output). Cache and
  US-region multipliers apply on top. In Claude Code on a subscription, fast mode always draws
  usage credits, which are real money ([cost data](agent-observability-and-cost.md)).
- **US-only inference** (`inference_geo: "us"`): ×1.1 on token prices, not on tool fees.
- **Tool fees:** web search $10 per 1,000 searches; web fetch has no fee.
- **Batch API:** 50% off.
- **Tokenizer:** Claude 4.7 and later models use a tokenizer that gives about 30% more tokens for
  the same text. Compare cost per task, not only price per token.

## Legacy but available

Fable 5, Opus 5, Opus 4.8, 4.7, 4.6, 4.5, Sonnet 5, Sonnet 4.6, Haiku 4.5.
