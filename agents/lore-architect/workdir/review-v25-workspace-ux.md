# Review — v25 Workspace UX & Team Adoption
Session: 2026-07-12.
Reviewer: Lore Architect (operational UX lens).
Documents: `draft-v25-workspace-pull.md`, `draft-v25-workspace-init.md`.

---

## 1. Verdict

**Approve with changes.**

The two-level pull architecture is sound. The init/pull separation (producer/consumer) is the right mental model. The two-draft pairing covers the ground. However, there are five blocker-class issues — one a correctness bug — plus a cluster of friction points that will hurt first-time adoption if left unaddressed. None require a redesign; all are fixable before ship.

---

## 2. User Journeys

### 2a. Solo Developer — Empty Directory → workspace-init

**Prerequisite gap (not modelled).** Step 0 resolves `<framework-root>` and the agent runs the skill — but the skill was loaded from *somewhere*. In a brand-new empty directory there is no `AGENTS.md`, no loaded framework, no skill context. How did the user get to `/lr:workspace-init`? The draft assumes "user has framework context" as a precondition without documenting it. First-time users hit this before step 1.

**Interview flow** (Steps 1–3) is well-structured. Ranked shortlist for repos in step 2 is the right UX call. The "reminder" note about lore agent repos needing to be in the workspace list is important — but buried in the spec; it must appear *in the wizard copy itself*, not only in docs.

**No confirmation gate before writes.** Steps 1–3 collect information; step 4 writes `lore-workspace.md` with no final "Here's what I'll do — proceed?" gate. A user who mistyped a URL in step 2 has no checkpoint before destructive write.

**Overall**: Flow works if the precondition is satisfied. Needs a confirmation gate and clear precondition documentation.

---

### 2b. Team Join — Clone → workspace-pull → workspace-init Refresh

The draft documents this path (init draft §"Team join path") and the sequence is correct:

```bash
git clone git@github.com:team/agent-workspace.git
cd agent-workspace
/lr-workspace-pull
/lr-workspace-init        # refresh mode (lore-workspace.md already present)
/lr-boot lore-architect
```

**This works well.** `lore-workspace.md` presence drives refresh mode cleanly. The AGENTS.md is already tracked in the workspace repo so the teammate gets boot context immediately on clone.

**One gap:** the team join path above assumes the workspace repo's `AGENTS.md` already has the managed section (it does, since it's committed). But after `workspace-pull` runs and clones new children, the managed section's `### Agents` list is stale until `workspace-init --refresh` regenerates it. The refresh is step 2 in the join sequence — correct. But the README (open item) is what a new teammate reads *before* knowing to run those commands. Without a README in the workspace repo, this sequence is undiscoverable.

---

### 2c. Optional vs Required Workspace Git

