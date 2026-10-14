---
lore: 1
type: topic
summary: "Codex surfaces as of 2026-10-14: Codex in the ChatGPT desktop app, CLI (0.162.1), IDE extension, Codex Cloud, mobile, GitHub/GitLab/Slack/Linear, SDK and app server, the removed codex mcp-server, and sign-in rules."
parent: lore/openai-apps-and-surfaces.md
---

# Codex surfaces

Checked 2026-10-14. Documented unless a line says otherwise. Lore's own engine profile for Codex
belongs to lore-architect (`lore-framework/docs/engines/codex.md` and its
`codex-engine-capabilities.md` topic); this topic holds the product facts only.

## Local surfaces (one Codex host)

- **Codex in the ChatGPT desktop app** (macOS, Windows; Linux preview since 2026-08-11). The
  standalone Codex app (macOS 2026-02-02, Windows 2026-03-04) **merged into the ChatGPT desktop
  app on 2026-07-09**, on every plan including Free. Chats run **Local**, in a **Worktree**, or
  in **Cloud**. Also SSH remote projects and chat handoff between hosts.
- **Codex CLI**: install with `curl -fsSL https://chatgpt.com/codex/install.sh | sh`,
  `npm install -g @openai/codex`, or `brew install --cask codex`. Latest stable release
  **rust-v0.162.1 (2026-10-09)**; 0.163.0 alphas are out (GitHub releases API).
- **IDE extension**: VS Code, Cursor, Windsurf; Xcode and JetBrains have their own Codex
  integrations. **No plugins in the IDE extension.**
- The desktop app, CLI, and IDE extension **share `~/.codex/config.toml`** (MCP servers, model,
  plugins), `AGENTS.md`, skills, and the local memory store for the same host.

## Codex Cloud

- A task runs in its own workspace from a **published cloud environment** (repos, dependencies,
  tools, network policy, secrets). Start from web or desktop (**Work in > Cloud**), mobile
  (**Codex**), the CLI (`codex cloud`), Slack, GitHub, GitLab, or Linear. Work continues while
  the computer sleeps. Reusable environments shipped at DevDay (2026-09-29).
- Requires **ChatGPT sign-in** (not an API key). Plus and higher.
- Repo skills (`.agents/skills`) work in cloud tasks; **personal skills are not synced**. No
  Computer Use or browser use in cloud environments yet.
- Internet access is set per environment (allowlists, network secrets, Tailscale VPN).
- **Codex Cloud (Legacy)** still serves Code Review and the Linear and GitHub integrations;
  OpenAI plans to deprecate it.

## Integrations

- **GitHub**: `@codex review` in a PR, automatic reviews, `## Code Review Rules` in `AGENTS.md`;
  Security Review (research preview; not on Plus).
- **GitLab** (beta, 2026-08-19, all plans), **Linear**, **Codex GitHub Action**.
- **Slack**: `@ChatGPT` in a channel; with Cloud delegation the repo work runs as a Codex Cloud
  task from a workspace-shared environment. Admin sets up the deployment. @ChatGPT in Teams too.

## Programmatic surfaces

- `codex exec` for scripts and CI; **Codex SDK** (TypeScript) controls local agents.
- **Codex app server**: a JSON-RPC protocol for embedding Codex (experimental, not for
  production).
- **`codex mcp-server` and the `codex-mcp-server` binary are removed.** Integrations must move to
  the app server, which is not an MCP server. `codex mcp` (Codex as an MCP *client*) still works.
- Enterprise: Codex access tokens and service accounts for non-interactive automation.

## Sign-in

- Sign in with ChatGPT (subscription usage) or an API key (API billing). Desktop, CLI, and IDE
  accept both for local work. Codex Cloud and GitHub/Slack integrations need ChatGPT sign-in.
- Headless devices: device-code sign-in (beta), or copy the auth cache.
- Custom model providers need a Responses-compatible endpoint; `wire_api = "chat"` is not
  supported. Amazon Bedrock is a built-in provider (`amazon-bedrock`).

Sources: https://learn.chatgpt.com/docs/environments/modes ; https://learn.chatgpt.com/docs/codex/cli ;
https://learn.chatgpt.com/docs/codex/ide ; https://learn.chatgpt.com/docs/environments/cloud-environments ;
https://learn.chatgpt.com/docs/third-party/github ; https://learn.chatgpt.com/docs/third-party/slack ;
https://learn.chatgpt.com/docs/mcp-server ; https://learn.chatgpt.com/docs/auth ;
https://learn.chatgpt.com/docs/whats-new ; https://github.com/openai/codex/releases
