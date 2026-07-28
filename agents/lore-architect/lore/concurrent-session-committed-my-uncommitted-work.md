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
  points at.
- `a-red-test-may-be-asserting-a-true-fact.md` — the other environment-truth surprise from the same
  day.
