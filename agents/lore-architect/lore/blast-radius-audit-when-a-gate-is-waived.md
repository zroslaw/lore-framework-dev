---
lore: 1
type: topic
summary: "The cheap structured substitute when the user waives the expensive gates: partition the change set, prove the untouched untouched, read every shared-code edit, and A/B the essential path's real output."
parent: lore-context.md
---

# Blast-Radius Audit When a Gate Is Waived

When the user declines the expensive gates but still asks *is this safe to ship?*, the honest answer
is not "ship blind, the gates were optional". There is a cheap structured substitute. It does not
replace a lifecycle run — it **bounds what the unrun gate could have caught**. v45 (2026-09-09) is
the worked example.

## The four steps, cheapest first

1. **Partition the change set by surface.** `git diff main...HEAD --name-only` piped through a
   `grep -v` of the feature's own files. What is left is, by construction, everything the release
   touches *outside* the thing being changed. On v45 that turned 76 changed files into 29, and most
   of those were link renames.
2. **Prove the untouched things untouched.** Loop the essential docs and scripts through
   `git diff main...HEAD --quiet -- <path>` and print `unchanged` / `CHANGED` per file. Fifteen
   `unchanged` lines are far stronger reassurance than prose, and it takes seconds. **Name the paths
   explicitly rather than globbing** — the point is to state which functions you are certifying.
3. **Read every shared-code edit.** v45 had exactly four (an extracted env dict, a
   `GIT_OPTIONAL_LOCKS` flag, a stamp refactor, one new optional parameter). Four is auditable by
   reading. **If this number is large, the audit fails and the gate is not waivable.**
4. **A/B the essential path's actual output.** The decisive evidence: run the old and new
   `lr-core preflight` against the same real agent, normalise the fields that must differ
   (framework root, profile path, version), and assert the rest is equal. On v45 it came back
   identical. That is a *measurement*, not an argument, and it is what makes the audit worth
   trusting.

## Then state what it does not cover

An audit shows the code paths did not move. It says nothing about whether a model follows new
instructions. On v45 the uncovered residue was exactly that: real-engine execution of the new prose
notices, and of the new command itself.

## Report it in the ship record

A waiver is a record, and **so is the thing done in its place**. Otherwise the next reader sees only
"lifecycle: did not run" and cannot tell whether anyone looked.

## See Also

- [gate-waiver-is-a-record.md](gate-waiver-is-a-record.md) — the waiver itself is the record; this
  is what to write *beside* it.
- [feedback-pre-ship-gates-on-request.md](feedback-pre-ship-gates-on-request.md) — why the expensive
  gates default to off, which is what makes this audit routine rather than exceptional.
- [a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) — why step 4's
  measured A/B outranks steps 1–3's reading.
- [a-release-review-starts-with-git-status.md](a-release-review-starts-with-git-status.md) — the
  audit certifies a specific tree; establish which tree first.
- [versioning-release-types.md](versioning-release-types.md) — the v45 entry carries the audit's
  result.
