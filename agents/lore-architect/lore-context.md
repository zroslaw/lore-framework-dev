# Lore Context

Compacted working knowledge for the **lore-architect**. This is the entry point to the lore graph, not a catalog — each theme points at its summary topic, which fans out to detail. For exhaustive lookup, scan `lore/` directly. (This doc follows the `lore-context` shape discipline: working-knowledge + summary-topic references, present-tense, no index, no version-history narrative — see `process-merge.md` § Step 4.)

## Soft Skills (surface at boot)

Behavioral working-style guidance carried with the agent, updated on user feedback (vs. "hard" skills shipped in deliberately-installed repos). **State available opt-in soft skills at boot so the user knows them.**

- **Follow-me mode** (opt-in, off by default) — when the user says "follow me", track their thinking direction; don't race ahead or overtake it; small suggestions only. See `soft-skill-follow-me-mode.md`. (The framework-level "soft skills as an explicit entity" concept is open — see `framework-improvements-backlog.md`.)

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

Operations are Claude Code plugin skills, `lr:` prefix. **Skills are thin pointers** — each `skills/<name>/SKILL.md` is a one-line reference to `docs/<name>.md`, where all logic lives. Same for generated `/lr-<agent>-agent` boot commands (thin delegations to `agent-boot.md`). When a skill orchestrates sub-skills, the orchestration gets its own `docs/<skill>.md`; non-skill procedures shared across call sites get a `docs/<procedure>.md` (e.g. `auto-pull.md`). See `slash-command-system.md`, `skill-doc-pattern.md`, `shared-procedure-doc-pattern.md`, `single-canonical-source-discipline.md`.

The plugin can also **bundle an MCP server** (declared in a root `.mcp.json`, auto-launched by Claude Code with its tools merged into the agent): **`lr-wait`** (v18) is the first — and the framework's first `python3` dependency (stdlib-only, no pip; the sole sanctioned exception to bash-on-BSD, for protocol-speaking server components). See `plugin-mcp-server-convention.md`, `wait-primitive-feature.md`.

## Boot & Freshness

Boot (`agent-boot.md`, single source of truth): discover agent → auto-pull repo → version check → read `role.md` + `lore-context.md` → detect teammate spawn → confirm. **Boot loads only those two files; topics are read on demand.** Repos auto-pull at every session-context boundary (boot, attach, pre-merge) to match the team's latest pushed state; `/lr:pull-lore` is the manual refresh. See `freshness-contracts-at-session-boundaries.md`, `auto-pull-mechanism.md`.

## Cross-Agent Collaboration

- **`/lr:recall [hint]`** — search lore of already-loaded agents (host + guests); fan-out per agent.
- **`/lr:consult <agent> [hint]`** — one-shot question to an unloaded agent; a subagent boots it, answers with file pointers, exits.
- **`/lr:attach <agent>`** — load another agent as a sustained guest; host stays sole executor, host-wins on conflicts.
- **`/lr:spawn-teammate` (BETA)** — spawn agents as Agent Teams teammates for parallel panes; the teammate's primary interlocutor is the user, not the lead.

See `lore-search-pattern.md`, `consult-pattern.md`, `attach-pattern.md`, `spawn-teammate-feature.md`, `teammate-conventions.md`.

## Finalization

User-triggered, four phases (`/lr:finalize` runs all; phases also run standalone): **reflect** (inline, host-first, per agent — needs session context) → **merge** (parallel subagents, one per agent booted as itself, file-driven — integrates reflections into `lore/`, `lore-context.md`, `role.md`) → **summarize** (host writes the canonical session summary + short guest summaries) → **commit+push** (one commit per touched repo; conflict-resolution on push rejection). Do not finalize unless the user triggers it. See `finalization-process.md`, `finalize.md`, `merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`.

## Versioning & Migration

`lore-framework/VERSION` (currently **18** — bump built on disk, commit pending) is the single source of truth; each repo stamps it in `lore-repo.md`. Plugin manifests mirror it as `1.<VERSION>.0` — the cache-detection lever (`/lr:check #19`). Each version may carry `migrations/<N>.md` (executed) and/or `release-notes/<N>.md` (shown); at least one. `/lr:update` and boot auto-upgrade walk versions forward, applying migrations and stamping; the upgrade gate defers on a `dirty ∩ write-set` collision. Cache-affecting versions (touch skills/scripts/referenced docs) need the Clear Plugin Cache footer. See `versioning-release-types.md`, `update-process.md`, `plugin-manifest-versioning.md`, `dirty-tree-gates-write-vs-read-distinction.md`.

## Consistency & Diagnostics

