# Workspace Lifecycle Redesign — Implementation-Ready Design

**Status:** designed 2026-08-09 in dialogue with the user; reviewed and revised 2026-08-09 against
the shipped implementation. All six open questions are resolved — five by decision, OQ1 by
experiment (Appendix B). **Implemented 2026-08-09/10 as v37** — phases 1–4 all landed in one
release (phase 4 was small enough to include rather than defer). Committed locally; **not pushed and
not tagged** at the user's instruction.

**Gate record.** `/lr:trilens-loop` round 1 ran to completion over three independent lenses
(executability, contract integrity, blast radius) against the implementation: 11 findings, all 11
applied, none declined. Round 2 was launched and **did not run** — all three reviewers died on an
account spend limit before reporting, and per the loop's own stopping rule a silent round is not
banked as clean. So the artifact carries one clean review round, not two. Still ungated:
the deterministic suite and the full lifecycle suite (the user deferred both). Two of round 1's
findings were real code defects, not doc wording — see § Implementation record.
**Scope:** the workspace layer's command surface, the workspace memory-file contract, and the
publication path for workspace-level state.
**Supersedes:** parts of `docs/workspace-init.md` (modes/flags, marker protocol, payload v2);
extends `docs/workspace-pull.md`; absorbs the drafted `docs/workspace-push.md` and check #24
(see Appendix C).

---

## 1. Problem

The workspace layer shipped in v25 with a complete **consumer** half and no **producer** half:

