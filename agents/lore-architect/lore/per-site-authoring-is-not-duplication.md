---
lore: 1
type: topic
summary: "Scope test before applying the single-canonical-source rule: the same words at many sites need one canonical site; different words following the same rule put the rule at the canonical site and the words at the point of use."
parent: lore-context.md
---

# Per-site authoring is not duplication — separate the rule from the text

When a rule must be applied at many sites, the anti-duplication reflex says "put it in one file and
point at it everywhere." That reflex is right about the **rule** and wrong about the **text** when
the text is genuinely different per site.

This is a **scope test on** [single-canonical-source-discipline.md](single-canonical-source-discipline.md),
not a competing rule: run it first, to decide whether that discipline applies at all.

## The case (v44, 2026-08-30)

Designing v44's skill announcements, I proposed a shared `docs/skill-announcement.md` holding the
announcement guidance, with a one-line pointer in each of 33 skill docs, and justified it with
single-canonical-source. The user rejected it and proposed the opposite: write each skill's
announcement text **into that skill's own doc**, plus a framework-development convention saying every
skill must have one.

The user was right, and my error is worth naming: **I applied a duplication rule to content that was
never duplicated.** Thirty-three announcements describing thirty-three different commands share a
*shape*, not a *string*. There was nothing to drift.

## The distinction to apply

Ask what would actually be copied:

- **The same words at many sites** → one canonical site, pointers elsewhere. Drift is real, and the
  pointer-only discipline governs.
- **Different words following the same rule** → the *rule* goes in the canonical site (for authors),
  the *words* go at the point of use (for executors). A shared file here buys nothing and costs a
  read at execution time.

The second case has a tell: **a "shared" file that would need a lookup table, a branch, or a
placeholder per site is not shared content — it is a rule wearing content's clothes.**

## Second-order benefit

Once the text lives at the point of use, the executor needs no extra read to produce it, and the long
doc holding all the rules stays out of the invocation path. My shared-file proposal would have made
every skill invocation read a second file, or a fragment of a long one — the cost the user flagged in
the same message. Same instinct as `literate-accelerator-pattern.md`: one artifact where two would
have to be kept in step.

## See Also

- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — the rule this
  scopes, refines, and does not replace.
- [skill-announcement-convention.md](skill-announcement-convention.md) — the case that produced it.
- `shared-procedure-doc-pattern.md` — the positive form, and the case where centralizing *is* right
  because the body really is one body.
- `literate-accelerator-pattern.md` — the same one-artifact-not-two instinct applied to scripts.
