Running backlog of framework-level improvements, deferred items, and open questions. Maintained by the lore-architect. Check and add to this as design conversations close without shipping everything, or as real-world usage surfaces gaps.

Items are grouped by area. Each has a one-line what + why + rough trigger or status. Promote an item into its own lore topic (and its own design draft in `workdir/`) when it becomes active.

## Init / Workspace Bootstrap

- **Workspace creation automation** — a scaffolding command or flow that creates a new workspace, optionally with an agent repo initialized, a `README.md` carrying setup instructions, and an auto-invocation of `/lr:init`. Status: partially addressed by v11's `/lr:workspace-sync` (the *consumer* side — bootstrap an existing workspace from one cloned agent repo). The *producer* side (initial scaffolding from nothing) is still deferred; revisit when we have more than one hand-built workspace.
- **Richer `/lr:init` payloads** — v1 payload was only the worktree convention; v11 renamed the header from "Lore Framework Domain" to "Lore Framework Workspace" but didn't grow the body. Future additions planned: workspace intro, list of registered agents, invocation tips (`/lr-<agent>-agent` shortcuts), links to framework docs. All extend the same `<!-- lr:init -->` marker block; mechanism unchanged. Trigger: user feedback on what's missing from the workspace CLAUDE.md; framework features that want visibility at session start.
- **Sync CLAUDE.md on framework version bump** — v11 changed the payload header; users have to rerun `/lr:init` manually to refresh. Options for future: `/lr:update` chains `/lr:init`; boot checks payload version and prompts. Decide when the next payload-changing version lands.
- **Booted-agent nudge for un-initialized workspace** — originally proposed: at boot, check for `<!-- lr:init -->` markers; if absent, emit a one-line suggestion to run `/lr:init`. Dropped in v9 as too complicated. User prefers the future workspace-creation-automation path to solve discovery.

## Worktree Convention

- **Invariant enforcement in `/lr:check`** — warn when a top-level repo dir is on a non-default branch (violating the worktree-convention invariant). Cheap check (a git command per repo). Trigger: drift observed in real use. See `worktrees-convention.md`.
- **Orphan-worktree / orphan-note checks** — optionally flag worktrees in `.worktrees/` with no tracking note in `agents/<name>/worktrees/`, or notes with no corresponding worktree. Weak signal (the note pattern is opt-in). Defer unless agents widely adopt the note convention.
- **Branch-naming convention check** — verify branches in worktrees follow the suggested `<agent-name>/<slug>` form. Very opinionated; probably never needed.

## Finalization / Autopush

- **Audit log of pushed summaries** — since the user no longer sees summaries pre-commit, a local audit trail (e.g., a `sessions-index.md` at the host repo root, appended to on each finalize) could help spot issues faster than browsing git history. Trigger: user reports missing a problematic summary.
- **Per-session opt-in gate flag** — `/lr:finalize --review` that restores the old approval flow for sensitive sessions. Cheap to add. Trigger: user asks for it at least twice.
- **Narrative-safety linter** — lightweight check on composed summary text before write (secrets regex, etc.). Adds machinery; currently relying on agent judgment per v9 design. Defer unless a real privacy incident occurs.

## Documentation / Meta

- ~~**README skills table sync**~~ — done in v11. Table now lists all skills, grouped by purpose (workspace setup / working with agents / session lifecycle / authoring / maintenance), with `/lr:finalize` description corrected to the four-phase form. Quick Start was also restructured to lead with the team-joining path.
- **README skill table refresh for v12** — verify `/lr:doctor` is added to the skills table (Maintenance group is the natural home). Trigger: next time the README is touched, or sooner if asked.
- **Markdown-renderer compatibility for HTML-comment markers** — `/lr:init` uses `<!-- lr:init:start -->` markers. Some renderers strip HTML comments. If any user's tooling bites on this, switch to visible sentinel headings. No action until observed.
- **Consolidated "framework conventions" doc** — there's `conventions.md`, `worktrees.md`, `skill-doc-pattern.md`-type rules scattered. At some size, a single index or "start here" doc could help. Not urgent.
- **Broken `contributions-feature.md` reference in `framework-scope-vs-agent-scope.md`** — its See Also points to `contributions-feature.md` which doesn't exist in `lore/`. Pre-existing dangling link; worth a cleanup pass on See Also sections across topics. Open sub-question: `/lr:check` claims reference integrity (checks 9–10 per `consistency-checks.md`) but this dangling link persists — either the check covers something narrower or it has a gap. Investigate during a future framework-maintenance session.
- **`agent-boot.md` team-shared framing note (open decision)** — the team-shared-knowledge principle is now named in lore and surfaced in the public README. Open question: should `agent-boot.md` (the universal boot procedure) also carry a one-line framing note so every agent at boot time understands its workspace is team-shared? Pro: universal applicability — every agent inherits the framing without depending on whether their specific lore captures it. Con: scope-creep into universal machinery; risk of cluttering the boot procedure with conceptual content; possibly redundant with README. Surfaced by the sonnet review; not yet decided.

