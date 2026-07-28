# A Trap Recorded Only in Lore Still Gets Hit

**A trap recorded only as knowledge protects nobody, including its author.** What works is a
guardrail sitting at the point of use — a check in the script, a named exact command in the doc, a
test — not a topic that has to be recalled first.

Lore is retrieved when a task *cues* it. A one-off shell command does not cue a retrieval.

## Evidence (2026-07-28 session)

In one session I hit two traps already written down in my own lore:

1. **GNU `timeout` on macOS.** Ran `timeout 180 codex exec … 2>/dev/null` to bound a probe.
   `timeout` does not exist on BSD/macOS; it failed with exit 127 and the redirect swallowed the
   error, so the command silently produced nothing. Recorded in
   `portable-shell-in-framework-docs.md` — and `auto-pull.md` warns about this exact failure in
   prose I have edited myself.
2. **`git -C` at a path that is not its own git root.** Ran `git -C <workspace> show
   main:docs/agent-boot.md` to compare doc sizes. The workspace root is itself a git repo (the
   meta-repo envelope), so it resolved there and reported the file as nonexistent. Recorded in
   `git-dash-c-needs-toplevel-guard.md` and `tooling-cwd-safety.md` — I wrote the guard for
   `scripts/lr-core` myself.

Both were caught within a turn, so no damage. The point is the pattern: **I had the knowledge and
it did not fire at the moment of use.**

## Generalization

This is `docs-engines-convention.md` § *Engine traps belong in the binding* generalized past engine
profiles. The binding is one instance of a point-of-use site; others are the script that performs
the operation, the exact command spelled out in a procedure doc, and a regression test.

`macos-var-symlink-realpath-ambiguity.md` is the same principle applied as a fix: the repair was
naming the exact `os.path.realpath()` one-liner rather than describing the comparison.

## Operational consequence

When a session surfaces a trap, ask **"where is the guardrail going to live?"** *before* writing the
topic. If the answer is only "in lore", expect to hit it again. The topic is the record; the
guardrail is the protection — ship both, and if only one is affordable, ship the guardrail.

Corollary for gate design: prefer a deterministic check inside the harness over a human prep step,
because a prep step is exactly a recalled instruction at a moment that does not cue recall — see
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`, where a correctly-executed manual mitigation
still lost.

Two later applications of the same reflex, both from 2026-07-28:

- The single-line registered-shortcut bootstrap was fixed in the doc **and** given a `/lr:check` #18
  clause plus `test_bootstrap_body_is_a_single_line`, because the check is what a user actually runs
  against their own workspace (`template-whitespace-is-contract-under-byte-exact-idempotency.md`).
- Engine-profile selection moved out of boot prose entirely and into `lr-core`'s `detect_engine`:
  when a procedure step's input is a fact about the running environment, the step belongs in the
  deterministic accelerator, not in instructions to a model
  (`engine-profile-must-be-observed-not-believed.md`).

## See Also

- `template-whitespace-is-contract-under-byte-exact-idempotency.md` — doc rule plus check plus test,
  because the doc rule alone was demonstrably not enough.
- `engine-profile-must-be-observed-not-believed.md` — the strongest form: move the step into the
  script rather than guarding the prose.
- `docs-engines-convention.md` § Engine traps belong in the binding — the narrower original form.
- `portable-shell-in-framework-docs.md`, `git-dash-c-needs-toplevel-guard.md`,
  `tooling-cwd-safety.md` — the three topics that failed to fire.
- `macos-var-symlink-realpath-ambiguity.md` — the fix shape (name the exact command).
- `haiku-ambiguity-detector.md` — the sibling reason procedure text must be executable as written
  rather than merely correct.
- `a-gate-cannot-be-a-model-self-report.md` — a gate whose evidence lives in the wrong medium; same
  family of "the safeguard was not where the failure happens".
