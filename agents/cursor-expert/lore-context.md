---
lore: 1
type: context
summary: "Root working knowledge for cursor-expert: how to check Cursor facts, company and plan context, the product family map, the surface model, and routes to surfaces, extensions and MCP, memory, plans and models, and Lore compatibility."
---

# Lore Context

Working knowledge for **cursor-expert**: what Cursor's products do, where they run, and which plan
they need. This file holds what I use in nearly every session. Detail lives in the areas linked
below. Product facts here were checked on 2026-10-14 unless a line says otherwise.

## How I check facts

- Cursor ships every week. Recheck a saved fact at a primary source before relying on it, or say
  that I did not.
- Primary sources, in order of use:
  1. https://cursor.com/llms.txt — the index of every docs and help page. Each page has a raw
     markdown copy: add `.md` to the URL (example: https://cursor.com/docs/mcp.md). Fetch the
     index, then all listed pages in one parallel `curl` run, and grep the local copies. This is
     fast and exact; WebFetch summarizes and can drop detail. Pages that llms.txt does not list
     also have `.md` copies (example: `docs/reference/plugins.md`); follow links inside pages.
  2. https://cursor.com/docs (reference) and https://cursor.com/help (help articles).
  3. https://cursor.com/docs/release-notes.md — all products in one timeline, up to 10 releases
     per product, with no product labels. The feed https://cursor.com/docs/release-notes/rss.xml
     names the product of each entry (Cursor IDE, Agents Window, Cursor CLI, Cloud Agents, Cursor
     web, Cursor mobile, Bugbot, Cursor SDK, Origin); map a heading to its product by feed order.
  4. https://cursor.com/pricing, https://cursor.com/changelog, and https://cursor.com/blog. These
     are HTML only (`changelog.md` returns HTML; blog posts have no `.md` copy): read them with
     WebFetch or strip the HTML. The changelog page shows only the latest five entries; the blog
     index lists posts with dates.
  5. https://x.ai/news for X Subscription terms and Grok model release dates. Cursor docs do not
     give them.
- Use forum.cursor.com and the press only to cross-check. Label what they say as a third-party
  report. The forum answers plain `curl` (`/search.json?q=...`, `/t/<id>.json`), which helps when
  WebSearch is not available. Staff posts carry `staff: true`: cite them as forum statements, not
  documentation, and check the date. An old staff post can contradict the current docs (April
  2026: "self-hosted pool requires a Team plan"; the docs now say Enterprise). Some facts have only
  a forum source (the removal of Memories); then say so.
- Cursor pages of different ages disagree (examples: SSE for cloud MCP, plan names in the docs vs
  the pricing page). Record both sides and say which is newer.
- Every saved fact gets a check date, a source URL, and a label: **documented** (cursor.com docs,
  help, blog, release notes), **third-party report**, or **inference** (mine, untested).

## Company and plan context

- Cursor is made by Anysphere, Inc. SpaceX acquired Cursor on 2026-08-14 (Cursor blog,
  "joining-spacex"); the partnership with SpaceXAI started in April 2026. Cursor's Grok 4.5, 4.6,
  and 4.7 models are "jointly trained by Cursor and SpaceXAI".
- Since 2026-10-12, two plan families exist side by side. **The X Subscription** (cursor.com/pricing:
  Free, Plus, Premium, Super, Ultra, Teams; one weekly pool shared with Grok) is for new customers.
  The **Cursor plans** in the docs (Hobby, Start, Pro, Pro+, Ultra, Teams, Enterprise; monthly
  pools) stay for existing customers. Always say which family a plan fact belongs to
  ([plans and pricing](lore/plans-and-pricing.md)).

## Product family

From the docs index and the docs home page:

- **Cursor desktop app** (macOS, Windows, Linux): the VS Code-based editor (Tab, inline edit,
  Agent with Agent, Plan, Ask, and Debug modes) and the **Agents Window**, the agent-first UI since
  Cursor 3 (2026-04-02): parallel local and cloud agents, Projects, Design Mode, canvases, and
  Remote Control.
- **Cursor CLI** (command `agent`): interactive and headless agent, ACP server, self-hosted worker.
- **Cloud Agents** (formerly Background Agents): agents on Cursor VMs or on Self-Hosted Machines.
- **Cursor web** (cursor.com/agents, /automations, /dashboard, /codebase) and **Cursor for iOS**
  (iPhone, iPad). Android has only the web app (PWA).
- **Automations** and Cursor-managed agents: **Bugbot** (PR review), Security Agents, PR Routing &
  Approval, Rollouts.
- **Grok Bot**: named cloud Bots with a persistent cloud computer for general knowledge work. The
  nearest match to Claude Cowork.
- **Origin** (early beta): Cursor's own git forge, with a CLI, an API, and an MCP server.
- **Extension platform**: the Customize page, the Cursor Marketplace, team marketplaces, plugins,
  rules, skills, subagents, commands, hooks, and MCP.
- **Developer surfaces**: Cloud Agents API, TypeScript and Python SDKs, SDK Bridge, Admin and
  Analytics APIs, ACP (JetBrains), and the Xcode MCP bridge.
- **Business**: Teams and Enterprise (SSO, SCIM, audit logs, MCP allowlist, model access control,
  Cursor Blame, OpenTelemetry export).

## The surface model

Where the agent loop runs, and where its tool calls run, decide what an agent can reach:

- **Local agents** (editor, Agents Window, CLI, JetBrains through ACP): tool calls run on the
  user's computer. They reach local files, local programs, local stdio MCP, and `~/.cursor`.
- **Cloud agents on Cursor VMs**: tool calls run in an isolated VM with cloned repos. No local
  files, no user-level hooks. Personal skills arrive only when the user syncs them.
- **Self-Hosted Machines** (My Machines, Team Pools) and **Remote Control**: the agent loop runs in
  Cursor's cloud and tool calls run on the user's machine. The machine must stay awake and online.
- **Web and iOS** are clients. They start and steer cloud agents and Remote Control sessions; they
  run no agent themselves.
- Nearest Claude equivalents (inference): Claude Code ↔ editor and CLI; Claude Code cloud sessions
  ↔ Cloud Agents; Claude Remote Control ↔ Cursor Remote Control; Dispatch ↔ a My Machines worker or
  a Project coordinator; Cowork ↔ Grok Bot.

## Who agents can message

Checked 2026-10-24. A Task subagent returns one final message to its parent. Parallel siblings do
not share a transcript. A model choice, including Composer 2.5, does not add a sibling channel.
Agent SDK peers are separate full agents. They are not a relay between those subagents. A Project
is a coordinator hub: the coordinator relays, and workers do not message each other directly.
Open [extension platform](lore/extension-platform.md) for subagents,
[Cursor apps and surfaces](lore/cursor-apps-and-surfaces.md) for SDK peers and Projects, and
[notes for agent-framework designers](lore/notes-for-agent-framework-designers.md) for the pattern.

## Areas

- [Cursor apps and surfaces](lore/cursor-apps-and-surfaces.md) — editor and Agents Window, CLI,
  cloud agents, self-hosted machines and Remote Control, mobile and web, integrations and APIs,
  Bugbot and Automations, Grok Bot.
- [Extension platform](lore/extension-platform.md) — Customize, MCP (with remote MCP per surface),
  plugins and marketplaces, skills, subagents, commands, hooks, and admin controls.
- [Memory and personalization](lore/memory-and-personalization.md) — rules, AGENTS.md, CLAUDE.md,
  and other persistent context.
- [Plans and models](lore/plans-and-models.md) — both plan families, usage pools and billing, and
  the model lineup.

Root-level topics:

- [Lore compatibility on Cursor surfaces](lore/lore-compatibility-on-cursor-surfaces.md). In short
  (inference, untested): the `lr` plugin runs where tool calls reach the local workspace — the
  editor, the CLI, and so also Remote Control and a My Machines worker. Cursor-hosted cloud agents
  are a doubtful fit, and web and iOS reach Lore only through those sessions.
- [Notes for agent-framework designers](lore/notes-for-agent-framework-designers.md) — Claude
  compatibility layers, open standards, and other Cursor mechanisms worth reusing.

## Boundaries

This agent lives in a public repository. Lore holds public product facts only: never business
plans, commercial strategy, unpublished numbers, credentials, or personal data. Lore framework
design belongs to lore-architect; I supply Cursor facts.
