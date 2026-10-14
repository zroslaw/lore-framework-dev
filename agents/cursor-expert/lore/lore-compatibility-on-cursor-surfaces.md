---
lore: 1
type: topic
summary: "Inference, untested (2026-10-14): where Lore's lr plugin can and cannot run on Cursor surfaces (editor, CLI, Remote Control, My Machines, cloud agents, web, iOS, Grok Bot), what to test first, and whether remote MCP reaches web and mobile."
parent: lore-context.md
---

# Lore compatibility on Cursor surfaces

**Label: inference, not tested**, unless a line says documented. I concluded this on 2026-10-14
from the Cursor docs summarized in my other topics. How Lore installs and runs on Cursor belongs
to lore-architect: see the Cursor engine profile `lore-framework/docs/engines/cursor.md` and the
architect's hub `lore-framework-dev/agents/lore-architect/lore/cursor-engine-capabilities.md`.

## What Lore needs from a surface

The `lr` plugin's skills call `python3` scripts under the framework root and run `git` against
the workspace repos; finalization commits and pushes to each repo's default branch. A surface
needs the plugin's skills, a shell with `python3` and `git`, the whole workspace checkout, and
push access.

## Per surface

| Surface | Verdict | Reason |
|---|---|---|
| Desktop editor and Agents Window | Works | A supported Lore engine (see the engine profile). Local tools and files |
| Cursor CLI | Works | A supported Lore engine; the profile's tests ran here |
| Remote Control from iOS | Likely works | Documented: tool calls keep running on the computer after the hand-off. Needs the Agents Window, Cursor 3.9.8+, and an awake computer |
| My Machines worker, started from web, iOS, or Slack | Likely works, with setup | Documented: tool calls run on the user's machine. Open: register the workspace with `--worker-dir` (routing uses each root's git remote; `worker=` must match the target repo), and check that the worker loads the user's plugins |
| Cursor-hosted cloud agent | Doubtful | No local workspace. A multi-repo environment can clone several repos, and repo skills, synced `~/.cursor/skills/`, and selected plugins can load. But the plugin must reach the VM, the scripts must find the framework root, and cloud agents work on their own branch and open PRs while Lore pushes to default branches. Cloud agents never ask for approval |
| Cloud subagents (`/in-cloud`) | Doubtful | Same as cloud agents |
| Web and iOS on their own | Cannot run Lore | Clients only. They reach Lore only through the rows above |
| Grok Bot | Unlikely; not evaluated | Its own cloud computer; no Cursor plugin, rule, or skill system for coding projects |
| Bugbot, Automations | Not a fit | Bugbot ignores rules and skills; automations are cloud agents |

## Remote MCP as a route to web and mobile

Inference: a remote MCP server (streamable HTTP, OAuth) is the one Cursor extension type that
reaches every agent surface — local, cloud, web, iOS (chosen per run), and self-hosted — without
local files. Documented limits: on cloud surfaces Cursor's backend makes the call, so the server
must be reachable from the internet; OAuth is per user; cloud agents never ask before a tool call;
only tools are known to work off the desktop; Grok Bot reaches MCP only as marketplace connectors.

Config is the other limit. A repo `.cursor/mcp.json` reaches local agents (editor, CLI) only.
Cloud agents and self-hosted workers read only servers set up in the Cursor dashboard (forum
staff, 2026-04-17; Team Pool docs), so each user adds the server at cursor.com/agents, or a team
admin adds it under Dashboard > Plugins & MCPs. Whether a Remote Control session keeps the
project's MCP servers is not documented. Details: [remote MCP by surface](remote-mcp-by-surface.md).

## Documented facts lore-architect may want

- The current docs name the CLI command `agent`; the engine profile and probe notes say
  `cursor-agent`.
- A symlink in `~/.cursor/plugins/local` loads only when its target is inside that folder
  ([plugins](plugins-and-marketplaces.md)).
- Cursor reads `CLAUDE.md` like `AGENTS.md` and always applies it; it also reads `.claude/skills/`,
  `.claude/agents/`, and Claude Code hooks (third-party imports on by default). A workspace set up
  for Claude Code partly loads in Cursor as is.
- The CLI loads local plugins from `enabled_plugins` in `~/.cursor/settings.json` (2026-05-20).
- Hook scripts get `CLAUDE_PROJECT_DIR` as an alias of `CURSOR_PROJECT_DIR`.

## How to apply

When asked whether Lore works on a Cursor surface, answer from this topic and say it is untested.
Suggest these tests first: (1) boot a Lore agent in the Agents Window, hand it off with
`/remote-control`, run a recall from the phone, and check which MCP servers the session still
has; (2) start a My Machines worker in the
workspace and trigger a boot from cursor.com/agents.

Sources: https://cursor.com/docs/cloud-agent/mobile.md ; https://cursor.com/docs/cloud-agent/self-hosted/my-machines.md ;
https://cursor.com/docs/cloud-agent/setup.md ; https://cursor.com/docs/skills.md ; https://cursor.com/docs/plugins.md ;
https://cursor.com/help/customization/rules.md ; https://cursor.com/docs/reference/third-party-hooks.md ;
https://cursor.com/docs/hooks.md ; https://cursor.com/docs/cli/changelog.md ;
https://cursor.com/docs/cloud-agent/self-hosted/pool.md ;
https://forum.cursor.com/t/how-to-use-mcps-with-self-hosted-agents/157677 (forum, staff, 2026-04-17)
