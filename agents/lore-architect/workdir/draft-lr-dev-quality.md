# Draft — lr-dev Feature: Bug-Finding & Test-Coverage (+ standardization)

> **Status: active exploration, not decided.** Companion to **`draft-lr-dev.md`** (the general lr-dev concept — knowledge model, mode/capability gate, repo lore, reusable review skill). This file covers the **first lr-dev feature**: automatically finding bugs/inconsistencies and raising unit-test coverage, plus the **standardized bug / scenario / report formats** the feature produces. Opened 2026-05-31 with the user (zroslaw).
>
> **⮕ 2026-06-01 reframe alignment (see `draft-lr-dev.md` §1A).** Terminology shift under the reframe: "**repo lore**" → **the context agent's lore**; the "**repo-lore repo**" → **the per-repo agent repo housing the `<repo>-context` agent**. The file/unit quality analysts here are **ephemeral subagents** spawned by a **separate specialist (worker) agent**, which **attaches the `<repo>-context` agent** for repo understanding and **feeds discoveries back** into it at finalization (per-agent reflection). The **capability-gate** framing referenced below is **superseded** — repo knowledge is just the context agent's own lore, governed by native per-agent write-ownership.

## 1. The feature

**Bug-finding & coverage** is **one feature** of the lr-dev catalog — and a complex one: it will grow multiple workflows, instructions, and mixed manual/automated flows over time. Below is its **first workflow: file-by-file analysis.** Roles, mode, and capability gating come from `draft-lr-dev.md`.

## 2. Workflow — file-by-file analysis

Per-file pipeline. **Canonical decomposition (validated 2026-06-02 prototype)** — five phases plus persistence. Prioritization/queue is deferred (§5); for the first runs we pick files by hand. The pipeline is implemented as a Claude Code dynamic Workflow script (current iteration: `workdir/draft-lr-dev-file-quality-workflow.js`); each `agent()` call carries the §4 schemas as JSON-Schema constraints — required fields are enforced at the tool-call layer, not just by prompt.

**Phase 1 — Decompose.** **file quality analyst** takes one file and decomposes it into testable **units** (functions, methods, classes — language-dependent).

**Phase 2 — Analyze (fan out, per unit, parallel).** For each unit a **unit quality analyst** subagent runs, instructed to do **two things at once**:
- **(a) hunt bugs** in the unit and its adjacent workflow components — trace all execution paths;
- **(b) author test scenarios** sufficient for ~full line/branch coverage + edge cases that cause product- or technical-level bugs.

Output per unit: a set of **potential bugs** (§4.2) + a set of **test scenarios** (§4.1) — *as scenarios, not code* (framework-agnostic).

**Workflow subagents `boot` the per-repo context agent as their first action**, not `attach`. A workflow subagent is a fresh session with no host context; `attach` has nothing to attach into. `boot` runs the agent's boot procedure cleanly and the subagent *becomes* the context agent. (See `workflow-primitive-operational-notes.md`.) Without context-agent booting, verifiers in particular flag legitimate domain idioms as "bugs" — this is the operational case validating the lr-dev reframe.

**Phase 3 — Aggregate.** **file quality analyst** composes all unit returns into a standardized **File Report** (§4.3).

**Phase 4 — Verify (two parallel agents, concurrent).**
- **Per-bug adversarial verifier** — *one subagent per bug*; defaults to "refute"; cross-checks (1) reachability of the triggering path against the actual caller graph, (2) substance of the cited intent source, (3) whether "expected" is intent-driven or analyst opinion. Returns a verdict (`real | false-positive | inconclusive`) plus a confidence-adjustment recommendation. All three checks need repo context — the verifier boots the context agent. Bugs are *genuinely independent claims* — adversarial-per-item is justified.
- **Single gap analyzer** (concurrent with the bug verifiers) — reverse-extracts scenarios from existing tests using the §4.1 schema, matches forward proposed against reverse extracted by intent (exact / equivalent / partial), produces a gap list with one-line whys. **Bidirectional-IR diff is real** once both directions use the same schema.

