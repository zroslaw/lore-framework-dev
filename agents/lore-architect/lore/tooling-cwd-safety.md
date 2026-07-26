Bash, Glob, Grep, and Read share the same process working directory. A `cd <subdir>` inside a Bash call silently shifts the CWD for every *later* tool call — including Glob patterns you think are relative to the domain root. This has bitten lore-architect operations more than once.

## The failure mode

`cd lore-agents && git status --porcelain` in a Bash call moves CWD to `lore-agents/`. A subsequent `Glob("lore-framework/migrations/4.md")` then resolves against `lore-agents/lore-framework/...` — which doesn't exist — and returns empty. The natural inference is "file missing" or "framework broken". Neither is true.

## Prescription

- **Never `cd` in Bash** if any downstream tool call depends on CWD. Use `git -C <lore-agent-repo> …` for git. Absolute paths for Glob/Grep/Read when working across repos.
- **When a Glob returns empty for a file you expect**, the first hypothesis is wrong CWD, not missing file. Verify with `pwd` before drawing conclusions.
- **Framework bugs are rare, tool-state drift is common.** When diagnosing a boot failure, confirm the symptom on disk with an absolute-path `ls` before blaming the framework.

## Codification in framework

v5 added the **Tooling: CWD Safety** section to `lore-framework/docs/conventions.md`, and converted every `git …` in framework docs (`update.md`, `version-check.md`, `check.md`, `lore-search.md`) to `git -C <lore-agent-repo> …`. Checks 13 and 14 of `/lr:check` use the same form.

Any new framework doc touching filesystems across repo boundaries must follow the same pattern. If you catch yourself writing `cd <repo> && git …`, replace it with `git -C <repo> …` unless a later step genuinely needs that CWD for an unrelated tool.

## The flip side: `git -C` has its own relative-path trap

Switching from `cd <repo> && git …` to `git -C <repo> …` fixes the CWD-drift hazard above, but `-C` reframes **every relative path in the command** to resolve against the `-C` target, not the shell's cwd. This bites hardest with `worktree add`:

`git -C <repo> worktree add <relative-path> -b <branch> <start-point>` resolves `<relative-path>` relative to `<repo>`, **not** the shell cwd. Running `cd <workspace> && git -C lore-framework worktree add .worktrees/lore-framework/<slug> …` (expecting the worktree at `<workspace>/.worktrees/...` per `worktrees-convention.md`) instead lands it **nested inside the repo**: `<workspace>/lore-framework/.worktrees/lore-framework/<slug>/`. Reproduced identically for a second repo in the same batch — a systematic framing gotcha, not a typo.

**Fix:** when using `git -C`, pass an **absolute path** for any destination argument (worktree dir, output file), or `cd` into the repo and use a relative path (as `worktrees-convention.md`'s own examples do — `cd <workspace>/<repo>` then `../.worktrees/...`). The convention doc's examples were already safe; the mistake was substituting `git -C` for `cd` without re-deriving the path's frame of reference.

**Recovery:** `git worktree remove <path> --force` then `git branch -D <branch>`, then redo with an absolute path. No data lost if the worktree was pre-populate-only (no commits yet).

The two hazards are complementary: `cd` drifts cwd for *later* tool calls; `-C` reframes relative paths *within its own command*. The safe habit that dodges both: `git -C <repo>` **with absolute paths** for any path argument.

## Scope

This is a domain-specific operational rule for agents that work across multiple sibling repos in a single domain — the entire reason lore-architect exists. Agents scoped to a single repo can ignore it.

## A third hazard: `-C` can silently retarget which repo, not just which path

The two hazards above (drift, relative-path reframing) both assume `git -C <dir>` at least operates
on `<dir>`'s own repo. It doesn't always: if `<dir>` is merely a directory *inside* a git repo rather
than that repo's root, `git -C <dir>` silently walks up to the enclosing repo and operates on *that*
— under exit 0, still reporting `<dir>` as the target. See `git-dash-c-needs-toplevel-guard.md` for
the fix (verify `rev-parse --show-toplevel` matches `realpath(<dir>)` before any mutating op) and a
concrete instance that hit exactly this in a workspace meta-repo layout.

## See Also

- `dirty-tree-gates-write-vs-read-distinction.md` — adjacent "name what the gate is protecting against" git-discipline. CWD safety and dirty-tree gates are both cases of **articulating the hazard precisely** rather than reflexively applying defensive boilerplate.
- `worktrees-convention.md` — the worktree placement rule the `git -C` relative-path trap silently violates; its own example commands (`cd` + relative) are already safe.
- `git-dash-c-needs-toplevel-guard.md` — the third `-C` hazard (silent repo-retargeting), distinct from the two above.
