# Plugin MCP Servers + Non-Shell Runtime Exception

Two conventions established in v18 with `lr-wait` — the framework's **first bundled MCP server** and **first `python3` dependency**. Both are codified in `lore-framework/docs/conventions.md` (§§ Plugin MCP Servers, Tooling: Non-Shell Runtimes). The feature that drove them is `wait-primitive-feature.md`.

## MCP server registration

- **Declare bundled servers in a `.mcp.json` at the plugin root.** Keeps `plugin.json` minimal; an inline `mcpServers` block in `plugin.json` is the equivalent alternative.
- **`${CLAUDE_PLUGIN_ROOT}` expands** inside `command` / `args` / `env` / `cwd` — reference bundled files as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>`.
- **Claude Code (the MCP host) auto-launches** the server subprocess when the plugin is enabled, merges its tools into the agent's toolset, and manages lifecycle (start at session begin, stop at end). Confirmed empirically: a bare root `.mcp.json` auto-discovers under `--plugin-dir` (a live `claude -p` run connected `lr-wait` and called its tool).
- **Adding, renaming, or removing a server is cache-affecting** — carry the Clear Plugin Cache footer, exactly as for a skill. The trigger lists in both `conventions.md` § Migration/Release-Note Authoring and `versioning-release-types.md` (the cache-affecting definition) now name a bundled MCP server / `.mcp.json` explicitly.

## Non-shell runtime exception (`python3`)

The framework is otherwise strictly **bash-on-BSD / stdlib** (see `portable-shell-in-framework-docs.md`; conventions § Tooling: Portable Shell). The single sanctioned exception:

- A **protocol-speaking server component** (e.g. an MCP stdio server exchanging newline-delimited JSON-RPC) where bash is impractical may be written in **`python3`, standard library only (no `pip install`)**. No dependency install; runs anywhere `python3` is present — any Linux, and any macOS with the Xcode Command Line Tools (a bare macOS may prompt to install them). `scripts/wait-server.py` is the first instance.
- This **parallels the pre-existing Node ULA module** (`df/aiqa/workflows/ula-file-pass.js`) — a language-specific module the framework ships and drives, not a portable one-liner.
- **Rule:** don't reach for `python3` for work a portable shell script can do. Companion tooling stays bash (e.g. `scripts/lr-emit`).

## See Also

- `wait-primitive-feature.md` — the v18 feature that established both conventions.
- `versioning-release-types.md` — the cache-affecting trigger definition (now names bundled MCP servers) and the v18 history entry.
- `portable-shell-in-framework-docs.md` — the bash-on-BSD default this carves the sole exception to.
- `plugin-vs-agent-repo-separation.md` — plugin repo hosts the bundled server; dev repo hosts its tests.
- `framework-scope-vs-agent-scope.md` — a bundled MCP server is framework-scope (universal, distributed).
- `skill-doc-pattern.md` — the sibling thin-pointer pattern; the server's skill (`skills/wait`) follows it.
