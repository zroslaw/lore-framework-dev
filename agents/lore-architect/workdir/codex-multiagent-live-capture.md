# Codex Multi-Agent — Live Ground-Truth Capture

Companion to `codex-multiagent-research.md`. This file records what was verified
**directly against the installed binary** (`/usr/local/bin/codex`, `codex-cli 0.142.5`) and
`codex features list` on 2026-07-05. Evidence tier: **BINARY** (authoritative for this
version) unless noted. Captured by lore-architect while designing the subagent-spawn adapter
binding for the multi-engine port.

## What we could and could not capture

- **Captured:** feature-flag state, the multi-agent tool set, built-in roles, config caps,
  thread/subagent data model, hooks, and — most useful — **Codex's own model-facing
  delegation guidance** (lifted from the `instructions_template` system prompt in the binary).
- **NOT cleanly capturable locally:** the exact per-parameter JSON Schemas for each tool.
  `codex debug prompt-input` renders only the *message* list (developer + user), **not** the
  `tools` array — the tool schemas are injected at API-request time. The binary holds them but
  not as one dumpable JSON blob. **To get exact schemas:** capture a live API request from a
  real session (request logging / proxy), or dump from source (`openai/codex` repo).

## Feature flags (`codex features list`)

| Flag | Stage | Effective |
|---|---|---|
| `multi_agent` | **stable** | **true (ON by default)** |
| `enable_fanout` | under development | false |
| `multi_agent_v2` | under development | false |
| `multi_agent_mode` | removed | false |
| `use_agent_identity` | under development | false |

So: single-level multi-agent is **on out of the box**; deeper fan-out (`enable_fanout`,
`multi_agent_v2`) is gated off in this version.

## Multi-agent tools (model-facing)

Confirmed present (names via `agents.*` config keys + description strings):
`spawn_agent`, `list_agents`, `wait_agent`, plus (from research + binary strings)
`followup_task`, `send_message`/`send_input`, `interrupt_agent`, `close_agent`, `resume_agent`,
and an experimental `spawn_agents_on_csv`.

Verbatim tool description (BINARY):
> **spawn_agent** — "Spawns an agent to work on the specified task. If your current task is
> `/root/task1` and you spawn_agent with task_name `task_3` the agent will have canonical task
> name `/root/task1/task_3`."

Hierarchical canonical task names (`/root/...`) → a real tree, not a flat pool.

## THE load-bearing constraint for the adapter

**These collaboration tools cannot be called from inside a shell command** (`functions.exec`).
Spawning must be expressed as **model instructions in the session**, not as a `codex ...`
shell invocation. This is exactly why our headless `codex exec` finalize test saw merge run
**inline** — the model had no in-context spawn tool in that mode, so it improvised inline.
It was NOT evidence that Codex lacks subagents.

## Built-in roles

`default`, `worker`, `explorer` (occurrence counts in binary: default ≫ worker ≫ explorer).
Guidance prefers a **worker** (bounded code-change subtask) over a read-only **explorer** when
the subagent can make a bounded patch in a clear write scope.

## Config caps (`agents.*`)

`agents.max_threads` (research: 6), `agents.max_depth` (research: 1),
`agents.job_max_runtime_seconds`. Depth 1 = the main agent may spawn subagents, but those
subagents cannot themselves spawn (no grandchildren) in this version.

## Thread / subagent data model (BINARY)

Subagent = a thread in a tree. Fields observed on the Thread type:
- `parent_thread_id` — "only set if this thread is a subagent"
- `agent_role` — role assigned to an AgentControl-spawned sub-agent
- `agent_nickname` — "random unique nickname assigned to an AgentControl-spawned sub-agent"
- `session id shared by threads that belong to the same session tree`
- ephemeral flag — subagent threads can be non-materialized on disk

## Hooks

`SubagentStart` / `SubagentStop` lifecycle hooks, each with `.command.input` / `.command.output`
schemas (alongside PreToolUse/PostToolUse/PreCompact/SessionStart/etc.). These give us
deterministic hook points around subagent lifecycle if the binding ever needs them.

## Codex's own delegation guidance (from `instructions_template`, BINARY — verbatim excerpts)

- "Use a subagent when a subtask is easy enough for it to handle and **can run in parallel**
  with your local work. Prefer delegating concrete, bounded sidecar tasks that materially
  advance the main task without blocking your immediate next local step."
- "While the subagent is running in the background, **do meaningful non-overlapping work
  immediately**."
- "Call **wait_agent** very sparingly. Only call wait_agent when you need the result
  immediately for the next critical-path step and you are blocked until it returns."
- "Do **not** redo delegated subagent tasks yourself; focus on integrating results or tackling
  non-overlapping work."
- "review the subagent's output and reasoning and emitted artifacts"; "clean up subagents'
  artifacts to avoid additional contamination."

### ⚠️ Skill-handling rule that directly touches lore's design

> "The main agent must **read each required instruction or reference file itself** before
> acting on it. **Do not delegate reading, summarizing, or interpreting skill instructions to a
> subagent.** Subagents may still perform task work when the selected skill allows it."

Implication: lore's merge/recall pattern where a spawned subagent **boots itself and reads
docs** partially collides with Codex's convention (Codex wants the *main* agent to read skill
docs, delegating only task work). The Codex binding may need to restructure fan-out so the host
reads the procedure doc, then hands each subagent a self-contained *task* brief — rather than
telling each subagent to go read `agent-boot.md` itself. Worth testing both ways.

## Declarative custom agents (research tier: DOCS/BINARY)

`~/.codex/agents/` and `.codex/agents/` hold custom agent defs: `name`, `description`,
`developer_instructions`, plus `model` / `effort` / `sandbox_mode` / `mcp_servers` /
`skills.config`. On this machine `~/.codex/agents/` does **not exist yet** (not created by
default — you author it). This is the natural home for a generated `.codex/agents/<lore-agent>.md`
per lore agent.

## AGENTS.md

Confirmed as Codex's project-memory file (appears in the feature/hook string table alongside
`mcpServers`, hooks, etc.). Aligns with the planned `CLAUDE.md → AGENTS.md` memory-file binding.

## Recommended binding priority (updated by this capture)

1. **Native `spawn_agent`** — generate a `.codex/agents/<lore-agent>.md` per lore agent; express
   fan-out (merge, recall) as **in-session model instructions**, not shell calls. Respect
   `max_depth=1` (host spawns; subagents don't re-spawn) and `max_threads` (≈6).
2. **Inline** — fallback when `multi_agent` is disabled, or a step would exceed `max_depth`.
3. **`codex exec --json` / `codex mcp-server`** — for **headless/batch** orchestration outside a
   live session (the only place shell-driven spawning applies), e.g. a CI-driven merge.

## Next step to harden this

Run a **real** (non-headless) Codex session that actually spawns a subagent, and capture the
live API request to read the exact `spawn_agent` / `wait_agent` JSON Schemas. Then encode the
binding against real schemas. Do not code the binding off string-scraping alone.

## Sources

- `/usr/local/bin/codex` (`codex-cli 0.142.5`) — `strings` + `codex features list` +
  `codex debug prompt-input`. BINARY tier, authoritative for this version, ahead of public docs.
- Companion: `codex-multiagent-research.md` (web/docs/community research, tiered sources).
