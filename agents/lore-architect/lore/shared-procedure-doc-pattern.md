When a behavior must fire from multiple sites (boot + attach + merge + a user-invoked skill), factor the procedure into its own doc once and have every call site delegate to it. A refinement of `skill-doc-pattern.md`, but for **procedures rather than skills**.

The skill-doc pattern says SKILL.md is a thin pointer to `docs/<skill>.md`. The shared-procedure-doc pattern extends that: when a *non-skill* procedure is needed by multiple skills/docs, it gets its own `docs/<procedure>.md` with an audience-note banner marking it as internal scaffolding (no `/lr:<procedure>` skill exists by that name).

## Canonical examples

- **`docs/version-check.md`** (v3+) — repo-version reconciliation. Called from `agent-boot.md` and `attach.md`. No `/lr:version-check` skill — it's a procedure, not a user-facing operation.
- **`docs/auto-pull.md`** (v13) — single-repo `git pull --ff-only` with safety gates. Called from `agent-boot.md` step 2, `attach.md` step 2, `process-merge.md` step 0, and `docs/pull-lore.md`. Each call site is a one-line "follow auto-pull.md scoped to `<repo>`."
- **`docs/resolve-conflicts.md`** — finalize-time merge of remote conflicts. Called from `docs/finalize.md` phase 4. Same shape: shared procedure, no skill.

## When to apply

If a behavior is going to be invoked from ≥2 sites with the same semantics, extract it before the second caller is written. Resist inlining "just for one more site" — drift starts immediately. The cost of the second inlined copy is low; the cost of the third is the bug you ship next month when one site updates and the others don't.

The same trigger as the `skill-doc-pattern.md` orchestration refinement (skill file growing inline step-by-step content), but applied at the doc layer rather than the skill layer.

## Authoring checklist

- **Top-of-doc audience note** clarifying it's internal — there is no `/lr:<procedure>` skill. Users invoke the behavior implicitly via the calling skills, and explicitly only via whichever user-facing skill exists (e.g., `/lr:pull-lore` for auto-pull).
- **Inputs** section listing what each caller passes in.
- **Procedure** section — the actual steps. Self-contained — every caller follows the same body.
- **Invariants** section so all callers share the contract (e.g., "best-effort, never blocks the surrounding flow"; "no destructive actions"; "idempotent").
- **Per-call-site verbosity table** when the same procedure has different visibility expectations across callers (boot/attach/merge usually quiet on no-op; user-invoked verbose). Express as a table mapping outcomes × call sites → output behavior.
- **Distinct From** section listing sibling procedures and how they differ. Prevents readers from conflating with the wrong procedure.
- **See Also** that reciprocates from each call site — every doc that delegates to this procedure should link back.

## Why this pattern composes with skill-doc-pattern

Skill-doc-pattern: `skills/<name>/SKILL.md` → `docs/<name>.md`. Logic in the doc, skill is a thin pointer.

Shared-procedure-doc-pattern: `docs/<procedure>.md` invoked from multiple `docs/<skill>.md` (or other docs). No matching skill — the procedure is shared scaffolding.

Both keep logic in `docs/`. Both keep the calling layer thin. The difference is that a shared procedure has *no* user-facing surface of its own — it's pure internal infrastructure. The audience-note banner is the distinguishing marker.

## Signals you should be using this pattern

- You're about to copy-paste a procedure into a second caller. Stop. Extract it.
- You find inconsistent behavior across two callers that should match. The fix is consolidation, not parallel patching.
- A user-invoked skill is doing exactly what an automatic step does internally — wrap both around the same procedure doc, with verbosity differing per call site.

## Anti-patterns

- **Inlining "just one more time."** The third caller is when drift starts shipping bugs.
- **Naming the procedure doc after a fictional skill.** If there's no `/lr:<procedure>` skill, the audience note must say so explicitly — otherwise readers expect a skill to exist.
- **Letting one caller add side-effects the others don't expect.** The procedure doc carries the contract; per-site customization is verbosity, not behavior.

## See Also

- `skill-doc-pattern.md` — the broader pattern this refines (skills as thin pointers to docs).
- `framework-defined-role-pattern.md` — sibling: one versioned plugin doc authored once and referenced from many *instances*, with each instance's `role.md` a thin pointer. Same "central body, thin callers/instances" shape, applied to roles.
- `auto-pull-mechanism.md` — v13's canonical worked example: one procedure doc, four call sites.
- `slash-command-system.md` — how skill files relate to docs at the top level.
