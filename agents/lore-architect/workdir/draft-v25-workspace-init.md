# Draft — v25 Workspace Init (replaces `/lr:init`)

Status: **planned** — ships in v25 with workspace-pull.
Session: 2026-07-12. **Revised after 3-lens review cycle (round 1).**

Supersedes: `docs/init.md` (hard rename `init` → `workspace-init`).
Companion: `draft-v25-workspace-pull.md`.

---

## The Problem

Today's `/lr:init` only writes a **worktree convention** block into the workspace memory file
(`AGENTS.md` / `CLAUDE.md`). It does not scaffold the workspace recipe, optional git root,
`lore-workspace.md`, `.gitignore`, or clone children.

## Objective

**`/lr:workspace-init`** — single entry point for workspace bootstrap and refresh:

| Mode | When | What it does |
|------|------|--------------|
| **Setup** | Not initialized | Interactive wizard → confirm → write artifacts → `workspace-pull` → memory file |
| **Refresh** | Initialized | Update memory-file managed section only |

Hard rename from `/lr:init` (no alias).

```
workspace-init  =  producer  (writes recipe, optional git root, README, memory file)
workspace-pull  =  consumer  (reads recipe, clones/pulls children, maintains gitignore)
```

Setup mode always ends with `scripts/workspace-pull`. Refresh mode does **not** auto-pull unless
the user asks.

---

## Precondition (document in skill + INSTALL guides)

The user must have **framework context** before invoking workspace-init — e.g. Cursor session
with `--plugin-dir`, loaded plugin, or mid-session fallback reading `.cursor-skills/lr-workspace-init/SKILL.md`.
An empty directory with no framework loaded cannot run the skill; document the bootstrap path
(clone framework → launch with plugin-dir → run workspace-init).

---

## Initialized?

A workspace is **initialized** when **either**:

1. `<workspace>/lore-workspace.md` exists, **or**
2. `<workspace>/<memory-file>` contains well-formed `<!-- lr:workspace-init:start -->` … `end`.

| State | Mode |
|-------|------|
| Neither | **Setup** |
| One or both | **Refresh** (unless `--reconfigure`) |

Legacy `lr:init:start/end` markers → offer migration to `lr:workspace-init:*` on first run; if
declined, refresh inside old markers for one release; `/lr:check` #23 warns.

### Flags

| Flag | Behavior |
|------|----------|
| *(none)* | Auto-detect setup vs refresh |
| `--refresh` | Force memory-file refresh only |
| `--reconfigure` | Re-run setup interview (git settings + descriptor); confirm overwrites |

**Adding a repo:** prefer editing `lore-workspace.md` + `workspace-pull`. Use `--reconfigure` for
git init/origin changes or full re-interview.

---

## Setup mode — execution order

Steps below are numbered in **execution order**.

### Step 0 — Context

Resolve `<workspace>` (cwd), `<memory-file>` from engine profile, `<framework-root>`.

### Step 1 — Discover starting state

Report: `lore-workspace.md`, memory file + markers, workspace git state, child subdirs.

Suggest remotes from existing subdirs with `lore-repo.md` or `git remote get-url origin`.

### Step 2 — Workspace-level repos

Ask which **high-level repositories** belong in this workspace (ranked shortlist).

**Wizard copy must state:** include lore **agent repos themselves**; domain dependencies inside
`lore-repo.md` are cloned automatically by workspace-pull phase 2.

Confirm URL → dirname table before proceeding.

### Step 3 — Workspace git tracking

Ask: **Track this workspace as a git repository?**

**Wizard copy must state tradeoff:**

| No | No team descriptor sharing via git; no phase 0 pull; no gitignore automation for children. |
|----|---------------------------------------------------------------------------------------------|
| Yes | Team can share `lore-workspace.md`; workspace-pull manages gitignore; optional remote. |

#### 3a — Git init

`git -C <workspace> init` if needed. On failure: report, skip 3b, continue to step 4; user fixes
via `--reconfigure`.

#### 3b — Remote origin (optional)

Ask for `origin` URL or skip. `remote add` or `set-url` only after confirm if origin exists.

Never auto-commit or auto-push.

### Step 4 — Confirmation gate

Show summary before any writes:

```
Will create/update:
  - lore-workspace.md (N repos: ...)
  - .gitignore (if git workspace)
  - README.md (team join instructions)
  - git init + origin (if chosen)
Then run workspace-pull, then write <memory-file> managed section.
Proceed? (yes/no)
```

If no → stop without writes.

### Step 5 — Write `lore-workspace.md`

Frontmatter: `description`, `repos:` (block list). Body: optional user prose (preserved on
`--reconfigure`; framework updates only `description` + `repos:` in frontmatter).

On `--reconfigure`: rewrite frontmatter block only; **preserve other frontmatter keys** and body.

### Step 6 — Seed `.gitignore` (if git workspace)

