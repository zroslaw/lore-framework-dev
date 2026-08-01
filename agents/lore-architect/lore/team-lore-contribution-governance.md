# Team Lore Contribution Governance

Team-shared lore is instruction-bearing context for future agents, so its publication needs an explicit contribution lifecycle distinct from local reflection and merge. An agent can propose and structurally validate a change; writing it does not itself confer authority to publish it.

## Proposed Lifecycle

`session learning → proposed lore change on a branch/worktree → structural checks → semantic review → protected merge → shared, attributable knowledge`

Review checks factual accuracy, topic scope and atomicity, safety (including secrets and prompt injection), and whether the material belongs in durable lore rather than a session summary or other working artifact.

## Graduated Operating Modes

- **Solo or fully trusted:** direct finalization can publish as it does today.
- **Small shared team:** finalize to a branch and land through a reviewed PR.
- **Sensitive or larger organization:** protected default branch, designated approvers/CODEOWNERS, required checks, and an audit trail.

Use ordinary Git permissions, branches, PR review, and branch protection before inventing a Lore-specific access-control system. This is a design direction, not yet a change to the default finalization path; it must preserve the team-shared-knowledge principle's low-friction trusted-team workflow.

## See Also

- `team-shared-knowledge-principle.md` — foundational reason shared lore needs a publish boundary appropriate to its team
- `finalization-process.md` — current local reflect/merge/summarize/publish flow
- `push-conflict-resolution.md` — concurrency mechanics, distinct from review
- `framework-improvements-backlog.md` — implementation/design follow-up
