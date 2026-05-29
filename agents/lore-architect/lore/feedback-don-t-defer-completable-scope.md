**Rule.** When a sweep or polish task is bounded and mechanical, do it now. Don't put it in the backlog as "vN.1 follow-up" if the work fits in the current session's scope.

## The corrective episode

During the v11 ship, I deferred a "full doc sweep of remaining `<domain>` refs in 12 files" to v11.1, calling it tedious-but-mechanical. The user pushed back: *"Sorry, why didn't you do this and postponed?"* Doing the sweep took ~5 minutes. The deferral added zero value and left the framework half-migrated. The reviewer fan-out then caught the half-migration as a BLOCKER.

## How to apply

When considering deferring work, ask:

- Is it bounded? (Specific list of files, well-defined scope?)
- Is it mechanical? (Disambiguation rules I can state up front?)
- Does deferring leave the system internally inconsistent?

If all three are yes → don't defer. Do the work and ship the change complete.

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
