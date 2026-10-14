---
lore: 1
type: topic
summary: "Cursor models as of 2026-10-14: own models (Grok 4.7, 4.6, 4.5 with SpaceXAI; Composer 2.5) with prices and effort levels, Auto and Cursor Router modes, the visible third-party models with per-token prices, Fast mode, and long context."
parent: lore/plans-and-models.md
---

# Models lineup

Source: https://cursor.com/docs/models-and-pricing.md and model pages, checked 2026-10-14
(documented). Prices are per million tokens: input / cache read / output.

## Cursor's own models (Cursor Models pool)

| Model | Standard | Fast | Context | Notes |
|---|---|---|---|---|
| **Grok 4.7** | $2 / $0.50 / $6 | $4 / $1 / $12 | 256k; 500k long context at 2x (Fast 3x) | Flagship. Released 2026-09-21 (x.ai). Effort low, medium, high (default), xhigh |
| Grok 4.6 | $2 / $0.50 / $6 | $4 / $1 / $12 | 256k | Released 2026-08-12 (Cursor blog). Cursor Router needs it allowed |
| Grok 4.5 | $2 / $0.50 / $6 | $4 / $1 / $18 | 256k | |
| **Composer 2.5** | $0.50 / $0.20 / $2.50 | $3 / $0.50 / $15 | 200k | Cursor's own fast coding model; Fast is the default in the product; no Cursor Token Rate |

- The Grok models are "jointly trained by Cursor and SpaceXAI" and are served in the Cursor vendor
  catalog, so teams that block the xAI provider can still allow them.
- Fast is the default speed on Pro and higher. On Start: fixed medium effort, standard speed.
- Grok 4.7 is available on desktop, web and cloud agents, CLI, SDK, Automations, and iOS.
- Cursor's help says: Grok 4.7 for hard, long work; Composer for everyday speed and cost (Composer
  is not deprecated).

## Auto and Cursor Router

- **Auto** modes: **Cost** (the old Auto logic), **Balance**, **Intelligence**. Balance and
  Intelligence use **Cursor Router**, a per-request classifier that picks the cheapest model with
  comparable quality.
- Router availability: Teams and Enterprise now (Enterprise must opt in); individual plans later.
  Router pool (help page): GPT-5.5, Claude Opus 5, Grok 4.6, Claude Fable 5; Grok 4.6 is required.
- Admins can hide or show the routed model (hidden by default) and impose Auto (soft or hard).
- SDK model id `auto-smart` with `optimize_for` = `cost`, `balanced`, or `intelligence`.
- New CLI installs default to Auto (CLI changelog).

## Third-party models shown by default

Other Models pool; API prices plus the Cursor Token Rate on Teams and Enterprise:

| Model | In / cache read / out | Notes |
|---|---|---|
| Claude Opus 5.5 | $4 / $0.20 / $20 | 300k default, 1M max; fast variant |
| Claude Sonnet 5.5 | $2 / $0.10 / $10 | 200k default, 1M max |
| Claude Haiku 5.5 | $0.10 / $0.01 / $0.50 | 5x above 100k input |
| Claude Fable 5.1 | $10 / $0.25 / $50 | Needs data-retention approval under Privacy Mode |
| GPT-5.6 Sol / Terra / Luna | $4/$0.40/$20 · $2/$0.20/$12 · $0.20/$0.02/$1.20 | 272k default, 1M long context; Sol promo pricing to 2026-11-21 |
| Gemini 4 Argon | $2 / $0.10 / $10 | |
| Gemini 3.1 Pro | $2 / $0.20 / $12 | |
| Gemini 3.8 Flash | $0.75 / $0.075 / $3.75 | |
| Muse Spark 1.3 (Meta) | $1.25 / $0.15 / $4.25 | |

Many more are "hidden by default" (older Claude, GPT-5.x and Codex models, Gemini 2.5–3.7, GLM,
Kimi). The Auto-review classifier uses Gemini 3.5 Flash Lite with Claude 4.5 Haiku as fallback.

## Notes

- "Max context" above the default window bills at the same rate for most Claude models; GPT and
  Grok long context costs more.
- Regional or US-only endpoints cost 10% more for some Claude models.
- Hobby users see a smaller set of models; paid plans unlock all.

Sources: https://cursor.com/docs/models-and-pricing.md ; https://cursor.com/docs.md ;
https://cursor.com/docs/models/grok-4-7.md ; https://cursor.com/help/models-and-usage/grok-4-7.md ;
https://cursor.com/docs/models/cursor-composer-2-5.md ; https://cursor.com/docs/cursor-router.md ;
https://cursor.com/help/models-and-usage/available-models.md ; https://cursor.com/docs/agent/security/run-modes.md ;
https://x.ai/news/grok-4-7 ; https://cursor.com/blog/grok-4-6
