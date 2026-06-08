# Feedback: "enforce X" ≠ "add a required schema field" — schemas-as-enforcement can over-reach

2026-06-08. Corrective. The user asked to *enforce* the agent considering a unit's context during bug-finding. I turned "enforce" into a **required structured `context` field** (role/callers/collaborators/lifecycle) in `bugs.schema.json`, reasoning that to force a behaviour you require an output that can't be produced without it (schemas-as-enforcement). The user rejected it sharply ("drop this shit"); I reverted to **prose-only enforcement** in `step-a` ("you **must** trace callers/neighbours").

**Why it over-reached:** schemas-as-enforcement is a real lever, but it over-reaches when the required field is *input scaffolding* (the agent's own reasoning trace) rather than the *deliverable*.

**How to apply:**
- Default to **prose enforcement first** ("you must…"). Only add a required field when the field IS a product the user wants persisted.
- The clean test the user drew: a field that is the *output* of the work is welcome (`dismissed[]` / verdicts / revised `severity` — all kept); a field that is *scaffolding for* the work is not (the context-map — dropped).
- Don't bulk up a schema to police behaviour.

Composes with `feedback-confirm-before-writing-lore.md` and `feedback-too-many-words.md` (executor-first; don't over-build). Contrast `ula-finding-schema.md`, where the added fields ARE deliverables and stuck.

## See Also

- `ula-finding-schema.md` — the fields that DID belong (deliverables).
- `feedback-too-many-words.md`, `feedback-confirm-before-writing-lore.md` — the executor-first / don't-over-build family.
