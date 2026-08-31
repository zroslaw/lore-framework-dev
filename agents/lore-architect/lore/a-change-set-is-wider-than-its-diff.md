---
lore: 1
type: topic
summary: "A contract or logic change touches sites the diff never shows — the test tree that pins the old form, the docstring, the caller's comment, the procedure doc; enumerate the set and grep the changed vocabulary across it."
parent: lore-context.md
---

# A Change Set Is Wider Than Its Diff

**When I change a contract or an algorithm, the sites that encode the *old* one do not appear in my
diff.** They are found by grepping the changed behaviour's vocabulary across the whole tree, not by
re-reading the change. v44's absolute→workspace-relative contract change produced both halves of
this in one session.

## The test tree pins the retired contract

The single v44-attributable lifecycle failure was `test_22_register_agent`, asserting that a
generated shortcut contains the **absolute** agent directory. v44 deliberately made that path
workspace-relative, and the emitted artifact was correct — the *test* encoded the retired contract,
and the v44 draft had never updated it.

This is the gate earning its keep in a way review cannot: four reading passes over the same change
set never noticed, because the test file was not in the diff. **When a change alters a contract,
grep the test tree for assertions on the old form as part of the change.**

The repair was to assert **both directions** — relative form present, absolute form absent — and
then prove the assertion discriminates: green against v44, red against v43. An assertion never shown
red against the previous tree is documentation in a test's clothing
([prove-a-new-test-red-against-the-previous-tag.md](prove-a-new-test-red-against-the-previous-tag.md)).

A stale test is the cheapest possible announcement of a contract change: it names, in an assertion,
exactly which promise the change retired. Treat a red test on a deliberate contract change as
information about the *change set*, not noise to silence.

## Prose adjacent to the code is the other half

Fixing `preflight.py`'s `--agent-dir` resolution, I made the same class of error three times in one
session:

1. Wrote a docstring saying the relative value "is joined onto `<workspace>`", then replaced the
   code with an upward search and left the docstring.
2. Fixed the helper's own docstring but left the **caller's inline comment** above it describing the
   replaced algorithm ("first hit wins, walking to the filesystem root").
3. Left `cmd_preflight`'s step text, `agent-boot.md` and `conventions.md` all describing the join.

This is expensive here specifically because `lr-core` is a **literate accelerator**: those comments
*are* the Script Fallback Contract's manual procedure
([literate-accelerator-pattern.md](literate-accelerator-pattern.md)). A stale comment is not
untidiness — it is a wrong procedure a model executes by hand when the script cannot run, in this
case accepting the first `role.md`-only decoy, the exact mis-boot the fix existed to prevent.

## The rule

Treat a logic or contract change as touching a **set**: the code, its docstring, the caller's
comment, the procedure doc, the placeholder table, and the tests that assert the old form. Grep the
changed behaviour's vocabulary across all of them before calling it done.

The fix-round variant is the same rule applied to my own repairs: after a batch of fixes, re-read
every site that *states* the rule I just changed, not only the site I edited
([a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md)).

## See Also

- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — the enumeration
  must cover sites that *state* a rule, not just sites that implement it.
- [consistency-sweep-read-not-just-grep.md](consistency-sweep-read-not-just-grep.md) — grep verifies
  tokens; only reading verifies facts. The two passes are complementary, not alternatives.
- [script-emits-data-doc-owns-the-words.md](script-emits-data-doc-owns-the-words.md) — which site
  owns which words in the script/doc pair.
- [prove-a-new-test-red-against-the-previous-tag.md](prove-a-new-test-red-against-the-previous-tag.md)
  — proving the repaired assertion discriminates.
- [lifecycle-testing-harness.md](lifecycle-testing-harness.md) — the gate that surfaced the stale
  test after four clean reading passes.
