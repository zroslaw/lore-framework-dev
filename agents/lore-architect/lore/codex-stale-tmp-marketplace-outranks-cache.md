---
lore: 1
type: topic
summary: "B10 closed: Codex identity failures came from a stale v32 tree in ~/.codex/.tmp/marketplaces winning over the installed cache, not from the marketplace source; the precheck never enumerates that root."
parent: lore/codex-engine-capabilities.md
---

# Codex: A Stale `.tmp/marketplaces` Tree Outranks the Installed Cache

Backlog **B10** ("cross-engine lifecycle coverage blocked by local installs") is **closed**, and
its diagnosis was wrong. Codex's marketplace source in `~/.codex/config.toml` already pointed at
`LR_FRAMEWORK_DIR`. Two other things blocked it:

1. **The installed plugin cache lagged** at v43 while the tree under test was v44. Fix:
   `codex plugin add lr@lore-framework`, which re-resolves from the local source.
   **`codex plugin marketplace upgrade` does not work** for a `source_type = "local"` marketplace —
   it errors `marketplace 'lore-framework' is not configured as a Git marketplace`. The harness's
   own `_identity_fix_message` recommends that command, so its remedy text is wrong for this
   install shape.
2. **A five-week-old v32 tree** in `~/.codex/.tmp/marketplaces/lore-framework/` that can win at
   runtime over the installed cache. Identity flapped across four probes: ok → `PLUGIN-VERSION '32'
   != expected '44'` → ok → ok. Moved aside; green 5/5 since, and the first trustworthy Codex arm
   on this machine followed (6/9 modules).

`codex plugin list` reported `installed, enabled 1.44.0` throughout. **The install record is not
what the runtime resolves** — and its VERSION column is the cache while its PATH column is the
source, so reading the row as one fact makes a stale install look like a stale source tree.

## Two harness gaps this exposes

- The Codex identity precheck reads the config source and `plugins/cache/*/VERSION`. It **never
  enumerates `.tmp/marketplaces/`**, so the deterministic check passes while the engine loads
  another tree — a gate that cannot see the thing it gates
  ([a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md), sibling form).
- Identity is probed **once per suite** and the verdict token is inherited by every module, so a
  mid-run substitution is invisible. A single flap makes the whole arm uninterpretable after the
  fact. Re-probe per module, or record the probe per module.

**Cost of not knowing this:** a `test_lore_v1` failure under a substituted v32 plugin looked exactly
like a v44 regression in the new `preflight --agent-dir` upward search (agent not found,
`available_agents` empty). It cleared once identity was verified.

## See Also

- [lifecycle-harness-plugin-identity-unverified.md](lifecycle-harness-plugin-identity-unverified.md)
- [cursor-cloud-plugin-rehydrates-over-plugin-dir.md](cursor-cloud-plugin-rehydrates-over-plugin-dir.md) — same shape on Cursor.
