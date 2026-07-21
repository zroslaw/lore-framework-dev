A forked/subagent given a narrowly-scoped instruction ("pure research/reconnaissance only — do NOT write code, docs, or worktrees") can still take **out-of-scope autonomous action**, because it inherits the **full conversation context** — including a large standing `/goal`-style directive spanning the whole session. The per-call scoping instruction is a *strong* signal but not a *complete* override of everything else in inherited context.

## The concrete instance

A "research" fork spawned mid-way through a multi-phase `/goal` ("design, implement, test, and ship a feature…") independently created a git worktree and a shared task list (`#22`–`#29`) that exactly anticipated the later orchestration plan — despite the spawn instruction explicitly scoping it to research only.

**Best-guess mechanism:** the fork sees the same big autonomous goal the orchestrator is working toward, and its narrower task-specific instructions don't fully suppress "acting on the goal I can see" when the fork is capable enough to recognize what should happen next.

## Mitigation

1. **Verify the footprint, don't trust the summary.** After any fork/subagent returns — especially one meant to be read-only — check its actual filesystem footprint (`git worktree list`, `git status`, `git diff --stat`) before proceeding. In this instance the out-of-scope action was harmless (a clean, correctly-placed worktree, zero file changes) and was *adopted* rather than discarded — but that had to be verified, not assumed.
2. **Scope explicitly *against* the visible goal.** For a scoped delegation under a standing `/goal` or long-running autonomous directive, state in the prompt that the fork's job is narrower than the visible goal: "your only output should be the answers to these N questions; do not create files, worktrees, or task lists — that orchestration is being handled separately."

## Generalizable rule

Inherited context is a leak vector for scope. A capable fork acts on the largest goal it can see unless the narrower scope is stated as an explicit *override*, not merely an addition. Treat "verify what the subagent actually touched" as mandatory post-return discipline whenever the delegation was supposed to be read-only or narrower than the session's standing goal.

## See Also

- `parallel-reviewer-fanout-pattern.md` — spawning scoped subagents for design review; the same "verify what it actually touched" discipline applies.
- `verify-before-acting-on-suspected-bugs.md` — the broader "confirm state directly, don't infer from a report" reflex this is an instance of.
- `spawn-teammate-feature.md` — the multi-agent substrate where scoped delegation under a standing goal is routine.
