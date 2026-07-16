# Lore Context

Compacted working knowledge for the **lore-architect**. This is the entry point to the lore graph, not a catalog — each theme points at its summary topic, which fans out to detail. For exhaustive lookup, scan `lore/` directly. (This doc follows the `lore-context` shape discipline: working-knowledge + summary-topic references, present-tense, no index, no version-history narrative — see `process-merge.md` § Step 4.)

## Style Skills

A category of user-invoked `/lr:` skill that changes how the agent *communicates or collaborates* (vs. operations like `/lr:recall`/`/lr:merge`). Regular thin-pointer skills — **not** boot-loaded or surfaced at boot; the user re-asserts a style by invoking its trigger. Three shipped in v19, composing on three levels: **`/lr:plain-language`** (sentence — plain short English), **`/lr:dialogue`** (turn — short turns, one step at a time), **`/lr:follow-me`** (thinking-direction — user drives, small suggestions only; extracted up from lore, canonical def now in `docs/follow-me.md`). A boot-loaded "soft skills" mechanism was prototyped and rejected in favor of plain skills. See `style-skills.md`, `skill-request-defaults-to-regular-skill.md`, `soft-skill-follow-me-mode.md`.

## Who I Am

Architect and maintainer of the lore system — the `lr` framework plugin and the agent ecosystem on it. I work across two repos: **`lore-framework/`** (the distributed plugin — changes to how agents work go here) and **`lore-framework-dev/`** (my own agent repo — my lore, workdir, sessions). I'm both builder and user: I use lore to track my own design knowledge. See `role.md`.

## System Architecture

Three discrete layers — identify which one owns a change before touching files:
1. **Plugin** (`lore-framework/`, installed as `lr`) — what's distributed via the marketplace: skills, docs, migrations, scripts, manifests, `VERSION`. Universal across installs.
2. **Domain** — the conceptual scope of one agent repo, marked by `lore-repo.md` (frontmatter: `description`, `version`, optional `repos:`). Holds `agents/<name>/` with `role.md`, `lore-context.md`, `lore/`, `workdir/`, `sessions/`.
3. **Workspace** — the filesystem Claude runs from; holds one or more agent repos + their declared siblings. Discovery scans workspace-root dirs for `lore-repo.md`; nested repos are invisible to most skills.

See `architecture-overview.md`, `workspace-vs-domain-vocabulary.md`, `agent-discovery-nesting-constraint.md`, `plugin-vs-agent-repo-separation.md`.

## Design Principles

Identity-layer framings that frame everything else:
- **Team-shared knowledge** — agents are team-shared knowledge containers, not personal notebooks. Design for concurrent multi-contributor use.
- **Engine, not KB** — the framework is the engine/environment for self-improving agents; the knowledge base is a consequence, not the identity.
- **Executors first, advisors second** — primary value is getting things done; conversation is secondary. The usage→learning positive feedback loop only spins under executor-first framing.

What each agent carries: **knowledge** (markdown — what it knows, accrues passively via reflection) + **skills** (tools + instructions — what it can do, evolves actively via in-flight teaching). Distinct assets; don't collapse them.

Core mechanics: directory-driven, plain markdown (frontmatter only on descriptor files), git-as-metadata, delete-don't-mark, knowledge graph by filename reference, concise context with detail on demand, skill/doc separation, repo-level versioning. Framework owns the universal; agents own repo/host/workflow specifics.

See `system-design-principles.md` (the full list and the overreach diagnostics), plus the framing topics `team-shared-knowledge-principle.md`, `framework-as-engine-not-kb.md`, `agents-are-executors-first.md`, `knowledge-vs-skills-distinction.md`, `framework-scope-vs-agent-scope.md`.

## Skills & Docs

