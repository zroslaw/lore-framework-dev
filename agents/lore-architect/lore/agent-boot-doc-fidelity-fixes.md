The lifecycle testing harness's (`lifecycle-testing-harness.md`) first real use (2026-07-03) found two genuine bugs in `agent-boot.md` — not by review, but by running haiku against it and watching it fail. Both are now fixed on disk. Case study for the general principle in `execution-testing-catches-blind-ambiguity.md`.

## Bug 1 — "current working directory" was ambiguous under a weaker model

Step 1 said "search all directories in the current working directory." Haiku, having just read `agent-boot.md` from the plugin directory, anchored its search there instead of the actual process cwd, then escalated to a filesystem-wide `find /Users/yaroslav ...` when nothing matched — which is also what triggered macOS TCC permission prompts for Photos/Music the user noticed (a broad `find` walking the whole home directory, not a real permissions problem). Sonnet never made this mistake in any run. Traced via `--output-format stream-json --verbose`, which shows every tool call — the final-text-only `--output-format json` would not have revealed this.

**Fix (shipped):** step 1 now says the cwd is "the directory this session was invoked from (run `pwd` first if unsure; this is *not* the plugin/framework directory you just read this file from)" and explicitly forbids widening the search beyond cwd.

## Bug 2 — "best-effort" was misread as "optional to attempt"

Step 2 (auto-pull) said "best-effort — never blocks boot." Haiku skipped the step outright — jumped from discovery straight to reading role.md/lore-context.md, never running `git pull`. Hypothesis: it over-generalized "never blocks boot" (which describes failure handling) into "doesn't need to happen" (skippable entirely).

**Fix (shipped):** reworded to "Always perform this step — do not skip it... 'best-effort' describes how failures are handled... not whether to attempt it."

## Outcome

Before fixes: haiku boot pass rate was roughly 50% across the 3 original boot scenarios, with the permission-prompt side effect as a visible symptom. After both fixes: 6/6 clean across 2 full trials, and every later scenario built this session (recall, reflect, merge, consult, attach, summarize, finalize e2e, the repo/workspace group) passed on the first attempt with no further doc changes needed.

## Debugging technique, worth reusing

When a lifecycle scenario fails, don't just read the final text output — rerun manually with `--output-format stream-json --verbose` piped through a small Python filter that prints each `tool_use` block. That's what pinpointed both bugs precisely instead of guessing from symptoms (e.g. the permission-prompt reports).

## A third, later instance (defer-clarity)

A subsequent harness run (2026-07-04, haiku) surfaced a third `agent-boot.md` fidelity issue of the same shape: haiku conflated a *deferred* version upgrade with *boot failure*, because the alarming "cannot auto-upgrade" message sat inline while the "this isn't a failure, keep going" reassurance was buried. The fix hoists the reassurance adjacent to the alarming message (`agent-boot.md` step 3 + `version-check.md` defer points). Full write-up and the generalizable rule live in `haiku-ambiguity-detector.md`; that fix is staged, not yet applied to the real framework (`port-landing-next-steps.md`).

## See Also

- `execution-testing-catches-blind-ambiguity.md` — the general principle this is a case study for.
- `haiku-ambiguity-detector.md` — the sharpened weak-model form + the third (defer-clarity) instance.
- `lifecycle-testing-harness.md` — the harness that found these.
- `multi-engine-portability-direction.md` — the "framework is prose" risk this is direct evidence for.
