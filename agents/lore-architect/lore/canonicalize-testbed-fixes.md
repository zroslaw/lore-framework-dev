# Canonicalize Testbed Fixes — Verify What's Actually Persisted

When a fix is developed in a **separate (testbed) session** — a throwaway run, a sibling Claude session, a manual experiment — **verify what actually landed on disk before declaring it done.** In-session/ephemeral fixes can produce a green run without ever being persisted, so a fresh invocation re-fails.

## The instance (2026-06-07)

The testbed got a clean ULA run partly via a **`$schema`-strip that was only an in-session action** — it was never written into the workflow file. The disk workflow still passed raw schemas, and all five schema `.json` files still carried `$schema`. A fresh `/lr:df-ula-file` would have re-failed with `no schema with key or ref …`. Caught by **grepping the actual file state**, not by trusting "it ran green." The canonical fix (the `noMeta` strip in `ula-file-pass.js`) had to be added even though "it already worked once."

## Two-session clobber risk (companion hazard)

When two sessions edit the **same framework file**, it's **last-write-wins** — silent loss. This session the testbed wrote the `args`-parse guard into `ula-file-pass.js`; the in-context copy in the other session went stale, and a naive write would have clobbered the guard.

**Rule:** if another session may have touched a file, **re-read it immediately before editing.** The harness "file unchanged since last read" check is the cheap confirmation — let it fail rather than blind-overwrite. Same family as the spawn-teammate concurrent-write / last-write-wins caveat.

## Operational rules

- **"It ran green once" ≠ "the fix is on disk."** A passing testbed run can depend on ephemeral in-session state. Confirm the canonical artifact (the committed/on-disk file) carries the fix.
- **Grep/inspect the actual files**, don't reason from the run result. (Mirrors `verify-before-acting-on-suspected-bugs.md`: verify state directly; and `consistency-sweep-read-not-just-grep.md`: a clean run is even weaker evidence than a clean grep.)
- **Re-read before editing any file a parallel session might own.** Last-write-wins eats silent edits.

## See Also

- `verify-before-acting-on-suspected-bugs.md` — verify state directly before acting; this is the persistence-side instance.
- `consistency-sweep-read-not-just-grep.md` — sibling verification-gap lesson from the same session.
- `df-module-conventions.md` — the DF workflow-authoring checklist; the `$schema`-strip and args-guard are the fixes that had to be canonicalized.
- `workflow-primitive-operational-notes.md` — where both workflow fixes live operationally.
- `spawn-teammate-feature.md` — the concurrent-write / last-write-wins caveat this generalizes.
