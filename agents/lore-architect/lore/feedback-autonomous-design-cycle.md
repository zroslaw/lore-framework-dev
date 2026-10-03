---
lore: 1
type: topic
summary: "User working style (2026-10-03): a delegated no-questions design cycle — review today's behavior, design with edge cases, iterate reviews, write a spec, separate design/spec drafts in workdir, finalize as a draft."
parent: lore-context.md
---

# Feedback — The Autonomous Design Cycle

On 2026-10-03 the user, away for hours, asked for a full design cycle with **no questions**:

1. review how the feature works today;
2. a design with edge cases;
3. repeated review until concerns are resolved;
4. an implementation spec;
5. design and spec as **separate** markdown files;
6. a finalized session recording the result as a **draft** for their later review.

The output feeds a future implementation session. First worked example:
[finalize-participant-revision-design.md](finalize-participant-revision-design.md).

## How to apply

- Put the files in `workdir/` as `draft-<feature>-design.md` and `draft-<feature>-spec.md`.
- **Resolve open questions by stating a decision with its reason** — do not block on the user
  ([feedback-commit-to-a-recommendation.md](feedback-commit-to-a-recommendation.md)).
- **Ship a review log inside the design doc** so the user can audit what was applied, accepted, or
  declined.
- **Minimalism is a reviewer in every round and the main direction** — see
  [feedback-mvp-minimalism.md](feedback-mvp-minimalism.md) for the lens and honest concept
  accounting.
- This is the explicit trigger that
  [feedback-draft-only-when-user-triggers.md](feedback-draft-only-when-user-triggers.md) waits for:
  in a dialogue session the conversation is the surface; in a delegated cycle the drafts are the
  deliverable.
