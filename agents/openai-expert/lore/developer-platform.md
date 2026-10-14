---
lore: 1
type: topic
summary: "Pointers to OpenAI's developer platform (2026-10-14): Responses API and its mcp tool, Agents API (managed Codex harness), Agents SDK, ChatKit, Workspace Agents API, Secure MCP Tunnel, Sign in with ChatGPT."
parent: lore-context.md
---

# Developer platform

Checked 2026-10-14. Documented. Pointer level only; read the linked docs for detail. API prices
are on each model page ([models lineup](models-lineup.md)).

- **Responses API**: the main model API. The `mcp` tool takes `server_url` (Streamable HTTP or
  HTTP/SSE) or `tunnel_id`, an optional `authorization` token, and `require_approval` (`always`,
  `never`, or per tool; approval requests arrive as `mcp_approval_request` items). Tool calls cost
  only tokens. The Assistants API is retired; Chat Completions remains.
- **Agents API**: OpenAI runs a **managed Codex harness** with saved sessions, compaction,
  multi-agent orchestration, programmatic tool calling, MCP, plugins, and an optional hosted or
  self-hosted sandbox.
- **Agents SDK**: the agent loop runs inside the developer's application (handoffs, guardrails,
  MCP, tracing).
- **ChatKit**: embeddable chat UI. **Agent Builder**: visual workflows; a migration guide moves
  them to Workspace Agents or the Agents SDK.
- **Workspace Agents API**: trigger published ChatGPT workspace agents from backend systems with
  access tokens.
- **Secure MCP Tunnel**: `tunnel-client` inside a private network opens outbound HTTPS to
  `api.openai.com:443`; ChatGPT custom MCP, Codex, and the Responses API can then call a private
  MCP server. Not for public plugin submission.
- **Sign in with ChatGPT** (DevDay 2026): websites, plugins, and open-source clients can sign users
  in with ChatGPT; eligible Plus and Pro users can let an app use their **ChatGPT plan** for AI
  requests (listed partners include Amp Code, Devin, Kilo Code, Hermes Agent). Commercial sign-in
  is a limited trial. The Codex app server can use such a token.
- **Docs MCP server**: `https://developers.openai.com/mcp` (read-only OpenAI docs).

Sources: https://developers.openai.com/api/docs/guides/agents ;
https://developers.openai.com/api/docs/guides/tools-connectors-mcp ;
https://developers.openai.com/api/docs/guides/secure-mcp-tunnels ;
https://developers.openai.com/workspace-agents/llms.txt ; https://developers.openai.com/siwc/llms.txt ;
https://learn.chatgpt.com/docs/sign-in-with-chatgpt
