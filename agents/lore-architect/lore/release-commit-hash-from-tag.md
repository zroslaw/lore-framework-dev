---
lore: 1
type: topic
summary: "Derive release commit SHAs from the lr--v1.<N>.0 tag, never from scrollback; note the v32-v35 tag gap where recovery must use versioning-release-types.md hashes instead."
parent: lore-context.md
---

# Record release commit hashes from the tag, not from memory of a recent SHA

When recording a runtime release commit anywhere (e.g. `MARKETPLACE.md`'s "Runtime release commit"), **derive it from the release tag** — never copy a SHA from terminal scrollback or a recent log line.

**Rule:**
- Resolve the commit from the tag: `git rev-parse --short '<tag>^{commit}'` (e.g. `lr--v1.<VERSION>.0`).
- Sanity-check reachability from the branch users consume: `git merge-base --is-ancestor <sha> main`.

## Why (the v26 incident)

`MARKETPLACE.md`'s runtime commit was filled in as `42dd3b8` by a Cursor-authored fix commit. That SHA was an **orphaned pre-push duplicate** of the release commit — same message ("Release v26: Cursor takeover conversion") but not reachable from `main`, likely amended/rebased before push. The real release commit is `3909129`, which is what tag `lr--v1.26.0` points to. Corrected in `84948e8`.

Two traps combined to make the wrong SHA look plausible: amend/rebase-before-push silently invalidates any SHA seen earlier in the session, and **duplicate commit messages** make an orphaned commit indistinguishable from the real one by eye. Deriving from the tag defeats both.

## The v32–v35 tag gap (and tagging as part of the push step)

Release tags (`lr--v1.<N>.0`) lapsed for **v32–v35** — those versions shipped to `main` untagged;
the last tag before the 2026-08-09 session was `lr--v1.31.0`. **v36 resumed tagging**
(`lr--v1.36.0` on `e5e097b`).

Why the gap matters: the Script Fallback Contract's floor case recovers a lost module via
`git show <last-release-tag>:<path>`. For the v32–v35 range that recovery must fall back to the
commit hashes recorded in `versioning-release-types.md` entries instead — the tag is not there to
resolve.

Discipline: **at every ship, tagging is part of the push step**. When verifying ship state, check
the tag list (`git tag -l 'lr--*'`), not just `git log` — an untagged release looks shipped by
every other signal.

## Proposed `/lr:check` item (future)

If `MARKETPLACE.md` names a runtime commit and the matching `lr--v1.<VERSION>.0` tag exists, verify they agree (`git rev-parse '<tag>^{commit}'` == the recorded SHA). A mechanical check would have caught the v26 drift at author time.

## See Also

- `engine-marketplace-readiness.md` § Submission identity discipline — the runtime-release-identity that this SHA records.
- `versioning-release-types.md` — per-version release history; the tag is the source of truth for the release commit.
- `verify-before-acting-on-suspected-bugs.md` — derive-from-source-of-truth over trust-scrollback is the same reflex.
- `consistency-checks.md` — where the proposed check would land.
