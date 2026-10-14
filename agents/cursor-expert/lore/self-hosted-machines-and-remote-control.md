---
lore: 1
type: topic
summary: "Agents whose loop runs in Cursor's cloud but whose tool calls run on the user's machine: My Machines, Team Pools, and Remote Control from iOS. Requirements, plans, MCP and hooks behavior, networking. Open for phone-to-laptop questions."
parent: lore/cursor-apps-and-surfaces.md
---

# Self-hosted machines and Remote Control

Checked 2026-10-14. Documented unless a line says otherwise. Both features split the agent: the
loop, inference, and planning run in Cursor's cloud; terminal commands, file edits, browser
actions, and git run on a machine the user controls.

## My Machines (personal worker)

- Install the CLI, `agent login`, then `agent worker start`. The worker opens an outbound HTTPS
  connection; no inbound ports or VPN. It stays connected until stopped.
- `--worker-dir <path>` (repeatable) registers repo roots; routing uses each root's git remote.
  `--name` names the machine; `--computer-use` lets the agent drive the desktop (macOS helper app,
  or Linux X11).
- Start a run on it: pick the machine under **My Machines** at cursor.com/agents (or the "Run on"
  menu, iOS worker picker), or use `worker=<name>` / `machine=<name>` in Slack, GitHub
  (`@cursoragent`), or a Linear comment. The machine must belong to the triggering user and match
  the target repo, or the request fails.
- Credentials: browser login, a personal user API key, or a user-scoped token. Service-account
  keys start only pool workers.
- The machine keeps its own tools, credentials, and network, and gets no dashboard secrets. Cursor
  never reads `.cursor/environment.json` there.
- Hooks: project hooks from the worker directory's `.cursor/hooks.json`; `sessionStart` and
  `sessionEnd` fire when a session claims and releases the worker.
- MCP: stdio servers run on the worker and reach private networks; HTTP/SSE servers run from
  Cursor's backend and cannot reach private endpoints. Configure servers in the Cloud Agents
  dashboard; the worker does not read the repo's `.cursor/mcp.json` (Team Pool docs; forum staff,
  2026-04-17). The help page says "some MCP gaps remain" on workers, and no tool exists to debug
  MCP loading on a worker (forum staff).
- Network: outbound to `api2.cursor.sh`, `api2direct.cursor.sh`, `downloads.cursor.com`, and the
  artifacts S3 host.
- Plan: no explicit plan line for My Machines; it is a cloud-agent path, so inference: any plan
  with Cloud Agents.

## Team Pools

Named queues of workers for a team (`agent worker --pool`); any-repo pools with
`--clone-git-repos`; a controller can scale machines from a spawn script. Partners: AWS Lambda,
Cloudflare, Coder, Daytona, E2B, Modal, Namespace, Vercel (blog 2026-09-02). **Enterprise plan**
and a service-account API key required (pool docs). A staff forum post of 2026-04-17 said "a Team
plan"; the docs are newer.

## Remote Control (local session → phone)

- Hand an agent that already runs on the computer to the phone: run `/remote-control` in its input
  in the **Agents Window** (only there), then open the session in the iOS app inbox.
- Cursor manages a worker on the computer by itself. The agent loop moves to the cloud; every tool
  call still runs on the computer. Repos, secrets, and build caches stay local; tool results and
  needed context go to Cursor.
- Requirements: Cursor 3.9.8 or later; turn it on in Settings > Agents; a plan with Cloud Agents
  (Start, Pro, Pro+, Ultra, Teams, Enterprise); cloud data storage allowed by privacy settings; a
  local or Remote SSH workspace (no git remote needed). On Teams and Enterprise an admin enables
  it under Dashboard → Cloud Agents → Self-Hosted, which also enables self-hosted workers.
- The computer must stay awake and online. "Keep this computer awake" (Settings > Agents) prevents
  sleep while plugged in.
- MCP: not documented in any doc or release note. Inference, untested: it follows worker routing —
  stdio servers on the computer, URL servers from Cursor's backend, and servers from the dashboard
  config rather than `.cursor/mcp.json`. If so, a project-only MCP server can be missing after the
  hand-off.
- The help page calls it beta. The changelog entry "Remote control for local agents" is dated
  2026-10-06.

## Compared with Claude (inference)

My Machines resembles Claude Dispatch (start work from the phone, run it on the desktop) but with
no manager agent; Projects add the coordinator. Remote Control matches Claude Code Remote Control:
one existing session steered from the phone.

Sources: https://cursor.com/docs/cloud-agent/self-hosted/my-machines.md ;
https://cursor.com/docs/cloud-agent/self-hosted.md ; https://cursor.com/help/ai-features/self-hosted-machines.md ;
https://cursor.com/docs/cloud-agent/self-hosted/pool.md ;
https://cursor.com/docs/cloud-agent/mobile.md ; https://cursor.com/help/ai-features/mobile-app.md ;
https://cursor.com/blog/self-hosted-machines ; https://cursor.com/changelog ;
https://forum.cursor.com/t/how-to-use-mcps-with-self-hosted-agents/157677 (forum, staff, 2026-04-17)
