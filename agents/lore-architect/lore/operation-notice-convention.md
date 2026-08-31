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

Sites: `version-check.md` Step 0 (the `R < F` path only), `agent-boot.md` Step 2's
`workspace_refresh` handling, and `attach.md`'s Step 3 subagent — which must print the notice into
its **returned report**, since a subagent's own output goes to a context nobody reads.

**Accuracy trap caught in review:** the first draft said the upgrade "writes files and commits
them". Step 4 also **pushes**. A notice whose entire job is disclosing what happens to the user's
files must name the most consequential part — verify the procedure you are describing rather than
describing it from memory
([verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md)).

## See Also

- [skill-announcement-convention.md](skill-announcement-convention.md)
- [required-literal-output-is-what-models-drop.md](required-literal-output-is-what-models-drop.md)
