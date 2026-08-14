---
lore: 1
type: topic
summary: "On macOS `/var` is a symlink, so bash `pwd` and git `--show-toplevel` disagree — \"resolve both to real paths\" is not self-executing prose; name the exact realpath command."
parent: lore-context.md
---

# macOS `/var` Symlink Makes `pwd` vs. `realpath` Disagree (Environment Trap)

Third macOS-specific environment trap found in a single stretch of work (siblings:
`macos-ps-o-multi-field-single-line.md`, `macos-documents-permission-loss-mid-session.md`) — worth
checking, on a fourth occurrence, whether these should consolidate under a hub topic. Found 2026-07-27
diagnosing `test_boot.py`'s flaky `test_05` scenario against the parked v31 branch.

## The bug

`docs/version-check.md`'s nested-repo guard (added in an earlier trilens round) told the executor to
run `git -C "<repo>" rev-parse --show-toplevel` and "compare the result against `<repo>` itself
(resolve both to real paths)" — correct in principle, but it didn't specify **how** to resolve a real
path. A weak model (haiku) filled the gap with `real_repo=$(cd "<repo>" && pwd)`.

On macOS, `/var` is a symlink to `/private/var`. Bash's `pwd` without `-P` returns the **logical** path
(does not resolve symlinks); git's `--show-toplevel` always returns the **physical**, resolved path.
Any tmpdir-based path — exactly what `TMPDIR` gives on macOS, and so any test-fixture-style repo —
makes the two disagree even when the repo genuinely *is* its own git root, producing a false "not its
own git root" verdict that silently skips a real, needed operation.

`scripts/lr-core`'s own `git_toplevel()` avoids this entirely because it uses `os.path.realpath()` on
both sides — the bug only exists in the parallel **prose** procedure doc, not in the deterministic
script.

## Measured impact

This alone accounted for the bulk of a ~50% failure rate on `test_boot.py`'s `test_05` scenario —
verified via A/B (see `flaky-scenario-diagnosis-needs-ab-baseline.md`): the shipped v30 baseline hit
the identical bug through its own copy of the same doc, at a similar rate, confirming this was a
pre-existing bug in shared prose, not a v31-specific regression.

## Fix

Replace "resolve both to real paths" with an exact, copy-pasteable one-liner —
`python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))"` — the same primitive the script
uses, so there's no room for the executor to substitute a plausible-but-wrong equivalent (like bare
`pwd`). Post-fix measured rate: 18/19 (95%), with the one residual failure showing a different,
non-deterministic shape (a full skip of reading `version-check.md`, not a miscomputed comparison) —
accepted as ordinary weak-tier variance, not chased further. Fix committed as `cd8ece1`
(lore-framework), part of the trilens rounds over the parked v31 branch — see
`v31-lr-core-parked-2026-07-25.md`.

## Generalizable rule

When a procedure doc asks an executor to compare two paths "resolved to real/absolute form," that
phrase is **not self-executing** — specify the exact command. This is a sharper instance of
`execution-testing-catches-blind-ambiguity.md`: the ambiguity here was invisible to prose review (a
strong reviewer resolves "resolve to real paths" the same way the author intended) and only surfaced
by running the real doc against a real weak-tier engine on real macOS paths.

## See Also

- `realpath-for-identity-logical-for-contract-shape.md` — the other half of the rule: resolve for
  *identity* questions (this topic), but **do not** resolve when validating that a caller typed a
  contract-shaped path, or a user with a symlinked scratch root is wrongly refused.
- `macos-ps-o-multi-field-single-line.md` — sibling macOS trap: `ps -o` with multiple fields prints
  one line, not one line per field.
- `macos-documents-permission-loss-mid-session.md` — sibling macOS trap: TCC permission revocation
  mid-session makes a run's verdict uninterpretable.
- `execution-testing-catches-blind-ambiguity.md` — the general principle this sharpens: prose
  ambiguity invisible to a strong-model reviewer only surfaces via real execution testing.
- `flaky-scenario-diagnosis-needs-ab-baseline.md` — the A/B methodology that distinguished this
  pre-existing bug from a suspected v31 regression.
- `haiku-ambiguity-detector.md` — why running at the haiku tier is the point: it's what surfaced this.
- `v31-lr-core-parked-2026-07-25.md` — the concrete run and fix commit this came from.
