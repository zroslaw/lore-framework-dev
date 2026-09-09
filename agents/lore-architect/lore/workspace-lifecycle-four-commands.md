---
lore: 1
type: topic
summary: "The workspace command surface — init (converges), pull, push, and diagnosis — all reading one deterministic scanner; v45 folded the status half into /lr:check."
parent: lore-context.md
---

# The Workspace Lifecycle: Four Commands, One Scanner

    workspace-init    initialize, or CONVERGE an initialized workspace to disk reality
    workspace-pull    consume  — pull the workspace repo, clone declared repos, pull top-level repos
    workspace-push    publish  — commit and push the framework-managed workspace files
    workspace-status  diagnose — read-only; every finding names the command that fixes it
                                (v45: absorbed into `/lr:check`; the skill no longer exists)

## The gap this closed

v25 shipped a complete **consumer** half and no **producer** half. `workspace-pull` phase 0
received teammates' descriptor changes, but `workspace-init` "printed the commit checklist", phase 3
edited `.gitignore` without committing, `finalize` was scoped to agent repos, and `update`
explicitly excluded the workspace repo. Framework writes accumulated dirty forever, and teammates
received stale state.

**Carry the general question, not just the fix: whenever a layer gains a consumer, ask what
publishes.** A consumer with no producer looks complete from the inside — everything it reads is
there — and only fails from the outside, where nobody is looking.

## One scanner, four consumers

`lr-core workspace-scan` (`scripts/lr_core/workspace_scan.py`, a literate accelerator) emits git
state, descriptors, children, memory-file state, shortcut inventory, the framework-managed path set
with dirty classification, and findings **S1–S18** (v42 added S17, routing descriptions; v43 added
S18, project-scope plugin settings). Init observes with it, status renders it,
`/lr:check` renders them, push takes its path set from it. No doc restates the
rules; the shared finding catalog owns each finding's wording, per
[script-emits-data-doc-owns-the-words.md](script-emits-data-doc-owns-the-words.md).

**v45 changed the surface, not the scanner.** `/lr:workspace-status` was removed and its
diagnosis became the workspace layer of `/lr:check`; `docs/workspace-status.md` became the shared
`docs/findings-catalog.md`, now serving every layer and every caller. Findings gained a new S19
(per-repo pull freshness) and S10 `stale_command_list`. Init, pull and push are unchanged. See
[unified-check-front-door.md](unified-check-front-door.md).

**Init converges** — no `--refresh` / `--reconfigure`. Converge is defined precisely as *drive the
scanner's findings to zero*, which is exactly what keeps init and status from drifting apart. A
workspace at canonical state reports `already current` and writes nothing.

## What the scanner does not cover (verified 2026-08-23)

`lr_core/workspace_scan.py` detects dirty working trees **only for the workspace root**. S1 covers
dirty framework-managed paths, S12 covers other dirty workspace-root paths. **There is no finding of
any kind for a dirty *child* repo** — confirmed by reading `build_findings` and the `dirty` /
`other_dirty` computation, both of which derive from a single `git status` on the workspace root.

This matters because "a child repo is dirty and can't be pulled" is the intuitive motivating case for
workspace-freshness work, and it is easy to assume the scanner already covers it. Any feature that
wants to report it must derive it itself.

Related boundary in `scripts/workspace-pull`: it dirty-guards only **phase 0** (the workspace root).
**Phase 4 fast-forwards every top-level child repo with no dirty check at all** — a pull can therefore
change files under a session that has uncommitted work and still report success, because `--ff-only`
succeeds whenever the incoming commits do not touch the dirty files.

**How to apply:** to know whether a child repo is dirty, ask git directly —
`git -C <repo> status --porcelain` for dirty, `git -C <repo> rev-list --count HEAD..@{u}` for behind.
Both are local and cheap. Do not expect a scanner finding to carry it. Whether reporting it is the
*right* response is a separate question — see
[guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md).

## Decisions worth remembering

- **Push stages framework-managed paths only**, by explicit path argument, never `git add .`.
  Other dirty files are listed and left alone. Auto-committing whatever is dirty is how unrelated
  work ships under a generic message.
- **The join/found seam discriminates on `git merge-base`, never on a commit count.** This workspace
  has a committer that is not a person (the Chronicler Being), so "no local commits yet" is not
  evidence of a fresh workspace. Same reason push's plan *shows* the riding-along commits from
  `git log --oneline @{u}..HEAD` instead of counting them: you confirm specific work, not a number.
- **Adopting a remote commits everything to `pre-join-<short-sha>` first.** The join path runs after
  init has already written the memory file and descriptor, and a workspace worth joining has its own
  versions of those files — so the switch must never be a bare `reset --hard`.
- **Declining a remote is recorded** as optional `sharing: local` in `lore-workspace.md`, which
  suppresses finding S3. *A finding a user can never clear teaches them to skim the whole report* —
  that is the reason the key exists, and it generalizes to every recurring diagnostic.
- **Ignoring is wider than declaring.** `.gitignore` covers every child git repo on disk; declaration
  governs only cloning and pulling. An undeclared clone can be committed into the workspace repo
  just as easily as a declared one.

## What v42 and v43 added to this surface

- **v42 — the surface runs on its own.** `lr-core preflight` gained a second leg that refreshes the
  workspace at most once per 16h, delegating to `workspace-pull` under a process bound and a
  filesystem lock. `workspace-init` also became the maintainer of the `AGENTS.md` **AI routing map**,
  auditing repo and agent descriptions as one aligned set (finding S17), with canonical text staying
  in `lore-repo.md` / `role.md` / the new optional `repo-context` block.
- **v43 — the workspace configures the plugin for whoever clones it.** `workspace-init` Step 4 writes
  committed `.claude/settings.json` and `.cursor/settings.json`; both joined `MANAGED_PATHS`, making
  them **the first managed paths whose content is mostly not the framework's**. Finding S18 (info)
  reports their absence. See
  [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md).

## See Also

- [workspace-memory-file-contract.md](workspace-memory-file-contract.md) — the v3 payload this surface writes.
- [workspace-meta-repo-pattern.md](workspace-meta-repo-pattern.md), [v25-workspace-pull-init-design.md](v25-workspace-pull-init-design.md) — the layer this completes.
- [workspace-owned-default-ignore-lines.md](workspace-owned-default-ignore-lines.md) — the ignore lines, and the terminology v37 retired.
- [literate-accelerator-pattern.md](literate-accelerator-pattern.md) — what the scanner is.
- [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md) — the design, shipped in v42,
  that makes this surface run on its own at boot, and the first consumer of the child-dirty gap above.
- [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md) — the v43 addition
  to `MANAGED_PATHS` and finding S18.
- [consistency-checks.md](consistency-checks.md) — the pre-v45 numbered catalog that used to render
  these findings as #22–24.
- [unified-check-front-door.md](unified-check-front-door.md) — where the diagnosis half went in v45.
