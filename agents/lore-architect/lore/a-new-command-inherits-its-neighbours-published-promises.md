---
lore: 1
type: topic
summary: "Before adding a command that writes where an existing one writes, enumerate what the neighbours promise about that location — docs, tests, findings catalog — and honour it by sharing the predicate, not reimplementing it."
parent: lore-context.md
---

# A New Command Inherits the Promises Its Neighbours Already Published

`/lr:workspace-sync` began by committing the workspace repo the way it commits a Lore repo:
everything not held. But `workspace-push` documents **and tests** that it never stages anything
outside the framework-managed path set, and `findings-catalog.md` S12 states that to users as "no
framework command will touch them". A personal draft left dirty at a workspace root would have been
committed and pushed — not a bug in the new command's own terms, a **contract collision** with a
promise the system had already made on its behalf.

**Before adding a command that writes where an existing one writes, enumerate what the existing
ones promise about that location** — in their docs, in their tests, and in any user-facing findings
catalog — and either honour it or change it deliberately and everywhere.

Honour it by **sharing the predicate**, not by reimplementing the rule: both commands now call the
same `is_managed`, so they cannot drift
([one-question-one-code-path.md](one-question-one-code-path.md),
[single-canonical-source-discipline.md](single-canonical-source-discipline.md)). This is the same
change-set-wider-than-the-diff reflex applied outward instead of inward
([a-change-set-is-wider-than-its-diff.md](a-change-set-is-wider-than-its-diff.md)).

**Review note:** the reviewer that found this was briefed on "system fit and release completeness"
— a lens worth spending on any change that adds a surface to an established system, and distinct
from correctness lenses that only read the new code
([parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md),
[lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)).
