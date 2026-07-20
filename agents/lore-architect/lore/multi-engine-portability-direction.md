# Multi-Engine Portability (Codex, Cursor) — Major Direction

User-raised 2026-07-02. A major new direction: Tier-1-parity ports of the lore framework to **OpenAI Codex** and **Cursor**, alongside Claude Code. Claude Code remains the major version — this is not a migration, it's giving mixed-engine teams a way to **share one team-shared agent repo** regardless of which coding agent each member runs (see `similar-projects-landscape.md` for why this is a real differentiator, not just nice-to-have). Two detailed workdir drafts exist for dedicated future design sessions: `workdir/draft-port-codex.md` and `workdir/draft-port-cursor.md`. This topic is the anchor pointer + key findings — the same relationship the drafts have to it that `workdir/draft-lr-dev.md` has to `lr-dev-direction.md`. Do not duplicate the phased plans here.

## Why the timing is right

The industry converged on lore-framework's own primitives since the framework's early design. **SKILL.md** is now an open standard (agentskills.io), and Codex, Cursor, and Claude Code all support it (reportedly 30+ tools total). Codex has *deprecated* its old custom-prompts mechanism in favor of skills. **AGENTS.md** is natively read by both Codex and Cursor. **MCP** is supported by both — `lr-wait` (v18, see `wait-primitive-feature.md`) ports with no redesign. This means the port is mostly **packaging, not redesign** — a year ago it would have been much harder.

## What's already engine-agnostic

The knowledge substrate itself — agent repos, `lore-repo.md`, `role.md`, `lore/`, `lore-context.md`, `sessions/`, git as the metadata/conflict-resolution layer — has no Claude Code dependency at all. A repo written entirely from Claude Code sessions is already readable and writable from Codex or Cursor today, by hand. The port work is entirely about giving each engine the same *procedural* affordances (boot, reflect, merge, finalize) that Claude Code gets via skills.

## Architectural levers (apply to both ports, and to Claude Code doc hygiene now)

- **`docs/engines/` adapter convention** — one file per engine declaring exactly five bindings: skill-invocation syntax, how to spawn a subagent (or "inline fallback"), how to bound a command's runtime, the memory-file target, and framework-root resolution. Procedure docs stop hardcoding Claude-specific phrases ("your Bash tool's timeout parameter," "spawn a `general-purpose` subagent") and reference the adapter instead. This is a **now-visible category of Claude-Code-specific leakage in otherwise-portable prose**, worth fixing even before any port ships, purely for doc hygiene — roughly 10-15 sites found by grep.
- **`<framework-root>`** replaces `${CLAUDE_PLUGIN_ROOT}` as the doc-level term; each engine adapter binds it to whatever that engine calls its equivalent (Claude: the plugin install path; Codex/Cursor: the skill-tree checkout location). **Empirically validated on Claude/haiku (2026-07-04)** via self-location ("the directory containing the `VERSION` file," resolved by a one-line rule at the top of each `SKILL.md`) — 18/19 lifecycle first pass, subagent fan-out clean, `stream-json` trace confirming haiku resolved the root by Reading `VERSION` rather than leaning on env-var expansion. This is the biggest single coupling (~55% of hits) and now the most de-risked. See `framework-root-self-location-validated.md`, `claude-coupling-inventory-and-port-tiers.md`.
- **AGENTS.md becomes the canonical `/lr:init` target** (all three engines read it); CLAUDE.md compatibility for Claude Code decided per-session, likely a thin pointer.
- **Explicit Tier 1 / Tier 2 split** — Tier 1 portable core: boot, recall, consult, reflect, merge, summarize, finalize, check, update, workspace-sync, list-*, create-*, init, pull-lore. Tier 2 Claude-first or still-unvalidated: attach (verify per-engine before promising), spawn-teammate, wait, df-*, register-repo shortcuts. Codex shortcut shape is now designed (personal skills under `~/.codex/skills/`) but generation/removal remains an implementation gap until lifecycle-tested. Agent Teams, the Workflow primitive (DF/ULA), and hooks stay Claude-only for now — no redesign attempted there.

## Per-engine specifics (detail lives in the drafts)

