# Standing Improvement List Practice

A ranked, continuously-refreshed improvement list for the Lore Agents framework must **always
exist** — not get produced once per architecture review and go stale. User-established practice
(2026-07-18). Lives at `workdir/what-to-improve.md`; the operating discipline that requires
maintaining it is named in `role.md` § Lore-Curation Disciplines ("Standing improvement list
maintenance").

## Relationship to `framework-improvements-backlog.md`

Two documents, two jobs — they must not fork:

- **`framework-improvements-backlog.md`** — the canonical *unranked* store. Full detail, grouped
  by area, additive-only until an item ships or goes moot.
- **`workdir/what-to-improve.md`** — the *ranked action view* on top of it. What to do next and
  why, in priority order, one-or-two-sentence entries with a pointer back to the backlog entry or
  lore topic that carries the detail.

When an item's detail grows past a couple of sentences, it belongs in the backlog or a topic —
the standing list keeps only the pointer. Same shape as `single-canonical-source-discipline.md`,
applied across two documents instead of within one.

## Refresh Protocol

Baked into the file itself, not just this topic:

- **Reread** at the start of every framework-work session — it frames what to pick up next unless
  the user redirects.
- **Full refresh** at each periodic architecture review: re-rank surviving items, insert new
  findings in rank order, delete shipped/moot entries (git history preserves them —
  delete-don't-mark, same discipline as lore topics).
- **On ship:** mark the item `✅ done <date>/<version>` inline, delete on the *next* refresh (not
  immediately), so the "what recently shipped" context survives one more session.
- **Evidence discipline:** findings born from a review cite their evidence (what was measured or
  observed), so a later session re-verifies rather than trusts a stale claim — same spirit as
  `verify-before-acting-on-suspected-bugs.md`.

## Tiering Convention (first instance, 2026-07-18 review)

Not mandated by the practice itself — future refreshes can reshape it — but a reasonable default
to reuse:

- **A** — verified inconsistencies, fixable now (bounded, next-ship tier)
- **B** — known backlog gaps, promoted with fresh justification
- **C** — new feature directions

A closing "recommended sequencing" section groups tiers into shippable batches.

## See Also

- `role.md` § Lore-Curation Disciplines — the operating discipline this practice backs
- `framework-improvements-backlog.md` — the unranked store this list ranks
- `naming-foundational-principles.md` — why this practice earns its own topic rather than living
  only as a `lore-context.md` line
- `single-canonical-source-discipline.md` — the pointer-not-restatement shape this relationship
  follows
- `feedback-too-many-words.md` — ranked-shortlist-over-enumeration, the working style this
  practice formalizes into a standing artifact
- `verify-before-acting-on-suspected-bugs.md` — the evidence-citation discipline in the refresh
  protocol
