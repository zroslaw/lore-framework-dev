Historical v11 baseline. The `workspace-sync` utility was the workspace-level git orchestration
skill that bootstrapped a fresh workspace (cloning declared siblings) and kept an existing one in
sync (pulling everything). It replaced `/lr:pull-domain` in v11 and was itself hard-renamed and
expanded in v25 into `/lr:workspace-pull` with `lore-workspace.md` + domain `repos:` two-level
declarations. Use `v25-workspace-pull-init-design.md` for the current shape.

**Script:** `lore-framework/scripts/workspace-sync [path]`

- Defaults to `.` if no path given.
- Discovers every `<workspace>/<subdir>/lore-repo.md`, parses each `repos:` block, merges into a deduplicated URL set.
- **Phase 1** — clones missing repos in parallel; output captured per-repo (clone progress would be unreadable interleaved).
- **Phase 2** — pulls every top-level git repo (existing + freshly cloned) in parallel with `--ff-only`; output streamed with a `[repo-name]` prefix in real time.
- Conflicts (remote mismatch, target-not-a-repo, dir-collision, clone/pull failure) are collected and reported at the end with one-line resolution hints. Repos in any conflict state are **skipped during the pull phase** — never run `git pull` against an unexpected remote.
- Exit codes: `0` clean, `1` conflicts/failures, `2` invalid invocation.
- Bash 3.2+ compatible (default macOS).

**Skill:** `/lr:workspace-sync`
- One-line delegation to `${CLAUDE_PLUGIN_ROOT}/scripts/workspace-sync` with cwd as the argument.
- Same skill-doc pattern as the rest of the framework: thin SKILL.md pointing to `docs/workspace-sync.md`.

**`repos:` schema** (in `lore-repo.md` frontmatter):
```yaml
repos:
  - git@github.com:org/repo-a.git
  - https://github.com/org/repo-b.git
```
Block-form list only. Inline-flow (`repos: [a, b]`), nested keys, anchors, and merge keys deliberately not supported — keeps the awk-based parser surface tight. Optional field; absence is fine. See `docs/workspace-sync.md`.

**Hardening applied during initial review** (security + parser robustness lens):
- **Path-traversal rejection.** Derived dir names of `.`, `..`, empty, slash-containing, or `-`-prefixed are refused with a conflict report. A hostile descriptor cannot reach into the workspace's parent directory.
- **Argument-injection prevention.** `git clone -- "$url" "$target"` so flag-shaped URLs become positional args.
- **Frontmatter anchored to line 1.** Code-fenced YAML examples in body content are not parsed as live declarations.
- **BOM tolerance.** UTF-8 BOM-prefixed descriptors parse correctly.
- **Symlink skip.** Symlinked top-level dirs are skipped during enumeration — no pulling repos that live outside the workspace via a symlink trick.
- **ANSI-escape scrub** on URL display. Control bytes stripped before printing summary lines.
- **`--ff-only` pulls** so divergent local branches surface as failures rather than silent merge commits.
- **`GIT_TERMINAL_PROMPT=0`** so HTTPS auth failures don't deadlock parallel children sharing a TTY.
- **`LC_ALL=C`** on git invocations so the summary's heuristic message detection works under any user locale.
- **Ctrl-C cleanup.** SIGINT/SIGTERM kills in-flight clone children and removes the tmpdir before exiting.

**Skill-to-script delegation pattern:**
When a skill is purely mechanical (no Claude judgment needed), it should call a shell script rather than instruct Claude to perform the steps itself. Benefits: script is independently usable without Claude, skill stays thin, `${CLAUDE_PLUGIN_ROOT}` resolves the path regardless of install location, parallel git operations don't burn tokens.

**Why one command (not separate `/lr:sync` + `/lr:pull`):**
First-run and steady-state are the same operation — the script just sees more missing repos on the first run. A separate "bootstrap" command would duplicate logic and add a step users have to remember on day one. See `framework-improvements-backlog.md` for the deferred-but-considered separations.

## See Also

- `framework-improvements-backlog.md` — `repos:` validators in `/lr:check`, undeclared-top-level-repo nudge.
- `plugin-vs-agent-repo-separation.md` — context for why declared-repos belongs in `lore-repo.md` (not in a separate manifest).
- `agent-discovery-nesting-constraint.md` — companion: `repos:` lands clones at workspace root, which keeps them discoverable.
- `yaml-parser-shell-hardening-checklist.md` — operational distillation of the parser/security hardening applied to this script. Apply when any future framework script parses user-controlled descriptor content.
- `workspace-vs-domain-vocabulary.md` — the v11 vocabulary split that unlocked this feature design.
- `parallel-reviewer-fanout-pattern.md` — the multi-lens review pattern used during this skill's two-round ship review.
