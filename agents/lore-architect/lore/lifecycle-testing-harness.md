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

## Keeper (Lore Beings) coverage — separate flag, higher blast radius (2026-07-20)

Until 2026-07-20 the harness had **zero** coverage of Lore Beings / the Being Keeper — the only
real-engine Keeper test was a standalone Cursor-only script (`test_lrb_cursor_real_e2e.py`, since
deleted, superseded by A3). Closed that gap with `tests/lifecycle/keeper_harness.py` +
`tests/lifecycle/test_lrb_lifecycle.py`: originally 8 scenarios — A1–A3 (core spawn→result→ledger
loop, one per engine kind), B1 (real process-tree kill, claude), C1 (self-scheduling round trip via
the outbox), C4 (self-scheduling denied under the default permission mode), D1 (real PID-identity
confirmed-match), E1 (real `lrb daemon` subprocess) — then B2/B3 added the same day (codex/cursor
process-tree-kill variants of B1): a code review found the Keeper's own concurrency-slot-leak bug
in exactly the per-engine-asymmetry blind spot B2/B3 exist to close, sharpening the case that
"engine-agnostic in the Keeper's own code" isn't sufficient justification to skip per-engine proof
for a mechanism (killpg) whose risk lives in the SPAWNED process tree's shape, not the Keeper's
call site. D2/D3 (PID-identity variants) remain deferred — `ps` is pure OS-level inspection,
independent of which engine spawned the PID, so that argument does hold there. See
`lore-beings-mvp-takeover-review.md`, `test_lrb_lifecycle.py` module docstring.

**Gated behind a *separate* flag, `LR_LIFECYCLE_KEEPER=1` — deliberately not folded into
`LR_LIFECYCLE=1`.** Keeper scenarios are a strictly higher blast-radius class: some spawn a real
background process (`lrb daemon`, launchd-style) that must be torn down even on assertion failure,
not just "one headless call that costs money." Keep the two gates distinct so a routine full-suite
pre-push run doesn't silently start daemons. The Keeper's own `$LRB_HOME` / `$LRB_LAUNCHAGENTS_DIR`
env-var sandboxing (already built into `lrb.py`, no prerequisite code change) is what makes these
scenarios safe to run against a throwaway home.

**Real-engine-verified 2026-07-20** at the recommended-minimum tier (9 of the design's 13
scenarios): **claude 6/6** (A1, B1, C1, C4, D1, E1), **codex 1/1** (A2), **cursor 1/1** (A3, after
adding a `session_cost_usd` fallback to the test's engine config — see
`cursor-agent-real-invocation-contract.md`). B2/B3/D2/D3 (codex/cursor variants of process-kill and
PID-identity) were deliberately deferred: those mechanisms are engine-agnostic in the Keeper's own
code, so claude coverage is the representative proof.

The scenario catalog + sandboxing mechanism + cheapest-model picks were produced by a **Fable-model
subagent given a design-only brief** (read the shipped `lrb.py`, the `harness.py` conventions, the
beings draft; propose but do not implement) → `workdir/draft-lrb-lifecycle-tests.md`. The design
correctly found the built-in env-var sandboxing by reading the actual source rather than assuming.
Two concrete issues hit while getting these green are recorded as their own topics:
`keeper-spawn-prompt-boilerplate-distraction.md` (a cheap model fixating on the always-appended
self-scheduling boilerplate) and the cursor-backend-flakiness note in
`cursor-agent-real-invocation-contract.md`.

Out of scope for this harness (covered elsewhere or not headless-scriptable):
- Tier 2 `wait`/`emit` — already covered at the protocol level by the pre-existing `test_wait.py`; a lifecycle-level duplicate adds little.
- `spawn-teammate` — not headless-scriptable (multi-pane UI).
- `df-repo-init` / `df-ula-file` — stayed out of scope (BETA).

## Assertion style

Assertions are structural, matching the design premise: git HEAD before/after, file existence, canary tokens planted in fixture files (to prove a file was actually read, not paraphrased around), `grep`-based fact checks after reflect/merge. No LLM-as-judge needed for any of the 19 — the catalog's premise (procedure outputs are files + git state, verifiable by script) held up in practice.

## Cost and gating

Gated behind `LR_LIFECYCLE=1` (real API cost, ~$0.10–1.35 per scenario on sonnet depending on complexity — the multi-step ones like attach, finalize end-to-end, and the dirty-tree-gate walk cost the most). Free layer-1/2 tests (script tests, lint checks) remain ungated and pass in ~4s.

## Claude account-limit signature

Claude Code account-limit exhaustion can masquerade as broad lifecycle breakage. The signature is:
earlier scenarios run normally with real durations and nonzero costs; then affected scenarios exit
quickly with code 1, report zero cost, and end with a message like `You've hit your session limit -
resets 12pm (Asia/Bangkok)`.

When a Claude lifecycle run flips into that pattern, inspect `LR_DEBUG_DIR` captures before treating
the failures as framework regressions. This is quota/session-limit exhaustion, not evidence that the
procedure docs suddenly broke.

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
- `lore-beings-design.md` — the feature the `LR_LIFECYCLE_KEEPER=1` track exercises; `keeper-spawn-prompt-boilerplate-distraction.md`, `cursor-agent-real-invocation-contract.md` — the two issues hit getting the Keeper scenarios green.
- `testing-simulate-process-escape-without-setsid-binary.md` — a fast synthetic-process-tree technique that complements this harness's real-engine B1/B2/B3 scenarios when only the process-tree *shape* (not real engine behavior) needs reproducing.
- `kill-tree-enumerate-before-signal-ordering.md`, `hot-path-latency-can-expose-latent-test-timing-races.md` — operational lessons from the B2/B3 Keeper kill-tree fix that produced this harness's cursor coverage.
