**Running lifecycle scenarios on the weakest available model (haiku) is not just a stress test whose failures you wave away as "weak model" — haiku is an *ambiguity detector*. Where it stumbles, the procedure doc is usually under-specified; a stronger model (including the doc's author and any strong-model reviewer) silently resolves the ambiguity, so prose review never catches it.**

A foundational operating principle, born from a concrete lifecycle-harness result. Named per the meta-rule in `naming-foundational-principles.md`.

## Why this matters

This is the execution-fidelity leg of `execution-testing-catches-blind-ambiguity.md`, sharpened: **the bar is not "works on sonnet" but "explanatory enough that even haiku executes it faithfully."** That bar also hardens the framework for the non-Claude engines we're porting to (`multi-engine-portability-direction.md`), which are themselves not top-tier — so clarity-for-haiku is directly clarity-for-port.

Caveat: the fix is **clarity and unambiguous structure, not more words.** A pointed sentence at the right spot (or a checklist) beats a longer paragraph — watch for bloat.

## The concrete instance (test_06, upgrade-gate-on-dirty-tree)

Haiku got the **hard** part right — detected the dirty ∩ migration-write-set collision, deferred the upgrade, left version and file untouched — then botched the **easy** part: it emitted the harness's `BOOT-FAILED` sentinel and stopped, conflating *"upgrade deferred"* with *"boot failed."*

Root cause in the doc: `version-check.md` prints an alarming deferral message (*"cannot auto-upgrade … Resolve by …"*) **inline at the defer point**, while the reassurance ("continue boot in degraded mode" / the invariant "Boot never fails on version errors") was terse or buried at the bottom. A weak model reading top-down acts on the scary message before reaching the reassurance.

## The defer-clarity fix (staged, validated 3/3 on haiku)

**Hoist the reassurance to be unmissable and adjacent to the alarming message.** Added to each defer point in `version-check.md`, and to `agent-boot.md` step 3, an explicit: *"A deferred upgrade is NOT a boot failure — return to agent-boot.md and finish loading the agent; do not report boot as failed."* Framing it at the boot level (agent-boot step 3: "version check never aborts boot; always proceed to step 4") makes the boot procedure's own structure pull a confused model forward.

This fix is orthogonal to the port — a genuine robustness win on its own. It is **staged, not yet applied to the real framework** — see `port-landing-next-steps.md`.

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
