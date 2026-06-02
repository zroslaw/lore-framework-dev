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

## See Also

- `parallel-reviewer-fanout-pattern.md` — per-lens fan-out is the inverse case (genuinely independent perspectives); pairs with the right-size-the-verify rule above.
- `shared-procedure-doc-pattern.md` — workflow scripts share traits with shared-procedure docs (body lives in one canonical file, sites point at it).
- `graduated-verification-confidence.md` — verdict states from verify stages should be a graded surface, not a boolean — workflows make this concrete (real / false-positive / inconclusive).
- `quality-repo-architecture.md` — the manifest-driven resumability pattern that composes with workflow output persistence.
- `knowledge-vs-skills-distinction.md` — workflow scripts are *skills* (instrumental); their structured outputs are *artifacts*, not knowledge.
