# Product name: "Lore Agents" (the brand over the engine)

The product/brand name is **"Lore Agents"** — user decision (2026-07-17), "more catchy than 'framework'". Applied in `lore-framework` commit `84948e8`.

The distinction that governs every naming call: **"Lore Agents" is the product; the lore framework is the engine underneath.** Adopter-facing surfaces carry the product name; the machinery keeps its working names.

## Scope boundaries (deliberate, settled — do not "fix" as inconsistencies)

**Renamed to "Lore Agents":**
- All adopter-facing doc titles and intros — README H1 + tagline ("AI coding agents with persistent, team-shared memory"), QUICKSTART, FIRST-STEPS references, the INSTALL-CLAUDE/CODEX/CURSOR H1s and preambles, `PRIVACY.md`, `MARKETPLACE.md`.
- Every engine manifest's `displayName` + description: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (top-level + `lr` entry descriptions), `.codex-plugin/plugin.json` (`interface.displayName`, short/long descriptions), `.cursor-plugin/plugin.json`, `.agents/plugins/marketplace.json` (`interface.displayName`). The Claude `displayName` is now `"Lore Agents"` (was `"Lore"`).

**NOT renamed (the engine keeps its names):**
- The GitHub repo name `lore-framework`.
- The marketplace name `lore-framework`.
- The plugin id `lr`.
- Internal `docs/` prose that refers to "the lore framework" as the machinery.

## Copy-sync invariant

Canonical description copy lives in `MARKETPLACE.md`. The Codex manifest `longDescription` must match its "Long description" **verbatim** — a review round caught drift there; keep them byte-identical whenever either changes.

## Grammar convention

Treat "Lore Agents" as a **singular product name** ("Lore Agents is a local, git-backed plugin…", "Lore Agents gives…") except where the sentence genuinely refers to the agents ("Lore Agents turns coding agents into…" reads fine either way).

## Name-collision watch (added 2026-07-20)

The 2026-07-20 competitive re-survey found "Lore" is now a contested name in exactly this
niche: **amarlearning/lore** ("institutional memory for your codebase"), **BYK/loreai**, and
**getlore-ai** all use "Lore" as or within their project name. None is dominant yet (largest
is loreai at 85 stars), but it's a standing consideration for discoverability/SEO of any
"Lore Agents" advertising and for the brand decision itself — re-check on future naming
discussions or before public marketplace submission. See `similar-projects-landscape.md`
§ Name collision and `positioning-triad-differentiation.md`.

## See Also

- `engine-marketplace-readiness.md` — where the manifest `displayName`/description fields live per engine.
- `plugin-distribution.md` — repo/marketplace/plugin-id names that stay unchanged.
- `terminology-domain-collision-trap.md` — the sibling terminology-hygiene discipline for adopter-facing prose.
- `paste-link-installer-doc-genre.md`, `onboarding-doc-narrative-pattern.md` — the adopter-facing docs that carry the product name.
- `similar-projects-landscape.md`, `positioning-triad-differentiation.md` — the name-collision finding and the positioning framing it bears on.