## Soft Skills vs Hard Skills (concept — elaborate later)

- **Make "soft skills" an explicit framework entity.** User-raised 2026-06-03. The distinction: **hard skills** are shipped in separate repos and installed deliberately — "hard" because they're hard to change and control. **Soft skills** travel *with the lore agent itself* — behavioral/working-style guidance the agent carries and continuously updates when the user is unhappy or tells it explicitly. They are easy to change because they live next to the agent, not in a distributed package. First concrete instance (the seed for this concept): "follow the user's thinking direction, don't over-think ahead or overtake the direction; suggest small improvements only." Open design questions for later: where soft skills physically live (lore topic? dedicated `soft-skills/` dir? part of `role.md`/`lore-context.md`?), how they're updated (passively via reflection vs. actively on explicit feedback), how they relate to the existing `knowledge-vs-skills-distinction.md` (soft skills look like a *third* category, or a sub-kind of the "skills" axis), and how they're surfaced at boot. Do **not** design now — flagged for a dedicated session. See `knowledge-vs-skills-distinction.md`, `in-flight-skill-teaching-pattern.md`.

## Cross-Agent Collaboration

- **Consult-feedback back-channel** — formal mechanism for the host to route newly-learned content back to the consultant's reflection queue after `/lr:consult`. Left out in v4 to keep consult lightweight. Revisit if users accumulate stale consultant lore relative to how it's actually used.
- **Host-wins vs interactive conflict resolution for lore overlaps** — current rule is host-wins on lore conflicts during attach. Might want finer control. Not an active issue.

## Search / Scaling

- **Vector DB search** — Chroma-backed semantic search over lore topics with incremental git-based index updates. Parked until subagent-scan pattern becomes impractical (rough trigger: >100 topics per agent). See `vector-db-search-parked.md`.
- **Workdir as reference library** — parked exploration of using `workdir/` as a structured knowledge base alongside lore. Lore = experiential, workdir = curated reference. Most valuable for domain-heavy specialists. No framework machinery planned — patterns emerge per agent. See `workdir-as-reference-library.md`.

## Autonomous Agents (major direction)

- **Autonomous background agents** — re-frame lore agents from session-bound interactive workers to always-on collaborators with persistent task state, asking for input only when needed. Implications across process model (daemonization), state model (task state, not just lore), communication model (agent → user channels), reflection model (autonomous reflect triggering), and multi-agent surface (switchboard for N parallel agents). Status: parked vision, no design doc yet. Concrete first step: `/lr:spawn-teammate` via Agent Teams. See `autonomous-agents-vision.md`.
- **Autonomous-agents substrate findings** — concrete macOS building blocks identified: tmux for the process layer, iTerm2 Python API for GUI control, Claude Code hooks (`Stop`, `Notification`, etc.) as the signal source (strictly superior to regex triggers), escape sequences for status surface (tab color/title), `terminal-notifier` for click-actionable notifications, and a Python switchboard daemon under `launchd` for orchestration. Security: never bind `0.0.0.0` without auth — RCE risk; prefer narrow HTTP API in front of the iTerm2 socket over raw socket exposure. Parked while Agent Teams experiment runs. See `autonomous-agents-substrate.md`.

## lr-dev (SDLC Extension — major direction)

New module/mode for development & SDLC automation; first feature is bug-finding & test-coverage. Anchor topic: `lr-dev-direction.md`. Full design in `workdir/draft-lr-dev.md` + `workdir/draft-lr-dev-quality.md` (active exploration). North star: autonomous "dark-factory" SDLC (see `autonomous-agents-vision.md`).