Operations are Claude Code plugin skills, `lr:` prefix on Claude; Cursor uses `/lr-<skill>` via
prefixed wrappers (`cursor-dual-skill-tree-one-repo.md`). **Skills are thin pointers** — each `skills/<name>/SKILL.md` is a one-line reference to `docs/<name>.md`, where all logic lives. Same for generated `/lr-<agent>-agent` boot commands (thin delegations to `agent-boot.md`). When a skill orchestrates sub-skills, the orchestration gets its own `docs/<skill>.md`; non-skill procedures shared across call sites get a `docs/<procedure>.md` (e.g. `auto-pull.md`). See `slash-command-system.md`, `skill-doc-pattern.md`, `shared-procedure-doc-pattern.md`, `single-canonical-source-discipline.md`.

The plugin can also **bundle an MCP server** (declared in a root `.mcp.json`, auto-launched by Claude Code with its tools merged into the agent): **`lr-wait`** (v18) is the first — and the framework's first `python3` dependency (stdlib-only, no pip; the sole sanctioned exception to bash-on-BSD, for protocol-speaking server components). See `plugin-mcp-server-convention.md`, `wait-primitive-feature.md`.

## Engine Hubs

Engine-specific operational knowledge now has one hub topic per engine: `claude-engine-capabilities.md`,
`codex-engine-capabilities.md`, and `cursor-engine-capabilities.md`. Use them as the entry points
for install/update model, invocation surface, subagent mechanism, memory file, MCP/plugin loading,
sandbox constraints, and lifecycle-harness caveats; keep atomic findings in the linked detailed
topics rather than rediscovering them from old session notes.

## Marketplace & Distribution

Shipping one repo to multiple engines' plugin marketplaces means handling **each engine's packaging
separately** — manifest schema, skill-tree location, and update model all differ, so Claude parity
does *not* imply Cursor/Codex parity. Claude Code is strict-clean; remaining public-distribution step
is Console-form community submission. Cursor is structurally ready, but seamless multi-user
propagation still needs a team marketplace + Auto Refresh + Cursor GitHub App validation. Codex
native packaging is resolved in v25: legacy Claude marketplace fallback still works, native
`.agents/plugins/marketplace.json` is preferred when present, and `.codex-plugin/plugin.json` is the
Codex version-bearing manifest. Public submission also needs reviewer-facing metadata (`MARKETPLACE.md`
directory copy + root `PRIVACY.md`) and precise separation between runtime release identity,
submission-support files, and per-engine verified publication status. See `engine-marketplace-readiness.md`, `plugin-distribution.md`,
`cursor-plugin-distribution-update-model.md`, `plugin-manifest-versioning.md`.

## Boot & Freshness

Boot (`agent-boot.md`, single source of truth): discover agent → auto-pull repo → version check → read `role.md` + `lore-context.md` → detect teammate spawn → confirm. **Boot loads only those two files; topics are read on demand.** Repos auto-pull at every session-context boundary (boot, attach, pre-merge) to match the team's latest pushed state; `/lr:pull-lore` is the manual refresh. See `freshness-contracts-at-session-boundaries.md`, `auto-pull-mechanism.md`.

## Cross-Agent Collaboration

- **`/lr:recall [hint]`** — search lore of already-loaded agents (host + guests); fan-out per agent.
- **`/lr:consult <agent> [hint]`** — one-shot question to an unloaded agent; a subagent boots it, answers with file pointers, exits.
- **`/lr:attach <agent>`** — load another agent as a sustained guest; host stays sole executor, host-wins on conflicts.
- **`/lr:spawn-teammate` (BETA)** — spawn agents as Agent Teams teammates for parallel panes; the teammate's primary interlocutor is the user, not the lead.

See `lore-search-pattern.md`, `consult-pattern.md`, `attach-pattern.md`, `spawn-teammate-feature.md`, `teammate-conventions.md`.

## Session Takeover (BETA)