**Per-scenario verify is dropped.** v1 of the prototype spent 19 parallel agents enforcing "every scenario cites a real intent source" and dropped zero scenarios — the §4.1 schema's required `intentSource` field plus the analyzer prompt's hard rule already do the work. Aggregate review (Phase 5) catches what the schema misses. (See `workflow-primitive-operational-notes.md` § Right-size the verify fan-out and `parallel-reviewer-fanout-pattern.md` § When NOT to fan out.)

**Phase 5 — Review (three parallel lenses).** Multi-lens review per the reusable `lr:dev-review` skill (`draft-lr-dev.md` §5). Default lens triad for this workflow: **intent-vs-observed** (does each "expected" assert intended behavior, not just current output?), **completeness** (gaps in coverage of paths/branches/edges), **soundness** (do similar-shaped bugs share verdicts? — bug verifiers can disagree). The file quality analyst picks the lenses; round-2 single focused reviewer per the parallel-reviewer pattern's v13 refinement.

**Phase 6 — Persistence.** The workflow's structured return is the run's only durable artifact unless it's written to disk. The **parent agent** (or a final write phase inside the workflow) writes a **§3-compliant File Report markdown file** to the quality repo (`quality-repo-architecture.md`) plus a manifest entry. Without this step the result lives only in the in-process notification and is lost. This is what makes the system **resumable across sweeps**: the manifest is the source of truth, not the workflow journal.

**Downstream of the workflow:**

- **Bugs → separate human-review branch** (later thread, not the first session). The *learnings* from triage (confirmed bug vs. known-correct pattern vs. false positive) feed back into the **per-repo context agent's lore** at finalization.
- **Scenarios → implemented now**, in the **quality repo** (`quality-repo-architecture.md`); **human-written tests in the source repo left untouched** even if scenarios duplicate. Drift between the AI suite and the human suite is information.
- **Real coverage tool**, run over the **newly generated tests only** (not human tests); analyze the report; fix gaps/inconsistencies.

**Two design properties to preserve:**
- **Scenarios are a bidirectional IR.** Forward: scenario → test code (any framework). Reverse: test code → scenario (for gap analysis, step 4). The schema must support both directions.
- **The analysis pass also bootstraps repo lore.** Non-derivable context a unit quality analyst uncovers → that file's `.lore.md` + relevant product/technical topics. Dissolves the chicken-and-egg (you need lore to test well, but you build lore by analyzing). The first runs are partly lore-bootstrapping runs.

**Guard against the test-gen trap.** "Comprehensive" tests can just canonize current (possibly buggy) behavior — change-detector tests. One mandatory review lens must be *"do these assert intended behavior, not just observed?"* This is where **product lore** earns its keep: intent comes from product lore, not from re-reading the code's current output. Enforced at the format level too (§3, "cite source of intent").

## 3. Standardization — cross-cutting design rules

All three deliverables are **markdown-first with a small YAML header** for the few machine-read fields (keeps the plain-markdown ethos, stays parseable). The leverage is in these rules:

- **Stable IDs** on every scenario/bug → dedupe + track across runs (a scenario proposed last run, implemented this run; a bug re-found).
- **A `class: product | technical` tag on every item** → ties each finding back to the two-lore split and routes its learning to the right category.
- **Every "expected behavior" cites its *source of intent*** (a product/tech topic, docstring, type, contract). Format-level enforcement of the coverage≠meaning guard: you can't assert observed output as "correct" without naming what says it should be.
- **`confidence` + `status` fields** acknowledge the soft-oracle reality (bugs) and drive the human triage that feeds repo lore.
- **Real counts only** in summaries (per [[dry-run-summary-counts]] — numbers come from the coverage tool, not the model).

## 4. The three schemas

### 4.1 Test scenario (the bidirectional IR — most important)

Header (YAML): `id`, `unit` (file+symbol), `class` (product|technical), `status` (proposed | implemented | covered-by-existing), `coverage-target` (line/branch).
Body (prose):
- **intent** — one line: what behavior this verifies.
- **setup / preconditions** — required state.
- **input / trigger** — the action.
- **expected** — the postcondition, **with its intent source cited**.
- **edge/branch tag** — which path/edge case it covers.

Same schema is produced *forward* (analyst authors from intent) and *reverse* (extracted from an existing test for gap analysis). Gap = desired − covered, matched on (unit, behavior).

