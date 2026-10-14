---
lore: 1
type: topic
summary: "Remote MCP servers on each OpenAI surface (2026-10-14): ChatGPT web, desktop, mobile, Codex CLI and desktop, Codex Cloud, API. Transport, OAuth (CIMD, DCR, static), headers, MCP features, plan gating, read vs write confirmations."
parent: lore/extension-platform.md
---

# Remote MCP per surface

Checked 2026-10-14. Each line carries its label. [D] = documented (OpenAI docs), [T] = third-party
report, [I] = inference (mine, untested). The unsettled items here (plan gating, mobile, Codex
Cloud, prompts) are also tracked in [open verification items](open-verification-items.md).

## Short answer

| Surface | Remote MCP? | How it is added | Transport | Auth |
|---|---|---|---|---|
| ChatGPT web (Chat, Work) | Yes [D] | Plugins page > **Add custom MCP server** > **Create as a plugin**, then install | SSE or streamable HTTP [D] | OAuth, none, or mixed; no static API-key headers [D] |
| ChatGPT desktop (Chat, Work) | Yes, same account plugins [D for plugins; I for custom ones] | Add on web; desktop shows account plugins | as web | as web |
| ChatGPT mobile (Chat, Work) | Probably, as an installed plugin [I] | Cannot add on mobile [D: adding is a web flow] | as web | as web |
| Codex CLI, Codex in desktop app, IDE | Yes [D] | `config.toml` `[mcp_servers.x] url = ...`, `codex mcp add`, or desktop Settings > MCP servers | Streamable HTTP (and stdio) [D] | Bearer token, static or env headers, header helper, OAuth, ChatGPT session [D] |
| Codex Cloud tasks | Not documented [D: no statement] | — | — | — |
| Responses API `mcp` tool | Yes [D] | `server_url` or `tunnel_id` per request | Streamable HTTP or HTTP/SSE [D] | `authorization` token parameter [D] |

## ChatGPT (hosted: web, desktop, mobile)

- **Add**: chatgpt.com/plugins > **+** > **Add custom MCP server** > name, Server URL (with
  `/mcp`) or **Tunnel** > authentication > accept the risk warning > **Create as a plugin**. The
  result is a personal (or workspace) plugin; **install it** before use; call it with `@`. [D]
- **Access**: "Use ChatGPT on the web." Workspace permissions and security restrictions,
  including **Lockdown**, apply. [D] The old "Developer mode" toggle is now this flow; the
  developer doc keeps the anchor `#what-is-chatgpt-developer-mode`. [D]
- **Network**: OpenAI's cloud calls the server, so it needs a **public HTTPS endpoint** or a
  **Secure MCP Tunnel** (outbound `tunnel-client` to `api.openai.com:443`; private servers; not
  for public submission). [D] A `localhost` URL cannot work. [I] ChatGPT presents an OpenAI
  mTLS client certificate and uses published egress IP ranges, which servers can allowlist. [D]
- **Auth options**: **OAuth**, **No authentication**, or **OAuth or no authentication** (mixed:
  `initialize` and `tools/list` without auth, each tool by its declared security scheme). [D]
  - OAuth 2.1 per the MCP authorization spec: protected resource metadata, `resource` parameter,
    PKCE `S256` (required in metadata), RFC 9207 `iss` checks. [D]
  - Client identity: **static (predefined) client credentials** win when given; else **CIMD**
    (`token_endpoint_auth_methods` `none` or `private_key_jwt`) when the server advertises it
    and the builder chooses it; else **DCR** (once per connection). [D]
  - Redirect URI: `https://chatgpt.com/connector_platform_oauth_redirect` (issuer-identified
    servers) or `https://chatgpt.com/connector/oauth/{callback_id}`. [D]
  - **Not supported**: client-credentials or other machine-to-machine grants, custom API keys,
    customer mTLS certificates. [D] So a static bearer header is not an option in ChatGPT. [I]
- **MCP features** [D unless marked]:
  - **Tools**, read and write. `search`/`fetch` are not required (only for company knowledge).
  - **Server instructions** (`instructions`): pulled on Refresh; keep the first 512 characters
    self-contained.
  - **Resources**: used for UI (MCP Apps standard) and for skill catalogs at submission
    (`resources/read`).
  - **Elicitation**, including OpenAI's extended forms.
  - **MCP Events** (2026-09-29): webhook subscriptions; needs MCP 2.0 (protocol `2026-07-28`);
    only in Work chats on web, cloud Work on desktop, and dots.
  - **Prompts**: the MCP concept page lists them, but no ChatGPT or Codex behavior is documented,
    and a second search on 2026-10-14 found none. Plugins "primarily use tools". [I: not used]
- **Read vs write and confirmations** [D]: ChatGPT respects `readOnlyHint`; a tool without it is a
  **write action**. Write actions need confirmation by default. The user can remember approve or
  deny for one tool for the rest of that conversation; new conversations ask again. Full JSON
  input and output show for each call. Admins can limit a connection to read-only actions
  (**Action control**).
- **Manage**: per-plugin details page to toggle tools and **Refresh** tools, descriptions, and
  instructions. [D]