- **Codex** — **ported, validated end-to-end (2026-07-05), and SHIPPED in v19** via the `docs/engines/` engine-profile binding: profile selection, framework-root self-location, and native subagent fan-out (recall + merge) all pass on real `codex exec`. See `codex-port-validated-end-to-end.md`, `docs-engines-convention.md`. Key corrections to earlier reads: **Codex has a native multi-agent subsystem** (in-session `spawn_agent` tools, `multi_agent_v1`) — the earlier "no native subagents / needs a `codex exec` script fallback" read was wrong (`codex-native-multi-agent-subsystem.md`); fan-out is expressed as model instructions to `spawn_agent`, not a shell script. Standing constraints: default sandbox denies network (threatens the auto-pull/finalize-push/workspace-sync freshness contracts — mitigated by existing degraded-mode design) and blocks `.git/` writes; the supported finalization path therefore requires `.git` writable through launch/configuration, while a commit-blocked default-sandbox run is degraded fallback (`codex-git-sandbox-blocks-dotgit.md`). Plugin loading is a persistent install (`codex plugin marketplace add` + `codex plugin add`), not a per-invocation flag — unlike Claude Code and Cursor, both of which take `--plugin-dir` (`codex-cli-plugin-loading-findings.md`). Repo-driven onboarding is agent-executed, and Codex per-agent shortcuts are designed as personal skills; shortcut generation/removal is not complete until lifecycle-tested. See `workdir/draft-port-codex.md`.
- **Cursor** — validated locally first, then **shipped in canonical `lore-framework` as v20**
  (commit `5cbb967`, manifests `1.20.0`, 2026-07-05). `--plugin-dir` works, slash skill
  invocation works, AGENTS.md is the memory-file target, and `ps -o args= -p $PPID` exposes
  `cursor-agent`, giving Boot Step 0 a strong detection signal. The shipped profile is
  intentionally conservative: rather than claim an unverified native Cursor subagent mechanism, it
  uses a **serial host-side** override for the fan-out procedures. That smaller claim was enough
  for the full currently-implemented lifecycle catalog to pass on the real local engine (`19/19`)
  before landing, using a separate `lore-framework-cursor/` build and a local Cursor harness
  driver. Cursor may still end up with a cleaner declarative subagent story via
  `.cursor/agents/*.md`, but that is now an optimization phase, not a blocker to Tier-1 parity.
  One real risk remains before advertising Cursor's parallel-agent support: Cursor auto-manages
  its own git worktrees for parallel agents, which may interact with the framework's existing
  worktree convention (`worktrees-convention.md`) in ways that are still not checked. The separate
  `lore-framework-cursor/` sibling is now **superseded**. See `workdir/draft-port-cursor.md`,
  `cursor-agent-cli-probe-findings.md`, `cursor-port-validated-end-to-end.md`,
  `cursor-cli-and-harness-operational-notes.md`.
- **Engine-specific durable entry points** — after the first wave of ports landed, the lore graph
  itself also needs a stable shape for future engine work: one hub topic per engine covering
  install/update, invocation, subagents, memory file, MCP/plugin loading, sandbox, and harness
  caveats. Use `claude-engine-capabilities.md`, `codex-engine-capabilities.md`, and
  `cursor-engine-capabilities.md` as those entry points; keep atomic facts in the linked detailed
  topics.

## Dominant shared risk

Both drafts converge on the same top risk: **the framework is prose executed by the model.** Merge alone is a 96-line procedure (`process-merge.md`) assuming faithful multi-step instruction-following. Fidelity on non-Claude models is unverified. Both plans end their phased work with an empirical fidelity report, explicitly framed as feeding the already-parked simplification/subtraction theme (`framework-improvements-backlog.md` § Architecture-Review Follow-Ups) — if a procedure degrades badly on another engine's models, that's a signal to simplify the procedure itself, not just to patch around it per-engine.

The Phase 0.5 harness already turned this from a theoretical risk into an observed one — see `agent-boot-doc-fidelity-fixes.md` for the first concrete instance (on Claude Code itself, before any port), and `execution-testing-catches-blind-ambiguity.md` for why prose review structurally can't catch this bug class.

**Update (2026-07-07): the knowledge-substrate half of the portability claim now has quantitative
backing.** The v1 quality-benchmark runs (`quality-benchmark-feature.md`,
`benchmark-findings-engines-models.md`) showed the boot-and-consult-lore path is robust down to
weak model tiers on all three engines (100% treatment on the easy catalog for every config,
including haiku and gpt-5.4-mini on the doc-driven codex path), with positive behavior uplift
(+37.5 to +75.0) in every engine+model config. Nuance worth carrying: **model–engine fit beats
model tier** — the same model can utilize lore very differently on different engines
(sonnet: 100% on claude vs 62.5% on cursor), so per-pairing measurement stays necessary.

**Update (2026-07-05): the hard Tier-B nucleus is now proven on Codex, not just feared.** The subagent fan-out (recall + merge) ran faithfully on real `codex exec` at the weak `gpt-5.4-mini` tier — including the host-reads-steps merge override, ground-truthed in Codex's rollout logs. So the "framework is prose" risk is empirically retired for the Codex boot/recall/merge path; the remaining fidelity questions are the un-exercised lifecycle scenarios and the still-unported Cursor target. See `codex-port-validated-end-to-end.md`.

## Positioning implication (revised 2026-07-20)

