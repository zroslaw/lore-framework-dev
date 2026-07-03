# Draft — Porting Lore Framework to Cursor (IDE agent + Cursor CLI)

Status: DRAFT for a dedicated design session. Written 2026-07-02 from a portability assessment
session (docs verified against cursor.com as of that date; Cursor 2.4 era). Companion draft:
`draft-port-codex.md`. **Phase 0 is shared between the two drafts — one body of work in the
plugin repo; whichever port session runs first executes it.**

## Goal

Same lore-agent experience in Cursor against the same team-shared agent repos. Claude Code
remains the major version. Cursor is the higher-adoption target of the two ports (IDE-native
audience) and, notably, has the **richest declarative primitives** of the three engines —
skills with invocation control, markdown-defined subagents, worktree-isolated parallel agents.

## Verified platform capability map (2026-07, Cursor 2.4)

| Capability | Cursor support | Notes |
|---|---|---|
| Skills | ✅ `SKILL.md`, Agent Skills standard | Discovered from `.agents/skills/` and `.cursor/skills/` (project), `~/.agents/skills/` and `~/.cursor/skills/` (user). Recursive/nested discovery. `scripts/`, `references/`, `assets/` supported |
| Skill frontmatter | ✅ `name`, `description`, plus `paths` (glob scoping), **`disable-model-invocation`**, `metadata` | `disable-model-invocation: true` ≈ classic slash command — exactly right for lifecycle skills |
| Invocation | ✅ implicit by description, explicit `/name` in Agent chat | `/` prefix like Claude Code (nicer than Codex's `$`) |
| Commands | ✅ `.cursor/commands/*.md` (project), `~/.cursor/commands/` (user) | Legacy-ish; `/migrate-to-skills` converts commands→skills. Prefer skills |
| Subagents | ✅ **declarative**: markdown files in `.cursor/agents/` (project) or `~/.cursor/agents/` (user); own context, custom system prompt, tool access; parallel | Best subagent story of the three engines for our merge pattern |
| Parallel/background agents | ✅ up to 8, auto-managed git worktrees | Composes with our worktree convention — verify interplay |
| AGENTS.md | ✅ supported (alongside `.cursor/rules`) | `/lr:init` target |
| MCP | ✅ `mcp.json`, env/OAuth auth | `lr-wait` ports as-is |
| Distribution | ✅ skills installable **from GitHub repos** via Customize > Rules | Closest thing to a marketplace among the ports |
| Headless | ✅ Cursor CLI (`cursor-agent`) | For background/finalize automation later |

## Dependency → target mapping

| Framework dependency | Cursor target | Effort |
|---|---|---|
| Agent repos (markdown+git) | unchanged | none |
| `skills/*/SKILL.md` | same shape; add `disable-model-invocation: true` to lifecycle skills (boot, finalize, merge, update, create-*) so they behave as explicit commands | low |
| `docs/*.md` + `${CLAUDE_PLUGIN_ROOT}` | `<framework-root>` convention (Phase 0, shared) | medium |
| `/lr:boot` naming | `/lr-boot` (lowercase name = folder; colon likely invalid) | low |
| Registered `/lr-<agent>-agent` shortcuts | generated skills with `disable-model-invocation: true`, or `.cursor/commands/` files; decide in session | low |
| Subagent fan-out (merge/consult/recall) | **generated `.cursor/agents/lr-merge.md`** (and siblings) — declarative subagent whose system prompt is the boot-as-target-agent brief | medium |
| CLAUDE.md `/lr:init` payload | AGENTS.md marker block (shared Phase 0); optionally also a `.cursor/rules` always-apply pointer | low |
| `lr-wait` MCP + `lr-emit` | `mcp.json` registration | low |
| Bash timeout parameter | verify Cursor terminal-tool timeout semantics; else fail-fast env vars recipe | low |
| `ps $PPID` teammate detection | skip — engine-gated | none |
| Agent Teams / Workflow (DF/ULA) / hooks | out of scope — Tier 2 Claude-first. Note: Cursor's 8-way parallel agents may *eventually* host a spawn-teammate analog — park, don't design | none |

## Phase 0 — engine-neutral groundwork (shared; see `draft-port-codex.md` for full detail)

1. `docs/engines/` adapter convention (five bindings: invocation, subagent, timeout,
   memory file, framework root).
2. `${CLAUDE_PLUGIN_ROOT}` → `<framework-root>` term.
3. `/lr:init` targets AGENTS.md.
4. Feature-tiering README section.

## Phase 1 — minimum viable Cursor port

1. **Packaging.** Repo-level install: clone lore-framework and symlink `skills/` into
   `~/.agents/skills/` (or `.agents/skills/` in the workspace). Verify Cursor's recursive
   discovery accepts the symlink; verify folder-name/`name` matching against our `lr-` names.
   Also test the **GitHub-install path** (Customize > Rules → install from repo) — if it works
   on the framework repo directly, it becomes the headline install instruction.
2. **Frontmatter pass.** Add `disable-model-invocation: true` to every lifecycle skill.
   Leave `recall`/`consult` implicit-invokable? — tempting (the agent auto-recalling lore when
   relevant is arguably *better* UX than Claude Code offers today), but risks surprise
   token/tool use. Decide in session; default to explicit-only for v1 parity.
3. **Sandbox/trust guidance** in `docs/engines/cursor.md`: boot auto-pull, finalize
   commit+push need terminal + network approval; document recommended settings and the
   degraded-mode behavior when denied.
4. **Walk the Tier-1 lifecycle** manually in the IDE agent: boot → recall → reflect →
   merge (inline fallback first) → summarize → finalize.
5. **`lr-wait`** via `mcp.json`; verify stdio server startup inside Cursor.

## Phase 2 — orchestration + Cursor-specific strengths

1. **Declarative merge subagent.** Generate `.cursor/agents/lr-merge.md` (system prompt =
   "boot as the named agent per agent-boot.md, run process-merge.md scoped to yourself,
   return a summary; do not commit"). Host skill fans out one per active agent, parallel.
   This is *cleaner* than Claude Code's prompt-assembled general-purpose subagent — the
   pattern may back-port. Same for consult/recall if fidelity is good.
2. **Worktree interplay.** Cursor's parallel agents auto-create worktrees; our worktree
   convention expects top-level checkouts on default branches with feature work under
   `.worktrees/`. Verify no collision (where does Cursor put its worktrees? does finalize
   from inside one behave per `auto-pull.md` § Worktrees?). Document in the adapter.
3. **`paths` scoping** — scope generated per-agent shortcut skills to the agent repo's
   directory via `paths:` so they only surface when relevant. Nice-to-have.
4. **Migrations/version-check fidelity** on Cursor's default model(s) (Composer et al.);
   simplify prose where it degrades.

## Phase 3 — distribution & validation

1. Install docs; decide primary install channel (GitHub-install vs symlink).
2. **Mixed-team test**: one repo, alternating Claude Code / Cursor sessions; concurrent
   finalize collision → resolve-conflicts; verify session summaries interleave cleanly.
3. **Cursor CLI smoke test** — Tier-1 lifecycle headless; groundwork for background
   finalize automation later.
4. Model-fidelity report → feed the simplification theme.

## Open questions for the session

- Does Cursor skill discovery accept symlinks? Does GitHub-install work for a repo whose
  skills live in a `skills/` subdirectory (not repo root)?
- Implicit invocation policy: which skills (if any) should the model be allowed to invoke
  on its own? (`recall` is the interesting candidate.)
- Do `.cursor/agents/` subagent definitions accept dynamic parameters (agent name/path),
  or does merge need one generated definition per lore agent?
- Cursor model lineup fidelity on long procedures — empirical.
- Where do Cursor sessions' equivalents of session JSONLs live (for the parked
  session-archival direction), if anywhere?
- Rules vs skills split: does anything of ours belong in `.cursor/rules` (always-apply),
  e.g. a one-liner CWD-safety/portable-shell reminder? Default: no — keep everything in skills.

## Risks

- **Model fidelity** (dominant, same as Codex): prose procedures on non-Claude models.
  Mitigation identical: test, script critical paths, simplify.
- **Worktree collision** between Cursor's auto-worktrees and our convention — could confuse
  boot discovery (nested checkouts are invisible to discovery by design). Needs Phase 2.2
  verification before advertising parallel-agent use.
- **Implicit skill invocation surprises** — an eager model booting agents or finalizing
  unprompted. Mitigation: `disable-model-invocation: true` everywhere in v1.
- **Two config surfaces** (`.agents/` standard + `.cursor/` native) — pick `.agents/` for
  standard-alignment, fall back to `.cursor/` only where the standard path underperforms.

## See also

- `draft-port-codex.md` — companion draft; owns the shared Phase 0 write-up.
- `worktrees-convention.md`, `auto-pull.md` § Worktrees — the interplay to verify.
- `merge-in-booted-subagents.md` — the pattern Phase 2.1 re-expresses declaratively.
