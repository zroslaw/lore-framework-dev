# Lore Framework → Codex Engine Binding — Design

Design draft, 2026-07-05. Grounded in: `codex-multiagent-research.md` (web/docs),
`codex-multiagent-live-capture.md` (binary ground-truth, `codex-cli 0.142.5`), and the actual
fan-out docs (`process-merge.md`, `recall.md`, `lore-search.md`, `consult.md`).
Status: **proposed, not applied.** Live plugin untouched.

## 0. The `docs/engines/` convention (how a profile is selected)

- The framework ships one profile per engine: `docs/engines/claude.md` (reference) and
  `docs/engines/codex.md`. Every profile fills the **same five bindings**; only values differ.
- **Selection (new boot step 0, in `agent-boot.md`):** the agent **self-locates** its framework
  root from this file's own path, then infers the engine from that path:
  - root under `~/.claude/plugins/…` or loaded via `--plugin-dir` → **claude**
  - root under `~/.codex/plugins/…` → **codex**
  - else → default to claude, warn.
  Then it **reads the matching `docs/engines/<engine>.md`** and keeps those binding values as
  standing context for the session.
- **Precedence:** if any later step conflicts with a profile value, the profile wins for that step.

## 1. The five bindings — Codex values

| # | Binding | Claude | **Codex** |
|---|---|---|---|
| 1 | **framework-root** | `${CLAUDE_PLUGIN_ROOT}` | **empty** — self-locate; inject the resolved absolute root everywhere a doc path is needed (incl. into subagent briefs). |
| 2 | **invocation-syntax** | user types `/lr:<skill>`; UI expands | Codex installs SKILL.md skills natively (our ~26 landed). **User** invokes via Codex's own skill mechanism. **Agent-initiated / headless:** do NOT type `/lr:…` (falls to shell) — read `docs/<skill>.md` and follow it. |
| 3 | **subagent-spawn** | `Agent` tool, N parallel calls in one message | **`spawn_agent`** (native, ON by default). Role `worker` (write) / `explorer` (read-only). **Expressed as in-session model instructions, never a shell call.** Parallel = multiple `spawn_agent`; collect with `wait_agent`. Caps: `max_threads≈6`, `max_depth=1`. |
| 4 | **memory-file** | `CLAUDE.md` | **`AGENTS.md`** (apply with `test_18_init` updated in lockstep). |
| 5 | **runtime-bounding** | Bash-tool timeout | No wrapper flag; bounded by Codex sandbox / `agents.job_max_runtime_seconds`. Neutralize timeout prose. |

## 2. Capability gate (Tier C — skip, don't port)

