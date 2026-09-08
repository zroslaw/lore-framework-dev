---
lore: 1
type: topic
summary: "v45 draft: a conditional notice fired when a procedure does something consequential the user did not ask for — distinct from a Step 0 announcement, and silent on no-ops by design."
parent: lore-context.md
---

# Operation Notice

Drafted in v45 (`v45-boot-announcements`), after the user asked why boot silently migrates a lore
repo or fast-forwards the workspace.

Both are **sub-procedures**, and `conventions.md` § Skill Purpose Announcement says *one
announcement per user invocation* — a doc read as a sub-procedure does not print its own Step 0, so
a chain does not announce at every hop. Adding a second Step 0 would have broken that rule, so the
resolution was to name a distinct category rather than overload the existing one.

| | Skill Purpose Announcement | Operation Notice |
|---|---|---|
| Fires | always, once per invocation | only when the operation actually runs |
| Says | what this command is for | what is happening to your files, and why |
| Silent when | never | the operation was a no-op |

**The silence half is load-bearing.** A notice that fires on a no-op trains the reader to skip the
line, and then they skip it the once it mattered — the same reasoning `agent-boot.md` already gives
for staying silent on a quiet `workspace_refresh`. Report the *action*, never the *check*.

Sites include version-check on the upgrade path and boot workspace-refresh handling. For attach,
the **host emits the notice before dispatching the worker**. The earlier draft put it in the
worker's returned report; that cannot notify the user before the worker acts. Corrected during
the v45 implementation review.

**Accuracy traps caught in review:** name potential publication, but do not promise writes,
commits, or pushes before safety checks decide whether they can proceed. The notice describes
the safety checks and conditional publication. The first draft omitted push; a later unconditional
promise was also inaccurate. Verify the procedure being described
([verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md)).

## See Also

- [skill-announcement-convention.md](skill-announcement-convention.md)
- [required-literal-output-is-what-models-drop.md](required-literal-output-is-what-models-drop.md)
