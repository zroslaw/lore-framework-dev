---
lore: 1
type: topic
summary: "A lock-claim primitive must create its lock's parent directory before the exclusive create, and must return a tri-state result — claimed/in-progress/error — never collapse 'couldn't create the lock' into 'contended.'"
parent: lore-context.md
---

# Lock-Claim: Directory Creation vs. Contention

A lock-claim primitive (`O_CREAT|O_EXCL` on a lock file) must create the lock's parent directory
*before* attempting the exclusive create, and must distinguish "the directory/lock couldn't be
created" from "another session holds a live lock." Collapsing both into one bare `except OSError:
return False` makes a permissions error or a missing parent directory silently masquerade as normal
contention.

## The concrete instance (v42 workspace-auto-refresh design, 2026-08-23)

Implementing `_claim_lock` for the workspace-auto-refresh feature
([workspace-auto-refresh-design.md](workspace-auto-refresh-design.md)), the very first call on a
brand-new workspace raised `FileNotFoundError` — the parent `.tmp/lr-state/` directory didn't exist
yet, because nothing had created it before the lock attempt — inside a bare `except OSError: return
False`. The caller read `False` as "in-progress" and reported it as such, indistinguishable from a
real concurrent session, on exactly the one case (first-ever run) where no other session could
possibly exist.

Caught by an end-to-end smoke test that expected a working refresh and got `in-progress` instead
with no state directory on disk at all. The tell was the **absence** of the expected side effect,
not an assertion failure — worth noting alongside
[verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md): the smoke
test's disagreement with disk state is what exposed the bug, not the returned boolean.

## The fix

`_claim_lock` returns a three-way result — `"claimed"` / `"in-progress"` / `"error"` — instead of a
bool. `os.makedirs` on the lock's parent directory is attempted first, with its own failure mapped
to `"error"`, kept structurally separate from the `O_EXCL`/mtime-staleness contention logic. The
caller maps `"error"` to a `failed`/`invocation` status rather than `in-progress`.

## How to apply

Any future TTL/lock-guarded mechanism in this framework (more `lr-core preflight` legs are likely)
should default to a **tri-state claim result, not a bool**, whenever "couldn't create the lock" and
"someone else holds the lock" are reachable through the same code path. This is the same shape as
the other v42-workspace-refresh design lessons: a single collapsed signal hides a rare but real case
behind a common one.

## See Also

- [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md) — the feature this lock guards.
- [guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md),
  [short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md) —
  sibling design-time rules from the same feature: collapsing distinct cases into one signal drops
  the rare one.
- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md) — the
  absence of an expected side effect as the tell that exposed this.
