# Codex Multi-Agent / Subagent Research

Research date: 2026-07-05 · Local Codex probed: **codex-cli 0.142.5** (Homebrew cask, `gpt-5.4-mini` default) · For: lore framework → Codex port ("subagent-spawn" adapter binding)

Evidence tiers used below:
- **[BINARY]** = ground-truthed from the installed 0.142.5 binary / CLI help / feature flags (authoritative for *this* installed build).
- **[DOCS]** = official OpenAI Codex docs (developers.openai.com).
- **[COMMUNITY]** = GitHub discussions / third-party blogs (weigh accordingly).
- **[INFERENCE]** = my reasoning, not directly stated.

---

## TL;DR

- **The lead's premise is half-right and needs correcting.** There is **no `codex subagent` / `codex agents` CLI *subcommand*** — that probe was correct. But Codex **does have a first-class, native multi-agent subsystem**; it is exposed **as model-facing tools inside a session**, not as a shell subcommand. So "no subagent subcommand" ≠ "no subagents." **[BINARY][DOCS]**
- **Native subagent spawning is real, shipping, and ON by default** in 0.142.5. The feature flag `multi_agent` is stage **`stable`** and **effective `true`**. The model is given tools `spawn_agent`, `followup_task`, `send_message`, `wait_agent`, `close_agent`, `resume_agent`, `interrupt_agent`, `list_agents` (backed by Rust modules `core/src/tools/handlers/multi_agents` and `multi_agents_v2`). **[BINARY]**
- **Teams / message-passing exist.** Subagents are threads in a **root-thread tree** with `parent_thread_id`, `agent_role`, and `agent_nickname`; agents exchange messages via a **mailbox** (`send_message` = message without triggering a turn; `followup_task` = message that triggers a turn; `interrupt=true` = preempt). This is a genuine lead/teammate model analogous to Claude Code "Agent Teams." **[BINARY]**
- **Custom, declarative agent definitions exist** — like Claude's subagent defs: files in `~/.codex/agents/` (personal) and `.codex/agents/` (project), with fields `name`, `description`, `developer_instructions`, and optional `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`, `nickname_candidates`. Built-in agents: `default`, `worker`, `explorer`. **[DOCS]**
- **Fan-out / orchestration**: parallelism is real (parent does non-blocking work while children run; `wait_agent` consolidates). A CSV fan-out primitive `spawn_agents_on_csv` (one worker per row, `max_concurrency`, `output_schema`) exists as an experimental skill. Deeper fan-out is gated behind `enable_fanout` (**`under development`, false**) and `multi_agent_v2` (**`under development`, false**). **[BINARY][DOCS]**
- **Codex Cloud** offers a parallel substrate: `codex cloud exec --env <ID> --attempts <N>` runs best-of-N attempts; `codex cloud list/status/diff/apply` manage them from the CLI. **[BINARY]**
- **Two solid emulation paths also exist** and are officially blessed for automation: (a) **`codex mcp-server`** → drive Codex as an MCP server from the OpenAI Agents SDK (`codex()` / `codex-reply()` tools, deterministic traced workflows); (b) **`codex exec --json`** isolated workers behind an external queue. **[DOCS][COMMUNITY]**
- **Bottom line for the port:** Codex is *closer* to Claude Code on multi-agent than assumed. The adapter should **map lore's spawn-teammate onto native `spawn_agent`/`send_message`/`wait_agent` first**, fall back to **inline (single-agent) execution**, and reserve **`codex exec` / `mcp-server`** for headless batch. See "Implications."

⚠️ **Recency caveat (read this):** 0.142.5 is far ahead of what public docs/GitHub described at my Jan 2026 knowledge cutoff. The **binary is authoritative for what your installed build actually does**; the web sources below corroborate the same feature set and the official docs pages exist, but exact tool names/config keys should be re-verified against the running binary before you code against them (see "How to re-verify locally").

---

## Native capabilities

### 1. Subagent spawning — **YES, native, default-on** [BINARY][DOCS]

