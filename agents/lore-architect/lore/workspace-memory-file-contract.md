---
lore: 1
type: topic
summary: "The workspace memory file is AGENTS.md on every engine plus a one-line @AGENTS.md import in CLAUDE.md; the old per-engine fork was a silent whole-engine outage."
parent: lore-context.md
---

# The Workspace Memory-File Contract (v3)

**`AGENTS.md` is canonical on every engine. `CLAUDE.md` carries one `@AGENTS.md` import line and
nothing else.** Landed in v37, replacing the per-engine filename fork.

## The outage this replaced

v25–v36 resolved the memory filename from the engine profile: `CLAUDE.md` on Claude Code,
`AGENTS.md` on Codex and Cursor. Measured behavior (Claude Code 2.1.226): **Claude Code does not
read `AGENTS.md`.** So a workspace carrying only `AGENTS.md` — the ordinary result of initializing
from Codex or Cursor, or of a teammate cloning such a workspace — gave every Claude Code session
*zero* workspace memory. Silently: no error, no warning, nothing in any report.

This dogfood workspace was in exactly that state for eleven versions. It is also why nobody noticed
its payload going stale: no one was reading it.

The general shape is worth carrying: **a per-engine binding on a shared artifact is an outage
waiting for the artifact to be shared.** The fork was correct for a workspace only ever touched by
one engine, and wrong the moment the framework's own premise — cross-engine teams — held.

## The contract

`CLAUDE.md` gets exactly:

    <!-- Lore Framework: this workspace's memory lives in AGENTS.md, shared across engines. -->

    @AGENTS.md

Idempotent by line: if any line's trimmed content is `@AGENTS.md`, do nothing. Never regenerate or
truncate the file — that one line is the only framework-managed content in it.

Measured properties: the import resolves; it composes with unrelated user content in the same file;
and a missing target is inert rather than an error, so write order is not load-bearing.

**Payload v3** — three exact level-2 headings (`## Lore Framework`, `## Repositories`, `## Agents`),
each with a `<!-- lr:managed … -->` provenance comment, replacing the `lr:workspace-init:*`
HTML-comment markers. A managed region runs from its heading to the next `^## `, or EOF —
**ignoring headings inside fenced code blocks**
([self-documenting-payload-vs-heading-delimiters.md](self-documenting-payload-vs-heading-delimiters.md)).
Skill references are engine-neutral (bare name plus a one-line syntax legend), since three engines
read the one file. Repositories lists *declared* repos; Agents lists *registered* agents, rendered
from shortcuts on disk — with the role description read from `<agent-dir>/role.md`, never from the
shortcut, because the Claude Code artifact is a single bootstrap line and carries none.

## Standing risk

The import is engine **behavior**, not a contract. Lifecycle scenario `test_18b` re-verifies it on
every run; that assertion is the only thing that would catch a silent regression, which would
reproduce this exact outage.

## Method note

Settled by experiment, not reasoning: bare temp directories, a unique sentinel per file,
`claude -p` with every file tool disabled so the model could not reach a file it was not given, and
a negative-control case that correctly returned nothing. My prior belief — "one file named
`AGENTS.md` everywhere" — was wrong, and would have shipped the same outage inverted.

## See Also

- [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md) — the v37 surface this landed with.
- [a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) — why the file tools were disabled.
- [measurement-records-name-their-environment.md](measurement-records-name-their-environment.md) — why the engine version is pinned above.
- [macos-case-insensitive-filename-collision-with-memory-files.md](macos-case-insensitive-filename-collision-with-memory-files.md) — the other memory-file trap.
