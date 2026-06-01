The recurring "stale skill catalog after an upgrade" pain — the failure mode that motivated `/lr:doctor` and the cache-clear footer (`cache-clear-footer-convention.md`, `ailment-catalog-pattern.md` → `doctor-stale-plugin-cache.md`) — has a **root cause** we only named in v14.

## The root cause

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` sat frozen at `1.0.0` from v1 through v13. Claude Code identifies a plugin release by the **manifest version**. Frozen manifest → the plugin layer never sees a new release → it never refreshes its cache on its own. The manual Clear Plugin Cache ritual existed entirely to work around this self-inflicted gap. Years of cache pain traced to one decoupled-version-field oversight.

## Discipline (codified in `conventions.md` § Plugin Manifest Versioning)

Applied at **every `VERSION` bump**:

- Set `version` in BOTH `plugin.json` and `marketplace.json` (the `lr` entry) to **`1.<VERSION>.0`** — framework `VERSION` 14 → manifest `1.14.0`.
- The mapping is **mechanical**, derived from `VERSION`: can't be forgotten, strictly increasing from the old `1.0.0`, valid semver.
- **Enforced by `/lr:check` #19** (`consistency-checks.md`) — flags any manifest whose version ≠ `1.<VERSION>.0`, and flags the two manifests disagreeing with each other.

Three layers of defense: documented (conventions) + mechanical (derived from VERSION) + checked (check #19).

## Relationship to the cache-clear footer

**Complementary, not redundant.** Bumping the manifest is what lets the platform *detect* a release at all. The cache-clear footer (`cache-clear-footer-convention.md`) is the manual belt-and-suspenders fallback. Keep both.

This is a new cache-propagation lever, **orthogonal** to both the migration-vs-release-notes axis and the cache-affecting axis tracked in `versioning-release-types.md`. Every cache-affecting release should now also bump the manifest.

## OPEN — verify next session

Does a manifest-version bump *alone* trigger Claude Code cache auto-invalidation (removing the need for a manual clear), or does it only *enable detection*? Test with a real marketplace install + restart. If it auto-invalidates, the cache-clear footer could become optional. Tracked in `framework-improvements-backlog.md`. This is exactly the kind of suspected behavior to verify empirically before acting on — see `verify-before-acting-on-suspected-bugs.md`.

## Where it sits

Plugin-layer concern (the three-layer model — `architecture-overview.md`). The manifest is part of what's distributed via the marketplace; it had simply never been kept in sync with `VERSION`.

## See Also

- `cache-clear-footer-convention.md` — the manual fallback; complementary to the manifest bump
- `consistency-checks.md` — check #19 enforces the `1.<VERSION>.0` rule; sits alongside check #3 (repo-level version) — same idea at the plugin layer vs the domain layer
- `versioning-release-types.md` — the manifest bump is a new lever recorded there; v14 history entry
- `ailment-catalog-pattern.md` — `doctor-stale-plugin-cache.md` was the symptom; this topic is its root cause
- `naming-foundational-principles.md` — naming the root cause (not just patching the symptom) is the meta-rule applied here
- `framework-improvements-backlog.md` — open question (auto-invalidation?) + check #19 graceful-skip follow-up
