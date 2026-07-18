# macOS Case-Insensitive Filename Collision With Memory Files

Observed live during the 2026-07-18 architecture review: Claude Code auto-injects a directory's
`CLAUDE.md` as memory context whenever a file under that directory is read — and on
case-insensitive APFS (the macOS default), that filename match is case-insensitive. Reading
`docs/engines/claude.md` (the engine-profile doc, lowercase by the framework's own
`docs/engines/` naming convention — see `docs-engines-convention.md`) triggered Claude Code to
load it a second time as directory memory, because the filesystem treats `claude.md` and
`CLAUDE.md` as the same name.

## Impact

Currently harmless: the same content surfaces twice, wasting a little context, no correctness
issue. But it's a real, non-obvious environmental interaction worth knowing before adding more
per-directory docs whose lowercase name happens to match an engine's memory-file name (`CLAUDE.md`
on Claude Code, `AGENTS.md` on Codex/Cursor — see each engine's binding in `docs/engines/*.md`).
Any future `docs/<subdir>/<name>.md` where `<name>` case-insensitively matches a memory filename
will silently duplicate context the same way.

## Operational Takeaway

When naming a new per-directory doc, check it against the memory filenames of all three engines
(`CLAUDE.md`, `AGENTS.md`) case-insensitively, not just exact match — `claude.md` == `CLAUDE.md`
on macOS APFS even though they'd be distinct on a case-sensitive filesystem (most Linux CI, some
non-default macOS volumes).

Filed as backlog item A5 in `workdir/what-to-improve.md` (rename `docs/engines/claude.md` or
document the quirk) — this topic is the durable "why," that item is the "do."

## See Also

- `claude-engine-capabilities.md` — the Claude engine hub; the memory-file binding lives there
- `docs-engines-convention.md` — the `docs/engines/<engine>.md` naming convention this collides
  with
- `conventions.md` — general framework naming conventions
