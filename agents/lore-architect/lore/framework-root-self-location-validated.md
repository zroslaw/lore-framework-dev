# `<framework-root>` Self-Location Design — Empirically Validated on Claude

The Phase-0 lever for multi-engine portability — replacing the Claude-only `${CLAUDE_PLUGIN_ROOT}` with a neutral, engine-agnostic term — now has an empirical result, not just a plan. This is the detail topic behind `multi-engine-portability-direction.md` § Architectural levers.

## The design that works

- Replace `${CLAUDE_PLUGIN_ROOT}` with the neutral defined term `<framework-root>` everywhere in `docs/` and `skills/`.
- Define it once, universally: **"the directory that contains the `VERSION` file."**
- Resolve it by **self-location**: a one-line rule injected at the top of every `SKILL.md` body — *"`<framework-root>` is the directory two levels up from this `skills/<name>/SKILL.md` file … resolve it to an absolute path before using it below."*
- Per-engine literal-path fallback (Claude = `${CLAUDE_PLUGIN_ROOT}`, Codex = install-cache path, Cursor = `--plugin-dir`) lives in a `docs/engines/<engine>.md` adapter — but self-location alone was enough on Claude.
- **Bootstrap catch:** this one binding can't hide behind a `Read <framework-root>/docs/…` pointer (chicken-and-egg) — it must be stated inline in the `SKILL.md` the engine already loaded.

## Evidence (2026-07-04, haiku, isolated copy via `LR_FRAMEWORK_DIR`)

- Full lifecycle suite: **18/19** first pass; every subagent fan-out scenario (consult, attach, merge, finalize, recall) **passed** — the host correctly substitutes the *resolved absolute path* into subagent briefs, so the fan-out concern is cleared for the path-resolution dimension (see `claude-coupling-inventory-and-port-tiers.md` for why only the path half of Tier B is thereby de-risked).
- Verbose (`stream-json`) trace proved **self-location, not env-var crutch**: haiku read `<framework-root>/docs/agent-boot.md` at the real copy path and **Read the `VERSION` file to anchor the root** — exactly what the wording pointed to. Clean proof: `${CLAUDE_PLUGIN_ROOT}` only auto-expands when that literal token appears in a path; the converted files never contain it, so the Read tool never received it — haiku *had* to reason out the resolution, and did.
- The only run-time regression seen was a *separate* doc-clarity issue (see `haiku-ambiguity-detector.md`), not a framework-root failure.

## Also validated on real Codex (2026-07-05)

Independently re-confirmed on the second engine: in the `lore-framework-codex` end-to-end run, Boot Step-0 self-located `<framework-root>` and the whole lifecycle executed with **zero `${CLAUDE_PLUGIN_ROOT}` leak** — on Codex the env var is genuinely empty (not just avoided), so self-location was the only path that could work, and it did. Two engines, two model families now agree. See `codex-port-validated-end-to-end.md`, `docs-engines-convention.md`.

## Operational guidance

- Mechanical scale: `${CLAUDE_PLUGIN_ROOT}` was 103 sites (~55% of all Claude coupling — see `claude-coupling-inventory-and-port-tiers.md`) but is the *easiest* coupling to neutralize. 41 files swapped + self-location line into 22 `SKILL.md`.
- Staged in an isolated copy; **not yet applied to the real `lore-framework`** — see `port-landing-next-steps.md`.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction this is Phase-0 of.
- `lifecycle-testing-harness.md` — the harness that validated this (via `LR_FRAMEWORK_DIR` + `LR_TEST_MODEL=haiku`).
- `claude-coupling-inventory-and-port-tiers.md` — the full coupling inventory this framework-root work is the biggest slice of.
- `haiku-ambiguity-detector.md` — the separate doc-clarity regression the same run surfaced.
- `docs-engines-convention.md`, `codex-port-validated-end-to-end.md` — the Codex re-validation of this binding.
- `port-landing-next-steps.md` — the staged-but-unapplied change set and how it lands.
