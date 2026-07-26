# Verify a regression test by mutation, not by "it passes"

When writing a regression test for a bug that was already fixed (or that you're about to fix), don't
trust "the test passes" as proof the test pins the bug — a test can pass **vacuously** (e.g. by never
reaching the code path it claims to cover) while still reading as a real regression guard.

## The technique

Verify by mutation: temporarily revert the fix (or stub the dependency to reproduce the broken
behavior), re-run, confirm the new test **specifically fails** while the rest of the suite stays
green, then restore and confirm green again. Checksum the restored file if the mutation was applied
via `sed`/Python string replacement, to be certain the revert was exact.

## Two instances where it earned its cost (v31 `lr-core`, 2026-07-26)

1. A pre-existing test's own docstring promised "a broken toolchain must never masquerade as a skip"
   but only exercised the *first* git call site (empty `PATH`) and never reached the second
   (`remote get-url origin`) it also claimed to cover. Mutation testing this gap is what surfaced that
   the existing "five steps" fix needed a **second, distinct** test, not a strengthened version of the
   first.
2. A newly-written test (`TestGitUnrunnableAtEveryCallSite`) stubbed `git` to directly return the
   unrunnable sentinel, which proved the branch logic worked but proved nothing about which *real*
   failures (signal death, a non-git-related shim error) actually reach that branch — an adversarial
   reviewer found and reproduced three real inputs the stub-based test would have let regress
   silently. The fix was to add tests that reproduce the actual failure mode (`kill -9` in a shim
   binary, a non-"not a git repository" `rev-parse` error) rather than only stubbing the internal
   sentinel value. (The bug these tests pin is `git-dash-c-needs-toplevel-guard.md`'s sibling finding
   in the same review round.)

## General rule

A stub-based unit test proves the code handles the **shape** of a failure; only a test that
reproduces the actual failure mechanism (signal, real subprocess exit, real file corruption) proves
the code's classification of **real-world** failures is correct. Reach for the latter whenever the
whole point of the code under test is to correctly classify or distinguish failure modes — which is
exactly the situation this framework's git-handling code is in throughout (`auto-pull-mechanism.md`,
`git-dash-c-needs-toplevel-guard.md`).

## See Also

- `git-dash-c-needs-toplevel-guard.md` — the production bug one of these mutation-verified tests
  pins.
- `verify-before-acting-on-suspected-bugs.md` — the general "confirm which cause, not just whether"
  discipline; this topic is the same reflex applied specifically to *trusting a regression test*
  rather than trusting a diagnosis.
- `hot-path-latency-can-expose-latent-test-timing-races.md` — a sibling test-methodology lesson
  (stash-and-rerun A/B to confirm which side caused a failure) from the same lineage of "don't trust
  the first green/red, confirm the mechanism."
- `testing-simulate-process-escape-without-setsid-binary.md` — a sibling technique for building a
  test that reproduces a real failure *shape* deterministically rather than stubbing it away.
- `v31-lr-core-parked-2026-07-25.md` — the parked feature this technique was applied to.
