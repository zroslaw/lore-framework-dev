**An orchestration pattern where a thin skill routes user-described cases against an open-ended catalog of named ailments, each with its own atomic topic and remedy.** Landed with `/lr:doctor` in v12.

A skill-doc-pattern variant — refines `skill-doc-pattern.md` along the case-decomposition axis (open-ended, additive) rather than the phase-decomposition axis (sequential, fixed) used by `/lr:finalize` since v8.

## The Pattern

An orchestrator doc (e.g. `docs/doctor.md`) holds:

- **Matching procedure** — how to route a user-described case to a member topic.
- **Catalog index** — registered members, by stable slug, organized into categories.
- **Authoring schema** — the four-section structure each member topic must use.
- **Scope gate** (universality test) — what belongs in the catalog vs what doesn't.

Each member is its own atomic topic at `docs/<orchestrator-prefix>-<slug>.md` (e.g. `doctor-stale-plugin-cache.md`), with the prefix matching the orchestrator's namespace so members are visually grouped on disk.

Adding a member is a **doc-only edit**: write the topic, register it in the orchestrator's catalog. No script changes, no plugin reload (other than the cache refresh that any doc-affecting change requires — see `cache-clear-footer-convention.md`).

The catalog **grows by accretion** — members are added when real-world failures (or real-world cases more broadly) get distilled into topics. Premature population is discouraged; the universality gate prevents overflow.

## How It Differs from Prior Orchestration Patterns

The v8 orchestration refinement (`skill-doc-pattern.md`) decomposes a skill **by phase** — `/lr:finalize` = reflect + merge + summarize + commit-push. The phases are sequential, fixed, and exhaustive.

The v12 ailment catalog decomposes **by case** — `/lr:doctor` matches a symptom against an open-ended catalog whose membership grows over time. The cases are pluggable, additive, and never exhaustive.

Both share: thin SKILL.md → orchestrator doc → sub-mechanism docs. Both are valid skill-doc-pattern variants; they decompose along different axes.

## Where the Pattern Reuses

The pattern fits any skill that:

- Routes to a known-fix when the case is in the catalog.
- Falls back to manual investigation + new-topic-during-finalization when it isn't.
- Should accumulate institutional wisdom from real usage rather than be designed exhaustively up-front.

Plausible future uses:

- Onboarding-doc anti-patterns (catalog of known terminology/framing traps).
- Workspace-sync conflict types (each conflict class an ailment, fix encoded).
- Common merge-conflict shapes during finalization (with reconciliation recipes).

## Universality Gate

A member belongs in a catalog only if the ailment can hit any user of the framework regardless of repo/host/workflow specifics. Repo-specific or workflow-specific issues belong in agent lore or specialist agents (reachable via `/lr:consult` / `/lr:attach`), not in a framework-distributed catalog. See `framework-scope-vs-agent-scope.md`.

The scope gate is what keeps an open-ended catalog from drifting into a dumping ground.

## Operational Guidance

When designing a new framework skill, ask whether the cases are exhaustive (phase decomposition) or open-ended (case decomposition). If open-ended:

1. Write the orchestrator doc with the four sections (matching, catalog, authoring schema, scope gate).
2. Ship with one or two seed members — the failure modes that motivated the skill — and let the catalog grow from real usage.
3. Don't try to enumerate cases in advance. The diagnostic is "if I keep finding myself wanting to add cases hypothetically, I'm violating the accretion principle."
4. Member topics follow `<orchestrator-prefix>-<slug>.md` for disk-level visual grouping.

## See Also

- `skill-doc-pattern.md` — the parent pattern this refines; phase-decomposition is the sibling variant.
- `naming-foundational-principles.md` — the meta-rule that motivated naming this pattern.
- `framework-scope-vs-agent-scope.md` — the principle the universality gate applies.
- `cache-clear-footer-convention.md` — the v12 convention that landed alongside the first ailment catalog.
- `feedback-don-t-defer-completable-scope.md` — discipline for adding catalog members at the moment they're discovered, not deferring.
