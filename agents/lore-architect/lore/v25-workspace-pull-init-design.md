v25 **workspace layer** design and local implementation. The workspace slice landed in
`lore-framework/main` as local commit `0311ab6` after the branch split collapsed into main. It is
not pushed yet; the full lifecycle suite remains the final empirical gate.

## Commands (hard renames)

| Old | New | Role |
|-----|-----|------|
| `/lr:workspace-sync` | `/lr:workspace-pull` | Consumer: pull workspace repo → workspace-level repos → domain-level repos |
| `/lr:init` | `/lr:workspace-init` | Producer: setup wizard + AGENTS.md refresh |

No deprecation aliases. Cursor wrappers were regenerated after the hard renames.

## Two-level repo declarations

| Level | File | `repos:` means |
|-------|------|----------------|
| Workspace | `<workspace>/lore-workspace.md` | High-level layout — agent repos, app repos, etc. |
| Domain | `<lore-agent-repo>/lore-repo.md` | Dependencies for that domain's agents |

`workspace-pull` runs workspace-level clone first, then domain-level clone from each discovered
`lore-repo.md` (agent repos must be in workspace list or already on disk). Union dedupe. Same
parser (`repos:` block-form); `conventions.md` now distinguishes workspace-level and domain-level
semantics.

## workspace-pull phases

0. Workspace root `git pull --ff-only` if git + origin; **any dirty working tree** → warn, skip,
   not fatal.
1. `lore-workspace.md` → clone missing.
2. All `*/lore-repo.md` → clone missing domain deps.
3. Gitignore: all **declared present** children (not only newly cloned); `url_to_dir` rejects
   gitignore metacharacters.
4. Pull all top-level git repos (undeclared repos still pulled — v11 parity).

## workspace-init

Setup: interview → **confirmation gate** → write descriptor → idempotent `.gitignore` seed
(`/.worktrees/` append-only) → default README → **workspace-pull** → memory file v2 (after pull).
Refresh: managed section only. `--reconfigure`: re-interview; gitignore never truncated.
register-repo wizard **deferred v26** (hint in summary).

Optional workspace git repo — team shares recipe; children gitignored.

## Verification & ship gate

Three-lens review (architecture, UX, implementation) — three rounds, converged approve 2026-07-12.
Implemented verification covered script fixtures for two-level clone, idempotency, non-git
workspace, git-workspace gitignore maintenance, domain-only backward compatibility, and unsafe URL
rejection. `claude plugin validate --strict` passed; cursor wrapper parity was 30/30; a haiku smoke
test followed the renamed skill pointers. The full lifecycle suite remains the final pre-push gate.

## See Also

- `workdir/draft-v25-workspace-pull.md` — canonical pull spec
- `workdir/draft-v25-workspace-init.md` — canonical init spec
- `workspace-meta-repo-pattern.md` — optional workspace-as-git-repo envelope
- `workspace-design-review-discipline.md` — review process
- `workspace-sync-utility.md` — v11 script baseline (rename to workspace-pull-utility on ship)
- `workspace-vs-domain-vocabulary.md`
- `v25-cursor-ops-parity-design.md`
