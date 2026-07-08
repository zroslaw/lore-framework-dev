# v24 Ship Status (as of 2026-07-08 — NOT shipped, all local)

v24 is complete in the `lore-framework` working tree but **uncommitted and unpushed** — the user explicitly deferred the ship ("keep it local, will ship later"). This topic rescues state from an unfinalized Codex lore-architect session (rollout `019f3ed9`, 2026-07-08) plus the 2026-07-08 Claude session's additions. **Delete or fold this topic into `versioning-release-types.md` when v24 actually ships.**

## Scope

As per `release-notes/24.md`: registration skills (`/lr:register-agent`, `/lr:unregister-agent`), Cursor native per-agent shortcuts, richer routing metadata, boot teammate-probe capability gating — **plus `/lr:takeover` (BETA)**, folded in by the 2026-07-08 session (skill, doc, `scripts/session-takeover`, cursor wrapper, README row, release-notes section). `VERSION`=24 and both plugin manifests at `1.24.0` are already in the tree. Release-notes-only (no `migrations/24.md`); cache-affecting (adds skill + script), footer already in the release notes.

This scope closes the three "Next-Session Active Threads" that were in `framework-improvements-backlog.md`: teammate-probe cleanup, routing metadata, agent-registration redesign.

## Validation state (from the Codex session, engine-by-engine)

- **Claude lifecycle suite: green**, including the new register/unregister scenarios.
- **Cursor lifecycle: green after a real fix** — `test_18_init` caught Cursor writing `CLAUDE.md` instead of `AGENTS.md`; root causes were weak phrasing in the shared `init` doc *and* the Cursor `lr-init` wrapper description itself saying `CLAUDE.md`. Both fixed; isolated repro then full repo/workspace file green.
- **Codex lifecycle: green on retry** (first run died uniformly mid-suite — rate-limit window, not a framework bug).
- **Quality benchmark:** Claude clean (full treatment success), Cursor positive-but-weaker uplift, **Codex run interrupted** when the session died — still to be run before ship.

## Remaining before ship

1. Run the Codex quality benchmark (the only unfinished validation leg).
2. Review + commit the `lore-framework` working tree (large diff: docs, skills, `.cursor-skills/`, manifests, release notes, README, `scripts/session-takeover`) and the dirty `tests/*` in `lore-framework-dev` (separate manual commit — outside finalize's `agents/` scope).
3. Push; then the usual cache-clear guidance applies (v24 is cache-affecting; footer already in release notes).
4. Ship-disciplines checklist at that moment: finalize the `versioning-release-types.md` v24 entry (a provisional one exists, marked unshipped), manifests already bumped, cache footer present.

Note: `lore-framework-dev/lore-repo.md` was stamped 23→24 by boot-time auto-upgrade on 2026-07-08 (uncommitted). Takeover feature validation (haiku, 2/2 pass) is recorded in `takeover-feature.md`.

## See Also

- `takeover-feature.md` — the feature folded into this release.
- `versioning-release-types.md` — carries the provisional v24 history entry; finalize at ship.
- `framework-improvements-backlog.md` — § Takeover follow-ups; the closed next-session threads.
