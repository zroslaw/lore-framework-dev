---
lore: 1
type: topic
summary: "Cursor CLI as of 2026-10-14: the agent command, install and auth, modes, headless print mode, cloud handoff with &, worktrees, MCP and plugin commands, ACP, and the self-hosted worker. Open for terminal or CI questions."
parent: lore/cursor-apps-and-surfaces.md
---

# Cursor CLI

Checked 2026-10-14. Documented unless a line says otherwise. Latest CLI build in the release notes:
v2026.10.08.

## Install, name, and auth

- Install: `curl https://cursor.com/install -fsS | bash` (macOS, Linux, WSL) or
  `irm 'https://cursor.com/install?win32=true' | iex` (Windows). It installs to `~/.local/bin` and
  auto-updates; `agent update` updates by hand.
- The command in the current docs is **`agent`**. The docs no longer show `cursor-agent`. The Lore
  engine profile and lore-architect notes still use `cursor-agent`. Tested 2026-10-24:
  `cursor-agent` still runs (build 2026.10.22-27dcf5f).
- Auth: `agent login` (browser; `NO_OPEN_BROWSER=1` prints the URL), or a user API key in
  `CURSOR_API_KEY` or `--api-key`. `agent status` shows the account.

## Working with the agent

- Modes: Agent (default), Plan (`/plan`, `--plan`), Ask (`/ask`), Debug (`/debug`). Shift+Tab
  rotates them. Custom Modes: pick a skill and press Option+Enter.
- Same rules system as the editor: `.cursor/rules`, plus `AGENTS.md` and `CLAUDE.md` at the project
  root. Nested rules and skills load since 2026-05-14.
- Sessions: `agent ls`, `agent resume`, `--continue`, `--resume <id>`, `/fork`, `/rewind`.
- Worktrees: `-w`/`--worktree [name]` creates `~/.cursor/worktrees/<repo>/<name>`.
- Cloud handoff: start a message with `&` to send it to a cloud agent; continue on web or mobile.
- Approvals: the CLI asks before shell commands. `/run-everything` (alias `/auto-run`), `--force`
  (`--yolo`), `--sandbox enabled|disabled`, `permissions.json` (since March 2026), and team policy.
- Subagents run in the CLI since March 2026 (CLI changelog). Tested 2026-10-24 in print mode:
  the `Subagent` tool starts a custom subagent, and `resume` by ID keeps its full context
  ([skills, subagents, and commands](skills-subagents-and-commands.md)).

## Headless and integration modes

- `agent -p "<prompt>"` (print mode) has full write and shell access. `--output-format text|json|
  stream-json`; `--trust` skips the workspace trust prompt in headless mode; skills run with
  `/skill-name` in `-p` mode. Admins can block headless use for a team.
- **ACP**: `agent acp` runs the CLI as an Agent Client Protocol server over stdio (JSON-RPC 2.0).
  JetBrains IDEs use this path ([integrations](integrations-and-public-api.md)).
- **Worker**: `agent worker start` makes the machine a Self-Hosted Machine for cloud agents
  ([self-hosted machines](self-hosted-machines-and-remote-control.md)).

## MCP and plugins in the CLI

- MCP uses the same `mcp.json` files as the editor (project → global → nested parent folders).
- Commands: `agent mcp list | list-tools <id> | login <id> | enable <id> | disable <id>`, and
  `agent mcp add <name> -- <command>` (shown on the Xcode page). `/mcp` opens the same views.
- Global servers from `~/.cursor/mcp.json` load without a per-workspace prompt; project servers
  still need approval to load (CLI changelog, April 2026). `--approve-mcps` approves all servers.
- OAuth from an SSH session: the CLI prints port-forwarding steps.
- Plugins: `/plugin` installs at user or project scope (interactive, since March 2026).
  `agent plugin marketplace add <git-url> [--git-ref]`, `list`, `update`, `remove` are scriptable.
  `--plugin-dir <path>` loads a local plugin; `enabled_plugins` in `~/.cursor/settings.json` points
  at local plugin folders (2026-05-20). Plugins imported from Claude Code appear beside native ones
  (2026-05-07).
- lore-architect recorded in August 2026 that no non-interactive plugin install command exists;
  see `lore-framework-dev/agents/lore-architect/lore/cursor-plugin-install-is-account-side.md`.

Sources: https://cursor.com/docs/cli/overview.md ; https://cursor.com/docs/cli/using.md ;
https://cursor.com/docs/cli/installation.md ; https://cursor.com/docs/cli/reference/parameters.md ;
https://cursor.com/docs/cli/reference/authentication.md ;
https://cursor.com/docs/cli/reference/slash-commands.md ; https://cursor.com/docs/cli/mcp.md ;
https://cursor.com/docs/cli/acp.md ; https://cursor.com/docs/cli/changelog.md ;
https://cursor.com/docs/integrations/xcode.md
