---
lore: 1
type: topic
summary: "Reading an engine's shipped JavaScript answers questions its docs are silent on, but the finding carries a grade — ran it / read the code / read the docs — and an undocumented route never goes into a contract like an install doc."
parent: lore-context.md
---

# Reading an Engine's Shipped Bundle Is Real Evidence — at a Stated Grade

Where an engine's docs are silent, its shipped JavaScript answers. In one session this yielded four
facts Cursor documents nowhere: that no `plugin install` CLI subcommand exists, that install is a
server-side RPC, that project-scope plugin config lives in `.cursor/settings.json` with a specific
entry shape, and an undocumented `plugin/add` deeplink route.

**Technique.** `grep -rhoE` over the version directory for path literals
(`"\.cursor"\s*,\s*"[^"]+"`), RPC message names, and user-visible strings, then walk the minified
call site by hand with a small Python script. A user-visible error string is the best anchor — it
names the file the code is about (`".cursor/settings.json contains syntax errors"` is what pinned
Cursor's writer).

## State the grade

Three tiers, and they are not interchangeable:

1. **Ran it** — a command executed and its output observed. Strongest.
2. **Read the shipped code** — the mechanism is real, but nothing proves the engine reaches that
   path in the configuration you care about.
3. **Read the docs** — weakest for engine internals; they were silent or wrong on every point above.

v43 ships **tier 2** for the Cursor project-settings load surface. That is recorded as *unverified*
in `docs/engines/cursor.md` § Load surfaces and in the release notes, rather than being reported at
the confidence the code reading felt like.

## The corresponding restraint: an undocumented finding does not go into a contract

The `plugin/add` deeplink is real and I could have written it into `INSTALL-CURSOR.md`. An install
doc is a **promise**; an undocumented route inside one is an unmarked liability that vanishes on a
Cursor release. It stays out until it is tier 1.

**And prefer probing the engine over believing a doc** — including the engine's own. Cursor's CLI
tip prints `use /plugins in interactive mode`; the working command is `/plugin`. The tool was wrong
about itself, and a screenshot of a real run settled it.

## See Also

- [codex-shortcuts-are-workspace-local.md](codex-shortcuts-are-workspace-local.md) — same reflex,
  earlier instance: probe before writing a limitation into four docs.
- [graduated-verification-confidence.md](graduated-verification-confidence.md) — the reporting side
  of the same honesty.
- [fetch-volatile-facts-live-not-memory.md](fetch-volatile-facts-live-not-memory.md),
  [measurement-records-name-their-environment.md](measurement-records-name-their-environment.md)
- [cursor-plugin-install-is-account-side.md](cursor-plugin-install-is-account-side.md),
  [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md) — what this
  technique produced.
