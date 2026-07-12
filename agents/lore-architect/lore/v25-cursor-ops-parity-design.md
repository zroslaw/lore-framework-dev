# v25 Cursor Ops Parity — Shipped (local, push deferred)

v25 closes the **operator ergonomics gap** between Cursor and Codex while leaving Tier-1 lifecycle
semantics unchanged. Design approved 2026-07-10 (four review rounds); **implemented same day** on
`lore-framework` branch `v25-cursor-ops-parity` (commit `4f3bfcf`). **Push deferred** by user at
finalize — framework tree is committed locally only.

## What shipped (Tier A)

- `scripts/install-cursor-plugin` — post-clone helper; `--symlink` opt-in (D2-gated); default no symlink
- `scripts/cursor-refresh-plugin` — `git pull --ff-only` + VERSION diff + fresh-session reminder
- `INSTALL-CURSOR.md` — depth parity with `INSTALL-CODEX.md`
- README — engine-neutral sweep + Cursor self-install block
- `docs/engines/cursor.md` — canonical mid-session fallback, load surfaces, refresh contract
- `docs/doctor-cursor-session-without-plugin.md` — atomic ailment, catalog-registered
- `/lr:check` #19 + `conventions.md` — **three** manifests (`.cursor-plugin/plugin.json` included)
- `release-notes/25.md`; `VERSION` 25; all manifests `1.25.0`

## Verification at implement

- D2/Tier B probe notes: `workdir/cursor-marketplace-probe-notes.md` (Tier B closed — only
  `--plugin-dir` in CLI help; IDE symlink load unverified headlessly)
- Script smoke + executable bit OK
- Cursor fallback smoke: implementation session booted lore-architect file-driven (no native plugin)
- Three in-session implementation review rounds → convergence (doc routing, canonical-copy
  discipline, release-notes section order)
- **`LR_LIFECYCLE=1` skipped** at user request before push

## Explicitly out of v25 (unchanged)

Tier B marketplace, `workspaceOpen` hooks, `agent-boot.md` Cursor note, Cursor takeover, new skills.

## Canonical spec

`workdir/draft-v25-cursor-ops-parity.md` — design archive + handoff checklist.

## See Also

- `v25-implementation-review-lessons.md`
- `cursor-engine-capabilities.md`
- `cursor-mid-session-fallback-validated.md`
- `plugin-manifest-versioning.md` — three-manifest discipline (v25)
- `framework-improvements-backlog.md`
