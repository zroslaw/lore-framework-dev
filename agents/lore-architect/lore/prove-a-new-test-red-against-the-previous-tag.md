---
lore: 1
type: topic
summary: "A new test is only evidence once it has been shown red against the previous release tag and green against HEAD; run it in a detached worktree via LR_FRAMEWORK_DIR."
parent: lore-context.md
---

# Prove a New Test Red Against the Previous Tag

After fixing the v38 defects I added 27 tests and the suite went green. **Green proves nothing on its
own:** a test written against code you just wrote passes by construction, so "the suite is green" is
a self-report wearing a gate's name (`a-gate-cannot-be-a-model-self-report.md`).

The cheap check that turns it into evidence:

```
git -C lore-framework worktree add --detach <path> <previous-tag>
LR_FRAMEWORK_DIR=<path> python3 tests/<new-test-file>.py
git -C lore-framework worktree remove <path> --force
```

**Every new test must be red against the previous tag and green against HEAD.** On v38 this produced
9 failures and 5 errors at `lr--v1.37.0`, and the split was itself informative:

- `FAIL` — the old code did the wrong thing. This is the real regression guard.
- `ERROR` — the symbol did not exist yet. This is new-surface coverage.
- **Green on both sides** — the test exercises something the fix did not change. Rewrite it or drop
  it; it is padding the count, not the coverage.

## Notes

- A worktree is the right tool because the tests locate the plugin under test via `LR_FRAMEWORK_DIR`,
  so the old and new trees coexist without disturbing the working checkout.
- `git -C <repo> worktree add <relative-path>` resolves the path relative to **`<repo>`**, not the
  cwd — mine landed in `lore-framework/.worktrees/` rather than the workspace's. Remove it from
  inside the repo and `rmdir` the empty parents, or it lingers as a phantom entry. Full form of this
  trap: `tooling-cwd-safety.md`.
- **Put it in the ship record.** "Every new test verified red before the fix" is a claim a reviewer
  can check; "tests added: 27" is not.

## See Also

- `a-gate-cannot-be-a-model-self-report.md` — the rule this implements: a gate must not be
  implemented in the medium it gates, and a suite grading its own author is exactly that. Its
  § deterministic-test form is the complement to red-then-green: a *string-containment test over
  prose* can be red against the previous tag and still be a self-report, because it only proves the
  doc still says what its author wrote.
- `a-red-test-may-be-asserting-a-true-fact.md` — the mirror case on the other side: before turning a
  red test green, establish which side is wrong.
- `point-of-use-guardrails-beat-recorded-lore.md` — this belongs in the test-writing step, not only
  in lore.
- `tooling-cwd-safety.md` — the `git -C` relative-path framing gotcha in full.
- `versioning-release-types.md` — the v38 entry, where the red-then-green claim is recorded.
