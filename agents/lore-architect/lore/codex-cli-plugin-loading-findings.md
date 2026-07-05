# Codex CLI — Plugin Loading & Boot Findings (First Empirical Probe)

First hands-on investigation of `codex` (0.142.5) as a port target, ahead of the parked
`workdir/draft-port-codex.md`. Concrete findings from a manual smoke test, not yet wired into
`tests/lifecycle/harness.py`.

## Plugin loading model differs from Claude Code

- **No per-invocation `--plugin-dir`.** Unlike Claude Code's `--plugin-dir <path>` (which
  cursor-agent's own `--plugin-dir` mirrors — see `cursor-agent-cli-probe-findings.md`), codex
  loads plugins via a persistent local install: `codex plugin marketplace add <local-path>`
  registers a marketplace, then `codex plugin add <name>@<marketplace>` installs it into
  `~/.codex/plugins/cache/...`. This is a setup/teardown step, not a flag on `codex exec` — a
  codex branch in `harness.py`'s `run_engine()` needs a one-time install step, not just an extra
  CLI arg.
- **`marketplace.json` compatibility is real, not hypothetical.** Registered lore-framework's
  existing `.claude-plugin/marketplace.json` (written for Claude Code) as a local codex
  marketplace and it parsed natively — zero adaptation needed. `codex plugin add
  lr@lore-framework` installed successfully at version `1.18.0`, all 26 skill directories present
  (incl. `boot`) under the installed path. Concrete evidence for the "packaging, not redesign"
  framing in `multi-engine-portability-direction.md`.

## Repo-driven onboarding contract

Codex onboarding is agent-driven. If a user gives Codex the Lore Framework repository URL and
asks it to install, the agent reads the repository README, runs
`codex plugin marketplace add zroslaw/lore-framework` followed by
`codex plugin add lr@lore-framework`, requests only permissions the commands actually need, and
asks the user to restart Codex after installation. For a local checkout, use its path instead of
the GitHub marketplace identifier. The README must keep this contract short and easy for an agent
to discover; the user should not have to execute a manual setup guide. See
`plugin-distribution.md`.

## Confirmed gap: `${CLAUDE_PLUGIN_ROOT}`

`printf '%s' "$CLAUDE_PLUGIN_ROOT"` returns empty inside a codex exec run — confirms the
predicted `docs/engines/` adapter gap. In this one run the model self-recovered by locating the
installed plugin's doc file directly (`find`/`sed` against
`~/.codex/plugins/cache/lore-framework/lr/<version>/docs/...`) instead of failing outright —
improvisation, not a resolved binding. Don't count on this generalizing; it's exactly the kind of
ambiguity the `docs/engines/` adapter lever is meant to remove.

> **Resolved (2026-07-05).** The `docs/engines/` framework-root binding + Boot Step-0 self-location
> now closes this deterministically — validated end-to-end on real Codex with **zero
> `${CLAUDE_PLUGIN_ROOT}` leak**. See `docs-engines-convention.md`,
> `framework-root-self-location-validated.md`, `codex-port-validated-end-to-end.md`.

## Skill invocation falls through to shell

Inside `codex exec`, `/lr:recall` is not dispatched as a lore skill. It is treated as a shell
command and fails, so the slash-command layer is not reliably active in this engine path.

Operational fallback on Codex is to read `docs/<skill>.md` directly and scan the relevant lore
topics manually. That preserves the knowledge-layer behavior even when the invocation layer is
not wired up — and this is exactly what the `docs/engines/codex.md` **invocation-syntax binding**
now codifies ("skills invoked by reading `docs/<skill>.md` directly when agent-initiated"). See
`docs-engines-convention.md`.

## CLI quirks for the harness driver

- `codex exec` always reads stdin, appending it as a `<stdin>` block even when the prompt is
  passed as an argument (per its own `--help`). Must redirect stdin from `/dev/null` explicitly
  or a scripted invocation can appear to hang waiting on EOF.
- JSONL stdout can be silently buffered — see `headless-cli-smoke-testing-discipline.md` for the
  general lesson this produced (a hard-killed foreground run looked like a total hang;
  backgrounding the identical command showed it had been working the whole time).
- Working invocation recipe, validated against the fixture `harness.py` already uses:
  `codex exec "<prompt>" -C <workspace> -s workspace-write --skip-git-repo-check --json < /dev/null`

## First real result: PASS

Manually ran the equivalent of `test_boot.py`'s `test_01_boot_happy_path` against codex. Both
canaries (`BOOT-CODEWORD`, `CONTEXT-CODEWORD`) printed correctly, auto-pull/version-check/role +
lore-context read all executed faithfully and in order, no commits created, working tree stayed
clean. Not yet wired into `harness.py`'s `run_engine()` — this was a manual smoke test outside
the test suite.

## Next step

Add a `codex` branch to `run_engine()` in `tests/lifecycle/harness.py` (including the one-time
marketplace/plugin-install setup) and run the full `test_boot.py` suite (6 scenarios) against it.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction this probe serves.
- `lifecycle-testing-harness.md` — the harness these findings feed into once wired.
- `cursor-agent-cli-probe-findings.md` — the sibling probe for the other port target.
- `headless-cli-smoke-testing-discipline.md` — the general debugging lesson from this session.
- `docs-engines-convention.md` — the engine-profile layer that resolves the framework-root and invocation-syntax gaps above.
- `codex-port-validated-end-to-end.md` — the later full-lifecycle Codex validation these probes led to.
- `codex-native-multi-agent-subsystem.md` — Codex's native subagent tools (found after these early probes).
- `codex-testing-methodology.md` — the rollout-log ground-truthing method built on top of these CLI recipes.
- `codex-local-plugin-update.md` — how to update a **local-source** marketplace install to a new plugin version (remove + re-add; `upgrade` is Git-only).
- `plugin-distribution.md` — the cross-engine installation entry point and repo-driven Codex contract.
