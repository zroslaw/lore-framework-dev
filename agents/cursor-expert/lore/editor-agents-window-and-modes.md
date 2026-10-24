---
lore: 1
type: topic
summary: "The Cursor desktop app as of 2026-10-14: editor vs Agents Window, agent modes, Tab and inline edit, tools, checkpoints, steering, side chats, subagents, worktrees, Projects, Design Mode, canvases. Open for what the desktop agent can do."
parent: lore/cursor-apps-and-surfaces.md
---

# Editor, Agents Window, and agent modes

Checked 2026-10-14. Documented unless a line says otherwise. Current desktop version: 3.24
(release notes).

## Two interfaces in one app

- **Editor (IDE)**: the classic VS Code-based editor with VS Code extensions. Agent opens in the
  side pane (Cmd+I).
- **Agents Window**: the agent-first interface, generally available with Cursor 3 on 2026-04-02.
  Open it with Cmd+Shift+P → Open Agents Window; go back with Open IDE. Both can be open at once.
- Features only in the Agents Window: multi-workspace, the new diffs and PR view, many parallel
  cloud agents, local ↔ cloud handoff, cloud subagents (`/in-cloud`, `/autopilot`), UI-native
  worktrees, Projects, Design Mode, Remote Control, Custom Modes (also in the CLI).

## Modes and editing features

- **Agent** (default): all tools. **Plan**: asks questions, researches, writes an editable plan
  (saved in the home directory unless you save it to the workspace). **Ask**: read-only.
  **Debug**: hypotheses, log statements, runtime evidence, then a fix. Shift+Tab rotates modes.
- **Custom Modes**: any skill used as a mode (Option+Enter) stays in context on every turn.
- **Tab**: AI autocomplete with multi-line edits, jump to the next edit, and cross-file edits.
  Hobby has a monthly Tab allowance; paid plans have unlimited Tab (models-and-pricing page).
- **Inline edit** (Cmd+K): edit or ask about selected code. User rules do not apply to it.

## Agent tools and controls

- Tools: file search, web search, fetch rules, read files (images too), edit files, shell, browser
  control, image generation, ask clarifying questions, MCP tools, subagents (Task tool).
- **Checkpoints**: local snapshots before big changes; restore reverts files only.
- **Queue vs steer**: Enter queues a message; "Send now" delivers it at the next tool call.
- **`/goal`**: a long-lived objective the agent works on until done (rolling out).
- **Side chats** (`/side`, `/btw`): durable child chats that see the parent as hidden context.
- **Conversation search**: Cmd+K in the Agents Window searches past transcripts (local index).
- **Shared transcripts**: Team or Public links (Teams and Enterprise only; 50 shares per day).
- **Run Modes** decide approvals for shell, MCP, and fetch calls: Auto-review (default since 3.6,
  2026-05-29), Allowlist, Run Everything. See [MCP in Cursor](mcp-in-cursor.md).

## Subagents, worktrees, Projects

- **Subagents**: built-in Explore and Browser (a help page also names Bash); custom ones in
  `.cursor/agents/` ([skills, subagents, commands](skills-subagents-and-commands.md)). Isolated
  copies on request: a git worktree each, or a cloud VM each.
- **Worktrees**: `.cursor/worktrees.json` drives setup in the Agents Window, the IDE, and the CLI.
- **Projects** (2026-09-10): a coordinator agent that plans and delegates to many agents, runs on
  cloud agents, keeps shared context files across machines, and acts on subscriptions (Slack,
  schedules, PR activity). All paid plans; not on Hobby or Privacy Mode (Legacy). Enterprise needs
  3.21.9 or later.
- **Projects stay a hub, not a mesh** (checked 2026-10-24). **Documented**
  (https://cursor.com/docs/agent/projects.md): the coordinator plans and delegates; it does not
  write code; shared context files sync across the project's agents. **Third-party report**,
  Cursor staff on the forum, 2026-09-14
  (https://forum.cursor.com/t/let-me-talk-to-subagents-and-let-sibling-agents-talk-to-each-other/171387):
  you can open a worker and message it; the coordinator stays in the loop; sibling-to-sibling
  messages are not there; the coordinator relays cross-agent handoffs. **Documented**, week of
  2026-10-05 (https://cursor.com/docs/release-notes/cloud-agents): when you @-mention an agent to
  a Project coordinator, the coordinator can read that transcript and send messages; it can
  message its parent coordinator; the receiver can reply. Access follows the user's. This is
  still coordinator-shaped. It is not a free peer mesh between Task subagents
  ([skills, subagents, and commands](skills-subagents-and-commands.md)). Agent SDK peers are a
  different path ([integrations and public API](integrations-and-public-api.md)).

## Visual work

- **Design Mode** (Cmd+Shift+D in the Agents Window browser): click elements, draw on a frozen
  frame, or narrate by voice.
- **Canvases**: interactive React artifacts beside the chat (`/canvas`). Publish a read-only share
  link for your team (paid plans, on a team, not with Legacy Privacy Mode).
- **Computer Use** on macOS is in the desktop app (3.24 release notes mention its permissions
  window).

Sources: https://cursor.com/docs/agent/agents-window.md ; https://cursor.com/docs/agent/overview.md ;
https://cursor.com/docs/agent/projects.md ; https://cursor.com/docs/release-notes/cloud-agents ;
https://forum.cursor.com/t/let-me-talk-to-subagents-and-let-sibling-agents-talk-to-each-other/171387 ;
https://cursor.com/docs/agent/plan-mode.md ;
https://cursor.com/docs/agent/prompting.md ; https://cursor.com/docs/agent/design-mode.md ;
https://cursor.com/docs/agent/tools/canvas.md ; https://cursor.com/docs/configuration/worktrees.md ;
https://cursor.com/docs/agent/security/run-modes.md ; https://cursor.com/help/ai-features/tab.md ;
https://cursor.com/help/ai-features/shared-transcripts.md ; https://cursor.com/docs/release-notes.md