**Direction reframed 2026-06-01 — context agents on existing primitives** (now leading; the three-tier / new-repo-kind / two-gate design is the superseded heavier alternative). Per-repo artifact knowledge is custodied by an ordinary **context agent** (one per source repo), housed in a shared per-repo agent repo. This dissolves most of the backlog items that were specific to the old machinery — see the struck items below. New framings landed as lore topics: `framework-defined-role-pattern.md`, `agent-split-only-when-forced.md`. See `lr-dev-direction.md` § Leading direction, `workdir/draft-lr-dev.md` §1A.

**First in-plugin BETA feature shipped 2026-06-03 (local, v16 deferred):** AIQA/ULA — `/lr:dev-aiqa-repo-init` + `/lr:dev-ula-file`. Layout: `dev/aiqa/` module subtree with `dev-` skill prefix. See `aiqa-ula-feature.md`, `dev-module-conventions.md`.

- ~~**Migrations must walk the new repo kind**~~ — *moot under the reframe.* No new `dev-repo-lore.md` repo kind; a context agent's normal `lore-repo.md` is already walked by `/lr:update`, boot auto-upgrade, and version-check/auto-pull. (Was: repo-lore stores would carry their own framework `version` needing recognition/migration/stamping.)
- ~~**Three-tier knowledge model + repo lore (write-gated)**~~ — *superseded.* No middle tier and no two-gate write capability; per-repo knowledge is an ordinary agent's lore (written only by that agent via reflect/merge — native write-isolation). The objective/subjective cut survives as reflection discipline, and the agent-agnostic property via housing in a shared per-repo agent repo. The `product/` ÷ `technical/` split is a filing-category dir inside the one context agent (`agent-split-only-when-forced.md`), not separate tiers/agents. See `lr-dev-direction.md`, draft §1A.
- **Reusable multi-lens review skill** — promote `parallel-reviewer-fanout-pattern.md` to an lr-dev skill (`lr:dev-review`) usable for any code change. *Survives the reframe.* See draft §6.
- **Context-agent generator** — a flag on `/lr:create-agent` or a dedicated generator skill that emits a context agent from a template + thin role pointer (`framework-defined-role-pattern.md`). New item from the reframe.
- **Open seams** — file-mirror placement inside the context agent's `lore/` + staleness between non-lr-dev touches; specialist÷context attach/consult ergonomics; scenario→code binding; generated-vs-human de-dup. Tracked in `lr-dev-direction.md` § Open decisions and draft §9.
- **Quality-repo conventions** — file/dir layout (`reports/`, `bugs/`, `scenarios/`, `tests/`, `manifest.yaml`), composite-build template, retention/pruning policy, manifest schema (per-file `path` / `lastAnalyzedSha` / `status` / `lastRunId`). New item from `quality-repo-architecture.md`. May graduate into a generator skill (`/lr:dev-quality-init <source-repo>`).
- **Promote the file-quality workflow script** — the prototype lives in `workdir/draft-lr-dev-file-quality-workflow.js`. When stable, move to the plugin's `workflows/` dir (or a `lore-dev` sibling plugin) so it's invokable as `Workflow({ name })` rather than `Workflow({ scriptPath })`. New item from the prototype.
- **Whole-repo sweep skill** — `lr:dev-quality-sweep`: orchestrator that reads the manifest, picks N stale files, runs the per-file workflow on each, persists File Reports, updates the manifest. Daily-cron-friendly (budgeted bottom-N rolling). Sits on top of the per-file workflow; depends on quality-repo conventions.

## `/lr:spawn-teammate` Beta Graduation

- **Lore-write serialization** — concurrent teammates write last-write-wins. Is file-lock/queued-merge needed or is "defer lore-changing work to finalization" sufficient?
- **Automated teammate finalization** — lead triggering finalization on all teammates before disbanding via SendMessage channel. Explore.
- **Hook integration** — test whether `Stop`/`Notification` hooks fire in teammate sessions; could automate teammate finalization.
- **Subagent-definition mode** — track if Agent Teams adds `skills`/`mcpServers` support; would enable more explicit spawning.
- **`/lr:check` validators** — add checks for Agent Teams enabled, teammate boot paths valid. Deferred until usage shows what to check.
- **Finalize/summarize consistency with teammate model** — those docs were designed for host+attached-guest; verify they compose correctly with Agent Teams' separate teammate sessions.
- **User-primary-interlocutor framing** — graduation invariant or tunable? Currently locked as a design invariant in BETA after the post-v10 boot-prompt reframe.

