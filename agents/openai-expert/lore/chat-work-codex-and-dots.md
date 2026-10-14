---
lore: 1
type: topic
summary: "Correct model of ChatGPT Chat vs ChatGPT Work (cloud, local, synced) vs Codex vs dots, with dates, requirements, and the Claude equivalents (Cowork, Dispatch, Remote Control, cloud sessions). Open when users mix them up."
parent: lore/openai-apps-and-surfaces.md
---

# Chat, Work, Codex, and dots

Checked 2026-10-14. Documented unless a line says otherwise.

## The three modes in ChatGPT

- **Chat**: question and answer, web search, drafts. It can use installed plugins (skills and
  remote MCP tools). It cannot touch the user's computer.
- **ChatGPT Work**: the agent mode. It plans a task, uses files, plugins, the browser, code and
  shell, and subagents, and returns a reviewable result (documents, decks, sheets, PDFs, Sites).
  Launched 2026-07-09 with GPT-5.6. Work and Codex **share one usage pool**.
  - Web and mobile: Work runs in a managed **cloud** container.
  - Desktop app: the user can also choose **Work locally** (local files, apps, browser).
  - **Local computer access with Work Cloud** (DevDay, 2026-09-29): the cloud coordinates a new
    task and an online, connected computer runs the steps that need it. The task continues on
    web, mobile, or desktop. If the computer is offline when a turn starts, the turn runs in a
    cloud container without local files. Existing tasks keep their original mode.
  - Third-party report: the older **agent mode** retired in early August 2026 and its help page
    points to ChatGPT Work.
- **Codex**: the developer view. Diffs, review, Git, shell detail, PR pane. Local, Worktree, or
  Cloud. Codex and Work overlap; Work hides technical detail.
- On desktop, Chat and Work chats appear in the ChatGPT view; Codex keeps a separate history
  (since 2026-07-13 to 17). Cloud Work chats sync across web, mobile, and desktop; local Work
  chats stay on the computer.

## Dots

- An always-on agent with its **own cloud computer and browser**, powered by GPT-6 Astra. It works
  between conversations, wakes itself, runs background agents, and asks the user for decisions.
- Reach it in the ChatGPT app (message or call), Slack, or Microsoft Teams. Same dot, same memory
  across channels.
- It can use installed plugins, start Work or Codex tasks, use a Codex Cloud environment, and use
  **one connected personal computer** (online, ChatGPT app open). Local skills need that computer.
- Create it in the mobile app, desktop app, or a desktop browser (not mobile web). Mobile setup
  arrived 2026-10-09.
- Access (rolling out): Pro 100, Pro 200, Pro 500 (18+, outside EEA, UK, Switzerland); Business
  Premium; Enterprise (off by default). Talking to a dot does not count toward usage limits; the
  tasks it starts do.

## Claude equivalents (inference)

| Claude | Nearest OpenAI feature | Main difference |
|---|---|---|
| Cowork (local and cloud) | ChatGPT Work (local and cloud) | Work also has cloud-coordinated local execution across devices |
| Dispatch | Dots, and synced Work | A dot is a persistent agent with its own cloud computer, not only a desktop manager |
| Claude Code Remote Control | Codex on mobile (remote connections) | Steers a host running the ChatGPT desktop app, not the CLI |
| Claude Code cloud sessions | Codex Cloud | Needs a published environment; repo skills only |
| Claude Code CLI | Codex CLI | Both are supported Lore engines |

Sources: https://learn.chatgpt.com/docs/use-chatgpt ;
https://learn.chatgpt.com/docs/get-started-with-work ; https://learn.chatgpt.com/docs/dots ;
https://learn.chatgpt.com/docs/whats-new/devday-2026 ; https://learn.chatgpt.com/docs/whats-new ;
third-party: https://www.usecarly.com/blog/what-is-chatgpt-agent/
