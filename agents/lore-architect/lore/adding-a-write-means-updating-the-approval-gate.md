---
lore: 1
type: topic
summary: "A procedure's approval surface is a separate site from its action list: adding a write means updating the confirmation template, the dry-run output, and every hand-maintained enumeration."
parent: lore-context.md
---

# Adding a Write to a Gated Procedure Means Updating the Gate's Template

`workspace-init` Step 3 is a confirmation gate: one plan listing **every** file write, then a single
yes/no. It ships a literal template block for the executor to reproduce. v43 added two new file
writes in Step 4 and did not touch that template.

Effect: a literal executor shows the user the old plan, gets a "yes", then writes two files the user
never saw — while the same document's "What `/lr:workspace-init` does NOT do" section promises
*"Does not write any file outside the Step 3 base plan."* The change made the doc contradict itself
and converted an approved run into an unapproved write.

**The general rule: a procedure's approval surface is a separate site from its action list, and
adding an action does not update it.** Grep for the gate whenever a step gains a side effect. The
same holds for dry-run output, summary templates, and any other place that *enumerates* what will
happen — these are enumerations maintained by hand, and an enumeration is exactly what a new item
silently falls out of.

Sibling sites found by the same review pass, all enumerations that needed the new entries:
`workspace-push.md`'s human-readable rendering of `MANAGED_PATHS`, `conventions.md`'s inventory of
literate-accelerator subcommands, `README.md`'s directory layout, and `docs/engines/cursor.md`'s
"honest table" of load surfaces.

## See Also

- [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md)
  — the same class, one step later in a procedure.
- [instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)
- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — enumerate every
  site that *states* a fact, not only every site that implements it.
- [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md)
