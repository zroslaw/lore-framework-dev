# Mid-Run Assertions Need the Transcript; End-State Assertions Can Use the Final Message

**An assertion about what the agent *said during* a run needs the transcript; an assertion about
the *end state* can use the final message.** Keep the two capture surfaces separate — mixing them
silently changes what a test means per engine.

## The concrete instance (2026-07-27)

Lifecycle `test_08` asserts the Script Fallback Contract's requirement 1 — tell the user which
script failed. Codex failed it, and **the artifacts could not say whether that was a real defect.**

Cause: `run_engine`'s Codex branch set `RunResult.text` from `codex exec --output-last-message` —
the final message only. The Script Fallback notice is emitted **mid-boot**, when preflight fails.
If Codex said it and then finished with the two codewords, a compliant run reads as a violation.
The debug dump stored only the final message too, so nothing on disk could settle it.

So Codex `test_08` is **undetermined, not failing** — the assertion was uninterpretable on that
engine, which is a harness defect, not a v31 model-fidelity defect.

## Applied (`467b009`)

`RunResult.transcript`, populated on Codex from the `--json` event stream, defaulting to `text` on
Claude/Cursor (which return one result string and no stream). `test_08`'s two "was the user told"
assertions moved to it; canary and `BOOT-FAILED` assertions stayed on `text`.

**Only `agent_message` items count** toward the transcript. Tool calls and reasoning are excluded
deliberately: `lr-core` appears in the command line that invokes it, so counting tool arguments
would pass the assertion without the user ever being told. **A too-broad transcript is worse than
the final message — it produces false greens instead of false reds.**

Codex event schema captured live from `gpt-5.4-mini` (a ~1¢ probe, worth running rather than
guessing — see `fetch-volatile-facts-live-not-memory.md`):

```json
{"type": "thread.started", "thread_id": "..."}
{"type": "turn.started"}
{"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": "..."}}
{"type": "turn.completed", "usage": {"input_tokens": ..., "output_tokens": ...}}
```

`turn.completed.usage` gives token counts but **no USD**, so Codex cost still is not directly
available from the stream (consistent with `codex-exec-real-invocation-contract.md`).

## Operational rule

When writing a lifecycle assertion, first classify it: *during* or *at the end*. Then check the
capture surface actually available on **each** engine — a per-engine capture asymmetry turns one
written assertion into different tests, and the weakest capture silently sets the meaning.

## See Also

- `lifecycle-testing-harness.md` — the harness this lives in; § Assertion style.
- `codex-exec-real-invocation-contract.md` — the Codex JSONL stream contract this reads.
- `fetch-volatile-facts-live-not-memory.md` — why the schema was probed live.
- `v31-lifecycle-rerun-partial-green-2026-07-27.md` — the run whose triage this corrected.
- `a-gate-cannot-be-a-model-self-report.md` — sibling: an assertion is only as good as the evidence
  class it can actually observe.
