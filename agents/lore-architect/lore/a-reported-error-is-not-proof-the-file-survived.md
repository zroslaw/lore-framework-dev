---
lore: 1
type: topic
summary: "An error row that reads the same for a refusal and for a destroyed file is not evidence about the filesystem — when a guard promises the target is unchanged, make that structural (temp file + os.replace), not a catch block."
parent: lore-context.md
---

# A Tidy Error Row Is Not Proof the File Survived

Found by an independent correctness review of v43, in code I had just written and tested.

`open(path, "w")` **truncates the target the instant it succeeds, before anything is written.** A
failure between those two moments — ENOSPC, a quota, a killed process — leaves a valid file replaced
by a few bytes of garbage. My code caught the `OSError` and reported a clean `{"action": "error"}`
row: byte-identical in the result envelope to a refusal that never opened the file at all.

The reviewer reproduced it. A `.claude/settings.json` holding a team's `permissions`, `hooks`, and
`env` became `{\n  "` — six bytes — while the caller was told "error, file untouched."

**The general shape: an error path that reports the same thing for "I declined to act" and "I acted
and destroyed it."** The report is not evidence about the filesystem. Whenever a guard's promise is
*the target is unchanged*, that promise has to be structural, not a catch block.

Fix: write to a sibling temp file, `os.fsync`, then `os.replace` (atomic on POSIX and Windows),
unlinking the temp on any failure.

## The sibling defect, same review

**`UnicodeDecodeError` is a `ValueError`, not an `OSError`.** A read guarded only by
`except OSError` lets one stray byte escape as an unhandled exception — which crashed the command
out of its JSON envelope entirely and, because `workspace-scan` calls the same function, took every
other finding in the scan down with it. When guarding file reads, catch both.

## Operational lesson

My own test suite's docstring named "someone's hooks disappeared during a converge" as the thing to
defend, and then tested only refusals that happen *before* any write is attempted. **Tests written
by the author of the fix cluster on the paths the author was already thinking about.** The refusal
cases were thorough; the durability case did not exist. Ask specifically: *what does this code do
when it fails halfway?*

## See Also

- [a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) — same family:
  the evidence does not support the claim.
- [prove-a-new-test-red-against-the-previous-tag.md](prove-a-new-test-red-against-the-previous-tag.md)
- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md)
- [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md) — the feature this
  was found in.
