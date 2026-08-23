---
lore: 1
type: topic
summary: "A skip condition keyed on a state that is normal for heavy users silently opts them out of the feature — ask what population the guard selects, and prefer reporting over guarding when the risk is 'the user did not know'."
parent: lore-context.md
---

# Guarding on a Normal State Excludes What Matters Most

Named 2026-08-23 while deciding whether an automatic workspace pull should skip dirty repos
([workspace-auto-refresh-design.md](workspace-auto-refresh-design.md)).

**Skipping dirty repos sounds safe. It is not.** Dirty is the *normal* state of a repo somebody is
working in. A guard keyed on it makes the most actively used repos the ones that stop being
refreshed — they stay stale indefinitely while emitting the same "please clean this up" message every
morning about work-in-progress the user has no intention of committing.

## Why the shape is dangerous

The guard's condition correlates with the very subjects the feature exists to serve. A freshness
feature that excludes actively-used repos has inverted its own purpose, and the inversion is
invisible because each individual skip looks prudent in isolation.

## How to apply

- **Before adding a skip condition, ask what population it actually selects.** If it selects the
  heaviest users of the feature, it is not a safety guard — it is a silent opt-out.
- **Prefer reporting over guarding when the risk is "the user did not know", not "data was
  destroyed."** Naming what happened costs one line and preserves the behaviour.
- **Check whether the guarded-against harm is real.** `git pull --ff-only` never destroys uncommitted
  work; in the worst case the merge refuses and git says so.
- **A recurring message about a normal state gets tuned out** — and takes the genuine signals sharing
  that output block down with it. This is the same reason
  [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md) gives a user a way to
  clear finding S3: *a finding a user can never clear teaches them to skim the whole report.*

## See Also

- [short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md) —
  sibling shape from the same design: a guard keyed on something convenient to observe rather than on
  the real condition.
- [dirty-tree-gates-write-vs-read-distinction.md](dirty-tree-gates-write-vs-read-distinction.md) —
  where a dirty-tree gate *is* justified: writes, not reads.
- [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md) — the design this was named in.
