---
lore: 1
type: topic
summary: "Inference, untested (2026-10-14): where Lore's lr plugin runs on OpenAI surfaces (Codex CLI yes, desktop Codex probably, ChatGPT Chat and hosted Work no) and why only a remote MCP server reaches ChatGPT mobile chat."
parent: lore-context.md
---

# Lore compatibility on OpenAI surfaces

**Label: inference, not tested,** unless a line says documented. I concluded this on 2026-10-14
from the OpenAI plugin and surface docs ([extension platform](extension-platform.md),
[surfaces](openai-apps-and-surfaces.md)) and a look at the installed `lr` 1.47.0 layout. How Lore
itself runs on Codex (sandbox, `.git` writes, `spawn_agent`) is lore-architect's: see
`lore-framework/docs/engines/codex.md`.

## What Lore needs from a surface

The `lr` plugin's value lives in skills plus scripts. The skills call `python3` scripts under the
framework root and run `git` against local workspace repos. So only a surface with local file and
git access can run boot, pull, reflect, merge, or finalize.

## Per surface

- **Codex CLI**: works; it is a supported Lore engine (documented in the Lore framework). Install
  goes to `~/.codex/plugins/cache/lore-framework/lr/<version>/`.
- **Codex in the ChatGPT desktop app**: probably works. It is the same Codex host: it shares
  `~/.codex/config.toml`, skills, `AGENTS.md`, and the plugin cache path
  `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` (documented). The desktop app also
  reads `.agents/plugins/marketplace.json` and the legacy `.claude-plugin/marketplace.json`
  (documented); `lr` ships `.codex-plugin/plugin.json` and `.claude-plugin/` (checked). Untested.
- **Local ChatGPT Work in the desktop app**: it runs on the Codex runtime with local files, so it
  might load `lr` skills too. Untested; Work hides shell detail, which makes debugging harder.
- **IDE extension**: no plugins (documented). `lr` skills would load only if copied into a skill
  location such as `.agents/skills`.
- **ChatGPT Chat (web, desktop, mobile) and hosted Work**: cannot run Lore. Even if `lr` were
  published as a plugin, its skill text would load but the scripts would run (if at all) in a
  cloud container without the workspace repos. `lr`'s local stdio MCP server (`lr-wait` in
  `.mcp.json`, checked) would be ignored or make the plugin desktop-only.
- **Codex Cloud**: repo skills work, personal skills do not sync, and the repos must be in the
  published environment (documented). Running `lr` there would need the framework and all agent
  repos inside the environment, plus Git push credentials. Not attempted.
- **Phone**: reaches Lore only through sessions that run elsewhere. **Codex on mobile** drives a
  desktop host where `lr` is installed (the host supplies plugins, skills, and files — documented),
  so a phone could run a Lore session on the laptop. A dot with a connected computer could start
  local Codex tasks there.
- **ChatGPT mobile chat directly**: only a **remote MCP server** can reach it — added on the web as
  a custom MCP server, created as a plugin, installed, then used in mobile Chat or Work
  ([remote MCP per surface](remote-mcp-per-surface.md)). It must be public HTTPS (or a Secure MCP
  Tunnel) with OAuth or no auth; static API-key headers are not supported.

## How to apply

When lore-architect or a user asks whether Lore works in ChatGPT or Codex, answer from this topic,
say it is untested, and suggest testing Codex in the desktop app first. Recheck the desktop app's
marketplace paths and the plugin's top-level layout against the current versions. This test is
tracked in [open verification items](open-verification-items.md).
