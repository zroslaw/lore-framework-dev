---
lore: 1
type: topic
summary: "Validated 2026-07-10 in a real Cursor chat without plugin load: given a framework checkout path, procedures run from disk via the .cursor-skills wrappers; detect by missing skills, never by CLAUDE_PLUGIN_ROOT."
parent: lore/cursor-engine-capabilities.md
---

# Cursor Mid-Session Fallback — Empirically Validated (2026-07-10)

Validated in a real Cursor IDE chat **without** native plugin load: Lore procedures execute when
the host is given a local `lore-framework` checkout path and reads docs from disk.

## Detection (Cursor)

- **Do not** use `${CLAUDE_PLUGIN_ROOT}` — always empty on Cursor, even when plugin loaded.
- **Do** check whether expected plugin skills (e.g. `/lr-boot`) are unavailable.

## Execution path

1. User provides absolute checkout path (chat, `AGENTS.md`, workspace layout).
2. Host treats path as `<framework-root>` (must contain `VERSION`).
3. For `/lr-<skill>`: read `.cursor-skills/lr-<skill>/SKILL.md` and follow (delegates to
   `docs/<procedure>.md`).

Name mapping is **not** mechanical — always use the wrapper SKILL, not guessed doc names.

## v25 formalization

Canonical wording ships in `docs/engines/cursor.md` § Mid-session fallback (v25, commit `4f3bfcf`
local). Framework semantic commitment: procedure docs remain self-contained for file-driven execution.

## See Also

- `v25-cursor-ops-parity-design.md`
- `cursor-engine-capabilities.md`
- `docs/engines/cursor.md`
