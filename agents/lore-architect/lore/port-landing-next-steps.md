# Port Landing — Staged Work + Next-Session Plan

State as of 2026-07-05. The **subagent-adapter pass is done**: a full `docs/engines/` engine-profile binding is IMPLEMENTED in the sibling `lore-framework-codex` build and VALIDATED end-to-end on real Codex (profile selection, framework-root self-location, native `spawn_agent` fan-out for recall + merge with the host-reads-steps override). See `docs-engines-convention.md`, `codex-port-validated-end-to-end.md`. What remains is **landing** it onto the canonical `lore-framework` plus two still-staged Claude-side change sets. The real `lore-framework/` plugin is still untouched — the deliberate choice (option a) to keep the live plugin stable and land the whole port as one reviewed, tested change set holds. This is the concrete resume point for `multi-engine-portability-direction.md`.

## Done: the `docs/engines/` engine-profile binding (implemented + Codex-validated)

Built in the `lore-framework-codex` sibling (no git remote) and proven on real `codex exec`:
`docs/engines/{claude,codex}.md` with all five bindings, Boot Step-0 engine selection, per-spawn-site
"Engine note" pointers. Recall + merge fan-out ran via native `spawn_agent`; framework-root
self-located with zero leak. Only gap = `.git`-sandbox commit block. Full shape in
`docs-engines-convention.md`; validation in `codex-port-validated-end-to-end.md`; design record
`workdir/codex-binding-design.md`.

## Ready to apply to the real `lore-framework` (validated on Claude/haiku)

1. **framework-root-full** — `${CLAUDE_PLUGIN_ROOT}` → `<framework-root>` across `docs/` + `skills/` (41 files), self-location line into 22 `SKILL.md`, generic resolution paragraph in `agent-boot.md`. See `framework-root-self-location-validated.md`. (Also independently re-validated on real Codex.)
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

## Next dedicated session (landing onto the canonical framework)

The subagent-adapter *design + build* is done (in `lore-framework-codex`); the remaining work is
consolidation onto the real plugin:

1. **Fold the `docs/engines/` convention back into canonical `lore-framework`** — port the Boot Step-0
   engine selection, the two profiles, and the per-spawn-site "Engine note" pointers from the
   `lore-framework-codex` build. This subsumes the old subagent-spawn binding item (Tier B nucleus,
   66 sites / 12 fan-out docs; see `claude-coupling-inventory-and-port-tiers.md`).
2. `CLAUDE.md` → `AGENTS.md` memory-file binding — **update `test_18_init` in lockstep** (it asserts `CLAUDE.md`).
3. Trivial timeout-prose neutralization (`auto-pull.md`, `conventions.md`).
4. Apply framework-root-full + defer-clarity + the above to the **real** framework, run the **full
   suite against the real framework** (not the copy), and commit (show tests before pushing).
5. **Wire a `codex` driver into `harness.py`'s `run_engine()`** (incl. the one-time
   marketplace/plugin-install setup and the rollout-log-based spawn assertions) so the Codex path is
   in the automated suite, not just manual — see `codex-testing-methodology.md`.
6. **Decide the `.git`-sandbox commit handling** for Codex finalize (run with `.git` writable, or
   document the uncommitted-hand-off gate) — see `codex-git-sandbox-blocks-dotgit.md`.

## Also produced this session (in workdir)

- `workdir/first-steps-codex.md`, `workdir/first-steps-cursor.md` — manual trial guides (install + boot) for running the framework on each engine in separate sessions. Codex path is verified; Cursor is "should work, unconfirmed" (blocked on account quota — see `cursor-agent-cli-probe-findings.md`).
- `workdir/claude-specific-inventory.md` — the full coupling inventory behind `claude-coupling-inventory-and-port-tiers.md`.

## Harness note for next time

`LR_FRAMEWORK_DIR` (point at a modified copy), `LR_TEST_MODEL=haiku`, and the canary mechanism together make a clean "does a doc change break/clarify execution?" loop — no new test code needed. Wiring an actual `codex` driver into `run_engine()` is still open. See `lifecycle-testing-harness.md`.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction this resumes.
- `docs-engines-convention.md` — the implemented engine-profile layer to fold back in.
- `codex-port-validated-end-to-end.md` — the end-to-end Codex validation that closed the subagent pass.
- `codex-git-sandbox-blocks-dotgit.md` — the git-sandbox gate to resolve during landing.
- `codex-testing-methodology.md` — the manual method; item 5 wires it into the automated harness.
- `framework-root-self-location-validated.md`, `haiku-ambiguity-detector.md` — the two staged Claude-side change sets.
- `claude-coupling-inventory-and-port-tiers.md` — the tiered work map the landing executes.
- `lifecycle-testing-harness.md` — the harness + `LR_FRAMEWORK_DIR`/`LR_TEST_MODEL` loop.
