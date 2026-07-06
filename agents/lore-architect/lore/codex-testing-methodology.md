# Codex Lifecycle-Testing Methodology (manual)

How to exercise the framework on real Codex, and the ground-truthing that makes results
trustworthy. Complements the lifecycle harness (`lifecycle-testing-harness.md`), whose `codex`
branch now covers the headless doc-driven execution path; this manual method remains the
ground-truth path for rollout-log verification and for diagnosing host-runtime issues.

- **Run headless:** `codex exec --full-auto --skip-git-repo-check < prompt.txt > log 2>&1`,
  **backgrounded and polled** (never foreground-killed — see
  `headless-cli-smoke-testing-discipline.md`). `--cd <repo>` (a.k.a. `-C`) makes a specific repo
  the writable root. Default model here was `gpt-5.4-mini` — a weak tier, so passing is a strong
  signal.
- **Boot without plugin install:** the natural-language boot (point at
  `<build>/docs/agent-boot.md` + the agent dir) exercises Step-0, framework-root, profile
  selection, and fan-out — no marketplace install needed, and it avoids `lr` plugin-id collisions.
- **Same doc-driven adapter as the harness:** for Codex, "engine-neutral prompt" means translating
  the lifecycle request into a doc-driven prompt against `<LR_FRAMEWORK_DIR>/docs/*.md`, not
  sending the same slash-skill instruction used on Claude/Cursor. That adapter is the reliable
  headless path.
- **Host writes to `~/.codex/` are a prerequisite:** if the outer sandbox makes `~/.codex/`
  read-only, Codex can die before entering the fixture repo (`~/.codex/state_5.sqlite`, readonly
  database). Treat that as a host-runtime setup issue, not a framework regression.
- **Ground-truth tool use in the session rollout logs, not the model's prose** — the load-bearing
  technique. `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` records real `function_call` items
  (`name: spawn_agent`, `namespace: multi_agent_v1`, `arguments`). A spawned subagent gets its own
  rollout file; `wait_agent.targets` holds its thread id. **Always verify spawn claims here — the
  model will narrate whatever the profile told it to do**, whether or not it actually spawned.
- **Capability probes:** `codex features list` (flag stages), `codex debug prompt-input` (renders
  the *message* list — NOT the tools array), `strings` on the binary for tool descriptions/schemas.
- **Isolate writes:** validate merge/finalize against a throwaway repo copy with its git remote
  removed, so no accidental push and the real repo stays clean.

## See Also

- `codex-port-validated-end-to-end.md` — the end-to-end result this methodology produced.
- `codex-native-multi-agent-subsystem.md` — the `spawn_agent` tools the rollout logs record.
- `codex-cli-plugin-loading-findings.md` — CLI quirks (stdin redirect, buffered JSONL, install model).
- `headless-cli-smoke-testing-discipline.md` — the background-don't-hard-kill rule this relies on.
- `lifecycle-testing-harness.md` — the automated harness this manual method complements.
