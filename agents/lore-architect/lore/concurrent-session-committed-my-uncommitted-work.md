# A Concurrent Session Can Commit and Push Your Uncommitted Work

On 2026-07-28 two lore-architect sessions ran against the same workspace. I had uncommitted edits to
`lore-framework/docs/engines/cursor.md`. The other session ran `git add` / `git commit` over a scope
that included that path, and pushed. My edits landed on `origin/main` inside a commit titled
"Cursor: run merge via Task subagents" — an unrelated message — without my session doing anything.

Nothing was lost, and **this is not a merge conflict**. It is a different failure mode from
`same-agent-multiple-engines-single-writer.md`, which is about two sessions *writing* the same file.
Here the other session never touched my content; its staging command simply had a wide enough scope
to sweep it up.

## Consequences worth naming

- **Work deliberately held back from shipping got pushed.** I had stated that these changes were
  ungated — no lifecycle run — and should not go out. A concurrent commit does not know that. This
  is `post-convergence-edits-need-their-own-gate.md` violated from the outside.
- **Attribution and history are muddled.** The commit message describes something else entirely, so
  the change is effectively unfindable by anyone reading the log.
- **`git status` stops being a reliable inventory of "my session's work."** A file can silently
  leave the dirty list while the session is still reasoning about it.

## Operational rules

- **In a shared workspace, re-check `git status` and `git log` before reporting on your own change
  set** — not just at the start of the session. Verify what is still yours.
- **Do not leave deliberately-ungated work sitting dirty in a shared repo.** Put it on a branch, or
  expect it to ship on someone else's schedule.
- **Prefer narrowly scoped `git add <path>` over directory-wide staging when other sessions may be
  live.** The finalize procedure's `git add agents/` is exactly the wide form, and it is the one
  most likely to be running concurrently.

## Confirmed in the other direction, with no concurrency at all (2026-08-31)

The rule above predicted this from the outside in. It then happened from the inside out, during my
own finalization, and the variant is worse than the one recorded.

Finalize Phase 4 Step 1 is `git -C <repo> add agents/`, justified in the doc as *"scoped to the
agent tree so incidental untracked files elsewhere are not swept in."* That justification holds only
for a repo with one agent. `lore-framework-dev` holds **`lore-architect` and `lore-advocate`**, so
the command staged `agents/lore-advocate/workdir/agoda-internal-announcement.md` — another agent's
untracked draft — into a commit titled `Finalize session 463ddfa1`. I caught it at
`git diff --cached` and unstaged it before committing.

**No second session was required.** The recorded failure needs a concurrent writer; this one needs
only a repo with more than one agent, which is the normal shape. Every finalize in a multi-agent
repo is exposed, every time. That makes it the more likely of the two to fire, and it is invisible
after the fact: the sweep looks identical to the agent having authored the file.

### The framework already knows the right shape

`resolve-conflicts.md` stages `git -C <repo> add agents/<your-name>/` — per-agent, correct.
`finalize.md` Phase 4 stages `agents/`. Two procedures in the same framework, same operation, one
right and one wrong, and the wrong one is the one that runs on every finalize. This is
`single-canonical-source-discipline.md` failing at the *implementation* sites rather than the prose
sites: nothing states a wrong rule, the two just drifted.

The fix is to narrow `finalize.md` Phase 4 to the active agents' own subtrees
(`agents/<agent-name>/` per active agent, which the phase already enumerates for its per-repo commit
loop). It ships wide in v44. Filed in `framework-improvements-backlog.md`.

### Standing rule, sharpened

**Read `git diff --cached` before every finalize commit, not `git status`.** The staged set is the
thing being committed and the only place the sweep is visible; `git status --porcelain` shows the
same file as `A ` whether it is mine or not. This is the concrete point-of-use guard the earlier
"prefer narrowly scoped `git add <path>`" rule was missing
(`point-of-use-guardrails-beat-recorded-lore.md`) — that rule cannot fire when the procedure I am
following is itself the thing issuing the wide command.

## The other session need not be a human

Since a persistent `--launchd` Keeper is now live on this machine
(`lore-beings-design.md` § launchd install status), a Lore Being can spawn engine sessions without
anyone starting them. **When a repo changes under you mid-session, the Keeper is a candidate
explanation alongside a human-run parallel session** — do not assume concurrency implies a person.

## See Also

- `same-agent-multiple-engines-single-writer.md` — the adjacent rule: same agent identity, multiple
  engines, contending for the *same* files. This topic is the wide-staging variant, where content
  never collides at all.
- `cross-engine-team-substrate-validated.md` — the coordination substrate that makes single-writer
  designation workable.
- `post-convergence-edits-need-their-own-gate.md` — why an ungated push matters even when nothing
  was lost.
- `parallel-edit-git-add-race-conflict-resolve.md` — the intra-session version of a `git add` racing
  content that is not ready.
- `finalization-process.md`, `push-conflict-resolution.md` — the finalize commit scope this rule
  points at; `resolve-conflicts.md` carries the correct per-agent staging form that `finalize.md`
  Phase 4 does not.
- `single-canonical-source-discipline.md` — the drift between those two procedures.
- `a-red-test-may-be-asserting-a-true-fact.md` — the other environment-truth surprise from the same
  day.
- `prove-superseded-before-discarding-colliding-wip.md` — the corollary at merge time: colliding
  dirty state may not be yours, so compute whether the incoming version contains it before
  discarding.
- `a-release-review-starts-with-git-status.md` — check every repo's dirty state before reviewing or
  reporting on a change set.
- `lore-repo-divergence-is-self-inflicted.md` — the shipped path that does this to me: finalize
  Phase 4's `git add agents/`, which is also how agent repos end up permanently diverged.
