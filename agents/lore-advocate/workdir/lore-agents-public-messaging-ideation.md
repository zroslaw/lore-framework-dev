# Lore Agents Public Messaging Ideation

A working bank of positioning, framing, and narrative directions for communicating Lore Agents.
Use it as source material for public relations, articles, launches, talks, demonstrations, social
posts, marketplace copy, documentation, and future README work.

These directions emerged during the August 2026 README positioning session. Version G was selected
for the framework README, but Versions A–F explore ideas that can be developed independently in
other materials. They are working drafts, not approved product claims or channel-ready copy.

## Version A — Expanded, team-oriented

### AI is powerful, but delegation is still hard

We can all see how powerful AI is and how much it can do. But getting useful results often requires
so much context and such precise guidance that delegation becomes a task of its own. Repeating the
background, managing what the agent needs to know, and explaining exactly how to proceed can be so
tedious that doing the work yourself still feels easier.

### Build an AI team that learns and grows with you

With Lore Agents, you create named specialists for the areas where continuity matters—a service
maintainer, research partner, personal advisor, or any other role you return to over time. Each
specialist has clear responsibilities and its own knowledge base, so a new session begins with an
established role and useful context instead of a generic assistant starting over.

At the end of a session, the specialist reviews what happened and curates what is worth keeping. It
can preserve your corrections, decisions and their rationale, domain knowledge, recurring
procedures, and lessons from mistakes. Over time, those deliberate updates become practical
expertise the specialist can apply in future work.

### Work with agents like teammates

Each agent has its own identity, expertise, and ability to grow. Give them resources and delegate
work—just like with human teammates. **Work with them, do things together, and guide them when
needed. Help them grow, and they will soon pay you back by becoming more capable and self-sufficient
with every session.**

## Version B — Concise, product-oriented

> Named AI specialists that learn and grow with you.

AI agents are useful, but every new session tends to begin with the same work: explain the
background, repeat your preferences, recover past decisions, and warn about the same gotchas.
Eventually, doing the task yourself can feel easier than delegating it.

Lore Agents turns that repeated context into a durable team. Each specialist has a role and a
Git-backed knowledge base. As you work together, the specialist deliberately curates decisions,
feedback, domain knowledge, and operational wisdom—then brings that expertise into future sessions
and shares it with other specialists.

**Open source · Git-backed Markdown · Claude Code · Codex · Cursor**

## Version C — Concept first, implementation second

### A different way to work with AI

AI agents are capable, but delegating work to them still creates work for you. You repeatedly
explain the background, recover useful details, restate preferences, and write instructions for
future sessions. The more context an agent needs, the more time you spend managing the agent
instead of benefiting from its help.

Lore Agents offers a different way to work with AI: build a team of named specialists and make
managing their context part of their job. Give each specialist a clear identity, role, and the
resources it needs. Then work alongside it, delegate real tasks, and guide it when necessary. The
specialist takes on the ongoing work of maintaining useful knowledge for its area, so you spend
less time preparing the agent to help you.

As you continue working together, that effort compounds. Specialists retain important decisions,
corrections, lessons, and domain knowledge; become more consistent and capable across sessions; and
can share their expertise with other specialists. Instead of starting over, you develop an AI team
that learns and grows with you.

### How the framework makes this practical

Each specialist has a defined role and its own knowledge base. At the end of a session, a guided
reflection identifies what was worth learning, and a merge process integrates the useful parts
into the specialist's Lore. When the specialist is booted again, it loads its identity, working
context, and a map of its accumulated expertise.

Lore Agents also gives specialists ways to recall their own knowledge, consult one another, and
work together in the same session. Roles, Lore, and session summaries are stored as plain Markdown
in Git, making them readable, reviewable, versioned, portable across supported coding agents, and
shareable with a team.

## Version D — Agents that manage their own context

> Lore Agents — agents that learn and grow with you.

One of the biggest burdens of working with AI is managing context. To get good results, you need to
provide enough background, give precise guidance, and carry important knowledge from one session
to the next. Agents may do the task itself well, but improving them remains manual: you update
their instructions, preserve useful decisions, repeat corrections, and teach them the same lessons
again. That work is tedious, and it makes delegation harder than it should be.

What if context management and continuous improvement became part of the agent's own job?

That is the idea behind Lore Agents. You create named specialists and give each one a clear role.
Each specialist takes responsibility for maintaining the knowledge it needs to perform that role.
This evolving body of knowledge is called **Lore**.

As you work together, the specialist uses its role and experience to identify what is worth
keeping—decisions, corrections, domain knowledge, procedures, and lessons from mistakes. When you
finalize a session, the agent organizes that knowledge and updates its Lore. The next time it is
booted, it starts with the expertise accumulated through your previous work together.

You still provide direction, judgment, and feedback. Lore Agents delegates the tedious work of
organizing, maintaining, and applying context to the specialists themselves. Over time, they
become more knowledgeable, consistent, and capable: agents that truly learn and grow with you.

## Version E — Concise context-delegation story

> Lore Agents — agents that learn and grow with you.

AI agents can do impressive work, but using them still requires tedious context management. You
provide background, give precise guidance, preserve important decisions between sessions, and
manually update instructions as the agent improves.

Lore Agents makes that work part of the agent's job. You create named specialists with clear roles,
and each one maintains its own evolving knowledge—its **Lore**. As you work together, the agent
curates useful decisions, corrections, domain knowledge, and lessons from experience, then carries
them into future sessions.

You provide direction and judgment; your specialists manage and apply the context they need. The
result is an AI team that becomes more knowledgeable, consistent, and capable over time.

## Version F — Technical, developer-oriented

> Your coding agents should learn the codebase—not relearn it every session.

Coding agents can write, debug, and review code, but continuity is still mostly your job. Engineers
restate architecture, conventions, current project state, past decisions, and the same hard-won
gotchas in session after session. That context ends up scattered across prompts, instruction files,
chat history, and people's heads. Maintaining it is tedious; missing it leads to wrong changes and
repeated investigations.

Lore Agents is a Git-native framework for turning that recurring context into maintained agent
expertise. You create named specialists—such as a service maintainer, platform engineer, or release
expert—and give each one a role and its own **Lore**: structured knowledge about the systems it is
responsible for.

The lifecycle is simple: **boot → work → finalize**. Boot loads the specialist's role, working
context, and a compact map of its expertise. During a task, it can recall detailed Lore or consult
other specialists. At finalization, the agent reviews the session, integrates useful decisions,
corrections, and discoveries into its Lore, and records the result in Git.

Everything is plain Markdown: inspect it, review it, diff it, revert it, and share it with the team.
The next session—or the next engineer—starts with accumulated design rationale, debugging lessons,
runbooks, and operational knowledge instead of reconstructing them from scratch.

**Open source · No hosted memory service · Claude Code · Codex · Cursor**
