**Migration / release-notes docs whose changes touch plugin-cached state must include a "Clear Plugin Cache" footer with concrete commands.** Codified in v12 alongside `/lr:doctor`.

The convention's canonical wording lives in `lore-framework/docs/conventions.md` § Migration / Release-Note Authoring. `release-notes/12.md` is the worked example. `docs/version-check.md` § For Framework Authors signposts the same rule from the procedure that authors actually consult when writing release notes.

## Why the Rule Exists

The plugin-cache stale-state failure is **invisible** until the user invokes a missing skill and gets confused. It's also the single failure that can take out the diagnostic tool itself — the v12 chicken-and-egg: `/lr:doctor` is needed to fix the missing-skill problem, but `/lr:doctor` itself can be missing if the cache is stale.

The footer convention puts the fix in the migration's own line of sight — readers don't have to discover `/lr:doctor` after-the-fact. The cache-clear is the single mandatory action for most cache-affecting releases; making it impossible to skim past in the release-notes is the ergonomic correct outcome.

## Triggers — When the Footer Is Required

Include the footer if the version added, removed, renamed, or modified any of:

- A skill (`skills/<name>/SKILL.md` or its directory)
- A `/lr-*` slash command surface
- A bundled script in `scripts/`
- A doc that a SKILL.md points at, where the runtime behavior changes (not just rephrasing)

Skip the footer for purely-informational releases (lore-context conventions, doc rephrasing that doesn't change runtime behavior, framing-only release notes).

## How to Apply

When authoring a new version's release-notes:

1. Read `lore-framework/docs/conventions.md` § Migration / Release-Note Authoring.
2. Decide whether triggers apply. If yes → footer required.
3. Use the canonical wording template; substitute the `<added/removed/renamed>` and `<new/renamed>` slots.
4. **Hoist the section near the top** of the release-notes (immediately after Summary works well; v12 demonstrates this) — not at the bottom where it's easy to miss.
5. **Disambiguate "Migration required: no" from "cache-clear required"** — they're different. Use phrasing like "Repo migration required: no — but a cache-clear is required" when the version is purely additive but cache-affecting.
6. Use the **targeted** cache wipe (`rm -rf ~/.claude/plugins/cache/<plugin-name>/`) before the broader form (`rm -rf ~/.claude/plugins/cache/`) — narrower scope is the default to avoid disrupting unrelated plugins; broader is the fallback.

## Versioning Interaction

The convention exposes a subtle classification: most release-notes-only versions are **also cache-affecting** because they change SKILL.md or its referenced docs. The cache-affecting axis is **orthogonal** to the migration-vs-release-notes axis — a version can be:

- Migration + cache-affecting (typical breaking change).
- Migration-only, no cache (rare; physical file changes that don't touch skills/scripts/SKILL.md docs).
- Release-notes-only + cache-affecting (typical additive feature like v11/v12).
- Release-notes-only, no cache (purely behavioral or framing-only, like v8).

`versioning-release-types.md` records this annotation per-version in its history list, alongside the existing migration/release-notes classification.

## Why Hoist, Not Append

Footer-by-position is misleading — the convention is "include it" plus "place it where readers can't miss it." v12's release notes places Clear Plugin Cache immediately after Summary, before What's New, because it's the single mandatory action and any reader who skims the release notes must see it. Burying it before See Also weakens the convention's purpose.

## Operational Discipline

This convention belongs to the rhythm of every framework version ship. Author the release-notes, evaluate triggers, hoist the footer if any apply, write the disambiguating phrasing, prefer the targeted cache wipe. The discipline is mechanical once internalized; the alternative is repeating v11's failure mode where users hit "skill is missing" with no in-line fix.

The discipline composes with the versioning history backfill discipline: every finalization that lands a `VERSION` bump should both (a) author the release-notes with the footer if applicable, and (b) backfill `versioning-release-types.md` history with the new entry, including the cache-affecting annotation.

## See Also

- `versioning-release-types.md` — the parent topic; carries per-version cache-affecting annotation in its history list.
- `ailment-catalog-pattern.md` — the catalog mechanism. `doctor-stale-plugin-cache.md` is the runtime fix that this convention exists to make discoverable up-front.
- `update-process.md` — the version reconciliation flow this convention augments at the authoring side.
- `framework-scope-vs-agent-scope.md` — universality test confirms this convention belongs in the framework: every adopter is exposed to plugin-cache effects.
