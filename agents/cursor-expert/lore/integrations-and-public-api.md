---
lore: 1
type: topic
summary: "Cursor integrations, Cloud Agents API, SDKs, agent-to-agent peers, admin APIs, and Origin. SDK 1.3.1 local runtime tested 2026-11-08, usage and cost 2026-11-09. Unverified: cloud lifetime and usage, queued follow-up, hosting."
parent: lore/cursor-apps-and-surfaces.md
---

# Integrations and public API

Checked 2026-10-14. Documented unless a line says otherwise. Most integrations are front doors to
[cloud agents](cloud-agents.md): setup asks for a repository provider, usage-based (on-demand)
pricing, and privacy settings.

## Chat and issue tools

| Integration | How a user starts work | Notes |
|---|---|---|
| Slack | `@Cursor <prompt>` in a channel or thread | Options `repo=`, `env=`, `branch=`, `model=`, `autopr=`, `worker=`, `pool=`, `channel=`; channel and team default pools; follow-ups in the thread |
| Microsoft Teams | `@Cursor <prompt>` | Installed from the Microsoft Marketplace; `repo`, `env`, `branch`, `model` options |
| GitHub | Comment `@cursor` on a PR or issue | The GitHub app also powers Bugbot; GitHub Enterprise Server supported. The My Machines page uses the handle `@cursoragent` |
| GitLab, Bitbucket Cloud, Azure DevOps | Repo provider for cloud agents and Bugbot; `@cursor` on Bitbucket PRs | GitLab self-hosted supported |
| Linear | Assign the issue to Cursor, or `@Cursor` in a comment | `[key=value]` options and parent-child labels |
| Jira | Assign a work item to Cursor or mention `@Cursor` | Jira Cloud with Rovo; **Teams and Enterprise only**; service-account or per-user auth |
| Notion | Notion Agents → New Agent → Cursor, then mention or assign | Beta; Notion Business or Enterprise; built on the Cursor SDK with a personal API key |

## IDEs and tools

- **JetBrains**: Cursor's agent inside IntelliJ, PyCharm, WebStorm and others through ACP, from
  the AI Assistant plugin's ACP registry. Needs a paid Cursor plan.
- **Xcode 26.3+**: Apple's built-in MCP server (`xcrun mcpbridge`, stdio, 20 tools) connects to
  Cursor like any MCP server. Needs a paid plan and a running Xcode.
- **Deeplinks**: `cursor://anysphere.cursor-deeplink/...` or `https://cursor.com/link/...` for
  prompts, commands, rules, and MCP installs.

## Programmatic access

| API or SDK | What it does | Availability |
|---|---|---|
| Cloud Agents API (`api.cursor.com/v1/...`) | Create agents and runs, stream, artifacts, environments, secrets, workers, pools, webhooks; inline `mcpServers` (max 50) | Beta, all plans |
| TypeScript SDK (`@cursor/sdk`, Node 22.13+) and Python SDK | Run Cursor's agent locally or in the cloud from code; same pricing and Privacy Mode as the IDE | All users (Start excludes the SDK) |
| SDK Bridge | Connect/protobuf protocol and binaries for other languages | All users |
| Admin, Analytics, AI Code Tracking, Bugbot APIs | Team members, usage, spend, audit logs, model access, metrics | Enterprise teams |
| Origin API | Origin repos, commits, checks, PRs, apps | Early beta |

- Auth: API keys from Dashboard → API Keys (`crsr_...`); Basic or Bearer. Default rate limit is
  20 requests per minute unless an endpoint says otherwise.
- The APIs and SDKs run agent workflows. They are not a raw chat-completions API.

## Agent-to-agent peers

