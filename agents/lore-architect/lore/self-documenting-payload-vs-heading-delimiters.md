---
lore: 1
type: topic
summary: "A natural-syntax delimiter collides with content — most sharply with the documentation of the delimiter itself; check what happens when your docs are treated as data."
parent: lore-context.md
---

# Self-Documenting Payloads Collide With Natural-Syntax Delimiters

Switching a managed region from an **escape-sequence** delimiter (HTML comments, sentinels) to a
**natural-syntax** one (markdown headings) buys readability and pays for it in ambiguity: the
delimiter now collides with ordinary content — and most sharply with the *documentation of the
delimiter itself*.

## The instance (v37)

The workspace memory file's managed sections are delimited by exact level-2 headings
(`## Lore Framework`, `## Repositories`, `## Agents`) — deliberately replacing HTML-comment markers
so the file reads as a real document rather than generated goo.

But the canonical payload is *documented* as a fenced block containing those literal heading lines,
and it is reproduced in `README.md` and `FIRST-STEPS.md`. A user who pastes the example into their
own `AGENTS.md` as a note would have had it read as a real heading. Headings decide where a managed
region **ends** — so the next regeneration could overwrite an arbitrary amount of their own prose.

Fix: boundary detection ignores every line inside a ``` or `~~~` fence, in both the prose rule and
the scanner (`workspace_scan.outside_fences`).

## The check to run

Whenever a format is self-documenting, **ask what happens when the documentation is treated as
data.** Specifically: fenced code, quoted blocks, and anything a user would plausibly copy out of
the docs and paste into the file the format governs. In this framework that question has teeth,
because the docs *are* the product and users are told to read them.

The trade is still right — markers were genuinely worse to live with — but it converts a parsing
problem into a content-collision problem, and content collisions are the ones that destroy user work
rather than merely erroring.

## See Also

- [workspace-memory-file-contract.md](workspace-memory-file-contract.md) — the format this governs.
- [template-whitespace-is-contract-under-byte-exact-idempotency.md](template-whitespace-is-contract-under-byte-exact-idempotency.md) — the sibling case: format details becoming load-bearing.
