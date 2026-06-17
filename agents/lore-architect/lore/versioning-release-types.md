Starting with v3, framework version bumps can carry two kinds of artifacts:

**Migration** (`migrations/<N>.md`) — physical instructions to modify user-side repo files (frontmatter updates, file regenerations, directory restructures). Executed by `/lr:update` and the auto-upgrade-at-boot. Must be idempotent.

**Release notes** (`release-notes/<N>.md`) — informational only; describes what's new in version N. Displayed to the user, not executed. No user-side file edits required.

## Rules for authoring a new version bump

- User-side file changes required → create `migrations/<N>.md`
- Feature/doc additions only → create only `release-notes/<N>.md`
- Large release with both → create both
- **At least one must exist** — the update process treats a gap as a framework packaging bug
- **If the version is cache-affecting** (touches `skills/`, `scripts/`, or any `docs/<name>.md` referenced by a SKILL.md whose runtime behavior changes), include the **Clear Plugin Cache** footer per `cache-clear-footer-convention.md`. The cache-affecting axis is **orthogonal** to the migration-vs-release-notes axis.

## Cache-propagation levers (two, as of v14)

Two distinct, complementary mechanisms make the platform pick up a cache-affecting release — orthogonal to both the migration-vs-release-notes axis and the cache-affecting flag:

1. **Plugin manifest version bump (v14+)** — set `version` to `1.<VERSION>.0` in `plugin.json` + `marketplace.json`. This is what lets Claude Code *detect* a new release at all (the manifests sat frozen at `1.0.0` v1–v13, so the platform never saw a new release — the root cause of years of cache pain). See `plugin-manifest-versioning.md`.
2. **Clear Plugin Cache footer (v12+)** — the manual belt-and-suspenders fallback in the release notes. See `cache-clear-footer-convention.md`.

Every cache-affecting release should now do BOTH: bump the manifest AND carry the footer. (Open question: whether a manifest bump alone auto-invalidates the cache, which would make the footer optional — tracked in `framework-improvements-backlog.md`.)

## History

Each entry annotates: kind (migration / release-notes / both), and as of v12, **cache-affecting?** (yes/no). Cache-affecting determines whether the v12 cache-clear footer is mandatory in the release notes.

