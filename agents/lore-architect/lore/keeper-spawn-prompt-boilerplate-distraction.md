# A short/ambiguous Keeper one-shot prompt can lose a cheap model to spawn-prompt boilerplate

Operational lesson from the C1 (self-scheduling round trip) real-engine Keeper scenario
(2026-07-20). `lrb.py`'s `build_spawn_prompt` appends the **same self-scheduling paragraph to every
spawned session** — existential task *or* one-shot work-session alike — explaining how to schedule a
future session via `lrb schedule`. That paragraph is always-present competing context, not inert
framing.

When a one-shot work-session's operator-supplied `prompt` is short and context-free (first attempt:
the bare string `"OUTBOX-ROUNDTRIP-OK"`), a cheap model (claude haiku) can fixate on the
self-scheduling boilerplate instead of the actual task. Observed for real once: the spawned session
called `lrb schedule` again rather than just answering, producing a "Scheduled next session
successfully…" response instead of the expected codeword.

**Fix that resolved it:** make the one-shot prompt an explicit, unambiguous instruction that also
tells the model *not* to use the self-scheduling mechanism — e.g. "Do not schedule anything else.
Just reply with exactly: X" — in plain ASCII with no punctuation for the model to mangle while
copying a command verbatim into a Bash call.

**Applies beyond the test suite:** anyone dispatching a real Keeper one-shot via `lrb schedule`
(including a being self-scheduling its own future work) should keep the `prompt` argument
self-contained and explicit, especially when the target being runs a cheap model. The shared
boilerplate paragraph competes for attention every wakeup.

## See Also

- `lore-beings-design.md` — the Keeper design; the spawn-prompt is the per-wakeup runtime contract
- `lifecycle-testing-harness.md` § Keeper coverage — the C1 scenario where this surfaced
- `haiku-ambiguity-detector.md` — the general "cheap model surfaces ambiguity a strong model
  resolves silently" pattern this is an instance of
