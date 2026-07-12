# Cursor marketplace / D2 probe notes (v25)

Date: 2026-07-10  
Machine: Yaroslav's MacBook Pro  
CLI: `cursor-agent` (build 2026.07.09-a3815c0 observed in worker parent args)

## Step 0 — CLI plugin surface

```bash
cursor-agent --help | grep -i plugin
```

Result:

```
  --plugin-dir <path>          Load a local plugin directory (can be specified
```

**Pass criterion:** document available commands or "none".  
**Outcome:** `--plugin-dir` exists. No separate `plugin add` / marketplace subcommands in `--help`.

**Tier B (marketplace install): CLOSED for this CLI build** — no marketplace commands to probe.

## D2 — Local plugins dir symlink

**Setup on this machine (pre-existing):**

```
~/.cursor/plugins/local/lore-framework → /Users/yaroslav/Documents/git-repos/lore-framework
```

**Step 0 finding:** only `--plugin-dir` is documented for plugin loading.

**IDE chat without `--plugin-dir`:** **NOT VERIFIED in this probe session.** Opening a fresh IDE
chat and confirming `/lr-boot` appears without `--plugin-dir` was not executed headlessly. Treat D2
as **unverified** for install-script defaults.

**Install-script decision (v25):** `install-cursor-plugin` defaults to **no symlink**; `--symlink`
is opt-in after team confirms D2 on their Cursor build.

## Deterministic path (verified)

`cursor-agent --plugin-dir <checkout>` — verified in v20+ lifecycle harness and prior sessions
(including 2026-07-10 lore-architect design session via file-driven fallback).

## Mid-session fallback (verified 2026-07-10)

This Cursor worker session runs **without** native `/lr-*` plugin skills loaded. Lore architect
was booted file-driven via `.cursor-skills/lr-boot/SKILL.md` → `agent-boot.md` — the v25
implementation session itself.

## Recommendations for INSTALL-CURSOR.md

- Document two-step clone + helper + `--plugin-dir` as the verified path.
- Do not claim IDE loads from `~/.cursor/plugins/local/` until D2 passes on the reader's build.
- Defer Tier B marketplace docs until a future CLI exposes install commands.
