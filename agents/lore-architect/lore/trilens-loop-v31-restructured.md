# `docs/trilens-loop.md` Restructured in v31 (parked)

The one-paragraph compression recorded in `trilens-loop-deliberately-minimal-2026-07-25.md` is **no
longer what the doc looks like**. On explicit user instruction across several turns (2026-07-26/27),
it was rewritten into a ~75-line structured doc. Still on `lore-framework` `wip/lr-core-v31`,
committed there as `lore-framework` `c3d418d`; **plugin branch not merged to main, not pushed.**
`lore-framework-dev` main already carries related lore (including this topic) via the 2026-07-27
merge — see `v31-lr-core-parked-2026-07-25.md`. Main's plugin still carries the v30 325-line doc
described in `trilens-loop-feature.md`.

This was not a "helpful restore" of the old version — it is a new shape the user asked for step by
step. The don't-re-expand-unasked rule held throughout: every expansion here was user-directed.

## What the doc now says

- **Sections:** `## The loop` (6 numbered steps), `## Stopping rules`, `## Exchange contract`,
  `## Overrides`. Structure over a plain prose block, at the user's explicit request.
- **Three lenses restored as the stated default** — "that is the whole idea to have different
  perspectives, 3 by default." Lens *choice* is named as the host's own responsibility, reasoned from
  what actually changed (a schema migration, a doc rewrite, and a new CLI command each want a
  different trio). That keeps the judgement layer in lore
  (`parallel-reviewer-fanout-pattern.md`) rather than freezing a lens table into the doc.
- **Exchange contract** — the session's main new idea. The host sends only: repo trees, the
  changed-file list, one or two sentences of orientation, and the lens. The reviewer returns only
  findings-as-pointers (path, line, signature/heading, ~1 paragraph, severity) plus a verdict. No
  diffs and no file contents cross the wire in either direction.
- **Reviewers discover the changes themselves** rather than being handed a diff — the fresh look is
  the deliverable. Note this is *not* justified by token savings; see
  `parallel-reviewer-fanout-pattern.md` § Cost for the measurement that kills that framing.
- **Vocabulary reinstated** — `BLOCKER`/`HIGH`/`MEDIUM`/`LOW`, `SHIP`/`SHIP-WITH-FIXES`/`BLOCK`,
  `APPLIED`/`DECLINED`/`ACCEPTED`. A round-1 finding showed a stopping rule keyed off a verdict value
  the compressed doc never defined. Reused v30's vocabulary rather than minting a new dialect.
- **Three-round ceiling is the one non-overridable rail.** A clean round 1 is explicitly a good
  outcome, not a reason to keep looking.
- **Regular-tier reviewer models** (sonnet / composer-2.5 / gpt-5.4 named as illustrations, not a
  lookup table) — restored on user instruction after first being surfaced as
  `ACCEPTED (not applied)`.
- **No host-side fallback**, with the semantics-class classification stated in the doc itself. This
  is what closed the `cursor.md` deferral — see `check-own-lore-before-dismissing-a-finding.md`.

The same commit also corrected `docs/engines/cursor.md` (Cursor's native `Task` subagents are no
longer described as unverified; Host-Side Override Rules no longer claim to apply "anywhere", which
contradicted the trilens carve-out) and `release-notes/31.md` (it still described a
single-paragraph doc that no longer exists).

## Codex reviewer tier — RECONCILED 2026-07-27

**`gpt-5.4` is correct** (user decision, restated 2026-07-27). The v31 doc already said so; the
stale sites were `release-notes/30.md:49` and `trilens-loop-feature.md`. Resolved the fix-forward
way: `release-notes/31.md` now carries an explicit correction-of-record line, `trilens-loop-feature.md`
was corrected on the v31 branch, and **shipped v30 notes were left untouched** — a shipped release
note is a historical record of what that version said, not a live reference. `versioning-release-types.md`'s
v30 entry likewise keeps `gpt-4.5` because it records v30's shipped scope faithfully.

## See Also

- `trilens-loop-deliberately-minimal-2026-07-25.md` — the rule that still governs this doc; its
  one-paragraph premise is superseded here.
- `v31-lr-core-parked-2026-07-25.md` — the parking record and current resume list.
- `trilens-loop-feature.md` — describes main's v30 doc; still accurate for main, and the topic to
  fold this into when v31 actually ships.
- `parallel-reviewer-fanout-pattern.md` — the judgement layer the doc deliberately defers to.
- `check-own-lore-before-dismissing-a-finding.md` — how the no-host-side-fallback clause got here.
