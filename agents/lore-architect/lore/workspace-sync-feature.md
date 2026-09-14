---
lore: 1
type: topic
summary: "The v46 /lr:workspace-sync repair command: per-repo order, classification-driven treatment, commit-before-fetch safety, merge ownership, holds, terminal statuses, and what it deliberately does not do."
parent: lore-context.md
---

# `/lr:workspace-sync` (shipped v46)

The workspace layer's **repair** command, and the only one of the four that commits on the user's
behalf. `workspace-pull` only fast-forwards, `workspace-push` only publishes the workspace repo's
managed files, `/lr:check` reports and repairs nothing — so a workspace could sit with uncommitted
findings, unpushed commits and a blocked pull, and nothing closed the loop. Shared Lore stops
flowing long before anything looks broken, which is exactly the divergence mechanism in
[lore-repo-divergence-is-self-inflicted.md](lore-repo-divergence-is-self-inflicted.md).

## Shape

Per repository, in order: **resume a merge this command left behind → inventory → commit → fetch
and merge → push → worktree hygiene.**

Classification decides treatment:

- **Lore agent repos** (have `lore-repo.md`) — committed, integrated and pushed in full.
- **The workspace repo** — integrated and pushed, but only **framework-managed paths** are ever
  staged, sharing the `is_managed` predicate with `workspace-push` so the two cannot drift
  ([a-new-command-inherits-its-neighbours-published-promises.md](a-new-command-inherits-its-neighbours-published-promises.md)).
- **Source repos** (no `lore-repo.md`) — brought up to date only; never committed, never pushed.
  Committing somebody's in-progress source work and publishing it is not a service.

Flags: `--dry-run`, `--no-push`, `--prune-worktrees`.

**The name is reused.** `workspace-sync` was the v11–v24 clone-and-pull bootstrap that v25 renamed
to `/lr:workspace-pull` ([workspace-sync-utility.md](workspace-sync-utility.md)); it had not
existed for twenty-one versions. `docs/fix-stale-plugin-cache.md` had been citing that rename as
its worked example of a stale cache, which would now misdiagnose a v46 user who correctly sees the
new command — it cites the v45 `doctor` -> `check` replacement instead.

## Load-bearing design points

- **Commit before fetch** is the whole safety argument —
  [commit-before-fetch-makes-a-merge-recoverable.md](commit-before-fetch-makes-a-merge-recoverable.md).
- **Ownership of an in-progress merge is claimed *before* the merge runs**, in a marker under the
  checkout's git dir holding the target sha. Claiming afterwards leaves a window where a kill
  produces a real merge with no evidence we started it, and every later run disowns it
  *permanently*. The marker is a hint revalidated against `MERGE_HEAD`, never a verdict
  ([a-state-file-is-a-hint-not-a-verdict.md](a-state-file-is-a-hint-not-a-verdict.md)).
- **Re-running is the continuation.** There is no `--continue`: phase 0 derives the resume
  condition from git itself, refuses a merge it did not start, and names the exact commands that
  end that state.
- **Holds** — junk, nested repos (tracked submodule *and* untracked clone), symlinks,
  credential-shaped names, files over 25 MB. Held paths are reported and left on disk, never
  deleted, and a hold **never applies to a deletion**
  ([a-guard-must-not-block-its-own-remedy.md](a-guard-must-not-block-its-own-remedy.md)).
- **`core.worktree` redirection blocks a repo** rather than publishing somebody else's directory
  ([git-dash-c-needs-toplevel-guard.md](git-dash-c-needs-toplevel-guard.md)).
- **One terminal status per repo**, initialized to `not-attempted` as a fail-safe:
  `published`, `up-to-date`, `local-only`, `blocked`, `skipped`, `not-attempted`. `local-only`
  means **pending publication, never success**. Repos are isolated so one failure cannot erase the
  report for repos that already pushed.
- **The committed list is read back from git** (`git diff-tree --name-only -r HEAD`) rather than
  reported from intent, so a hook that adds or drops paths cannot make the report lie.
- Prohibited throughout: `reset --hard`, `checkout --force`, `push --force`, `stash`, `clean`,
  `--autostash`, `rebase`, and deleting any file. Asserted by an **AST walk of every `git()` call
  site** with a subcommand allowlist — a text grep either trips on the header that names these
  operations *because* it forbids them, or gets weakened until it proves nothing.

## Deliberately not done

No lock of its own — git's index lock arbitrates, and the doc states the limit. Hooks are not
bypassed: `--no-verify` would also disable the secret-scanning hooks that protect exactly this kind
of unattended publishing.

## Relationship to the session-worktree design

Shipped as a deliberate substitute for the unfinished session-worktree design. That design
**prevents** these divergence states; this command **resolves** them after the fact. Shipping the
repair does not reduce the case for the prevention, and the repair stays useful once prevention
lands. See [v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).

Gate record and scope for the release: [versioning-release-types.md](versioning-release-types.md).
What review caught that the suite could not:
[defects-hide-in-the-intersections-a-suite-partitions.md](defects-hide-in-the-intersections-a-suite-partitions.md).
