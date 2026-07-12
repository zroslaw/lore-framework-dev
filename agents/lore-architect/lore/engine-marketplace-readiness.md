# Engine Marketplace Readiness & Visibility

How to get `lr` onto each engine's plugin marketplace with good discoverability, and where we stand.
Grounded in official docs (code.claude.com, cursor.com/docs, learn.chatgpt.com/codex) 2026-07-12.
This is the "are we marketplace-ready?" map; keep engine-specific operational detail in the engine hubs.

## Claude Code — most mature path; we're close

- **Manifest** `.claude-plugin/plugin.json`: only `name` is strictly required. Visibility/metadata fields (all recognized): `displayName` (picker name, v2.1.143+, falls back to `name`), `description`, `keywords` (discovery tags), `homepage`, `repository`, `license`, `author`, `$schema` (editor autocomplete). Unrecognized fields are ignored (warn under `--strict`). **Enriched 2026-07-12** — added `$schema`, `displayName: "Lore"`, `homepage`, `keywords`.
- **Marketplace file** `.claude-plugin/marketplace.json` (we have it): `source` must be `"./"` (trailing slash). Entry carries name/source/description/version/repository/license.
- **Public marketplaces:**
  - `claude-plugins-official` — curated by Anthropic, **no application process**; Anthropic decides at its discretion.
  - `claude-community` — public community marketplace; third-party submissions land after review. Users add via `/plugin marketplace add anthropics/claude-plugins-community`, install as `@claude-community`.
- **Submit to community:** in-app forms — claude.ai (`claude.ai/admin-settings/directory/submissions/plugins/new`, needs Team/Enterprise + directory-mgmt access) **or** Console (`platform.claude.com/plugins/submit`, works for individual authors). Run **`claude plugin validate --strict`** locally first; the review pipeline runs the same check + automated safety screening. Approved plugins are pinned to a commit SHA in `anthropics/claude-plugins-community`; CI bumps the pin as you push; catalog syncs nightly.
- **Version/update:** explicit `version` pins → users only update when it's bumped (our `1.<VERSION>.0` discipline fits exactly). Omit it and the commit SHA is used (every commit = new version). Users refresh a marketplace with `/plugin marketplace update`; in-session `/reload-plugins`.
- **Validation (2026-07-12):** `claude plugin validate ./lore-framework --strict` — **both layers pass.** It validates the *marketplace* manifest when a `marketplace.json` is present (to strict-check the plugin manifest alone, validate a copy of the dir without the marketplace file). The one strict failure was the marketplace missing a top-level `description` (recognized optional field) — added and re-validated green. `--strict` treats unrecognized fields + missing metadata as errors; the review pipeline runs the same check.
- **Reserved marketplace names:** Claude reserves a set for Anthropic (`claude-community`, `claude-plugins-official`, `claude-plugins-community`, `anthropic-*`, `first-party-plugins`, `healthcare`, …) and re-checks on every load — a marketplace named into a reserved slot stops loading as "untrusted source." Our `lore-framework` is safe; never rename into that set.
- **Readiness verdict:** manifest + marketplace.json valid and **strict-clean**; visibility fields present. Remaining: submit via Console form. Low effort.

## Cursor — structurally ready; needs a logo + auto-refresh validation

- **Layout:** single-plugin repo → root `.cursor-plugin/plugin.json`, **omit** the Cursor `marketplace.json` (that's a multi-plugin-monorepo thing). Confirmed against the Cursor plugin-template README.
- **Manifest best-practice fields:** `name` (kebab regex `^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$` — `lr` passes), `displayName`, `description`, `version`, `author`, `license`, `keywords`, `logo` (SVG, relative path). **Applied 2026-07-12** — added `displayName`, `keywords`, `logo: "assets/logo.svg"` + committed `assets/logo.svg`. Skills declared via `"skills": ".cursor-skills/"` path-override (validator-supported).
- **Skill frontmatter:** each `.cursor-skills/*/SKILL.md` needs `name` + `description` (validator-required) — all 30 conform.
- **Submission:** send repo link to the Cursor team (Slack / email per template docs); `node scripts/validate-template.mjs` targets the monorepo layout, so it won't run 1:1 against our single-plugin repo (expected).
- **Update model:** see `cursor-plugin-distribution-update-model.md`. Seamless propagation needs a **team marketplace + Auto Refresh + Cursor GitHub App**; unvalidated for us today.

## Codex — DISCREPANCY: our lore vs current official spec

- **Our port lore** (`plugin-distribution.md`, `codex-cli-plugin-loading-findings.md`) says Codex installs via `codex plugin marketplace add zroslaw/lore-framework` + `codex plugin add lr@lore-framework`, consuming the **`.claude-plugin/marketplace.json`** — validated end-to-end at port time.
- **Current official Codex build-plugins spec** (learn.chatgpt.com/codex/build-plugins) describes a **distinct packaging**: required manifest `.codex-plugin/plugin.json` (fields: `name`, `version`, `description` required; `author`/`homepage`/`repository`/`license`/`keywords`/`skills`/`mcpServers`/`apps`/`hooks`/`interface` optional — `interface` holds `displayName`/`category`/`logo`/`screenshots`/etc. for install-surface visibility), marketplace file at `.agents/plugins/marketplace.json` (repo) or `~/.agents/plugins/marketplace.json`, commands `codex plugin marketplace add owner/repo` + a `/plugins` in-CLI browser, install cache `~/.codex/plugins/cache/$MARKETPLACE/$PLUGIN/$VERSION/`.
- **We have NO `.codex-plugin/` and NO `.agents/plugins/marketplace.json`.** So under the *current* spec we are not formally packaged for Codex.
- **Do not assert either way.** Recalled port lore reflects what was true when written; the docs summary came from a fast model. **Verify on a real current Codex build** which manifest Codex actually loads before building `.codex-plugin/` or claiming Codex marketplace-readiness (`verify-before-acting-on-suspected-bugs.md`). If the formal `.codex-plugin/` packaging is now required, that's a net-new deliverable (manifest + `interface` visibility block + marketplace.json + lifecycle-harness validation), not a tweak.

## Cross-cutting visibility levers (all engines)

`displayName` (human name in pickers), `description` (shown when browsing), `keywords`/tags (search), `logo` (marketplace cards — Cursor + Codex `interface`; Claude has no logo field today), `homepage`/`repository` (attribution + docs), a good top-level `README.md`, and an accurate `version` for controlled updates.

## See Also

- `cursor-plugin-distribution-update-model.md` — Cursor update/auto-refresh detail
- `plugin-distribution.md` — the base distribution overview (Claude/Codex install commands)
- `plugin-manifest-versioning.md` — the `1.<VERSION>.0` three-manifest discipline; check #19
- `claude-engine-capabilities.md`, `cursor-engine-capabilities.md`, `codex-engine-capabilities.md`
- `verify-before-acting-on-suspected-bugs.md` — why the Codex packaging gap is a verify-first item
