# Draft — v25 Workspace Pull (extends Cursor ops parity)

Status: **planned** — to ship in v25 alongside cursor-ops-parity work.
Session: 2026-07-12. **Revised after 3-lens review cycle (round 1).**

Supersedes: `docs/workspace-sync.md` behavior (hard rename + two-level pull + optional workspace repo).
Related: `workspace-pull-utility.md` (renamed from `workspace-sync-utility.md`),
`workspace-vs-domain-vocabulary.md`, `framework-improvements-backlog.md` § Init / Workspace Bootstrap.
Companion: `draft-v25-workspace-init.md`.

---

## The Problem

v11's `/lr:workspace-sync` reads **only** domain-level declarations (`repos:` in each
`lore-repo.md`) and pulls top-level git children. It does not:

1. Version a **team workspace layout** as its own artifact (`lore-workspace.md` in an optional
   workspace git repo).
2. **Pull the workspace repo first** so teammates receive descriptor changes (new repos) via git.
3. Run an explicit **two-phase** reconcile: workspace-level repos first, then domain-level repos
   declared inside lore agent repos.
4. Manage **`.gitignore`** for nested clones when the workspace root is git-tracked.
5. Name the operation by user intent: **pull fresh state**, not "sync".

## Objective

Extend **v25** with **`/lr:workspace-pull`** (hard rename from `workspace-sync`) that:

- Optionally pulls a git-tracked workspace root (with dirty-tree guard).
- Reads a workspace descriptor and clones/pulls **workspace-level** repos.
- Then discovers every top-level `lore-repo.md` and clones/pulls **domain-level** repos from each
  `repos:` block.
- Appends `.gitignore` entries for all **declared** child repos present on disk (not only newly
  cloned this run).
- Works unchanged when the workspace root is **not** a git repo (local-only mode).

### Semantic commitment

**Two levels of repo declarations, one command:**

| Level | Descriptor | `repos:` means |
|-------|------------|----------------|
| **Workspace** | `<workspace>/lore-workspace.md` | High-level layout — which top-level repos belong in this workspace |
| **Domain** | `<lore-agent-repo>/lore-repo.md` | Agent-domain dependencies — sibling repos agents in that domain need |

Same YAML key, different semantics — document both in `conventions.md`.

`/lr:workspace-pull` runs both levels in order. Domain discovery requires workspace-level agent
repos to be present first — the workspace list must include lore agent repos themselves (or they
must already exist on disk from a prior pull).

## Non-Goals (v25 workspace-pull slice)

- Branch/ref pinning in descriptors.
- Git submodules.
- Auto-removing clones when a repo drops out of a descriptor (`--prune` deferred).
- Workspace descriptor version stamp / migrations.
- Auto-committing `.gitignore` changes.
- Nested agent-repo discovery (still top-level subdirs only).

---

## Artifacts

### `lore-workspace.md` (new, workspace root)

```yaml
---
description: Yaroslav's agentic dev workspace
repos:
  - git@github.com:zroslaw/lore-framework-dev.git
  - git@github.com:zroslaw/lore-agents.git
---
```

- Block-form `repos:` only (same parser rules as `lore-repo.md`).
- **High-level list only** — repos that should exist as top-level siblings in `<workspace>/`.
- Optional markdown body for human onboarding (user-owned; framework updates frontmatter only on
  `--reconfigure`).
- **Optional file** — if absent, phase 1 is a no-op; phase 2 (domain) still runs (backward compat).

### Workspace git repo (optional)

When `<workspace>/.git` exists:

- `lore-workspace.md`, `AGENTS.md`, `README.md`, `scripts/` are **tracked**.
- Child repo directories are **gitignored** (managed by workspace-pull).
- `origin` remote optional — pull phase 0 skipped when absent.

---

## Procedure — `/lr:workspace-pull`

Script: `scripts/workspace-pull` (refactor from `workspace-sync`). Skill name: `/lr:workspace-pull`
(Claude/Codex: colon form; Cursor slash picker: `/lr-workspace-pull` wrapper).

### Phase 0 — Workspace root pull (conditional)

