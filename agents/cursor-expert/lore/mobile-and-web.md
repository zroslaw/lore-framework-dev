---
lore: 1
type: topic
summary: "What a user can do with Cursor from a phone or a browser (2026-10-14): Cursor for iOS features and limits, Android PWA, cursor.com/agents, what stays web-only, MCP on mobile, Remote Control, in-app purchase, and Grok Bot mobile."
parent: lore/cursor-apps-and-surfaces.md
---

# Mobile and web

Checked 2026-10-14. Documented unless a line says otherwise.

## Cursor for iOS

- Native app for iPhone (iOS 26.0+) and iPad (iPadOS 26.0+), English only, every App Store region
  except mainland China. Third-party reports date the public beta launch to about 2026-06-29.
- Plans: any plan with Cloud Agents — Start, Pro, Pro+, Ultra, Teams, Enterprise. Free accounts
  can sign in but cannot start agents. SSO works.
- It runs on the same backend as cursor.com/agents and the Agents Window. Agents started on the
  phone carry `source: iosApp` and appear everywhere.
- What works:
  - Start cloud agents on a Cursor cloud machine, a Team Pool, or one of My Machines; any cloud
    model at its maximum context; lock the phone and come back later.
  - Follow the chat live, send follow-ups, open subagent transcripts.
  - Review and merge PRs: diffs, checks, reviewers, squash merge, auto-merge, mark ready.
  - Slash commands, skills, and automations "work the same" as on desktop, CLI, and web.
  - Design Mode on photos and screenshots (Apple Pencil on iPad); voice dictation.
  - MCP: choose which servers a run uses at launch, including the Slack MCP. Answer an MCP sign-in
    request from a "Needs Attention" card (mobile 1.9.0).
  - Push notifications, and Live Activities for up to eight agents.
  - **Remote Control**: steer a session that runs on the user's computer
    ([self-hosted machines and Remote Control](self-hosted-machines-and-remote-control.md)).
- What stays on the web or desktop: editor, terminal, file browser; environments and secrets;
  adding and managing MCP servers; source control setup; automations, rules, and skills config;
  admin, billing, usage.
- In-app purchase: monthly Pro, Pro+, or Ultra through Apple (help page). On-demand usage needs a
  card on the web.

## Android

No native Cursor app. Open cursor.com/agents in Chrome and use **Install App** (PWA). The help page
says Android is planned with no date.

## Web: cursor.com

- **cursor.com/agents**: start and manage cloud agents on any device; choose a repo, environment,
  model, or machine; add and enable personal MCP servers (MCP dropdown); attachments up to 4 MB per
  document or image and 15 MB per video. Steering a running agent ("Send now") arrived here first.
- **cursor.com/automations**, **cursor.com/dashboard** (billing, usage, integrations, team admin,
  Plugins & MCPs), **cursor.com/codebase** (Origin repos), **cursor.com/s/...** (shared
  transcripts).
- The web has no local agent. Everything it starts is a cloud agent or a self-hosted run.

## Grok Bot on mobile

Grok Bot has its own mobile app. The Grok Bot help page says iOS and Android; the Grok Bot docs
overview says "the mobile app runs on iPhone". The help page is more specific; treat Android as
likely but unconfirmed ([Grok Bot](grok-bot.md)).

## Compared with Claude (inference)

Like the Claude mobile app, the Cursor app is mainly a client. Unlike Claude, Cursor mobile has no
chat that runs skills in a sandbox: every task on the phone is a cloud agent or a Remote Control
session.

Sources: https://cursor.com/docs/cloud-agent/mobile.md ; https://cursor.com/help/ai-features/mobile-app.md ;
https://cursor.com/docs/cloud-agent.md ; https://cursor.com/help/ai-features/cloud-agents.md ;
https://cursor.com/help/account-and-billing/app-store-subscription.md ;
https://cursor.com/help/grok-bot/mobile.md ; https://cursor.com/docs/grok-bot.md ;
https://cursor.com/docs/release-notes.md ;
https://pulse2.com/cursor-launches-native-ios-app-for-building-with-ai-agents-from-anywhere/ (third-party)
