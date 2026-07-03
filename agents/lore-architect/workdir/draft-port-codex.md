# Draft — Porting Lore Framework to OpenAI Codex (CLI + IDE extension)

Status: DRAFT for a dedicated design session. Written 2026-07-02 from a portability assessment
session (docs verified against developers.openai.com as of that date). Companion draft:
`draft-port-cursor.md`. Shared groundwork (Phase 0) is identical in both drafts by design —
do it once, in the plugin repo, before either port.

## Goal

Same lore-agent experience on Codex: boot an agent, work, recall/consult, finalize —
against the **same team-shared agent repos** Claude Code users push to. Claude Code remains
the major version; Codex is a Tier-1-core port for adoption. The differentiator to preserve:
**mixed-engine teams sharing one knowledge substrate** (no competing product does this).

## Verified platform capability map (2026-07)

| Capability | Codex support | Notes |
|---|---|---|
| Skills | ✅ `SKILL.md`, open Agent Skills standard (agentskills.io) | Lives in `.agents/skills/` (repo), `~/.agents/skills/` (user), `/etc/codex/skills` (admin). Optional `scripts/`, `references/`, `assets/`, `agents/openai.yaml`. Custom prompts are **deprecated in favor of skills**. |
| Skill invocation | ✅ `/skills` picker, `$skillname` inline, implicit by description | `$` prefix, not `/lr:` — naming must adapt |
| AGENTS.md | ✅ native, layered global→project | Direct replacement for the `/lr:init` CLAUDE.md payload |
| MCP | ✅ `~/.codex/config.toml` `[mcp_servers]`, stdio + streaming HTTP; `codex mcp` CLI | `lr-wait` ports as-is |
| Subagents | ✅ explicit-only ("Codex only spawns subagents when you explicitly ask") | Own model+tool work; more tokens. No declarative agent files like Cursor's |
| Headless | ✅ `codex exec` | Enables scripted fan-out as a subagent alternative |
| Plugin/marketplace | Partial — "plugins" bundle skills + MCP config; no central marketplace | Distribution is git-clone/copy based |
| Sandbox / approvals | ⚠️ default sandbox restricts network + writes outside workspace | **Auto-pull, finalize push, workspace-sync all need network.** Must document required config |

## Dependency → target mapping

| Framework dependency | Codex target | Effort |
|---|---|---|
| Agent repos (markdown+git) | unchanged | none |
| `skills/*/SKILL.md` thin pointers | same shape; standard-conformant frontmatter (`name` lowercase = folder) | low |
| `docs/*.md` shared procedures | unchanged content; root resolution changes (see Phase 0) | low |
| `${CLAUDE_PLUGIN_ROOT}` | **no equivalent** → framework-root resolution convention (Phase 0) | medium |
| `/lr:boot` etc. | `$lr-boot` / `/skills` picker; `lr:` colon likely invalid in skill names | low (rename map) |
| Registered `/lr-<agent>-agent` shortcuts | generated per-agent skills in `.agents/skills/` or repo-level AGENTS.md pointers | low |
| Subagent fan-out (merge/consult/recall) | explicit subagent request in prose; fallback: sequential inline; option: `codex exec` fan-out script | medium |
| CLAUDE.md `/lr:init` payload | AGENTS.md (same marker block) | low |
| `lr-wait` MCP + `lr-emit` | `config.toml` registration | low |
| Bash-tool timeout parameter (auto-pull et al.) | Codex shell has no per-call timeout param → rely on fail-fast env vars (already the standalone-script recipe in `conventions.md`) | low |
| `ps $PPID` teammate detection | skip — no Agent Teams on Codex | none (gate by engine) |
| Agent Teams / spawn-teammate, Workflow (DF/ULA), hooks | out of scope — Tier 2, Claude-only | none |

## Phase 0 — engine-neutral groundwork (shared with Cursor port; do first, in `lore-framework/`)

1. **Engine-adapter convention.** New `docs/engines/` with one file per engine
   (`claude-code.md`, `codex.md`, `cursor.md`). Each declares exactly five bindings:
   (a) skill invocation syntax, (b) how to spawn a subagent (or "inline fallback"),
   (c) how to bound a command's runtime, (d) memory-file target (CLAUDE.md / AGENTS.md),
   (e) framework-root resolution. Procedure docs replace Claude-specific phrases
   ("your Bash tool's timeout parameter", "single message with multiple Agent tool calls",
   "spawn a `general-purpose` subagent") with adapter references. Bounded sweep — grep the
   docs for the known phrases; ~10–15 sites.
