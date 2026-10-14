---
lore: 1
type: topic
summary: "Team and Enterprise admin controls in Cursor (2026-10-14): what Teams vs Enterprise get, MCP and plugin governance, model access, Run Mode and sandbox policy, privacy and data residency, identity, service accounts, audit and telemetry."
parent: lore/extension-platform.md
---

# Admin and enterprise controls

Checked 2026-10-14. Documented unless a line says otherwise. Most controls live in the dashboard at
cursor.com/dashboard (Team Settings, Plugins & MCPs, Cloud Agents, Automations).

## Teams vs Enterprise (Cursor plan family)

- **Teams** (self-serve): central billing and admin, usage analytics, team-wide Privacy Mode,
  SAML/OIDC SSO, one team marketplace, Team Rules, Team MCP servers, Cursor Router settings, Sync
  Skills policy, Protected Git Scopes, Admin API keys, Bugbot, cloud agents and automations.
- **Enterprise only** (dashboard page "Enterprise-Only Settings" and docs): Model Access Control,
  enhanced spend limits, Auto Run configuration, repository blocklist, **MCP Configuration (MCP
  Allowlist)**, Cursor Ignore configuration, `.cursor` directory protection, AI Code Tracking API,
  Audit Log, SCIM, team and managed hooks, Team Pools (self-hosted), service accounts, Cursor
  Blame, OpenTelemetry Export, unlimited team marketplaces, pooled usage, invoicing.
- The X Subscription pricing page gives a similar split: Teams $30+/user; Enterprise adds
  invoicing, SCIM, granular spend controls, group settings, auto-run/browser/network controls,
  repository/model/MCP access controls, audit logs, service accounts, and Grok Bot controls.

## MCP and plugin governance

- **Distribution** (Teams and Enterprise): Team MCP servers and team marketplaces with Default Off,
  Default On, or Required plugins. A switch "Run team MCP servers on members' machines" runs every
  team HTTP server, and each member's own MCP servers, locally in members' IDEs after a
  confirmation; cloud agents still use Cursor's servers.
- **Policy** (Enterprise): MCP Allowlist with command entries (stdio, matched on the full command
  string), URL entries (HTTP/SSE), and per-server tool allowlists; per-server network modes for
  local servers (Allow all, Allowlist, Deny all, No sandbox); "User MCP extensions" and a User MCP
  network denylist. Allowlisting approves; it does not install.
- MDM can place `~/.cursor/permissions.json` to set the MCP auto-run allowlist.
- **Allow Local Plugin Imports** (off by default on Enterprise) and **Allow Members to Publish**
  (skills) are marketplace settings.

## Agent runtime policy

- Admins choose which Run Modes users may pick, the sandbox network rules, and a team read policy
  (Workspace read mode, 3.23). Team settings override user and project settings.
- Admins can disable headless CLI use, turn on "Restrict Cloud Agent Usage" (Enterprise), allow
  team follow-ups on teammates' cloud agents, enable Remote Control, and turn off Cursor Cloud MCP
  or shared canvases.
- Managed policy `AgentRemoteWorkspaceAuthorities` (3.24) turns Agent off in local windows and
  allows it only in approved remote workspaces.

## Models and privacy

- Model Access Control (Enterprise) blocks models per team or group; Cursor Router respects it and
  needs Grok 4.6 allowed. Admins can restrict personal API keys (BYOK).
- Privacy Mode: on by default for teams; admins can enforce it. Code is not used for training.
  Some models (Claude Fable 5 and 5.1) need data-retention approval.
- Data residency: US-only residency for eligible models at a 10% price uplift. CMEK for cloud agent
  data (Enterprise). Private Inference gateways appear in 3.24 release notes.

## Identity, accounts, and audit

- SSO (SAML/OIDC), SCIM provisioning (Enterprise), Organizations of linked teams, Organization
  Groups, billing groups, service accounts (Enterprise) for APIs, the CLI, cloud agents, and pool
  workers.
- Audit logs (Enterprise), Admin API, Analytics API, AI Code Tracking API, OpenTelemetry Export
  (Enterprise; OTLP/HTTP to the customer's collector; includes skills, hooks, plugins, cloud agent
  events, and recorded Grok Bot actions).

Sources: https://cursor.com/docs/account/teams/dashboard.md ; https://cursor.com/docs/account/teams/pricing.md ;
https://cursor.com/docs/enterprise/model-and-integration-management.md ; https://cursor.com/docs/mcp.md ;
https://cursor.com/docs/plugins.md ; https://cursor.com/docs/agent/security/run-modes.md ;
https://cursor.com/docs/enterprise/privacy-and-data-governance.md ; https://cursor.com/docs/models-and-pricing.md ;
https://cursor.com/docs/enterprise/opentelemetry-export.md ; https://cursor.com/docs/account/enterprise/service-accounts.md ;
https://cursor.com/help/security-and-privacy/privacy.md ; https://cursor.com/pricing ; https://cursor.com/docs/release-notes.md
