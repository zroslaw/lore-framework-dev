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

**Authoring approach (v2):** fan `/lr:consult` calls out in parallel to the agents that actually did the work — the host (lore-architect) doesn't have the operational detail; the working agents do. See `use-cases-via-parallel-consult-pattern.md` for the full procedure (mapping, parallel dispatch, brief shape, weaving returns, caveats).

**Meta closer subsection.** End the use-cases list with a final subsection titled along the lines of *"And — meta — this very document — `<host>` + `<N>` agents"*. Two short paragraphs:

1. **Naming the agents.** State that the doc was co-authored with the host agent and list the consultants that fed each section by name. Reference back to specific lore topics that drove specific sections (e.g., "§1's narrative came from `onboarding-doc-narrative-pattern.md`").
2. **Naming the loop.** Close with the self-referential payoff: the agents that did the work are the ones writing the doc about the work, and the doc itself becomes a referenced session in their lore next time someone boots them.

Why it works: the reader has just walked through N use cases; the (N+1)th is the doc they're holding — self-illustrating proof. Closes the positive-feedback-loop framing from §1: §1 *asserts* the loop; the meta subsection *demonstrates* it. Skip for strict reference manuals — keep it for narrative/showcase docs.

**Placement differs on a landing page.** The above meta-closer-at-the-end placement holds for a long-form narrative doc (the Activities-team-intro shape this pattern documents), where "Getting started" instructions aren't competing for the same fold. Applying the same self-referential idea (the framework's own maintainer agent living in its own agent repo) to a **landing-page-length README** is a different placement problem: putting it between the use-cases section and the primary "Getting started" CTA competes with the reader's momentum right at the moment they're deciding whether to try the thing — flagged by newcomer-lens review as a real regression. The fix: a compact section placed *after* "Getting started" (e.g. titled `## Go deeper — meet the maintainer agent`), not before it. **Rule of thumb:** in a short landing-page doc, primacy goes to the single strongest CTA; treat the meta/self-referential example as a secondary "go deeper / here's proof" beat placed after that CTA, not as part of the pitch preceding it. See `paste-link-installer-doc-genre.md` for the sibling doc-genre finding from the same session.

## Section 3 — The Anatomy

Demystification, not specification. Lead with "A Lore Agent is, mechanically, just a directory of plain markdown files…" Same blockquote-headline pattern as §1 — visual rhythm carries across. "Deliberately boring" works as a tone marker.

A short `tree`-style code block between the lead-in and the bullet list helps enormously — readers grasp the structure visually before parsing prose. Keep it ≤20 lines, abbreviate long lists with `…`, use real example agent names from the target repo (not generic placeholders). Show one agent expanded, one or two siblings collapsed to communicate "many agents per repo." Include `sessions/YYYY/MM/` even though it's not in the four-piece list — it's visible on disk and readers will ask.

Three blockquote beats, in this order:

1. **"A role, a context, a body of lore, and a workdir."** — the four pieces of an agent. One bullet per piece (`role.md`, `lore-context.md`, `lore/`, `workdir/`), each ≤2 sentences: what it is, when it's loaded, what it's for. Mention the ≤50K-token budget on `lore-context.md` as a concrete constraint.
2. **"Boot → work → finalize."** — the session lifecycle. Three sub-bullets (Boot / Work / Finalize), with Finalize expanded to the v9 four phases (Reflect → Merge → Summarize → Commit+push) as a numbered list. This is where the doc earns its keep — readers see how growth actually happens.
3. **"Plain markdown, in Git, by design."** — the closing framing. Why the boring choice matters: reviewable, portable, durable, team-trustable. Pre-empts "why not a database / vector store / proprietary format" without arguing the point head-on.

What to skip in §3:
- Reflection/merge internals (how reflection extracts, how merge integrates) — the four-phase enumeration is enough for onboarding.
- File-format details beyond "plain markdown" — `lore-context.md` token budget is the only number worth surfacing.
- Cross-agent mechanisms (`/lr:recall`, `/lr:consult`, `/lr:attach`) — these belong in §4 Features and the use-cases section, not Anatomy. Mentioning them in §3 dilutes the focus on a single agent's structure.

## Section 4 — Features

Full command reference grouped by purpose:
- Day-to-day (boot, finalize, list-agents, list-repos, workspace-sync)
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

Source session: Activities team's intro doc, ~3 days of iteration with the user. The user's revisions converged on this structure after several reorderings; preserved here so the next onboarding doc starts closer to the right shape. v2 (May 2026) added §3 Anatomy and the §2 meta-closer/parallel-consult patterns from a follow-up authoring session.

## See also

- `use-cases-via-parallel-consult-pattern.md` — how to populate §2 by fanning consults to the working agents.
- `sonnet-subagent-review-pattern.md` — pre-publication review step for high-stakes onboarding drafts.
- `framework-as-engine-not-kb.md` — the "boring by design" framing §3 pulls from.
- `paste-link-installer-doc-genre.md` — the sibling AI-agent-facing genre (vs. this doc's human-facing narrative genre).
- `onboarding-funnel-team-join-path.md` — the team-join-path bug class (the landing prose must offer a joining-a-team route, not railroad fresh-start).
- `ai-installer-review-lens.md` — the review lens purpose-built for the installer genre, complementing the newcomer-lens review this pattern already relies on.