**`/lr:takeover`** converts engine-native session logs into a markdown digest so a new session on any engine can continue interrupted work. Codex, Claude Code, and Cursor are supported (`scripts/session-takeover` — list, convert, render). Cursor pairs tool results from `store.db` to JSONL `tool_use` batches via batch-window name matching; same-name parallel batches and interrupted sessions set `pairing_uncertain`. See `takeover-feature.md`, `cursor-takeover-batch-pairing.md`, `engine-session-log-formats.md`.

## Finalization

User-triggered, four phases (`/lr:finalize` runs all; phases also run standalone): **reflect** (inline, host-first, per agent — needs session context) → **merge** (parallel subagents, one per agent booted as itself, file-driven — integrates reflections into `lore/`, `lore-context.md`, `role.md`) → **summarize** (host writes the canonical session summary + short guest summaries) → **commit+push** (one commit per touched repo; conflict-resolution on push rejection). Do not finalize unless the user triggers it. See `finalization-process.md`, `finalize.md`, `merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`.

## Versioning & Migration

`lore-framework/VERSION` — **v26 is shipped and pushed** (Cursor takeover conversion for
`/lr:takeover` BETA; `release-notes/26.md`, manifests `1.26.0`; `lore-framework` main commit
`ce90f9a` on top of `3909129` "Release v26: Cursor takeover conversion", tagged `lr--v1.26.0`).
**v25** (Cursor ops parity, native Codex packaging, workspace pull/init) is the prior release. Each repo stamps
`VERSION` in `lore-repo.md`; four version-bearing plugin manifests mirror `1.<VERSION>.0`. `/lr:check`
#19 enforces them. See `versioning-release-types.md`, `takeover-feature.md`,
`cursor-takeover-batch-pairing.md`, `plugin-manifest-versioning.md`.

## Consistency & Diagnostics

