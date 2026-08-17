---
lore: 1
type: topic
summary: "Resolve symlinks when comparing two paths for identity; compare logical components when validating that a caller typed a contract-shaped path — using the wrong one produces a false mismatch in one direction and a false refusal in the other."
parent: lore-context.md
---

# Realpath for Identity, Logical Components for Contract Shape

Two path checks look alike and need opposite treatment. I got each one wrong once during the v39
review, in opposite directions, within two rounds.

**Comparing two paths for identity** — "is this the same directory as that one?" — must resolve
symlinks on both sides. Unresolved, macOS's `/var` → `/private/var` makes two names for one directory
compare unequal. This is the rule already recorded in
[macos-var-symlink-realpath-ambiguity.md](macos-var-symlink-realpath-ambiguity.md) and enforced in
`version-check.md`'s nested-repo guard.

**Validating that a caller supplied a path of an agreed shape** — "does this end in
`.tmp/lr-finalize/<run-id>`?" — must *not* resolve first. Resolving rewrites the very components
being validated: a user whose `.tmp` is a symlink to a redirected scratch root (a synced home
directory, or writes moved off a slow disk) has their correct path collapsed into the target's name
and refused. In v39 that refusal would have fired mid-finalization, on the real user's real session,
on a setup the framework intends to support.

The discriminator is what the check is *for*. Identity questions are about the filesystem, so ask the
filesystem. Shape questions are about whether the caller followed the contract, so read what the
caller actually wrote. A shape guard exists to catch a mistyped destination, not to overrule someone
who deliberately redirected their own storage.

Two corollaries worth carrying:

- **State the direction where the check lives.** Both the writer's docstring and the calling
  procedure now say *why* they compare logical components, in one sentence, because the next reader's
  instinct will be to "fix" it by adding a `resolve()`.
- **The prose statement of the rule drifts first.** The v39 guard was correct in code from round 2
  onward, and its restatement in the Cleanup section was still wrong two rounds later — describing
  the run directory's own trailing components instead of its parent chain, a check no real run could
  satisfy. See [fix-defects-are-context-errors.md](fix-defects-are-context-errors.md) § v39 and
  [single-canonical-source-discipline.md](single-canonical-source-discipline.md).

## Third instance — a fixture that writes a tool's config bypasses its normalization (v41, 2026-08-17)

A Keeper self-scheduling scenario failed with "cwd is not a registered workspace." The tool was
entirely correct: its register path stores realpaths and its schedule path compares realpaths. The
**fixture** wrote the config file directly with the bare `mkdtemp()` result, which on macOS is the
logical `/var/...` path — so the registered workspace could never match and no being could ever be
found.

The generalization is not about paths at all: **a fixture that hand-writes a tool's config inherits
none of the normalization the tool's own entry point applies.** Construct through the command, or
realpath at the fixture root. Fixed at the fixture, the scenario passed in 80s versus a 356s timeout
loop.

Honesty note kept in the ship record: lore showed this scenario green earlier with no relevant code
change since, so no regression was claimed — only that it fails now, and why.

## See Also

- [macos-var-symlink-realpath-ambiguity.md](macos-var-symlink-realpath-ambiguity.md) — the identity
  half, with the exact `os.path.realpath()` one-liner that replaced unexecutable prose.
- [point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md) —
  why the "why logical, not resolved" sentence belongs in the docstring, not only here.
- [versioning-release-types.md](versioning-release-types.md) — the v39 entry, where this guard's
  review history is recorded.
