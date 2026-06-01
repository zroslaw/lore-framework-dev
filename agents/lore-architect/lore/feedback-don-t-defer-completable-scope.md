**Rule.** When a sweep or polish task is bounded and mechanical, do it now. Don't put it in the backlog as "vN.1 follow-up" if the work fits in the current session's scope.

## The corrective episode

During the v11 ship, I deferred a "full doc sweep of remaining `<domain>` refs in 12 files" to v11.1, calling it tedious-but-mechanical. The user pushed back: *"Sorry, why didn't you do this and postponed?"* Doing the sweep took ~5 minutes. The deferral added zero value and left the framework half-migrated. The reviewer fan-out then caught the half-migration as a BLOCKER.

## The v14 sharpening — don't merely OFFER, either

A second instance, this time about *offering* rather than back-logging. After surfacing a review finding (the manifest-version-frozen-at-`1.0.0` cache root cause), I *offered* to add the enforcing `/lr:check` #19 rather than just doing it. User: **"yes, you should have done it above — fix the update."**

Sharpening: the rule isn't only "don't defer to a later session" — it's also **don't merely OFFER a clearly-correct, bounded completion; just do it.** When the altitude-correct completion is obvious and bounded (here: a consistency check enforcing a convention I was already codifying), execute it in the same pass and show the result, rather than ending the turn with "want me to…?". Offering when the answer is obviously yes adds a round-trip and reads as deferral.

The distinction: **obvious-correct-completion → do it; genuine-fork → ask.** Still ask when there's a real choice — scope, outward-facing/irreversible actions, or genuine user preference. (In the same v14 session, the AskUserQuestion forks — ship scope, commit landing, HTTPS-reframe — were legitimate asks; the manifest-check enforcement was not.)

## How to apply

When considering deferring work, ask:

- Is it bounded? (Specific list of files, well-defined scope?)
- Is it mechanical? (Disambiguation rules I can state up front?)
- Does deferring leave the system internally inconsistent?

If all three are yes → don't defer. Do the work and ship the change complete. And if the completion is obvious and bounded, don't pause to offer it — just do it and show the result.

## Defer only when

- The work is open-ended (e.g., "design vector-DB indexing").
- It requires real-world feedback first (e.g., "decide whether to add `--ff-only` based on user reports").
- It's a future capability that can wait (e.g., "per-entry overrides in `repos:`").

## Smell of bad deferral

"We can do this later, it's just a sweep." If it's just a sweep, do the sweep.

## Connected feedback

The user's earlier "too complex, simpler, wording and ideas" cue earlier in the same session — both about not over-elaborating *and* about not under-shipping. Different sides of the same precision discipline.

## See Also

- `framework-improvements-backlog.md` — the legitimate backlog. Use it for genuinely-future work, not for procrastination. Items there pass the three-question test (open-ended / needs feedback / future capability) — bounded mechanical sweeps do not.
- `parallel-reviewer-fanout-pattern.md` — the half-migration was caught by review, but should have been avoided in the first place.
