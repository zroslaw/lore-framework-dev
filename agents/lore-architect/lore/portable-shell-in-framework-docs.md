Framework-authored shell commands run wherever the agent booted — and the primary dev platform is macOS (BSD userland), not GNU/Linux. Commands that silently assume GNU coreutils break there, and the failure is invisible: a `command not found` (exit 127) inside a best-effort flow reads as the underlying operation failing, not as a portability bug.

## Canonical instance (motivated v14)

v13 auto-pull's "short timeout (60s)" guidance invited `timeout 60 git …`. `timeout`/`gtimeout` are GNU coreutils, absent on stock macOS → exit 127 → auto-pull aborts → boot drops to degraded mode for a spurious reason. Net effect: **v13 auto-pull silently never ran on macOS** (the primary dev platform) even though it appeared shipped. A whole shipped feature was a no-op on the main platform because of one non-portable binary buried in emitted guidance.

## Rules (codified in `conventions.md` § Tooling: Portable Shell)

- **No GNU-only binaries** — especially `timeout`/`gtimeout`. To bound a Claude-run command, use the **Bash tool's own timeout parameter**, not a `timeout` wrapper.
- **Standalone scripts have no Bash-tool timeout** and no portable one-liner for a hard wall-clock cap. Prevent hangs at the source instead: fail-fast env vars (`GIT_TERMINAL_PROMPT=0`, `GIT_SSH_COMMAND` with `BatchMode`/`ConnectTimeout`) or a bash watchdog (background + `sleep` + `kill`). `scripts/workspace-sync` takes the fail-fast-env-vars route.
- **Watch BSD-vs-GNU flag diffs** on tools present in both userlands: `sed -i` (BSD needs `-i ''`), `date -d` (GNU-only), `readlink -f` / `realpath` (not always present), `grep -P`, `xargs -r`.
- **Prefer git's own knobs** over external wrappers: `GIT_TERMINAL_PROMPT=0`, `GIT_SSH_COMMAND`, `git -C <repo>`.

## Transport-aware hang model (where the timeout actually lives)

The portable-shell rule pairs with auto-pull's hang model: the **Bash-tool timeout is the transport-agnostic backstop** (kills any stall regardless of SSH/HTTPS/future transport — the universal no-hang guarantee); the git env vars are per-transport **fast-fail niceties** layered on top. See `auto-pull-mechanism.md` for the full model.

## Composition

Same shape as `tooling-cwd-safety.md` — a portability landmine hidden inside an emitted shell command; name the rule rather than fixing the one-off. An application of `naming-foundational-principles.md`. When authoring or reviewing any doc or script that emits shell, assume BSD/macOS and check every command.

## See Also

- `tooling-cwd-safety.md` — sibling "hazard hidden inside emitted shell" discipline (CWD drift vs portability); both are cases of articulating the hazard precisely
- `auto-pull-mechanism.md` — the v14 fix that motivated this rule; carries the transport-aware hang model (Bash-tool-timeout backstop + per-transport fast-fail env vars)
- `naming-foundational-principles.md` — the meta-rule this topic applies (name the principle, don't fix the instance)
- `plugin-compat-template-audit.md` — adjacent "audit every emission site" discipline; portability is one more axis to audit at template/doc-emission sites
- `versioning-release-types.md` — v14 history entry (release-notes-only, cache-affecting)