- v1, v2 — migration-only (both required user-side schema changes). Cache-affecting status pre-dates the convention.
- v3 — release-notes-only (added /lr:recall, subagent-scan, auto boot version check; no user-side file changes needed). Cache-affecting (added skill).
- v4 — release-notes-only (added /lr:attach, /lr:consult; additive). Cache-affecting (added skills).
- v5 — both (migration regenerating legacy sibling-path boot commands, plus release notes). Cache-affecting.
- v6 — both (migration, plus release notes). Cache-affecting.
- v7 — release-notes-only (session summaries feature; `sessions/` dirs created on demand, no schema change). Cache-affecting (touched summarize/finalize docs).
- v8 — release-notes-only (purely behavioral: merge moves to uniform subagents, guest summaries in phase 3, commit+push centralized into phase 4, conflict-resolution subagent procedure). Cache-affecting (touched process-merge.md, finalize.md, summarize.md — all SKILL.md-referenced).
- v9 — release-notes-only (worktree convention, `/lr:init`, fully automated finalization). Cache-affecting (added /lr:init skill, touched finalize.md).
- v10 — release-notes-only (`/lr:spawn-teammate` BETA — Agent Teams integration). Cache-affecting (added skill).
- **v11 — release-notes-only**; added `/lr:workspace-sync` (hard rename of `/lr:pull-domain`), `repos:` field in `lore-repo.md`, full vocabulary sweep `<workspace>` vs domain. **Cache-affecting** — the hard rename triggered the very failure mode that motivated v12 (users still seeing `/lr:pull-domain` from stale cache).
- **v12 — release-notes-only**; added `/lr:doctor` skill with the ailment catalog pattern (see `ailment-catalog-pattern.md`); codified the cache-clear authoring convention in `docs/conventions.md` (see `cache-clear-footer-convention.md`). **Cache-affecting** — adds new skill; the chicken-and-egg case where the skill needed to fix stale-cache *is* the skill being added.
- **v13 — release-notes-only**; added auto-pull at boot/attach/pre-merge plus user-invoked `/lr:pull-lore` skill. New `docs/auto-pull.md` is the shared per-repo procedure (single source of truth across all four sites); new `skills/pull-lore/SKILL.md` + `docs/pull-lore.md` orchestrate it across active agents. `agent-boot.md`, `attach.md`, and `process-merge.md` modified to call into auto-pull. **Cache-affecting** — adds new skill; modifies SKILL.md-referenced docs (boot/attach/merge). Motivated by team-shared agent repos: a teammate pushing lore between sessions could leave the host booting from days-stale state, with finalize-merge re-introducing already-revised decisions. See `auto-pull-mechanism.md`.
- **v14 — release-notes-only** (no migration). **Cache-affecting: yes** (modifies SKILL.md-referenced docs `auto-pull.md` + `check.md`, the `workspace-sync` script, and `conventions.md`). Scope: portable auto-pull timeout fix (the macOS `timeout`-binary bug that had silently disabled v13 auto-pull on macOS — `portable-shell-in-framework-docs.md`) + transport-symmetric hang hardening (auto-pull + workspace-sync) + plugin manifest versioning bump to `1.<VERSION>.0` (`plugin-manifest-versioning.md`) + new `/lr:check` #19 (`consistency-checks.md`) + conventions §§ Portable Shell and Plugin Manifest Versioning + cache-footer placement fix ("near the end" → "near the top"). **First release to bump the plugin manifest** (`1.0.0` → `1.14.0`). See `auto-pull-mechanism.md`, `plugin-manifest-versioning.md`, `portable-shell-in-framework-docs.md`.
- **v15 — release-notes-only** (no migration; existing v14 repos auto-stamp on next boot). **Cache-affecting: yes** (modifies SKILL.md-referenced docs `version-check.md`, `spawn-teammate.md`, `agent-boot.md`, `check.md`, `conventions.md`; adds `teammate-conventions.md`). Shipped 2026-06-02 (commit `3749109`). Scope — four user-surfaced friction sources fixed in one ship: (1) **write-aware boot-time auto-upgrade gate** — narrows from "any uncommitted change defers" to `dirty ∩ write-set` collision check; per-version write-set declared in migration `## Write Paths`; conflict markers remain a separate hard-defer (see `dirty-tree-gates-write-vs-read-distinction.md`); (2) **`/lr:spawn-teammate` Step 7 disambiguated** — the skill's session IS the lead, calls `Agent` directly with `team_name`/`name`/`subagent_type`/`prompt`; plus `TeamCreate` for deterministic naming and stale-dir cleanup; (3) **post-spawn verification (Step 7c)** — reads `~/.claude/teams/<team>/config.json` after `Agent` returns; backend-aware (iterm2 checks `tmuxPaneId`); race-tolerant (5×~50ms retry); surfaces four-state outcome `verified-live` / `verified-inconclusive` / `unverified` / `spawn-errored` (third instance of graduated-verification, see `graduated-verification-confidence.md`); (4) **teammate input-direction rules anchored at boot** — new `docs/teammate-conventions.md` is the single canonical source for the four standing RULES; `agent-boot.md` Step 5 detects spawned-teammate context (`ps -o args= -p $PPID` looking for `--agent-id`) and loads it as standing context. New `conventions.md` sections: § Migration Write Paths (with Glob token grammar + Empty write-set sentinel forms subsections), § Teammate Discipline (pointer index), § Known gap: workspace-root paths. New `/lr:check` #20 (three substeps, all error-severity): 20.1 section presence, 20.2 fenced body presence, 20.3 body content shape. Migrations 2/5/6 backfilled with `## Write Paths` sections (don't-defer-completable-scope discipline). Plugin manifests bumped `1.14.0` → `1.15.0`. Cache-clear footer hoisted near top. **Pattern observation:** seven rounds of multi-lens review converged before ship — operational lessons folded into `parallel-reviewer-fanout-pattern.md`; multi-round-until-convergence is now an architect discipline (`role.md` § Lore-Curation Disciplines bullet 6). New foundational topics: `graduated-verification-confidence.md`, `single-canonical-source-discipline.md`. See `dirty-tree-gates-write-vs-read-distinction.md`, `spawn-teammate-feature.md`, `consistency-checks.md`.
- **v16 — release-notes-only** (no migration; additive). **Cache-affecting: yes** (adds new skills `/lr:df-repo-init` + `/lr:df-ula-file` and their `df/` docs/prompts/schemas). Shipped 2026-06-08 (`lore-framework` commits `005f18a` dev→df rename + ULA verification BETA, then `3ff811f` v16 bump). Scope — ships the first **lr-dev / Dark Factory (DF)** module with a real manifest version (`1.15.0` → `1.16.0`), graduating it from `--plugin-dir`-only to marketplace visibility. Content: the DF module + AIQA/ULA single-file pass (split → A find bugs → B clean-room scenarios → C gap → **D verify → E guardrail**, plus an independent **aggregation-level re-verification**); findings carry `impact-summary` / `nature` / `severity` / `confidence` / `category`; `crossUnit[]` findings; a preserved two-stage `dismissed[]`. Remains **BETA** (schemas may change without migration). Notable: the whole dev→df rename rode in the same ship. See `aiqa-ula-feature.md`, `ula-bug-verification-track.md`, `ula-finding-schema.md`, `df-module-conventions.md`.
- **v17 — release-notes-only** (no migration; the discipline applies incrementally at the next merge). **Cache-affecting: yes** (modifies SKILL.md-referenced docs `process-merge.md` + `conventions.md`). Scope — the **`lore-context.md` shape discipline**: merge Step 4 now shapes `lore-context.md` toward compacted working-knowledge + references to summary topics (not an index of all topics) and strips version-history narrative; shape supersedes the size-only ceiling as the governing constraint. `conventions.md` § Lore Context redefined as entry-point-not-catalog, pointing at `process-merge.md` § Step 4 (single canonical source). New foundational topic: `lore-context-shape-discipline.md`. First applied as a manual groom of the lore-architect's own `lore-context.md` (~6.4K → ~1.4K words). Also captured in the backlog this ship: the **simplification / subtraction** review item (migration-machinery / cross-agent-mechanism-count / no-GC-for-named-principles) and the **lore housekeeping "sleep" pass** (the periodic consolidation sibling of the per-session shape discipline). Manifests bumped `1.16.0` → `1.17.0`. Cache-clear footer hoisted near top. See `lore-context-shape-discipline.md`, `process-merge.md` § Step 4.

