---
lore: 1
type: topic
summary: "How I write a lore topic: atomic, plain markdown, kebab-case filename, under 5K tokens, essential-only, with v1 frontmatter on every new file (the schema itself is owned by docs/lore-structure.md)."
parent: lore-context.md
---

# Lore Topic Format

Lore topics are plain markdown files in `lore/`.

- **Filename:** lowercase kebab-case, descriptive of the content, ≤64 chars.
- **Size:** under 5K tokens preferred, can exceed when needed.
- **Content:** atomic — one concept, decision, discovery, or recommendation.
- **Links:** reference other topics by filename; area hubs summarize an area and route to its
  children.
- **Only essential information** — no filler, no general knowledge anyone could look up.
- **Include operational recommendations** when relevant ("if you need to do X, do it through Y").

## Frontmatter

**Every new lore file carries Lore v1 frontmatter.** The schema, the `area`/`topic`/`context` type
system, and the hub/leaf structure are owned by `lore-framework/docs/lore-structure.md` — read it
there rather than from a copy here.

Legacy files predating v1 are frontmatter-free and stay that way until migrated. Migration is lazy
via merge, or explicit via `/lr:groom`; convert a legacy file only when its type, summary, and
parent are clear, and leave ambiguous ones legacy.

Note for anyone reading an old copy of this topic: it previously stated "No frontmatter" as a flat
rule. That was correct before framework v36 and is now wrong — a good illustration of why a stated
rule is a second implementation with its own drift surface
(`single-canonical-source-discipline.md`).

## See Also

- `lore-context-shape-discipline.md` — the sibling rule for the root context file: shape over size.
- `scripted-prose-edit-needs-a-read-back.md` — how to edit these files' long bullets safely, and
  what a scripted edit cannot see about the prose it writes.
- `single-canonical-source-discipline.md` — why the field schema is pointed at, not restated here.
- `naming-foundational-principles.md` — when a framing deserves its own topic at all.