**Superseded claim:** this section used to argue that no surveyed competitor federates knowledge across different coding engines, and that shipping this port would therefore create an unmatched differentiator. The 2026-07-20 landscape re-survey invalidated that — claude-mem, BYK/loreai, and rohitg00/agentmemory all now claim multi-engine support, so cross-engine federation is table stakes, not a moat (see `similar-projects-landscape.md` § What changed).

The port still matters — it's the technical enabler that makes "share one team-shared agent repo regardless of which coding engine each member runs" possible at all, and mixed-engine teams remain a real practical benefit. But it's now a supporting fact, not the headline claim. The headline is the **positioning triad** — canonical framing at `positioning-triad-differentiation.md`: (1) named role-based agents as the knowledge unit, (2) a deliberate, skill-triggered reflect/merge curation lifecycle vs. everyone else's automatic capture, (3) cross-agent collaboration (attach/consult/recall/spawn-teammate). Lead README/marketplace/positioning language with the triad; mention cross-engine and git-sharing as supporting facts. See `similar-projects-landscape.md` and `workdir/positioning-analysis-2026-07-20.md` for the full argument and draft pitch line.

## Status

**Codex port SHIPPED in canonical `lore-framework` as v19** (commit `72b1b2a`, manifests `1.19.0`,
pushed 2026-07-05). **Cursor engine profile SHIPPED in canonical `lore-framework` as v20**
(commit `5cbb967`, manifests `1.20.0`, pushed 2026-07-05). **Cursor dual skill tree SHIPPED as v21**
(commit `f7b1c2b`, manifests `1.21.0`, 2026-07-06) — the last packaging gap for mixed-engine teams
sharing one repo, fixing Cursor's picker showing raw folder names (`cursor-dual-skill-tree-one-repo.md`).
Two full workdir drafts anchored the work; both Tier-1 engine-profile legs are now landed. Trajectory:

- **Coupling inventory + tiering complete** — the full "real list" (5 adapter bindings; Tier A/B/C) exists in `claude-coupling-inventory-and-port-tiers.md` (durable summary) and `workdir/claude-specific-inventory.md` (full per-site).
- **Full engine-profile binding IMPLEMENTED and VALIDATED end-to-end on real Codex** (2026-07-05, in the sibling `lore-framework-codex` build) — the `docs/engines/` convention (all five bindings, Boot Step-0 engine selection) passes on `codex exec`: profile selection, framework-root self-location (zero `${CLAUDE_PLUGIN_ROOT}` leak), and native `spawn_agent` fan-out for **both** recall and merge (host-reads-steps override). The Tier-B subagent nucleus — the part most feared — is proven. The test's `.git`-sandbox commit block is now a documented launch/configuration requirement for the supported finalization path. See `docs-engines-convention.md`, `codex-port-validated-end-to-end.md`, `codex-native-multi-agent-subsystem.md`, `codex-git-sandbox-blocks-dotgit.md`, `codex-testing-methodology.md`.
- **Landed into canonical v19** — the validated `docs/engines/` build was folded from the sibling
  into the real plugin (via the working-tree-diff technique, `landing-via-working-tree-diff.md`),
  together with framework-root-full (`framework-root-self-location-validated.md`) and the
  defer-clarity robustness fix (`haiku-ambiguity-detector.md`, authored fresh at landing).
  Re-validated 6/6 on haiku against the real v19 tree. The `lore-framework-codex` sibling is now
  **superseded and deletable**.
- **Cursor landed into canonical v20** — the separate sibling `lore-framework-cursor/` with
  `docs/engines/cursor.md` and the five-file framework diff was folded into the real plugin after
  the local `19/19` validation pass. The landing also added `release-notes/20.md` and bumped
  `VERSION` / plugin manifests to `20` / `1.20.0`. The `lore-framework-cursor` sibling is now
  **superseded and deletable**. The matching lifecycle-harness support in
  `lore-framework-dev/tests/` remains a separate dev-repo change outside finalize's `agents/`
  commit scope. See `cursor-port-validated-end-to-end.md`, `cursor-cli-and-harness-operational-notes.md`.
- **Cursor dual skill tree landed into canonical v21** — one repo now carries both engines' skill
  namespaces (Claude Code loads canonical `skills/<skill>/` → `/lr:<skill>`; Cursor loads 27
  prefixed wrappers `.cursor-skills/lr-<skill>/` → `/lr-<skill>` via `.cursor-plugin/plugin.json`),
  plus `scripts/sync-cursor-skills` and `/lr:check` #21 (cursor-tree parity). Full-harness-verified
  before push: **42/42** on `claude` (19/19 lifecycle + 23 deterministic). See
  `cursor-dual-skill-tree-one-repo.md`, `lifecycle-testing-harness.md`.