- **`/lr:check`** — 20 content-consistency checks (descriptor/version, structure, references, size/state, drift, plugin-manifest #19, migration write-paths #20). See `consistency-checks.md`.
- **`/lr:doctor`** — diagnoses runtime/environmental issues that escape content checks (esp. stale plugin cache) via an accreting ailment catalog. See `ailment-catalog-pattern.md`.

## Operating Disciplines

How I work, especially at version ships and high-stakes lore edits:
- **On VERSION bumps:** backfill `versioning-release-types.md` history, add the cache-clear footer if cache-affecting, bump both plugin manifests to `1.<VERSION>.0`, promote any newly-named principle to its own topic. (Full curation disciplines live in `role.md`.)
- **Pre-ship review:** multi-lens parallel-reviewer fan-out, iterated until a round finds nothing worth fixing (convergence is the ship signal); sonnet boot-as-self review for high-stakes single edits. See `parallel-reviewer-fanout-pattern.md`, `sonnet-subagent-review-pattern.md`.
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

Co-authoring framework onboarding docs for adopting teams is part of the role. Load the identity-layer framings first, then the toolkit: `onboarding-doc-narrative-pattern.md`, `use-cases-via-parallel-consult-pattern.md`, `terminology-domain-collision-trap.md`, `agent-as-universal-working-environment.md`, `in-flight-skill-teaching-pattern.md`. First instance: the Activities team's intro doc.

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — major direction; a `lr` module for SDLC automation toward an autonomous "dark factory" SDLC. Per-repo artifacts + narrative context live in a `<repo>-df` backbone (a `repo-lore/<file>/` mirror: `file-lore.md` narrative landing + flat structured aspect subdirs like `ula/`). Skills not agents; persistence external. First aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`) — unit-level analysis with a bug-verification track, BETA. The DF/ULA design thread is closed and the module ships as BETA. Anchor: `lr-dev-direction.md`; see `df-per-repo-backbone.md`, `aiqa-ula-feature.md`, `df-module-conventions.md`, `workflow-primitive-operational-notes.md`.
- **Autonomous agents** (parked vision) — agents as always-on background collaborators with persistent task state, raising for input only when needed. Concrete steps taken: `/lr:spawn-teammate` (multi-agent substrate, v10) and the v18 **`lr-wait`** primitive — the first *inbound-signal* step: an agent blocks on an event and an external actor (cron/CI/webhook/human, via `lr-emit`) wakes it with text. See `autonomous-agents-vision.md`, `autonomous-agents-substrate.md`, `wait-primitive-feature.md`.
- **Multi-engine portability (Codex, Cursor)** — major direction, user-raised 2026-07-02; Claude Code stays the major version, goal is Tier-1-parity ports so mixed-engine teams can share one team-shared agent repo. The knowledge substrate (agent repos, `lore-repo.md`, `role.md`, `lore/`, `lore-context.md`, git) is already engine-agnostic — SKILL.md is now an open standard both engines support, AGENTS.md is native to both, MCP ports `lr-wait` unchanged — so the port is mostly packaging, not redesign. Key lever: a `docs/engines/` adapter convention replacing hardcoded Claude-specific phrasing (`${CLAUDE_PLUGIN_ROOT}` → `<framework-root>`) with a small per-engine binding. Dominant shared risk: the framework is prose executed by the model — merge-procedure fidelity on non-Claude models is unverified. Parked vision with two full workdir drafts (`workdir/draft-port-codex.md`, `workdir/draft-port-cursor.md`), not yet started. Anchor: `multi-engine-portability-direction.md`; see `similar-projects-landscape.md` (the positioning case this unlocks — no surveyed competitor federates knowledge across different coding engines).
- **Lore housekeeping / consolidation "sleep" pass** and the **simplification/subtraction** review item — active follow-ups from the 2026-06-13 architecture review; see `framework-improvements-backlog.md`. That review's settled dispositions (incl. DF-inside-`lr` and team-shared/multi-author as deliberate, not defects — don't re-raise) live in `architecture-review-dispositions.md`. A newer 2026-07-02 review added two further backlog items (post-merge diff verification, recall-time staleness surfacing) — see `framework-improvements-backlog.md` § Merge Quality, § Search / Scaling.
- Parked: workdir-as-reference-library; vector-DB search (until >100 topics/agent); the session-as-durable-artifact cluster (boot auto-push, boot-context cache, suspend/resume, JSONL archive). All in `framework-improvements-backlog.md`.

## Current State

Workspace holds three repos: **`lore-framework/`** (plugin, VERSION 18 — built, commit pending; public at github.com/zroslaw/lore-framework), **`lore-framework-dev/`** (this repo — framework-dev agents; a workspace-root sibling at github.com/zroslaw/lore-framework-dev), **`lore-agents/`** (personal agents: tax-advisor, masschallenge-judge). The plugin now bundles its first MCP server (`lr-wait`, v18) and carries its first `python3` dependency; dev-only tests live here in `lore-framework-dev/tests/`, not in the plugin. ~93 lore topics.

## Running Backlog

`framework-improvements-backlog.md` is the canonical list of deferred items and open questions. Read it at the start of framework-design sessions — surprises emerge from the accumulation.
