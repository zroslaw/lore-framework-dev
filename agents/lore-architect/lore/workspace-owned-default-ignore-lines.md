# Standard ignore lines (the term "workspace-owned" is retired)

> **Terminology, v37.** *Workspace-owned* was overloaded — it meant two different things eleven
> lines apart in `check.md`. Split and retired:
> - **standard ignore lines** — the three entries below; *content inside* `.gitignore`.
> - **framework-managed paths** — what `/lr:workspace-push` may stage; defined in code
>   (`workspace_scan.MANAGED_PATHS`), rendered by docs, never restated. See
>   [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md).

A git-tracked lore workspace should always ignore these exact lines in `.gitignore`:

- `/.worktrees/` — non-default-branch checkouts
- `/.lr-beings/` — Being Keeper runtime state
- `/.tmp/` — local scratch (debug logs, throwaway fixture repos)

**Who maintains them**

- `/lr:workspace-init` writes them during initialization and re-asserts them on every convergence
  pass. **As of v37 there are no `--refresh` / `--reconfigure` flags** — init converges.
- `/lr:workspace-pull` phase 3 re-asserts them, plus a `/<dirname>/` line for **every child git repo
  on disk** — declared or not (v37, D9). Declaration governs cloning and pulling; ignoring governs
  safety. A child whose directory name would corrupt the file as a pattern (leading `!` or `-`, or
  any of `*`, `?`, `[`) is skipped and reported instead — see
  [widening-a-source-drops-its-validation.md](widening-a-source-drops-its-validation.md).
- `/lr:check` #22 warns if any standard line or child-repo line is missing; as of v37 it renders
  finding **S7** from the scanner rather than re-deriving the rule.

**Scratch rule:** disposable / test scaffolds belong under `.tmp/<name>/`, not as a top-level workspace child. Top-level throwaways look like undeclared agent repos and pollute `git status`. Lifecycle `create-repo` fixtures use `.tmp/new-fixture-repo` and pass that path as the skill **argument**.

**Deferred follow-ups.** *Closed in v37:* undeclared top-level repos are now covered — they are
ignored by phase 3, reported as finding S5, and named by a pull-time nudge; lifecycle `test_19`
now asserts that an undeclared child gains its ignore line. *Still open:* check §1 "scan all
directories" can disagree with `lr-core` skip-dotdirs; `lrb workspaces add` still only appends
`/.lr-beings/`.

Landed on local `main` via merge of `lore-architect/workspace-scratch-ignores` into both `lore-framework` and `lore-framework-dev`. See also `v25-workspace-pull-init-design.md`, `consistency-checks.md`, `trilens-feedback-only-selective-apply.md`, `fold-feature-into-local-main-via-stash.md`.
