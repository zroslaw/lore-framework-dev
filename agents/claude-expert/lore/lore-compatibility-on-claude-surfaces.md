---
lore: 1
type: topic
summary: "Inference, untested (2026-10-13): where Lore's lr plugin can and cannot run on Claude surfaces, why chat and mobile cannot run it, and what to test first. Open when asked if Lore works in the Claude app, Cowork, or on mobile."
parent: lore-context.md
---

# Lore compatibility on Claude surfaces

**Label: inference, not tested.** I concluded this on 2026-10-13 from the plugin platform-support
docs ([plugins](plugins-install-and-surface-support.md)) and a check of the installed plugin
layout.

## What Lore needs from a surface

The `lr` plugin's value lives in skills plus scripts. The skills call `python3` scripts under the
framework root and run `git` against local workspace repos. So only a surface with local file and
git access can run boot, pull, reflect, merge, or finalize.

## Per surface

- **Claude Code**: works; this is where `lr` is installed today. A CLI install stays on that
  machine, so `lr` does not appear in the claude.ai account, chat, Cowork, or mobile
  ([one-way sync](extension-platform.md)).
- **Chat (web, desktop, mobile)**: cannot run Lore. If someone added the lore-framework marketplace
  at Customize > Plugins, chat could load the `lr` skill text, but chat skills run in Claude's code
  sandbox, which has neither the workspace nor the repos.
- **Local Cowork in Claude Desktop**: loads skills, agents, and hooks and runs on the user's
  computer, so it is the most likely Claude surface after Claude Code where `lr` could work.
  Untested.
- **Top-level `bin/` rule**: a plugin with a top-level `bin/` is refused by chat and Cowork.
  Checked 2026-10-13: the installed `lr` 1.47.0 has no top-level `bin/`, `hooks/`, or `agents/`
  (top level: assets, df, docs, migrations, release-notes, scripts, skills, plus markdown files),
  so this rule does not block it.
- **Phone**: reaches Lore agents only through sessions that run elsewhere — Dispatch or Remote
  Control (on the user's machine), or Claude Code cloud sessions with the repos cloned into that
  environment ([surfaces](claude-apps-and-surfaces.md)). A remote MCP server is the only kind of
  Lore component that would reach Claude mobile chat directly.

## How to apply

When lore-architect or a user asks whether Lore works in the Claude app, Cowork, or on mobile,
answer from this topic, say it is untested, and suggest testing in a local Cowork session first.
Re-check the `bin/` rule and the plugin's top-level layout against the installed version, since
both can change.
