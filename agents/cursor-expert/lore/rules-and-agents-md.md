---
lore: 1
type: topic
summary: "Cursor rules as of 2026-10-14: project .mdc rules and their four apply types, AGENTS.md (nested), CLAUDE.md (always applied), User Rules vs ~/.cursor/rules, Team Rules and enforcement, precedence, and what each surface loads."
parent: lore/memory-and-personalization.md
---

# Rules and AGENTS.md

Checked 2026-10-14. Documented unless a line says otherwise.

## Project rules

- `.cursor/rules/` holds `.mdc` files (subfolders work). A plain `.md` file there is **ignored**:
  it has no frontmatter. Use AGENTS.md for plain markdown.
- Frontmatter decides when a rule loads:

| Type | `alwaysApply` | `globs` | `description` | Loads |
|---|---|---|---|---|
| Always Apply | true | — | — | Every chat |
| Apply to Specific Files | false | set | — | When a matching file is in context |
| Apply Intelligently | false | — | set | When the agent judges it relevant |
| Apply Manually | false | — | — | Only when `@`-mentioned |

- Rule text reaches the agent as written. An `@file` mention is a pointer: the agent reads the file
  with its tools; the content is not inlined. This is the same in the editor, CLI, and cloud.
- Create with `/create-rule` or Customize → Rules → Add Rule. Keep rules under 500 lines.
- `.cursorrules` in the project root is legacy and "will be deprecated".
- Rules cannot be imported alone from a repo; ship them in a plugin.

## AGENTS.md and CLAUDE.md

- `AGENTS.md` in the project root and in any subfolder. Nested files combine with parents; the
  more specific file wins.
- Cursor reads `CLAUDE.md` like `AGENTS.md` and **always** applies it, whatever its frontmatter
  says (help page). The CLI reads both at the project root.
- Inference, untested: Claude Code's `@path` import lines inside CLAUDE.md are probably not
  expanded by Cursor; the docs describe only plain inclusion.

## User Rules

- Set in Customize → Rules. Stored on the Cursor account; they sync to every machine at sign-in.
  Used by Agent (Chat), not by inline edit or Tab.
- User rule **files** in `~/.cursor/rules` stay on the machine and do not sync.
- User Rules and Team Rules are not in profile exports.

## Team Rules (Teams and Enterprise)

- Free-form text in the dashboard (cursor.com/dashboard/team-content); optional glob patterns.
- "Enforce this rule" makes it required; otherwise members can turn it off in Customize.
- Precedence when guidance conflicts: **Team Rules → Project Rules → User Rules**. All applicable
  rules merge.

## Per surface

- Editor and CLI: all types.
- Cloud agents: repo rules, User Rules, and Team Rules (cloud best-practices page); AGENTS.md.
- Bugbot: none of these. It uses `.cursor/BUGBOT.md` and rules in Automations.

Sources: https://cursor.com/docs/rules.md ; https://cursor.com/help/customization/rules.md ;
https://cursor.com/docs/cli/using.md ; https://cursor.com/docs/cloud-agent/best-practices.md ;
https://cursor.com/docs/cloud-agent/setup.md ; https://cursor.com/help/ai-features/bugbot.md
