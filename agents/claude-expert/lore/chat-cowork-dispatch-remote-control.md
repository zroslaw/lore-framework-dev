---
lore: 1
type: topic
summary: "Correct model of chat vs Cowork (local and cloud) vs Dispatch (a Desktop feature, not an app) vs Claude Code Remote Control vs cloud sessions, with requirements and dates. Open when users mix them up."
parent: lore/claude-apps-and-surfaces.md
---

# Chat, Cowork, Dispatch, Remote Control, cloud sessions

Checked 2026-10-13. Documented unless a line says otherwise. Users often mix these up; this is the
short, correct model.

- **Chat**: question and answer. It can call remote connectors and use skills. It can create files
  (documents, spreadsheets) in Claude's sandbox for download, but it cannot change files on the
  user's computer. In the desktop app, chat can also use local desktop extensions (`.mcpb`).
- **Cowork**: an agent session, like a Claude Code session but for general knowledge work. It works
  on a goal in many steps with a folder or project, connectors, plugins, plugin agents, and hooks.
  It runs locally in Claude Desktop, or in the cloud from web or mobile (since 2026-07-07, Max
  first). Inference: a cloud Cowork session cannot reach local files. The rollout of "Cowork in
  every conversation" to Pro and Max on web, desktop, and mobile started 2026-09-16; chats,
  projects, connectors, and skills carry over.
- **Dispatch**: **not a separate app.** It is a feature inside Claude Desktop (Cowork): one
  long-running manager-agent conversation that splits a goal into child tasks. It routes coding
  work to Claude Code sessions (against a set-up workspace) and knowledge work to Cowork sessions
  (in a project). Child tasks do not spawn children. From the mobile app, a user starts Dispatch
  tasks that run on the desktop; results show on both devices.
  - Requirements: Pro or Max, the latest Claude Desktop on macOS or Windows, open, with the
    computer awake and online.
  - A permission prompt that gets no reply in 10 minutes is denied, and the task continues without
    that action.
  - Launched 2026-03-17 for Pro and Max.
- **Claude Code Remote Control**: the phone (Code tab) steers one existing local Claude Code
  session turn by turn. The machine must be on.
- **Claude Code cloud sessions**: run on Anthropic's infrastructure (Code tab or claude.ai/code)
  and continue with the laptop closed. They need a claude.ai account (not a Console API key or
  Bedrock) and share Claude Code rate limits.

**Remote Control vs Dispatch:** with Remote Control you drive one session yourself; with Dispatch
you delegate a goal to a manager agent and check the results later.

How these look from the phone: [Claude mobile app](claude-mobile-app.md).

Sources: https://claude.com/docs/cowork/guide/dispatch ; https://code.claude.com/docs/en/mobile ;
https://support.claude.com/en/articles/12138966-release-notes
