# Worktree Lifecycle and Audit

The workspace worktree convention needs a lifecycle as well as a location rule: otherwise concurrent work leaves abandoned dirty trees, branches, and files.

`create → active → park or hand off → ready to land → land → retire`

- **Create:** use the standard `.worktrees/<repo>/<slug>/` location, a named branch, and one designated writer.
- **Active:** a dirty worktree is allowed only while it has an active owner.
- **Park or hand off:** make a WIP commit, or explicitly hand off the current diff and its owner; do not make stashes the normal parking mechanism.
- **Ready to land:** commits are scoped and validation status is known.
- **Land:** merge or complete the PR into its target branch.
- **Retire:** remove the worktree; delete its branch only after confirming it is merged or intentionally abandoned.

An audit should derive its report from Git rather than require new mandatory metadata: each worktree's branch, last-commit age, clean/dirty status, and merged status, with stale or unowned dirty trees flagged. Keep Git worktrees as the primitive; do not add a heavyweight wrapper command before the convention and report prove insufficient.

## See Also

- `worktrees-convention.md` — current workspace invariant and placement rule
- `framework-improvements-backlog.md` — lifecycle/audit implementation follow-up
- `team-lore-contribution-governance.md` — branches and review as the shared lore publication path
