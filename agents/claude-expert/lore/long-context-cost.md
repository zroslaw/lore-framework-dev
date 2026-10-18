---
lore: 1
type: topic
summary: "Long-context cost (2026-10-18): no per-token premium up to 1M on 4.6+ models except Haiku 5.5 over 100K; why big contexts still cost more per turn; 1M plan access; Claude Code controls for context size."
parent: lore/plans-and-models.md
---

# Long-context cost

Checked 2026-10-18. Sources:
https://platform.claude.com/docs/en/about-claude/pricing (§ Long context pricing, § Prompt
caching) and https://code.claude.com/docs/en/model-config (§ 1M context window). **Documented**
unless a line says otherwise.

## Per-token price by context size (API)

- **No long-context premium** on Claude 4.6 and later models (Opus 5.5, Opus 5, Sonnet 5.5,
  Fable 5.1, Opus 4.8, and others) and Claude Mythos Preview: the full 1M window is at standard
  prices. "A 900k-token request is billed at the same per-token rate as a 9k-token request."
  Caching and batch discounts apply across the full window.
- **Exception — Haiku 5.5:** a request whose prompt is over **100,000 tokens** pays 5× prices:
  $0.10 → $0.50 input, $0.50 → $2.50 output, cache read $0.01 → $0.05 per MTok (batch $0.05/$0.25 →
  $0.25/$1.25). The prompt length counts all input tokens, cache reads and writes included. Each
  request is priced on its own.
- US-only inference (`inference_geo`) adds ×1.1 on every category, including Haiku 5.5's higher
  prices.
- Fast mode pricing applies across the full context window.

## Why a big context still costs more in total

Every turn re-sends the whole context, mostly as cache reads. Opus 5.5 cache prices: 5-minute
write $5, 1-hour write $8, read $0.20 per MTok (reads are 0.05× input on Opus 5.5 and Sonnet 5.5;
0.025× on Fable 5.1; 0.1× on other models).

Worked example (inference, my arithmetic, Opus 5.5 list prices):

- About 320K tokens of context → about $0.06 per turn in cache reads alone; about $0.01 at 50K.
- A cache miss re-writes the whole context: 320K × $5/MTok ≈ $1.60 (5-minute write), ≈ $2.56
  (1-hour write).
- In Claude Code, the main-conversation cache TTL is 5 minutes with an API key, and 1 hour on a
  subscription within the plan's included usage (from the Agent SDK cost-tracking page, see
  [observability and cost](agent-observability-and-cost.md)).
- On Pro or Max there is no per-token bill, but bigger turns use more tokens, so limits are
  reached sooner (inference).

## 1M context in Claude Code

- Native 1M, no suffix: Fable 5.1, Fable 5, Sonnet 5 and later, Haiku 5.5, Opus 4.7 and later.
- Opus 4.6 and Sonnet 4.6 reach 1M only through the `[1m]` variant (`/model opus[1m]`). Plan
  access: Opus 4.6 1M is included on Max, Team, Enterprise and needs usage credits on Pro;
  Sonnet 4.6 1M needs usage credits on every subscription plan; API and pay-as-you-go have full
  access.
- Auto-compaction on native-1M models starts at about 967K tokens by default.
- Controls: `/compact`, `/clear`; `/autocompact 200k` (current model; `/autocompact auto` resets);
  `"autoCompactWindow": 200000` in settings; `claude --autocompact 500k`;
  `CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000` (plain count, wins over the others);
  `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` (treats native-1M models as 200K). Accepted range 100K–1M.

**How to apply:** when asked "does a big context cost more", answer: not per token (except Haiku
5.5 over 100K), but yes per turn, because the whole context is re-sent; the real risk is a cache
miss on a large context. Recommend compaction controls for long Claude Code sessions.
