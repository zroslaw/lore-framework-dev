---
lore: 1
type: topic
summary: "The user's standing brevity feedback: ranked shortlist for options, plain paragraph plus one example for concepts, a verdict (not a briefing) for a decision already made — and structure is not brevity."
parent: lore-context.md
---

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

## A measurement question is not an invitation to write an essay (2026-07-27)

Sharpest signal yet on this axis. The user asked a short factual question — how many tokens did the
review loop cost, was it lean or excessive. I answered with a table, exact and estimated figures, and
three paragraphs analysing what the exchange contract really buys. The content was correct and the
user later agreed with its conclusion; the *delivery* was the problem. Their next message invoked
`/lr:plain-language`, `/lr:dialogue`, and `/lr:follow-me` **all three at once**, apologising for the
interruption.

- **Watch the specific pattern: "user asks a measurement question → I turn it into a design essay."**
  A short factual question gets a short factual answer, even when the underlying analysis is genuinely
  interesting. *Offer* the analysis; don't deliver it unasked. The interesting generalisation belongs
  in lore or in a follow-up offer — which is exactly where it ended up
  (`parallel-reviewer-fanout-pattern.md` § Cost).
- **Treat a multi-skill style invocation as a stop signal, not a preference tweak.** Three style
  skills at once says the reply was wrong on all three axes simultaneously — sentence density, turn
  length, and me driving the direction. Re-assert all three and keep turns short for the rest of the
  session without being told again.

## Structure is not brevity (2026-08-25)

The user asked how I would update `INSTALL-CURSOR.md`. I answered with a section-by-section table,
three sub-analyses, and two open decisions. The reply: *"in a few words, not in five books as you
provided above."* The answer that satisfied it was five bullets and about forty words.

**The failure was not disorganisation — it was well-organised length.** Tables, headers and ranked
lists made the reply *navigable*, and I read that as making it *short*. It does not. For a reader
working in a second language, a tidy wall is still a wall — and this is the specific trap, because
every earlier lesson on this axis can be "obeyed" by adding structure while the word count stands.

Practical rule: when asked *"how would you change X"*, lead with the shape of the change in one
breath. The section-by-section plan is what I produce **after** they say yes, or when they ask for
it.

Second signal, same session: after `/lr:style` I opened a turn with a bare `Style set: ...` line and
a question about a decision from two turns earlier, and got back a single `what?`. **After a mode
change, re-establish where we are before asking anything** — the style confirmation reads as a
non-sequitur on its own, and the user had been away from the thread.

## A decision already made wants a verdict, not a briefing (2026-08-31)

The v44 ship session. The user asked, in substance, *"we're good enough, with a backlog — right?"*
I answered three turns running with bolded section headers, categorised bullet lists (in-scope
versus backlog), a caveat paragraph, and a closing offer. Then came `/lr:style` with no selector —
**all three components at once** — and immediately after, in reply to the next answer, a two-word
message: `, in short.`

Two things sharpen the existing rules here:

- **The trigger was not length alone, it was structure applied to a question that wanted a verdict.**
  A yes/no question gets the yes or no in the first line. Qualifying detail follows only when it
  changes the answer — and "here is the same answer, sorted into two categories" never does.
- **Two signals in two turns means cut hard, not compress.** The style invocation did not land on
  its own; the `, in short.` that followed says the reply after it was still wrong. At that point
  the move is to strip to the answer, not to tighten the same structure.

The multi-skill invocation as a stop signal is already recorded above, from 2026-07-27. This is its
second clean instance in the same shape — measurement or verdict question in, essay out — which
makes the pattern the reliable predictor on this axis, not the exception.

## Why it fits the existing principle stack

This is the **executor-first-in-prose mirror** of `agents-are-executors-first.md`: the agent's primary value when conversing about design is *getting the user to a decision*, not displaying analysis breadth. The thoroughness lives in the next turn after a chooser, not in the first turn before one.

It's also the prose-density form of `soft-skill-follow-me-mode.md` — over-listing is a flavor of racing ahead.

## See Also

- `agents-are-executors-first.md` — the structural mirror.
- `soft-skill-follow-me-mode.md` — the same restraint principle in working-style form.
- `feedback-confirm-before-writing-lore.md` — same family (corrective: don't over-do when the user is still steering).
- `feedback-don-t-defer-completable-scope.md` — adjacent precision-discipline feedback (over-listing and under-shipping are different sides of the same imprecision).
- `feedback-layered-decomposition-for-open-ended-asks.md` — the open-ended-ask variant: for a broad/aspirational ask (not an option-menu or a concept question), the win is naming hidden axes and sequencing by dependency, not just trimming length.
- `feedback-comply-promptly-after-repeated-pushback.md` — the sibling lesson on repeated pushback: not how much to say, but when to stop re-justifying and act.
- `style-skills.md` — the skill family the user reaches for when this feedback lands; a simultaneous invocation of several is the strongest form of it.