**Feature flag (authoritative for this build):** `codex features list` →
```
multi_agent           stable             true      ← enabled by default
multi_agent_v2        under development  false
enable_fanout         under development  false
goals                 stable             true
collaboration_modes   removed            true
multi_agent_mode      removed            false
```

**Model-facing tools** (extracted from binary strings + Rust symbol names `codex_core::tools::handlers::multi_agents{,_v2}::*`):

| Tool | Description (verbatim / near-verbatim from binary) |
|---|---|
| `spawn_agent` | "Spawn a sub-agent for a well-scoped task." Creates a child agent; **hierarchical canonical task names**: "If your current task is `/root/task1` and you spawn_agent with task_name `task_3` the agent will have canonical task name `/root/task1/task_3`." |
| `followup_task` | "give an existing agent a new task and trigger a turn." |
| `send_message` (aka `send_input`) | "Send a message to an existing agent. Use interrupt=true to redirect work immediately." `send_message` passes a message **without triggering a turn**; `interrupt=true` interrupts the current task and handles the message immediately, else it queues. |
| `wait_agent` | "Wait for agents to reach a final status. Completed statuses may include the agent's final message. Returns empty status when timed out." Guidance: "**Call wait_agent very sparingly.** Only call wait_agent when you need the result immediately for the next critical-path step and you are blocked until it returns." |
| `interrupt_agent` | preempt a running agent. |
| `close_agent` | "close / shutdown / stop agent." |
| `resume_agent` | "Resume a previously closed agent by id so it can receive send_input and wait_agent calls." |
| `list_agents` | "List live agents in the current root thread tree. Optionally filter by task-path prefix." |

**Agent lifecycle statuses** (binary): `pending_init`, `running`, `interrupted`, `errored`, `not_found`, `completed`, `failed`.

**Important call constraint (binary):** these collaboration tools **cannot be called from inside `functions.exec`**. They must be direct tool calls (`to=functions.spawn_agent`, or `to=functions.agents.spawn_agent` when `tool_namespace = "agents"`). They are intentionally absent from the exec `tools.*` namespace. → *An adapter that shells out must not expect a nested shell to reach these tools.*

