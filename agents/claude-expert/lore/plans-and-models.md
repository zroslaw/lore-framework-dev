---
lore: 1
type: area
summary: "Claude plans and models: plan tiers and list prices, which features each plan gates, and the current model lineup with API IDs. Open before answering which plan or model; always recheck prices."
parent: lore-context.md
---

# Plans and models

Scope: the consumer and business plans (Free, Pro, Max, Team, Enterprise), what each plan
unlocks, and the model lineup with API prices.

**Never quote a price, limit, or model ID from memory.** Recheck https://claude.com/pricing for
plans and https://platform.claude.com/docs/en/about-claude/models/overview for models. Third-party
price lists were stale or wrong when I checked on 2026-10-13.

## Plan-gated features seen in the docs

Collected across areas, checked 2026-10-13 (documented):

- **Skills** in chat: Pro or higher.
- **Claude Code**: Pro or higher (also on Team).
- **Directory plugins** in Discover: Pro, Max, Team, Enterprise.
- **Search past chats**: paid plans.
- **Dispatch**: Pro or Max.
- **Cloud Cowork**: Max first (since 2026-07-07). "Cowork in every conversation" began rolling out
  to Pro and Max on 2026-09-16. Team lists Cowork.
- **Memory**: on by default for Free, Pro, and Max; off per member on Team and Enterprise until
  the member turns it on.
- **Fable access**: full on Enterprise; on Team only on Premium seats, at 50% of weekly limits.

## Children

- [Plans and pricing](plans-and-pricing.md) — each plan's price and features, and the
  Enterprise-only list.
- [Models lineup](models-lineup.md) — current models, API IDs, prices, and shared specs.
- [Claude Code OAuth usage probe](claude-code-oauth-usage.md) — inference (2026-10-16): local
  method to read account usage windows via OAuth (credential locations, endpoint, headers,
  field names). Method only; no tokens or personal numbers; machine ops stay with
  workstation-keeper.