**Idempotent:** if `.gitignore` already exists, do **not** truncate or overwrite — only append
`/.worktrees/` if that exact line is absent. workspace-pull phase 3 owns child-repo entries;
reconfigure must not wipe them.

If creating new file:

```gitignore
# Child repositories — managed by /lr:workspace-pull (lore-framework v25+)
# Do not commit nested repo contents into the workspace repo.

/.worktrees/
```

### Step 7 — Write `README.md` (default yes)

Minimal team-join template (no prompt fatigue — create unless user declined in step 4 summary):

```markdown
# <workspace description>

## Join this workspace

git clone <origin-url> && cd <dirname>
/lr:workspace-pull
/lr:workspace-init --refresh
/lr:boot <primary-agent>
```

Skip if no git remote (local-only workspace).

### Step 8 — Run `workspace-pull`

Invoke `scripts/workspace-pull`. On failure:

```
workspace-pull failed. Artifacts on disk: lore-workspace.md, .gitignore, README.md.
Recovery:
  1. Fix the reported error (auth, URL, conflict)
  2. /lr:workspace-pull
  3. /lr:workspace-init --refresh
```

Memory file not written yet — correct, since agents may not exist on disk.

### Step 9 — Write memory file managed section

Written **after** workspace-pull so agent discovery reflects disk state.

Markers: `<!-- lr:workspace-init:start -->` … `end`.

If agent scan returns zero results, emit fallback line in `### Agents`:

> _(Run `/lr:workspace-pull` then `/lr:workspace-init --refresh` to populate)_

Engine-aware command notation in managed section:

- Claude: `/lr:workspace-pull`, `/lr:boot`, `/lr:workspace-init`
- Cursor/Codex: `/lr-workspace-pull`, `/lr-boot`, `/lr-workspace-init` (or engine-neutral prose:
  "workspace-pull skill")

### Step 10 — Summary (includes register-repo hint)

Do **not** run register-repo wizard in v25 (deferred v26). Print as next step:

```
Optional: /lr:register-repo <repo-dirname>  # per-agent boot shortcuts
```

Commit checklist:

```bash
git -C "<workspace>" status
git add lore-workspace.md .gitignore README.md <memory-file>
git commit -m "Initialize lore workspace"
git push -u origin HEAD   # when ready
```

---

## Refresh mode

1. Read managed section (`lr:workspace-init` markers, or legacy `lr:init` with migration offer).
2. Build canonical payload v2 from disk (`lore-workspace.md`, agent scan).
3. Identical → "already current".
4. Else → diff managed section only → confirm → replace.

Does **not** modify `lore-workspace.md`, `.gitignore`, or run git. Empty agent scan → fallback
text in payload.

---

## Reconfigure mode

Re-run steps 2–9 with confirmation. Step 3a (`git init`) is idempotent on existing repos. Step 6
only appends missing `/.worktrees/` — never overwrites `.gitignore`. Does not delete child repos
removed from descriptor.

---

## Canonical payload v2

~~~markdown
<!-- lr:workspace-init:start -->
## Lore Framework Workspace

This directory is a Lore Framework workspace.

### Repositories
<dynamic dirnames or "See lore-workspace.md">

### Agents
<dynamic agent names or fallback hint>

### Commands
- workspace-pull — refresh descriptor and all declared repos
- boot \<agent\> — load a lore agent
- workspace-init --refresh — update this section after framework upgrade

### Conventions
- Top-level repos stay on their default branch.
- Non-default branch work → git worktree at `.worktrees/<repo>/<slug>/`.

Full convention: https://github.com/zroslaw/lore-framework/blob/main/docs/worktrees.md
<!-- lr:workspace-init:end -->
~~~

---

## Team join path

```bash
git clone git@github.com:team/agent-workspace.git
cd agent-workspace
/lr:workspace-pull
/lr:workspace-init --refresh
/lr:boot lore-architect
```

README in workspace repo makes this discoverable.

---

## Framework changes (checklist)

- [ ] Rename `skills/init/` → `skills/workspace-init/`; `docs/workspace-init.md`
- [ ] Hard-remove `/lr:init`; cross-ref sweep
- [ ] `/lr:check` #23 legacy markers
- [ ] Document precondition in INSTALL-CURSOR.md / README
- [ ] Lifecycle: S15–S18 (setup, refresh, migration, idempotency)
- [ ] Close backlog: workspace creation automation, richer init payloads
- [ ] v26 backlog: register-repo in wizard (step deferred from v25)

---

## Resolved (round 1 review)

| Item | Resolution |
|------|------------|
| Step order | 0–10 in execution order; pull before memory file |
| `/.worktrees/` | not `/worktrees/` |
| Phase 3 gitignore scope | all declared present repos (in pull draft) |
| register-repo in wizard | deferred v26; hint in summary |
| README | default yes |
| `git push` | `-u origin HEAD` |
| Thin wrapper | removed — hard rename only |
| Confirmation gate | step 4 before writes |

---

## See Also

- `draft-v25-workspace-pull.md`
- `review-v25-workspace-ux.md`
