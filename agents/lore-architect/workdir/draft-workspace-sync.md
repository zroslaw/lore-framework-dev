# Design — `/lr:workspace-sync` (v46)

Date: 2026-09-13. Status: design for implementation this session.

## Problem

Lore stops flowing between people and sessions because repos accumulate blockers nothing
resolves: uncommitted findings sitting dirty for days, commits ahead of origin that were never
pushed, pulls blocked by local modifications, branches diverged from origin, and worktree
registrations pointing at directories that no longer exist. Today's evidence in this very
workspace: `lore-agents` carries eleven uncommitted health-advisor lore files,
`lore-framework-dev` is three commits ahead of origin, and the workspace repo is dirty.

`/lr:workspace-pull` only fast-forwards (and `--ff-only` is file-granular, so any of the above
blocks it). `/lr:workspace-push` only publishes the workspace repo's own framework-managed files.
`/lr:check` reports and never repairs. Nothing closes the loop.

The v46 session-worktree design would prevent these states from arising. It is unfinished. This
utility does not prevent them — it **resolves them after the fact**, which is a much smaller
problem, and is worth having even once worktrees land.

## Scope

One command, `/lr:workspace-sync`, that drives every repo in the workspace to: *everything local
is committed, integrated with origin, and published* — or reports precisely why it is not.

**Non-goals.** No session isolation, no worktree lifecycle, no branch policy, no PR creation, no
release automation. It does not replace `workspace-pull` (which clones missing declared repos) or
`workspace-push` (which curates *which* workspace files are framework-managed).

## Repo classification

| Kind | Detected by | Treatment |
|---|---|---|
| **Workspace repo** | the workspace root is its own git root | publish (commit + integrate + push) |
| **Lore agent repo** | top-level dir containing `lore-repo.md` | publish |
| **Source repo** | any other top-level dir that is a git repo | **integrate only** — fetch and merge origin; never commit, never push |

Source repos are pull-only by deliberate asymmetry: committing and pushing somebody's in-progress
source work is a destructive act dressed as helpfulness, and the goal for those repos is only "am I
on the latest version". Lore repos are the opposite — their whole purpose is shared knowledge, and
an uncommitted lore file is a finding nobody else can see.

## The one ordering decision that carries the safety

**Commit first, then fetch, then merge, then push.**

Committing before fetching means the merge is always between two *commits*, never between a commit
and a dirty working tree. Everything the user had is in git history before any remote state
arrives, so no remote content can overwrite unsaved work, `git merge --abort` always restores an
exact prior state, and the merge either completes or leaves recoverable conflict markers over
content that is already safely committed.

This is also why `--ff-only`'s file-granular failures stop mattering: by merge time the tree is
clean, so the "modified tracked file an incoming commit touches" case cannot arise.

## Per-repo procedure

Each repo is independent. One repo's failure never stops another; there is no cross-repo atomicity.

**Phase 0 — Resume.** If a merge is already in progress (`MERGE_HEAD` present): unmerged paths
remaining ⇒ report `blocked: conflict` with the path list and stop for this repo. No unmerged paths
⇒ the model resolved them since the last run, so `git commit --no-edit` and continue. This makes a
plain re-run the continuation mechanism: no state file, no `--continue` flag, and the condition is
derived from git rather than asserted by a marker.

**Phase 1 — Inventory.** Branch, upstream, origin URL, ahead/behind, dirty and untracked paths,
worktree registrations. Detached HEAD, no origin remote, or no upstream branch ⇒ report and skip
the repo; guessing the intended branch is exactly the kind of guess that loses work.

**Phase 2 — Commit** (publish repos only). Stage every non-ignored change — tracked modifications,
deletions and untracked files — except the junk filter below, and commit as
`workspace-sync: publish local state`. Report the exact path list. Nothing to stage ⇒ no commit,
not an empty one.

*Junk filter* (never staged, never deleted): `*.swp`, `*.swo`, `*~`, `.DS_Store`, `*.orig`,
`*.rej`, `__pycache__/`. These are editor and merge debris; committing them publishes noise, and
they are the one category where "preserve everything" would degrade the shared repo. Everything
else is committed, because a file the user left in a lore repo is a finding until proven otherwise.

**Phase 3 — Integrate.** `git fetch origin`, then `git merge --no-edit origin/<upstream-branch>`.
A merge, never a rebase: rebase rewrites local commits and can drop them under conflict; merge
keeps both histories intact, which is the data-preservation requirement in git terms. Outcomes:
up to date, fast-forwarded, merged, or **conflict** ⇒ leave the merge in progress, report the
conflicted paths, stop for this repo. The conflicted content is safe: both sides are committed and
the markers are recoverable.

**Phase 4 — Push** (publish repos only, unless `--no-push`). `git push origin HEAD:<branch>`. On
rejection (origin advanced mid-run), re-run phases 3–4 up to 3 attempts total. Never `--force`.
Push failure with the local commit intact is reported as `local-only` — *pending publication, not
success*.

**Phase 5 — Worktree hygiene.** `git worktree prune` removes registrations whose directory is
gone. That deletes no content and is always safe, so it always runs. Worktree *directories* are
only removed under `--prune-worktrees`, and only when all three hold: the checkout is clean, its
branch has no commits missing from the repo's default branch, and it is not the current worktree.
Anything else is reported as a retained candidate with the reason. Deleting a worktree holding
unmerged commits or dirty files is precisely the data loss this utility exists to avoid.

## Conflict resolution — the split

The script does every deterministic thing and **stops at semantic judgement**. A conflict leaves
markers in files and a structured `conflicts: [paths]` list in the JSON; resolving lore prose is
the model's job, following the merge rules already written in `docs/resolve-conflicts.md`
(preserve both sides' distinct information, prefer the more specific version, never invent content,
never delete a side to make it compile). The doc then re-runs the command, and phase 0 picks it up.

This keeps the script small and honest: *script emits data, doc owns the words* — and the one thing
that genuinely needs a reader of the content stays with the reader of the content.

## Interface

```
lr-core workspace-sync [--workspace DIR] [--dry-run] [--no-push] [--prune-worktrees]
```

`--dry-run` performs no writes at all and reports the planned action per repo. Output is the
standard `{ok, data, warnings, errors}` object; `data.repos[]` carries one entry per repo with
`kind`, `branch`, `actions[]`, `committed[]`, `integrate`, `push`, `worktrees`, and `blocked`.
`ok:false` when any publish repo ends blocked or local-only.

## Prohibited operations (invariants, enforced by absence and by test)

`reset --hard`, `checkout --force`, `push --force`/`--force-with-lease`, `stash`, `clean`,
`--autostash`, `rebase`, and deleting any tracked or untracked file. A test asserts the module's
source contains none of these tokens, because the rule is easier to break than to notice.

## Artifacts

- `lore-framework/scripts/lr_core/workspace_sync.py` — literate accelerator; docstrings normative.
- `lore-framework/scripts/lr_core/cli.py` — `workspace-sync` subcommand.
- `lore-framework/skills/workspace-sync/SKILL.md` — thin pointer.
- `lore-framework/docs/workspace-sync.md` — Step 0 announcement, operation notice (it commits and
  pushes), invocation, conflict-resolution routing, report rendering, manual fallback pointer.
- `lore-framework/.cursor-skills/lr-workspace-sync/` — generated by `scripts/sync-cursor-skills`.
- `lore-framework-dev/tests/test_workspace_sync.py` — deterministic tests over real git sandboxes.
- README skill table, `release-notes/46.md`, `VERSION`, four manifests at `1.46.0`.
