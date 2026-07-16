# Paste-link installer doc — a second onboarding genre

Onboarding docs used to have one genre: prose *pitching* a human reader (`onboarding-doc-narrative-pattern.md`). A second, distinct genre exists: a doc written *to the AI agent* as the literal installer, meant to be pasted as a link into any coding agent with "set this up for me." Shipped as `QUICKSTART.md` plus per-engine `INSTALL-<ENGINE>.md` in `lore-framework`.

## Shape that worked

- Open with the human-facing hook and a one-line "paste this link" instruction — dual-audience framing right at the top, since both the human and the agent read the same page.
- A dedicated `## For the AI agent reading this` section, addressed in second person to the agent, as a numbered operator playbook:
  1. Detect context (which engine).
  2. Fetch the matching canonical doc.
  3. Execute, narrating each step to the user.
  4. Pause before side-effecting/elevated actions.
  5. Verify success (accounting for restart-required quirks).
  6. Hand off to the next doc.
- Each per-engine `INSTALL-<ENGINE>.md` gets its own matching `## For the AI agent reading this` preamble, so an agent landing on any entry point gets the same operating contract, not just the hub (`QUICKSTART.md`).

## The failure mode this genre invites

A doc *about* an agent executing steps reads fine to a human proofreader but can still tell the agent to do something it structurally cannot — relaunch its own session, self-invoke a skill that shell-falls-through on that engine, guess a filename that diverges from the skill name. This is exactly the class of bug a **literal-execution** review lens catches and a prose lens won't. See `ai-installer-review-lens.md` for the review-lens response to this genre's specific failure mode, and `skill-doc-filename-divergence-bug-class.md` for a concrete bug this lens caught.

## See Also

- `onboarding-doc-narrative-pattern.md` — the sibling human-facing genre (long-form narrative, different audience and shape).
- `ai-installer-review-lens.md` — the review lens purpose-built for this genre.
- `skill-doc-filename-divergence-bug-class.md` — a bug this lens caught in the shipped installer docs.
- `onboarding-doc-narrative-pattern.md` § placement note — a landing-page meta-example placement refinement discovered in the same session, applied to the README that links to these installer docs.
