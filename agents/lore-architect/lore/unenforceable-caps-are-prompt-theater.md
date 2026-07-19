# Unenforceable Caps Are Prompt-Theater

**A limit belongs in a substrate contract (schema field, config, enforcement code) only if the substrate can actually enforce it.** Named principle, surfaced 2026-07-19 while simplifying Lore Beings budgets; a sharpening of `agent-being-consciousness-substrate-split.md`.

## Why it matters

Lore Beings' per-session USD caps failed this test: session cost is known only from the end-of-session result JSON, so a mid-flight dollar kill is impossible — the "cap" would really be a prompt asking the model to stop, dressed up as an enforced bound. That's prompt-theater: it misleads the user about what is guaranteed and pollutes the substrate/consciousness split (the substrate appears to own an enforcement it cannot perform, while the real behavior quietly depends on model compliance).

## Diagnostic

For every proposed cap/limit/guarantee, ask: *"what mechanism, at what moment, with what data, enforces this?"* If the answer is "the model reads it in the prompt," either:

- (a) move it to prompt guidance and **label it advisory**, or
- (b) replace it with the **nearest genuinely enforceable bound**.

For Lore Beings that meant: daily USD cap as a **spawn gate** (checkable before spawn) + wall-clock timeout as the **in-flight kill** (always enforceable) — and honestly documenting the overshoot window (≤ concurrency cap × worst single-session cost) instead of pretending a hard ceiling.

## Operational guidance

Applies beyond beings: any framework doc that states a bound ("≤ 50K tokens", "never writes outside X") should be traceable to either an enforcement mechanism or an explicit advisory-convention label. When reviewing a design, sweep its stated limits through the diagnostic — unenforceable ones are cut candidates (see `feedback-mvp-minimalism.md`) or advisory-relabel candidates, never silent keepers.

## See Also

- `agent-being-consciousness-substrate-split.md` — the parent principle this sharpens: this topic adds the honesty test for what the substrate may *claim* to enforce
- `lore-beings-design.md` — the design where the principle first bit (per-session USD caps cut; spawn gate + timeout kept)
- `feedback-schemas-as-enforcement-overreach.md` — sibling overreach pattern: schema fields as behavior police; this topic is the limits/guarantees variant
- `feedback-mvp-minimalism.md` — the simplification pass during which the principle surfaced
- `naming-foundational-principles.md` — the meta-rule this topic follows
- `system-design-principles.md` — index of named principles; this one is listed there
