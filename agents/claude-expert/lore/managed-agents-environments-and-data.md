---
lore: 1
type: topic
summary: "Managed Agents environments (2026-10-18): cloud sandbox image and limits, packages and networking, self-hosted sandboxes for own images or big data, and Files API, repo, and memory limits. Open for any sandbox or data-size question."
parent: lore/managed-agents.md
---

# Managed Agents — environments, sandboxes, and data

**Documented**, checked 2026-10-18. Sources:
https://platform.claude.com/docs/en/managed-agents/environments,
https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference (the URL
`.../cloud-containers.md` serves this page),
https://platform.claude.com/docs/en/build-with-claude/files, and the bundled `claude-api` skill
(`shared/managed-agents-environments.md`, `shared/managed-agents-self-hosted-sandboxes.md`,
`shared/managed-agents-memory.md`).

## Cloud environments (`config.type: "cloud"`)

- Fixed image: Ubuntu 24.04, x86_64, **up to 8 GB RAM and up to 10 GB disk**. Preinstalled:
  Python 3.10–3.13, Node 20–22, Go, Rust, Java 21, Ruby, PHP, C/C++, PostgreSQL 16, Redis 7,
  SQLite, Playwright with Chromium, ffmpeg, pandoc, LibreOffice, tesseract, TeX Live, and more.
- **No custom Docker image.** The only customization is `packages` (apt, cargo, gem, go, npm,
  pip, optionally pinned) and `networking`.
- `packages` install before the agent starts and are **cached across sessions that share the
  environment**. Packages that the agent installs itself during a session are lost: each session
  gets a fresh container, and sessions share no files.
- Environment updates apply only to new containers. Environments are **not versioned**.
- Make one environment per task type. Agent and environment are chosen independently when a
  session is created: one agent can run in many environments, and many agents can share one.
- **Networking:** `limited` (an allowlist, plus `allow_package_managers` and `allow_mcp_servers`)
  or `unrestricted`. An API create that omits `networking` gets `unrestricted`; the Console form
  starts at Limited. Under `limited`, `allowed_hosts` also limits `web_search` and `web_fetch`.

## Self-hosted sandboxes (`config.type: "self_hosted"`)

- The agent loop stays at Anthropic; bash, file tools, and code run in the user's container. The
  worker polls Anthropic over outbound connections only (`EnvironmentWorker` in the SDKs, or
  `ant beta:worker poll`). `--on-work <script>` can `docker run` a fresh container from the user's
  own image for each session.
- This is the way to use **your own image** and **data larger than 10 GB** (mount a volume).
- Tool inputs and outputs still go to Anthropic, and `web_search` / `web_fetch` always run on
  Anthropic's servers.
- Image needs: `/bin/bash`; the TypeScript worker also needs Node 22+, `unzip`, and `tar`. Memory
  stores need a writable `/mnt/memory` and the SDK worker (the CLI worker does not mount them).

## Getting context and data in

- **Files API:** 500 MB per file and 1 TB per organization. Up to 999 file resources per
  session, mounted read-only under `/mnt/session/uploads/`. Files written to
  `/mnt/session/outputs/` can be downloaded with `files.list(scope_id=<session_id>)`.
- **GitHub repos:** cloned into `/workspace/<repo>`. The token stays outside the sandbox (a git
  proxy).
- **Memory stores:** at most 100 KB per memory and up to 8 stores per session. Use them for
  notes, not bulk data.
- **Live data:** MCP servers or custom tools. **Small context:** the system prompt or the first
  message.

## How to apply

For a large dataset (the example asked was about 15 GB), say plainly that the cloud sandbox
cannot hold it. Recommend a self-hosted sandbox (it keeps the Managed Agents features) or the
[Agent SDK](agent-sdk.md) in the user's own container (the simplest). Agents work on big data
through tools (grep, partial reads, Python), so the context window does not limit the data size
on disk.