- **v22 follow-up shipped in canonical `lore-framework`** — top-level `INSTALL-CODEX.md` and
  `INSTALL-CURSOR.md`, `scripts/codex-refresh-plugin`, and engine-specific `R > F`
  version-mismatch guidance. The directly affected Codex lifecycle path gained its own targeted
  scenario and was rerun on `gpt-5.4-mini` before push.
- **v23 follow-up shipped in canonical `lore-framework`** — the Cursor wrapper side moved from
  `skills/cursor/` to the hidden `.cursor-skills/` root after real Codex validation showed the old
  wrapper tree was still being surfaced as redundant `lr:lr-*` skills. The practical verification
  loop for plugin-layout changes is now: update repo, refresh the installed Codex plugin, then
  rerun a real skill-count check.
- **Manual trial guides in workdir**: `workdir/first-steps-codex.md` (verified) and
  `workdir/first-steps-cursor.md` (still useful as the original manual recipe, now superseded by
  the shipped v20 Cursor profile and harness run).

See `workdir/draft-port-codex.md`, `workdir/draft-port-cursor.md`, `port-landing-next-steps.md`.

Phase 0.5 — the shared automated testing pipeline designed in a third companion draft (2026-07-03), `workdir/draft-testing-pipeline.md` — is now **built and real**, not just designed: one engine-neutral scenario catalog (fixture + prompt + assertions per scenario) run headless per engine via thin drivers, graded pass-rates as the fidelity scorecard, built on Claude Code first as the baseline. It mechanizes the Phase-3 "model-fidelity report" both port drafts call for. 19 of 21 Tier-1 scenarios pass on Claude Code. See `lifecycle-testing-harness.md` for the implementation; `workdir/draft-testing-pipeline.md` remains the original design doc.

The harness's first real use already found two genuine doc-fidelity bugs in `agent-boot.md` — before either port started — concrete first-hand evidence for the "framework is prose" risk below. See `agent-boot-doc-fidelity-fixes.md` and the general principle `execution-testing-catches-blind-ambiguity.md`.

## See Also

- `workdir/draft-port-codex.md`, `workdir/draft-port-cursor.md` — the phased per-engine plans; this topic is the anchor, not a restatement.
- `workdir/draft-testing-pipeline.md` — the shared multi-engine testing pipeline (Phase 0.5) original design doc; scenario catalog + per-engine drivers + fidelity scorecard.
- `lifecycle-testing-harness.md` — the built implementation of Phase 0.5, its coverage, and cost/gating.
- `quality-benchmark-feature.md`, `benchmark-findings-engines-models.md` — the quality track and its v1 cross-engine lore-utilization evidence for this direction's portability claim.
- `agent-boot-doc-fidelity-fixes.md`, `execution-testing-catches-blind-ambiguity.md`, `haiku-ambiguity-detector.md` — the harness's real finds and the general/weak-model principles behind them.
- `claude-coupling-inventory-and-port-tiers.md` — the full coupling inventory + Tier A/B/C map.
- `framework-root-self-location-validated.md` — the biggest Tier A slice, validated on Claude/haiku and now on real Codex.
- `docs-engines-convention.md` — the implemented five-binding engine-profile adapter layer.
- `codex-port-validated-end-to-end.md` — the Codex port proven end-to-end on real `codex exec`.
- `codex-native-multi-agent-subsystem.md` — Codex's in-session subagent fan-out (corrects "no native subagents").
- `codex-git-sandbox-blocks-dotgit.md` — the `.git`-write gate and supported finalization contract.
- `codex-testing-methodology.md` — the rollout-log ground-truthing behind the Codex validation.
- `port-landing-next-steps.md` — the landing record and the remaining follow-ups.
- `similar-projects-landscape.md` — the competitive survey this direction's positioning case rests on.
- `positioning-triad-differentiation.md` — the canonical positioning framing that now supersedes this topic's old cross-engine-uniqueness claim.
- `wait-primitive-feature.md` — the MCP-based primitive that ports with no redesign, evidence for "packaging not redesign."
- `framework-scope-vs-agent-scope.md` — the layer-ownership test the `docs/engines/` adapter lever will need to pass.
- `worktrees-convention.md` — the Cursor auto-worktree interplay flagged to verify.
- `codex-cli-plugin-loading-findings.md`, `cursor-agent-cli-probe-findings.md` — the first empirical per-engine probes.
- `headless-cli-smoke-testing-discipline.md` — the operational lesson those probes produced (don't hard-kill a headless CLI run).
- `skill-doc-pattern.md` — what the thin-pointer skill/doc packaging maps onto per engine.
- `plugin-mcp-server-convention.md` — the MCP registration convention that ports unchanged.
- `framework-improvements-backlog.md` § Architecture-Review Follow-Ups — the simplification/subtraction theme this direction's fidelity report feeds.
- `lr-dev-direction.md`, `autonomous-agents-vision.md` — sibling major directions (different axes: SDLC activity, process/substrate, and now engine portability).
