# Lifecycle Testing Harness

The multi-engine lifecycle testing harness — designed in `workdir/draft-testing-pipeline.md`, Phase 0.5 of `multi-engine-portability-direction.md` — is built and real, not just designed. Lives in `lore-framework-dev/tests/lifecycle/`: `harness.py` (fixture builder — throwaway agent repo + local bare git `origin`, zero network — plus a headless engine driver for `claude -p`) and one `test_*.py` file per scenario group: `test_boot.py`, `test_recall.py`, `test_finalize.py`, `test_consult_attach.py`, `test_repo_workspace.py`.

## Coverage

19 of the 21 Tier-1 scenarios from the design catalog (`workdir/draft-testing-pipeline.md` § Scenario catalog v1) are implemented and passing on Claude Code — the baseline engine, per the draft's Phase 0.5 sequencing.

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

## Why this has value now, not just at port time

The harness was designed as Phase 0.5 groundwork for the Codex/Cursor ports, but its first real use (see `agent-boot-doc-fidelity-fixes.md`) found two genuine bugs in `agent-boot.md` on Claude Code itself — before either port started. It's a live doc-fidelity check on Claude Code's own procedures, not just a port-readiness gate. See `execution-testing-catches-blind-ambiguity.md` for the general principle this demonstrates, and `role.md` § Responsibilities / Lore-Curation Disciplines for the operating discipline it now backs.

## See Also

- `workdir/draft-testing-pipeline.md` — the original design doc; scenario catalog, sequencing, open questions. Don't duplicate here.
- `agent-boot-doc-fidelity-fixes.md` — the concrete bugs this harness found on its very first real use.
- `execution-testing-catches-blind-ambiguity.md` — the general principle: prose ambiguity invisible to a strong model only surfaces via execution testing.
- `multi-engine-portability-direction.md` — the anchor topic this harness serves (Phase 0.5).
- `parallel-reviewer-fanout-pattern.md` — the model-review pre-ship discipline this complements with empirical regression testing.
