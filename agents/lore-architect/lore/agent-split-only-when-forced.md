# Agent split: one until forced, along the axis the pressure reveals

A heuristic for deciding whether a scope of knowledge/work is one agent or several, surfaced in the lr-dev context-agent design (2026-06-01).

## Rule

Start with **one agent** for a coherent scope. **Split only when a concrete pressure forces it** — most often the `lore-context.md` ≤50K-token budget, or a genuine role/identity divergence — and split **along the axis the pressure actually reveals**, not along a guessed axis decided up front.

## Why

Distinctions that look like they want separate agents are often *filing categories, not identities*. In lr-dev, "product" vs "technical" felt like two agents but is really two drawers of one coherent subject — a senior engineer holds both. They belong as `product/` ÷ `technical/` category dirs inside one agent's `lore/`, interlinked, not as two agents.

Promoting a filing distinction to an agent boundary has real costs:
- **Fragments the knowledge graph** — cross-references and the no-duplication discipline weaken across agent boundaries; one home per fact is harder to maintain when the homes are different agents.
- **Forces runtime re-joining** — work that needs both halves must `/lr:attach` or `/lr:consult` to reassemble what could have been co-located in one agent's lore.

## On the ≤50K budget specifically

It's a *router-not-payload* problem: `lore-context.md` is a thin index into deep `lore/` topics loaded on demand, so one agent ≠ one giant context — the agent can custody far more knowledge than its context budget, because the budget governs the index, not the corpus. Overflow of the *index* is the signal to split — and only at that point do you actually know which axis is big (maybe product/technical, maybe by subsystem, maybe something unguessed). Splitting earlier guesses the axis blind.

## Relationship to other principles

Generalizes `framework-scope-vs-agent-scope.md` ("isolate the universal core first, push specifics out only as needed") to the question of how finely to slice agents: don't pre-fragment; let pressure reveal the seam. The same "don't build the boundary until forced" instinct that keeps the framework thin keeps the agent roster from over-splitting.

## See Also

- `framework-scope-vs-agent-scope.md` — the broader "isolate the core, push specifics out only as needed" rule this extends to agent granularity.
- `lr-dev-direction.md` — the context-agent design where one-agent-per-repo (product/technical as filing categories) was decided.
- `framework-defined-role-pattern.md` — the recurring role that a context agent instantiates; this topic answers "how many of them per repo" (one).
- `team-shared-knowledge-principle.md` — co-locating a repo's knowledge in one agent keeps it a coherent shared asset rather than scattering it.
