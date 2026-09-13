---
lore: 1
type: topic
summary: "A failure-classification table in executable prose must be built by walking the procedure's own exit paths, not from the cases the design discussed — an unlisted outcome makes the executing model guess."
parent: lore-context.md
---

# A Classification Table Must Enumerate Exit Paths, Not Interesting Cases

The v46 publish procedure classified publication failures into two rows — **transient** (network,
auth, timeout) and **blocked** (foreign conflict, merge refused). It read as complete. It omitted
**plain non-fast-forward rejection**, which is the *only* way the update path can fail at all, and
the outcome of exhausting the merge-retry cap.

The omission was not carelessness. It is the natural result of writing the table from the failures
the design had been *thinking about*: both listed rows came from hard cases discovered in review, and
the ordinary case nobody had argued about never got a row.

**The test is mechanical: walk the procedure's own exit paths and check each one appears.** Every way
the preceding step can end without success is a row. Do not enumerate from the discussion — the
discussion is biased toward the cases that were difficult, which is uncorrelated with the cases that
happen.

## Why this bites harder in executable prose than in code

An executing model handed an unlisted outcome **guesses**, and here the two guesses (keep the commit
/ roll it back) differ in whether the user's work survives. A missing `else` in code usually throws;
a missing row in executable prose silently picks one
([models-copy-what-they-should-compute.md](models-copy-what-they-should-compute.md) is the sibling
form — what the doc leaves unstated, the model supplies from its own priors).

**State the completeness requirement in the table's own preamble** — "every exit path of the previous
step has a row here" — so the next person adding a row knows what the set is supposed to cover, and
so a reviewer can check the table against the procedure instead of against plausibility. The
requirement belongs at the table, not in a distant convention section
([instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)).

Same predicate, one code path, remains the code-side discipline:
[one-question-one-code-path.md](one-question-one-code-path.md). Found by the deep grounded review of
the v46 spec ([review-grounding-beats-lens-novelty.md](review-grounding-beats-lens-novelty.md),
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md)).
