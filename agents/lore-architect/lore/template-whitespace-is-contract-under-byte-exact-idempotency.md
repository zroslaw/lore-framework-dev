# Template Whitespace Becomes Contract Once a Check Is Byte-Exact

The registered-shortcut bootstrap lives in each engine profile as a fenced markdown block. It was
wrapped across three lines so it read well inside the doc, while `register-repo.md`'s Claude
template said to write "exactly this single line." Executing migration 33 I copied the profile's
wrapping verbatim and produced a three-line shortcut.

It looked harmless and was not:

- **`migrations/33.md` classifies an existing shortcut as `current` only on a byte-for-byte match**
  against a freshly generated artifact. A differently-wrapped file is never `current`, so every
  upgrade rewrites a shortcut that was already correct.
- **Claude Code renders a slash command's description from the file's first line.** A wrapped
  bootstrap shows up in the command list as a sentence fragment.

## Two lessons

1. **A doc that displays a template will have that template copied exactly as displayed**, wrapping
   included. Readability formatting in the source is indistinguishable from content to the executor
   — there is no channel in a fenced block that says "this newline is decorative." If the artifact
   must be one line, the fenced block must be one line.
2. **Once any check compares bytes, whitespace is semantics.** Byte-exact idempotency is a good
   design — it is what makes "already current, leave it alone" decidable — but it silently promotes
   every formatting choice into the contract. Say so explicitly wherever the template is authored,
   because the author of the template and the author of the check are usually not thinking about
   each other.

## Applied

Unwrapped the bootstrap in all three engine profiles, stated the rule canonically in
`register-repo.md` § Resolve the shortcut bootstrap, added a single-line clause to `/lr:check` #18,
and added `test_bootstrap_body_is_a_single_line`.

**The doc rule alone was not enough** — the check is what a user actually runs against their own
workspace, and the test is what stops the profiles drifting back. Same reasoning as
`point-of-use-guardrails-beat-recorded-lore.md`.

## See Also

- `registered-shortcuts-are-framework-owned.md` — why byte-exact regeneration is the right model for
  these artifacts in the first place.
- `point-of-use-guardrails-beat-recorded-lore.md` — why this needed a check and a test, not just a
  sentence in a doc.
- `single-canonical-source-discipline.md` — the profiles hold the template; `register-repo.md` holds
  the rule about it.
- `docs-engines-convention.md` — the three profiles that carry the bootstrap block.
- `consistency-checks.md` — check #18 and its new single-line clause.