```
IF <workspace>/.git AND origin remote configured:
  IF working tree or index is dirty (any tracked modification that would block
     git pull --ff-only — not lore-workspace.md alone):
    WARN to stderr — skip phase 0, use local files
  ELSE:
    git -C <workspace> pull --ff-only
    ON failure (network, auth, diverged history):
      WARN to stderr — not fatal; proceed with local lore-workspace.md
ELSE:
  skip (local-only workspace — not an error)
```

Phase 0 failure **never** increments the exit-1 problem counter when phases 1–4 succeed.

### Phase 1 — Workspace-level repos

```
IF <workspace>/lore-workspace.md exists:
  parse repos: via parse_repos_field (same awk as lore-repo.md)
  merge into declared set
FOR each URL:
  derive dirname via url_to_dir, classify clone | present | conflict
Clone missing workspace-level repos (parallel)
```

### Phase 2 — Domain-level repos

```
Discover every <workspace>/<subdir>/lore-repo.md (top-level only; skip symlinks)
FOR each descriptor: parse repos:, merge into declared set (dedupe with phase 1)
FOR each URL not already satisfied: classify clone | present | conflict
Clone missing domain-level repos (parallel)
```

**Ordering invariant:** phase 1 completes before phase 2 begins.

**Partial phase 1 warning:** if N workspace-level clones failed, warn that domain-level repos
declared inside those missing agent repos may not have been discovered — fix clone failures and
re-run.

**Union dedupe:** same URL in workspace and domain descriptors → clone once.

### Phase 3 — `.gitignore` plumbing (conditional)

```
IF <workspace>/.git:
  IF .gitignore absent: create with managed header only (no /worktrees/ — that's workspace-init)
  FOR each URL declared in phases 1–2 that is successfully cloned OR already present (not conflict):
    derive dirname; skip if url_to_dir rejected it
    skip dirnames with gitignore metacharacters (* ? [ ! prefix) — defense in depth
    IF line "/<dirname>/" not already in .gitignore (exact line match):
      append "/<dirname>/"
  (never auto-commit)
```

Template header when creating from scratch:

```gitignore
# Child repositories — managed by /lr:workspace-pull (lore-framework v25+)
```

### Phase 4 — Pull all top-level git repos

```
FOR each top-level subdirectory that is a git repo (skip symlinks):
  git pull --ff-only (parallel)
Skip repos in conflict state from earlier phases.
```

Repos freshly cloned in phases 1–2 are included; `Already up to date` is expected, not an error.

**Scope note:** phase 4 also pulls top-level git repos that are **not** declared in any descriptor
(v11 parity — e.g. manually cloned app repos). Only conflict-state repos are skipped.

### `url_to_dir` hardening (extend v11)

Reject empty, `.`, `..`, `-` prefix, slashes, **and gitignore metacharacters**: `*`, `?`, `[`,
`!` prefix.

### Exit codes

Unchanged: `0` clean, `1` failures/conflicts, `2` invalid invocation.

### Summary report (extended)

```
workspace:          <path>
lore-workspace.md:  present | absent
descriptors:        N lore-repo.md file(s)
workspace-level:    N URL(s)
domain-level:       M URL(s) (K after dedup)
cloned:             ...
pulled:             ...
phase-0:            ok | skipped | warned
conflicts:          ...
```

---

## Rename & compatibility

| Old (v11–v24) | New (v25) |
|---------------|-----------|
| `/lr:workspace-sync` | `/lr:workspace-pull` |
| `docs/workspace-sync.md` | `docs/workspace-pull.md` |
| `scripts/workspace-sync` | `scripts/workspace-pull` |
| `.cursor-skills/lr-workspace-sync/` | `.cursor-skills/lr-workspace-pull/` |
| `workspace-sync-utility.md` (lore topic) | `workspace-pull-utility.md` (update for v25) |

**Hard rename** — no thin wrapper, no deprecation alias. Doctor catalog may note stale
`workspace-sync` skill name for one release. Update all cross-refs including `auto-pull.md`,
`pull-lore.md`, `init.md` → `workspace-init.md`, README, INSTALL-*.

---

## Example — two-level workspace

`agent-workspace/lore-workspace.md`:

```yaml
repos:
  - git@github.com:zroslaw/lore-framework-dev.git
```

