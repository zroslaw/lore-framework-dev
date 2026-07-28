# Workspace-owned default ignore lines

A git-tracked lore workspace should always ignore these exact lines in `.gitignore`:

- `/.worktrees/` — non-default-branch checkouts
- `/.lr-beings/` — Being Keeper runtime state
- `/.tmp/` — local scratch (debug logs, throwaway fixture repos)

**Who maintains them**

- `/lr:workspace-init` setup and **reconfigure** seed them (Step 6).
- `/lr:workspace-pull` phase 3 re-asserts them (plus declared child `/<dirname>/` lines).
- `/lr:check` #22 warns if any standard line is missing (renamed conceptually to “workspace gitignore coverage”).
- `/lr:workspace-init --refresh` does **not** touch `.gitignore` — use `workspace-pull` to repair ignores on an already-initialized workspace.

**Scratch rule:** disposable / test scaffolds belong under `.tmp/<name>/`, not as a top-level workspace child. Top-level throwaways look like undeclared agent repos and pollute `git status`. Lifecycle `create-repo` fixtures use `.tmp/new-fixture-repo` and pass that path as the skill **argument**.

**Deferred follow-ups** (not closed by this change): `#22` still does not cover undeclared top-level lore-repos; check §1 “scan all directories” can disagree with `lr-core` skip-dotdirs; no deterministic lifecycle assert yet that init/pull wrote the three lines; `lrb workspaces add` still only appends `/.lr-beings/`.

Landed on local `main` via merge of `lore-architect/workspace-scratch-ignores` into both `lore-framework` and `lore-framework-dev`. See also `v25-workspace-pull-init-design.md`, `consistency-checks.md`, `trilens-feedback-only-selective-apply.md`, `fold-feature-into-local-main-via-stash.md`.
