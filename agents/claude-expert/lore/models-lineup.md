---
lore: 1
type: topic
summary: "Current Claude models as of 2026-10-13: Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5 with API IDs, per-token prices, default effort, shared specs, caching and batch discounts, and legacy models."
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
| Claude Haiku 5.5 | `claude-haiku-5-5` | from $0.10 / from $0.50 | medium | High-volume, latency-sensitive tasks; fastest |

## Shared specs

- All four: 1M-token context, 128K max output (300K on the Batches API with the
  `output-300k-2026-03-24` beta header, for some models), adaptive thinking (always on for Fable
  5.1 and Opus 5.5), reliable knowledge cutoff June 2026. Retirement not sooner than
  September–October 2027.
- Extended thinking with a manual `budget_tokens` is not accepted on current models. Use adaptive
  thinking with the effort parameter.
- Dateless IDs are pinned snapshots (since the 4.6 generation). The same IDs work on the Claude
  API, Google Cloud, Microsoft Foundry, and Claude Platform on AWS; Bedrock uses the `anthropic.`
  prefix.
- The Models API returns `max_input_tokens`, `max_tokens`, `line`, and a `capabilities` object
  (thinking, server tools) for each model. Read `line` rather than parsing the ID.

## Discounts

- Batch API: 50% off.
- Cache reads: 10% of base input price; 2.5% on Fable 5.1 and Claude Mythos 5.1; 5% on Opus 5.5 and
  Sonnet 5.5. Claude Mythos 5.1 appears only in the pricing notes.

## Legacy but available

Fable 5, Opus 5, Opus 4.8, 4.7, 4.6, 4.5, Sonnet 5, Sonnet 4.6, Haiku 4.5.
