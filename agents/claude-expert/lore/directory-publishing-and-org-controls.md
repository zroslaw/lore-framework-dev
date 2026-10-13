---
lore: 1
type: topic
summary: "Publishing plugins and MCP connectors to the Claude directory (portal since 2026-09-25, who can submit, how review works) and the Team/Enterprise org controls over plugins and connectors."
parent: lore/extension-platform.md
---

# Directory publishing and org controls

Checked 2026-10-13. Documented.

## Publishing to the directory

- Any paid-plan user can submit a plugin or an MCP connector through the portal at
  claude.ai/directory/manage (launched 2026-09-25). On Team and Enterprise, an Owner submits.
- Every version gets automated validation and a security scan. A person reviews new listings.
- Plugins that users add from a marketplace URL or by upload skip this review.

## Org controls (Team and Enterprise)

- An Owner sets each plugin to **Not available**, **Available to install**, **Installed by
  default**, or **Required**, and chooses which Anthropic sources the org uses.
- An Owner can add connectors for the org; members then connect with their own accounts.
- Team members without permission see a **Request** button on directory connectors.

Sources: https://claude.com/docs/connectors/directory ;
https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory
