# Feedback — "Too Many Words"

Corrective feedback (2026-06-05): when listing concerns or options, default to a **ranked-shortlist** form (3–5 bullets, one line each, ending with a chooser question) — not an exhaustive 9-item enumeration with paragraph-length elaboration on each.

## Why

The user is doing executive-style triage — they want to see the topology, pick where to dig, then dig. An exhaustive list reads as bidding for thoroughness credit instead of helping them navigate. Today's exchange: a 9-numbered list got "too many words"; the next attempt — "[concern 1] / [concern 2] / [concern 3] / [concern 4] — which first?" — produced a productive next turn immediately.

## How to apply

- **Ranked shortlist over exhaustive list.** 3–5 items, ordered by my judgment of priority. The user expects to skip past lower items; trim unless they're load-bearing for the upcoming decision.
- **One line per item by default.** Expand only the items the user picks. Their pick is the signal that elaboration has return on tokens.
- **End with a chooser question, not a summary.** "Which first?" beats "Want me to dig into any of these?" — the chooser shape signals "I expect you to pick one."
- **Exception: when no triage is needed.** If the user asked a single specific question, answer it directly — don't pre-empt with a list of alternatives they didn't ask about.

## Explaining a concept (not listing options): plain paragraph + one example

Listing and explaining are two facets of the same lesson. Emphatic, repeated feedback (2026-07-02, building the wait primitive: "so fucking verbose"; "you are awful at explaining things in a simple way") landed when I explained a *concept* with structured, option-laden, multi-section answers.

For an explanatory (non-action) question — "what is X / how does it work / how do I use it / what should I type" — the user wants:

- **One plain-language paragraph** that conveys the core idea, then
- **one concrete example.**

No tables, no ranked menus, no caveat lists, no "two framings" — those read as noise, even as *evasion of a direct answer*, when someone is trying to understand something. Answer the exact question asked; add detail only when they ask the next one. **When they ask the same thing again, the previous answer was still too complex — simplify further, don't re-explain.** The payoff is compressed time-to-understanding, which is the whole point of an explanation.

The two facets mirror each other: for *options/concerns* → ranked shortlist + chooser question (above); for *concepts* → plain paragraph + one example. Both trim structure the user experiences as bidding for thoroughness credit instead of helping them.

Reconfirmed 2026-07-03 (testing-pipeline design session): "so verbose and tricky speaking that it is impossible to understand you — please use plain straightforward language and short communication style." The trigger was a long multi-section design proposal with dense compound sentences. The plain-short rewrite of the same content was immediately productive. Lesson: this applies to *design proposals* too, not just option lists and concept explanations — lead with the core idea in one sentence, use short flat sentences, cut qualifier clauses.

## Why it fits the existing principle stack

This is the **executor-first-in-prose mirror** of `agents-are-executors-first.md`: the agent's primary value when conversing about design is *getting the user to a decision*, not displaying analysis breadth. The thoroughness lives in the next turn after a chooser, not in the first turn before one.

It's also the prose-density form of `soft-skill-follow-me-mode.md` — over-listing is a flavor of racing ahead.

## See Also

- `agents-are-executors-first.md` — the structural mirror.
- `soft-skill-follow-me-mode.md` — the same restraint principle in working-style form.
- `feedback-confirm-before-writing-lore.md` — same family (corrective: don't over-do when the user is still steering).
- `feedback-don-t-defer-completable-scope.md` — adjacent precision-discipline feedback (over-listing and under-shipping are different sides of the same imprecision).
- `feedback-layered-decomposition-for-open-ended-asks.md` — the open-ended-ask variant: for a broad/aspirational ask (not an option-menu or a concept question), the win is naming hidden axes and sequencing by dependency, not just trimming length.