**The branching is present but undersells the tradeoff.** Step 3 asks "Should this workspace directory be a git repository?" with a binary Yes/No. What the user loses on "No" is not stated at the prompt:
- No phase 0 (no automatic descriptor pull from teammates' changes)
- No gitignore automation (child repo clutter in workspace dir)
- No team sharing via workspace repo remote

The "No" path is legitimate (local-only dev), but the user needs to understand they're opting out of the team-coordination layer. The wizard copy should state the tradeoff, not just offer the gate.

**Local-only workspace with multiple contributors** is an underspecified scenario: if two developers both run workspace-init locally with no workspace git repo, how do they share `lore-workspace.md`? They don't — they each maintain their own. The spec implies this but doesn't say it. Some teams may find this confusing vs. a shared descriptor.

---

### 2d. Wizard Interview Flow — Friction, Clarity, Error Recovery

**Step numbering contradiction (blocker-class for implementers).** The init draft lists steps 1–9 in document order: 6 = memory file, 7 = workspace-pull. Then an "Ordering note" inside step 6 says "revised order: run step 7 before step 6." The steps are not renumbered. An implementer reading this will implement the wrong order and hit a bug: the agent-discovery lines in the memory file will be empty (repos not yet cloned when step 6 runs). The draft must renumber steps to reflect the actual execution order, removing the inline override note.

**Correct execution order (for reference):**
1. Context
2. Discover state
3. Repos interview
4. Git tracking
5. Write lore-workspace.md
6. Seed .gitignore
7. Run workspace-pull ← must precede memory file write
8. Write memory file managed section
9. Register-repo shortcuts (optional)
10. Summary

**Step 8 (register-repo) interrupts the success moment.** After a multi-step wizard the user wants to see the summary. Injecting an optional sub-interview before the summary creates fatigue. Either move register-repo into the summary as "next step you can run: `/lr:register-repo <repo>`" or make it a separate command entirely.

**Error recovery is implicit throughout.** If any step fails (git init fails, URL parse fails, workspace-pull fails), the spec says "report; artifacts remain; user fixes and re-runs." This is fine but each failure site should produce a concrete recovery command, not just a status message. See §3 for workspace-pull failure specifics.

---

### 2e. workspace-pull Failure Mid-Init

**Current spec:** step 7 failure → "report; workspace artifacts from steps 4–5 remain; user fixes and re-runs pull."

**What the user actually has at failure:**
- `lore-workspace.md` written ✓
- `.gitignore` seeded (if git workspace) ✓
- Memory file managed section: **NOT written** (step 8 runs after pull in revised order)
- Child repos: partial (some cloned, some failed)

**Recovery path is not spelled out.** The failure message should say:

> "workspace-pull failed. Your lore-workspace.md and .gitignore are intact. Fix the issue above, then run:
> 1. `/lr:workspace-pull` — re-clones missing repos (idempotent)
> 2. `/lr:workspace-init --refresh` — writes memory file once repos are on disk"

The spec should confirm `workspace-pull` idempotency on partial failure (already-cloned repos → present → skip). This is implied but not stated.

---

### 2f. Teammate Adds Repo to lore-workspace.md

**Phase 0 pull → phase 1 clone → phase 3 gitignore: the happy path works.** The example in the pull draft demonstrates this clearly.

**But phase 3 has a scope gap (blocker-class).** Phase 3 appends `/<dirname>/` only for repos "cloned in phases 1–2." If a teammate manually cloned a repo before it appeared in `lore-workspace.md`, that dir is already on disk. When it later appears in the descriptor, workspace-pull's phase 1/2 classifies it as "present → skip" and phase 3 never fires for it. Result: repo directory is present and declared but not in `.gitignore`. The new check #22 catches this reactively, but the fix should be proactive:

**Phase 3 should cover all declared repos present on disk, not only repos cloned this invocation.**

Revised phase 3 logic:
```
FOR each repo URL declared in lore-workspace.md + lore-repo.md (phases 1+2 set):
  derive dirname
  IF <workspace>/<dirname> exists as directory:
    IF /<dirname>/ not already in .gitignore:
      append /<dirname>/
```

This makes gitignore management idempotent and complete on every pull.

---

### 2g. Worktrees Convention in AGENTS.md

The managed section includes the worktrees convention (top-level = default branch; non-default = `.worktrees/<repo>/<slug>/`) and references `worktrees.md`. The gitignore seeds `/worktrees/` upfront.

**Bug: `/worktrees/` does not match `/.worktrees/`.** The convention uses a dot-prefixed directory (`.worktrees/`). A gitignore pattern of `/worktrees/` anchors to a top-level directory literally named `worktrees`, not `.worktrees`. These two strings do not match. The seeded pattern must be `/.worktrees/`.

Verify: does the worktrees convention document use `.worktrees/` or `worktrees/`? If it's `.worktrees/`, every workspace that opts into git tracking has a broken gitignore for worktrees from day one.

---

### 2h. Hard Rename Impact on Existing Users

**workspace-sync → workspace-pull:**
The spec has a contradiction. The "Deprecation" prose says "hard rename — no alias." The framework changes checklist says "workspace-sync thin wrapper calling workspace-pull." These cannot both be true. Decide: thin wrapper (compat for one release) or hard remove. The review lens says no alias. Given that, delete the checklist item and accept breakage. The doctor check mitigation is sufficient if it's surfaced prominently.

**init → workspace-init:**
Harder for existing users because `lr:init` is used in memory-file refresh workflows, and those users may have muscle memory or existing docs. The migration path (detect old markers → offer one-step upgrade) is well designed. The one-release compat path inside old markers is the right call.

**Bottom line:** hard rename on workspace-sync is the right call if doctor surfaces it. Hard rename on init needs the marker migration to ship in the same version — the spec has this. Both renames should be listed in release notes prominently under a "Breaking Changes" header.

---

### 2i. Reconfigure Mode vs Manual Edit

The design doesn't surface the simpler path clearly: **for most changes (adding a repo), the user should just edit `lore-workspace.md` directly and run `/lr:workspace-pull`** — no `--reconfigure` needed. `--reconfigure` is for re-running the setup interview: changing git remote, updating description, adding git tracking after the fact.

This distinction is not stated anywhere visible. The workspace-init doc should include a "When to use what" table:

| Goal | Recommended path |
|------|-----------------|
| Add/remove a repo | Edit `lore-workspace.md`, run `/lr:workspace-pull` |
| Change workspace description | Edit `lore-workspace.md` directly |
| Add git tracking after init | `/lr:workspace-init --reconfigure` |
| Change remote origin | `/lr:workspace-init --reconfigure` |
| Update memory file after framework upgrade | `/lr:workspace-init --refresh` |

Without this table, users will reach for `--reconfigure` for everything and be surprised by the full interview.

---

### 2j. README Scaffold (Open Item)

**This is a team-adoption blocker.** The team join path is: `git clone`, `cd`, run commands. But a new teammate doesn't know those commands unless the workspace repo has a `README.md`. The open item should be resolved to: **default yes** in the wizard, no question asked. The README is a first-class team artifact.

Minimum template for the seeded README:

```markdown
# <Workspace Name>

Lore Framework workspace — <description>.

## Join this workspace

Prerequisites: [Lore Framework installed](link), SSH access to workspace repos.

```bash
git clone <this-repo-url>
cd <workspace-dir>
/lr-workspace-pull      # clones all declared repos
/lr-workspace-init      # refreshes agent context in AGENTS.md
/lr-boot <agent>        # boot the agent you need
```

## Repos in this workspace

See `lore-workspace.md` for the full list.

## Conventions

- Production work: default branch of each repo
- Feature work: `git worktree` under `.worktrees/<repo>/<slug>/`
```

The wizard should ask for the workspace name (used in `lore-workspace.md` description and README title) once, and reuse it.

---

### 2k. Cursor vs Claude vs Codex Memory File

The spec says memory-file is `AGENTS.md` on Cursor/Codex, `CLAUDE.md` on Claude. The managed section's `### Commands` block lists:

```
/lr-workspace-pull
/lr-boot <agent>
/lr-workspace-init --refresh
```

**These command names are engine-specific.** Cursor uses `/lr-workspace-pull` (hyphen, skill name). Claude uses `/lr:workspace-pull` (colon, command format). The spec doesn't distinguish. If the wrong format is written to `CLAUDE.md`, Claude won't recognize the commands.

The managed section payload must be templated by engine, at minimum for the Commands section. A simple approach: two payload variants selected at step 0 based on resolved engine profile. Or use a comment noting "command format depends on your AI coding tool."

**Codex (AGENTS.md):** Does Codex support slash commands at all? If not, the Commands section in Codex's `AGENTS.md` should describe these as framework operations to invoke, not slash commands.

---

### 2l. Failure Modes — Dirty Workspace Tree

**Dirty workspace tree before phase 0 pull:**
`git pull --ff-only` on a dirty working tree fails with a non-obvious error. The spec has no guard. Phase 0 should pre-check:

```
IF <workspace>/.git AND origin remote configured:
  IF git -C <workspace> diff-index --quiet HEAD:
    git -C <workspace> pull --ff-only
  ELSE:
    ERROR: "Workspace has uncommitted changes. Commit or stash before running workspace-pull."
    EXIT 1
```

**Uncommitted lore-workspace.md before phase 0:**
Specific case: user locally edited `lore-workspace.md` (maybe added a repo) without committing. Phase 0 pull would fail or leave a conflict. The dirty-tree check above catches this. The error message should hint: "If you've edited lore-workspace.md locally, consider committing first or running workspace-pull without a remote workspace repo."

**Auth failures on clone:**
Phase 1/2 clone failures include auth errors, wrong URL format, private repos with no access. The exit code 1 covers all failures, but the summary should bucket them:
- `CONFLICT:` existing dir with different remote
- `AUTH_FAIL:` clone returned 128 / permission denied
- `NETWORK:` clone returned non-zero with no auth error

At minimum, auth failures should be called out distinctly so the user knows it's not a bug in their descriptor.

**`--ff-only` on diverged workspace repo:**
If workspace repo history diverged (teammate force-pushed, or local commits not on remote), `--ff-only` fails. This is correct behavior, but the error should tell the user: "Workspace repo history diverged — resolve manually with `git pull --rebase` or `git merge`."

---

## 3. Critical UX Issues (Blockers)

**B1 — Gitignore worktrees pattern bug.**
Init seeds `/worktrees/` but convention uses `.worktrees/`. Pattern must be `/.worktrees/`. Affects every git-tracked workspace from first init.

**B2 — Step numbering contradiction in init draft.**
Document lists memory-file write (step 6) before workspace-pull (step 7), but ordering note says run 7 before 6. Implementer will build the wrong order. Renumber to reflect actual execution sequence.

**B3 — Phase 3 gitignore scope gap.**
`workspace-pull` phase 3 only adds dirs cloned in this invocation. Repos already on disk but newly declared in descriptor are silently skipped. Phase 3 logic must cover all declared repos present on disk, not just those cloned this run.

**B4 — Workspace-pull failure recovery path undefined.**
Partial-state failure (workspace-pull fails mid-init) leaves user with lore-workspace.md written but no memory file, and no explicit recovery instructions. Failure message must output the exact commands to resume.

**B5 — Dirty workspace tree guard missing from phase 0.**
`git pull --ff-only` on dirty working tree gives confusing errors. Phase 0 must pre-check `git diff-index --quiet HEAD` and abort with a clear message.

---

## 4. Friction Points (Non-Blocking)

**F1 — No confirmation gate before step 4 writes.**
After the interview, user should see a summary of what will be created/changed and confirm before any file is written. One prompt: "Ready to initialize — proceed? [y/N]"

**F2 — Reconfigure vs. manual edit not surfaced.**
The "add a repo" use case should be documented as "edit lore-workspace.md + run workspace-pull," not `--reconfigure`. A usage table (see §2i) belongs in both the wizard summary and docs.

**F3 — workspace-sync wrapper/hard-remove contradiction in checklist.**
Checklist item "workspace-sync thin wrapper calling workspace-pull" contradicts "hard rename, no alias." Remove the wrapper item from the checklist and commit to one behavior.

**F4 — Register-repo (step 8) in the wrong place.**
Interrupts the success summary. Move to a "what's next" section in the summary output, not an interactive y/n gate.

**F5 — README scaffold is unresolved (open item #1).**
This is a team-adoption blocker. Resolve to: wizard creates README by default (no prompt needed for solo dev; on setup the answer is almost always yes). See §2j for template.

**F6 — Engine-specific command format in managed section.**
`/lr-workspace-pull` is Cursor syntax. Claude uses `/lr:workspace-pull`. The managed section must be engine-aware or engine-agnostic. See §2k.

**F7 — Solo dev bootstrap precondition undocumented.**
Empty directory + first lore use: how does the user have the skill loaded? The install docs should link to workspace-init, and workspace-init should document its prerequisites. Even one line in step 0 suffices.

**F8 — Auth failure classification in pull summary.**
Phase 1/2 clone failures are all exit-code 1. Summary should distinguish auth failures from network errors from conflict states.

**F9 — "No git workspace" path doesn't state what is lost.**
Step 3 wizard copy should list the tradeoffs before asking, not just offer the gate.

---

## 5. Questions for Design Author

**Q1.** The worktrees convention document (`worktrees.md`) — does it use `.worktrees/` (dot-prefixed) or `worktrees/`? The answer determines whether B1 is a real bug or a documentation alignment issue.

**Q2.** What is the intended resolution of the workspace-sync wrapper vs. hard-remove contradiction? The review recommends hard remove, but confirm intent.

**Q3.** For the team join path: is `AGENTS.md` always committed to the workspace git repo (i.e., the managed section is already present when a teammate clones)? If yes, the join path works as written. If the managed section is considered ephemeral / local-only, the join path needs a workspace-init setup step, not just refresh.

**Q4.** Phase 3 currently runs "for each child repo dirname cloned in phases 1–2." Should it instead be "for each declared repo that is present on disk"? The latter is idempotent and complete; the former misses pre-existing repos. Is there a reason to scope it narrowly?

**Q5.** For `CLAUDE.md` vs `AGENTS.md` — does the framework already have a mechanism to emit engine-specific content in managed sections, or would this be new infrastructure? If new, is it in scope for v25?

**Q6.** Step 8 (register-repo): is this meant to be interactive in the wizard, or can it be deferred to a "next steps" message? Recommend the latter to avoid wizard fatigue.

**Q7.** `--ff-only` on workspace repo pull: is the intent to be conservative (only accept fast-forward, fail otherwise), or should a rebase fallback be attempted? Recommend conservative, but surface a clear rebase hint on failure.

**Q8.** The open item on legacy `lr:init` markers: "one-release compat inside old markers, or hard break only?" The draft recommends "migrate on sight with one prompt." Is there a case where users would want to decline migration and keep old markers permanently? If not, remove the compat path and simplify.

---

## 6. Specific Recommendations

### Wizard copy — Step 3 (git tracking)

Current: "Should this workspace directory be a git repository?"

Recommended:

> **Should this workspace directory be a git repository?**
> 
> Saying yes enables:
> - Team sharing: push `lore-workspace.md` + `AGENTS.md` so teammates get workspace layout on clone
> - Automatic `.gitignore` management for nested repos
> - Phase 0 descriptor pull (teammates' repo additions arrive on your next workspace-pull)
>
> Saying no creates a local-only workspace — useful for solo work, but descriptor changes must be shared manually.
> 
> Track workspace as git repo? [Y/n]

---

### Wizard flow — Confirmation gate (new step between 3 and 4)

Before writing any files, show:

```
Ready to initialize workspace at /path/to/workspace/

Will create:
  lore-workspace.md      (repos: url-1, url-2)
  .gitignore             (worktrees + child repos after pull)
  AGENTS.md              (managed section, after workspace-pull)
  README.md              (y/n — see below)

Git: will run git init, add remote origin <url>

Proceed? [y/N]
```

---

### Phase 3 — Revised scope

```
# Cover all declared repos present on disk, not only those cloned this run
all_declared_dirs = (workspace-level + domain-level dirnames)
FOR each dirname in all_declared_dirs:
  IF <workspace>/<dirname> is a directory:
    IF /<dirname>/ not already in .gitignore:
      append /<dirname>/
```

---

### Phase 0 — Dirty tree guard

```bash
if git -C "$WORKSPACE" diff-index --quiet HEAD -- 2>/dev/null; then
  git -C "$WORKSPACE" pull --ff-only
else
  echo "ERROR: workspace has uncommitted changes — commit or stash, then re-run."
  exit 1
fi
```

---

### Init step order — Renumber

Remove the "Ordering note" inline override. Number steps to match execution:

1. Context  
2. Discover state  
3. Repos interview  
4. Git tracking  
5. Confirmation gate *(new)*  
6. Write lore-workspace.md  
7. Seed .gitignore  
8. Run workspace-pull ← **before memory file**  
9. Write memory file managed section  
10. Summary (includes: "next: `/lr:register-repo <repo>`" if applicable)  

---

### README scaffold — Default yes, no prompt

On setup mode, create `README.md` with the team-join template (see §2j) unless it already exists. Do not prompt — the README is always useful and can be freely edited post-init.

---

### Managed section — Engine-aware Commands block

```markdown
### Commands

<!-- Engine: Cursor/Codex -->
- `/lr-workspace-pull` — refresh workspace descriptor and all declared repos
- `/lr-boot <agent>` — boot a lore agent
- `/lr-workspace-init --refresh` — update this section after framework upgrade

<!-- Engine: Claude -->
- `/lr:workspace-pull`
- `/lr:boot <agent>`
- `/lr:workspace-init --refresh`
```

Or emit only the engine-appropriate variant at init time (cleaner).

---

### workspace-pull failure message template

```
workspace-pull encountered errors (exit 1).

Succeeded: lore-workspace.md ✓  .gitignore ✓  (N repos cloned)
Failed: M repos could not be cloned (see above)

To resume:
  1. Fix the issue above (auth, URL, network)
  2. /lr-workspace-pull        ← re-clones missing repos (safe to re-run)
  3. /lr-workspace-init --refresh   ← writes AGENTS.md once repos are on disk
```

---

*End of review.*
