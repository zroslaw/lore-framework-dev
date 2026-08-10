---
lore: 1
type: topic
summary: "When a change broadens where a value comes from, the validation attached to the old source does not travel with it — re-attach it at the sink."
parent: lore-context.md
---

# Widening a Value's Source Drops Its Validation

**Rule: when a change broadens the *provenance* of a value that feeds a writer, go read what the
writer's existing input path validated and why, then re-apply it. Treat "same value, new source" as
a new input, not as a refactor.**

## The instance (v37, decision D9)

`scripts/workspace-pull` had always refused to write a `.gitignore` line for a directory name
derived from a URL containing `!`, `*`, `?`, or `[`. `url_to_dir()` filtered them, with a comment
explaining that such a line becomes a glob or a negation rather than a path.

v37 widened phase 3 to ignore **every child git repo on disk**, declared or not — taking the name
from `basename` instead of from a URL. The filter lived on the URL path, so the new path had none.
A directory literally named `!notes` is trivially creatable locally even though no git host would
allow it as a repo name, and `/!notes/` in `.gitignore` is a negation that un-ignores something
else. The result would have been silent `.gitignore` corruption.

**Why it slipped.** The design specified D9 in prose — "ignore all child git repos on disk" — and
prose has nowhere to put "and re-run the metacharacter filter". The validation was invisible at the
altitude the decision was made. A TriLens blast-radius reviewer found it; the implementation and my
own self-review did not.

## The corollary the fix forced

Fixing the writer forced a matching decision in the *reader*: what does the scanner report for a
child it cannot ignore? Not the coverage finding (S7, "run `workspace-pull`") — because running
`workspace-pull` can never resolve it. It became a conflict finding (S13, "rename the directory").

**A finding whose suggested remedy cannot resolve it is worse than no finding**: the user runs the
remedy, nothing changes, and they learn to distrust the whole report.

## See Also

- [name-keyed-global-registry-cannot-answer-per-scope.md](name-keyed-global-registry-cannot-answer-per-scope.md) — the other v37 defect found by review, not by design.
- [yaml-parser-shell-hardening-checklist.md](yaml-parser-shell-hardening-checklist.md) — the sibling class of input-hardening trap.
- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — one definition; this is what happens when a *guard* has two entry points instead.
