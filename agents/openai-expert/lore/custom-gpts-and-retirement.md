---
lore: 1
type: topic
summary: "Custom GPTs are being replaced by plugins: what transfers (instructions and files become a skill), what does not (custom actions), who can migrate, and the planned dates (creation ends 2026-09-25, retirement 2026-12-11)."
parent: lore/extension-platform.md
---

# Custom GPTs and their retirement

Checked 2026-10-14.

- **Direction** (documented): "We're transitioning custom GPTs to plugins." At retirement, custom
  GPTs stop running and leave the GPT directory (the GPT store).
- **Planned dates** (help article 20001519, read through search snippets; dates "subject to
  change"):
  - Enterprise migration target: 2026-09-17.
  - **Creation of new custom GPTs ends: 2026-09-25.** Publish drafts before this to migrate them.
  - **Scheduled retirement: 2026-12-11.** Other plans follow a similar timeline through in-product
    notices.
- **What transfers** (documented): GPT instructions and knowledge files become a **skill**;
  connected apps stay part of the plugin. **Custom actions do not transfer**; rebuild them as a
  supported app's actions or a **custom MCP server**
  ([remote MCP per surface](remote-mcp-per-surface.md)).
- **Who can migrate** (documented): the GPT's creator or a workspace owner or admin; the GPT must
  be published. After migration the original GPT is read-only but runs until retirement. A GPT can
  still be migrated after retirement, but it no longer runs.
- **Invocation change**: a GPT is opened or `@`-mentioned; a plugin or skill is `@`-mentioned or
  chosen automatically by its description.
- **Admin side** (documented): GPT builders can use connected apps or custom actions, not both in
  one GPT; admins restrict action domains; separate permissions for sharing and for publishing
  replacement plugins to the workspace.

Sources: https://learn.chatgpt.com/docs/migrate-custom-gpts ;
https://learn.chatgpt.com/docs/enterprise/gpts-and-sharing ;
https://help.openai.com/en/articles/20001519 (search snippets only)
