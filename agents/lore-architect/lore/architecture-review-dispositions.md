# Architecture-Review Dispositions (2026-06-13)

A thorough self-review of the framework architecture: read the real implementation, engaged the design rationale, formed an independent critique, ranked the findings. This topic records the **dispositions** — what was actioned, deferred, or closed-as-deliberate — so settled-for-now questions don't get re-litigated. The detail of each disposition lives in its home topic (linked); this is the index.

## Dispositions

- **`lore-context.md` reads as a bloated index** → **ACTIONED** as the v17 lore-context shape discipline. The fix followed from diagnosing the real mechanism — *drift* against the design intent, not a "denormalized index" (the label I first reached for was wrong). See `lore-context-shape-discipline.md`; the misdiagnosis lesson is folded into `verify-before-acting-on-suspected-bugs.md` § Diagnose the mechanism before naming a weakness.

- **Machinery-about-the-framework has outgrown the core** (migration apparatus built well past its ~3 real migrations; the cache-staleness apparatus), **cross-agent mechanism count** (`consult` may be an `attach` usage, not a primitive), and **"name every principle" has no garbage-collector** → **DEFERRED together** as the simplification / subtraction theme. The framework optimizes for accretion and preservation with no countervailing subtraction force. The **lore housekeeping "sleep" pass** is the active mechanism proposed for the no-GC gap. Both live in `framework-improvements-backlog.md` (§ Architecture-Review Follow-Ups; § Lore Housekeeping / the "sleep" pass) — do not duplicate that detail here.

- **DF module living inside `lr`** → **DELIBERATE current decision, not a defect.** The user affirmed it. DF *may* graduate to a sibling plugin later; the `df-` prefix and `df/` subtree are pre-factored so the split would be mechanical. A known future option, not a pending fix. Recorded at `lr-dev-direction.md` § Disposition.

- **Team-shared / multi-author as the foundational framing** → **DELIBERATE current decision, not an open question.** The user affirmed it. Multi-author lore (with accepted voice drift) is a chosen property, not a coherence defect. Recorded at `team-shared-knowledge-principle.md`.

## Working-style note

The user does executive triage: a ranked findings list with clear recommendations let them action one, defer three, and close two as deliberate in a single pass. Bring critique as a ranked shortlist with a recommended disposition per item, not an exhaustive enumeration. See `feedback-too-many-words.md`.

## See Also

- `lore-context-shape-discipline.md` — the one actioned item (v17).
- `verify-before-acting-on-suspected-bugs.md` — the mislabel→misdiagnosis lesson the actioned item produced.
- `framework-improvements-backlog.md` — where the deferred simplification/subtraction theme and the "sleep" pass live in full.
- `lr-dev-direction.md`, `team-shared-knowledge-principle.md` — the two closed-as-deliberate framings.
- `feedback-too-many-words.md` — the ranked-shortlist working style this review exercised.