2. **Framework-root resolution.** Replace `${CLAUDE_PLUGIN_ROOT}` with a defined term
   `<framework-root>`: "the directory containing `VERSION`, resolved relative to the invoked
   SKILL.md (two levels up)". Claude adapter binds it to `${CLAUDE_PLUGIN_ROOT}`; Codex/Cursor
   bind it to the skill-tree install location. Keeps single-canonical-source: docs stay put.
3. **AGENTS.md as canonical init target.** `/lr:init` writes AGENTS.md (all three engines read
   it); Claude Code keeps CLAUDE.md compatibility (write both, or a one-line CLAUDE.md pointer
   to AGENTS.md — decide in session).
4. **Feature tiering doc.** README section: Tier 1 portable core (boot, recall, consult,
   reflect, merge, summarize, finalize, check, update, workspace-sync, list-*, create-*,
   init, pull-lore), Tier 2 Claude-first (attach*, spawn-teammate, wait, df-*, register-repo
   shortcuts). (*attach is likely portable but verify guest-boot mechanics per engine before
   promising it.)

## Phase 1 — minimum viable Codex port

1. **Skill-tree packaging.** Decide: (a) users `git clone` lore-framework into
   `~/.agents/skills/lore-framework/` with skills discoverable via nesting, or (b) an
   `scripts/install-codex` that symlinks/copies `skills/` into `~/.agents/skills/`.
   Verify how Codex handles nested skill dirs and whether folder-name-must-match-`name`
   forces a flatter layout. Prefer symlink: one checkout, auto-updates via git pull.
2. **Skill naming.** `lr:boot` → `lr-boot` (etc.). Keep the `lr-` prefix for namespace safety
   in the flat `$skillname` space. The Claude plugin keeps `lr:` — the adapter records the map.
3. **Sandbox/approvals guidance.** A `docs/engines/codex.md` section: recommended
   `config.toml` (workspace-write sandbox with network enabled, or approval-on-request),
   because boot auto-pull, finalize commit+push, and workspace-sync are network operations.
   Degraded-mode behavior (already designed — auto-pull never blocks boot) covers denials.
4. **Port the Tier-1 core skills** and walk the full lifecycle manually: boot → work →
   recall → reflect → merge (inline sequential fallback) → summarize → finalize → push.
5. **`lr-wait` registration doc** — `[mcp_servers.lr-wait]` stanza; `lr-emit` unchanged.

## Phase 2 — orchestration + parity

1. **Subagent merge.** Prose for "explicitly request a subagent per active agent"; measure
   fidelity. If flaky, ship `scripts/merge-fanout` using `codex exec` per agent (deterministic,
   matches the direction of moving critical paths into scripts).
2. **Consult / recall fan-out** — same treatment.
3. **Migrations/version-check** on Codex-driven boots — verify the prose walk holds on
   codex models; simplify if fidelity is poor (feeds the parked simplification theme).
4. **`/lr:check`** run + fix engine-assumption findings.

## Phase 3 — distribution & validation

1. Install docs (README section per engine), Codex "plugin" bundle if it earns its keep.
2. **Mixed-team test**: same agent repo, alternating Claude Code and Codex sessions,
   concurrent finalize collision → resolve-conflicts path.
3. Model-fidelity report: which procedures degraded on Codex models, what was hardened.

## Open questions for the session

- Does Codex skill discovery accept a symlinked/nested tree? (Determines packaging.)
- Skill-name collision policy in the flat `$name` space — is `lr-` prefix enough?
- Does Codex implicit skill invocation risk *unwanted* boot/finalize triggering?
  (`disable-model-invocation` equivalent? Cursor has it; check Codex.)
- How faithful are codex models on the 96-line merge procedure? (Empirical; drives
  script-vs-prose decisions.)
- Version/migration stamping: repos touched by multiple engines — stamp is engine-neutral
  (framework VERSION), but *cache-clear footers* are Claude-specific; release notes may need
  per-engine upgrade sections.
- Where do generated per-agent shortcut skills live on Codex, and are they worth it at all
  (vs `$lr-boot <name>`)?

## Risks

- **Model fidelity** is the dominant risk — the framework is prose executed by the model.
  Mitigation: test each Tier-1 procedure, prefer scripts for critical paths, simplify prose.
- **Sandbox friction**: default-deny network makes the freshness contracts (auto-pull/push)
  silently degrade. Mitigation: loud degraded-mode warnings (already designed) + setup doc.
- **Standard drift**: agentskills.io is young; Codex's `agents/openai.yaml` extension hints at
  vendor forks. Keep the adapter layer thin so drift lands there, not in procedures.

## See also

- `draft-port-cursor.md` — companion; shares Phase 0.
- `framework-improvements-backlog.md` — simplification theme (fidelity pressure aligns with it).
- `conventions.md` § Portable Shell — the standalone-script timeout recipe Phase 1.3 leans on.
