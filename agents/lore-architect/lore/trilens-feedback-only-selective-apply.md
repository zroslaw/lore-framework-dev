# Trilens: feedback-only then selective apply

For a small doc/script change, one trilens round with **feedback only** (no auto-apply) worked well: gather independent findings, triage with the user in short turns, then apply a short fix-now list.

Worth fixing in-session for the workspace-ignore work:

- Memory-file Conventions block must mention `.tmp/` scratch (not only worktrees)
- Check #22 fix text must not claim `--refresh` repairs `.gitignore`
- Lifecycle `create-repo` must pass `.tmp/…` as the skill **argument**, and Codex fallback must share the same pre-DONE path checks

Deferred: undeclared top-level lore-repo hole in #22, check discovery vs skip-dotdirs, deterministic ignore-line assertions, `lrb` seeding all three standard lines.

Dropped as edge-case noise: “`.tmp/`-only tree never triggers #22” — rare when real workspaces already have top-level descriptors.

See `trilens-loop-feature.md`, `workspace-owned-default-ignore-lines.md`.
