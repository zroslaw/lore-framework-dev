# Draft — lr-dev Feature: Bug-Finding & Test-Coverage (+ standardization)

> **Status: active exploration, not decided.** Companion to **`draft-lr-dev.md`** (the general lr-dev concept — knowledge model, mode/capability gate, repo lore, reusable review skill). This file covers the **first lr-dev feature**: automatically finding bugs/inconsistencies and raising unit-test coverage, plus the **standardized bug / scenario / report formats** the feature produces. Opened 2026-05-31 with the user (zroslaw).
>
> **⮕ 2026-06-01 reframe alignment (see `draft-lr-dev.md` §1A).** Terminology shift under the reframe: "**repo lore**" → **the context agent's lore**; the "**repo-lore repo**" → **the per-repo agent repo housing the `<repo>-context` agent**. The file/unit quality analysts here are **ephemeral subagents** spawned by a **separate specialist (worker) agent**, which **attaches the `<repo>-context` agent** for repo understanding and **feeds discoveries back** into it at finalization (per-agent reflection). The **capability-gate** framing referenced below is **superseded** — repo knowledge is just the context agent's own lore, governed by native per-agent write-ownership.

## 1. The feature

**Bug-finding & coverage** is **one feature** of the lr-dev catalog — and a complex one: it will grow multiple workflows, instructions, and mixed manual/automated flows over time. Below is its **first workflow: file-by-file analysis.** Roles, mode, and capability gating come from `draft-lr-dev.md`.

## 2. Workflow — file-by-file analysis

Per-file pipeline. Prioritization/queue is deferred (§5); for the first runs we pick files by hand.

1. **file quality analyst** (the lr-dev-enabled repo agent, in a transient role) takes one file and decomposes it into testable **units** (units depend on the language: functions, methods, classes, etc.).
2. For each unit it fans out a **unit quality analyst** subagent (ephemeral, general-purpose), instructed to do **two things at once**:
   - **(a) hunt bugs** in the unit and its adjacent workflow components — trace all execution paths;
   - **(b) author test scenarios** sufficient for ~full line/branch coverage + edge cases that cause product- or technical-level bugs.
   Output: a set of **potential bugs** (for later human review) + a set of **test scenarios** — *as scenarios, not code* (framework-agnostic).
3. **file quality analyst aggregates** all unit-quality-analyst returns into a standardized **File report** (§4.3).
4. *(Optional, user-gated)* **gap analysis** — reverse-extract scenarios from existing tests, diff against desired scenarios. Uses the same scenario schema in reverse.
5. **Bugs → separate human-review branch** (later thread, not the first session). The *learnings* from triage (confirmed bug vs. known-correct pattern vs. false positive) feed **repo lore**.
6. **Scenarios → implemented now**, in a **separate location**; **human-written tests left untouched** even if scenarios duplicate.
7. **Real coverage tool**, run over the **newly generated tests only** (not human tests); analyze the report; fix gaps/inconsistencies.
8. **Multi-lens review cycle** over the new tests (the reusable `lr:dev-review` skill — `draft-lr-dev.md` §5). The **file quality analyst** is the orchestrator and picks the lenses.

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

## 4.4 Open question — are reports lore or transient artifacts?

My read: the **File reports are run snapshots** (belong in the repo-lore repo, e.g. `technical/quality/reports/`, but disposable/prunable), while the **durable distillation** — known-correct patterns, captured intent, known issues — flows into product/tech/artifact lore. To decide: where reports physically land, and whether old ones are pruned vs retained as history.

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
- `parallel-reviewer-fanout-pattern.md` — the multi-lens review reused in step 8.
- `framework-improvements-backlog.md` § lr-dev — backlog home.