`lore-framework-dev/lore-repo.md`:

```yaml
repos:
  - git@github.com:zroslaw/lore-framework.git
```

**First `/lr:workspace-pull`:** phase 0 (if git) → clone dev → discover dev's lore-repo.md → clone
framework → gitignore both → pull all.

**Teammate adds `lore-agents` to `lore-workspace.md`, pushes:** phase 0 pull → clone agents →
domain merge → gitignore → pull all.

---

## Framework changes (checklist)

### Script
- [ ] Refactor `scripts/workspace-sync` → `scripts/workspace-pull` (phases 0–4).
- [ ] Phase 0 dirty-tree guard; phase 0 failure non-fatal.
- [ ] Phase 1: `parse_repos_field "$WORKSPACE/lore-workspace.md"`.
- [ ] Phase 3: all declared present repos, not only newly cloned.
- [ ] Extend `url_to_dir` for gitignore metacharacters.
- [ ] Update awk warning string `workspace-sync` → `workspace-pull`.
- [ ] Partial phase 1 domain-discovery gap warning.

### Docs & skills
- [ ] `docs/workspace-pull.md`; hard-remove workspace-sync surfaces.
- [ ] `conventions.md` — `lore-workspace.md` schema; dual meaning of `repos:`.
- [ ] Cross-ref sweep: `auto-pull.md`, `pull-lore.md`, README, INSTALL-*.

### Check
- [ ] #22: declared child on disk but not gitignored in git workspace → warn.
- [ ] #23: legacy `lr:init:start` markers without `lr:workspace-init:start` → warn + remediation.

### Lore topic
- [ ] Rename/update `workspace-sync-utility.md` → `workspace-pull-utility.md`.

### Release
- [ ] Amend `release-notes/25.md` (workspace-pull + workspace-init; cache-affecting).
- [ ] Close backlog items: workspace creation automation, richer init payloads.

### Harness (pre-ship gate)

**workspace-pull (S1–S14):**

| # | Scenario |
|---|----------|
| S1 | Fresh two-level clone (workspace + domain repos) |
| S2 | Idempotent re-run (no duplicate gitignore) |
| S3 | Non-git workspace (phases 0+3 skip) |
| S4 | Backward compat: no lore-workspace.md, lore-repo.md only |
| S5 | Phase 0 dirty working tree → warn, phases 1–4 proceed |
| S6 | Phase 0 network failure → warn, not fatal |
| S7 | URL dedup across workspace + domain levels |
| S8 | Dir collision (two URLs → same dirname) |
| S9 | Path traversal URL rejected |
| S10 | Gitignore metacharacter dirname rejected |
| S11 | Phase 4 pull of freshly cloned repo (already up to date) |
| S12 | Gitignore merge with existing user patterns |
| S13 | Symlinked top-level dir skipped |
| S14 | Remote mismatch conflict |

**workspace-init (S15–S18):** setup wizard fixture, refresh idempotency, legacy marker migration,
refresh after pull populates agents.

- [ ] All scenarios green before v25 push.

### Dogfood
- [ ] Scaffold `agent-workspace` via `/lr:workspace-init`.

---

## Pairing with workspace-init

| Command | Role |
|---------|------|
| `/lr:workspace-init` | Setup wizard + memory-file refresh; setup ends with `workspace-pull` |
| `/lr:workspace-pull` | Ongoing pull: workspace repo → workspace-level → domain-level repos |

**Manual repo add (preferred over `--reconfigure`):** edit `lore-workspace.md`, commit, teammates
run `workspace-pull` only.

---

## Resolved decisions

1. `lore-workspace.md` ✓
2. Hard rename `workspace-sync` → `workspace-pull` (no alias) ✓
3. `/lr:workspace-init` replaces `/lr:init` ✓
4. Phase 3 covers all declared present repos ✓
5. Phase 0 dirty-tree → warn and skip, not fatal ✓

---

## See Also

- `draft-v25-workspace-init.md`
- `review-v25-workspace-ux.md` — round 1 UX review artifact
- `workspace-vs-domain-vocabulary.md`
- `agent-discovery-nesting-constraint.md`
