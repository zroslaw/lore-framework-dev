---
lore: 1
type: topic
summary: "Defines the small first rollout — GitHub, plugin-directory presence, a safe demo, Agoda channels, LinkedIn — and the first article's structure."
parent: lore-context.md
---

# Initial Rollout

The first campaign stays deliberately small and ordered:

1. Use the GitHub destination as the campaign anchor. The README leads with “Named AI specialists that learn and grow with you” and the pain of repeatedly maintaining context and instructions. Keep the plugin descriptions, marketplace copy, Quick Start, and first screen aligned with that message; then make curated knowledge, collaboration, and how to try Lore Agents immediately clear.
2. Prepare one short, public-safe demonstration with a non-Agoda agent or synthetic example.
3. Publish a personal internal message in Agoda developer-AI channels. The maintainer already uses an elaborate set of lore agents in daily work, making this the most credible source of early users and practical feedback.
4. Adapt the same story into one post from the maintainer's personal LinkedIn profile.
5. Learn from questions and reactions before expanding into the larger [channel strategy](channel-strategy.md).

This ordering still holds for the *content* steps, but it is no longer the whole rollout. Measured
evidence says the highest-leverage moves are not content at all: **presence in the coding-agent
plugin directories with a one-command install**, and **integrations that put Lore Agents inside
frameworks developers already use**. We ship as a Claude Code plugin and support Codex and Cursor,
and we are not yet using that as a discovery asset. Treat directory presence as a rollout step in
its own right, runnable in parallel with the content steps rather than after them, and see
[growth evidence](growth-evidence.md) for why it outranks anything published.

## The first public article

The article opens with the pain and a concrete example. The approach is the payoff, not the
entrance. Agreed structure:

1. A real moment where the old way broke down.
2. What was done instead — named specialists with domains.
3. The small concrete example.
4. Why it works — how they learn, why curation matters, why roles bound it.
5. The implementation and install.

The approach still gets published in full; it simply arrives fourth. One draft covering origins,
usage example, internals, source-as-lore, workspaces, domains, and activities is too much for one
piece and must be split along these lines.

**Publishing the idea or approach first, externally, was considered and rejected.** Publishing
reserves nothing and the category is crowded, so a concept-only post invites "how is this different
from X". This audience rewards "I built this, here is what happened" and is cold on agent
philosophy. And leading with the concept discards the rare asset: the maintainer runs a team of
agents daily and the thing is already built and open source. The maintainer's own evidence points
the same way — explaining the approach internally at Agoda over a long period produced little
enthusiasm, so explanation has been tested and underperformed. Both studied competitors also led
with pain, never architecture.

**Internal Agoda framing is the exception to leading with proof:** concept-first works there, because credibility is pre-established and proof is not needed to be heard. Keep the short awareness note for PMs and the concrete version for engineers.

The first Agoda message is personal and concrete: AI agents kept losing useful knowledge between sessions; named specialists now curate durable expertise and consult one another in daily work; the framework is open source; and a small number of interested developers are invited to try it.

Periodic internal updates are useful about every three or four weeks, but only when there is genuine value: a meaningful feature, a short demonstration, a new use case, a lesson from daily use, or a result from another developer. Each update answers what changed, why it matters, and how to try it.

## Agoda safety boundary

- Do not expose internal code, architecture, systems, people, data, screenshots, or agent lore.
- Use public-safe or synthetic examples in demonstrations.
- Present Lore Agents as the maintainer's open-source project unless stronger Agoda association is explicitly approved.
- Check applicable Agoda open-source, confidentiality, and internal-promotion policies before publication.

A website, newsletter, Product Hunt launch, large video program, and broad multi-platform cadence are later steps. GitHub is the initial destination.
