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

**Full-suite ship gate (v21, 2026-07-06):** the complete suite ran as the last gate before the v21
push — **19/19** lifecycle scenarios + 23 deterministic = **42/42** on the `claude` engine (~$9.4,
~27 min). This is the reference cost/time for a full pre-push run, and reinforces that the gate is
the *complete* suite, not a proportionate subset (see `execution-testing-catches-blind-ambiguity.md`
§ pre-ship = pre-push). The v21 ship also folded in engine-neutral driver support:
`harness.py` cursor + codex branches plus an engine-neutral `memory_file_name()` (dev commit
`73876d1`).

**Sibling track (2026-07-07):** a third test track, the quality benchmark
(`lore-framework-dev/tests/quality/`, gated `LR_QUALITY=1`), measures **lore utilization** — did
the lore make the output better — where this harness measures **procedure fidelity**. Same repo
placement rule (outside finalize's `agents/` commit scope), same deterministic-first assertion
discipline; it adds a pinned LLM judge only for the behavior stage. See
`quality-benchmark-feature.md`.

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

- **Parallelize the suite** — scenarios are fixture-isolated; today they run serially via
  `unittest discover` (~15–45 min/engine). Future: `LR_LIFECYCLE_JOBS`, parallel by test file, or
  parallel by engine in separate terminals; cap concurrency for API limits. See
  `lifecycle-harness-parallelization.md`; TODO in `tests/lifecycle/harness.py`.
- Tests 14 and 15 are specced in the catalog but not implemented.
- Not yet run: a full pass on `opus`, to complete the three-model baseline before either port session starts.
- **Codex**: `run_engine()` now has a real codex branch. It runs `codex exec` directly, defaults
  to `gpt-5.4-mini`, redirects stdin from `/dev/null`, and captures the final agent message via
  `--output-last-message` rather than trying to normalize Codex's JSONL stream into the
  Claude/Cursor shape. The driver translates the engine-neutral lifecycle prompt into a reliable
  **doc-driven** Codex prompt at runtime by pointing at `<LR_FRAMEWORK_DIR>/docs/*.md`, so the
  harness does not depend on a preinstalled Codex plugin or matching plugin cache. Immediate host
  constraint: the outer process launching `codex exec` must allow writes to `~/.codex/`, or Codex
  can fail before the fixture run starts (`~/.codex/state_5.sqlite`, readonly database). Still
  open: rollout-log-based spawn assertions and broader Codex scenario coverage beyond the current
  smoke path. See `codex-testing-methodology.md`, `codex-port-validated-end-to-end.md`, and
  `port-landing-next-steps.md`.
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
- `lifecycle-harness-parallelization.md` — future improvement: parallel scenario execution.
- `quality-benchmark-feature.md` — the sibling quality track (`tests/quality/`): lore utilization, planted-needle probes, treatment/control uplift.
- `benchmark-measurement-design-principles.md` — the measurement-design principles shared with (and extending) this harness's assertion style.
