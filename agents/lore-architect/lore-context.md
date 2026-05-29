# Lore Context

## System Architecture

The lore system has **three discrete layers** (made explicit in v11):

1. **Plugin layer** (`lore-framework/`, installed as `lr`) — what's distributed via the marketplace. Skill definitions, docs, `migrations/`, marketplace config, `VERSION`, `scripts/workspace-sync`. Universal across all installs. As of v12: includes `/lr:doctor` skill + `docs/doctor-*.md` ailment catalog topics + cache-clear convention in `docs/conventions.md`.
2. **Domain layer** — the conceptual scope of a single agent repo. Each agent repo is identified by `lore-repo.md` at its root (YAML frontmatter: `description`, `version`, optional `repos:` list — the **only** place a framework version is stamped). Contains agent definitions: `role.md` (frontmatter: `description` only), `lore-context.md`, `lore/`, `workdir/`, `sessions/`. **Plugin vs agent-repo separation** is a deliberate axis (different from content-scope): plugin repos host what's distributed; agent repos host what contributors clone. See `plugin-vs-agent-repo-separation.md`.
3. **Workspace layer** (filesystem) — the parent directory Claude is launched from. Holds one or more agent repos plus their declared sibling repos. v11 introduced workspace-level orchestration: `/lr:workspace-sync` skill + `repos:` field. **Discovery constraint:** agent repos must sit at the workspace root to be discoverable — nested placements are functional but invisible to `/lr:list-*`, `/lr:check`, `/lr:recall`, `/lr:boot`, `/lr:workspace-sync`, etc. Only registered `/lr-<name>-agent` shortcuts reach nested repos.

See `architecture-overview.md`, `domain-directory-concept.md`, `agent-discovery-nesting-constraint.md`, `workspace-vs-domain-vocabulary.md`.

**Vocabulary (v11 split):** "workspace" = filesystem (the dir Claude runs from; new `<workspace>` placeholder, replaces `<domain>`). "Domain" = conceptual scope of one agent repo (prose only — no brackets). A multi-domain workspace is several agent repos coexisting side-by-side. The split unlocked the `/lr:workspace-sync` design: agent repo (domain) declares siblings → workspace (filesystem) gathers them. When extending the framework, identify which layer a change belongs to. See `workspace-vs-domain-vocabulary.md`.

## Design Principles

**Foundational framings (identity-layer trio):**
- Lore agents are **team-shared knowledge containers**, not personal notebooks — `team-shared-knowledge-principle.md` (outcome layer).
- LRF is the **engine/environment/tooling for self-improving Lore Agents**, not a knowledge base — `framework-as-engine-not-kb.md` (identity layer). KB is a *consequence* of how agents persist state, not the framework's identity.
- Agents are **executors first, advisors second** — primary value is getting things done; conversational use is a secondary affordance. `agents-are-executors-first.md`.

These three frame every principle below.

**Persisted-state distinction:** what each agent carries is **knowledge** (markdown — what it knows) plus **skills** (tools + instructions — what it can do). Two distinct, growing assets with distinct growth mechanisms — knowledge accrues passively via reflection, skills evolve actively via in-flight teaching. Don't collapse them. See `knowledge-vs-skills-distinction.md`, `in-flight-skill-teaching-pattern.md`.

**Self-sustaining dynamic:** the user's incentive (work faster) is the same activity that feeds the agent's growth — a **positive feedback loop between usage and learning**. Loop only spins under executor-first framing; advisor-only use breaks it. See `positive-feedback-loop-framing.md`.

**Positioning:** the agent is increasingly the **universal working environment** — unified interface to git, JIRA, Confluence, Grafana, Slack. Lore Agents specialize this generic environment with area-specific knowledge and skills. See `agent-as-universal-working-environment.md`.

