# Port Landing — Staged Work + Next-Session Plan

State as of 2026-07-04. Two validated change sets live **only in an isolated scratchpad copy** (`LR_FRAMEWORK_DIR=…/lore-framework-tierA`); the real `lore-framework/` plugin is untouched. Deliberate choice (option a) — keep the live plugin stable and land the whole port as one reviewed, tested change set. This is the concrete resume point for `multi-engine-portability-direction.md`.

## Ready to apply to the real `lore-framework` (validated on Claude/haiku)

1. **framework-root-full** — `${CLAUDE_PLUGIN_ROOT}` → `<framework-root>` across `docs/` + `skills/` (41 files), self-location line into 22 `SKILL.md`, generic resolution paragraph in `agent-boot.md`. See `framework-root-self-location-validated.md`.
2. **defer-clarity fix** — `agent-boot.md` step 3 + two defer points in `version-check.md`: "a deferred upgrade is NOT a boot failure, keep loading the agent." Orthogonal to the port; a genuine robustness win on its own. See `haiku-ambiguity-detector.md`.

## Style skills riding along (built 2026-07-05, uncommitted)

Three user-invoked *style* skills are built and sitting **uncommitted** in `lore-framework/`:
`/lr:plain-language`, `/lr:follow-me` (extracted from lore — canonical def now in the framework), and
`/lr:dialogue`. Files: `skills/{plain-language,follow-me,dialogue}/SKILL.md`,
`docs/{plain-language,follow-me,dialogue}.md`. They are mechanically unrelated to the port, but the
user chose to **ship them together with the codex adoption**. They were deliberately pulled out of
v18's lr-wait release notes — so when the port version is cut, give them a release-notes entry at
that version. `/lr:check` should pass on them (standard thin-pointer shape); the three form a
composable set (sentence-level / turn-level / thinking-direction). Full category writeup in
`style-skills.md`; `follow-me`'s design history stays in `soft-skill-follow-me-mode.md`.

## Next dedicated session (the subagent-adapter pass)

1. Build the `docs/engines/` adapter convention + `docs/engines/claude.md` — the **subagent-spawn binding** (Tier B nucleus, 66 sites / 12 fan-out docs; see `claude-coupling-inventory-and-port-tiers.md`).
2. `CLAUDE.md` → `AGENTS.md` memory-file binding — **update `test_18_init` in lockstep** (it asserts `CLAUDE.md`).
3. Trivial timeout-prose neutralization (`auto-pull.md`, `conventions.md`).
4. Then apply framework-root-full + defer-clarity + the above to the **real** framework, run the **full suite against the real framework** (not the copy), and commit (show tests before pushing).

## Also produced this session (in workdir)

- `workdir/first-steps-codex.md`, `workdir/first-steps-cursor.md` — manual trial guides (install + boot) for running the framework on each engine in separate sessions. Codex path is verified; Cursor is "should work, unconfirmed" (blocked on account quota — see `cursor-agent-cli-probe-findings.md`).
- `workdir/claude-specific-inventory.md` — the full coupling inventory behind `claude-coupling-inventory-and-port-tiers.md`.

## Harness note for next time

`LR_FRAMEWORK_DIR` (point at a modified copy), `LR_TEST_MODEL=haiku`, and the canary mechanism together make a clean "does a doc change break/clarify execution?" loop — no new test code needed. Wiring an actual `codex` driver into `run_engine()` is still open. See `lifecycle-testing-harness.md`.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction this resumes.
- `framework-root-self-location-validated.md`, `haiku-ambiguity-detector.md` — the two staged change sets.
- `claude-coupling-inventory-and-port-tiers.md` — the tiered work map the next session executes.
- `lifecycle-testing-harness.md` — the harness + `LR_FRAMEWORK_DIR`/`LR_TEST_MODEL` loop.
