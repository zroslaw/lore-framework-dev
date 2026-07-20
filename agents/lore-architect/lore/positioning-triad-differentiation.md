# Positioning Triad — Canonical Differentiation Framing

Canonical advertising/comparison framing, established 2026-07-20 (competitive re-survey +
user-requested positioning session). Supersedes the earlier "no surveyed competitor federates
knowledge across different coding engines" claim in `multi-engine-portability-direction.md`,
which the 2026-07-20 re-survey showed to be false (see below).

## The triad

Lead all positioning/README/marketplace copy with these three, not with cross-engine support
or git-sharing alone — no surveyed competitor has *any* element of the triad, let alone all
three (see `similar-projects-landscape.md` for the per-competitor survey):

1. **Named role-based agents as the knowledge unit.** Every competitor scopes memory to a
   codebase or project. Lore-framework scopes it to a *role* — a tax-advisor, a
   lore-architect — with its own identity, role definition, and accumulated lore that travels
   across projects and engines. A categorically different design, not a feature gap a
   competitor can patch quickly.
2. **Deliberate, skill-triggered reflect/merge curation lifecycle.** The field bets on
   automatic capture (hooks, proxies, background daemons). We bet on intentional curation —
   knowledge is curated, not accumulated. Structurally defensible: auto-capture tools can't
   adopt this without abandoning their core pitch ("zero workflow changes"); their weakness is
   inherent, since automatic capture accumulates noise and nobody's daemon writes a
   feedback-discipline topic.
3. **Cross-agent collaboration mechanisms.** Attach / consult / recall / spawn-teammate — a
   team of *agents* consulting each other's knowledge. Nobody else has the concept, because
   nobody else has named agents as the unit.

Fourth, harder-to-copy supporting asset: **~150 topics of accumulated design lore proving the
system works on itself.** The framework's architect is itself a lore agent — a self-hosting
demo no competitor can fake.

## Eroded axes — do not lead with these anymore

- **Cross-engine support** — now table stakes: claude-mem (~65K stars), BYK/loreai, and
  rohitg00/agentmemory all claim multi-engine support as of 2026-07. This is *why* the old
  `multi-engine-portability-direction.md` positioning claim ("no surveyed competitor federates
  knowledge across different coding engines") no longer holds.
- **Team-shared via git** — amarlearning/lore has it today (nascent); BYK/loreai roadmaps it
  as "Folk Lore."
- **Markdown-in-git substrate** — commoditizing via Google OKF and Linux-Foundation AGENTS.md.

These still matter as supporting facts and technical enablers (the multi-engine port is what
makes the triad reachable by mixed-engine teams at all — see
`multi-engine-portability-direction.md`) — just not as the headline positioning claim anymore.

## Advertising-ready pitch line (draft)

> A team of named, role-based AI agents that deliberately curate and share knowledge — across
> sessions, across projects, and across whichever coding engine each teammate uses.

Lead with the triad; mention cross-engine and git-sharing as supporting facts, never as the
headline.

## Risk assessment

- **Convergence, not any single competitor.** BYK/loreai is one shipped "Folk Lore" release
  away from cross-engine + team-shared + heavy release momentum. The triad pitch must be
  standing before that lands.
- **Contrarian bet.** claude-mem's star count shows the market currently rewards
  zero-friction *automatic* memory. Deliberate curation is a bet that quality beats
  convenience — right for *teams* (noise compounds at team scale), but against the market's
  current gradient. Sell curation as the team-scale advantage in copy, not as extra work.
- **Name collision.** Three external projects named "Lore" (amarlearning/lore, BYK/loreai,
  getlore-ai) — see `lore-agents-product-name.md`.

## Re-survey cadence (operational lesson)

The competitive space moved materially in 18 days (2026-07-02 → 2026-07-20): claude-mem went
cross-engine at ~65K stars, three external "Lore"-named projects surfaced, Google shipped OKF,
and AGENTS.md standardized under the Linux Foundation. Operational rule (also stamped in
`similar-projects-landscape.md` § Status): **re-survey the landscape before any
positioning-sensitive ship** — README rewrite, marketplace submission, public announcement.
Watch item: BYK/loreai's planned "Folk Lore" team-sync release is the convergence event this
pitch must precede.

## Provenance

2026-07-20 session — fresh web survey + positioning dialogue, user-requested source material
for advertising copy and competitor comparisons. Full argument and draft copy:
`workdir/positioning-analysis-2026-07-20.md`. Underlying facts: `similar-projects-landscape.md`.

## See Also

- `similar-projects-landscape.md` — the competitive survey this framing rests on; per-competitor
  facts and the "what changed" delta between the 2026-07-02 and 2026-07-20 surveys.
- `multi-engine-portability-direction.md` — the direction whose earlier "no competitor federates
  across engines" positioning claim this framing supersedes; cross-engine remains a technical
  enabler, just not the headline.
- `lore-agents-product-name.md` — the "Lore" name-collision consideration for the product brand.
- `workdir/positioning-analysis-2026-07-20.md` — full argument, risk assessment, and draft
  advertising copy (workdir source material, not lore).
