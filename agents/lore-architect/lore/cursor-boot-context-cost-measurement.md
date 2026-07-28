# Cursor Boot Context Cost (measured 2026-07-28)

Empirical boot-cost measurement on Cursor (256K window) for `lore-architect`, using Cursor's Context Usage UI plus `lore-framework/scripts/token-count` (`tiktoken` / `o200k_base`).

## What boot costs

| Slice | Tokens | Of 256K |
|---|---:|---:|
| Files read on this boot (incl. version-check) | 22,960 | ~9.0% |
| Conversation Δ for the boot turn | ~26,500 | ~10.4% |
| Files without `version-check.md` (normal match) | 19,091 | ~7.5% |
| Est. conversation Δ without version-check | ~22,600 | ~8.8% |

**Rule of thumb:** a regular version-match boot is **~20K tokens** (~8–9% of a 256K Cursor window). Fixed session overhead (~22K tools/rules/skills) is separate and unchanged by boot.

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
