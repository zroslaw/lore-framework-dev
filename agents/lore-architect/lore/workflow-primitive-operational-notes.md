# Workflow Primitive — Operational Notes

Claude Code's dynamic Workflow tool runs a JS script that orchestrates `agent()` calls in stages with structured-schema returns. First substantive use was the lr-dev quality file-by-file analysis prototype (see `draft-lr-dev-file-quality-workflow.js`). These notes capture what's worth keeping for the next workflow.

## When workflow is genuinely the right primitive

Workflow fits when **all** are true:

- Control flow benefits from being deterministic (loops, conditionals, fan-out shapes the model shouldn't redecide each turn).
- The work decomposes cleanly into stages that can fan out (per-item parallel work).
- Each stage's prompt + opts can be authored once and reused across items.
- Results are structured enough to be schema-constrained (so downstream stages don't re-parse model prose).

If only some hold, a small number of plain `Agent` calls is usually simpler.

## Boot, not attach, inside workflow subagents

A workflow subagent is a fresh Claude session with no host context. `/lr:attach` has nothing to attach into and produces nothing useful. `/lr:boot <agent>` runs the boot procedure and the subagent *becomes* the agent.

**Rule: workflow subagents that need an agent's identity must boot it as their first action.** Validated in the lr-dev quality prototype: `loreTopicsConsulted` arrays returned populated from booted bug-verifier and gap-analyzer subagents — the boot procedure runs cleanly inside a subagent context. Generalizes beyond lr-dev to any workflow whose subagents must operate from a specific agent's perspective.

## Schemas as enforcement, not documentation

Putting a `schema` on `agent()` calls is not just for the parent's parsing convenience — it's a hard constraint the model retries against. Required fields like `intentSource` on a Scenario, `triggeringPath` on a Bug, etc., are enforced at the tool-call layer; the model can't return an item missing them. Stronger discipline than prompt-only enforcement. Use this for any field that downstream stages depend on.

## Pipeline default; barrier when you need cross-item context

`pipeline()` lets fast items advance through stages while slow items still finish stage 1 — wall-clock = slowest single chain, not sum-of-slowest-per-stage. Use it as the default for multi-stage work. Reach for `parallel()` between stages only when the next stage genuinely needs the *whole* prior stage to be done (dedup, summary, "give me all findings to compare").

## Right-size the verify fan-out

Per-item adversarial verify is correct when each item is a **genuinely independent claim** that can fail in idiosyncratic ways (bugs, security findings, design proposals). Per-item verify is **wrong** when the items share a uniform property a single agent can audit in bulk (e.g., "every scenario cites a real source").

**Default question:** *"Would a single agent looking at all N items at once produce the same verdicts as N separate agents?"* If yes, batch.

Real cost data from the prototype: v1 of the quality workflow used per-scenario verify (19 parallel agents, full file context each, **zero scenarios dropped**) — pure waste; the schema constraint already did the work. Removed in v2. Composes with the lessons in `parallel-reviewer-fanout-pattern.md` (where independent adversarial framing per *lens* is the right move because lenses really are independent, not redundant).

## Cost ramps fast under fan-out

Real run: ~17–28 agents producing 770k–905k tokens for a single small file. Per-file cost is a real budget consideration; whole-repo sweeps need throttling and prioritization. **Workflow design rule: every fan-out point must justify its size.** "Could one agent do this?" is a 10× cost question, not a stylistic one.

## Persistence is the parent's job

A workflow's structured `return` is the single most important durable artifact of the run, but the framework doesn't auto-persist it. Without a write step, the result lives only in the in-process notification and is lost when the conversation rolls.

**Add a final write phase to any workflow whose output should survive the session**, or have the parent immediately serialize the return. For multi-run systems (e.g., resumable repo sweeps), persistence is also where the manifest gets updated — see `quality-repo-architecture.md` for the manifest-driven resumability pattern.

## Background execution + task-notification loop

Workflows run in the background; the parent gets a `task-notification` when done. The structured `<result>` payload is the workflow's `return` value. The parent should **restate findings in its own text** — the user's view of the result is the parent's prose, not the raw payload. Long-running workflows are friendly to the parent's context budget because the workflow's intermediate agent traffic stays in the workflow's own subagent dirs.

## File-on-disk script is iterable; resumable via runId

The script can live anywhere on disk. Edit-and-rerun via `Workflow({ scriptPath })` works the same as the original launch. `resumeFromRunId` lets unchanged-prefix `agent()` calls return cached results — useful when iterating on a late stage without paying for the early stages again.

## Where to keep workflow scripts

For draft iteration, keep the script in the agent's `workdir/`. When stable and reusable, move to `~/.claude/workflows/` or the plugin's `workflows/` dir to make it a named workflow invokable as `Workflow({ name })`. Same iteration loop as drafts in markdown — workflow script in `workdir/` ≈ markdown draft in `workdir/`; both graduate by moving out.

## Dynamic Workflow Runtime Availability

The Claude Code dynamic Workflow primitive (`agent()`/`phase()`/`parallel()` JS runtime) is **not present in every session's toolset**. Verify rather than assume: check the session's deferred-tool list and run `ToolSearch` for workflow/orchestration/phases — if only Team/Task/Cron/Monitor come back, the runtime is absent.

**Fallback that works:** simulate orchestration with the `Agent` tool directly — one splitter subagent, then one unit-pass subagent per unit. Prompts and schemas designed for the workflow runtime are portable to this fallback without rewriting.

Also note: **no JS runtime (node/deno/bun) on the primary dev machine** — workflow JS can't be syntax-checked locally. Eyeball-review the JS or rely on the runtime's own parse.

Composes with `graduated-verification-confidence.md` (state confidence, plan for "unavailable") and `verify-before-acting-on-suspected-bugs.md`.

## `args` can arrive as a string — destructuring fails

Passing a JSON object as the Workflow tool's `args` failed **twice** with `Error: args must include { … }`, because the value reached the script as a *string* rather than a parsed object — so `const { filePath } = args` yielded `undefined` and the guard threw. The Workflow tool docs warn about exactly this: a stringified list/object breaks `args.map`/destructuring.

**Workaround that worked:** for a one-off run, stop relying on `args` injection — **hardcode the inputs directly in the workflow script** (filePath, sourceRepoPath, the unit list, and the prompts/schemas as inline JS constants). Self-contained script, no args coupling. For a single-shot scoped run this is simpler and more robust than fighting the args encoding. (Note this trades away the inject-then-undefined fail-loud discipline below — acceptable only because the script is self-contained and disposable.) If args injection *is* needed, ensure the value is passed as an actual JSON value, not a pre-stringified blob.

## Single-unit scoping = bypass the splitter

The stock ULA workflow's phase 1 splits the file into *all* units, then fans out. To scope a run to a chosen subset (or a single unit) cheaply, **skip the split phase and feed the explicit `{id, signature}` unit(s) straight into the Unit Pass.** Clean, no framework edits, honors "only this unit." Worked first try once the args encoding was sorted. This is how the single-unit validation in `ula-validated-turbo-boost-switcher.md` was run.

## Reviewing AI-Generated Workflow Code

AI-generated orchestration code needs the same adversarial review as any code. Running `/code-review` (max effort) on freshly-authored workflow JS surfaced **real correctness bugs**. Recurring defect classes worth watching:

- **Result/unit misalignment:** zipping `parallel()` results back to inputs by array index assumes order preservation. Fix: match each result to its item via an identity the result *carries itself* (a slug, an id) via a Map — never by index. Drop redundant outer identity stamps that can contradict the artifact.
- **Silent drops:** a `.filter(r => r.a && r.b)` that removes incomplete results loses items with no trace. Always collect and **name** dropped items, surface them (return a `dropped: []`, log a WARNING).
- **Inject-then-undefined:** when prompts/schemas are injected via `args` and referenced as `prompts.stepA` etc., a missing/mis-mapped key embeds the literal `"undefined"` into an agent prompt or builds a malformed schema. Fix: **fail loud** — validate all required keys up front and throw; document the file→key mapping explicitly (a table) so it can't be guessed wrong.
- **Schema strictness coupling:** a composite schema validating N sub-artifacts at once is all-or-nothing — one over-strict constraint (e.g. `minItems:1`) on one sub-item fails the whole unit. Principle: **schema enforces structure, prompt enforces quality/semantics.** Don't push quality bars into the schema where a single miss nukes a batch.
- **Per-unit full-file embedding:** embedding the whole file in every parallel unit prompt = O(units×filesize) tokens. Prefer letting the agent self-read the file (also aligns with "agent gathers its own context"); keep full embed only where genuinely needed (e.g., the split step).

Process lesson: the **review→fix→re-review loop converged** — round 2 confirmed fixes held and found only lower-severity residuals (e.g., unit-id uniqueness assumed but not enforced). This mirrors the multi-round-until-convergence discipline. See `parallel-reviewer-fanout-pattern.md`.

## See Also

- `parallel-reviewer-fanout-pattern.md` — per-lens fan-out is the inverse case (genuinely independent perspectives); pairs with the right-size-the-verify rule above.
- `shared-procedure-doc-pattern.md` — workflow scripts share traits with shared-procedure docs (body lives in one canonical file, sites point at it).
- `graduated-verification-confidence.md` — verdict states from verify stages should be a graded surface, not a boolean — workflows make this concrete (real / false-positive / inconclusive).
- `quality-repo-architecture.md` — the manifest-driven resumability pattern that composes with workflow output persistence.
- `knowledge-vs-skills-distinction.md` — workflow scripts are *skills* (instrumental); their structured outputs are *artifacts*, not knowledge.
- `ula-validated-turbo-boost-switcher.md` — the single-unit ULA run these args/scoping lessons came from.
