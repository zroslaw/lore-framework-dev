---
lore: 1
type: topic
summary: "Scripted line-index editing of long role.md / lore-context.md bullets is the right tool but is blind to nested-bold corruption and wrong above/below cross-references — read the prose back."
parent: lore-context.md
---

# A Scripted Prose Edit Needs a Read-Back

Long `role.md` / `lore-context.md` bullets are single logical lines too long for reliable `sed`, so
python line-index replacement is the right tool. It is also blind to everything about the *prose* it
writes. Two defects landed in one edit on 2026-08-22, both invisible to the script and both needing
a second pass:

1. **Nested bold.** `**Header (v15+; **on request since X**)** —` is broken markdown: adding
   emphasis *inside* an already-bold span silently corrupts it. Keep an inserted phrase
   unemphasized inside a bold header.
2. **Cross-reference direction.** I wrote "same reasoning as the gate **above**" in a bullet sitting
   *before* its referent. Sibling bullets get reordered over time and get referenced from memory of
   the conversation rather than from file order — resolve every "above"/"below" against the actual
   line numbers before writing it.

## Mechanics that worked — keep them

- **Assert both span boundaries** — the first line's prefix *and* the last line's content — before
  slicing. A first attempt that asserted only the start plus a guessed end line aborted cheaply,
  because the assertion ran before any write.
- **Apply replacements bottom-up** by line index, so earlier spans stay valid when a replacement
  changes the line count.
- **Re-run `lr-core lore-map`** afterwards: one call validates new v1 frontmatter, confirms the file
  is reachable in the taxonomy, and reports `lore_context_estimated_tokens` against the 10K target.

## See Also

- `lore-context-shape-discipline.md` — what the file being edited is for.
- `lore-topic-format.md` — the format rules the edit has to preserve.
- `fix-defects-are-context-errors.md` — the same shape one level up: defects introduced by a fix
  concentrate in the prose describing it.
