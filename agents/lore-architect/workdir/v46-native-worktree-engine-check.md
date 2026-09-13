# Native worktree capability check

Checked 2026-09-13. Evidence: official documentation and installed CLI help; no end-to-end
three-engine worktree lifecycle test. These are dated observations, not a permanent API contract.

- Claude Code 2.1.270 CLI has `--worktree`. [Worktree docs](https://code.claude.com/docs/en/worktrees)
  describe session isolation; [tools reference](https://code.claude.com/docs/en/tools-reference)
  describes EnterWorktree, including an existing worktree of the current repository.
- Codex CLI 0.142.5 help exposes `--cd` and `--add-dir`; no top-level worktree flag was observed.
  [Desktop docs](https://learn.chatgpt.com/docs/environments/git-worktrees) describe native worktree
  task creation and Handoff, which moves task/branch state rather than merging main and pushing.
  This session's app handoff tool cannot move its calling task. Neither observation is proof of
  capability absence in every Codex interface.
- Cursor CLI 2026.08.11-e8db854 exposes `--worktree`, `--worktree-base`, `--workspace`, `--add-dir`.
  [Worktree docs](https://cursor.com/docs/configuration/worktrees) distinguish Agents Window native
  controls from IDE `/worktree` and `/apply-worktree` skills, and document managed cleanup.
  [Multi-root announcement](https://cursor.com/changelog/04-24-26) establishes cross-repo editing.
  [April IDE explanation](https://forum.cursor.com/t/cursor-3-worktrees-best-of-n/156507/47)
  describes multi-root skill support and long-session path forgetting;
  [June support response](https://forum.cursor.com/t/worktrees-for-multi-projects/160168/6)
  says simultaneous native multi-root creation remained unsupported. These different surfaces
  must not be collapsed into a blanket capability claim. Historical forgetting is not a present
  failure measurement.

Local Git inspection confirmed the workspace, lore-framework-dev and lore-agents are independent
repositories, with the child repositories not tracked in the parent index. A parent worktree alone
therefore does not isolate their contents. Multi-root access is not evidence of automatic per-repo
isolation, persistent binding after compaction, or enforced prevention of primary writes.

Decision: Lore owns lifecycle in Python across engines. Optional native integration is presentation
and tool-path assistance only. Resume from [the decision](v46-session-worktree-decision.md); test
two repositories per engine, repeated boot/finalize, resume/compaction, and guards before readiness.
