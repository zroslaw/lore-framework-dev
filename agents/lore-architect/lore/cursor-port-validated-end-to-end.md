# Cursor Port Validated End-to-End (local near-landing build)

The Cursor port is now validated end-to-end on the real local engine, not just drafted.

Validated shape (2026-07-05):

- separate local build at `lore-framework-cursor/`
- explicit `docs/engines/cursor.md`
- boot Step 0 detects Cursor from the parent `cursor-agent` process
- `memory-file` = `AGENTS.md`
- Cursor uses a conservative **serial host-side** override for the fan-out paths instead of
  claiming an unverified native subagent mechanism

The important result is that this conservative profile is already enough for the currently
implemented Tier-1 lifecycle surface. The full implemented lifecycle catalog passed on the real
local Cursor installation:

- `cursor-agent 2026.07.01-41b2de7`
- model `composer-2.5-fast`
- `19/19` lifecycle scenarios green through the harness

Operational conclusion: for Cursor v1, prefer a **small, explicit engine-profile diff** over a
"native-feeling" redesign. The verified near-landing framework diff is only:

- `docs/engines/cursor.md` (new)
- `docs/agent-boot.md`
- `docs/attach.md`
- `docs/init.md`
- `docs/resolve-conflicts.md`

Landing state after validation:

- the separate build is suitable as a near-landing artifact
- remaining work is landing discipline: copy validated docs into canonical `lore-framework/`,
  carry the harness updates in `lore-framework-dev/`, add release notes, rerun Cursor against
  canonical
- still deferred on purpose: `lr-wait` / `.mcp.json`, DF / AIQA, migrations, and any stronger
  Cursor-native subagent design

The key framing change is that Cursor is no longer "blocked by quota / unvalidated." It is now
**validated locally with a conservative serial profile**, but not yet landed into the canonical
framework repo.