### 4.2 Bug report

Header (YAML): `id`, `unit`, `class` (product|technical), `severity`, `confidence`, `status` (unreviewed | confirmed | rejected-false-positive | known-correct).
Body (prose):
- **suspected fault** — what's wrong.
- **triggering path** — the execution path the unit quality analyst traced.
- **expected vs actual** — with the **intent source** for "expected".
- **evidence** — code excerpt, path trace.
- **disposition** — filled at human triage; its outcome feeds repo lore (confirmed → known-issue topic; false-positive → known-correct-pattern topic; a confirmed bug also seeds a regression scenario).

### 4.3 File report (the aggregate; unit of human review)

- **Header** — file, language, units found, run metadata (date, agent, lr-dev/framework version, model).
- **Summary** — real counts: units analyzed; bugs by class/confidence; scenarios by category; coverage before/after (once implemented).
- **Per-unit sections** — each unit → its bug blocks (§4.2) + scenario blocks (§4.1).
- **Gap analysis** *(optional)* — existing scenarios vs proposed vs gap.
- **Coverage** — tool output summary (real numbers), gaps fixed.
- **Review** — lenses used + dispositions.

## 4.4 Reports landing — resolved (2026-06-02): the quality repo

**Resolved by `quality-repo-architecture.md`.** File Reports and other quality artifacts (bug catalog, scenario catalog, gap analyses, AI-generated tests, manifest) live in a **separate, non-restricted quality repo** — *not* in the per-repo context agent's lore, and *not* in the source repo. Three reasons:

1. **Different lifecycles.** Reports are run snapshots produced mechanically by the workflow and curated by humans through triage. None of that goes through reflection/merge. Treating them as lore would force them through a process they don't fit.
2. **Compliance-regime fit.** When the source repo is under a strict review regime (mandatory human review, audit trail), AI-authored artifacts can't land in it. The quality repo is unrestricted.
3. **Composite-build access.** AI-generated tests can exercise real source-repo code without being copied into it.

The **durable distillation** — known-correct patterns, captured intent, known issues — *does* flow into the per-repo context agent's lore at finalization (per the reflection discipline that survives from the original objective/subjective cut). The split:

- File Reports / bug entries / generated tests → **quality repo** (artifacts, prunable, manifest-tracked).
- Patterns / intent / known-issues distilled from triage → **context agent's lore** (knowledge, reflected on).

Old reports: retained for now (cheap; useful as history during early lr-dev maturation). Pruning policy is a future quality-repo concern, not an architecture decision.

## 5. Deferred (feature-specific)

- **No auto-fixing of bugs** — find + report only; auto-fix is a later north-star increment.
- **File prioritization/queue** — coverage-driven ordering of which files to attack; pick by hand at first.
- **Scenario → code binding** — how scenarios get realized in a concrete framework (per-language adapters?).
- **Generated-vs-human test de-dup** — kept separate now; reconcile later.
- **Mouse-repo run** — `My-Turbo-Boost-Switcher` is the chosen experimentation repo; inspection + first run deferred until these drafts stabilize.

## 6. Foundational framings to promote (at finalization)

- **test scenarios as a bidirectional IR** (what-to-test decoupled from how; forward + reverse).
- **coverage ≠ meaningfulness guard** (cite source of intent; product lore supplies intent) + **analysis-pass-bootstraps-repo-lore** synergy.
- **deliverable-format design rules** (stable IDs, product/technical class tag, intent-source citation, confidence/status, real counts).

## 7. See also

- `draft-lr-dev.md` — general lr-dev concept (mode, capability gate, repo lore, review skill).
- `parallel-reviewer-fanout-pattern.md` — the multi-lens review reused in Phase 5; § When NOT to fan out is the principle behind dropping per-scenario verify.
- `quality-repo-architecture.md` — the three-repo split this workflow's persistence step writes into.
- `workflow-primitive-operational-notes.md` — operational lessons from the prototype (boot-not-attach, schemas-as-enforcement, persistence-is-parent's-job, right-size the verify fan-out).
- `framework-improvements-backlog.md` § lr-dev — backlog home.
