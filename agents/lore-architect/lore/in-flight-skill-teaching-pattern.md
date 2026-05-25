# In-flight skill teaching — the actual mechanism

When users improve a Lore Agent's skill in-session, the mechanism has two distinct modes worth naming:

1. **Automatic capture via reflection** — user works with the agent, the agent absorbs improved patterns naturally; reflection at session end picks them up. No explicit user action.
2. **Explicit guidance** — user directs the agent in-session: *"update your procedure for X to also do Y"* or *"from now on, always check Z before doing W."* The agent acknowledges and the change gets captured at finalize.

Both modes are part of the same loop. The framing that landed best in onboarding prose: **"Reflection picks up improvements automatically; explicit guidance ('update your procedure for X to also do Y') works too."**

Why this matters as a distinct framing:

- It removes the perceived friction of "I have to formally edit a skill file in some other repo." Users see they can just *say it* in the working session and the framework does the rest.
- The phrasing of the explicit-guidance example matters: a concrete imperative form ("update your procedure for X to also do Y") makes the behavior immediately imaginable. Abstract ("teach the agent new things") doesn't land.
- The "no detour into a separate maintenance repo, no context-switch into 'skill authoring mode'" line names what the user is *not* doing — which is what makes the easy-and-frictionless framing feel concrete.

This is the mechanism behind the **"skill set growth made easy and frictionless"** headline beat. Pair them when explaining: the headline names the property; this pattern names the mechanism. See `positive-feedback-loop-framing.md` for the broader loop and `knowledge-vs-skills-distinction.md` for why skills get singled out.

**Note for future framework work:** the explicit-guidance flow is currently informal — the user just says it, the model interprets, reflection picks up the result. If usage shows reliability gaps (the model forgets/ignores explicit guidance between turns), there's room for a more formal `/lr:teach <subject>` skill. Not needed yet — flagged in `framework-improvements-backlog.md` if it becomes one.

Surfaced in Lore Agents Intro drafting for the Activities team.
