# Engine Marketplace Readiness & Visibility

How to get `lr` onto each engine's plugin marketplace with good discoverability, and where we stand.
Grounded in official docs (code.claude.com, cursor.com/docs, learn.chatgpt.com/codex) 2026-07-12.
This is the "are we marketplace-ready?" map; keep engine-specific operational detail in the engine hubs.

## Claude Code — most mature path; we're close

- **Manifest** `.claude-plugin/plugin.json`: only `name` is strictly required. Visibility/metadata fields (all recognized): `displayName` (picker name, v2.1.143+, falls back to `name`), `description`, `keywords` (discovery tags), `homepage`, `repository`, `license`, `author`, `$schema` (editor autocomplete). Unrecognized fields are ignored (warn under `--strict`). **Enriched 2026-07-12** — added `$schema`, `displayName`, `homepage`, `keywords`. The `displayName` is now `"Lore Agents"` (rebrand, commit `84948e8`; was `"Lore"`) — see `lore-agents-product-name.md` for the product-vs-engine naming split that governs every manifest string.
- **Marketplace file** `.claude-plugin/marketplace.json` (we have it): `source` must be `"./"` (trailing slash). Entry carries name/source/description/version/repository/license.
- **Submission-support bundle:** public review needs reviewer-facing metadata, not only runtime manifests. The root `MARKETPLACE.md` carries copy/paste directory fields for Claude Code, Codex, and Cursor; root `PRIVACY.md` exists because the Claude Console submission form requires a privacy policy URL. Treat these as submission-support files on `main`, separate from the runtime release tag/commit.
- **Public marketplaces:**
  - `claude-plugins-official` — curated by Anthropic, **no application process**; Anthropic decides at its discretion.
  - `claude-community` — public community marketplace; third-party submissions land after review. Users add via `/plugin marketplace add anthropics/claude-plugins-community`, install as `@claude-community`.
- **Submit to community:** in-app forms — claude.ai (`claude.ai/admin-settings/directory/submissions/plugins/new`, needs Team/Enterprise + directory-mgmt access) **or** Console (`platform.claude.com/plugins/submit`, works for individual authors). Run **`claude plugin validate --strict`** locally first; the review pipeline runs the same check + automated safety screening. Approved plugins are pinned to a commit SHA in `anthropics/claude-plugins-community`; CI bumps the pin as you push; catalog syncs nightly.
- **Version/update:** explicit `version` pins → users only update when it's bumped (our `1.<VERSION>.0` discipline fits exactly). Omit it and the commit SHA is used (every commit = new version). Users refresh a marketplace with `/plugin marketplace update`; in-session `/reload-plugins`.
- **Validation (2026-07-12):** `claude plugin validate ./lore-framework --strict` — **both layers pass.** It validates the *marketplace* manifest when a `marketplace.json` is present (to strict-check the plugin manifest alone, validate a copy of the dir without the marketplace file). The one strict failure was the marketplace missing a top-level `description` (recognized optional field) — added and re-validated green. `--strict` treats unrecognized fields + missing metadata as errors; the review pipeline runs the same check.
- **Reserved marketplace names:** Claude reserves a set for Anthropic (`claude-community`, `claude-plugins-official`, `claude-plugins-community`, `anthropic-*`, `first-party-plugins`, `healthcare`, …) and re-checks on every load — a marketplace named into a reserved slot stops loading as "untrusted source." Our `lore-framework` is safe; never rename into that set.
- **Readiness verdict:** manifest + marketplace.json valid and **strict-clean**; visibility fields present; `MARKETPLACE.md` + `PRIVACY.md` make the Console form copy/paste-ready. The v25 plugin tag (`lr--v1.25.0`) is pushed; remaining step is Console form submission. Low effort.

## Cursor — structurally ready; needs auto-refresh validation