- **`/lr:check`** — 23 content-consistency checks (descriptor/version, structure, references, size/state, drift, four-manifest #19, migration write-paths #20, cursor-tree parity #21, workspace-layer checks #22–23). See `consistency-checks.md`.
- **`/lr:doctor`** — diagnoses runtime/environmental issues that escape content checks (esp. stale plugin cache) via an accreting ailment catalog. See `ailment-catalog-pattern.md`.

## Operating Disciplines

How I work, especially at version ships and high-stakes lore edits:
- **On VERSION bumps:** backfill `versioning-release-types.md` history, add the cache-clear footer if cache-affecting, bump all four version-bearing plugin manifests to `1.<VERSION>.0`, promote any newly-named principle to its own topic. (Full curation disciplines live in `role.md`.)
- **Pre-ship review:** multi-lens parallel-reviewer fan-out, iterated until a round finds nothing worth fixing (convergence is the ship signal); sonnet boot-as-self review for high-stakes single edits. See `parallel-reviewer-fanout-pattern.md`, `sonnet-subagent-review-pattern.md`. **Second, empirical leg (v18+):** for procedure docs covered by the lifecycle testing harness, also run the relevant scenarios against real engine execution before shipping — review catches reasoning issues, the harness catches model-execution-fidelity issues invisible to a strong-model reviewer. See `lifecycle-testing-harness.md`, `execution-testing-catches-blind-ambiguity.md`.
- **Verify before asserting** — check filesystem/state directly before "fixing" a suspected bug; verify *which* bug, not just whether. See `verify-before-acting-on-suspected-bugs.md`.
- **Curation meta-rules:** name foundational principles as their own topics; single canonical source (pointer, don't restate); don't defer completable bounded sweeps; graduated verification (confidence, not boolean). See `naming-foundational-principles.md`, `single-canonical-source-discipline.md`, `feedback-don-t-defer-completable-scope.md`, `graduated-verification-confidence.md`.
- **User-feedback working style:** ranked-shortlist over exhaustive enumeration; confirm before writing durable lore mid-session; populate dry-run counters with would-be outcomes; "enforce X" ≠ add a required schema field. See `feedback-too-many-words.md`, `feedback-confirm-before-writing-lore.md`, `feedback-schemas-as-enforcement-overreach.md`.

## Key Constraints

- `lore-context.md` ≤ 50K tokens; **shape over size** — working-knowledge + summary-topic references, not an index (see `lore-context-shape-discipline.md`).
- Lore topics: atomic, <5K tokens preferred, plain markdown, no frontmatter.
- Descriptor frontmatter: `lore-repo.md` = `description` + `version` (+ optional `repos:`); `role.md` = `description` only.
- Command filenames: lowercase/digits/hyphens, ≤64 chars.
- Placeholders: `<workspace>`, `<lore-agent-repo>`, `<guest-lore-agent-repo>`, `<agent-name>`, `${CLAUDE_PLUGIN_ROOT}`.
- **CWD safety:** never `cd` when later tools depend on cwd — use `git -C <repo>`. **Portable shell:** assume BSD/macOS, no GNU-only binaries (`timeout`); bound commands via the Bash-tool timeout.
- See `conventions.md`, `placeholder-vocabulary.md`, `tooling-cwd-safety.md`, `portable-shell-in-framework-docs.md`.

## Onboarding-Doc Authoring

Co-authoring framework onboarding docs for adopting teams is part of the role. Two distinct genres now exist: **`onboarding-doc-narrative-pattern.md`** (long-form prose pitching a human reader) and **`paste-link-installer-doc-genre.md`** (a doc written *to the AI agent* as the literal installer, meant to be pasted as a link — shipped as `QUICKSTART.md` + per-engine `INSTALL-<ENGINE>.md`). Load the identity-layer framings first, then the toolkit: the two genre topics above, `use-cases-via-parallel-consult-pattern.md`, `terminology-domain-collision-trap.md`, `agent-as-universal-working-environment.md`, `in-flight-skill-teaching-pattern.md`. Pre-ship review for either genre uses `parallel-reviewer-fanout-pattern.md`'s multi-lens fan-out; the installer genre additionally needs the **AI-installer (literal executor)** lens (`ai-installer-review-lens.md`) — it catches execution-fidelity bugs (e.g. `skill-doc-filename-divergence-bug-class.md`) the newcomer/editorial lenses miss. Landing-page placement of a self-referential/meta example differs from long-narrative placement — primacy goes to the strongest CTA; see `onboarding-doc-narrative-pattern.md` § placement note. First instance: the Activities team's intro doc.

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — major direction; a `lr` module for SDLC automation toward an autonomous "dark factory" SDLC. Per-repo artifacts + narrative context live in a `<repo>-df` backbone (a `repo-lore/<file>/` mirror: `file-lore.md` narrative landing + flat structured aspect subdirs like `ula/`). Skills not agents; persistence external. First aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`) — unit-level analysis with a bug-verification track, BETA. The DF/ULA design thread is closed and the module ships as BETA. Anchor: `lr-dev-direction.md`; see `df-per-repo-backbone.md`, `aiqa-ula-feature.md`, `df-module-conventions.md`, `workflow-primitive-operational-notes.md`.
- **Autonomous agents** (parked vision) — agents as always-on background collaborators with persistent task state, raising for input only when needed. Concrete steps taken: `/lr:spawn-teammate` (multi-agent substrate, v10) and the v18 **`lr-wait`** primitive — the first *inbound-signal* step: an agent blocks on an event and an external actor (cron/CI/webhook/human, via `lr-emit`) wakes it with text. See `autonomous-agents-vision.md`, `autonomous-agents-substrate.md`, `wait-primitive-feature.md`.
- **Multi-engine portability (Codex, Cursor)** — major direction, user-raised 2026-07-02; Claude
  Code stays the major version, goal is Tier-1-parity ports so mixed-engine teams can share one
  team-shared agent repo. The knowledge substrate (agent repos, `lore-repo.md`, `role.md`,
  `lore/`, `lore-context.md`, git) is already engine-agnostic — SKILL.md is an open standard both
  engines support, AGENTS.md is native to both, MCP ports `lr-wait` unchanged — so the port is
  mostly packaging, not redesign. The whole port surface is **5 adapter bindings** via the
  `docs/engines/` engine-profile convention (framework-root, subagent-spawn, runtime-bounding,
  memory-file, invocation-syntax) + Boot Step-0 engine selection; the full Claude-coupling
  inventory with Tier A/B/C tiering exists (`claude-coupling-inventory-and-port-tiers.md`).
  **The Codex port SHIPPED in v19** (canonical `lore-framework`, commit `72b1b2a`, manifests
  `1.19.0`): `docs/engines/{claude,codex}.md`, `<framework-root>` self-location across every
  SKILL.md, and the defer-clarity boot fix — validated end-to-end on real `codex exec` (profile
  selection, zero `${CLAUDE_PLUGIN_ROOT}` leak, native `spawn_agent` fan-out for recall **and**
  merge with the host-reads-steps override) and re-validated 6/6 on haiku against the real v19
  tree. The hard Tier-B subagent nucleus is proven, not feared; Codex has a **native in-session
  multi-agent subsystem** (`spawn_agent`/`wait_agent`, `multi_agent_v1`). Trust rests on
  ground-truthing tool use in Codex's rollout logs, not model self-report. The
  supported Codex finalization path requires `.git` writable through launch/configuration; the
  default sandbox can leave reflect/merge output on disk but block commit, which is a degraded
  fallback rather than a merge failure. Codex per-agent shortcuts use personal skills
  (`~/.codex/skills/lr-<agent>-agent/SKILL.md`, `$lr-<agent>-agent`), but register/unregister/list
  support remains an explicit implementation gap until lifecycle-tested. The
  `lore-framework-codex` staging sibling is now superseded and deletable. **The Cursor engine
  profile SHIPPED in v20** (canonical `lore-framework`, commit `5cbb967`, manifests `1.20.0`,
  `release-notes/20.md`): `docs/engines/cursor.md`, Boot Step-0 detection for `cursor-agent` /
  `~/.cursor`, and Cursor engine notes in `docs/attach.md`, `docs/init.md`, and
  `docs/resolve-conflicts.md`. The shipped Cursor profile stays intentionally conservative: a
  **serial host-side** override rather than an unverified native fan-out claim. That smaller claim
  was enough for the real local Cursor installation to pass the full implemented lifecycle catalog
  (`19/19`) before landing. The separate `lore-framework-cursor/` sibling is now superseded and
  deletable. **The Cursor dual skill tree SHIPPED in v21** (commit `f7b1c2b`, manifests `1.21.0`,
  `release-notes/21.md`): one repo carries both engines' skill namespaces — Claude loads canonical
  `skills/<skill>/` (`/lr:<skill>`), Cursor loads 27 prefixed wrappers `.cursor-skills/lr-<skill>/`
  (`/lr-<skill>`) via `.cursor-plugin/plugin.json`, plus `scripts/sync-cursor-skills` and
  `/lr:check` #21 (cursor-tree parity) — closing the last mixed-engine packaging gap (Cursor's
  picker showing raw folder names). Full-harness-verified before push: **42/42** on `claude` (19/19
  lifecycle + 23 deterministic, ~$9.4/~27 min). See `cursor-dual-skill-tree-one-repo.md`. Matching
  lifecycle-harness support in `lore-framework-dev/tests/` remains a separate
  dev-repo change outside finalize's `agents/` commit scope. Remaining deferred Claude-first
  surfaces: `lr-wait` `.mcp.json`, DF/AIQA + `migrations/*`, Codex shortcut lifecycle validation,
  rollout-log-backed Codex harness assertions, and any stronger Cursor-native parallel story. The dominant
  "framework is prose" risk is empirically retired for the Codex path and materially reduced for
  Cursor's implemented Tier-1 path. Anchor: `multi-engine-portability-direction.md`; see
  `docs-engines-convention.md`, `codex-port-validated-end-to-end.md`,
  `cursor-port-validated-end-to-end.md`, `cursor-cli-and-harness-operational-notes.md`,
  `landing-via-working-tree-diff.md`, `codex-native-multi-agent-subsystem.md`,
  `codex-git-sandbox-blocks-dotgit.md`, `codex-testing-methodology.md`,
  `framework-root-self-location-validated.md`, `claude-coupling-inventory-and-port-tiers.md`,
  `lifecycle-testing-harness.md`, `codex-cli-plugin-loading-findings.md`,
  `codex-local-plugin-update.md`, `cursor-agent-cli-probe-findings.md`,
  `headless-cli-smoke-testing-discipline.md`, `haiku-ambiguity-detector.md`, and
  `similar-projects-landscape.md` (the positioning case — no surveyed competitor federates
  knowledge across different coding engines). **v22** then added top-level engine-readable install
  guides (`INSTALL-CODEX.md`, `INSTALL-CURSOR.md`), a Codex refresh helper, and engine-specific
  `R > F` guidance — plus the durable per-engine hub topics `claude-engine-capabilities.md`,
  `codex-engine-capabilities.md`, and `cursor-engine-capabilities.md` so future engine work starts
  from a stable operational map rather than scattered probes. **v23** then tightened the Cursor
  packaging: the wrapper side moved from `skills/cursor/` into `.cursor-skills/` because Codex was
  recursively surfacing the old tree as `lr:lr-*` duplicates; the practical verification loop is
  now "update repo → refresh installed Codex plugin → re-run a real skill-count check." The
  portability claim's knowledge-substrate half now has quantitative backing: the v1 quality
  benchmark showed positive lore-utilization uplift on every engine+model config and 100%
  easy-catalog treatment down to weak tiers, with the nuance that **model–engine fit beats model
  tier** (see `quality-benchmark-feature.md`, `benchmark-findings-engines-models.md`).
- **Lore housekeeping / consolidation "sleep" pass** and the **simplification/subtraction** review item — active follow-ups from the 2026-06-13 architecture review; see `framework-improvements-backlog.md`. That review's settled dispositions (incl. DF-inside-`lr` and team-shared/multi-author as deliberate, not defects — don't re-raise) live in `architecture-review-dispositions.md`. A newer 2026-07-02 review added two further backlog items (post-merge diff verification, recall-time staleness surfacing) — see `framework-improvements-backlog.md` § Merge Quality, § Search / Scaling.
- Parked: workdir-as-reference-library; vector-DB search (until >100 topics/agent); the session-as-durable-artifact cluster (boot auto-push, boot-context cache, suspend/resume, JSONL archive). All in `framework-improvements-backlog.md`.
- **v25 workspace layer (pull + init)** — implemented locally in `lore-framework` commit `0311ab6`.
  Hard renames: workspace-sync→workspace-pull, init→workspace-init. Two-level repo declarations
  (`lore-workspace.md` + domain `repos:`), optional workspace-as-git-repo envelope, cursor wrapper
  regeneration, checks #22–23. Full lifecycle remains the pre-push gate. See
  `v25-workspace-pull-init-design.md`, `workspace-meta-repo-pattern.md`.

## Current State

Workspace holds three canonical repos: **`lore-framework/`** (plugin), **`lore-framework-dev/`**
(this repo — lore-architect lore + drafts), and **`lore-agents/`** (personal agents). **v26 is
shipped and pushed** in `lore-framework/` (Cursor takeover conversion; commit `ce90f9a`, tag
`lr--v1.26.0`). **v25** (workspace layer, native Codex packaging, Cursor ops parity) is the prior
release. See `takeover-feature.md`, `cursor-takeover-batch-pairing.md`, `release-notes/26.md` (plugin tree).

## Running Backlog

`framework-improvements-backlog.md` is the canonical list of deferred items; its § "v25 SHIP
CLOSURE" records the final v25 gate disposition. Quality benchmark tier/probe expansion is now in
the dev repo with regular/deep matrix defaults and local override support. ~139 lore topics.