- `workspace-pull` phase 0 pulls the workspace repo so teammates' descriptor changes arrive — but
  nothing ever pushes them. `workspace-init` explicitly never commits ("prints the commit
  checklist"), `workspace-pull` phase 3 edits `.gitignore` without committing, `finalize` phase 4
  is scoped to agent repos (`git add agents/`), and `update.md` explicitly excludes the enclosing
  workspace repo as a publication target (`docs/update.md:169`) while its migrations regenerate
  workspace-root shortcuts (`docs/update.md:176`).
- Consequence, observed live on the dogfood workspace (2026-08-09): `AGENTS.md` and a registered
  shortcut dirty from framework-generated refreshes that were never committed; a divergent
  untracked `scripts/lr_core/` variant; **no origin remote at all** — so the entire team-sharing
  story of the workspace layer has never run end-to-end. See Appendix A.
- **The memory file has been inert on Claude Code the whole time.** Confirmed by experiment
  (Appendix B): Claude Code 2.1.226 does not read `AGENTS.md`. The dogfood workspace carries
  `AGENTS.md` and no `CLAUDE.md`, so every Claude Code session here since v25 has started with
  **zero workspace memory** — which is also why nobody noticed the payload going stale. The
  engine-forked memory file is not a cosmetic problem; it is a silent whole-engine outage.
- Secondary frictions: the `<!-- lr:workspace-init:* -->` HTML-comment markers make the memory
  file read as generated goo; the `--refresh` / `--reconfigure` flag taxonomy pushes mode
  bookkeeping onto the user; and there is no quick way to see the workspace's operational state.

## 2. Concepts (unchanged)

- **Domain** — the scope of one lore agent repo (`lore-repo.md`; `agents/<name>/` with role,
  lore, workdir, sessions). The portable, team-shared unit; travels between workspaces via git.
- **Workspace** — the directory the engine runs from; contains one or more domains plus the other
  repos they declare, side by side. Optionally itself a small git repo (the **meta-repo**) that
  versions the assembly recipe — descriptor, memory files, `.gitignore`, `README.md`, registered
  shortcuts — and never child-repo contents (each child has its own history and is gitignored).
- **`lore-workspace.md`** — frontmatter `description` + block-form `repos:` (clone URLs of the
  top-level repos, including the agent repos); body is user prose. This design adds exactly one
  **optional** key, `sharing: local` (§ 5.1 interview item 4) — written only when a user declines
  a remote, absent otherwise, never required, no migration. That is the whole schema delta.

## 3. Design summary

Four commands with the `workspace` prefix — two existing, two new, zero renames:

| Command | Status | One-line semantics |
|---|---|---|
| `/lr:workspace-init` | rework | Initialize an uninitialized workspace; on an initialized one, **converge** it to current disk reality (absorbs `--refresh`/`--reconfigure`). |
| `/lr:workspace-pull` | small deltas | Pull the workspace repo (if git-tracked), clone declared-but-missing repos (both levels), maintain `.gitignore`, pull every top-level repo. |
| `/lr:workspace-push` | **new** | Commit framework-managed workspace files and push the workspace repo. Never touches child repos or user files. |
| `/lr:workspace-status` | **new** | Read-only diagnosis: branches, worktrees, dirty/unpushed workspace state, declaration drift — each finding with a suggested fix. |

Underneath all four sits **one deterministic scanner** (§ 6). Init observes with it, status renders
it, check consumes it, push takes its framework-managed-path set from it.

### Decisions

Settled in the 2026-08-09 design dialogue (D1–D12) and the review pass that followed (D13–D19).
Revised entries are marked.

- **D1 — Four-command surface.** `init` / `pull` / `push` / `status`. "Add a repo" and "add an
  agent" need no fifth command: create or clone the thing, run `init` (it notices and offers), or
  use the existing `create-*` / `register-*` skills.
- **D2 — Init converges.** One entry point, no user-facing mode flags. Uninitialized → full
  interview. Initialized → convergence pass: re-scan disk, offer undeclared repos, refresh
  managed sections, re-assert `.gitignore`, raise git/remote questions only when something is off.
  The confirmation gate (D12) is what makes "refreshes completely" safe. A workspace already at
  canonical state exits with `already current` and writes nothing.
- **D3 — Push publishes framework-managed paths only.** Other dirty workspace-root files are
  listed in the plan and left untouched. Committing arbitrary user files automatically is how
  unrelated work ships under a generic message. (User-confirmed decision.)
- **D4 — One scanner, four consumers.** *(revised — was "status and check share one scanner")*
  The findings logic is written once, deterministically (§ 6), and consumed by
  `/lr:workspace-status` (render all), `/lr:check` #22–#24 (render the subset it owns),
  `/lr:workspace-init` Step 1 (observation input, D13), and `/lr:workspace-push` (the
  framework-managed path set, D15). No prose duplication of the rules anywhere.
- **D5 — Named sections replace HTML-comment markers** in the memory file. The exact headings
  become the ownership contract; the file reads as a real document. Each managed heading carries a
  single provenance comment beneath it (D18). Marker-based workspaces are migrated by `init`
  (one-time, offered, not forced).
- **D6 — One writer per section.** *(revised — adds `unregister-repo`)* Lore Framework intro ←
  `init`. Repositories ← `init`. Agents ← `register-agent` / `unregister-agent` /
  `register-repo` / `unregister-repo`. `init`'s convergence re-renders the Agents section **from
  the registered shortcuts on disk** — registration remains the single membership authority; init
  is only the renderer.
- **D7 — The Agents section lists *registered* agents** (the "what can I boot here" answer).
  Agents on disk but unregistered do not appear; `status` nudges about them (S11).
- **D8 — `AGENTS.md` is canonical; `CLAUDE.md` is a one-line import stub.** *(revised — OQ1
  resolved by experiment, Appendix B.)* Claude Code does not read `AGENTS.md`; it does honor an
  `@AGENTS.md` import inside `CLAUDE.md`, composed with any user content in that file, and it
  ignores a missing import target rather than erroring. So the framework writes the full payload
  to `AGENTS.md` only and ensures `CLAUDE.md` contains the import line (§ 4.3). One source of
  truth, no copy-drift possible, no double-load. Consequence: command notation inside the shared
  content must be engine-neutral (§ 4.1).
- **D9 — `.gitignore` covers *all* child git repos on disk**, declared or not. Declaration
  governs cloning/pulling only; ignoring governs safety. (Today only declared repos are ignored —
  and the live workspace already needed a hand-added `/lore-chronicler/` line, commit `d05ba90`,
  which is exactly this gap.)
- **D10 — The memory file carries a Lore Framework section**: what this workspace is, links to
  the framework repo, the command set, core conventions, and the **no-plugin fallback**: an
  engine without the `lr` plugin is advised to clone `lore-framework` into the workspace and use
  its `docs/` as the instruction source. `init` offers to include the framework repo in the
  workspace `repos:` list so `workspace-pull` materializes that fallback automatically (default
  yes; declinable in one keystroke for teams on marketplace installs).
- **D11 — Init synchronizes with the remote, discriminating on shared history.** *(revised — was
  "local is fresh"; OQ4 resolved.)* The founding-vs-joining question is answered by
  `git merge-base`, not by counting local commits — any autonomous writer in the workspace (this
  machine has one: Appendix A) defeats a commit-count test. Full decision table in § 5.1 Step 6.
- **D12 — The confirmation gate and diff-before-replace survive.** No file writes before the user
  approves the plan; managed-section rewrites show a scoped diff first.
- **D13 — Init observes through the scanner.** *(new)* `workspace-init` Step 1 runs
  `lr-core workspace-scan` and interviews from its output. Convergence is then defined precisely —
  *converge = drive the scanner's findings to zero* — instead of a prose checklist that drifts
  from the S-list.
- **D14 — Terminology split: "standard ignore lines" vs "framework-managed paths".** *(new)* The
  shipped docs use *workspace-owned* for both the three `.gitignore` entries (`check.md:243`) and
  the publishable path set (`check.md:280`), eleven lines apart in the same file. The publishable
  set is renamed **framework-managed paths** throughout; the `.gitignore` entries keep **standard
  ignore lines**. `workspace-owned` is retired as a term.
- **D15 — The scanner owns the framework-managed path set as data.** *(new)* The set is defined
  once, in code (§ 7), and emitted in the scanner's output. Docs render it; no doc restates it.
  This closes the restatement already present at `check.md:281`.
- **D16 — Phases 1–3 ship in one release.** *(new)* Phase 1's `workspace-push.md` necessarily
  references `--reconfigure` and the marker format, both of which phase 3 retires. Shipping them
  separately puts a dead flag reference in a live doc for a whole version. Phase 4 may follow
  later. Interim-safe wording is applied to the drafted artifacts now regardless (Appendix C).
- **D17 — The push plan shows the riding-along commits, not a count.** *(new)* Unpushed non-managed
  commits are the norm on a workspace with an autonomous writer, not an edge case. The plan prints
  `git log --oneline @{u}..HEAD` so the user is confirming specific work, not a number.
- **D18 — Managed headings carry a provenance comment.** *(new)* Directly beneath each framework
  heading: `<!-- lr:managed — regenerated by workspace-init; edits here are overwritten -->`. A
  single comment, not a delimiter pair — it restores the "don't write here" signal that markers
  gave for free, at the point of use, without bringing back pair-matching or malformed-pair
  handling.
- **D19 — Codex per-agent shortcuts are materialized at join, not published.** *(new)* Codex
  shortcuts live in `~/.codex/skills/`, outside the repo, so they can never be published. The join
  path instead *regenerates* them locally: `status` finding S15 fires on Codex when agent repos are
  present with no matching Codex skills, and `init`'s convergence offers to run `register-repo` for
  each declared agent repo. Making the join path work is this release's purpose; recording the gap
  and moving on would leave Codex teammates with no bootable agents.

## 4. The memory-file contract

### 4.1 Canonical payload (v3 — sections, not markers)

`AGENTS.md` carries, in this order, before any user content:

~~~markdown
# <workspace description>

## Lore Framework

<!-- lr:managed — regenerated by workspace-init; edits here are overwritten -->

This directory is a [Lore Framework](https://github.com/zroslaw/lore-framework) workspace — named
agents with persistent, git-shared knowledge, usable from Claude Code, Codex, or Cursor.

Invoke skills as `/lr:<skill>` on Claude Code, `/lr-<skill>` on Cursor and Codex.

| Skill | What it does |
|---|---|
| `boot <agent>` | Load a lore agent (see Agents below) |
| `workspace-status` | Diagnose this workspace; every finding names its fix |
| `workspace-pull` | Pull the workspace repo, clone declared repos, pull every top-level repo |
| `workspace-push` | Commit and push the framework-managed workspace files |
| `workspace-init` | Initialize this workspace, or converge it after anything changed |

Conventions: top-level repos stay on their default branch (production state); non-default-branch
work goes in a git worktree under `.worktrees/<repo>/<slug>/`; local scratch under `.tmp/<name>/`.
Full convention: https://github.com/zroslaw/lore-framework/blob/main/docs/worktrees.md

No `lr` plugin in this engine? Clone the framework into the workspace —
`git clone https://github.com/zroslaw/lore-framework.git` — and use its `docs/` as the instruction
source, starting with `docs/agent-boot.md`.

## Repositories

<!-- lr:managed — regenerated by workspace-init; edits here are overwritten -->

- `<dirname>` — <description from lore-repo.md / lore-workspace.md, or "(no description)">

## Agents

<!-- lr:managed — regenerated by workspace-init and the register-agent family -->

- `<agent-name>` (`<repo-dirname>`) — <role description>. Boot: `lr-<agent-name>-agent`.
~~~

Notes:

- **Skill order follows the daily path** (boot first, diagnostics next, setup last), not the
  lifecycle order of the design.
- **Engine-neutral notation.** The same file is read by three engines, so skill references use the
  neutral form with the one-line legend above the table — never a single engine's slash syntax.
- The `# <workspace description>` title is framework-written at creation but afterwards treated
  as user-owned (renaming the workspace title must not fight the tool).
- The Repositories section lists **declared** repos — the union of `lore-workspace.md` `repos:`
  and every domain `repos:`. Undeclared git repos present on disk are deliberately *not* listed;
  they are a `status` finding (S5), not a workspace fact.
- The Agents section lists **registered** agents (D7). An empty scan renders the single line
  `_(No agents registered yet — run `register-agent` to add one.)_`.

### 4.2 Section ownership and parsing rules

- **Managed region.** A managed section runs from its exact level-2 heading line to the line
  before the next `^## ` heading, or EOF. The framework regenerates that region and touches
  nothing else in the file.
- **Heading match.** Exact, case-sensitive, level-2: `## Lore Framework`, `## Repositories`,
  `## Agents`. First occurrence wins; later duplicates are left alone and reported (S10).
- **User renames or deletes a framework heading:** the writer recreates the canonical section at
  its canonical position; the orphaned user-renamed section is left in place; `status` flags the
  duplication.
- **User edits inside a framework section:** overwritten at the next regeneration. Three things
  make that fair rather than surprising — the provenance comment (D18) marks the region at the
  point of use, D12 shows a scoped diff before replacing, and the region is bounded by ordinary
  markdown structure the user can see.
- **Section order:** framework sections first, in canonical order, then user sections. If user
  sections have been interleaved, regeneration edits section bodies in place and does not reorder
  the file; `status` notes non-canonical order as informational.
- **A file missing entirely** is created with the full payload.

### 4.3 The `CLAUDE.md` import stub

Claude Code reads `CLAUDE.md`, not `AGENTS.md` (Appendix B). The framework therefore ensures
`CLAUDE.md` contains one import line, and never writes the payload there:

~~~markdown
<!-- Lore Framework: this workspace's memory lives in AGENTS.md, shared across engines. -->

@AGENTS.md
~~~

Rules:

- **Idempotent by line.** If `CLAUDE.md` exists and already contains a line whose trimmed content
  is `@AGENTS.md`, do nothing. Otherwise append the two lines above, preserving all existing
  content. Verified: the import resolves when composed with unrelated user content (Appendix B,
  case `imp2`).
- **Never regenerate or truncate `CLAUDE.md`.** It is a user file that the framework adds one line
  to. Only that line is framework-managed.
- **Missing target is inert.** A `CLAUDE.md` with `@AGENTS.md` and no `AGENTS.md` on disk loads
  the rest of the file without error (case `imp3`) — so ordering between the two writes is not
  load-bearing.
- **Other engines are unaffected.** Cursor and Codex read `AGENTS.md`; a stray `CLAUDE.md` stub is
  inert there, and the comment line explains itself if a human opens it.
- **Version pin.** This mechanism is verified against Claude Code 2.1.226 (Appendix B). It is a
  behavior of the engine, not a contract, so it is re-verified by a lifecycle scenario
  (§ 10, `test_18b`) rather than assumed to hold.

### 4.4 Migration from markers

`init`'s convergence pass detects a `<!-- lr:workspace-init:start/end -->` (or legacy
`<!-- lr:init:* -->`) pair in either memory file and offers a one-time conversion:

1. Parse the managed block, discard it, re-render as v3 sections in `AGENTS.md`.
2. Preserve all content outside the markers verbatim, in place.
3. Drop the markers.
4. If the marker block was in `CLAUDE.md`, replace it with the import stub (§ 4.3) and write the
   payload to `AGENTS.md`.

Declining keeps the old format working for this release; `/lr:check` warns until migrated (today's
#23, generalized to "legacy memory-file format" — see § 8).

## 5. Command specifications

### 5.1 `/lr:workspace-init` (rework)

**Invocation:** no flags in the common path. `--dry-run` is retained as a debugging aid (plan only,
zero writes). `--refresh` / `--reconfigure` are retired; if supplied, print one line
("`workspace-init` now converges — the flag is no longer needed") and proceed normally.

**Step 0 — Context.** Resolve `<workspace>` (cwd), `<framework-root>`, engine (needed for D19 and
for report wording only; file content is engine-neutral per D8).

**Step 1 — Observe (D13).** Run:

```
python3 "<framework-root>/scripts/lr-core" workspace-scan --workspace "<workspace>"
```

Everything init needs to decide is in that output: descriptors, declared repo set, memory-file
format and section state, git/remote/branch/ahead-behind, children with their git and declaration
status, registered shortcuts, framework-managed path set with dirty classification, and the finding
list. Init performs no independent discovery. If the scanner cannot run, apply the Script Fallback
Contract (`docs/conventions.md`) — the scanner is a *literate* accelerator, so its own module
docstrings are the normative spec for a manual pass.

**Step 2 — Determine the work.** Uninitialized (no `lore-workspace.md` and no managed memory
content) → full interview. Initialized → convergence: the delta between observed state and
canonical state *is* the scanner's finding list; interview only the genuinely open questions.
**Zero findings and no format drift → report `already current` and stop, writing nothing.**

Interview items (asked only when unknown or drifted):

1. **Repos.** Which top-level repos belong here — ranked suggestions: undeclared child git repos
   found on disk first (with their origin URLs, from S5), then any other candidates. Lore agent
   repos and ad-hoc repos (repos in no domain at all) go into the same flat `repos:` list; the
   distinction is auto-detected at pull time by `lore-repo.md` presence and is deliberately not
   recorded (avoids redundant schema).
2. **Framework repo.** Offer to include `lore-framework`'s clone URL in `repos:` (default yes) —
   this materializes the no-plugin fallback (D10).
3. **Git tracking.** If not a git repo: track it? (recommended default: yes; declining = supported
   local-only mode).
4. **Remote.** If no origin: provide one? Skippable — but a skip is *recorded*, not just tolerated:
   write `sharing: local` into `lore-workspace.md`'s frontmatter (one optional key, no enforcement,
   no migration) so a deliberately local-only workspace can say so. Without that, S3 nags forever
   about a state the user already chose on purpose, and a finding the user cannot ever clear trains
   them to ignore the whole report. `sharing: local` suppresses S3; adding a remote later clears the
   key.
5. **Codex shortcuts (D19).** On Codex only, when S15 fires: offer to run `register-repo` for each
   declared agent repo.

**Step 3 — Confirmation gate.** One plan listing every file write and git action. `no` → stop,
zero writes.

**Step 4 — Write.**

- `lore-workspace.md` — frontmatter `description` + `repos:` only; body and any other frontmatter
  keys preserved.
- `.gitignore` — standard ignore lines (`/.worktrees/`, `/.lr-beings/`, `/.tmp/`) plus
  `/<dirname>/` for **every child git repo on disk** (D9) and every declared repo. Append-only,
  idempotent by exact line, never truncating.
- `README.md` — team-join card (clone → workspace-pull → workspace-init → boot), written when a
  remote exists; skipped otherwise.
- `AGENTS.md` — v3 payload (§ 4.1); marker migration per § 4.4; Agents section rendered from
  registered shortcuts (D6/D7).
- `CLAUDE.md` — import stub only, idempotent (§ 4.3).

**Step 5 — Run `workspace-pull`** (clones declared repos; its phase 3 re-asserts `.gitignore`).

**Step 6 — Remote synchronization (D11).** Only when git-tracked. Fetch first
(`git -C <workspace> fetch origin`), then decide from history relationships — never from a commit
count, since an autonomous writer in the workspace produces commits nobody typed:

| Observed | Meaning | Action |
|---|---|---|
| No `origin` remote | Local-only workspace | Skip; report that push and team-sharing are inert until a remote exists |
| `git ls-remote --heads origin` empty | Founding a new shared workspace | Stage the framework-managed paths (§ 7), commit `chore(lore): initialize lore workspace`, `push -u origin HEAD` |
| `merge-base --is-ancestor HEAD origin/<branch>` | Local is behind or equal | Fast-forward, re-run Steps 1–5 against what arrived, then commit/push any remaining delta |
| `merge-base --is-ancestor origin/<branch> HEAD` | Local is ahead | Commit the delta and push |
| Merge-base exists, neither is an ancestor | Diverged | Stop; suggest `workspace-pull` (phase 0) then `workspace-push`; never merge automatically |
| **No merge-base at all** | Unrelated histories — a *join* onto someone else's workspace | Stop and offer two explicit options: **(a) adopt the remote** — move local commits to `pre-join-<short-sha>`, hard-reset to `origin/<branch>`, then re-run Steps 1–5; **(b) this is a different workspace** — supply a different remote. Never `--allow-unrelated-histories` automatically |

**Step 7 — Summary.** What was written, what was synchronized, what remains — each remaining item
phrased as the scanner finding it corresponds to, so the wording matches what `status` will say
next time.

### 5.2 `/lr:workspace-pull` (deltas only)

Semantics unchanged (phases 0–4 as shipped in v25). Three deltas:

1. **Phase 3 ignores all child git repos on disk** (D9), not only declared ones.
2. **Undeclared-repo nudge:** after phase 4, one line naming top-level git repos not declared in
   any descriptor, suggesting `workspace-init` (which will offer to declare them). This is the
   backlog item "Undeclared-top-level-repo nudge" — it ships here.
3. **Phase 0 reports behind-ness explicitly** so a skipped-because-dirty pull cannot look like a
   successful one (feeds S14).

### 5.3 `/lr:workspace-push` (new)

As drafted in `docs/workspace-push.md`, with these alignments:

- **Preconditions:** git-tracked workspace, own git root (realpath rule — the macOS `/var` symlink
  trap, `docs/version-check.md` Step 1b), on a branch.
- **Scope:** the framework-managed paths of § 7, taken from the scanner's emitted set (D15) —
  nothing else, ever (D3).
- **Plan + one confirmation:** paths to commit with diffstat; memory-file diffs flagged when they
  extend beyond the managed sections; dirty non-managed paths listed as untouched; **and the
  actual `git log --oneline @{u}..HEAD` of commits that will ride along** (D17).
- **Execute:** explicit-path deletion-aware staging (`git add -A -- <paths>`; never bare `-A`,
  never `.`), commit `chore(lore): publish workspace state`, verify the commit contains only
  managed paths, push (`push`, or `push -u origin HEAD` when no upstream; commit-only with a
  report when no remote).
- **Failure:** non-fast-forward → report, suggest `workspace-pull` then retry; never force. Auth /
  network → the commit is already local; report the error verbatim.
- **Nothing to do:** "workspace already published", plus an informational list of non-managed dirty
  paths.

### 5.4 `/lr:workspace-status` (new)

Read-only. Runs `lr-core workspace-scan` and renders its findings; performs no write and **no
network** (§ 6.3). Output: finding list ordered by severity then ID, each with a concrete fix; ends
with `workspace clean` when empty.

Findings catalog:

| # | Finding | Severity | Suggested fix |
|---|---|---|---|
| S1 | Framework-managed workspace files dirty (§ 7 set) | warn | `workspace-push` |
| S2 | Workspace commits ahead of upstream | warn | `workspace-push` |
| S3 | Git-tracked workspace, no origin remote **and no `sharing: local`** in `lore-workspace.md` | info | `git remote add origin <url>`, or `workspace-init` (which offers to record local-only instead) |
| S4 | Workspace not git-tracked (descriptors present) | info | `workspace-init` (offers tracking) |
| S5 | Undeclared top-level git repos on disk | info | `workspace-init` (offers to declare) |
| S6 | Declared repos missing on disk | warn | `workspace-pull` |
| S7 | Child repo not covered by `.gitignore` | warn | `workspace-pull` (phase 3) |
| S8 | Top-level repo not on its default branch | warn | worktree convention (`docs/worktrees.md`) |
| S9 | Worktrees under `.worktrees/` inventory (stale/orphaned noted) | info | prune manually |
| S10 | Memory-file contract violation: `AGENTS.md` absent, `CLAUDE.md` import stub missing, managed heading missing or duplicated, or legacy marker format | warn | `workspace-init` |
| S11 | Agents on disk without a registered shortcut | info | `register-agent` |
| S12 | Dirty non-managed workspace-root files | info | user's own — listed for visibility only |
| S13 | Conflict-state repos (origin mismatch vs declaration, etc. — as `workspace-pull` classifies) | warn | resolve per `workspace-pull` report |
| S14 | Workspace behind its upstream (from local refs; may be stale) | info | `workspace-pull` |
| S15 | **Codex only** — declared agent repos present with no matching `~/.codex/skills/lr-*-agent/` | info | `register-repo <repo>` (D19) |

**Disambiguation line** (added verbatim to all three diagnostic docs, per the command-surface
curation concern): *"`workspace-status` diagnoses this workspace's git and descriptor state;
`/lr:check` verifies content consistency inside agent repos; `/lr:doctor` diagnoses engine and
plugin runtime problems."*

## 6. The scanner

### 6.1 Home and invocation (OQ3 → resolved: `lr-core` subcommand)

```
python3 "<framework-root>/scripts/lr-core" workspace-scan --workspace <path>
```

`lr-core` already owns preflight-style JSON reporting, is python3-stdlib-only, and is the
established home for mechanical procedures that must not be executed as prose. The name
`workspace-scan` avoids collision with the existing `scan` subcommand (agent lore manifest).
Implementation module: `scripts/lr_core/workspace_scan.py`, **literate** — its module and function
docstrings are the normative spec for a manual fallback pass, in the style of `preflight.py`.

### 6.2 Output contract

The standard envelope (`{"ok", "data", "warnings", "errors"}`), with:

```jsonc
{
  "data": {
    "workspace": "/abs/path",
    "applicable": true,              // false → not a workspace root; consumers skip
    "engine": "claude|codex|cursor|unknown",
    "git": {
      "tracked": true, "own_root": true, "branch": "main", "detached": false,
      "origin": "git@github.com:…", "upstream": "origin/main",
      "ahead": 0, "behind": 0        // null when no upstream
    },
    "descriptors": { "lore_workspace": true, "declared": [ {"url": "…", "dirname": "…", "source": "workspace|domain"} ] },
    "children": [ {"dirname": "…", "git": true, "lore_repo": true, "declared": true,
                   "origin": "…", "default_branch": "main", "current_branch": "main", "ignored": true} ],
    "memory": { "agents_md": {"present": true, "format": "v3|markers|legacy-markers|absent",
                              "sections": {"lore_framework": "present|missing|duplicated", "…": "…"}},
                "claude_md": {"present": true, "import_stub": true} },
    "shortcuts": { "claude": ["lore-architect"], "cursor": [], "codex": ["lore-architect"] },
    "managed_paths": { "set": ["lore-workspace.md", "…"], "dirty": ["AGENTS.md"], "other_dirty": ["scripts/"] },
    "findings": [ {"id": "S1", "severity": "warn", "data": {"paths": ["AGENTS.md"]}} ]
  }
}
```

**The script emits data; the doc owns the words.** A finding carries an `id`, a `severity`, and
structured `data` — never a finished user-facing sentence. `docs/workspace-status.md` holds the
message and fix wording for each ID (the § 5.4 table is that source). This is the seam that goes
wrong by default: a script string that reads like a finished message gets printed as one, and
printing it *looks* like handling the situation, so the executor never reaches the doc that owns
the remedy.

**Exit codes:** `0` = the scan ran (findings may be present); `2` = the scan could not run
(unreadable workspace, bad arguments). Findings never set a nonzero exit — they are results, not
failures.

### 6.3 No network, and what that costs

Every git query is local-refs-only:

- ahead/behind — `git rev-list --left-right --count @{u}...HEAD`
- default branch — `git symbolic-ref --short refs/remotes/origin/HEAD`; **if absent, S8 is not
  emitted** for that repo rather than guessing `main`
- origin URL — `git remote get-url origin`
- dirty paths — `git status --porcelain` (includes untracked)
- worktrees — `git worktree list --porcelain`

Consequence: `behind` reflects the last fetch, so S14 is `info` and its wording says so. `status`
never fetches (OQ5 → resolved: no network, no flag until a need appears). `init` Step 6 *does*
fetch, because it is about to make a publication decision — that is a different contract, and it
is the only place in this design that touches the network beyond `workspace-pull`'s own clones.

### 6.4 Deterministic classification rules

- **Framework-managed path match** — exact path or glob from the § 7 set, matched against
  `git status --porcelain` output including untracked entries. Untracked directories reported by
  git as `dir/` expand before matching.
- **Child git repo** — a top-level entry with a `.git` directory *or* file (worktree/submodule
  form). Symlinked entries are followed once and reported if they escape the workspace.
- **Declared dirname derivation** — identical to `workspace-pull`: last URL path segment, trailing
  `.git` stripped; unsafe names (traversal, leading `-`, `.gitignore` metacharacter) are skipped
  and reported as warnings.
- **`.gitignore` coverage** — exact-line match on `/<dirname>/`. No pattern interpretation; the
  writer only ever emits that exact form, so the reader only ever needs to find it.
- **Own git root** — `git rev-parse --show-toplevel` compared against
  `os.path.realpath(workspace)`. Never `pwd`: on macOS `/var` is a symlink to `/private/var` and
  the logical path disagrees with git's physical one.
- **Engine** — reuse `preflight.detect_engine`, never a second detector and never the executing
  model's belief about itself. `data.engine` exists solely to gate S15 and to pick the shortcut
  directories to inventory; an `unknown` verdict suppresses S15 rather than guessing.

## 7. Framework-managed paths (canonical set)

The single source of truth for "what the framework writes at the workspace root". Defined in code
(D15) at `scripts/lr_core/workspace_scan.py` and emitted as `data.managed_paths.set`; every doc
renders it from there rather than restating it.

| Path | Written by |
|---|---|
| `lore-workspace.md` | init |
| `AGENTS.md` | init; register-agent family (Agents section) |
| `CLAUDE.md` | init (import stub line only) |
| `.gitignore` | init; workspace-pull phase 3 |
| `README.md` | init |
| `.claude/commands/lr-*-agent.md` | register-agent family; update migrations |
| `.cursor/skills/lr-*-agent/SKILL.md` | register-agent family; update migrations |

Codex per-agent shortcuts live in `~/.codex/skills/` — outside the workspace repo, so no
publication path applies. They are **materialized at join instead** (D19, S15).

Memory files are only partially framework-managed — `AGENTS.md` down to three sections,
`CLAUDE.md` down to one line — but git commits whole files, so push's plan highlights when a
memory-file diff extends beyond the managed region (the user confirms their own edits ride along).

**Terminology (D14):** these are *framework-managed paths*. The three `.gitignore` entries
(`/.worktrees/`, `/.lr-beings/`, `/.tmp/`) are *standard ignore lines*. The overloaded term
*workspace-owned* is retired from all docs in this ship.

## 8. Integrations

- **`register-agent` / `unregister-agent` / `register-repo` / `unregister-repo`:** in the same
  operation as the shortcut write/removal, insert/update/remove the agent's entry in the Agents
  section of `AGENTS.md`, and ensure the `CLAUDE.md` import stub exists (D6). These four skills
  share one doc, `docs/register-repo.md` — there is no `docs/register-agent.md`; the section is
  added there once and applies to all four flows.
- **`/lr:check`:** #22 extends to the all-child-git-repos rule (D9); #23 generalizes from "legacy
  `lr:init` markers" to "legacy memory-file format" (either marker vocabulary, plus a
  payload-in-`CLAUDE.md` workspace); #24 becomes a thin consumer of the scanner. All three render
  scanner findings rather than restating rules. No renumbering. The check count in
  `skills/check/SKILL.md`'s description and in any doc that says "23 checks" is updated to 24 —
  a bounded mechanical sweep that ships here, not later.
