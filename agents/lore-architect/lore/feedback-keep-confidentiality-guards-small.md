---
lore: 1
type: topic
summary: "User directive (2026-10-04): keep confidentiality guards short and fail-closed; when a safety guard draws findings in two consecutive review rounds, replace it with the coarsest rule that disables the feature in the risky case."
parent: lore-context.md
---

# Feedback — Keep Confidentiality Guards Small

User directive (2026-10-04): confidentiality handling should not take a large part of a design or its
implementation. Agree on a fail-closed guard, keep it short, and don't let it dominate review rounds.

## What the same session showed

On the finalize participant revision draft
([finalize-participant-revision-design.md](finalize-participant-revision-design.md)), a confidentiality
guard patched round after round kept generating new leak findings — restrict additions to the same
repo → the host must stay in that repo → a stays-inside-repo constraint — each patch opening a new
seam. What converged was the **coarsest fail-closed form**: "if a confidential repo is in use, the
feature does nothing", one gate line, with the manual override (`/lr:attach`) left to the user.

## How to apply

- When a safety guard produces findings in **two consecutive review rounds**, stop refining it.
  Replace it with the coarsest fail-closed rule that disables the feature in the risky case.
- State it as **one gate line**, so it can later be swapped as a unit for real metadata (here, repo
  visibility in `lore-repo.md`).
- This is the minimalism lens applied to safety
  ([feedback-mvp-minimalism.md](feedback-mvp-minimalism.md)) and a specific case of a periphery that
  churns while the core is stable
  ([non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md)).
