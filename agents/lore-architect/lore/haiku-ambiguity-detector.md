**Running lifecycle scenarios on the weakest available model (haiku) is not just a stress test whose failures you wave away as "weak model" — haiku is an *ambiguity detector*. Where it stumbles, the procedure doc is usually under-specified; a stronger model (including the doc's author and any strong-model reviewer) silently resolves the ambiguity, so prose review never catches it.**

A foundational operating principle, born from a concrete lifecycle-harness result. Named per the meta-rule in `naming-foundational-principles.md`.

## Why this matters

This is the execution-fidelity leg of `execution-testing-catches-blind-ambiguity.md`, sharpened: **the bar is not "works on sonnet" but "explanatory enough that even haiku executes it faithfully."** That bar also hardens the framework for the non-Claude engines we're porting to (`multi-engine-portability-direction.md`), which are themselves not top-tier — so clarity-for-haiku is directly clarity-for-port.

Caveat: the fix is **clarity and unambiguous structure, not more words.** A pointed sentence at the right spot (or a checklist) beats a longer paragraph — watch for bloat.

## The concrete instance (test_06, upgrade-gate-on-dirty-tree)

Haiku got the **hard** part right — detected the dirty ∩ migration-write-set collision, deferred the upgrade, left version and file untouched — then botched the **easy** part: it emitted the harness's `BOOT-FAILED` sentinel and stopped, conflating *"upgrade deferred"* with *"boot failed."*

Root cause in the doc: `version-check.md` prints an alarming deferral message (*"cannot auto-upgrade … Resolve by …"*) **inline at the defer point**, while the reassurance ("continue boot in degraded mode" / the invariant "Boot never fails on version errors") was terse or buried at the bottom. A weak model reading top-down acts on the scary message before reaching the reassurance.

## The defer-clarity fix (shipped in v19, validated 3/3 on haiku)

**Hoist the reassurance to be unmissable and adjacent to the alarming message.** Added to each defer point in `version-check.md`, and to `agent-boot.md` step 3, an explicit: *"A deferred upgrade is NOT a boot failure — return to agent-boot.md and finish loading the agent; do not report boot as failed."* Framing it at the boot level (agent-boot step 3: "version check never aborts boot; always proceed to step 4") makes the boot procedure's own structure pull a confused model forward.

This fix is orthogonal to the port — a genuine robustness win on its own. It **shipped in v19** (commit `72b1b2a`); it was authored fresh at landing because it was staged separately from the codex build, not carried in it. Re-validated 6/6 on haiku against the real v19 tree — test_06 now defers cleanly without emitting the boot-failure sentinel. See `port-landing-next-steps.md`.

## The axis is engine, not just model tier (session-archive feature, 2026-07-21)

The detector has a **second axis**: the agent harness, not only the model tier. Concrete instance — a new `docs/summarize.md` sub-step ("Step 1.5"), inserted mid-procedure to drive a `session-takeover archive` call, executed correctly on **Claude Code (sonnet)** and **Codex (gpt-5.4-mini)**, but was **silently skipped, twice across independent runs, on Cursor (`cursor-agent`)** — which runs **sonnet underneath**. Same model tier that passed on Claude Code; the difference was purely the CLI agent loop wrapping it. So this is not a model-tier ambiguity gap — it's an **engine/harness fidelity gap**. Cursor and Codex are not just "cheaper/weaker Claude"; their agent loops have independently different procedural-fidelity characteristics.

Two composed lessons:

1. **Run lifecycle scenarios on multiple *engines*, not just multiple model tiers within one engine.** Engine-axis gaps are invisible to model-tier testing alone. This is the harness's real reach — "run on every engine" (see `lifecycle-testing-harness.md`).
2. **Inserting a new step into the middle of an established, long, numbered procedure is empirically higher-risk than appending one, or adding a standalone doc** — a real-engine agent dropped the inserted step outright rather than misreading it. A failed mitigation confirmed the depth: sharpening the disambiguating sentence (adding "a stderr warning is NOT a skip signal") did **not** fix it — the model then never invoked the tool at all. So the fix is not "sharpen the wording," it's the *structure*: prefer append or standalone-doc over mid-procedure insertion; where insertion is unavoidable, only real-engine verification **on every target engine** catches a silent skip (code review and even sonnet self-review will not — the insertion reads correctly to a strong reader). Disposition on the original instance: documented as a known BETA gap, non-blocking (no partial/corrupted summary resulted; the archive script itself is correct on Cursor's log format).

## Generalizable rule

**Wherever a procedure prints a scary "cannot X" message but the flow is meant to continue, put the "this is not a failure, keep going" directive immediately adjacent — never only in a trailing invariants section.** A weak (or hurried, or context-pressured) reader acts on the first strong signal it hits.

## Diagnostic

When a lifecycle scenario fails on haiku but passes on sonnet, do **not** dismiss it as "weak model." Read the failure as a pointer to under-specified prose: which sentence did the weaker model resolve differently, and why. The fix is at that sentence, not in the model choice.

## See Also

- `execution-testing-catches-blind-ambiguity.md` — the parent principle; this sharpens its execution-fidelity leg (weak-model bar).
- `agent-boot-doc-fidelity-fixes.md` — the earlier two harness-found `agent-boot.md` bugs (the same "haiku surfaced what review missed" shape); the defer-clarity fix is the third.
- `lifecycle-testing-harness.md` — the tool; run it at more than one model tier so haiku can do its detector job.
- `naming-foundational-principles.md` — the meta-rule this topic's own existence follows.
- `system-design-principles.md` — where this principle is indexed.
- `multi-engine-portability-direction.md` — why the haiku bar doubles as a port-readiness bar.
- `port-landing-next-steps.md` — where the staged defer-clarity fix lands.
