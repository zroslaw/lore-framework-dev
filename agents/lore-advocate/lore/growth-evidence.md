---
lore: 1
type: topic
summary: "Measured evidence on what actually grew comparable projects, and how to measure adoption honestly."
parent: lore-context.md
---

# Growth Evidence

Measured from the first market-research sweep (2026-09-12) across claude-mem and mem0. The durable
evidence base is [market research](../workdir/market-research/README.md); its index carries a
corrections log and supersedes any single study file, so start there and do not cite a study
directly. Figures decay — trust the date stamps, not the numbers.

## What actually caused growth

**Friction reduction causes growth only on the surface where most of the market already lives.**
claude-mem's only two usage inflections were installer changes — 37x on shipping a Claude Code
plugin manifest (Oct 2025), 14x on moving to native `/plugin install` (Apr 2026) — and both stepped
up and held, the shape of a permanent change rather than a decaying spike. mem0 shipped a Claude
Code plugin in Mar 2026 with no effect on its curve, because it is a Python library for application
developers and that surface is not its market. For Lore Agents the coding-agent hosts *are* the
market, so the conclusion applies to us for an understood reason rather than by analogy.

**The highest-leverage tactic found is becoming a dependency inside other people's frameworks.**
mem0's compounding growth came from being a CrewAI extra, a package inside LlamaIndex's own
namespace, a Vercel AI SDK provider, and an AWS Agent SDK memory provider — a developer installs
the framework and gets mem0 without choosing it. A pull request into someone else's framework costs
nothing and scales down to a solo maintainer. This is the single most transferable tactic in the
sweep.

**Content grew neither project.** See [channel strategy](channel-strategy.md) for how this changed
the channel roles.

**Relaunch beats launch, but only with an existing audience.** mem0's largest single jump (9,368 →
17,141 stars in one week) came from renaming a dying RAG framework, announcing it, and hitting
GitHub Trending #1. Trending ranks stars *gained*, so an inherited audience bursting on command is
the mechanism. A project at zero stars has no base to burst from — relevant to any rename decision.

**Positional conviction correlates with winning.** mem0's core README paragraph is unchanged for 25
months across roughly 130 README commits; claude-mem rewrote its pitch five times in twelve months
and its usage is flat while mem0's still climbs. Pick a pitch and hold it.

**Neither project led with the idea.** Every hook was the user's pain in plain words with the
install command adjacent — never architecture, never a theory of agents.

**A benchmark with a number beats an essay.** mem0's arXiv paper made it the reference other
projects benchmark against.

**Founder standing is not a prerequisite.** claude-mem's author had 124 other public repos topping
out at 44 stars before this one.

## How to measure

**Use install and download curves, not GitHub stars.** Stars are a lagging attention metric, and in
one sweep they misled in three different directions:

- claude-mem shows 93.7K stars against a flat ~70–85K/month npm curve, with a memecoin attached to
  the README in Jan 2026 supplying a direct farming incentive.
- mem0 shows 65.2K stars on a repo that is a renamed prior product (embedchain), so an undetermined
  share was earned by something else — yet its real usage is roughly 47x claude-mem's.
- The watchers/stars ratio was tried as a discriminator and **withdrawn the same day**: mem0 scores
  0.38% against claude-mem's 0.32%, near-identical despite $24M of funding and 47x the usage.

Reliable sources: `api.npmjs.org/downloads/range/...`, `pypistats.org`, and
`https://github.com/<repo>/graphs/contributors-data`, which returns per-contributor commit totals
as JSON and is not subject to the 60/hour unauthenticated REST limit. Release and tag `.atom` feeds
bypass that limit too.

Watch the measurement trap that nearly produced a false positive: pypistats' 180-day window leaves
the current month partial, which reads as a step change if taken as a monthly total.

## What to avoid copying

The memecoin, GeoIP and cohort telemetry, eleven releases in a day, promotional banners shipped
into users' terminals, and mem0's open-source-to-platform migration funnel.

One undefended flank is worth remembering: mem0 removed OpenMemory, its local-first private MCP
memory server, from README, docs, and repo on 2026-03-24, choosing hosted platform over local-first.
That is exactly where Lore Agents lives, and nobody funded is defending it.
