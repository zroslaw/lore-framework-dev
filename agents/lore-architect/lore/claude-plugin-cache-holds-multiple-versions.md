---
lore: 1
type: topic
summary: "Claude's marketplace plugin cache keeps several versioned directories at once, so \"the installed skill\" is ambiguous; resolve <framework-root> from the path the engine printed as a skill base directory, never by picking the newest."
parent: lore/claude-engine-capabilities.md
---

# Claude's Plugin Cache Holds Several Versions At Once

`~/.claude/plugins/cache/lore-framework/lr/` accretes **one directory per installed version** and
does not prune. On 2026-08-31 it held `1.41.0`, `1.42.0` and `1.43.0` side by side, alongside three
`plugins-*-backup.*` trees, the workspace checkout, and a worktree — nine hits for
`find … -path '*/skills/boot/SKILL.md'`.

This makes the phrase *"the `SKILL.md` for the **installed** `/lr:boot` skill"* — the wording every
generated per-agent shortcut uses (`docs/engines/claude.md` § Registered shortcut bootstrap) —
ambiguous the moment more than one version is cached.

## The failure it produced

I resolved `<framework-root>` by taking the **highest version number** from the `find` output:
`1.43.0`. The whole session's boot ran from there — `agent-boot.md`, `version-check.md`, and the
upgrade that stamped `lore-framework-dev` from 42 to 43.

Later the user invoked `/lr:style`, whose engine-supplied header reads:

```
Base directory for this skill: .../plugins/cache/lore-framework/lr/1.42.0/skills/style
```

The engine dispatches from **1.42.0**. The session had booted from a tree the engine does not use.

## Why picking the newest is wrong in principle

Which version the engine dispatches is **a fact about the running environment**, and it is directly
observable: every slash-command invocation prints its own base directory. Choosing by version number
derives an answer that was available to be read — the same error as
[models-copy-what-they-should-compute.md](models-copy-what-they-should-compute.md), and the sibling
of [engine-profile-must-be-observed-not-believed.md](engine-profile-must-be-observed-not-believed.md):
a binding must not be selected by the thing it binds.

Newest is also not a safe heuristic in the other direction. The cache can hold a version *ahead* of
what is enabled, so "newest" can silently mean "not installed at all".

## Operational guidance

- When resolving `<framework-root>` from a shortcut and `find` returns **more than one** candidate
  under the plugin cache, do not take the highest version. Prefer the path the engine itself last
  printed as a skill base directory, and say in one line which root you used and why.
- With no dispatched path yet observed, report the ambiguity at boot rather than choosing silently.
  A boot off the wrong version is invisible in the boot report — every field still renders.
- **Check before trusting a boot-time upgrade.** The version stamped into a lore agent repo comes
  from whichever `VERSION` the booting session resolved, so a boot off a newer-than-installed cache
  stamps the repo ahead of the plugin the user actually runs.
- A cache clear (`rm -rf ~/.claude/plugins/cache/lore-framework/`) collapses the ambiguity as a side
  effect, which is one more reason the cache-clear footer earns its place on cache-affecting
  releases ([cache-clear-footer-convention.md](cache-clear-footer-convention.md)).

## Candidate guardrail

`lr-core preflight` already selects the engine profile deterministically and is the natural place to
**enumerate every plugin-cache version present and flag the multi-version case**, rather than leaving
the executor to guess from a `find`. Point-of-use beats recorded lore
(`point-of-use-guardrails-beat-recorded-lore.md`) — this topic protects nobody at the moment a
shortcut fires.

## See Also

- [framework-root-self-location-validated.md](framework-root-self-location-validated.md) §
  *Operational trap* — the same observable shape (two roots in one session) from a **different**
  cause: a manual boot instruction versus later slash-command dispatch. This topic is the
  cache-internal cause.
- [ephemeral-session-plugin-snapshot-topology.md](ephemeral-session-plugin-snapshot-topology.md) — a
  third cause on one host flavor: a per-session snapshot of the whole bundle.
- `claude-engine-capabilities.md` — the engine hub this sits under.