Directory-driven, plain markdown (frontmatter only for descriptor files), git-as-metadata, delete-don't-mark, knowledge graph via filename references. Decoupled framework, agent-driven operations, concise context with detailed docs on demand, explicit (repo-level) versioning, skill/doc separation. **Framework-scope vs agent-scope:** framework owns what is universal; agents own repo/host/workflow specifics — isolate the universal core first, push specifics to agent lore or specialist agents reached via `/lr:consult` / `/lr:attach`. See `system-design-principles.md`, `framework-scope-vs-agent-scope.md`.

**Meta-rule for lore curation:** name foundational principles as their own topics — don't leave them implicit in the mechanisms they motivate. The `team-shared-knowledge-principle.md` topic itself is the canonical example: it was implicit across the multi-author finalization machinery for many versions before being named. The v12 `cache-clear-footer-convention.md` and `ailment-catalog-pattern.md` are recent applications of the same meta-rule. When designing a new feature and the rationale traces back to an unnamed framing, name it before continuing. See **`naming-foundational-principles.md`**.

## Plugin Skill System

All operations use Claude Code plugin skills with `lr:` prefix:
- `/lr:<action>` — framework skills: boot, reflect, merge, summarize, finalize, register-repo, unregister-repo, create-repo, create-agent, list-agents, list-repos, check, workspace-sync, update, recall, attach, consult, init, spawn-teammate (BETA), **doctor** (v12)
- `/lr-<agent-name>-agent` — optional per-agent boot commands, generated by `/lr:register-repo`

**Skills are thin references** — each `skills/<name>/SKILL.md` is a one-line pointer to `docs/<name>.md`. All logic lives in the doc. Same principle applies to generated artifacts: registered `/lr-<name>-agent` commands are one-line delegations to `agent-boot.md`.

**Orchestration refinement (v8+):** when a skill orchestrates across multiple sub-skills (e.g., `/lr:finalize` = reflect + merge + summarize + commit+push), the orchestration logic gets its own `docs/<skill>.md` — still leaving the SKILL.md a thin pointer, but extracting phase descriptions/failure-handling/invariants out of the skill file itself. Trigger: the skill file starts growing inline step-by-step content. See `skill-doc-pattern.md`, `slash-command-system.md`.