- **Layout:** single-plugin repo → root `.cursor-plugin/plugin.json`, **omit** the Cursor `marketplace.json` (that's a multi-plugin-monorepo thing). Confirmed against the Cursor plugin-template README.
- **Manifest best-practice fields:** `name` (kebab regex `^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$` — `lr` passes), `displayName`, `description`, `version`, `author`, `license`, `keywords`, `logo` (relative path). **Applied 2026-07-12** — added `displayName`, `keywords`, and `logo: "assets/logo-512.png"`; v25 ships PNG logo assets and removes the earlier SVG placeholder. Skills declared via `"skills": ".cursor-skills/"` path-override (validator-supported).
- **Skill frontmatter:** each `.cursor-skills/*/SKILL.md` needs `name` + `description` (validator-required) — all 30 conform.
- **Submission:** send repo link to the Cursor team (Slack / email per template docs); `node scripts/validate-template.mjs` targets the monorepo layout, so it won't run 1:1 against our single-plugin repo (expected).
- **Update model:** see `cursor-plugin-distribution-update-model.md`. Seamless propagation needs a **team marketplace + Auto Refresh + Cursor GitHub App**; unvalidated for us today.

## Codex — native packaging resolved in v25

- **Legacy fallback still works:** Codex can install `lr` through `.claude-plugin/marketplace.json`,
  so earlier port lore was not wrong.
- **Native marketplace preferred when present:** on `codex-cli 0.142.5`, registering a real local
  checkout with `codex plugin marketplace add <repo>` prefers `.agents/plugins/marketplace.json`
  when that file exists.
- **Version-bearing manifest:** `.codex-plugin/plugin.json` is the Codex plugin manifest and reads
  `version: 1.<VERSION>.0`. It joins check #19's four version-bearing manifests.
- **Marketplace file:** `.agents/plugins/marketplace.json` carries marketplace policy/source
  metadata but no per-plugin version, so it is structurally validated by live install testing rather
  than the manifest-version check.
- **Empirical parser details:** a root-source entry works with
  `source: { source: "local", path: "./" }`; the valid no-auth policy enum is `ON_USE`
  (`ON_FIRST_USE` is rejected by the real parser).
- **Operating rule:** for future Codex packaging questions, register the real checkout, then run a
  clean remove/add cycle. Treat docs summaries as hypotheses until the live parser accepts the file.

## Cross-cutting visibility levers (all engines)

`displayName` (human name in pickers), `description` (shown when browsing), `keywords`/tags (search), `logo` (marketplace cards — Cursor + Codex `interface`; Claude has no logo field today), `homepage`/`repository` (attribution + docs), a good top-level `README.md`, and an accurate `version` for controlled updates.

## Submission identity discipline

Keep three identities separate when describing readiness:

- **Runtime release identity:** the plugin tag and runtime commit users/installers consume, e.g. `lr--v1.25.0` at runtime commit `09fe4f0`. **Derive the recorded runtime commit from the tag**, never from scrollback — see `release-commit-hash-from-tag.md` (the v26 orphaned-SHA incident).
- **Submission-support metadata:** reviewer-facing files such as `MARKETPLACE.md` and `PRIVACY.md` on `main`; these can exist to support forms without redefining the runtime release.
- **Verified publication status:** per-engine facts about where the plugin is actually published or validated. Claude Console submission-ready, Codex native repo packaging-ready, and Cursor local `--plugin-dir`-ready are not the same as public marketplace publication.

Before a public submission, run `claude plugin validate --strict`, create/push the Claude plugin tag with `claude plugin tag --push`, ensure `MARKETPLACE.md` has current directory copy, and ensure `PRIVACY.md` is reachable from the repository root. Do not claim Codex or Cursor public marketplace publication until the live product's submission/distribution path has been verified.

## See Also

- `cursor-plugin-distribution-update-model.md` — Cursor update/auto-refresh detail
- `plugin-distribution.md` — the base distribution overview (Claude/Codex install commands)
- `plugin-manifest-versioning.md` — the `1.<VERSION>.0` four-manifest discipline; check #19
- `lore-agents-product-name.md` — the "Lore Agents" product name that fills the `displayName`/description fields
- `release-commit-hash-from-tag.md` — derive the recorded runtime release commit from the tag, not scrollback
- `claude-engine-capabilities.md`, `cursor-engine-capabilities.md`, `codex-engine-capabilities.md`
- `verify-before-acting-on-suspected-bugs.md` — why the Codex packaging gap is a verify-first item
