# Knowledge vs Skills — distinct persisted assets

When describing what a Lore Agent persists, **distinguish knowledge and skills as two distinct, growing assets**. They differ in nature and in growth mechanism — collapsing them under "what the agent knows" loses the self-improvement story.

- **Knowledge** — information in markdown: lore topics, lore-context, custom reference docs the agent maintains. *What it knows.*
- **Skills** — tools plus instructions for using them to perform specific tasks (committing in git, monitoring MRs, arranging JIRA tickets, navigating a codebase). *What it can do.*

Both live in git, both grow over time, both are shared across everyone who uses the agent. But:

- Knowledge grows mostly via reflection — captured as a side effect of conversation.
- Skills grow via in-flight teaching, often *explicit* (user says "update your procedure for X to also do Y") and often *user-incentivized* (a more capable agent makes the user faster). See `in-flight-skill-teaching-pattern.md`.

Why this matters for explanation: "the agent learns from each session" reads as a vague claim until the listener understands which axis is growing. Splitting knowledge from skills lets each axis carry its own narrative — knowledge accumulates passively from conversations; skills evolve actively because users are motivated to refine them in-session.

**Terminology caveat (per `terminology-domain-collision-trap.md`):** "Skill" is itself overloaded — LRF plugin skills (`/lr:*` slash commands) vs an agent's skills (tools + instructions for tasks). Same artifact-kind in some cases but distinct framing. Be explicit in onboarding prose.

Surfaced in Lore Agents Intro drafting — the user explicitly clarified the distinction when an early draft used "knowledge" and "skills" as a hendiadys. The fix produced cleaner prose and a sharper sales pitch.
