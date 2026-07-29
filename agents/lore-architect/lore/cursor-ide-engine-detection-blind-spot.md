# Cursor IDE Sessions Assume Claude on Engine Detection

Found 2026-07-29 while attaching/diagnosing a `health-advisor` boot in **Cursor IDE
chat** (extension-host), not `cursor-agent` CLI.

`lr-core` `detect_engine` returned `confidence: "assumed"`, `signal: "default"`,
detail `no engine signal in N readable ancestor(s)` → Claude reference profile.
Host correctly re-ran with `--engine cursor`.

## Why every real signal missed

- **Ancestry:** tool shell → `Cursor Helper (Plugin): extension-host …` →
  `Cursor.app/.../MacOS/Cursor`. `ENGINE_PROGRAMS` only matches `claude` /
  `codex` / `cursor-agent`. Bare `Cursor` / Helper are **deliberately excluded**
  so Claude/Codex started from Cursor's integrated terminal are not mislabeled —
  correct for that case, blind for native IDE agent chat.
- **Containment:** boot used workspace checkout `<workspace>/lore-framework` as
  `<framework-root>`, outside `~/.cursor/`. Plugin-cache under
  `~/.cursor/plugins/cache/...` *would* have fired containment → cursor.
- **`CLAUDE_PLUGIN_ROOT`:** unset on Cursor (always).

## Relationship to prior detection work

The 2026-07-25 backlog item (bare `~/.codex` existence before ancestry) was
retired by moving selection into `detect_engine`
(`engine-profile-must-be-observed-not-believed.md`). Deleting that rung also
exposed Codex's correlated-signal blind spot
(`removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`). This is
the **next** Cursor surface gap: scripted detection still cannot observe IDE chat.

Same operational remedy as Codex's documented blind spot: when `confidence` is
`assumed`, say so and name `--engine cursor` as the correction. The user knows
which engine they launched.

## Fix options (open — backlog B8)

Decide deliberately; do not stack all:

1. Trusted IDE-only argv signal with a negative test that Claude-from-Cursor-terminal
   still resolves to claude.
2. Cursor registered shortcuts / boot wrappers always pass `--engine cursor`.
3. Document assumed-Claude + `--engine cursor` path in `docs/engines/cursor.md`.
4. Prefer self-located plugin-cache `<framework-root>` on Cursor so containment helps.

Filed in `framework-improvements-backlog.md` § Boot Step-0 (2026-07-29 bullet) and
`workdir/what-to-improve.md` **B8**. Lifecycle-testable once an IDE-shaped argv
fixture exists; today the harness mostly exercises CLI.

## See Also

- `engine-profile-must-be-observed-not-believed.md` — why selection is scripted.
- `removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md` — Codex
  sibling blind spot from the same detection redesign.
- `cursor-engine-capabilities.md` — Cursor hub.
- `docs/engines/cursor.md` — point-of-use profile (document option 3 there when shipping).
- `graduated-verification-confidence.md` — why `assumed` is reported, not silent.