**Declarative custom agent definitions [DOCS]** — direct analog to Claude subagent defs / Cursor `.cursor/agents/`:
- Personal: `~/.codex/agents/`  ·  Project: `.codex/agents/` (one file per agent).
- Required: `name`, `description`, `developer_instructions`.
- Optional: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`.
- "Codex loads these files as **configuration layers** for spawned sessions" → custom agents override the same settings a normal session config can. A custom agent matching a built-in name (`default`/`worker`/`explorer`) takes precedence.
- Config key `[agents]` block confirmed in binary (`OrchestratorFeatureToml`, and TOML keys `max_threads`, `max_depth`, `job_max_runtime_seconds`, `interrupt_message`, `review_model`). Docs give defaults: `agents.max_threads=6`, `agents.max_depth=1`.

**Hooks [BINARY]:** lifecycle hooks `SubagentStart` / `SubagentStop` exist (command names `subagent-start` / `subagent-stop`, with input/output JSON schemas) — parallel to Claude Code's `SubagentStop` hook. Full hook set: `pre-tool-use, permission-request, post-tool-use, pre-compact, post-compact, session-start, user-prompt-submit, subagent-start, subagent-stop, stop`.

### 2. Teams / parallel multi-agent — **YES** [BINARY][DOCS]

- **Thread tree:** every subagent is a thread carrying `root_thread_id` (session tree), `parent_thread_id` ("only set if this thread is a subagent"), `agent_role`, `agent_nickname` ("random unique nickname assigned to an AgentControl-spawned sub-agent"). Persisted in SQLite (`threads.agent_role`, `threads.agent_nickname`, `root_thread_id`). **[BINARY]**
- **Message passing** between agents via a **mailbox** ("Whether the wait call returned because no mailbox update arrived before the timeout"). `send_message` (no turn) vs `followup_task` (turn) vs `interrupt`. This is the lead/teammate + inter-agent messaging model. **[BINARY]**
- **`/agent` CLI command [DOCS]:** in the interactive CLI/app, `/agent` switches between active agent threads, inspects an ongoing thread, and lets you steer/stop/close a running subagent. Press `o` to open a thread before approving/rejecting its approval requests.
- **Sandbox inheritance [DOCS]:** subagents inherit the parent's sandbox policy; parent runtime overrides (`/permissions`, `--yolo`) reapply to children; a custom agent may override via `sandbox_mode`.
- **Parallelism [DOCS]:** "Multiple agents run in parallel; Codex waits until all requested results are available, then returns a consolidated response." Canonical prompt: *"Spawn one agent per point, wait for all of them, and summarize the result for each point."*

### 3. Dynamic workflows / fan-out — **PARTIAL (shipping primitive + gated deeper features)** [BINARY][DOCS]

- **Model-driven fan-out** works today: the model plans, spawns N agents with disjoint write scopes, does non-blocking local work, then `wait_agent`s. The system prompt embeds extensive **delegation doctrine** (verbatim from binary): assign **ownership** ("Worker 1 … authentication module, Worker 2 … database layer"), **disjoint write sets** ("decompose work so each delegated task has a disjoint write set"), "while the subagent is running in the background, do meaningful non-overlapping work immediately," "do not delegate urgent blocking work when your immediate next step depends on the result." **[BINARY]**
- **CSV fan-out primitive** `spawn_agents_on_csv` (experimental skill): params `csv_path`, `instruction` (with `{column}` placeholders), `id_column`, `output_schema`, `output_csv_path`, `max_concurrency`, `max_runtime_seconds`; each worker calls `report_agent_job_result` once. This is a true pipeline/parallel-over-rows primitive. **[DOCS]**
- **Gated / not-yet:** `enable_fanout` and `multi_agent_v2` are both `under development`/false in 0.142.5; `deferred_executor` and `use_agent_identity` also `under development`. So the *next-gen* orchestration layer is present in the binary but not switched on. There's also an **`orchestrator`** concept (config `OrchestratorToml`/`OrchestratorFeatureToml`, orchestrator-authority skills via `skills.list`/`skills.read`, orchestrator phase machine) — appears tied to Cloud/app-server orchestration; details unverified. **[BINARY][INFERENCE]**
- **"Ultra" reasoning effort** triggers "proactive multi-agent behavior" (binary: "Use `effort: \"ultra\"` for proactive multi-agent behavior"). I.e. at Ultra the model spontaneously delegates; at lower efforts it only spawns when asked. **[BINARY]**

### 4. Codex Cloud — parallel task substrate [BINARY][DOCS]

