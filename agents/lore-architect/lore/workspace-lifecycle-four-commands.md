---
lore: 1
type: topic
summary: "The v37 workspace command surface — init (converges), pull, push, status — all four reading one deterministic scanner."
parent: lore-context.md
---

# The Workspace Lifecycle: Four Commands, One Scanner

    workspace-init    initialize, or CONVERGE an initialized workspace to disk reality
    workspace-pull    consume  — pull the workspace repo, clone declared repos, pull top-level repos
    workspace-push    publish  — commit and push the framework-managed workspace files
    workspace-status  diagnose — read-only; every finding names the command that fixes it

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
with dirty classification, and findings **S1–S15**. Init observes with it, status renders it,
`/lr:check` #22–#24 render the subset they own, push takes its path set from it. No doc restates the
rules; `docs/workspace-status.md` owns each finding's wording, per
[script-emits-data-doc-owns-the-words.md](script-emits-data-doc-owns-the-words.md).

**Init converges** — no `--refresh` / `--reconfigure`. Converge is defined precisely as *drive the
scanner's findings to zero*, which is exactly what keeps init and status from drifting apart. A
workspace at canonical state reports `already current` and writes nothing.

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

## See Also

- [workspace-memory-file-contract.md](workspace-memory-file-contract.md) — the v3 payload this surface writes.
- [workspace-meta-repo-pattern.md](workspace-meta-repo-pattern.md), [v25-workspace-pull-init-design.md](v25-workspace-pull-init-design.md) — the layer this completes.
- [workspace-owned-default-ignore-lines.md](workspace-owned-default-ignore-lines.md) — the ignore lines, and the terminology v37 retired.
- [literate-accelerator-pattern.md](literate-accelerator-pattern.md) — what the scanner is.
