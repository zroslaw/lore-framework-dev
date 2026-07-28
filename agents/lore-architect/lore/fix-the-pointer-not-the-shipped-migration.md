# Fix the Pointer, Not the Shipped Migration

While reviewing the v32 shortcut-bootstrap implementation, found (independently, then corroborated
by Cursor from a separate read — see `independent-engine-review-catches-structural-blind-spots.md`)
that `docs/check.md`'s remedy text for a legacy shortcut format told users to run `/lr:update`
because "migration 6 regenerates them" — but migration 6's own template still writes the exact
absolute-path form v32 exists to eliminate. Running the suggested fix would have silently re-broken
what it just healed.

## The fix that landed

**Not** rewriting `migrations/6.md`. Instead, leave the shipped migration as the historical record
of what that version did, and correct the *pointer* — `check.md` now explicitly warns "do not run
migration 6: its historical template writes the cache-vulnerable absolute boot path this check
rejects" and points only at re-registration as the remedy.

## Operational rule

When a shipped migration's output becomes wrong for a *new* case, don't retroactively rewrite the
migration — migrations are a per-version historical record, not living code (see
`placeholder-vocabulary.md` for the adjacent case: `migrations/2.md`'s frozen old-vocabulary
placeholders exist specifically to content-match historical files, and rewriting them would break
that matching). Fix whatever *points at* the migration instead: check remedies, doctor ailments,
onboarding docs. Only write a brand-new migration if the new case genuinely needs automated repair
that the doctor/re-register path can't cover.

## Why this generalizes

A migration's job is to describe what *that version* did to reconcile a repo — it's frozen the
moment it ships, same as a release note (`versioning-release-types.md` § In-band BETA refinement
draws the same freeze line for release notes). The **live** surface is always something that reads
or references the migration — a check, a doctor ailment, a piece of prose — never the migration
file itself. When a historical artifact and a live pointer disagree, the live pointer is what's
wrong, because it's the only one of the two that's still making a claim about the present.

## See Also

- `versioning-release-types.md` — the v32 entry records this exact fix (`migrations/6.md` left
  unmodified, `check.md` corrected) as part of the shortcut-bootstrap release scope.
- `placeholder-vocabulary.md` — the adjacent "don't rewrite historical migration content" case,
  for a different reason (content-matching against bytes already on disk, not staleness).
- `independent-engine-review-catches-structural-blind-spots.md` — how this bug was actually found
  (two engines, separate reads, same finding).
- `consistency-checks.md` — where a future `/lr:check` rule could assert migration-vs-pointer
  consistency mechanically, if this class of bug recurs.