Checked 2026-10-24. **Documented** (https://cursor.com/docs/agent-sdk/guides/agent-to-agent).
These connections are not a relay for editor Task subagents
([skills, subagents, and commands](skills-subagents-and-commands.md)).

- A peer is a full agent you would also run on its own. A subagent is a child role inside one
  agent. Subagent reach is the parent only. Peer reach is local co-hosted agents, or declared
  deployments on the same team, by deployment slug.
- On Cursor-managed hosting the SDK routes and authenticates. The caller does not set a URL or a
  secret. The caller decides when to delegate. The specialist keeps its own instructions, tools,
  and session.
- The caller uses MCP tools on the connection: `ask` (reason; returns status, sessionId, and
  reply), `check` (poll a running session), and `call_tool` (run a declared deterministic tool
  with no extra model turn). Pass `sessionId` to continue the specialist's session.
- Local try: one `agent-sdk dev` process, with `agent` set to the specialist's mount slug.
  Prefer one-way routing. Do not add reciprocal routes for the same request.

Projects stay a separate hub. See [editor and Agents Window](editor-agents-window-and-modes.md).

## SDK local runtime: tested 2026-11-08

**Local test**, not documentation: `@cursor/sdk` 1.3.1, Node 24.22, macOS x64, local runtime,
login stored by `Cursor.auth.login()`. Cloud runtime, API-key mode, Windows, Linux, nested
subagents, and terms for use as a backend were not tested.

- **Auth and models:** the stored login (`~/.cursor/sdk/auth.json`) worked with no env var.
  `Cursor.models.list()` returned 48 models; 35 have an effort-like parameter whose id differs by
  model (`effort`, `reasoning_effort`, or `reasoning`) and whose values differ (`low/medium/high`,
  plus `xhigh`, `max`, `minimal`, `none`, `extra-high` on some). Other parameters: `thinking`,
  `context`, `fast`. Seven models have none, including `default` (Auto). A local run needs an
  explicit `model` (`{ id: "default" }` works); without it `agent.send` throws `ConfigurationError`.
- **Lifetime:** `Agent.create({ agentId, local: { cwd }, model })` keeps a caller-chosen
  `agentId`. `agent.send()` returns a promise of a `Run`; `run.stream()` yields events;
  `run.wait()` gives status, result, usage. `Agent.create` without a `send` leaves a phantom run in
  status `running`, and `Agent.resume` in a new process then fails with `UnknownAgentError: already
  has active run`: create the agent at the first send. `Agent.resume`, `get`, `list`, `listRuns`,
  `getRun` and `messages.list` find a local agent only with `{ runtime: "local", cwd }`. Resume of
  an unknown ID gives `AgentNotFoundError`.
- **Usage:** a `listRuns` item has id, currentStatus, createdAt, model, and per-run usage.
  `inputTokens` includes both `cacheReadTokens` and `cacheWriteTokens` (probe 2026-11-09 with
  claude-haiku-5-5: 10,004 = 7,315 cache read + 2,685 cache write + 4 fresh). `totalTokens` =
  input + output; the SDK docs formula that adds the cache tokens again is wrong.
  `reasoningTokens` is part of output. No account limits, context window, or subagent usage
  appeared in the paths tested.
- **Model parameters (2026-11-09):** Fast, context, and effort are params on the model selection
  (`fast: true/false`, `context: "256k"/"500k"`, an effort param), not model IDs. A run's `model`
  keeps only the params the caller sent. A missing param means the catalog default, which can be
  Fast and 500k, so send the params explicitly when cost matters. Model `default` is Auto.
- **Cost (2026-11-09):** `Agent.getUsage()` returns server cost `{ rawCostCents, chargedCents }`
  per agent and per run or turn. For local agents it rolls out per account; on the tested
  individual account it returned `[feature_unavailable]`. `chargedCents` is 0 for usage included
  in the plan, BYOK, and credit grants, so use `rawCostCents` for the list-price cost.
- **No per-request usage:** the SDK drops its internal `modelCallCompleted` events. The local store
  `~/.cursor/projects/<cwd>/sdk-agent-store/*/index.db` holds one usage event per run. A summary
  (compaction) run has no usage, so its cost shows only in `getUsage` or on the dashboard.
- **Message delivery:** `run.steer(text)` worked in a running turn (`complete_delivered`) and the
  turn answered it. `run.cancel()` ended a turn with status `cancelled`, and no shell child
  processes remained.
- **History:** `run.conversation()` returns turns with `steps` only (`thinkingMessage`,
  `assistantMessage`, `toolCall`): no user prompt, no timestamps. A steering text shows as the
  turn's `userMessage`. A run whose process died stays `running` and `conversation()` never
  answers: use a timeout. `Agent.messages.list` returns user messages in order (steering
  included) as `message.turn.value.userMessage.text`. `agent.summarize()` emits `summary` events
  and the context survived; the summary run has no usage and no turn (inference for detection).
- **Subagents:** inline `agents: { name: { description, prompt } }` and `.cursor/agents/*.md` both
  worked. A subagent is a `task` tool call; `args.agentId` is present from the first `running`
  event; `args.subagentType` is `{ kind: "custom", name }`; the result holds `conversationSteps`
  and `agentId`, in a different step shape (`{ toolCall: { shellToolCall: ... } }`,
  `{ thinkingMessage: { text } }`, `{ assistantMessage: { text } }`). The SDK also writes plain
  transcripts under `~/.cursor/projects/<workspace>/agent-transcripts/<agent>/` (lossy: no tool
  results).
- **Sandbox:** `local.sandboxOptions` has one field, `enabled`. With `true`, the SDK threw
  `ConfigurationError: sandboxing is not supported in this environment` inside an already
  sandboxed shell (cause not confirmed). Without it, a shell command wrote outside `cwd`.
- **Noise:** the SDK prints `Ripgrep path not configured` and shell-parser notes to stderr
  (harmless). pnpm installs it but warns about ignored build scripts.

## Still unverified (recorded 2026-10-18)

- **Cloud and API lifetime and usage:** what persists across runs in the Cloud Agents API and the
  cloud runtime; which events expose tokens, cost, and subagent usage there, and how to attribute
  them to a run and a parent without double counting.
- **Follow-up queueing in the cloud:** the local test showed steer and cancel only. Check queued
  follow-ups after work finishes, delivery timing, and cancellation effects on the cloud runtime.
- **Hosting:** which SDK control and tool-execution components can run on private infrastructure.
  Distinguish a local SDK session from a self-hosted worker controlled by Cursor's cloud. Recheck
  [self-hosted machines](self-hosted-machines-and-remote-control.md) and [cloud agents](cloud-agents.md).
- **Nested subagents**, and terms for use of the SDK as a product backend.

Before an implementation recommendation, recheck the official SDK, API, and worker documentation
below. Record exact methods or endpoints, supported surfaces, check dates, and limits. Practical
guidance for wrappers: [framework design notes](notes-for-agent-framework-designers.md).

## Origin

- Cursor's git forge in early beta: create repos, push and pull with git, mirror GitHub repos,
  PRs and stacks, code search at cursor.com/codebase, Origin Apps (App Marketplace, changelog
  2026-10-13), and an `origin` CLI.
- Plans: Start, Pro, Pro+, Ultra, Teams, Enterprise; not free; not with Legacy Privacy Mode.
- Origin MCP: `https://api.origin.cursor.com/mcp` (and `/mcp/readonly`), stateless streamable
  HTTP, tools only. Available only in Cursor and Grok Bot for now.

Sources: https://cursor.com/docs/integrations/slack.md ; https://cursor.com/docs/integrations/microsoft-teams.md ;
https://cursor.com/docs/integrations/github.md ; https://cursor.com/docs/integrations/linear.md ;
https://cursor.com/docs/integrations/jira.md ; https://cursor.com/docs/integrations/notion.md ;
https://cursor.com/docs/integrations/jetbrains.md ; https://cursor.com/docs/integrations/xcode.md ;
https://cursor.com/docs/reference/deeplinks.md ; https://cursor.com/docs/api.md ;
https://cursor.com/docs/cloud-agent/api/endpoints.md ; https://cursor.com/docs/sdk/typescript.md ; https://cursor.com/docs/agent-sdk/guides/agent-to-agent ;
https://cursor.com/docs/sdk/bridge.md ; https://cursor.com/docs/origin.md ; https://cursor.com/docs/api/origin/mcp.md ;
https://cursor.com/docs/models-and-pricing.md ; https://cursor.com/changelog
