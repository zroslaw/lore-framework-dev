---
lore: 1
type: topic
summary: "git -C <dir> can target a repo other than <dir> — escaping up to an enclosing repo, or following core.worktree to another directory; one rev-parse --show-toplevel vs realpath check catches both."
parent: lore-context.md
---

# `git -C <dir>` Is Not Always the Repo You Named — Guard Before Mutating

`git -C <dir> <command>` silently walks **up** the filesystem to the enclosing git repository when
`<dir>` is merely a directory *inside* one, rather than failing. Any framework code or procedure
that runs git against a directory it did not itself create as a git repo — a lore agent repo, a
declared sibling repo, anything discovered by path rather than by cloning — must verify that
directory is the ROOT of its own git repo before doing anything else with it, or every subsequent
`git -C` call in that procedure (pull, log, stamp-write) silently retargets the enclosing repo while
continuing to report the original path.

## Concrete instance (v31 `lr-core`, found by round-1 adversarial review, reproduced)

A lore repo that is a plain directory inside a larger git workspace (the framework's own documented
"workspace meta-repo" layout — see `workspace-meta-repo-pattern.md`) had `pull_repo` fast-forward the
*enclosing* workspace's `HEAD`, drop the TTL stamp inside the *enclosing* repo's `.git/`, and report
`"repo": ".../ws/repo-one"` — a mutating git operation attributed to a path it never touched, under
exit 0. `scan`'s `git log` similarly reported every committed topic as "uncommitted or untracked"
because the pathspec, built relative to the lore repo, matched nothing when run against the actual
(outer) toplevel.

## Fix pattern

Run `git -C <dir> rev-parse --show-toplevel`, compare against `realpath(<dir>)` (resolve symlinks on
both sides — macOS tempdirs are a real-world case of this mismatch), and refuse (a `skipped`/degraded
result, not a crash) rather than proceed when they differ.

- A **mutating** operation (pull, stamp write) needs the hard refusal — never silently act on the
  wrong repo.
- A **read-only** operation that must still work inside a nested layout (like a topic-date scan)
  should instead resolve paths against the real toplevel rather than refusing outright — refusing a
  read-only op over a mismatch it can route around is unnecessarily strict.

## Second hazard: `core.worktree` redirection (v46, `workspace-sync`)

The same guard catches a second, independent way `git -C <path>` acts on something other than
`<path>`. A repo whose config sets `core.worktree` — the dotfiles-in-`$HOME` pattern is the
ordinary benign case, not an attack — makes `status` / `add` / `commit` operate on **that other
directory**: an unattended sync would commit and push its files and record the repo's own tracked
files as deletions, because relative to the redirected worktree they are missing.

Here `<path>` genuinely *is* its own repo root, so the enclosing-repo hazard above is absent and
the redirection is invisible to every check but this one. The check was already written for the
workspace root and had simply never been applied to child repos. `/lr:workspace-sync` now blocks
such a repo and says why ([workspace-sync-feature.md](workspace-sync-feature.md)); the boot-time
upgrade gate in `version-check.md` applies the same comparison.

It is **not** a false positive on a **linked worktree checkout** (`.git` as a *file*), which
resolves its own toplevel to itself — verified. So one comparison distinguishes three states:
"this directory is inside someone else's repo", "this repo's tree is somewhere else", and "this
repo is itself a worktree".

**General form:** any helper that takes a path and shells out to a configurable tool should verify
the tool agrees about what that path *is*, before acting on it.

## When this applies

Apply this whenever writing or reviewing any script/procedure that takes a directory path and runs
`git -C` against it without having verified provenance (i.e., without having `git init`ed or
`git clone`d that exact path itself). This is distinct from the CWD/relative-path hazards in
`tooling-cwd-safety.md` (`cd` drifting later tool calls; `-C` reframing relative path *arguments*
within its own command) — this is a third, separate hazard: `-C` reframing which repo the command
targets in the first place, silently, when the directory isn't a repo root.

## See Also

- `tooling-cwd-safety.md` — the sibling CWD/`-C` hazards (drift and relative-path reframing); this
  topic is the third member of that family.
- `verify-regression-tests-via-mutation.md` — the regression tests for this bug (and its sibling
  `scan` misreport) were verified by mutation rather than trusted on first green.
- `v31-lr-core-parked-2026-07-25.md` — the parked feature where this was found and fixed.
- `workspace-meta-repo-pattern.md` — the workspace layout that makes "directory inside a larger git
  repo" a real, not hypothetical, case.
