# Workspace Lifecycle Redesign — Design Draft

**Status:** designed 2026-08-09 in dialogue with the user; ready for review, near-ready for
implementation. Targets the release after v36.
**Scope:** the workspace layer's command surface, the workspace memory-file contract, and the
publication path for workspace-level state.
**Supersedes:** parts of `docs/workspace-init.md` (modes/flags, marker protocol, payload v2);
extends `docs/workspace-pull.md`; absorbs this session's drafted `docs/workspace-push.md` and
check #24 (see § Already-drafted artifacts).

---

## 1. Problem

The workspace layer shipped in v25 with a complete **consumer** half and no **producer** half:

- `workspace-pull` phase 0 pulls the workspace repo so teammates' descriptor changes arrive — but
  nothing ever pushes them. `workspace-init` explicitly never commits ("prints the commit
  checklist"), `workspace-pull` phase 3 edits `.gitignore` without committing, `finalize` phase 4
  is scoped to agent repos (`git add agents/`), and `update.md` explicitly excludes the enclosing
  workspace repo as a publication target while its migrations regenerate workspace-root shortcuts.
- Consequence, observed live on the dogfood workspace (2026-08-09): `AGENTS.md` and a registered
  shortcut dirty from framework-generated refreshes that were never committed; a stray untracked
  `scripts/lr_core/` copy; **no origin remote at all** — so the entire team-sharing story of the
  workspace layer has never run end-to-end. See Appendix A.
- Secondary frictions: the `<!-- lr:workspace-init:* -->` HTML-comment markers make the memory
  file read as generated goo; the `--refresh` / `--reconfigure` flag taxonomy pushes mode
  bookkeeping onto the user; there is no quick way to see the workspace's operational state; and
  the memory file is engine-forked (`CLAUDE.md` vs `AGENTS.md`), so a mixed-engine team's founder
  chooses which engine's teammates start blind.

## 2. Concepts (unchanged)

- **Domain** — the scope of one lore agent repo (`lore-repo.md`; `agents/<name>/` with role,
  lore, workdir, sessions). The portable, team-shared unit; travels between workspaces via git.
- **Workspace** — the directory the engine runs from; contains one or more domains plus the other
  repos they declare, side by side. Optionally itself a small git repo (the **meta-repo**) that
  versions the assembly recipe — descriptor, memory files, `.gitignore`, `README.md`, registered
  shortcuts — and never child-repo contents (each child has its own history and is gitignored).
- **`lore-workspace.md`** — frontmatter `description` + block-form `repos:` (clone URLs of the
  top-level repos, including the agent repos); body is user prose. Schema unchanged by this
  design.

## 3. Design summary

Four commands with the `workspace` prefix — two existing, two new, zero renames:

| Command | Status | One-line semantics |
|---|---|---|
| `/lr:workspace-init` | rework | Initialize an uninitialized workspace; on an initialized one, **converge** it to current disk reality (absorbs `--refresh`/`--reconfigure`). |
| `/lr:workspace-pull` | small deltas | Pull the workspace repo (if git-tracked), clone declared-but-missing repos (both levels), maintain `.gitignore`, pull every top-level repo. |
| `/lr:workspace-push` | **new** | Commit framework-managed workspace files and push the workspace repo. Never touches child repos or user files. |
| `/lr:workspace-status` | **new** | Read-only diagnosis: branches, worktrees, dirty/unpushed workspace state, declaration drift — each finding with a suggested fix. |

Settled decisions (from the 2026-08-09 design dialogue):

- **D1 — Four-command surface.** `init` / `pull` / `push` / `status`. "Add a repo" and "add an
  agent" need no fifth command: create or clone the thing, run `init` (it notices and offers), or
  use the existing `create-*` / `register-*` skills.
- **D2 — Init converges.** One entry point, no user-facing mode flags. Uninitialized → full
  interview. Initialized → convergence pass: re-scan disk, offer undeclared repos, refresh
  managed sections, re-assert `.gitignore`, raise git/remote questions only when something is off.
  The confirmation gate (D12) is what makes "refreshes completely" safe.
- **D3 — Push publishes framework-managed paths only.** Other dirty workspace-root files are
  listed in the plan and left untouched. Committing arbitrary user files automatically is how
  unrelated work ships under a generic message. (User-confirmed decision.)
- **D4 — Status and check share one scanner.** The findings logic is written once
  (deterministic, script-backed — see § 6.4) and consumed by both `/lr:workspace-status` (quick
  pane) and `/lr:check` (deep sweep). No prose duplication of the rules.
- **D5 — Named sections replace HTML-comment markers** in the memory file. The exact headings
  become the ownership contract; the file reads as a real document. Marker-based workspaces are
  migrated by `init` (one-time, offered, not forced).
- **D6 — One writer per section.** Lore Framework intro ← `init`. Repositories ← `init`.
  Agents ← `register-agent` / `unregister-agent` (and `register-repo` as the batch form).
  `init`'s convergence re-renders the Agents section **from the registered shortcuts on disk** —
  registration remains the single membership authority; init is only the renderer.
- **D7 — The Agents section lists *registered* agents** (the "what can I boot here" answer).
  Agents on disk but unregistered do not appear; `status` nudges about them.
- **D8 — `CLAUDE.md` and `AGENTS.md` carry the same content.** Baseline mechanism: `init` writes
  both files identically and `status` flags drift. Candidate optimization (Open Question OQ1):
  `AGENTS.md` canonical + `CLAUDE.md` as a one-line `@AGENTS.md` import — adopt only after
  empirical verification on Claude Code. Consequence either way: command notation inside the
  shared content must be engine-neutral (see § 4.1).
- **D9 — `.gitignore` covers *all* child git repos on disk**, declared or not. Declaration
  governs cloning/pulling only; ignoring governs safety. (Today only declared repos are ignored.)
- **D10 — The memory file carries a Lore Framework section**: what this workspace is, links to
  the framework repo, the command set, core conventions, and the **no-plugin fallback**: an
  engine without the `lr` plugin is advised to clone `lore-framework` into the workspace and use
  its `docs/` as the instruction source. `init` offers to include the framework repo in the
  workspace `repos:` list so `workspace-pull` materializes that fallback automatically.
- **D11 — Init synchronizes with the remote**, with an explicit found-vs-join seam (§ 5.1
  Step 6): empty remote → initial commit + push; remote with history while local is fresh → this
  is a *join*, fast-forward to it; both with history → stop and explain.
- **D12 — The confirmation gate and diff-before-replace survive.** No file writes before the user
  approves the plan; managed-section rewrites show a scoped diff first.

## 4. The memory-file contract

### 4.1 Canonical payload (v3 — sections, not markers)

Both memory files (`AGENTS.md`, `CLAUDE.md`) carry, in this order, before any user content
additions:

~~~markdown
# <workspace description>

## Lore Framework

This directory is a [Lore Framework](https://github.com/zroslaw/lore-framework) workspace —
named agents with persistent, git-shared knowledge, usable from Claude Code, Codex, or Cursor.

Skills (invoke per your engine: `/lr:<skill>` on Claude Code, `/lr-<skill>` on Cursor/Codex):

- **workspace-init** — initialize this workspace, or refresh it after anything changed
- **workspace-pull** — pull the workspace repo, clone declared repos, pull all top-level repos
- **workspace-push** — commit and push framework-managed workspace files
- **workspace-status** — diagnose workspace state with fix suggestions
- **boot `<agent>`** — load a lore agent

Conventions: top-level repos stay on their default branch (production state); non-default-branch
work goes in git worktrees under `.worktrees/<repo>/<slug>/`; local scratch under `.tmp/<name>/`
(full convention: https://github.com/zroslaw/lore-framework/blob/main/docs/worktrees.md).

No `lr` plugin in this engine? Clone the framework into the workspace —
`git clone https://github.com/zroslaw/lore-framework.git` — and use its `docs/` as the
instruction source, starting with `docs/agent-boot.md`.

## Repositories

- `<dirname>` — <description from lore-repo.md / lore-workspace.md, or "(no description)">
- ...

## Agents

- `<agent-name>` (`<repo-dirname>`) — <role description>. Boot: **lr-<agent>-agent** shortcut,
  or **boot <agent-name>**.
- ...
~~~

Exact wording of the intro prose is draft-level; the structure and the three headings are the
contract. Notes:

- **Engine-neutral notation.** Because the same content lives in both files, skill references use
  the neutral form with a one-line per-engine legend, never a single engine's slash syntax.
- The `# <workspace description>` title is framework-written at creation but afterwards treated
  as user-owned (renaming the workspace title must not fight the tool).
- The Repositories section lists **declared** repos (union of `lore-workspace.md` and domain
  `repos:`) plus present-on-disk undeclared git repos are *not* listed — they are `status`
  findings, not workspace facts.

### 4.2 Ownership and edge behaviors

- The framework owns the exact headings `## Lore Framework`, `## Repositories`, `## Agents` and
  regenerates each section's body (heading to next heading). Everything else in the file is user
  content and is never touched.
- **User renames or deletes a framework heading:** the writer recreates the canonical section at
  its canonical position; the orphaned user-renamed section is left in place; `status` flags the
  duplication.
- **User edits inside a framework section:** overwritten at the next regeneration — but every
  regeneration goes through diff-and-confirm (D12), so the user sees the loss before accepting.
- **Section order:** framework sections first, in canonical order, then user sections. If user
  sections have been interleaved, regeneration edits section bodies in place and does not reorder
  the file; `status` may note non-canonical order as informational.
- **Both files, one change:** every writer (init, register-agent family) applies the same edit to
  both memory files in the same operation. A file missing entirely is created with the full
  payload.

### 4.3 Migration from markers

`init`'s convergence pass detects a `<!-- lr:workspace-init:start/end -->` (or legacy
`<!-- lr:init:* -->`) pair and offers a one-time conversion: parse the managed block, re-render as
v3 sections, drop the markers, preserve all content outside the markers verbatim. Declining keeps
the old format working for this release; `/lr:check` warns until migrated (today's #23,
generalized).

## 5. Command specifications

### 5.1 `/lr:workspace-init` (rework)

**Invocation:** no flags in the common path. (`--dry-run` may be kept as a debugging aid;
`--refresh`/`--reconfigure` are retired — their behaviors are absorbed by convergence.)

**Step 0 — Context.** Resolve `<workspace>` (cwd), `<framework-root>`, engine (for reporting
only; file content is engine-neutral per D8).

**Step 1 — Observe.** Collect, without writing anything:
- descriptors: `lore-workspace.md` present? parseable? declared repo set;
- memory files: which exist, format (v3 sections / marker-based / absent), drift between the two;
- workspace git state: repo? own git root (realpath comparison — the macOS `/var` symlink rule
  from `version-check.md` Step 1b)? origin remote? upstream? ahead count? dirty paths (classified
  owned/other per § 7);
- children: top-level dirs — git repos? `lore-repo.md` present? declared? origin URL;
- registered shortcuts on disk (`.claude/commands/lr-*-agent.md`,
  `.cursor/skills/lr-*-agent/SKILL.md`) and the agent dirs they point to.

**Step 2 — Determine the work.** Uninitialized (no descriptor, no managed memory content) → full
interview. Initialized → convergence: compute the delta between observed state and canonical
state; interview only the genuinely open questions.

Interview items (asked only when unknown or drifted):
1. **Repos.** Which top-level repos belong here — ranked suggestions: undeclared child git repos
   found on disk first (with their origin URLs), then any other candidates. Lore agent repos and
   ad-hoc repos (repos in no domain at all) go into the same flat `repos:` list; the distinction
   is auto-detected at pull time by `lore-repo.md` presence and is deliberately not recorded
   (avoids redundant schema).
2. **Framework repo.** Offer to include `lore-framework`'s clone URL in `repos:` (default yes) —
   this materializes the no-plugin fallback (D10).
3. **Git tracking.** If not a git repo: track it? (recommended default: yes; declining = supported
   local-only mode).
4. **Remote.** If no origin: provide one? (skippable; without it, push and team sharing stay
   inert and `status` will keep saying so).

**Step 3 — Confirmation gate.** One plan listing every file write and git action. `no` → stop,
zero writes.

**Step 4 — Write.**
- `lore-workspace.md` — frontmatter `description` + `repos:` only; body preserved.
- `.gitignore` — standard workspace-owned lines (`/.worktrees/`, `/.lr-beings/`, `/.tmp/`) plus
  `/<dirname>/` for **every child git repo on disk** (D9) and every declared repo. Append-only,
  idempotent by exact line.
- `README.md` — team-join card (clone → workspace-pull → workspace-init → boot), written when a
  remote exists; skipped otherwise.
- Memory files — both, v3 payload; marker migration per § 4.3; Agents section rendered from
  registered shortcuts (D6/D7).

**Step 5 — Run `workspace-pull`** (clones declared repos; its phase 3 re-asserts `.gitignore`).

**Step 6 — Remote synchronization (D11).** Only when git-tracked:
- **No remote** → skip; report that push/team-sharing are inert until one exists.
- **Remote empty** (fresh `ls-remote` shows no heads) → stage the framework-managed paths (§ 7),
  commit (`chore(lore): initialize lore workspace`), `push -u origin HEAD`.
- **Remote has history, local is fresh** (no local commits, or only this run's) → this is a
  **join**, not a founding: fast-forward to the remote, then re-run convergence (Steps 1–5)
  against what arrived, and only then commit/push any remaining delta.
- **Both have history** → stop with an explanation; suggest `workspace-pull` (phase 0) then
  `workspace-push`; never merge automatically.

**Step 7 — Summary.** What was written, what was synchronized, what remains (e.g.
"2 unregistered agents found — register with `register-agent` to list them in AGENTS.md").

### 5.2 `/lr:workspace-pull` (deltas only)

Semantics unchanged (phases 0–4 as shipped in v25). Two deltas:

1. **Phase 3 ignores all child git repos on disk** (D9), not only declared ones.
2. **Undeclared-repo nudge:** after phase 4, one line naming top-level git repos not declared in
   any descriptor, suggesting `workspace-init` (which will offer to declare them). This is the
   backlog item "Undeclared-top-level-repo nudge" — it ships here.

### 5.3 `/lr:workspace-push` (new)

As drafted in `docs/workspace-push.md` this session (uncommitted), aligned with this design:

- **Preconditions:** git-tracked workspace, own git root (realpath rule), on a branch.
- **Scope:** the framework-managed paths of § 7 — nothing else, ever (D3).
- **Plan + one confirmation:** paths to commit (with diffstat; memory-file diffs note when they
  extend beyond the framework sections), dirty non-owned paths listed as untouched, unpushed
  earlier commits that will ride along.
- **Execute:** explicit-path deletion-aware staging (`git add -A -- <paths>`; never bare `-A`,
  never `.`), commit `chore(lore): publish workspace state`, verify the commit contains only
  owned paths, push (`push`, or `push -u origin HEAD` when no upstream; commit-only with a report
  when no remote).
- **Failure:** non-fast-forward → report, suggest `workspace-pull` then retry; never force. Auth/
  network → commit is local, report verbatim.
- **Nothing to do:** "workspace already published", plus informational list of non-owned dirty
  paths.

### 5.4 `/lr:workspace-status` (new)

Read-only — runs no write and no network beyond `git ls-remote`-class queries (even those only
when cheap; ahead/behind uses the local upstream ref). Output: finding list, each with severity
and a concrete fix; ends with "workspace clean" when empty.

Findings catalog (initial):

| # | Finding | Severity | Suggested fix |
|---|---|---|---|
| S1 | Framework-managed workspace files dirty (§ 7 set) | warn | `workspace-push` |
| S2 | Workspace commits ahead of upstream | warn | `workspace-push` |
| S3 | Git-tracked workspace, no origin remote | info | `git remote add origin <url>` or `workspace-init` |
| S4 | Workspace not git-tracked (descriptors present) | info | `workspace-init` (offers tracking) |
| S5 | Undeclared top-level git repos on disk | info | `workspace-init` (offers to declare) |
| S6 | Declared repos missing on disk | warn | `workspace-pull` |
| S7 | Child repo not covered by `.gitignore` | warn | `workspace-pull` (phase 3) |
| S8 | Top-level repo not on its default branch | warn | worktree convention (`docs/worktrees.md`) |
| S9 | Worktrees under `.worktrees/` inventory (stale/orphaned noted) | info | prune manually |
| S10 | Memory files drifted from each other, or framework sections missing/duplicated/marker-format | warn | `workspace-init` |
| S11 | Agents on disk without registered shortcut | info | `register-agent` |
| S12 | Dirty non-owned workspace-root files | info | user's own — listed for visibility only |
| S13 | Conflict-state repos (origin mismatch vs declaration, etc. — as `workspace-pull` classifies) | warn | resolve per `workspace-pull` report |

**Architecture (D4):** the findings are computed by one deterministic scanner and rendered by the
skill; `/lr:check`'s workspace checks (#22–#24) consume the same scanner instead of restating the
rules in prose. Scanner home: Open Question OQ3.

## 6. Integrations

- **`register-agent` / `unregister-agent` / `register-repo`:** in the same operation as the
  shortcut write/removal, insert/update/remove the agent's entry in the Agents section of **both**
  memory files (D6). This is the only writer of that section besides init's re-render.
- **`/lr:check`:** #22 extends to the all-child-git-repos rule (D9); #23 generalizes to "legacy
  memory-file formats" (old `lr:init` markers *and* `lr:workspace-init` markers, once v3 ships);
  #24 (workspace publication state — drafted this session) becomes a thin consumer of the status
  scanner. No renumbering.
- **`/lr:update`:** keeps its deliberate exclusion — the workspace repo is not an automatic
  publication target. Migrations that regenerate workspace-root shortcuts leave the dirt for
  `workspace-push`; `status` S1 makes it visible. (Rationale: update's auto-commit gates are
  per-repo and conservative; the workspace repo needs the user-confirmed path.)
- **`finalize`:** unchanged — agent repos only. Optionally (not in this ship): a one-line
  post-phase-4 hint when the status scanner reports S1/S2.
- **`create-agent` / `create-repo`:** unchanged writers (they don't touch memory files); their
  summaries gain a pointer: "register the agent (`register-agent`) to add it to AGENTS.md."
- **README / QUICKSTART / INSTALL funnel:** the join path and founder path get updated for the
  four-command surface; the join path stays `clone → workspace-pull → workspace-init → boot`
  (init's join seam now makes running init after clone safe and useful).

## 7. Workspace-owned paths (canonical set)

The single source of truth for "what the framework manages at the workspace root" — referenced by
push (staging scope), status (S1), check, and init (dirty classification). Defined once in
`docs/workspace-push.md`; every other doc points here.

| Path | Written by |
|---|---|
| `lore-workspace.md` | init |
| `AGENTS.md`, `CLAUDE.md` | init; register-agent family (Agents section) |
| `.gitignore` | init; workspace-pull phase 3 |
| `README.md` | init |
| `.claude/commands/lr-*-agent.md` | register-agent family; update migrations |
| `.cursor/skills/lr-*-agent/SKILL.md` | register-agent family; update migrations |

Codex per-agent shortcuts live in `~/.codex/skills/` — outside the workspace repo; no publication
path applies (recorded, not a gap to fix).

Memory files are only partially framework-managed (three sections), but git commits whole files —
push's plan therefore highlights when a memory-file diff extends beyond the framework sections
(the user confirms their own edits ride along).

## 8. Compatibility and migration

- **`lore-workspace.md` schema:** unchanged.
- **Memory files:** marker-based workspaces migrate via init's offered conversion (§ 4.3). No
  numbered migration file — the workspace layer carries no version stamp; init-detects-and-offers
  is the established pattern (v25 did the same for `lr:init` → `lr:workspace-init` markers).
- **Flags:** `--refresh` / `--reconfigure` retired. If invoked, print a one-liner that plain
  `workspace-init` now converges, and proceed.
- **Ship classification:** release-notes-only at the domain level (no agent-repo migration);
  **cache-affecting** (touches `skills/`) → Clear Plugin Cache footer per `conventions.md`; all
  four version-bearing manifests bump to `1.<N>.0`; `versioning-release-types.md` gains the entry
  at ship, per the standing disciplines.

## 9. Open questions

- **OQ1 — CLAUDE.md mechanism.** Baseline: identical copies written together, drift flagged
  (S10). Candidate: `CLAUDE.md` = `@AGENTS.md` import (single source of truth). Adopt only after
  verifying on Claude Code that the import loads reliably at session start in real workspaces
  (and deciding what Cursor/Codex do with a stray one-line CLAUDE.md). Empirical check, not
  assumption.
- **OQ2 — Exact heading names and intro wording** (§ 4.1 is the proposal; bikeshed at
  implementation review).
- **OQ3 — Scanner home.** Options: (a) `lr-core workspace-status` subcommand — consistent with
  the accelerator/literate direction, python3 stdlib; (b) a standalone `scripts/workspace-status`
  bash script — consistent with `scripts/workspace-pull`. Recommendation: (a); the findings
  logic is exactly the kind of mechanical procedure that should not be executed as prose
  (standing-list item A1's lesson), and lr-core already owns preflight-style JSON reporting.
- **OQ4 — Init's join seam, "local is fresh" definition.** Proposal: zero local commits, or only
  commit(s) created by this init run. Sharpen at implementation.
- **OQ5 — Should `status` ever go to the network** (e.g. `ls-remote` to detect remote-empty vs
  behind)? Proposal: no network by default; a `--remote` flag if the need appears.
- **OQ6 — Framework repo in `repos:` by default** (D10 says offer, default yes). Confirm the
  default with real adopter feedback; a team with marketplace installs may prefer to decline.

## 10. Implementation plan

Phased so each slice is independently shippable and gateable:

1. **Push + owned-paths canonicalization.** `docs/workspace-push.md` (drafted; align to § 7),
   `skills/workspace-push/SKILL.md` (drafted), cursor wrapper sync, README row, cross-refs in
   workspace-pull/init docs.
2. **Status + scanner.** Scanner (per OQ3 decision), `docs/workspace-status.md`,
   `skills/workspace-status/SKILL.md`, wrappers; rewire check #22–24 onto the scanner.
3. **Memory-file v3 + init convergence.** Rewrite `docs/workspace-init.md` (§ 5.1), payload v3,
   marker migration, remote-sync seam; `workspace-pull` deltas (D9 + nudge).
4. **Register-agent integration.** Agents-section maintenance in the register/unregister/
   register-repo docs; both-files writing.

Gates per the standing disciplines: TriLens loop to convergence on the touched procedure docs;
lifecycle scenarios — the existing workspace-init scenario updated for convergence + v3 payload,
new scenarios for push (publish → phase-0 visibility on a second checkout) and status (findings
against a seeded messy fixture workspace); full suite at cheapest tiers per engine before push.
Dogfood: this workspace is the first real run — init convergence (marker migration + AGENTS.md
regeneration), remote decision (Open: user to provide origin URL or declare local-only), push of
the currently-dirty state, and removal of the stray `scripts/lr_core/` after confirming it is a
copy (Appendix A).

## Appendix A — Evidence from the live workspace (2026-08-09)

`/Users/yaroslav/Documents/agent-workspace`, workspace repo state at review time:

- `git status`: `AGENTS.md` modified (framework-written managed-section refresh: chronicler repo,
  new agents, updated commands — never committed); `.claude/commands/lr-lore-architect-agent.md`
  modified (regenerated shortcut — never committed); `scripts/lr_core/` untracked (stray copy of
  the framework's lr_core package; origin unknown; verify then remove).
- `git remote -v`: empty — no origin. Last commit `79510c2` (manual). The README join card exists
  on disk but references nothing clonable.
- Interpretation: every gap this design closes, exhibited simultaneously — framework writes
  outpacing manual commits (no push path), invisible decay (no status), inert sharing (no
  remote), and hygiene debris with no owner.

## Appendix B — Already-drafted artifacts (this session, uncommitted in `lore-framework/`)

| Artifact | Disposition under this design |
|---|---|
| `docs/workspace-push.md` | Stands; § 7 table already matches; keep as phase-1 basis. |
| `skills/workspace-push/SKILL.md` | Stands. |
| `docs/check.md` #24 | Rework in phase 2 to consume the status scanner; interim prose version acceptable for phase 1. |