- **Plan gating — unresolved conflict**:
  - [D] The developer docs state no plan list. The Codex and Work plan matrix marks **MCP** and
    **Connectors** available on Plus, Pro, Business, and Enterprise (Free and Go are not in that
    matrix).
  - [T] June 2026 table (caipi.ai): Free and Go no custom MCP; Plus and Pro yes; Business admins
    only; Enterprise admins plus RBAC; write actions "beta" on Business and Enterprise.
  - [T] October 2026 (smartscope.blog): Business and Enterprise need the **Create plugins with
    MCPs** permission (off by default on Enterprise); Plus and Pro can create but not share such
    plugins.
  - [T] Search snippets of help article 12584461 ("Developer mode and MCP apps in ChatGPT", older
    versions) named Business and Enterprise/Edu on the web. Help pages block fetches; verify in a
    browser before quoting a plan.
  - [T] Boomi's help page: full MCP with writes on Business, Enterprise, Edu; Plus and Pro
    read-only through developer mode. Zuplo's docs: Pro, Team, Enterprise, Edu. Both likely
    describe the pre-plugin developer-mode era.
  - [D vs stale snippet] A search snippet of the plugin quickstart said "Settings → Security and
    login → turn on Developer mode" first; the live quickstart (fetched 2026-10-14) has no such
    step. So the toggle was probably removed; recheck in the UI.
  - Second attempt on 2026-10-14 (developer docs, Apps SDK paths, changelog, search) found no
    primary plan list. Treat plan gating as **unverified**.
- **Mobile**: plugins work in mobile Chat and Work [D]; a custom-MCP personal plugin should too,
  but no page says so [I]. An older developer-mode FAQ said "web only" [T, June 2026 quote].

## Codex (CLI, desktop app Codex, IDE extension — one host config)

- `config.toml` (`~/.codex/` or trusted-project `.codex/`), shared by the three clients. [D]
- Streamable HTTP keys: `url`; `bearer_token_env_var`; `http_headers` (static); `env_http_headers`;
  `http_headers_helper` (a local command that prints headers; refreshed once after 401/403);
  `auth = "oauth"` (default) or `"chatgpt"` (ChatGPT session, trusted first-party servers). [D]
- OAuth: `codex mcp login <name>`; CIMD preferred when advertised, else DCR; or a pre-registered
  client (`--oauth-client-id`, `--oauth-client-secret`). Loopback callback
  `http://127.0.0.1/callback[/<id>]`; `mcp_oauth_callback_url` for remote devboxes. Prefers
  server `scopes_supported`. [D]
- Features: tools, server instructions, resources (app-server `mcpServer/resource/read`),
  elicitation (form and URL modes; `approval_policy.granular.mcp_elicitations`). Prompts: not
  documented. SSE transport: not listed for Codex. [D]
- Approvals: `default_tools_approval_mode` = `auto` | `prompt` | `writes` | `approve`; per-tool
  `approval_mode`; `enabled_tools` / `disabled_tools`; `required`; timeouts (start 10 s, tool
  60 s). Host sandbox and approval policy apply. [D]
- Network: the host machine connects directly, so private and localhost servers work. [I] MCP
  servers have their own network controls, separate from sandbox networking. [D]
- Plan: any sign-in, including an API key. [D] Some plugins' OAuth flows do not work with API-key
  sign-in. [D]
- From the phone, Codex on mobile uses the **host's** MCP servers; iOS offers per-chat or
  cross-chat MCP approval choices. [D]

## Codex Cloud

No page states MCP support for cloud tasks. Agent Security notes that its network rules "do not,
by themselves, disable hosted web search, apps, or MCP" on managed Codex Cloud paths [D], which
hints that hosted apps exist there. The Codex changelog lists a code change "Add turn-start cloud
plugin discovery to the MCP extension" (#46572) [D, meaning unclear]. Local `config.toml` servers
do not follow a task to the cloud [I]. A second search on 2026-10-14 (cloud docs, config
reference, changelog, openai/codex docs) found no statement. Test before promising remote MCP in
Codex Cloud.

Sources: https://developers.openai.com/api/docs/guides/custom-mcp-server ;
https://developers.openai.com/plugins/build/auth ; https://developers.openai.com/plugins/build/mcp-server ;
https://developers.openai.com/plugins/build/mcp-events ;
https://developers.openai.com/plugins/deploy/connect-chatgpt ;
https://developers.openai.com/api/docs/guides/secure-mcp-tunnels ;
https://developers.openai.com/api/docs/guides/tools-connectors-mcp ;
https://learn.chatgpt.com/docs/extend/mcp ; https://learn.chatgpt.com/docs/plugins ;
https://learn.chatgpt.com/docs/pricing ; https://learn.chatgpt.com/docs/enterprise/agent-security ;
third-party: https://caipi.ai/blog/which-plans-support-mcp-2026 ;
https://smartscope.blog/en/blog/chatgpt-sites-mcp-server-plugin-hosting-2026/ ;
https://help.boomi.com/docs/Atomsphere/Platform/Connect_chatgpt_setup ;
https://zuplo.com/docs/mcp-gateway/connect-clients/chatgpt.md
