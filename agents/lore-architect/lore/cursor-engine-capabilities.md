# Cursor Engine Capabilities

Cursor is a shipped Tier-1 engine path for Lore Framework with a deliberately conservative profile.
This topic is the durable entry point for Cursor-specific operational assumptions; keep the detailed
validation and probe notes in the linked topics below.

## Operational shape

- **Plugin loading** — verified path: local checkout via `cursor-agent --plugin-dir
  /absolute/path/to/lore-framework`. Post-clone helper: `scripts/install-cursor-plugin` (v25).
  Symlink under `~/.cursor/plugins/local/` is **opt-in** (`--symlink`) until D2 confirms IDE
  loads without `--plugin-dir`; see `workdir/cursor-marketplace-probe-notes.md`.
- **Plugin refresh** — `scripts/cursor-refresh-plugin` (git pull + VERSION diff + fresh-session
  reminder), then new `cursor-agent --plugin-dir` session; no hot-reload.
- **Mid-session fallback** — when plugin skills are unavailable, file-driven execution via
  `.cursor-skills/lr-*/SKILL.md`; canonical contract in `docs/engines/cursor.md`. Empirically
  validated 2026-07-10 (`cursor-mid-session-fallback-validated.md`).
- **Invocation surface** — skill wrappers under `.cursor-skills/lr-<skill>/` → `/lr-<skill>`;
  per-agent shortcuts `/lr-<agent>-agent` under `.cursor/skills/` after registration.
- **Subagent model** — serial host-side execution is the **validated default**, with one carve-out
  since v30. Cursor does have native subagents (shipped in **2.4**, 2026-01-22 — editor, CLI and Cloud
  Agents — dispatched via a `Task` tool; async subagents and the nesting rule followed in 2.5), so the
  v20 profile's blanket "no native mechanism relied on" was epistemic caution that had gone stale. The
  corrected binding keeps serial execution for recall / consult / attach / merge / conflict resolution
  (all validated that way, all lossless under serialization) and uses `Task` only for procedures where
  **subagent independence is the semantics, not an optimization** — `trilens-loop.md` is the sole
  current exception, and extension to the serial-default procedures needs its own validation run. See
  `subagent-as-optimization-vs-subagent-as-semantics.md`, `docs-engines-convention.md` § v30 profile
  corrections. **Load-bearing unknown:** whether `Task` accepts a free-text brief or only dispatches
  pre-defined agent files by name — the profile's § Native subagents section separates what Cursor
  documents from what we have validated, and procedures using `Task` handle the name-only case by
  writing throwaway `readonly` definitions under `.cursor/agents/` and deleting them afterwards.
- **Memory file** — `AGENTS.md`.
- **Doctor** — `doctor-cursor-session-without-plugin` for missing skills entirely (v25).
- **Three-manifest discipline** — `.cursor-plugin/plugin.json` bumped with Claude manifests;
  check #19 enforces; hygiene only — not a verified Cursor cache lever.
- **Usage auto-retrieval** — plan quota scriptable via undocumented `usage-summary` API
  (`sub::jwt` cookie); session context % via CLI statusline only (interactive, not headless `-p`);
  IDE context ring is manual. See `cursor-usage-auto-retrieval.md`; draft probe in
  `workdir/cursor-cli-usage/`.
- **Boot context cost** — version-match boot ≈ **~20K tokens** (~8–9% of 256K); measure with
  `scripts/token-count` (`o200k_base`). See `cursor-boot-context-cost-measurement.md`.

## Why this hub exists

Cursor-specific facts were previously split across probe notes, port validation, and dual-tree docs.
This hub is the starting map for install, refresh, fallback, invocation, and constraints.

## See Also

- `v25-cursor-ops-parity-design.md`
- `cursor-mid-session-fallback-validated.md`
- `cursor-port-validated-end-to-end.md`
- `cursor-cli-and-harness-operational-notes.md`
- `cursor-dual-skill-tree-one-repo.md`
- `cursor-plugin-distribution-update-model.md` — install/update/auto-refresh model
- `engine-marketplace-readiness.md` — marketplace submission + manifest visibility
- `docs-engines-convention.md`
- `multi-engine-portability-direction.md`
- `engine-session-log-formats.md`
- `subagent-as-optimization-vs-subagent-as-semantics.md` — the principle behind the v30 `Task` carve-out
- `trilens-loop-feature.md` — the only semantics-class procedure today, and why the carve-out exists
- `feedback-composer-25-subagent-reviews.md` — composer-2.5 as a reviewer tier
- `cursor-boot-context-cost-measurement.md` — ~20K version-match boot on 256K Cursor window