- **`docs/conventions.md`:** the `lore-workspace.md` schema reference gains the optional
  `sharing: local` key. It is the canonical schema site, so it is the only place the key is
  specified; every other doc points here.
- **`/lr:update`:** keeps its deliberate exclusion — the workspace repo is not an automatic
  publication target (`docs/update.md:169`). Migrations that regenerate workspace-root shortcuts
  leave the dirt for `workspace-push`; S1 makes it visible. (Rationale: update's auto-commit gates
  are per-repo and conservative; the workspace repo needs the user-confirmed path.)
- **`finalize`:** unchanged — agent repos only. Optionally (not in this ship): a one-line
  post-phase-4 hint when the scanner reports S1/S2.
- **`create-agent` / `create-repo`:** unchanged writers (they don't touch memory files); their
  summaries gain a pointer: "register the agent (`register-agent`) to add it to `AGENTS.md`."
- **README / QUICKSTART / INSTALL funnel:** the join path and founder path get updated for the
  four-command surface; the join path stays `clone → workspace-pull → workspace-init → boot`
  (init's join seam now makes running init after clone safe and useful). Keep the fork question
  verbatim-identical across README, QUICKSTART, and all three INSTALL preambles.

## 9. Compatibility and migration

- **`lore-workspace.md` schema:** one new optional key, `sharing: local`. Absent means "not
  answered yet" and behaves exactly as today — no migration, no rewrite of existing descriptors,
  no failure on an older framework reading a newer descriptor (unknown frontmatter keys are already
  ignored by both parsers). Documented in `docs/conventions.md` § descriptor schema alongside
  `description` and `repos:`.
- **Memory files:** marker-based workspaces migrate via init's offered conversion (§ 4.4). A
  workspace whose payload sits in `CLAUDE.md` (every Claude-founded workspace to date) has it moved
  to `AGENTS.md` with the stub left behind. No numbered migration file — the workspace layer
  carries no version stamp; init-detects-and-offers is the established pattern (v25 did the same
  for `lr:init` → `lr:workspace-init` markers).
- **Flags:** `--refresh` / `--reconfigure` retired with a one-line notice and pass-through.
- **Ship classification:** release-notes-only at the domain level (no agent-repo migration);
  **cache-affecting** (touches `skills/`) → Clear Plugin Cache footer per `conventions.md`, hoisted
  near the top; all four version-bearing manifests bump to `1.<N>.0`;
  `versioning-release-types.md` gains its entry on the same finalization as the ship; the release
  is tagged `lr--v1.<N>.0` as part of the push step.

## 10. Implementation plan

**Phases 1–3 ship as one release (D16).** Phase 4 may follow separately.

**Phase 1 — Push and the managed-path set.**
- `scripts/lr_core/workspace_scan.py` — the managed-path set and dirty classification only (the
  rest lands in phase 2).
- `docs/workspace-push.md` (drafted) — align to § 7, adopt D14 terminology, add D17's commit log,
  remove the `--reconfigure` pointer and the marker-format description.
- `skills/workspace-push/SKILL.md` (drafted) — stands as written.
- `scripts/sync-cursor-skills` run; README skill row; cross-refs in `workspace-pull.md` /
  `workspace-init.md`.

**Phase 2 — Status and the full scanner.**
- Complete `workspace_scan.py`: S1–S15, § 6.2 envelope, § 6.4 classification rules.
- `docs/workspace-status.md` (owns all finding wording), `skills/workspace-status/SKILL.md`,
  cursor wrapper.
- Rewire `check.md` #22–#24 onto the scanner; add the three-way disambiguation line to
  `workspace-status.md`, `check.md`, and `doctor.md`.

**Phase 3 — Memory-file v3 and init convergence.**
- Rewrite `docs/workspace-init.md` to § 5.1: scanner-driven Step 1, convergence, v3 payload,
  marker migration, `CLAUDE.md` stub, D11 remote table, flag retirement.
- `workspace-pull` deltas (D9, undeclared-repo nudge, phase-0 behind-ness).
- Update the check count to 24 wherever it appears.

**Phase 4 — Register-agent integration.**
- Agents-section maintenance in `docs/register-repo.md`, covering all four register/unregister
  flows (D6), plus the `CLAUDE.md` stub guarantee.

### Test changes (name them now — they are the phase gates)

| Test | Change |
|---|---|
| `tests/lifecycle/test_repo_workspace.py::test_18_workspace_init` | Assert v3 headings and the provenance comment instead of `<!-- lr:workspace-init:start -->`; assert payload lands in `AGENTS.md` |
| `tests/lifecycle/test_repo_workspace.py::test_18b_claude_md_import` | **New.** On Claude Code: assert `CLAUDE.md` exists, contains exactly one `@AGENTS.md` line, and does not contain the payload. This is the standing re-verification of Appendix B |
| `tests/lifecycle/harness.py::memory_file_name()` | Replace with `memory_files()` returning the canonical file plus the stub; the current engine fork silently asserts against the wrong file under D8 |
| `test_repo_workspace.py::test_19_workspace_pull` | Extend: an undeclared child repo on disk gains a `.gitignore` line (D9) and triggers the nudge |
| **New** `test_26_workspace_push` | Seed a dirty managed path plus a dirty non-managed path; assert only the managed one is committed, and that a second checkout sees it after `workspace-pull` phase 0 |
| **New** `test_27_workspace_status` | Seed a messy fixture (undeclared repo, missing ignore line, dirty managed file, unregistered agent); assert the expected finding IDs appear and `workspace clean` does not |

### Gates

- `/lr:trilens-loop` to convergence on the touched procedure docs — `workspace-init.md`,
  `workspace-push.md`, `workspace-status.md`, `workspace-pull.md`, `check.md`,
  `register-repo.md`.
- Deterministic suite green.
- Full lifecycle suite at the cheapest practical tier per engine (Claude Code → haiku,
  Codex → gpt-5.4-mini, Cursor → composer-2.5), background, push only on green. The memory-file
  change makes this non-optional: it is precisely a model-execution-fidelity surface, and the
  engine-fork removal touches every engine's boot path.
- A gate result belongs to the artifact state it ran against. Record the commit each gate
  certified; any edit landed afterwards is ungated and either re-runs the gate or becomes a
  follow-up.

### Dogfood plan (this workspace, first real run)

1. `workspace-init` convergence: marker migration, payload moved `AGENTS.md` → v3 sections,
   `CLAUDE.md` stub created — which restores workspace memory on Claude Code here for the first
   time.
2. Declare `lore-chronicler` (currently on disk, undeclared, hand-ignored in `d05ba90`).
3. Remote decision: **resolved 2026-08-09 — local-only** (user's call). `init` records
   `sharing: local`; S3 is suppressed here. Consequence for the gates: the join/found seam
   (§ 5.1 Step 6) and push-to-remote **cannot be exercised on this workspace at all** — they are
   covered only by the lifecycle fixtures (`test_26_workspace_push`), which therefore stop being
   optional. Dogfooding here validates init convergence, the memory-file contract, status, and
   commit-without-push; nothing more.
4. `workspace-push` the currently-dirty state — commit-only, no push. The Chronicler's commits
   appear in the plan (D17) rather than being counted.
5. `scripts/lr_core/` — **resolved: abandoned intermediate, safe to delete.** Traced 2026-08-09:
   no file matches any blob in framework history; `scripts/lr-core` was a single file at v35
   (`7cfae9c`) and the `lr_core/` package first appears in the v36 release commit
   (`e5e097b`, 12:39). The workspace copy is dated 10:17 the same day — a snapshot taken *during*
   the package split, ~2h20m before it landed. It is strictly behind and internally broken:
   `find_repos` is defined twice, the v36 Lore-v1 constants are absent, `framework_root()` still
   walks two levels (correct for the old single-file path, wrong for its own), and there is no
   `lr-core` wrapper, so it has no entry point. Nothing unique to preserve.

## 11. Residual risks

Not open questions — decisions have been made. These are the places where the decision rests on
something outside the framework's control.

- **The `@AGENTS.md` import is engine behavior, not a contract.** Verified on Claude Code 2.1.226
  (Appendix B). If a future version changes it, every Claude Code workspace loses workspace memory
  silently — the same failure this design is fixing. Mitigation: `test_18b` re-verifies it on every
  lifecycle run, which is the only signal that would catch a silent regression.
- **Cursor/Codex reading `CLAUDE.md`.** Neither is known to; if one starts, it sees a two-line stub
  with a self-explaining comment. Low blast radius, no mitigation planned.
- **Section-heading collision with user content.** A user whose own `## Agents` heading predates
  the framework's gets their section adopted as managed on first convergence. D12's diff makes the
  loss visible before it happens, and S10 reports the duplicate afterwards, but there is no way to
  distinguish the two by structure alone.
- **D10's framework-repo-in-`repos:` default.** Default yes; a team on marketplace installs may
  reasonably decline. One keystroke either way; revisit with real adopter feedback rather than
  guessing now.
- **S15 depends on Codex register/unregister**, which remains an unvalidated implementation path in
  lore. If it is still unvalidated at implementation time, S15 ships as a diagnostic only and the
  init offer (D19) is held back rather than shipping an offer that leads somewhere broken.

## Appendix A — Evidence from the live workspace (2026-08-09)

`/Users/yaroslav/Documents/agent-workspace`, verified at review time:

- `git status`: `AGENTS.md` modified (framework-written managed-section refresh — never committed);
  `.claude/commands/lr-lore-architect-agent.md` modified (regenerated shortcut — never committed);
  `scripts/lr_core/` untracked.
- `git remote -v`: **empty — no origin.** The README join card exists on disk but references
  nothing clonable.
- `HEAD` is `257c8aa`, *"Record 2026-08-09 workspace chronicle"* — written by the **Chronicler**
  Being via the live launchd Keeper, adding `workdir/diary/2026-08-09.md` to the workspace repo.
  This is why D11 discriminates on shared history rather than commit count (§ 5.1 Step 6) and why
  D17 shows riding-along commits instead of counting them: **this workspace has a committer that
  is not a person.**
- `.gitignore` contains `/lore-chronicler/` — hand-added in `d05ba90` because the repo is on disk
  but undeclared. That is D9's motivating case, already paid for manually.
- `AGENTS.md` exists, `CLAUDE.md` does not — so per Appendix B, **every Claude Code session in
  this workspace has started with no workspace memory since v25.**
- `scripts/lr_core/` is an abandoned mid-refactor snapshot from the v36 package split (traced in
  § 10, dogfood item 5) — no entry point, a duplicated `find_repos`, a `framework_root()` that
  resolves to the wrong depth for its own location. Safe to delete; kept in evidence here only
  because the first review pass called it "a stray copy" without checking, and it is not one.

Interpretation: every gap this design closes, exhibited simultaneously — framework writes
outpacing manual commits (no push path), invisible decay (no status), inert sharing (no remote),
a silently dead memory file, and hygiene debris with no owner.

## Appendix B — Memory-file loading experiment (2026-08-09)

**Environment:** Claude Code 2.1.226, macOS (Darwin 25.5.0), model `haiku`, default settings, empty
temp workspaces, no `lr` plugin loaded. *(An environment-dependent measurement records the
environment it was taken in, or it generates false drift alarms later.)*

**Method:** each case is a bare directory containing only the memory file(s) under test, each
carrying a unique sentinel. One headless run per case:
`claude -p '<ask for sentinels visible in context>' --model haiku --disallowedTools Read Bash Glob Grep Edit Write WebFetch Task`.
Disabling file tools is what makes this evidence rather than self-report — the model cannot reach
a file it was not given, and case `a` returning `NONE` is the negative control that proves it.

| Case | `CLAUDE.md` | `AGENTS.md` | Result |
|---|---|---|---|
| `a` | absent | sentinel `ZEBRA-7741` | **`NONE`** — `AGENTS.md` is not read |
| `c` | sentinel `MANGO-3182` | absent | `MANGO-3182` — `CLAUDE.md` is read |
| `both` | sentinel `MANGO-3182` | sentinel `ZEBRA-7741` | `MANGO-3182` only — **no double-load** |
| `imp` | `@AGENTS.md` | sentinel `ZEBRA-7741` | `ZEBRA-7741` — the import resolves |
| `imp2` | user prose + sentinel + `@AGENTS.md` | sentinel `ZEBRA-7741` | **both** — the import composes with user content |
| `imp3` | user prose + sentinel + `@AGENTS.md` | absent | user sentinel only, no error — a missing target is inert |
| `canon` | the exact § 4.3 stub (comment + import) | sentinel `ZEBRA-7741` | `ZEBRA-7741` — the shipped stub works verbatim |

**Conclusions, feeding D8 and § 4.3:**

1. Claude Code does not read `AGENTS.md`. "One file named `AGENTS.md` everywhere" — the
   simplification this review initially suspected — is **wrong**.
2. Writing both files in full would not double-load, so it was safe; it was simply unnecessary, and
   it would have carried a permanent copy-drift surface (the original S10) for no benefit.
3. The `@AGENTS.md` import works, composes with user content, and fails inert. That makes
   `AGENTS.md`-canonical-plus-stub strictly better than dual copies: one source of truth, drift
   structurally impossible, and the only framework-managed content in `CLAUDE.md` is a single line.

## Appendix C — Already-drafted artifacts (uncommitted in `lore-framework/`)

| Artifact | Disposition |
|---|---|
| `docs/workspace-push.md` | Phase-1 basis. Required edits: drop the `--reconfigure` pointer (Step 1.1) and the marker-format description (§ Workspace-owned paths) — both are retired by phase 3; rename to *framework-managed paths* (D14); add D17's commit log to the Step 3 plan. **Applied 2026-08-09.** |
| `skills/workspace-push/SKILL.md` | Stands as written. |
| `docs/check.md` #24 | Interim prose version is fine for phase 1; phase 2 rewires it onto the scanner. Required edit now: stop restating the managed-path set inline (D15) — point at the canonical definition. **Applied 2026-08-09.** |

## Implementation record (2026-08-09/10, v37)

Phases 1–4 shipped together. Deltas from the design as written, all discovered by the TriLens round:

- **Phase 4 was included, not deferred.** D16 allowed it to follow later; it turned out to be one
  section in `docs/register-repo.md`, and leaving it out would have shipped an Agents section that
  only `workspace-init` maintained.
- **Two real code defects, caught by review, not by the design.** Both were in
  `scripts/lr_core/workspace_scan.py` / `scripts/workspace-pull`, and neither is visible in prose:
  1. **D9's ignore-everything rule bypassed the unsafe-name filter.** `workspace-pull` has always
     refused to write a `.gitignore` line for a *URL-derived* name containing `!`, `*`, `?`, or `[`.
     Extending phase 3 to filesystem-derived names reintroduced exactly the hole the filter exists to
     close — a local directory named `!notes` is trivially creatable and turns its ignore line into a
     negation. Fixed in both writer and scanner; an unsafe child is now S13 (rename it), not S7
     (run workspace-pull, which cannot help).
  2. **S15 was computed workspace-wide instead of per-repo.** One Codex shortcut anywhere silenced
     the finding for every repo. Since `~/.codex/skills/` is user-global and agent names collide
     across repos by design, a shortcut from an unrelated workspace could silence it too. Now
     per-repo, with the residual name-collision limit stated in the S15 row rather than hidden.
- **The join path destroyed uncommitted work.** § 5.1 Step 6's adopt-remote option said
  `reset --hard origin/<branch>` — but Step 4 has already written the memory file and descriptor by
  then, and a workspace worth joining has its own versions of those files. The rescue point is now
  a full `add -A` commit onto `pre-join-<short-sha>` *before* any branch switch, and the offer says
  out loud what adopting replaces.
- **Managed-region boundaries now ignore fenced code blocks.** The canonical payload is itself a
  fenced example containing literal `## Lore Framework` lines; a user pasting one into their
  `AGENTS.md` would have had it read as a real heading, which decides where a managed region *ends*
  and therefore how much of their file a regeneration overwrites. Applied in both the prose rule and
  `workspace_scan.outside_fences`.
- **The Agents render had no description source.** "Render from the shortcuts on disk" is
  under-specified: the Claude Code shortcut is a single bootstrap line carrying no description. The
  shortcut now supplies membership and the absolute `<agent-dir>`; `role.md` at that dir supplies the
  description. Uniform across all three engines.
- **`workspace-push` left a bad commit on the branch.** The post-commit verification said "do not
  push" but never undid the commit, so the next push would have carried it. Now `reset --soft HEAD^`.

Not done, deliberately: no `migrations/37.md` (no agent-repo content changes — `/lr:update` bumps the
stamp only); no release tag and no push; the dogfood plan (§ 10) has not been run on this workspace,
so its own S1/S3/S5/S10 findings are still open.
