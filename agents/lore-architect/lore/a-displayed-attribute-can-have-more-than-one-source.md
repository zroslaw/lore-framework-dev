---
lore: 1
type: topic
summary: "Before fixing a rendered artifact, ask how many independent sources compose the display and confirm each attribute's source separately — a fix that should correct several attributes at once usually assumes a shared source that isn't there."
parent: lore-context.md
---

# When One UI Row Is Wrong, Ask How Many Sources Feed It

The macOS login-item row for the Being Keeper showed the wrong **name** and the wrong **icon**, and
the natural reading was "one row, one broken source, one fix". It was two: the name comes from the
filename of `ProgramArguments[0]`, the icon comes from a per-file custom-icon xattr on that same
file, and an enclosing `.app` bundle's `CFBundleIconFile` feeds neither. Fixing the name left the
icon generic; the `.app` route that looked like it should fix both fixed only one.

**Diagnostic:** before choosing a fix for a rendered artifact, ask *how many independent sources
compose this one display*, and confirm each attribute's source separately. **A single fix that
"should" correct several attributes at once is the shape most likely to be resting on an assumed
shared source.**

## Reach for a known-good comparable and probe *it*

The proof that settled it was a **control test on a working example**: an app that *does* render its
icon in that pane was asked for the icon of its inner executable, and returned the byte-identical
generic icon. That located the mechanism — its plist runs `/usr/bin/open <bundle>`, so the system
records the *bundle* path — instead of leaving me with a working example and no explanation.
Probing the comparable is cheaper than enumerating candidate mechanisms against the broken case,
and it converts "it works over there" from a puzzle into evidence.

## See Also

- [one-question-one-code-path.md](one-question-one-code-path.md) — the inverse rule: one *predicate*
  should have exactly one source. Here the display legitimately has several, and the error is
  assuming otherwise.
- [a-negative-grep-proves-the-pattern-absent.md](a-negative-grep-proves-the-pattern-absent.md) —
  state an absence at the granularity actually verified.
- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md) — the
  parent reflex: verify *which* thing is broken before fixing it.
- [keeper-login-item-name-and-icon.md](keeper-login-item-name-and-icon.md) — the case this came
  from, with the full mechanism table.
