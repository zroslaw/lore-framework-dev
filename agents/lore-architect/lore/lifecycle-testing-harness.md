# Lifecycle Testing Harness

The multi-engine lifecycle testing harness — designed in `workdir/draft-testing-pipeline.md`,
Phase 0.5 of `multi-engine-portability-direction.md` — is built and real, not just designed.
Lives in `lore-framework-dev/tests/lifecycle/`: `harness.py` (fixture builder — throwaway agent
repo + local bare git `origin`, zero network — plus headless engine drivers) and one `test_*.py`
file per scenario group: `test_boot.py`, `test_recall.py`, `test_finalize.py`,
`test_consult_attach.py`, `test_repo_workspace.py`.

## Coverage

19 of the 21 Tier-1 scenarios from the design catalog (`workdir/draft-testing-pipeline.md`
§ Scenario catalog v1) are implemented. They pass on:

- **Claude Code** — the baseline engine, per the draft's Phase 0.5 sequencing
- **Cursor** — the real local engine, first validated against the pre-ship
  `lore-framework-cursor/` build and now corresponding to canonical `lore-framework` v20;
  driven via `cursor-agent -p`

Deliberately deferred:
- **#14 concurrent-finalize collision** — needs a two-clone push-race script.
- **#15 finalize-with-guest** — needs a cross-repo guest fixture.

Both need more scaffolding than the rest and weren't worth rushing.

Out of scope for this harness (covered elsewhere or not headless-scriptable):
- Tier 2 `wait`/`emit` — already covered at the protocol level by the pre-existing `test_wait.py`; a lifecycle-level duplicate adds little.
- `spawn-teammate` — not headless-scriptable (multi-pane UI).
- `df-repo-init` / `df-ula-file` — stayed out of scope (BETA).

## Assertion style

Assertions are structural, matching the design premise: git HEAD before/after, file existence, canary tokens planted in fixture files (to prove a file was actually read, not paraphrased around), `grep`-based fact checks after reflect/merge. No LLM-as-judge needed for any of the 19 — the catalog's premise (procedure outputs are files + git state, verifiable by script) held up in practice.

## Cost and gating

Gated behind `LR_LIFECYCLE=1` (real API cost, ~$0.10–1.35 per scenario on sonnet depending on complexity — the multi-step ones like attach, finalize end-to-end, and the dirty-tree-gate walk cost the most). Free layer-1/2 tests (script tests, lint checks) remain ungated and pass in ~4s.

## Repo placement

`tests/` sits at the `lore-framework-dev` repo root, not under `agents/lore-architect/` — finalize's Phase 4 commit is scoped to `agents/` only (per `finalize.md` Phase 4 step 1: `git add agents/`), so harness code needs its own separate commit, outside the finalize flow.

## What's still open

- Tests 14 and 15 are specced in the catalog but not implemented.
- Not yet run: a full pass on `opus`, to complete the three-model baseline before either port session starts.
- **Codex**: `run_engine()` still has no codex branch. But the framework has now been **manually
  validated end-to-end on real Codex** (2026-07-05) — the full boot→recall→merge lifecycle,
  including native `spawn_agent` fan-out, via the `docs/engines/` build; see
  `codex-port-validated-end-to-end.md`. The ground-truthing method (rollout-log verification of
  spawn claims, not model self-report) is in `codex-testing-methodology.md`. Wiring an automated
  `codex` branch (incl. the one-time marketplace/plugin-install setup codex needs, unlike Claude
  Code's per-invocation `--plugin-dir`, and rollout-log spawn assertions) so this is in the suite
  rather than manual is still open — see `port-landing-next-steps.md`.
- **Cursor**: the earlier quota-blocked state is now superseded. A local `cursor` branch was added
  to `run_engine()` and the full implemented scenario catalog passed on the real local engine
  (`19/19`) against the pre-ship `lore-framework-cursor/` build that later landed as canonical
  `lore-framework` v20. Important operational note: the harness code lives under `tests/`,
  outside finalize's `agents/` commit scope, so harness changes still require their own manual
  commit after a finalize run. See `cursor-port-validated-end-to-end.md`,
  `cursor-cli-and-harness-operational-notes.md`.
- Manual engine probes done outside the harness should be backgrounded and polled, not foreground-run with a hard kill timeout — see `headless-cli-smoke-testing-discipline.md` (the lesson that produced this note).

## Doc-change validation loop (`LR_FRAMEWORK_DIR` + `LR_TEST_MODEL`)

Point `LR_FRAMEWORK_DIR` at a modified *copy* of the framework and set `LR_TEST_MODEL=haiku`; together with the canary mechanism this makes a clean "does a doc change break or clarify execution?" loop — no new test code needed. This is how the framework-root port and defer-clarity fixes were validated (2026-07-04): the `<framework-root>` self-location conversion ran **18/19 first pass on haiku**, with every subagent fan-out scenario passing, and a `stream-json` trace confirmed haiku resolved the root by Reading the `VERSION` file rather than leaning on env-var expansion. See `framework-root-self-location-validated.md`. Running at the **haiku tier deliberately** is what turns the harness into an ambiguity detector — see `haiku-ambiguity-detector.md`.

## Why this has value now, not just at port time

The harness was designed as Phase 0.5 groundwork for the Codex/Cursor ports, but its first real use (see `agent-boot-doc-fidelity-fixes.md`) found two genuine bugs in `agent-boot.md` on Claude Code itself — before either port started, and a later run surfaced a third (the defer-clarity issue in `haiku-ambiguity-detector.md`). It's a live doc-fidelity check on Claude Code's own procedures, not just a port-readiness gate. See `execution-testing-catches-blind-ambiguity.md` for the general principle this demonstrates, and `role.md` § Responsibilities / Lore-Curation Disciplines for the operating discipline it now backs.

## See Also

- `workdir/draft-testing-pipeline.md` — the original design doc; scenario catalog, sequencing, open questions. Don't duplicate here.
- `agent-boot-doc-fidelity-fixes.md` — the concrete bugs this harness found on its very first real use.
- `execution-testing-catches-blind-ambiguity.md` — the general principle: prose ambiguity invisible to a strong model only surfaces via execution testing.
- `haiku-ambiguity-detector.md` — why running at the haiku tier is the point, not a caveat; the defer-clarity fix this harness surfaced.
- `framework-root-self-location-validated.md` — the `<framework-root>` port change set validated via the `LR_FRAMEWORK_DIR` loop.
- `port-landing-next-steps.md` — the landing record plus the remaining follow-ups not yet folded
  into the automated suite.
- `multi-engine-portability-direction.md` — the anchor topic this harness serves (Phase 0.5).
- `parallel-reviewer-fanout-pattern.md` — the model-review pre-ship discipline this complements with empirical regression testing.
- `codex-cli-plugin-loading-findings.md`, `cursor-agent-cli-probe-findings.md` — first empirical
  per-engine probes.
- `codex-port-validated-end-to-end.md`, `codex-testing-methodology.md` — the manual end-to-end Codex validation and its rollout-log ground-truthing (what the automated codex driver must replicate).
- `cursor-port-validated-end-to-end.md`, `cursor-cli-and-harness-operational-notes.md` — the local
  Cursor validation and the harness-driver operational details.
- `headless-cli-smoke-testing-discipline.md` — how to run manual engine probes without a hard-kill timeout destroying the evidence.