## Backfill discipline

Every finalization that lands a `VERSION` bump must check whether `versioning-release-types.md` has an entry for the new version. If not, add it — including kind, scope summary, and cache-affecting annotation. Backfill at the same finalization that ships the version is the principled timing — not "we'll get to it later." Drift in the history list erodes the topic's value as a per-version classification index.

This discipline composes with the deferral-discipline rule (`feedback-don-t-defer-completable-scope.md`): the backfill is a bounded mechanical task that fits in the current ship's scope. It also composes with the cache-clear-footer convention: the same finalization should both (a) ensure the release-notes has the footer if applicable, and (b) record the cache-affecting status in this history list.

The role.md responsibilities call this out explicitly — see `role.md` § Lore-Curation Disciplines.

## In-band BETA refinement (post-v10 observation)

When a BETA feature needs refinement after its initial release, the version-bump ceremony is **not** required. Pattern:

1. **Edit the procedure doc** (`docs/<feature>.md`) — source of truth for current behavior.
2. **Leave the release notes alone** (`release-notes/<N>.md`) — they're a historical record, frozen at the version they describe. A verbatim citation that goes stale post-refinement is acceptable.
3. **No `VERSION` bump** — the BETA caveat ("internal procedure may evolve based on real-world usage") in the release notes is the contract that licenses this.
4. **Update lore at finalization** — design-decisions topics for the feature reflect the *current* state, not the originally-shipped state.

When the feature graduates from BETA, the graduation release notes describe the cumulative final state, not each iteration. Stable (non-BETA) features need a different cadence — refinements there are full release-notes events with version bumps.

**When to break this pattern** (not yet observed; anticipated):

- **Breaking change within BETA** — if existing usage will fail in a non-obvious way, mark explicitly with release notes + bump.
- **New state, file format, or per-agent metadata** — needs migration tracking regardless of stability label.
- **Refinement large enough to be a new feature** — graduate the BETA or treat as v(N+1).

First observed instance: spawn-teammate post-v10 boot-prompt reframe (see `spawn-teammate-feature.md`). If more BETA refinements accumulate and the playbook stays stable, this section should be promoted to a standalone topic (`beta-refinement-workflow.md`).

## See Also

- `cache-clear-footer-convention.md` — the v12 authoring convention this topic's cache-affecting axis tracks; the manual cache-propagation lever.
- `plugin-manifest-versioning.md` — the v14 cache-propagation lever (manifest `1.<VERSION>.0` bump); the primary release-detection mechanism.
- `update-process.md` — how the update flow applies migration + release-notes artifacts.
- `feedback-don-t-defer-completable-scope.md` — discipline that the backfill rule applies to itself.
- `portable-shell-in-framework-docs.md` — the v14 portability rule; the bug that made v13 auto-pull a macOS no-op.
- `dirty-tree-gates-write-vs-read-distinction.md` — v15 extends the write-side with the collision-check refinement.
- `spawn-teammate-feature.md` — v15 Step 7 disambiguation, Step 7c verification, teammate-conventions integration.
- `graduated-verification-confidence.md`, `single-canonical-source-discipline.md` — v15-promoted foundational topics.