See `spawn-teammate-feature.md` for full beta graduation question list.

## Session Summaries

- **Compaction-aware narrative quality** — on long sessions, auto-compaction may drop or compress earlier turns; summaries skew toward late-session work and can hallucinate earlier events. Current mitigation: prompt instructs the model to note "early-session hazy" rather than confabulate (weak). Possible directions: landmark scratch file written during the session for summarize to cross-reference; bounded read of the session JSONL isolated to this site; accept bias and rely on in-session summarization cadence. Trigger: systematic bias observed when reviewing the summary corpus.
- **Cross-repo guest participation gap (partial)** — v8 added short guest summaries for guests that had lore updates. Guests attached but with no lore updates still leave no trace in their own repo. Minor gap; revisit if cross-repo specialist agents become common. Fully solving requires pointer-file-on-attach or similar convention.
- **Reliable start-time capture** — summary frontmatter `start` is best-effort from session memory, rounded to nearest 5 minutes. Options: `agent-boot.md` writes `.session-started` marker for summarize to read+delete; minimal one-field read from session JSONL's first-line `timestamp` (shape-stable); formalize "approximate, best-effort" in the schema and move on. See `session-summaries-feature.md`.

## Process

- **Reflect-merge ergonomics** — writing reflections then merging them has overhead for single-agent sessions with trivial deltas. Inline shortcut for "just write to lore directly" is sometimes more pragmatic. Document when to shortcut vs when to go through the full flow.

## Ailment Catalog (`/lr:doctor`, v12)

- **Accretion candidates** — additional ailments to capture when real-world cases surface: workspace-sync conflict shapes, common merge-conflict reconciliation recipes, onboarding-doc anti-patterns (terminology/framing traps), agent boot failures from missing `lore-repo.md`/`role.md` files, registered command desynced from agent name. Add as cases distill from real usage; do not pre-populate. See `ailment-catalog-pattern.md`.
- **Ailment-discovery hook in finalization** — when a session diagnoses an issue not yet in the catalog, the finalize flow should prompt: "Was this an ailment? Add a `doctor-<slug>.md` topic?" Lightweight discipline cue. Trigger: after enough sessions where catalog gaps were noticed only after the fact.
- **`/lr:check` cross-reference to `/lr:doctor`** — already added in v12 (one-line cross-ref in `check.md` and `update.md`). If users discover further gaps where `/lr:check` reports clean but a runtime issue persists, that's the signal to add a new ailment.

## Workspace-Sync (`/lr:workspace-sync`, v11)

- **`repos:` validators in `/lr:check`** — verify URL syntax (parseable, has scheme), reachability (probe with `git ls-remote`, run sparingly because network), dir-name collision (two declared URLs deriving the same dir name across descriptors). Not added in v11 by design — wait until usage shows what to check. Trigger: user reports stale or broken URL lists; multi-domain workspaces accumulate friction. See `workspace-sync-utility.md`.
- **Undeclared-top-level-repo nudge** — when `/lr:workspace-sync` finishes and there are top-level git repos in the workspace that aren't declared in any `repos:` field, print a one-liner: *"N undeclared top-level repos: foo, bar, baz. Add to a lore-repo.md `repos:` block to share workspace structure."* Contextual nudge, not a guide. Cheap to add. Trigger: real adopters with multi-domain workspaces want their setups to bootstrap for teammates.
- **Per-entry overrides in `repos:`** — schema currently is a flat URL list. Branch pinning, custom dir name, depth, etc. would need an object-form entry: `{ url: ..., branch: ..., dir: ... }`. Defer until real-world usage demands it; v11 schema is deliberately tight. See `workspace-sync.md` Limitations.
- **Inline-flow form (`repos: [a, b]`)** — deliberately not supported in v11 to keep the awk parser surface small. Reconsider only if users complain.
- **workspace-sync BatchMode behavior-change note (v14, doc follow-up)** — v14 added `GIT_SSH_COMMAND` `BatchMode=yes` to `scripts/workspace-sync`; SSH keys needing an interactive passphrase (not in an ssh-agent), or unknown host keys, now fail-fast instead of prompting. Correct for parallel jobs, but currently undocumented — add a one-line note to `release-notes/14.md` § workspace-sync (or a future release-notes). Low-severity `/code-review` finding, shipped as-is. See `portable-shell-in-framework-docs.md`.

