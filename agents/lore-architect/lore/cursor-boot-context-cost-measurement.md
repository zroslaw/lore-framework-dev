# Boot Context Cost Measurement (measured 2026-07-28)

Measure the files a boot procedure loads separately from tool output and hidden engine context. `lore-framework/scripts/token-count` uses `tiktoken` / `o200k_base`: it is exact for that encoding and a stable cross-engine proxy, though not a billing-accurate count for every model. Do not use `characters / 4` for decisions; Markdown, paths, and code made it materially disagree with the tokenizer in a live boot measurement.

The Cursor measurement below also used Cursor's Context Usage UI for its conversation delta.

## What boot costs

| Slice | Tokens | Of 256K |
|---|---:|---:|
| Files read on this boot (incl. version-check) | 22,960 | ~9.0% |
| Conversation Δ for the boot turn | ~26,500 | ~10.4% |
| Files without `version-check.md` (normal match) | 19,091 | ~7.5% |
| Est. conversation Δ without version-check | ~22,600 | ~8.8% |

**Rule of thumb:** a regular version-match boot loads **about 18–20K file tokens** for this agent. Fixed engine/session overhead is separate and unchanged by the boot files.

## File breakdown (this boot)

| File | Tokens |
|---|---:|
| `lore-context.md` | 8,922 |
| `docs/version-check.md` | 3,869 (only on skew) |
| `docs/agent-boot.md` | 3,526 |
| `docs/engines/cursor.md` | 3,257 |
| `role.md` | 3,162 |
| `lr-boot` + per-agent shortcut SKILL.md | ~224 |
| Preflight JSON | 384 |

`lore-context.md` is the largest single boot payload. `version-check.md` adds ~3.9K when skew routes there — match skips it.

Conversation Δ exceeds the file sum by ~3.5K (tool wrappers, MCP schema for workspace root move, boot confirmation reply). Preflight JSON is only ~384 of that gap.

## Codex file-only measurement

The same `lore-architect` boot on Codex loaded about **21.8K** file-and-result tokens when version skew routed it through `version-check.md`; a version-match boot would have been about **17.9K**. Its main slices were `lore-context.md` (8.9K), `role.md` (3.2K), `agent-boot.md` (3.5K), the Codex engine profile (1.7K), and the conditional version-check document (3.9K). This is a repeatable file budget, not a claim about Codex's complete hidden startup context.

The main reduction opportunity remains on-demand loading: the initial path needs preflight, result routing, role, and lore context; task-specific operating guidance can load when its situation occurs.

## How to remeasure

```
python3 -m venv /tmp/tiktoken-venv && /tmp/tiktoken-venv/bin/pip install -q tiktoken
/tmp/tiktoken-venv/bin/python lore-framework/scripts/token-count <paths…>
```

macOS Homebrew Python is PEP 668 externally-managed — use a venv (or `--break-system-packages`), not bare `pip install tiktoken`.

## Relation to existing lore

Confirms `agent-boot-doc-grew-when-scripted.md`'s "~3K tokens for `agent-boot.md`" in a full-stack measurement. The subtraction backlog (A8 / operating-manual split / `read_next` for Step 2) remains the main lever on the framework side; `lore-context.md` size is the other large lever and is agent-local.

## See Also

- `agent-boot-doc-grew-when-scripted.md`
- `framework-improvements-backlog.md` § Agent Boot-Context Caching (parked)
- `standing-improvement-list-practice.md` (A8)
- `cursor-engine-capabilities.md`
