---
lore: 1
type: topic
summary: "A state file annotates a condition the system can prove independently; it never asserts it. Consumers revalidate against the real source and delete a file whose condition is gone — plus derive-don't-maintain and one canonical reader."
parent: lore-context.md
---

# A State File Is a Hint, Not a Verdict

**When adding a state file that records a fault, the file annotates a condition the system can prove
independently; it never asserts the condition itself.** Consumers revalidate against the real source
and delete a file whose condition is gone.

## How I got this wrong

I designed a stranded-publish marker that was the **sole evidence** for a health finding. It had
exactly one removal path — the framework's own next successful publication. A user who fixed the repo
by hand would have left the marker in place, and the repo would have reported a fault forever, at
`warn` severity, in two separate surfaces. I had written a rule against crying wolf three sections
earlier in the same document
([guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md)
is the neighbouring failure: a signal that misfires trains itself out of the user's attention).

The framework already had the convention and I had not generalized it. `update.md`'s
`lr-update-pending` marker is never trusted at face value — retry requires branch, upstream and
`HEAD` all to still match, and a marker failing any check is reported as **stale** rather than acted
on. `workspace_refresh.py:needs_refresh` self-heals on every malformed-timestamp case. Both treat
their file as a hint over an authoritative source
([update-process.md](update-process.md),
[workspace-auto-refresh-design.md](workspace-auto-refresh-design.md)).

## Three rules for any new state file

- **Revalidate and self-clear.** Stale, malformed, unknown-version, or wrong-branch all mean "no
  useful information" — report nothing, delete it. The condition is re-derived from the real source
  (here: `git rev-list --count`), and the file only says *where to look*.
- **Derive what you can instead of maintaining it.** Counters and first-seen timestamps required a
  read-modify-write that two concurrent sessions could interleave and lose; the file's own mtime gave
  the same signal for free. Do not build bookkeeping for a decision you are deferring.
- **One canonical reader.** Two consumers in two languages parsing the same file by convention will
  drift; put the parse in one function and have both call it
  ([single-canonical-source-discipline.md](single-canonical-source-discipline.md),
  [one-question-one-code-path.md](one-question-one-code-path.md)).

Where the file goes is its own decision:
[git-common-dir-for-repo-wide-state.md](git-common-dir-for-repo-wide-state.md).
These rules made the marker expensive relative to what independent detection already gives, which is
why review after review deferred it. The tiering that deferred it is withdrawn, so **the marker and
its canonical reader now ship in v46** and owe the first review they never had
([v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md)).