**Ailment catalog refinement (v12):** a second skill-doc-pattern variant — orchestrator decomposes by **case** (open-ended, additive) rather than by **phase** (sequential, fixed). `/lr:doctor` matches a user-described symptom against a catalog of named ailments at `docs/doctor-<slug>.md`. Each member is its own atomic topic with a four-section authoring schema (symptoms, diagnosis, remedy, prevention). The catalog grows by accretion as real-world cases distill into topics; a universality gate keeps it from drifting. The first shipped ailment is `doctor-stale-plugin-cache.md` — the failure mode that motivated v12 (a v11+ skill missing because Claude Code's plugin cache holds a prior version). See **`ailment-catalog-pattern.md`**.

**Boot flow:** `agent-boot.md` is the single source of truth. Boot procedure: discover → **version check** → read role.md + lore-context.md → confirm. If repo version differs from framework VERSION, `docs/version-check.md` runs the auto-upgrade (migrations + release notes, uncommitted-changes safety gate, degraded mode on failure).

**Cross-agent collaboration (v4+):** three mechanisms compose cleanly:
- `/lr:recall [hint]` — search lore of agents *already loaded* (host + attached guests). Fans out across all active agents in parallel.
- `/lr:consult <agent> [hint]` — one-shot question to an *unloaded* agent. Subagent boots consultant, answers with file pointers, exits. No finalization for the consultant. See `consult-pattern.md`.
- `/lr:attach <agent>` — load another agent as a **guest** into the host session for sustained co-work. Host remains the sole executor; guest's role + lore-context join host's context. Recall fans out to it; finalization iterates per active agent. See `attach-pattern.md`.

**Host/guest model:** exactly one host per session (originally booted agent). Zero or more guests attached via `/lr:attach`. Host-wins on lore conflicts. No detach.

**Lore search (v3+):** preferred mechanism is a subagent scan via `docs/lore-search.md`. Use a structured 4-part brief (task / session context / angle / output shape). Direct tools (Grep/Read/git log) for exact-term lookups. User-invocable via `/lr:recall [hint]`. Fans out across active agents when guests attached. See `lore-search-pattern.md`.

`/lr:workspace-sync` (v11) — clones any repos declared in `lore-repo.md` `repos:` lists that aren't yet present, then pulls every top-level git repo in the workspace. Hard rename of `/lr:pull-domain` (no alias). Delegates to `scripts/workspace-sync`. See `workspace-sync-utility.md`.

`/lr:doctor` (v12) — diagnoses runtime/environmental framework issues and applies (or guides) fixes via the ailment catalog. Distinct from `/lr:check` (content-level consistency) and `/lr:update` (version reconciliation). Targets issues that escape both — most commonly plugin-cache effects after upgrades. See `ailment-catalog-pattern.md`.

## Versioning & Migration

`lore-framework/VERSION` is the single source of truth (**currently `12`**). Each repo stamps this version in `lore-repo.md` frontmatter — one identifier per repo, no per-agent stamps.

**Two-track update flow (v3+):** each version bump may carry `migrations/<N>.md` (physical file changes, executed) and/or `release-notes/<N>.md` (informational, displayed). At least one must exist per version. v8 is **release-notes-only** (purely behavioral: merge-in-subagents, guest summaries, centralized commit+push, conflict resolution — none of which touches user-side files). **In-band BETA refinement (post-v10):** BETA features can be refined post-release without a `VERSION` bump or release-notes edit — edit the procedure doc, leave release notes historical, update lore at finalization. The BETA caveat in the release notes is the contract that licenses this. First observed instance: spawn-teammate boot-prompt reframe. Folded into `versioning-release-types.md`; promote to standalone topic if more BETA refinements accumulate. See `versioning-release-types.md`.

**Cache-affecting axis (v12+):** orthogonal to migration-vs-release-notes. Most release-notes-only versions are *also* cache-affecting because they change SKILL.md or referenced docs. v8 was rare: release-notes-only AND non-cache-affecting (purely behavioral). v11 and v12 are the typical shape: release-notes-only + cache-affecting. The **Clear Plugin Cache** footer is mandatory in release notes whose version touches `skills/`, `scripts/`, or any SKILL.md-referenced doc whose runtime behavior changes. Canonical wording in `lore-framework/docs/conventions.md` § Migration / Release-Note Authoring; `release-notes/12.md` is the worked example. Hoist the footer near the top, not the bottom — it's the single mandatory action and easy to miss in a long release-notes doc. See **`cache-clear-footer-convention.md`**.

`/lr:update [--dry-run]` reconciles user-side state: walks versions R+1 through F, applies migrations and shows release notes, stamps new version on success. Migrations must be idempotent. Dry-run previews changes without writing. Manual-edited generated files trigger a three-way merge with user confirmation. Uncommitted changes only — user reviews and commits themselves.

**Auto-upgrade at boot:** `agent-boot.md` checks version on every boot; runs the same walk automatically if behind. Uncommitted changes in the repo defer the upgrade. Boot continues in degraded mode on any failure. See `update-process.md`.

**Ownership-aware migrations (v5+):** user-side generated files fall into two buckets — framework-owned-stale (regenerate with three-way-merge on user edits) vs orphaned (prompt delete, never auto-remove). Filename alone is insufficient; ownership is the determining question. See `migration-ownership.md`.

**Template-emission audit:** plugin-compat leaks happen at template-emission sites, not just in runtime code. When changing file-reference conventions, audit every doc that emits content — `register-repo.md`, `create-repo.md`, migration docs. See `plugin-compat-template-audit.md`.

**Lore-curation disciplines on `VERSION` bumps (v12+):** every finalization that lands a new `VERSION` should:
1. Backfill `versioning-release-types.md` history with the new entry (kind + scope summary + cache-affecting annotation). No "we'll get to it later." The discipline applies to itself: v11 + v12 backfill happened during the v12 ship's finalization.
2. Author release notes with the Clear Plugin Cache footer if cache-affecting; hoist it near the top.
3. Promote any newly-discovered foundational principle to its own lore topic before declaring the design done. The v12 ship produced two such promotions: `cache-clear-footer-convention.md` and `ailment-catalog-pattern.md`.

These disciplines now live in `role.md` § Lore-Curation Disciplines.

## Plugin Distribution

Self-hosted marketplace at `github.com/zroslaw/lore-framework`. Install with `/plugin marketplace add zroslaw/lore-framework` then `/plugin install lr@lore-framework`. For local dev: `claude --plugin-dir ./lore-framework`. See `plugin-distribution.md`.

## Finalization Process (v9)

User-triggered, **four-phase**: `/lr:reflect` → `/lr:merge` → `/lr:summarize` → **commit+push** (or `/lr:finalize` for the full chain). See `finalization-process.md`, `docs/finalize.md`.

**Phase 1 — Reflect:** inline, host-first, per active agent. Stays inline because reflection needs session context.

**Phase 2 — Merge (v8):** **parallel subagents, one per active agent, each booted as its target** — uniform for single- and multi-agent sessions (a single-agent session just spawns one subagent). `general-purpose` subagents (merge needs Write/Edit/Bash). Each subagent runs `docs/process-merge.md` scoped to itself. Does not commit. See `merge-in-booted-subagents.md`. The inline-vs-subagent split between reflect and merge is deliberate — see `reflect-merge-execution-asymmetry.md` (rule: delegate when file-driven, keep inline when session-context-driven).

**Pre-publication review patterns (operational, not finalize phases):**

- **Sonnet single-lens role-as-perspective** — for high-stakes lore additions (principle topics, structural changes, public-facing doc edits): spawn a sonnet `general-purpose` subagent booted as the same agent to critique the change before continuing. Same role-as-lens mechanism as merge and `/lr:consult`, applied to review. Catches duplicated wording, muddled diagnostics, imprecise See Also descriptions, broken cross-references, unguarded claims. See **`sonnet-subagent-review-pattern.md`**.
- **Parallel multi-lens fan-out** — for shipped framework artifacts (scripts, skills, doc sweeps, schema changes, **and v12+ doc-only `VERSION` ships**): three parallel reviewers with mutually-exclusive lenses. v11 used correctness/security/UX (round 1) + terminology/newcomer/release-readiness (round 2). v12 (doc-only ship) used UX/discoverability + framework-architectural-consistency + correctness/safety with **filesystem verification**. Round 2 is worth running for verdict-grade ("ship as-is" vs "more rounds"), even if catch rate is low. The architecture lens reading the architect's own `lore-context.md` as a baseline is especially powerful — applies the architect's stated meta-rules to the change. The correctness lens running actual bash commands (filesystem verification) catches defects pure prose review misses (the v12 targeted-vs-broader cache-wipe was caught only because the reviewer ran `ls`/`cat`/`find` on the actual cache directory). See **`parallel-reviewer-fanout-pattern.md`**, and **`yaml-parser-shell-hardening-checklist.md`** for the operational distillation of the security lens.

Skip both for routine edits — overhead isn't worth it. Both patterns rely on the same boot-as-target-agent or boot-with-explicit-lens trick.

**Deferral discipline (corrective feedback):** when a sweep or polish task is bounded and mechanical, do it now — don't defer to a "vN.1 follow-up" if it fits in the current session's scope. The smell is: "We can do this later, it's just a sweep." If it's just a sweep, do the sweep. The legitimate backlog is for open-ended work, work needing real-world feedback first, or future capability. Applied recursively this session: the v11+v12 history backfill in `versioning-release-types.md` was a bounded mechanical task that fit the v12 ship — backfilled during the same finalization rather than deferred. See **`feedback-don-t-defer-completable-scope.md`**.

**`/lr:spawn-teammate` (v10, BETA):** Spawns lore agents as Claude Code Agent Teams teammates; current session becomes the team lead. Spawn prompt always uses `agent-boot.md` with absolute agent-dir path; no subagent-definition mode (skills/mcpServers not applied to teammates). Context inference + fuzzy matching for zero-arg case. **Design invariant (post-v10 in-band refinement):** the spawn prompt frames the user — in the teammate's own session — as the **primary interlocutor**; SendMessage is reserved for explicit user-requested coordination. This was reframed from the v10 initial "await further instructions from the team lead via SendMessage" after real-usage showed teammates defaulting to reporting back to the lead even when the user was driving them directly. Beta caveats: last-write-wins on concurrent lore writes, no automated cross-teammate finalization. Open graduation questions in `spawn-teammate-feature.md`. See also `autonomous-agents-substrate.md` (tmux/iTerm2 custom substrate, now parked while Agent Teams experiment runs).

**Phase 3 — Summarize (v9 change):** composed inline by the host. Writes the canonical session summary to the host agent's `sessions/YYYY/MM/` with a UUIDv4 in frontmatter, plus short guest summaries (v8) for attached guests with lore updates. **v9 removed the approval gate** — summarize writes directly; a new step 12 displays the host summary contents inline after write so the user sees what was recorded. Consultants never get a summary. The host must retain each merge subagent's return from phase 2 for phase 3 to compose guest summaries' lore-changes sections. See `session-summaries-feature.md`, `finalize-autopush.md`.

**Phase 4 — Commit+Push (v9 change):** one commit per touched repo, no approval prompt, then push. Default message: `Finalize session <short-uuid>`. Per-repo one-line confirmation is printed after each push. Standalone `/lr:reflect`, `/lr:merge`, `/lr:summarize` still leave changes uncommitted — only `/lr:finalize` touches git. Users wanting pre-commit review can invoke the standalone skills and commit manually. Privacy defense is now narrative-guidance-in-prompt only; post-hoc review via git history. See `finalize-autopush.md`.

**Push conflict resolution (v8):** on phase 4 push rejection inside an agent subtree, `docs/resolve-conflicts.md` spawns one booted `general-purpose` subagent per conflicted agent, capped at 3 total attempts. Scope: lore/lore-context/role only. Rule: "reconciliation, not invention." See `push-conflict-resolution.md`.

## Consistency Checks & Runtime Diagnostics

`/lr:check` runs 18 checks (content-level consistency). Descriptor validation (1–5): repo discovery via `lore-repo.md`, frontmatter validation, repo-level version consistency. Structural (6–8): registration, boot command paths, agent directory structure. Reference integrity (9–10): topic references. Size/state (11–13): lore-context size, pending reflections, uncommitted changes. Temporal/semantic (14–16): staleness, semantic consistency, boot command vs role.md. Drift/orphans (17–18, added v5): orphaned pre-plugin skill commands, legacy sibling-path boot commands. See `consistency-checks.md`.

`/lr:doctor` (v12, sibling of `/lr:check` and `/lr:update`) — diagnoses **runtime/environmental** issues that escape content-level checks and version reconciliation. The first shipped ailment is `doctor-stale-plugin-cache.md`. Catalog grows by accretion. See `ailment-catalog-pattern.md`.

## Key Constraints

- `lore-context.md` budget: ≤50K tokens
- Lore topics: atomic, <5K tokens preferred, plain markdown, no frontmatter
- Descriptor files: `lore-repo.md` has `description` + `version`; `role.md` has `description` only
- Command filenames: lowercase, numbers, hyphens only (max 64 chars)
- **Placeholder vocabulary (v5+, v11 update):** `<lore-agent-repo>`, `<guest-lore-agent-repo>`, `<agent-name>`, `<workspace>` (renamed from `<domain>` in v11), `${CLAUDE_PLUGIN_ROOT}` — see `placeholder-vocabulary.md`, `workspace-vs-domain-vocabulary.md`
- **CWD safety:** never `cd` in Bash when later tool calls depend on working directory; use `git -C <lore-agent-repo> …` — see `tooling-cwd-safety.md`

See `conventions.md` in `lore-framework/docs/`.

## Onboarding Doc Authoring

Co-authoring framework onboarding docs for individual teams adopting Lore Agents is part of the role (see `role.md`). The accumulated toolkit:

- **Identity-layer framings** (load before drafting): `framework-as-engine-not-kb.md`, `agents-are-executors-first.md`, `team-shared-knowledge-principle.md`.
- **What agents persist**: `knowledge-vs-skills-distinction.md`, `in-flight-skill-teaching-pattern.md`.
- **Dynamic + positioning**: `positive-feedback-loop-framing.md`, `agent-as-universal-working-environment.md`.
- **Reusable structure**: `onboarding-doc-narrative-pattern.md` — §1 four-beat narrative (status quo → why obvious fix fails → Lore Agents alternative → universal working environment), §3 Anatomy three-beat structure with directory tree visual aid, §4 grouped command reference, §2 meta-closer subsection that names the doc's own authoring loop. Tone rules (blockquote headlines, no "your X" for reader-state, terminology hygiene).
- **Use-cases authoring**: `use-cases-via-parallel-consult-pattern.md` — fan `/lr:consult` calls out in parallel (background) to the agents that actually did the work; weave returns; honor "nothing relevant" caveats.
- **Terminology hygiene**: `terminology-domain-collision-trap.md` — "Domain" is the LRF term *only*; use "area"/"subsystem"/"project" for the loose-English sense. Same applies to "Agent", "Skill", "Lore" — qualify on first use, watch adjacent occurrences.

When a team requests help, recall these and draft from them. First instance: Activities team's `LORE_AGENTS_INTRO.md` (~3 days of iteration v1; follow-up v2 added §3 Anatomy + §2 use-cases via parallel consults).

## Current State

Three repos in this workspace:
- `lore-framework/` — plugin. **`VERSION=12`**. v9: worktree convention, `/lr:init`, fully automated finalization (no approval gates). v10: `/lr:spawn-teammate` (BETA) — Agent Teams integration. v11: `/lr:workspace-sync` (hard rename of `/lr:pull-domain`), `repos:` field in `lore-repo.md`, full vocabulary sweep workspace-vs-domain. **v12: `/lr:doctor` skill with ailment catalog pattern; cache-clear-footer authoring convention codified in `docs/conventions.md`; first shipped ailment `doctor-stale-plugin-cache.md`.** Public: https://github.com/zroslaw/lore-framework. v12 ship commit: `b735777`.
- `lore-framework-dev/` (renamed from `lore-framework-agents/` earlier; in this workspace it's at the workspace root) — dedicated agent repo for framework development; houses `lore-architect`. Carved out from `lore-agents/` so framework design knowledge is team-shared and the plugin distribution stays slim. Stamped at the latest version. See `plugin-vs-agent-repo-separation.md`, `agent-discovery-nesting-constraint.md`.
- `lore-agents/` — two personal agents: masschallenge-judge, tax-advisor.

Lore topics (~55 after this merge): `architecture-overview.md`, `system-design-principles.md`, `finalization-process.md`, `lore-topic-format.md`, `slash-command-system.md`, `domain-directory-concept.md`, `consistency-checks.md`, `plugin-distribution.md`, `workspace-sync-utility.md` (was `pull-domain-utility.md`, v11), `workdir-as-reference-library.md`, `update-process.md`, `skill-doc-pattern.md`, `versioning-release-types.md` (v11+v12 history backfilled, cache-affecting axis added), `lore-search-pattern.md`, `attach-pattern.md`, `consult-pattern.md`, `design-doc-before-implement.md`, `vector-db-search-parked.md`, `tooling-cwd-safety.md`, `plugin-compat-template-audit.md`, `placeholder-vocabulary.md`, `migration-ownership.md`, `session-summaries-feature.md`, `jsonl-session-files-investigation.md`, `merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`, `push-conflict-resolution.md`, `framework-scope-vs-agent-scope.md`, `worktrees-convention.md`, `lr-init-feature.md`, `finalize-autopush.md`, `framework-improvements-backlog.md`, `autonomous-agents-vision.md`, `autonomous-agents-substrate.md`, `spawn-teammate-feature.md`, `team-shared-knowledge-principle.md`, `naming-foundational-principles.md`, `plugin-vs-agent-repo-separation.md`, `agent-discovery-nesting-constraint.md`, `sonnet-subagent-review-pattern.md`, `framework-as-engine-not-kb.md`, `agents-are-executors-first.md`, `knowledge-vs-skills-distinction.md`, `positive-feedback-loop-framing.md`, `agent-as-universal-working-environment.md`, `onboarding-doc-narrative-pattern.md`, `terminology-domain-collision-trap.md`, `in-flight-skill-teaching-pattern.md`, `use-cases-via-parallel-consult-pattern.md`, `workspace-vs-domain-vocabulary.md`, `yaml-parser-shell-hardening-checklist.md`, `parallel-reviewer-fanout-pattern.md` (extended for doc-only edits), `feedback-don-t-defer-completable-scope.md`, **`ailment-catalog-pattern.md`** (v12 — case-decomposition variant of skill-doc-pattern), **`cache-clear-footer-convention.md`** (v12 — release-notes authoring convention).

## Active Design Explorations

**Autonomous lore agents** (parked vision, major direction) — re-frame lore agents from session-bound interactive workers to always-on background collaborators with persistent task state, raising for user input only when needed. Concrete first step: `/lr:spawn-teammate` via Agent Teams (v10). Custom macOS substrate (tmux + iTerm2 Python API + Claude Code hooks + switchboard daemon) parked while Agent Teams experiment runs. See `autonomous-agents-vision.md`, `autonomous-agents-substrate.md`, `spawn-teammate-feature.md`.

**Workdir as reference library** (parked) — using `workdir/` as a structured knowledge base alongside lore. Lore = experiential (in your head), workdir docs = curated reference material (on your desk). No new framework machinery needed. Most valuable for domain-heavy agents. Draft ideation doc in `workdir/draft-workdir-as-knowledge-base.md`. See `workdir-as-reference-library.md`. Likely candidate for specialist/guest agents introduced with v4's attach pattern. Composes well with autonomous-agents direction (autonomous agents accumulate workdir artifacts heavily).

**Vector DB search** (parked) — Chroma-backed semantic search over lore topics, with incremental git-based index updates. Deferred until subagent-scan pattern becomes impractical (rough trigger: >100 topics per agent). See `vector-db-search-parked.md`.

**Consult-feedback back-channel** (deferred) — a formal mechanism for the host to route newly-learned content back to the consultant's reflection queue after `/lr:consult`. Left out in v4 to keep consult genuinely lightweight. Revisit if users accumulate stale consultant lore relative to how it's actually used.

**Ailment catalog growth** (active, v12+) — catalog members accrete from real-world cases, not pre-population. Candidates tracked in `framework-improvements-backlog.md` § Ailment Catalog. Universality gate keeps the catalog framework-scoped (repo/host/workflow specifics belong elsewhere). See `ailment-catalog-pattern.md`.

## Running Backlog

See `framework-improvements-backlog.md` for the canonical list of deferred items, open questions, and possible-future-work entries. Read at the start of framework-design sessions — surprises emerge from the accumulation.
