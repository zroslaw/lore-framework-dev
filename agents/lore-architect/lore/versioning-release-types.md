---
lore: 1
type: area
summary: "Hub for per-version release history (children by version range) and the authoring rules behind it: migration vs release-notes, the orthogonal cache-affecting axis, the two cache-propagation levers, and the backfill discipline."
parent: lore-context.md
---

Starting with v3, framework version bumps can carry two kinds of artifacts:

**Migration** (`migrations/<N>.md`) — physical instructions to modify user-side repo files (frontmatter updates, file regenerations, directory restructures). Executed by `/lr:update` and the auto-upgrade-at-boot. Must be idempotent.

**Release notes** (`release-notes/<N>.md`) — informational only; describes what's new in version N. Displayed to the user, not executed. No user-side file edits required.

## Rules for authoring a new version bump

- User-side file changes required → create `migrations/<N>.md`
- Feature/doc additions only → create only `release-notes/<N>.md`
- Large release with both → create both
- **At least one must exist** — the update process treats a gap as a framework packaging bug
- **If the version is cache-affecting** (touches `skills/`, `scripts/`, a **bundled MCP server** — a root `.mcp.json` or an inline `mcpServers` block in `plugin.json` — or any `docs/<name>.md` referenced by a SKILL.md whose runtime behavior changes), include the **Clear Plugin Cache** footer per `cache-clear-footer-convention.md`. The cache-affecting axis is **orthogonal** to the migration-vs-release-notes axis. (The `.mcp.json` / bundled-MCP-server trigger was added in v18 alongside `lr-wait`, mirroring `conventions.md` § Migration/Release-Note Authoring — see `plugin-mcp-server-convention.md`.)

## Cache-propagation levers (two, as of v14)

Two distinct, complementary mechanisms make the platform pick up a cache-affecting release — orthogonal to both the migration-vs-release-notes axis and the cache-affecting flag:

1. **Plugin manifest version bump (v14+; four version-bearing manifests since v25)** — set `version` to `1.<VERSION>.0` in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (lr entry), `.cursor-plugin/plugin.json`, and `.codex-plugin/plugin.json`. Claude manifests are the original cache-detection lever; Cursor is consistency/visibility hygiene; Codex is the version read by native installs. `.agents/plugins/marketplace.json` has no per-plugin version and is not part of the check. See `plugin-manifest-versioning.md`.
2. **Clear Plugin Cache footer (v12+)** — the manual belt-and-suspenders fallback in the release notes. See `cache-clear-footer-convention.md`.

Every cache-affecting release should now do BOTH: bump the manifest AND carry the footer. (Open question: whether a manifest bump alone auto-invalidates the cache, which would make the footer optional — tracked in `framework-improvements-backlog.md`.)

## History

Each entry annotates: kind (migration / release-notes / both), and as of v12, **cache-affecting?** (yes/no). Cache-affecting determines whether the v12 cache-clear footer is mandatory in the release notes.

Entries live in three child topics, oldest to newest — append every new version to the newest one:

- [versioning-history-v01-v20.md](versioning-history-v01-v20.md) — v1–v20.
- [versioning-history-v21-v36.md](versioning-history-v21-v36.md) — v21–v36.
- [versioning-history-v37-v47.md](versioning-history-v37-v47.md) — v37–v47; **v47 is the latest recorded**.

## Backfill discipline

Every finalization that lands a `VERSION` bump must add the new version's entry to the newest history child (`versioning-history-v37-v47.md`) — including kind, scope summary, and cache-affecting annotation. Backfill at the same finalization that ships the version is the principled timing — not "we'll get to it later." Drift in the history list erodes the topic's value as a per-version classification index.

**Scan the whole tail for gaps, not just the current version — the discipline is not self-healing (v21 lesson).** Appending only the current version's entry each ship silently carries forward any gap a prior slipped ship left. Landing v21 (2026-07-06), I found the history was missing **both** v20 and v21 — the v20 ship had slipped the backfill entirely, and appending only v21 would have left the v20 gap permanent. So at every ship, before adding the new entry, scan the tail between the last recorded version and the one shipping and backfill **all** missing entries in the same ship. Cheap check: `for v in <last+1>..<current>; do grep -c "v$v " versioning-release-types.md; done` — any `0` is a gap. This is a bounded mechanical sweep, so it belongs in the current ship (`feedback-don-t-defer-completable-scope.md`). `/lr:check` has no check for this yet — a candidate: assert a history entry exists for every `release-notes/<N>.md` / `migrations/<N>.md` (see `consistency-checks.md`).

**The release notes decay once per review round, so re-audit them last.** This entry records gates
whose results exist by the time it is written; `release-notes/<N>.md` does not — it is drafted while
the gates are still running, and every fix round changes the thing it describes. Re-audit every
self-referential claim (gate dispositions, round and finding counts, test counts, what was waived)
against the tree being pushed, as the last step before tag and push. See
[a-release-record-goes-stale-while-you-fix-it.md](a-release-record-goes-stale-while-you-fix-it.md).

This discipline composes with the deferral-discipline rule (`feedback-don-t-defer-completable-scope.md`): the backfill is a bounded mechanical task that fits in the current ship's scope. It also composes with the cache-clear-footer convention: the same finalization should both (a) ensure the release-notes has the footer if applicable, and (b) record the cache-affecting status in this history list.

The role.md responsibilities call this out explicitly — see `role.md` § Lore-Curation Disciplines.

**"Commit pending" can accumulate across versions — verify `git HEAD` at session start.** When lore
says a version is "built, commit pending," don't assume the last-described version is the committed
one. At the start of the v18/v19 ship, the public repo `HEAD` was still at v17 — *both* v18 (lr-wait,
recorded as "commit pending") and the whole port were uncommitted in one working tree, so shipping
required untangling and committing in order (v18 first, then v19), not a single push. Ground the
current state in `git log`/`git HEAD`, not in the most recent lore entry (a `verify-before-acting`
instance — `verify-before-acting-on-suspected-bugs.md`).

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
- `trilens-loop-feature.md` — the v30 feature; `subagent-as-optimization-vs-subagent-as-semantics.md` — the v30-promoted foundational topic.
- `post-convergence-edits-need-their-own-gate.md` — the artifact-state discipline that keeps a ship's recorded validation honest.
- `fix-the-pointer-not-the-shipped-migration.md` — the v32-ship operational rule: when a shipped
  migration's output becomes wrong for a new case, fix what points at it (check remedies, doctor
  ailments), never the migration file itself.
- `cross-engine-team-substrate-validated.md` — the shared-folder cross-engine review process behind
  the v32 design; `independent-engine-review-catches-structural-blind-spots.md` for what it caught.
