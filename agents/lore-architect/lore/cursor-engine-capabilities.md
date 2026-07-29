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
- **Subagent model** — Cursor has native subagents (shipped in **2.4**, 2026-01-22 — editor, CLI and
  Cloud Agents — dispatched via a `Task` tool; async subagents and the nesting rule followed in 2.5).
  **`Task` accepts free-text briefs** (`prompt` + `subagent_type`; validated 2026-07-28 —
  `cursor-task-free-text-brief-validated.md`). **Merge** and **`/lr:trilens-loop`** run through
  parallel `Task` fan-out (one write-capable `Task` per active agent for merge;
  `cursor-merge-via-task.md`). Recall / lore-search, consult, attach version-reconcile, and conflict
  resolution remain **serial host-side** until separately upgraded. If `Task` is missing on an old CLI
  build, stop and report — do not silently host-side merge. See
  `subagent-as-optimization-vs-subagent-as-semantics.md`, `docs-engines-convention.md` § v30 profile
  corrections, `merge-in-booted-subagents.md`.
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
- **Detection blind spot (IDE chat)** — native Cursor IDE agent chat (extension-host) has no
  `cursor-agent` in ancestry and a workspace `<framework-root>` misses `~/.cursor/` containment, so
  `detect_engine` returns `confidence: "assumed"` → Claude profile. Bare `Cursor` / Helper are
  deliberately non-signals (protects Claude-in-Cursor-terminal). Remedy today: `--engine cursor`.
  Open fix options as backlog B8. See `cursor-ide-engine-detection-blind-spot.md`.

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
- `subagent-as-optimization-vs-subagent-as-semantics.md` — optimization vs semantics classification
- `cursor-task-free-text-brief-validated.md` — free-text `Task` brief shape confirmed
- `cursor-merge-via-task.md` — merge upgraded from serial host-side to `Task`
- `merge-in-booted-subagents.md` — engine-neutral merge execution model
- `trilens-loop-feature.md` — semantics-class procedure; also uses `Task` on Cursor
- `feedback-composer-25-subagent-reviews.md` — composer-2.5 as a reviewer tier
- `cursor-boot-context-cost-measurement.md` — ~20K version-match boot on 256K Cursor window
- `cursor-ide-engine-detection-blind-spot.md` — IDE chat assumes Claude; `--engine cursor` remedy
- `engine-profile-must-be-observed-not-believed.md` — why detection is scripted, not believed
