# A Red Test May Be Asserting Something True About the Machine

**Before making a red test green, establish which side is wrong.** A test can fail because the world
changed, because the code is broken, or because it is correctly reporting an unwelcome truth about
the environment. Only the first two are "test rot," and the third is the one that punishes a reflex
fix.

## Two failures, one 2026-07-28 run, opposite correct treatments

Both looked like rot on sight. Only one was.

**`test_lrb.py::test_install_is_sandboxed_and_idempotent`** asserts that the real
`~/Library/LaunchAgents/com.lore-beings.keeper.plist` does not exist after a *sandboxed* install. It
failed because that plist genuinely exists on this machine
(`lore-beings-design.md` § launchd install status). The assertion was doing its job: it is a
**sandbox-escape check**, and "fixing" it would have deleted a real safety guarantee in order to
make a suite green. Left untouched and reported instead.

**`test_session_archive.py`** pinned `framework_version` to `"29"` while `VERSION` is 33. That one
*was* rot — but the first fix was still wrong. I de-hardcoded **both** assertions using the literal;
the markdown one then failed. The archive frontmatter value is **caller-supplied** via
`--frontmatter-json`, and the test asserts that `setdefault()` does not clobber it, so the literal
was correct there. Only the `stats` value reads the live `VERSION`. Two sources, one number,
opposite correct treatments.

## Rules

- **Establish which side is wrong before touching either.** The failure message names what was
  observed, never why — same shape as
  `v31-lifecycle-rerun-partial-green-2026-07-27.md`'s "a failure list is a hypothesis."
- **A test whose assertion protects against a dangerous outcome gets the strongest presumption of
  correctness.** Sandbox escape, credential leak, destructive write: weakening one of these is a
  change to the safety posture, not a test cleanup, and it must be argued as such.
- **When de-hardcoding a constant, check every assertion that uses it separately.** Identical
  literals can have different provenance — one read from live state, one supplied by the caller —
  and a single sweep silently changes what one of them means.

Incidental but material: this failure is how I learned a real Lore Beings Keeper is installed and
running on this machine.

## See Also

- `verify-before-acting-on-suspected-bugs.md` — the parent reflex; this is its test-suite face.
- `verify-regression-tests-via-mutation.md` — the inverse case: a *green* test that proves nothing.
- `v31-lifecycle-rerun-partial-green-2026-07-27.md` — a failure list is a hypothesis until someone
  reads the transcripts.
- `lore-beings-design.md` — the live launchd Keeper install this surfaced.
- `concurrent-session-committed-my-uncommitted-work.md` — the other environment-truth surprise from
  the same day.