`codex cloud` is marked **[EXPERIMENTAL]** in 0.142.5. Subcommands:
```
codex cloud exec --env <ENV_ID> [--attempts N] [--branch B] "<prompt>"   # submit task, best-of-N
codex cloud list | status | diff | apply
```
- `--attempts` = best-of-N assistant attempts (parallel attempts, pick best). **[BINARY]**
- Tasks run in a remote env against a git branch; `apply` pulls the diff locally. **[BINARY]**
- **Viable as a subagent substrate?** For *headless batch fan-out with isolation*, yes — spawn many `codex cloud exec` tasks from a script and reconcile diffs. Not for tight in-session message-passing (that's what native `spawn_agent` is for). **[INFERENCE]**

---

## Emulation paths (also useful even though native exists)

| Path | How it works | Works? | Trade-offs |
|---|---|---|---|
| **Native `spawn_agent` (preferred)** | Ask the running agent (or a custom agent def) to spawn/message/wait/close children. | ✅ Shipping, default-on in 0.142.5. | Best context isolation + message passing + consolidation. But only reachable **from inside a live model turn**, not from a shell script; cannot be invoked from within `functions.exec`. **[BINARY]** |
| **`codex mcp-server` + OpenAI Agents SDK** | `codex mcp-server` exposes Codex over MCP (stdio); Agents SDK connects via `MCPServerStdio`, gets tools `codex()` (start, with config) and `codex-reply()` (continue via `threadId`). Build sequential handoffs / parallel fan-out in Python. | ✅ Officially documented. | Deterministic, **fully traced** (OpenAI Traces dashboard), reviewable pipelines that "scale from a single agent to a full delivery pipeline." Cost: you own the orchestration code; extra process; each `codex()` is a fresh session (context isolation is total but you must pass context explicitly). **[DOCS]** |
| **`codex exec --json` workers behind a queue** | External queue manager launches many `codex exec --json` non-interactive workers; each emits patches/artifacts, not shared-tree mutations. | ✅ Recommended by OpenAI staff for **automated batch** (vs interactive → use native subagents). **[COMMUNITY]** | Strong isolation; parallelism = however many processes you run; token cost = N full sessions (no shared context ⇒ re-send context each worker); output capture via `--json` stream. Must avoid concurrent writes to one tree → use **git worktrees / branches / per-task sandboxes**; use SQLite/Redis for coordination, not model-edited JSON. **[COMMUNITY]** |
| **Nested `codex exec` recursion (shell)** | An agent shells out to `codex exec "<subtask>"`. | ⚠️ Works mechanically but discouraged for coordination. | No mailbox/consolidation; the nested process **cannot reach native collaboration tools**; you reinvent waiting/locking/retries. Fine for a one-shot "ask a fresh Codex to do X and capture stdout." **[BINARY][INFERENCE]** |
| **`codex app-server` / `exec-server`** | `[experimental]` JSON-RPC-style protocols (TS bindings + JSON-schema generators: `codex app-server generate-ts` / `generate-json-schema`; `codex exec-server --listen ws://…\|stdio`) to drive threads programmatically, incl. resuming/forking threads and (per protocol) subagent threads. | ⚠️ Experimental, low-level. | Most powerful/most work; this is the substrate the app itself uses. Overkill for the lore adapter unless you need a long-lived daemon. **[BINARY]** |

---

## Comparison table — Claude Code vs Codex 0.142.5

| Capability | Claude Code | Codex 0.142.5 | Notes |
|---|---|---|---|
| Spawn a subagent from within a session | `Agent` tool (`subagent_type`) | ✅ `spawn_agent` tool (`multi_agent` flag, stable/on) | Codex adds **hierarchical task paths** (`/root/task1/task_3`). |
| Declarative agent definitions | `.claude/agents/*.md` frontmatter | ✅ `~/.codex/agents/` + `.codex/agents/` (name/description/developer_instructions + model/effort/sandbox/mcp/skills) | Near 1:1. |
| Fork current context into child | `subagent_type: "fork"` | ✅ thread **fork** (`thread/fork`, `Source thread id when created by forking`) | Both support fork-with-context. |
| Named teammates / Agent Teams | Agent Teams (named parallel teammates) | ✅ root-thread tree + `agent_nickname`/`agent_role`; `/agent` to switch/steer | Comparable. |
| Message passing between agents | `SendMessage(to:…)` | ✅ `send_message` (no turn) / `followup_task` (turn) / `interrupt` — mailbox model | Comparable; Codex distinguishes turn vs no-turn. |
| Wait / consolidate results | implicit (final message returned) | ✅ `wait_agent` (explicit, "use sparingly"), plus auto-consolidation | Codex is explicit. |
| Resume/close teammates | continue via SendMessage | ✅ `close_agent` / `resume_agent` / `list_agents` | Codex has explicit close+resume. |
| Lifecycle hooks | `SubagentStop` hook | ✅ `subagent-start` + `subagent-stop` hooks | Codex has start too. |
| Concurrency / depth caps | (soft) | ✅ `agents.max_threads` (6), `agents.max_depth` (1) | Codex exposes hard config. |
| Fan-out primitive | scripted `Agent` calls / workflows | ⚠️ `spawn_agents_on_csv` (experimental) + `enable_fanout` (dev/off) | Codex primitive exists but young. |
| Cloud/remote parallel tasks | (background/remote agents) | ✅ `codex cloud exec --attempts N` (best-of-N), list/status/diff/apply | Both have a cloud story. |
| Headless scripting | `claude -p` / SDK | ✅ `codex exec --json`, `codex mcp-server` + Agents SDK | Codex MCP-server path is well-documented. |
| Sandbox inheritance to children | yes | ✅ inherits; per-agent `sandbox_mode` override | Comparable. |

**Net:** for the features lore depends on (spawn, name, message, wait, custom defs, hooks, sandbox), **Codex 0.142.5 is roughly at parity with Claude Code**, with a couple of things still maturing (fan-out primitive, `multi_agent_v2`, orchestrator).

---

## Implications for the lore port ("subagent-spawn" adapter binding)

Recommended design, in priority order:

1. **Primary binding → native `spawn_agent` family.** Map lore's `/lr:spawn-teammate` and consult/attach flows onto native Codex tools:
   - spawn teammate → `spawn_agent` (pass the lore agent's boot prompt as the task; set `task_name` to the lore agent name so canonical paths read `/root/<lead>/<agent>`).
   - lore agent identity → a generated **`.codex/agents/<agent>.md`** def per lore agent (`name`, `description`, `developer_instructions` = the agent-boot text, `model`/`model_reasoning_effort`/`sandbox_mode` from lore config, `mcp_servers`/`skills.config` for lore tooling). This is the cleanest analog to how lore agents map to Claude subagent defs; generate these in `/lr:register-repo`.
   - teammate messaging → `send_message` / `followup_task`; gather → `wait_agent`; teardown → `close_agent`.
   - **Guardrail:** these tools are unreachable from inside `functions.exec`, so the adapter must express spawning as *instructions to the model*, not as a shell command it runs. A lore command that spawns must yield to a model turn.
2. **Fallback binding → inline (single-agent) execution.** When `multi_agent` is disabled, or depth would exceed `agents.max_depth` (default 1 — note this is *shallow*; lore's consult-a-consultant chains may hit it), degrade gracefully to running the sub-task in the current thread (the "inline fallback" the lead flagged). Detect capability with `codex features list | grep multi_agent`. Honor `agents.max_threads` (default 6) as the teammate cap.
3. **Batch/headless binding → `codex exec --json`** (or `codex mcp-server` + a thin orchestrator) for non-interactive lore runs (CI, scheduled `/lr:finalize` fan-out, DF file passes). Use **git worktrees/branches per worker** to avoid write collisions (matches lore's existing worktree isolation). Reserve **Cloud** (`codex cloud exec --attempts`) for best-of-N or heavy isolated jobs.
4. **When each is worth it:**
   - Interactive, context-sharing, message-passing co-work → **native `spawn_agent`** (don't emulate).
   - Deterministic, auditable, reproducible pipelines a human reviews → **`mcp-server` + Agents SDK** (Traces).
   - Pure parallel throughput over many independent items → **`codex exec --json` queue** or **CSV fan-out / Cloud**.
   - Don't build **nested `codex exec` recursion** for coordination — no mailbox, no consolidation, can't reach native tools.
5. **Hooks:** lore's teammate lifecycle logic can bind to `subagent-start` / `subagent-stop` hooks (same shape as Claude's `SubagentStop`), so the adapter for hook bindings can be near-shared.

---

## How to re-verify locally (before coding the adapter)

Safe, read-only, no network/login/session:
```
codex features list | grep -E 'multi_agent|fanout|goals|collaboration'
codex --help ; codex cloud --help ; codex exec --help ; codex mcp-server --help
codex debug prompt-input  # renders the model-visible tool/prompt list as JSON — best way to see the LIVE spawn_agent schema
strings <codex-binary> | grep -iE 'spawn_agent|wait_agent|send_message|close_agent|list_agents|multi_agents'
```
The binary lives at `/usr/local/Caskroom/codex/0.142.5/codex-x86_64-apple-darwin` (symlinked from `/usr/local/bin/codex`). `codex debug prompt-input` is the authoritative way to capture the exact JSON tool schemas the model sees in your build (I did not run it this session to avoid any session side effects; recommend it as the next step).

---

## Open questions / unverified

- **Exact JSON schema** of each tool (`spawn_agent` args beyond `task_name`; `wait_agent` targets/timeout/pollInterval; `send_message` items vs legacy plain-text) — inferred from strings, not dumped. Resolve via `codex debug prompt-input`. **[unverified]**
- **`orchestrator` layer** — what it governs (Cloud? app-server? a higher-level planner over subagents?), its phase machine, and `orchestrator.mcp.enabled`. Present in binary, purpose not confirmed. **[unverified]**
- **`multi_agents` (v1) vs `multi_agents_v2`** — both modules ship; which tools route to which, and what flips when `multi_agent_v2`/`enable_fanout` are enabled. **[unverified]**
- **Depth default = 1** — whether lore's consult/attach chains need `agents.max_depth` raised, and interaction with `max_threads`. **[unverified]**
- **Version introduction points** — 0.142.5 has it stable-on; the exact release where `multi_agent` flipped to stable is not pinned (docs say only "current releases enable subagent workflows by default"). **[unverified]**
- **Public-doc vs installed-build drift** — 0.142.5 is ahead of what my Jan-2026 training and some public pages reflect; treat binary probes as source of truth. **[caveat]**

---

## Sources

1. **[BINARY]** Local `codex --version` / `codex --help` / subcommand help (`cloud`, `exec`, `mcp`, `mcp-server`, `app-server`, `exec-server`, `debug`, `plugin`) — codex-cli 0.142.5. Accessed 2026-07-05.
2. **[BINARY]** `codex features list` — full feature-flag table incl. `multi_agent=stable/true`, `multi_agent_v2`, `enable_fanout`, `goals`, `collaboration_modes`. Accessed 2026-07-05.
3. **[BINARY]** `strings` over `/usr/local/Caskroom/codex/0.142.5/codex-x86_64-apple-darwin` — tool descriptions (`spawn_agent`, `followup_task`, `send_message`/`send_input`, `wait_agent`, `interrupt_agent`, `close_agent`, `resume_agent`, `list_agents`), Rust symbols `codex_core::tools::handlers::multi_agents{,_v2}::*`, thread-tree fields, hooks, delegation doctrine, embedded base instructions / AGENTS.md spec. Accessed 2026-07-05.
4. **[DOCS]** Subagents – Codex | OpenAI Developers — https://developers.openai.com/codex/subagents (and `.md`): custom agent defs, `~/.codex/agents` & `.codex/agents`, `[agents]` config, built-ins, `/agent`, `spawn_agents_on_csv`, sandbox inheritance, parallel consolidation. Accessed 2026-07-05.
5. **[DOCS]** CLI – Codex | OpenAI Developers — https://developers.openai.com/codex/cli: subagents overview, `exec` scripting, `mcp-server` mode. Accessed 2026-07-05.
6. **[DOCS]** Use Codex with the Agents SDK — https://developers.openai.com/codex/guides/agents-sdk: `codex mcp-server`, `MCPServerStdio`, `codex()` / `codex-reply()` tools, sequential handoffs + parallel workflows, Traces. Accessed 2026-07-05.
7. **[COMMUNITY]** GitHub Discussion #3898 "orchestrate sub-agents … queue/worker pattern" — https://github.com/openai/codex/discussions/3898: OpenAI-staff guidance to use native subagents for interactive work vs `codex exec --json` workers + git worktrees for batch; MCP as integration boundary not scheduler. Q Sep 2025 / A Jun 2026. Accessed 2026-07-05.
8. **[COMMUNITY]** GitHub Issue #11701 "Subagent configuration and orchestration" (openai/codex) — corroborates config/orchestration surface. Accessed 2026-07-05 (title-level only).
9. **[COMMUNITY]** Firecrawl blog "Multi-Agent Orchestration With Codex"; RoggeOhta/awesome-codex-cli (subagents/plugins list) — background corroboration, lower weight. Accessed 2026-07-05.
10. **[BINARY/DOCS]** Codex self-knowledge manual referenced by the binary — https://developers.openai.com/codex/codex-manual.md (setup, skills, plugins, MCP, hooks, AGENTS.md, automations). Not fully fetched; noted for follow-up. Accessed 2026-07-05.
