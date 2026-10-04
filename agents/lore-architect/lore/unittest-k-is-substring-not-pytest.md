---
lore: 1
type: topic
summary: "stdlib unittest -k is substring/glob over test ids, not pytest boolean expressions — compound patterns match nothing."
parent: lore/lifecycle-testing-harness.md
---

# unittest `-k` Is Substring Match, Not pytest Expressions

When selecting lifecycle or other scenarios with `python3 … -m unittest -v -k …`, **unittest treats
`-k` as a simple substring/glob over test method ids** — not pytest's boolean `-k` expressions.

Patterns like `test_14 or test_15` match **no** tests (`NO TESTS RAN`). Prefer:

- the **class name** (e.g. `FinalizeParticipantRevisionScenarios`);
- a **shared substring** present in both ids (e.g. `revise`);
- or a **fully qualified** method: `FinalizeParticipantRevisionScenarios.test_14_finalize_revises_participants`.

Instance: filtering v47 participant-revision scenarios during harness work (2026-10-04).

See [lifecycle-testing-harness.md](lifecycle-testing-harness.md) § Cost and gating.