## Consistency Checks (`/lr:check`) & Plugin Manifest (v14, v15)

- **check #19 — skip a missing `marketplace.json` gracefully.** Check #19 reads `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/marketplace.json` unconditionally. It's co-located for this plugin (source `"./"`), but co-location isn't guaranteed for all install/cache layouts (a marketplace-install cache may carry only `plugin.json`). Make the `marketplace.json` half conditional on the file existing, rather than erroring. Low-severity `/code-review` finding, shipped as-is. See `consistency-checks.md`, `plugin-manifest-versioning.md`. (`docs/check.md`)
- **Verify whether a manifest-version bump alone triggers Claude Code cache auto-invalidation.** If a `1.<VERSION>.0` manifest bump *alone* makes the platform refresh its cache (not merely *detect* the release), the manual Clear Plugin Cache footer could become optional. Test with a real marketplace install + restart — verify empirically before dropping the footer (`verify-before-acting-on-suspected-bugs.md`). Open question from `plugin-manifest-versioning.md`.

## Write-Aware Gate / Migration Write Paths (v15)

- **Bring the v15 collision-check gate to `/lr:update`.** Currently `/lr:update` is interactive-by-design and writes through dirty files unconditionally. Bringing the `dirty ∩ write-set` gate to it would make the principle universal across automatic and user-invoked write paths. Trade-off: `/lr:update` is interactive so the friction trade is different (the user is already at the keyboard), but a same-shape gate would still prevent accidental overwrites. See `dirty-tree-gates-write-vs-read-distinction.md`.
- **A3-arch deferred to v16.** The architecture-lens finding from a late v15 review round, deferred so v15 could ship. Carry forward to v16 design discussions; the specific finding is in the v15 review notes (round-by-round summary in `parallel-reviewer-fanout-pattern.md` § v15 operational lessons).
- **Workspace-root paths gap (documented, not fixed).** The boot-time gate is per-repo and cannot see workspace-root files (`.claude/commands/lr-*-agent.md`). v15 documents this in `conventions.md` § Known gap; protection there is the in-migration three-way merge, not the gate. Fix would require a workspace-aware gate layer; defer until a real bug surfaces.

## Workspace Topology

- **Discovery gap for nested agent repos** — workspace discovery scans direct subdirectories of cwd only; nested agent repos are invisible to `/lr:list-*`, `/lr:check`, `/lr:recall`, `/lr:workspace-sync`, `/lr:spawn-teammate`, `/lr:boot`. Currently `lore-framework-dev/` is nested inside `lore-framework/` as a temporary placement, reachable only via the registered `/lr-lore-architect-agent` shortcut. User will extract to a workspace-root sibling on its own GitHub repo. Tracked here for the eventual move; deeper question of whether discovery should walk one level (or accept a config-file hint) is open if nested layouts become a recurring pattern. See `agent-discovery-nesting-constraint.md`, `plugin-vs-agent-repo-separation.md`.

## Agent Teams / Spawn-Teammate (additions)

- **Real-world trial run for `/lr:spawn-teammate`** — `~/.claude/settings.json` now sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (configured this session). Next session after Claude Code restart, `/lr:spawn-teammate` is usable. Worth a real trial on framework work — the feature is BETA with open design questions (last-write-wins lore serialization, finalization across teammates). First usage will inform graduation. See `spawn-teammate-feature.md` for the open beta questions.

## How To Use This Backlog

- Add a bullet when an idea comes up during design but won't ship this session.
- Promote to its own lore topic + workdir draft when it becomes active work.
- Delete bullets that become moot (e.g., if a new framework mechanism obsoletes them).
- Reread at the start of framework-design sessions — surprises emerge from the accumulation.

## See Also

- `workdir/draft-lr-init-feature.md` — design session that established the v9 deferred list (many items above originate there)
- `design-doc-before-implement.md` — why active items get a workdir draft before framework-file edits
- `framework-scope-vs-agent-scope.md` — test for whether a proposed framework item belongs here or in agent-owned territory
- `feedback-don-t-defer-completable-scope.md` — when *not* to add to this backlog: bounded mechanical sweeps belong in the current ship, not deferred
