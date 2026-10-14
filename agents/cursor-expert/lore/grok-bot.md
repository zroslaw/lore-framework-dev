---
lore: 1
type: topic
summary: "Grok Bot (2026-10-14): Cursor's general knowledge-work agent product with named Bots on one persistent cloud computer per account, plugins, skills, routines, memory, apps, plans, and team controls. The nearest match to Claude Cowork."
parent: lore/cursor-apps-and-surfaces.md
---

# Grok Bot

Checked 2026-10-14. Documented unless a line says otherwise. Grok Bot docs live under
cursor.com/docs/grok-bot and cursor.com/help/grok-bot.

## What it is

- **Bots** are named AI teammates with a job and context that "compounds over time". The user
  messages a Bot; it does multi-step work across apps and websites and asks for approval when
  needed.
- **One persistent cloud computer per account** (browser, filesystem, terminal). All of a user's
  Bots share it, with its files, browser sessions, and app logins. Work continues with the laptop
  closed. Isolation between users is strict.
- Bots run in parallel, message each other, share **group chats**, and hand off tasks.
- **Skills**: saved instructions; a Bot can learn one from a demonstration ("Teach a task", up to
  10 minutes of recorded screen work). **Routines**: run a skill on a schedule or on an event
  (Slack message, GitHub notification).
- **Memory**: a Bot keeps stable preferences, role context, and summaries of prior work. Memory is
  separate per Bot.
- **Plugins** ("Connect apps"): Gmail, Google Calendar, Drive, Sheets, Notion, Slack, and others.
  Connections belong to the signed-in account and are available to every Bot. An Email plugin gives
  a Bot its own address. Grok Bot picks the model; there is no model picker.
- Safety: Auto-review checks each action, with custom rules ("Ask first" wins on conflict).
- Team Bots: one shared Bot for a team. Shared links copy a Bot's configuration, not its computer.

## Apps

Desktop app for macOS, Windows, and Linux. Mobile: the help page says iOS and Android; the docs
overview says iPhone only (conflict; the help page is more specific). Mobile cannot update or
reset the computer.

## Plans

- Included with every paid individual Cursor plan (Pro, Pro+, Ultra) and every self-serve Cursor
  Teams seat; Enterprise through the account team. Also through a linked SuperGrok, SuperGrok Plus,
  SuperGrok Heavy, or X Premium+ subscription, or a Grok Business seat.
- Usage is **weekly**, then on-demand if enabled. A link and a Cursor plan do not add together.
- In The X Subscription, Grok Bot starts at Premium ($30).

## Team controls

Grok Bot inherits the team's Cursor connector (MCP) policy: admins allow or block connectors in the
Team Marketplace; the MCP allowlist is Enterprise only. OAuth tokens stay on Cursor's connector
backend; Bots never receive them. Admins cannot push connectors to members. Enterprise adds audit
events, Action Recording via OpenTelemetry, and network and identity controls.

## Gaps

The docs do not say whether an individual can add a custom remote MCP server by URL to Grok Bot.
Inference: only connectors from the marketplace or a team marketplace appear as plugins.

## Compared with Claude (inference)

Grok Bot fills the role of Claude Cowork (general knowledge work by an agent with tools), but it
always runs on a cloud computer, never on the user's own machine.

Sources: https://cursor.com/docs/grok-bot.md ; https://cursor.com/docs/grok-bot/work.md ;
https://cursor.com/docs/grok-bot/teams.md ; https://cursor.com/docs/grok-bot/settings.md ;
https://cursor.com/help/grok-bot/plans.md ; https://cursor.com/help/grok-bot/mobile.md ;
https://cursor.com/help/grok-bot/connect-plugins.md ; https://cursor.com/pricing
