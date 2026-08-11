# A Gate Cannot Be a Model Self-Report

**A gate must not be implemented in the medium it is gating.** If the failure mode is "the model
executed against the wrong material", the check cannot be "ask the model what material it had" —
that is asking a program to verify its own binary.

## The concrete instance (2026-07-27/28)

The A7 plugin-identity gate (`lifecycle-harness-plugin-identity-unverified.md`) exists to prove the
lifecycle suite ran against the tree under test. On Cursor it was implemented as an **engine-side
probe**: a prompt asking the model to report which plugin root supplied its `lr` skills, including
the instruction "if an installed/cached plugin overrode `--plugin-dir`, report the override path
instead."

It passed while being wrong. The probe recorded `PLUGIN-IDENTITY-OK 31 <worktree>` and the suite
then ran against an installed **v30** plugin.

**Mechanism:** the model checked `--plugin-dir` first (as told), read that tree's `VERSION`, and
reported 31 — truthfully. It never noticed that a *different* tree was actually serving its skills.
Noticing that requires knowing which files you were fed, which is exactly what a model cannot
introspect. The instruction to "report the override path instead" was unexecutable, not ignored.

Codex had this right from the start — `check_codex_plugin_sources()` reads `~/.codex/config.toml`
and the plugin cache off the filesystem, deterministically, before any engine call. Cursor had no
such check, so the model probe *was* the whole gate. The asymmetry was invisible because both
engines "had A7 coverage" — a coverage checkbox hid an evidence-class difference.

## Applied

`check_cursor_plugin_sources()` now walks `~/.cursor/plugins/{local,marketplaces,cache}` and rejects
any tree whose `VERSION` differs from `LR_FRAMEWORK_DIR`. Filesystem only, no engine call. Run
against the real machine state it named both stale v30 trees immediately.

## Diagnostic

When adding a gate, ask: **what evidence does this rest on, and could the thing being tested have
produced that evidence?** If yes, it is not a gate — it is a self-report wearing a gate's name.

Corollary for review: "engine X and engine Y both have coverage for this" is not a parity claim
until you check what *class* of evidence each one rests on.

## See Also

- `engine-profile-must-be-observed-not-believed.md` — the sibling one layer down: a gate must not be
  implemented in the medium it gates; a *binding* must not be selected by the thing it binds. Same
  diagnostic question, applied to engine-profile selection at boot.
- `lifecycle-harness-plugin-identity-unverified.md` — the gate this rule was learned on.
- `cursor-cloud-plugin-rehydrates-over-plugin-dir.md` — the environment behavior that made the
  false pass possible.
- `execution-testing-catches-blind-ambiguity.md` — sibling: a strong-model reviewer cannot see
  ambiguity it silently resolves; here a model cannot see material it was silently handed.
- `lore-beings-mvp-takeover-review.md` — the same family (trusting a verdict whose production
  conditions were never checked), via a blocked capability rather than substituted material. The
  candidate topic name for that family is `sandbox-degraded-review-blind-spot.md`; see `role.md`
  § Sandboxed-review blind spot for the promotion bar.
- `post-convergence-edits-need-their-own-gate.md` — the adjacent rule about *which artifact* a gate
  result belongs to.
- `point-of-use-guardrails-beat-recorded-lore.md` — why the fix belongs in the harness rather than
  in a human prep step.
- `prove-a-new-test-red-against-the-previous-tag.md` — the same diagnostic applied to a test suite: a
  green suite written by the author of the fix is a self-report until each test is shown red against
  the previous tag.
- `independent-engine-review-catches-structural-blind-spots.md` — an adjacent but distinct family:
  a fully-functional review still misses things a *different engine* catches, with no environmental
  defect or silent substitution involved.
