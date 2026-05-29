When writing a shell script that parses YAML frontmatter from user-controlled markdown files (e.g., `lore-repo.md`), apply this hardening checklist. Distilled from the security review of `scripts/workspace-sync` — every item below caught a real issue.

## Parser-side

1. **Anchor frontmatter to line 1.** Otherwise a code-fenced YAML example in the body is parsed as live frontmatter. Concrete attack: a doc that contains
   ````
   ```yaml
   ---
   repos:
     - https://EVIL/should-not-clone.git
   ---
   ```
   ````
   gets its example URLs cloned. Fix: `NR == 1 { if ($0 ~ /^---/) fm = 1; else exit }`.

2. **Strip BOM on line 1.** UTF-8 BOM (`\xEF\xBB\xBF`) prefix from Windows editors makes line-1 anchor fail silently — frontmatter never opens, file looks empty. Strip in awk: `if (NR == 1 && substr($0, 1, 3) == "\357\273\277") $0 = substr($0, 4)`.

3. **Strip trailing CR.** CRLF line endings break `$/` regex anchors. Universal fix: `sub(/\r$/, "", $0)` on every line.

4. **Quote-aware `#` comment stripping.** A naive `sub(/[[:space:]]*#.*$/, "", line)` mangles `"https://gitlab/group/repo#branch"` into `"https://gitlab/group/repo` (unbalanced quote, fails clone). Fix: only strip `#` comments when the value's first char isn't `"` or `'`.

5. **Warn on unclosed frontmatter.** Track a state counter (0 = before, 1 = inside, 2 = closed). Warn at EOF if state is still 1 — the file is malformed, results may be incomplete.

## URL-derived-name side

6. **Reject path-traversal in derived dir names.** A URL like `https://x/..git`, `https://x/..`, or `https://x/.` strips `.git` and yields `..` or `.`. The script then operates on the workspace's parent. Reject empty, `.`, `..`, `-`-prefixed, and slash-containing names with an explicit conflict report.

7. **Argument terminator on `git clone`.** `git clone -- "$url" "$target"`. Without `--`, a URL starting with `-` is parsed as a flag. Fixes the `--upload-pack=cmd` injection class entirely.

8. **Skip symlinks** when enumerating workspace dirs. Otherwise a symlink targeting `/Users/me/.ssh` (or any other repo) gets pulled.

9. **Scrub control bytes before display.** A URL containing literal `\033[` paints fake "all green" output over real failures. `LC_ALL=C tr -d '\000-\010\013\014\016-\037\177'` before any `echo`/`printf` of attacker-controlled data.

## Parallel-execution side

10. **Index-suffix tmpfile keys.** A name-only sanitizer collides: `foo bar` and `foo_bar` both map to `foo_bar`. Two parallel writers race the same tmpfile. Fix: combine sanitized name with the loop index → `i-name`.

11. **Trap signals to kill children.** `trap cleanup_signal INT TERM` plus `kill -- -$$` in the handler — otherwise Ctrl-C leaves backgrounded `git clone` processes running, partial dirs survive, next run sees them as conflicts.

12. **`GIT_TERMINAL_PROMPT=0`** at script entry. Parallel git processes sharing one TTY would otherwise deadlock on a credential prompt.

13. **`LC_ALL=C` on git invocations** whose output you parse heuristically (`Already up to date.`, `N file(s) changed`). Without it, non-English locales silently break the success/failure heuristics.

## Bash 3.2 compat (default macOS)

14. **No associative arrays.** Use parallel indexed arrays + linear search. Fine for dozens of entries.

15. **`${arr[@]:-}` injects a phantom empty element** when the array is empty (under `set -u`). `for u in "${arr[@]:-}"` runs once with `u=""`. Guard with `[[ ${#arr[@]} -eq 0 ]] && return ...` first, then iterate `"${arr[@]}"` unguarded.

## Cleanup-on-failure

16. **`rm -rf` partial clones on clone failure.** Otherwise the partial dir survives, next run reports it as "exists but is not a git repository" → manual cleanup required.

## Verification approach

shellcheck + targeted smoke tests per item: empty workspace, BOM-prefixed descriptor, code-fenced fake frontmatter, path-traversal URLs, conflict-state remote mismatch. Each test catches one or two items.

## When to apply

Whenever the framework grows another shell script that parses user-controlled descriptor content. The checklist is the operational distillation of the parallel-reviewer security lens; applying it up front saves a round-trip with reviewers later.

## See Also

- `workspace-sync-utility.md` — the script this checklist was distilled from.
- `parallel-reviewer-fanout-pattern.md` — the multi-lens review process under which the security lens caught these. This checklist makes the security lens cheaper to internalize.
- `tooling-cwd-safety.md` — adjacent: shell CWD hygiene across tool calls.
