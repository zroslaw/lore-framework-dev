# Cursor Port Validated End-to-End and Landed in Canonical v20

The Cursor port is no longer just a validated sibling build. The conservative Cursor profile was
validated locally first, then landed in canonical `lore-framework` as **v20** on 2026-07-05
(commit `5cbb967`, manifests `1.20.0`).

Validated shape before landing:

- separate local build at `lore-framework-cursor/`
- explicit `docs/engines/cursor.md`
- boot Step 0 detects Cursor from the parent `cursor-agent` process
- `memory-file` = `AGENTS.md`
- Cursor uses a conservative **serial host-side** override for the fan-out paths instead of
  claiming an unverified native subagent mechanism

The important result is that this conservative profile was already enough for the currently
implemented Tier-1 lifecycle surface. The full implemented lifecycle catalog passed on the real
local Cursor installation:

- `cursor-agent 2026.07.01-41b2de7`
- model `composer-2.5-fast`
- `19/19` lifecycle scenarios green through the harness

Operational conclusion: for Cursor v1, prefer a **small, explicit engine-profile diff** over a
"native-feeling" redesign. The shipped framework diff is still only:

- `docs/engines/cursor.md` (new)
- `docs/agent-boot.md`
- `docs/attach.md`
- `docs/init.md`
- `docs/resolve-conflicts.md`

What landed in canonical v20:

- added `docs/engines/cursor.md`
- updated `docs/agent-boot.md` Step 0 to detect `cursor-agent` / `~/.cursor`
- added Cursor engine notes to `docs/attach.md`, `docs/init.md`, and `docs/resolve-conflicts.md`
- added `release-notes/20.md`
- bumped `VERSION` to `20` and plugin manifests to `1.20.0`

Shipped-state implications:

- the separate `lore-framework-cursor/` build is now **superseded and deletable**
- **v21 (local, not pushed to framework remote, 2026-07-05)** adds the dual skill tree:
  initially `skills/cursor/lr-*/`, `.cursor-plugin/plugin.json`, `scripts/sync-cursor-skills`,
  check #21. **v23** later relocates the wrapper side to `.cursor-skills/lr-*/` to keep the Cursor
  wrappers out of Codex's plugin skill crawl without changing Cursor's `/lr-<skill>` surface.
  See `cursor-dual-skill-tree-one-repo.md`.
- the matching lifecycle-harness support in `lore-framework-dev/tests/` remains a **separate
  dev-repo change** outside finalize's `agents/` commit scope
- still deferred on purpose: `lr-wait` / `.mcp.json`, DF / AIQA, migrations, and any stronger
  Cursor-native subagent design

The key framing change is that Cursor is no longer "blocked by quota / unvalidated" or
"validated locally but not yet landed." It is now **shipped in canonical `lore-framework` with the
same conservative serial profile that passed local validation**.
