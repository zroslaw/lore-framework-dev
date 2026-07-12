`/lr:check` runs 21 consistency checks. Defined in `<framework-root>/docs/check.md`.

> **Naming note (a v14 near-miss — see `verify-before-acting-on-suspected-bugs.md`):** the plugin catalog doc is **`docs/check.md`**, NOT `consistency-checks.md`. `consistency-checks.md` is *this lore topic's* name only. `skills/check/SKILL.md` correctly points at `docs/check.md`. Don't "fix" the skill to repoint it — verify on disk first.

**Descriptor validation (1–5):**
1. Agent repo discovery — scan for `lore-repo.md` at root; flag if no lore agent repos found
2. lore-repo.md validation — verify YAML frontmatter has non-empty `description` and `version`
3. Framework version consistency (repo) — compare `lore-repo.md` version against `VERSION`; warn on mismatch (triggers `/lr:update`)
4. Agent discovery — scan `agents/` within discovered repos; flag repos with no agents (informational)
5. role.md frontmatter validation — verify YAML frontmatter has non-empty `description`. Legacy `version` field (if present) is flagged as informational — the repo predates migration 2.

**Structural (6–8):**
6. Agent discovery vs registration — bidirectional: every agent dir has a boot command (informational, not error — registration optional); every boot command points to a real agent dir (error if broken)
7. Boot command link validity — all file paths in `lr-*-agent.md` resolve on disk
8. Agent directory structure — each agent has `role.md`, `lore-context.md`, `lore/`, `workdir/`

**Reference integrity (9–10):**
9. lore-context.md topic references — filenames linked in lore-context exist in `lore/`
10. Lore topic cross-references — filenames referenced inside topics exist in the same `lore/`

**Size and state (11–13):**
11. lore-context.md size — warn at 40K tokens, flag at 50K
12. Pending reflections — non-empty `reflections/` dir means merge not yet run
13. Uncommitted lore changes — git status detects modified lore files not yet committed

**Temporal/semantic (14–16):**
14. lore-context.md staleness — topics committed more recently than lore-context may not be reflected in summary
15. lore-context.md semantic consistency — topic headings/opening sentences compared against lore-context summaries
16. Boot command vs role.md — timestamps + agent name match between boot command and role.md heading

**Drift / orphans (17–18, added v5):**
17. Orphaned pre-plugin skill commands — flags `.claude/commands/lr-<name>.md` files where `<name>` collides with a current framework skill (e.g., `lr-boot.md`, `lr-reflect.md`). These are pre-plugin local duplicates that shadow or duplicate the installed plugin skill; framework no longer emits them. Informational — user decides to keep or delete. See `migration-ownership.md`.
18. Legacy sibling-path per-agent boot commands — scans `lr-*-agent.md` for `lore-framework/docs/agent-boot.md` pattern (pre-v5 emission form). These break on plugin installs. Triggers `/lr:update` (migration 5 regenerates them). See `plugin-compat-template-audit.md`.

**Plugin manifest (19, added v14):**
19. Plugin manifest version — reads framework `VERSION` (N) and the `version` of all three plugin manifests: `.claude-plugin/plugin.json`, the `lr` entry in `.claude-plugin/marketplace.json` (skip gracefully if missing — see backlog), and `.cursor-plugin/plugin.json` (v25+). Asserts every read manifest `== 1.<N>.0`. Errors on mismatch or pairwise disagreement. Claude manifests are the cache-detection lever; `.cursor-plugin/plugin.json` is mechanical parity only. Enforces `plugin-manifest-versioning.md`. Complementary to check #3 (repo-level stamp vs `VERSION`).

**Migration write paths (20, added v15):**
20. Migration write-paths declaration — three substeps, all error-severity, applied to every `migrations/<N>.md`:
    - **20.1 — section presence:** the `## Write Paths` section exists. Without it, the boot-time auto-upgrade gate falls back to conservative blanket-dirty (everything looks dirty), reintroducing the friction the v15 write-aware gate was designed to remove.
    - **20.2 — fenced body presence:** the section contains a fenced code block (the parser reads only the fenced body to avoid prose contaminating the write-set).
    - **20.3 — body content shape:** the fenced body is either an accepted empty-write-set sentinel (`(none)`, optionally followed by space/hyphen/em-dash + prose; or an empty fenced block) or one or more glob tokens drawn from the canonical character class declared in `conventions.md` § Migration Write Paths § Glob token grammar. A malformed body silently produces an empty write-set, which the gate treats as "no collisions possible" — the worst-case false-positive (proceeds when it shouldn't).
    All three substeps land at error because each failure mode degrades the gate the same way (blanket-dirty fallback or silently-empty write-set); severity is graduated by blast radius and they all sit at the high end. Enforces the v15 `dirty-tree-gates-write-vs-read-distinction.md` write-set declaration discipline. See `conventions.md` § Migration Write Paths.

**Cursor dual skill tree (21, added v21):**
21. Cursor-tree parity — verifies the `.cursor-skills/lr-<skill>/` wrapper tree stays 1:1 with the canonical `skills/<skill>/` tree (the dual-skill-tree pattern in `cursor-dual-skill-tree-one-repo.md`). Checks: a wrapper exists for every canonical skill and vice versa (orphan detection), each wrapper's frontmatter `name` is `lr-<skill>`, self-location references `.cursor-skills/lr-<skill>/SKILL.md`, invocation-syntax matches, and no content drift between wrapper and canonical intent. Enforces that `scripts/sync-cursor-skills` was re-run after any skill add/rename. Added in v21, path root moved in v23 to keep wrappers out of Codex's plugin crawl. See `cursor-dual-skill-tree-one-repo.md`.

**History:** originally 17 checks. Migration 2 dropped the agent-level version check (old check 6) because `role.md` no longer carries a `version` field — subsequent checks renumbered down by one, leaving 16. Migration 5 added checks 17 and 18 for drift detection. v14 added check 19 (plugin manifest version) — the first non-migration check addition (release-notes-only ship). v15 added check 20 (migration write-paths declaration) — also release-notes-only. v21 added check 21 (cursor-tree parity) — release-notes-only.

**Candidate check (not yet implemented):** a version-history-completeness check — assert `versioning-release-types.md` has a history entry for every `release-notes/<N>.md` / `migrations/<N>.md` on disk. Surfaced by the v21 gap (both v20 and v21 entries were missing, the backfill discipline having silently slipped at v20). Would make the version-history-backfill discipline self-healing instead of relying on per-ship diligence. See `versioning-release-types.md` § Backfill discipline.

Key principle: git history is the metadata layer for temporal checks — no embedded timestamps in files.

## See Also

- `plugin-manifest-versioning.md` — check #19 enforces the `1.<VERSION>.0` manifest rule
- `verify-before-acting-on-suspected-bugs.md` — the `check.md` vs `consistency-checks.md` near-miss that the naming note above guards against
- `migration-ownership.md` — checks 17/18 drift-detection rationale
- `plugin-compat-template-audit.md` — check 18 (legacy sibling-path boot commands)
- `framework-improvements-backlog.md` — check #19 graceful-skip-on-missing-`marketplace.json` follow-up
- `dirty-tree-gates-write-vs-read-distinction.md` — the v15 write-set discipline check #20 enforces
