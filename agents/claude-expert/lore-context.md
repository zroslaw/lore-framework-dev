---
lore: 1
type: context
summary: "Root working knowledge for claude-expert: how to check Claude facts, the product family map, the surface model, and routes to apps, extensions, memory, plans and models, and Lore compatibility."
---

# Lore Context

Working knowledge for **claude-expert**: what Anthropic's Claude products do, where they run, and
which plan they need. This file holds what I use in nearly every session. Detail lives in the
areas linked below. Product facts here were checked on 2026-10-13 unless a line says otherwise.

## How I check facts

- Product facts change monthly. Recheck a saved fact at a primary source before relying on it, or
  say that I did not.
- Primary sources, in order of use:
  1. https://claude.com/docs (index: https://claude.com/docs/llms.txt) — apps, Cowork, extensions,
     admin.
  2. https://code.claude.com/docs — Claude Code.
  3. https://platform.claude.com/docs — models, API, per-token prices.
  4. https://support.claude.com — help articles and the release notes
     (https://support.claude.com/en/articles/12138966-release-notes), which date when each feature
     reached each surface.
  5. https://claude.com/pricing — plans.
- Help-center articles of different ages can disagree (example: connectors on mobile). Prefer the
  newer one and record the conflict.
- Third-party blogs often carry stale model names and prices. Use them only to cross-check.
- Many features roll out by plan (Max first, then Pro) and by surface. Record the plan, the
  surface, and the date.
- Every saved fact gets a check date, a source URL, and a label: **documented** (Anthropic docs or
  help center), **third-party report**, or **inference** (mine, untested).

## Product family

From the claude.com docs index and the pricing page:

- **Claude apps** — web (claude.ai), desktop (macOS, Windows), mobile (iOS, Android). Artifacts,
  Projects, memory, Claude Design, Slides, Docs, Dashboards (beta), Motion (beta).
- **Cowork** — agentic workspace with projects, plugins, Dispatch, and scheduled tasks; runs
  locally in Claude Desktop or in the cloud.
- **Claude Code** — terminal, IDE extensions, the desktop Code tab, cloud sessions (web and
  mobile), Remote Control. Docs at code.claude.com/docs.
- **Extension platform** — connectors, skills, plugins, MCP Apps, desktop extensions (MCPB), and
  the directory publishing portal.
- **Claude Tag** — Claude in Slack channels, with admin-governed access, spend limits, and
  routines.
- **Claude for Microsoft 365** — Excel, PowerPoint, Word, and Outlook add-ins.
- **Claude Science** — a desktop workbench for scientific research.
- **Claude in Chrome** — a browser agent; also a built-in browser in Claude Desktop on third-party
  providers.
- **Claude Desktop on 3P** — Desktop on Bedrock, Vertex, Foundry, gateways, or the Claude API,
  with managed configuration.
- **Claude for Government**, **Claude Security** (beta, Enterprise), **Financial services
  plugins** for Cowork.
- **Developer platform** — Claude API, Agent SDK, Managed Agents, Console (platform.claude.com).

Claude Tag, Microsoft 365, Science, Chrome, Desktop on 3P, Government, Security, and the API and
Agent SDK have no Lore beyond this list yet.

## The surface model

The most common confusion. Where a session runs decides what it can reach:

- **Chat** (web, desktop, mobile) runs in Anthropic's cloud. It calls remote connectors, runs
  skills in a code sandbox, and creates files for download, but it cannot change files on the
  user's computer. Desktop chat can also use local `.mcpb` extensions.
- **Cowork** is an agent session for knowledge work: local in Claude Desktop (local files, local
  MCP, plugin agents and hooks) or in the cloud.
- **Dispatch** is a feature inside Claude Desktop, not an app: a manager agent that hands a goal to
  Cowork and Claude Code sessions on the desktop. Users start it from the desktop or the phone.
- **Remote Control** steers one existing local Claude Code session from the phone. **Cloud
  sessions** are full Claude Code sessions on Anthropic's servers.
- Installs made in **Customize** (web or desktop) follow the account to every surface, including
  Claude Code as synced plugins. Installs made from the Claude Code CLI stay on that machine.

## Areas

- [Claude apps and surfaces](lore/claude-apps-and-surfaces.md) — chat, Cowork, Dispatch, Claude
  Code remote and cloud modes, and the mobile app.
- [Extension platform](lore/extension-platform.md) — connectors, skills, plugins, directory
  publishing, and org controls.
- [Memory and personalization](lore/memory-and-personalization.md) — memory topics, search past
  chats, instructions, and projects.
- [Plans and models](lore/plans-and-models.md) — plan tiers and prices, plan-gated features, and
  the model lineup.

Root-level topic: [Lore compatibility on Claude surfaces](lore/lore-compatibility-on-claude-surfaces.md).
In short (inference, untested): the `lr` plugin needs local `python3`, `git`, and the workspace
repos, so it runs only where a session has local file and git access — Claude Code today, possibly
a local Cowork session — and never in chat or on mobile chat.

## Boundaries

This agent lives in a public repository: Lore holds public product facts only, never business
plans, commercial strategy, unpublished numbers, credentials, or personal data.