- **teammate-detection.** Boot step 5's `ps -o args= -p $PPID` is **sandbox-blocked** on Codex
  (`operation not permitted`). Profile states: treat any error as "not a teammate," continue as
  host. Claude-only Agent-Teams/spawn-teammate features stay gated off (but see §4 — Codex now
  *could* host them natively; that's a future upgrade, not this binding).

## 3. Fan-out sites — how each lands on Codex

All three fan-out procedures share one shape today: *"spawn one `general-purpose` subagent per
active agent (parallel, one message, multiple Agent calls); each subagent **boots as its agent**
per `${CLAUDE_PLUGIN_ROOT}/docs/agent-boot.md` and runs the procedure scoped to itself; host
collects summaries."*

**Neutralization (framework side):** replace the hard-coded "Agent tool / single message /
`${CLAUDE_PLUGIN_ROOT}`" mechanics in these docs with a pointer to the **subagent-spawn binding**
and the **framework-root** value from the active profile. The *procedure* stays engine-agnostic;
the *mechanism* comes from the profile.

| Site | Doc | Codex expression |
|---|---|---|
| **merge** | `process-merge.md` | Host self-locates root `R`. For each agent: `spawn_agent` role `worker`, brief = _"Boot as `<name>` (repo `<path>`) per `R/docs/agent-boot.md`, run `R/docs/process-merge.md` scoped to yourself, return a short summary, do not commit."_ Spawn all in parallel; `wait_agent` to collect; host aggregates + commits once. |
| **recall** | `recall.md` / `lore-search.md` | Same shape, role `explorer` (read-only), brief points at `R/docs/lore-search.md`. Collect + synthesize. |
| **consult** | `consult.md` | Single `spawn_agent` worker booted as the consulted agent; returns synthesis + file pointers; closed after. |

Notes:
- **Depth-1 is fine.** These are host→children fan-outs; subagents don't re-spawn. No conflict
  with `max_depth=1`.
- **`max_threads≈6`.** Fan-outs are per active-agent — typically 1–3. If a future session had
  >6 agents, chunk the spawn. (`log`/note the chunking; don't silently cap.)
- **framework-root into the brief.** Because `${CLAUDE_PLUGIN_ROOT}` is empty on Codex, the host
  must inline the resolved absolute `R` into each brief. Already validated on haiku that the
  spawned model substitutes an embedded absolute path correctly.
- **procedure steps inline, not a doc pointer (per §4).** On Codex the brief carries the
  procedure *steps* the host read from `R/docs/process-merge.md`, rather than telling the
  subagent to open that doc. The subagent still boots as its agent (identity load). The table
  briefs above show the Claude phrasing ("run `R/docs/process-merge.md` scoped to yourself");
  the Codex profile overrides it to the host-reads-and-passes form.

## 4. The "who reads the doc" tension — DECIDED (profile-level override)

Codex's system prompt says: *"the main agent must read each required instruction/reference file
itself; do not delegate reading, summarizing, or interpreting **skill** instructions to a
subagent."* Lore's fan-out has each subagent read the **procedure** doc itself.

**Decision:** keep the **shared procedure docs unchanged** (engine-agnostic). Put the Codex
handling **in `docs/engines/codex.md` as a subagent-spawn override note**:

> On Codex, the **host (main agent) reads the procedure doc** (`process-merge.md` /
> `lore-search.md` / `consult.md`) itself, then **passes the procedure steps inline in each
> subagent's brief** — rather than instructing the subagent to open the procedure doc. The
> subagent still **boots as its agent** (loads its own `role.md` + `lore-context.md`): that is
> *identity loading*, not skill-reading, and stays. Only "read the procedure yourself" moves to
> the host.

Why this is the right shape:
- Engine-specific behavior lives in the engine profile; the shared procedure stays clean — the
  whole point of the `docs/engines/` convention.
- It satisfies Codex's convention (main agent reads instructions; subagent does task work).
- No staleness: the host reads the *current* procedure doc at run time and passes it, so it
  tracks doc edits automatically.

**Scope of what it solves:** the *procedure-doc-reading* half only. Boot-as-self identity
loading is untouched (permitted). And this is still a **predicted** tension — a live Codex merge
test confirms whether the override was even necessary; if `spawn_agent` workers happily read the
procedure doc themselves, the note is a belt-and-suspenders safeguard, not a fix.

## 5. Deferred (not in this binding)

- **`multi_agent_v2`** — under development, OFF by default. Design to stable `multi_agent`. Don't
  couple. (Probe later to learn what it adds.)
- **Native Codex teams for `spawn-teammate`.** Codex's `InterAgentCommunication` (addressed
  messaging, handoff, wake-on-message) means the *Claude-only* spawn-teammate feature could
  eventually be ported natively. Out of scope now; noted as a real future upgrade.
- **`codex exec --json` / `mcp-server` batch spawning.** Only relevant for headless/CI
  orchestration (the one place shell-driven spawning is valid). Not needed for interactive
  finalize/recall.

## 6. Validation plan (empirical, before applying to the live plugin)

Run each on a real (non-headless) Codex session against a throwaway repo copy, model = the
default and at least one stronger tier:
1. **framework-root + engine-select** — boot picks `codex.md`, resolves root, no `${...}` leakage.
2. **merge fan-out** — a real `spawn_agent` worker boots-as-self, reads `R/docs/*`, returns a
   summary, host aggregates + commits once. Confirms §4 reading (a) vs (b).
3. **recall fan-out** — `explorer` workers, correct topics, synthesis.
4. **AGENTS.md** — `test_18_init` passes against `AGENTS.md`.
Only after these pass on Codex do we apply to the real framework and run the full suite.

## 7. Order of work (lands as one reviewed change set)

1. Tier-A mechanical (already staged): framework-root self-location + defer-clarity.
2. `docs/engines/` convention + `claude.md` (reference) + `codex.md` (from this design).
3. Boot step 0 (engine-select) into `agent-boot.md`.
4. Neutralize fan-out mechanics in `process-merge.md` / `recall.md` / `lore-search.md` /
   `consult.md` → point at the binding.
5. `CLAUDE.md → AGENTS.md` + `test_18_init` in lockstep.
6. Timeout-prose neutralization (`auto-pull.md`, `conventions.md`).
7. Validate on Codex (§6) → apply to real framework → full suite → show tests → commit.

## See also (lore)
`multi-engine-portability-direction.md`, `claude-coupling-inventory-and-port-tiers.md`,
`port-landing-next-steps.md`, `framework-root-self-location-validated.md`,
`codex-cli-plugin-loading-findings.md`; workdir: `codex-multiagent-research.md`,
`codex-multiagent-live-capture.md`.
