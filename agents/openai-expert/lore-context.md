---
lore: 1
type: context
summary: "Root working knowledge for openai-expert: how to check OpenAI facts, the product family map, the surface model (Chat, Work, Codex, dots), and routes to apps, extensions, memory, plans and models, and Lore compatibility."
---

# Lore Context

Working knowledge for **openai-expert**: what OpenAI's products do, where they run, and which plan
they need. This file holds what I use in nearly every session. Detail lives in the areas linked
below. Product facts here were checked on 2026-10-14 unless a line says otherwise.

## How I check facts

- Product facts change weekly. Recheck a saved fact at a primary source before relying on it, or
  say that I did not.
- Primary sources, in order of use:
  1. https://learn.chatgpt.com/docs — the ChatGPT and Codex product docs (index:
     https://learn.chatgpt.com/llms.txt; full export: https://learn.chatgpt.com/docs/llms-full.txt).
     The weekly digest https://learn.chatgpt.com/docs/whats-new dates each change.
  2. https://developers.openai.com — plugins and MCP (`/plugins/llms.txt`), API (`/api/llms.txt`),
     Codex. Every page has a Markdown twin: append `.md` to the URL.
  3. https://github.com/openai/codex — CLI releases (`gh api repos/openai/codex/releases`).
  4. https://help.openai.com — help articles and release notes. **Automated fetches get HTTP 403**
     (checked 2026-10-14). Read it in a browser, or use search-result snippets and label them so.
  5. https://chatgpt.com/pricing and https://openai.com/chatgpt/pricing — also HTTP 403 for
     fetches. The plan table at https://learn.chatgpt.com/docs/pricing is readable.
- Many terms changed in 2026. "Connectors" became "apps", and apps now ship inside **plugins**.
  "Developer mode" became **Add custom MCP server** on the Plugins page. The standalone Codex app
  merged into the ChatGPT desktop app. Old blog posts use the old names.
- Third-party pages often carry old plan names and prices. Use them only to cross-check.
- Every saved fact gets a check date, a source URL, and a label: **documented** (OpenAI docs or
  help center), **third-party report**, or **inference** (mine, untested).
- Refresh order: the What's new digest, then the llms-full exports (split them into pages with
  `workdir/split-llms-full.py` and grep), then search snippets only for blocked pages. Detail and
  traps (plan matrix, changelog, stale snippets): [research method](lore/research-method-for-openai-docs.md).
- Some facts are still unsettled (custom MCP plan gating, MCP on mobile and in Codex Cloud, `lr`
  in desktop Codex, Codex multi-agent v2 wait controls, Codex subagent sibling discovery). Check [open verification items](lore/open-verification-items.md) before
  relying on one.

## Product family

From the learn.chatgpt.com index and the DevDay 2026 digest (2026-09-29):

- **ChatGPT apps** — web, desktop (macOS, Windows, Linux preview), mobile (iOS, Android). Three
  modes: **Chat**, **ChatGPT Work** (the agent; replaced agent mode), and **Codex**.
- **Dots** — an always-on personal agent with its own cloud computer (rolling out from
  2026-09-29; Pro, Business Premium, Enterprise).
- **Codex** — Codex in the desktop app, Codex CLI, IDE extension, Codex Cloud, Codex on mobile,
  GitHub/GitLab/Slack/Linear integrations, Codex SDK, app server, Codex Security.
- **Extension platform** — plugins (skills + MCP servers + optional UI + hooks), one universal
  directory for ChatGPT and Codex; custom MCP servers; custom GPTs (retiring 2026-12-11).
- **Other ChatGPT features** — Projects, memory, Space and Pages, Sites (hosted web apps),
  scheduled tasks, browser and Computer Use, ChatGPT Voice, ChatGPT for Excel, @ChatGPT in Slack
  and Teams.
- **Developer platform** — Responses API, Agents API (managed Codex harness), Agents SDK,
  ChatKit, Workspace Agents API, Sign in with ChatGPT.

## The surface model

The most common confusion. Where a session runs decides what it can reach:

- **Chat** (web, desktop, mobile) runs in OpenAI's cloud. It uses installed plugins and their
  remote MCP tools. It cannot touch the user's computer.
- **ChatGPT Work** runs in a managed **cloud** container on web and mobile. In the desktop app it
  can also run **locally** (files, apps, browser). With "Local computer access with Work Cloud",
  the cloud coordinates the task and an online computer runs the local steps.
- **Codex** runs **local** (desktop app, CLI, IDE: local files, local MCP, hooks) or in **Codex
  Cloud** (a published environment; work continues while the computer sleeps).
- **The phone** is a client: it uses plugins in Chat and Work, starts Codex Cloud tasks, and
  steers a connected Mac or Windows host through **Codex on mobile** (remote connections).
- Claude equivalents (inference): ChatGPT Work ≈ Cowork; Codex on mobile ≈ Remote Control; Codex
  Cloud ≈ Claude Code cloud sessions; dots go beyond Dispatch (own cloud computer, Slack and Teams).

## Areas

- [OpenAI apps and surfaces](lore/openai-apps-and-surfaces.md) — Chat, Work, Codex, dots, the
  desktop and mobile apps, browser and Computer Use, Codex session logs and resume.
- [Extension platform](lore/extension-platform.md) — plugins, apps (connectors), skills, remote
  MCP per surface, Codex configuration and multi-agent v2 subagents, custom GPTs, admin controls.
- [Memory and personalization](lore/memory-and-personalization.md) — ChatGPT memory, projects,
  custom instructions, Codex memories, Computer History.
- [Plans and models](lore/plans-and-models.md) — plan prices, Codex usage, plan-gated features,
  model lineup and API IDs.

Root-level topics:

- [Lore compatibility on OpenAI surfaces](lore/lore-compatibility-on-openai-surfaces.md). In short
  (inference, untested): `lr` runs where a Codex host has local `python3`, `git`, and the repos —
  Codex CLI (a supported Lore engine) and probably Codex in the desktop app. It cannot run in
  ChatGPT Chat. A remote MCP server is the only Lore component that could reach ChatGPT mobile chat.
- [Developer platform](lore/developer-platform.md) — API, Agents API and SDK, Secure MCP Tunnel,
  Sign in with ChatGPT (pointers only).
- [Notes for agent-framework designers](lore/notes-for-agent-framework-designers.md) — OpenAI
  features with no direct Claude equivalent.
- [Research method for OpenAI docs](lore/research-method-for-openai-docs.md) — blocked sites,
  exports, the split helper, how to weigh snippets.
- [Open verification items](lore/open-verification-items.md) — unsettled facts and how to settle
  each one.

## Boundaries

This agent lives in a public repository: Lore holds public product facts only, never business
plans, commercial strategy, unpublished numbers, credentials, or personal data. Claude facts
belong to claude-expert, Cursor facts to cursor-expert, and Lore framework design to
lore-architect.
