---
lore: 1
type: topic
summary: "When cold reviewers contradict each other on a fact, open the cited source and read the invariants that qualify the rule; record the check in the review log's Declined list so the claim is not re-raised."
parent: lore-context.md
---

# Settle Conflicting Reviewer Claims in the Source

When two cold reviewers disagree about a factual claim, don't pick by reviewer confidence or
recency — **open the cited source and read the neighbouring invariants.**

## The case (2026-10-04)

On the finalize participant revision draft
([finalize-participant-revision-design.md](finalize-participant-revision-design.md)), a minimalism
reviewer said "cut the sentence — Phase 4 already commits every active agent's repo"; a data-flow
reviewer said a demoted booted agent's repo would be skipped. `finalize.md` Phase 4 does list "each
active agent's repo", but its Invariants section says *No empty commits: if nothing was produced by
phases 1–3 in a given repo, skip committing* — which decides it for the data-flow reviewer. The
minimalism reviewer read one paragraph; the data-flow reviewer read the whole procedure.

## How to apply

- Before applying a "this is redundant, existing behavior covers it" cut, find the existing rule
  **and every invariant that qualifies it**.
- Record the check in the review log's **Declined** list. The same cut was raised again the next
  round; the log entry let me decline it in seconds.

Related: [review-grounding-beats-lens-novelty.md](review-grounding-beats-lens-novelty.md) (claims
about other files are where reviews fail) and `check-own-lore-before-dismissing-a-finding.md` (read
the rule, don't reconstruct it).
