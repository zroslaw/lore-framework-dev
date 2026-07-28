# Registered Shortcuts Are Framework-Owned

Generated per-agent shortcuts are migration artifacts, not user-owned configuration. A shortcut that
identifies its owned agent directory is recognized as framework-owned and must be regenerated in full
when the framework's generated form changes. This includes a user-modified boot path, frontmatter, or
instructions: preserving those edits can retain a known broken form and makes the generated artifact's
authority ambiguous.

Recognition is the boundary. Never create a missing optional registration, overwrite an unrecognised
artifact, or replace a shortcut that identifies a different agent directory; the latter is a collision.
The v32 version-agnostic form exposed why this is necessary: existing registered shortcuts otherwise
retain the cache-version-pinned boot path that the new generator removed. A normal boot or update
migration is the appropriate way to refresh recognized existing registrations.

## Three-engine delivery rule

Migration, release, and doctor guidance for shortcut repair must name the engine-native Claude, Codex,
and Cursor entry points and cache-refresh commands explicitly. A generic `/lr:` instruction is not a
portable remedy: shortcut invocation and plugin refresh are engine bindings, not shared syntax.

## Byte-exact classification makes the template's whitespace load-bearing

Because a shortcut counts as `current` only on a byte-for-byte match against a freshly generated
artifact, every formatting choice in the authored template — including line wrapping inside a fenced
block in an engine profile — is part of the contract. A wrapped bootstrap is never `current`, so
each upgrade rewrites an already-correct file, and Claude Code renders the shortcut's description
from its first line, so the command list shows a fragment. Enforced by `/lr:check` #18 and
`test_bootstrap_body_is_a_single_line`. See
`template-whitespace-is-contract-under-byte-exact-idempotency.md`.

## See Also

- `template-whitespace-is-contract-under-byte-exact-idempotency.md` — the general rule behind the
  single-line bootstrap requirement.
- `fix-the-pointer-not-the-shipped-migration.md` — preserve historical migration records; correct or
  add the live migration path that repairs current artifacts.
- `docs-engines-convention.md` — engine bindings are the point-of-use source for portable execution.
- `slash-command-system.md` — generated per-agent shortcut shapes and registration surface.
