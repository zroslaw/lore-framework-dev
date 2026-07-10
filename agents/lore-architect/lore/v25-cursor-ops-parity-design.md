# v25 Cursor Ops Parity — Design (approved, not yet implemented)

v25 closes the **operator ergonomics gap** between Cursor and Codex while leaving Tier-1 lifecycle
semantics unchanged. Four design-review rounds converged on **approve (ready to implement)** on
2026-07-10.

## Problem

Cursor has shipped lifecycle parity (v20–v24) but lacks Codex-level install/refresh scripting,
README self-install guidance, documented mid-session fallback, doctor coverage for missing plugin,
and three-manifest version discipline (`.cursor-plugin/plugin.json` lagged unchecked).

## Ship unit (Tier A)

- `scripts/install-cursor-plugin` — post-clone helper; two-step install (clone → script →
  `cursor-agent --plugin-dir`); symlink gated on D2 probe
- `scripts/cursor-refresh-plugin` — `git pull` + VERSION diff + fresh-session reminder
- `INSTALL-CURSOR.md` — depth parity with `INSTALL-CODEX.md`
- README — bounded engine-neutral sweep + Cursor self-install block
- `docs/engines/cursor.md` — canonical mid-session fallback (via `.cursor-skills/lr-*/SKILL.md`),
  load surfaces table, refresh contract
- `docs/doctor-cursor-session-without-plugin.md` — atomic ailment, catalog-registered
- Extend `/lr:check` #19 + `conventions.md` for **three** manifests
- `release-notes/25.md` with near-top cache-clear section; VERSION 25 / manifests `1.25.0`

## Explicitly out of v25

Tier B marketplace (unless probe passes before final gate), `workspaceOpen` hook templates,
`agent-boot.md` Cursor note, Cursor takeover, new `/lr:*` skills.

## Pre-ship gates

Script temp-HOME smoke → Cursor fallback smoke (file-driven boot) → full `LR_LIFECYCLE=1` on `claude`
(last, on final tree) → commit + push framework → lore-architect finalize same session.

## Canonical spec

`workdir/draft-v25-cursor-ops-parity.md` — implementation handoff checklist at end.

## See Also

- `cursor-engine-capabilities.md`
- `cursor-mid-session-fallback-validated.md` (reflection merged)
- `framework-improvements-backlog.md` § v25
- `plugin-manifest-versioning.md`
- `INSTALL-CURSOR.md` (current thin guide; v25 expands)
