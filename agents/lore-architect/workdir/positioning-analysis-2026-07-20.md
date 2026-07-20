# Competitive Positioning Analysis — 2026-07-20

Purpose: source material for advertising copy and competitor comparisons (user request,
2026-07-20 session). Derived from the same-day landscape re-survey in
`../lore/similar-projects-landscape.md` — read that first for the per-competitor facts;
this file carries the *argument*.

## Verdict

Still competitive, still unique — but the window is narrower than in early July 2026, and
the clock is visibly ticking. Differentiation is now something we must argue, not
something the landscape hands us by default.

## The triad — what is still uniquely ours

Nobody in the surveyed field has even *one* of these; we have all three working together:

1. **Named agents as the unit of knowledge.** Every competitor scopes memory to a codebase
   or project. We scope it to a *role* — a tax-advisor, a lore-architect — with its own
   identity, role definition, and accumulated lore that travels across projects and
   engines. A categorically different design, not a feature gap they can patch quickly.

2. **Deliberate curation lifecycle.** The field bets on automatic capture (hooks, proxies,
   background daemons). We bet on intentional reflect/merge — knowledge is *curated*, not
   accumulated. Most defensible position: auto-capture tools can't adopt it without
   abandoning their core pitch ("zero workflow changes"). Their weakness is inherent —
   automatic capture accumulates noise; nobody's daemon writes a feedback-discipline topic.

3. **Cross-agent collaboration.** Attach / consult / recall / spawn-teammate — a team of
   *agents* consulting each other's knowledge. Nobody else has the concept, because nobody
   else has agents as the unit.

Fourth asset, harder to copy than any mechanism: **~150 topics of accumulated design lore
proving the system works on itself.** The framework's architect is itself a lore agent —
a self-hosting demo no competitor can fake.

## Eroded axes — do NOT lead with these anymore

- **Cross-engine** — now table stakes: claude-mem (~65K stars), BYK/loreai, and
  rohitg00/agentmemory all claim multi-engine support (as of July 2026).
- **Team-shared via git** — amarlearning/lore has it today (nascent); loreai roadmaps it
  as "Folk Lore."
- **Markdown-in-git substrate** — commoditizing via Google OKF and Linux-Foundation
  AGENTS.md. Validates the bet and removes it as a differentiator simultaneously.

## Risk assessment

- **Convergence, not any single competitor.** BYK/loreai is one shipped "Folk Lore"
  release away from cross-engine + team-shared + heavy release momentum. The triad pitch
  must be standing before that lands.
- **Contrarian bet.** claude-mem's star count shows the market currently rewards
  zero-friction *automatic* memory. Deliberate curation is a bet that quality beats
  convenience — right for *teams* (noise compounds at team scale), but against the
  market's current gradient. Be clear-eyed about this in copy: sell curation as the
  team-scale advantage, not as extra work.
- **Name collision.** Three external projects named "Lore" (amarlearning/lore, BYK/loreai,
  getlore-ai) — bears on `lore-agents-product-name.md` and on SEO/discoverability of any
  advertising.

## Advertising-ready pitch line (draft)

> A team of named, role-based AI agents that deliberately curate and share knowledge —
> across sessions, across projects, and across whichever coding engine each teammate uses.

Lead with the triad; mention cross-engine and git-sharing as supporting facts, never as
the headline.

## Action hooks

- Rewrite README/marketplace positioning to lead with the triad before convergence lands.
- B6 (Claude community marketplace submission) urgency raised.
- Patch the stale "no competitor federates across engines" claim in
  `../lore/multi-engine-portability-direction.md`.

Provenance: 2026-07-20 session (fresh web survey + positioning dialogue). Facts:
`../lore/similar-projects-landscape.md`. Improvement item: backlog § OKF Alignment;
standing list C5.
