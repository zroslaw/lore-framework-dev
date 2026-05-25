# Onboarding-doc narrative pattern

A reusable structure for Lore Framework onboarding docs aimed at developers and managers who already use Claude Code. Tested while drafting the Activities team's `LORE_AGENTS_INTRO.md`.

## Section 1 — The Idea (sales pitch, no commands)

Four-beat narrative, each beat a **headline phrase as a blockquote** followed by a paragraph that unwraps it. The beats stack into a complete value-prop:

1. **Status quo** — "today, most people use AI agents in an ad-hoc, unstructured way." Be concrete: `CLAUDE.md`/`AGENTS.md` + a few static reference markdown files; skills equally static, updated in dedicated maintenance sessions in external repos. Conclusion: most sessions start from zero.
2. **Why the obvious fix doesn't work** — "just build a proper KB" is itself unstructured; every team invents its own layout/format/cadence; KBs go stale almost immediately after writing. Manual KBs are a tax on shippers.
3. **Lore Agents — the structured alternative** — four headline beats, each a blockquote:
   - *"A structured, hassle-free, continuously updated knowledge base, skills, and operational wisdom."* (the alternative)
   - *"A team asset, not only a personal one — knowledge and skills accumulate across people, teams, and the whole org."* (sharing/synergy)
   - *"A positive feedback loop between usage and learning."* (the dynamic — see `positive-feedback-loop-framing.md`)
   - *"Skill set growth made easy and frictionless, embedded in the work itself."* (skills specifically — see `in-flight-skill-teaching-pattern.md`)
4. **The agent is the universal working environment** — closer; positions Lore Agents inside an emerging behavior, then claims specialization is the payoff. See `agent-as-universal-working-environment.md`.

## Section 2 — Some Use Cases (so far)

Concrete examples grounded in the team's actual use. Skipped in v1 of the doc.

## Section 3 — The Anatomy

How the moving parts fit together. Skipped in v1.

## Section 4 — Features

Full command reference grouped by purpose:
- Day-to-day (boot, finalize, list-agents, list-repos, pull-domain)
- Cross-agent collaboration (recall, consult, attach, spawn-teammate)
- Finalization sub-steps (reflect, merge, summarize)
- One-time / setup (init, register-repo, unregister-repo)
- Authoring (create-repo, create-agent)
- Maintenance (check, update)

Each command gets a one-line description. The grouping is the framework's surface area; the descriptions are the entry points.

## Section 5 — Business Domain and Swarm of Agents

Cross-area work and `/lr:spawn-teammate`. Skipped in v1.

## Tone & language patterns that worked

- **Blockquote headline phrases** beat inline-bold sentences for visual scannability.
- **No "your X"** when the X is reader-state (their workspace, their session) — the doc is *for* readers, not *about* them. Use neutral phrasing ("the workspace", "the session"). Reserve "you" for actual instructions.
- **Strict terminology** — "Domain" is the LRF concept (top-level workspace dir); other senses must use "area"/"subsystem"/etc. See `terminology-domain-collision-trap.md`.
- **Acknowledge the trajectory, hide the gap** — current agents lean advisor-y, framework is built for execution. Tension is real but not worth surfacing in onboarding prose.
- **Compounding-adoption line** — "the wider the adoption, the more value" should appear once, in the team-asset paragraph. Don't restate.

## What to skip

- Implementation details of reflection/merge — readers don't need them.
- "Why we chose markdown over X" — interesting to engineers who already use the framework, irrelevant to onboarding.
- Side-quests on agent-creation (`/lr:create-agent`) — the 90% case is using existing agents.

## Foundational framings to carry into any draft

The §1 narrative depends on these — don't draft without them loaded:

- `framework-as-engine-not-kb.md` — engine, not KB.
- `agents-are-executors-first.md` — executor, not advisor.
- `knowledge-vs-skills-distinction.md` — two distinct growing assets.
- `team-shared-knowledge-principle.md` — shared, not personal.
- `positive-feedback-loop-framing.md` — the dynamic.
- `in-flight-skill-teaching-pattern.md` — the mechanism.
- `agent-as-universal-working-environment.md` — the positioning.
- `terminology-domain-collision-trap.md` — terminology hygiene.

Source session: Activities team's intro doc, ~3 days of iteration with the user. The user's revisions converged on this structure after several reorderings; preserved here so the next onboarding doc starts closer to the right shape.
