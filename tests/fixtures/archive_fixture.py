"""Synthetic Claude Code and Codex session-log fixtures.

These exercise the *parse path* of scripts/session-takeover (JSONL shaped like
the real engine transcripts), which the pre-existing stub_*_engine.py fixtures
do NOT — those emit CLI-stdout envelopes from the external lrb.py vantage.

Each builder writes a log file and returns its path plus any values a test
needs to assert against (token totals, the UUID planted in tool output, etc.).
"""

import json
import os


# --------------------------------------------------------------- claude


def _claude_records(session_id, cwd, lore_uuid, with_sidechain):
    """The list of JSONL records for a synthetic Claude session."""
    recs = [
        {"type": "ai-title", "aiTitle": "Fixture Archive Session"},
        {
            "type": "user",
            "sessionId": session_id,
            "cwd": cwd,
            "timestamp": "2026-07-20T10:00:00.000Z",
            "message": {"role": "user", "content": "Boot the fixture agent."},
        },
        {
            "type": "assistant",
            "sessionId": session_id,
            "cwd": cwd,
            "timestamp": "2026-07-20T10:00:05.000Z",
            "message": {
                "role": "assistant",
                "model": "claude-sonnet-5",
                "usage": {
                    "input_tokens": 1000,
                    "output_tokens": 200,
                    "cache_read_input_tokens": 500,
                    "cache_creation_input_tokens": 100,
                },
                "content": [
                    {"type": "text", "text": "Running the boot command now."},
                    {
                        "type": "tool_use",
                        "id": "toolu_main_1",
                        "name": "Bash",
                        "input": {
                            "command": "python3 -c 'import uuid; print(uuid.uuid4())'"
                        },
                    },
                ],
            },
        },
        {
            "type": "user",
            "sessionId": session_id,
            "timestamp": "2026-07-20T10:00:06.000Z",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_main_1",
                        "content": [
                            {
                                "type": "text",
                                # The lore UUID lands in tool OUTPUT — this is what
                                # find-by-uuid greps for.
                                "text": lore_uuid,
                            }
                        ],
                    }
                ],
            },
        },
    ]
    if with_sidechain:
        recs.append(
            {
                "type": "assistant",
                "sessionId": session_id,
                "isSidechain": True,
                "timestamp": "2026-07-20T10:00:07.000Z",
                "message": {
                    "role": "assistant",
                    "model": "claude-haiku-4-5",
                    "usage": {
                        "input_tokens": 4000,
                        "output_tokens": 800,
                        "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0,
                    },
                    "content": [
                        {
                            "type": "text",
                            "text": "SUBAGENT-SECRET investigating the codebase.",
                        }
                    ],
                },
            }
        )
    recs.append(
        {
            "type": "assistant",
            "sessionId": session_id,
            "timestamp": "2026-07-20T10:00:09.000Z",
            "message": {
                "role": "assistant",
                "model": "claude-sonnet-5",
                "usage": {
                    "input_tokens": 1200,
                    "output_tokens": 300,
                    "cache_read_input_tokens": 900,
                    "cache_creation_input_tokens": 0,
                },
                "content": [{"type": "text", "text": "Done — agent booted."}],
            },
        }
    )
    return recs


def write_claude_log(path, session_id="claude-fixture-session",
                     cwd="/tmp/fixture", lore_uuid="LORE-UUID-CLAUDE-1234",
                     with_sidechain=True):
    recs = _claude_records(session_id, cwd, lore_uuid, with_sidechain)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return {
        "path": path,
        "session_id": session_id,
        "lore_uuid": lore_uuid,
        # Expected aggregate token totals (main + sidechain when present):
        "expected_tokens_with_sidechain": {
            "input": 1000 + 4000 + 1200,
            "output": 200 + 800 + 300,
            "cache_read": 500 + 0 + 900,
            "cache_creation": 100,
        },
        "expected_tokens_main_only": {
            "input": 1000 + 1200,
            "output": 200 + 300,
            "cache_read": 500 + 900,
            "cache_creation": 100,
        },
    }


def claude_projects_session(projects_home, session_id, lore_uuid,
                            project="fixture-project"):
    """Write a Claude log into a ~/.claude/projects-style tree for discovery."""
    path = os.path.join(projects_home, project, f"{session_id}.jsonl")
    write_claude_log(path, session_id=session_id, lore_uuid=lore_uuid)
    return path


# ---------------------------------------------------------------- codex


def _codex_records(session_id, cwd, lore_uuid):
    return [
        {
            "type": "session_meta",
            "payload": {
                "id": session_id,
                "timestamp": "2026-07-20T11:00:00.000Z",
                "cwd": cwd,
                "originator": "codex_cli",
                "cli_version": "1.0.0",
            },
        },
        {
            "type": "turn_context",
            "timestamp": "2026-07-20T11:00:01.000Z",
            "payload": {"model": "gpt-5-codex"},
        },
        {
            "type": "response_item",
            "timestamp": "2026-07-20T11:00:02.000Z",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Run the boot check."}],
            },
        },
        {
            "type": "response_item",
            "timestamp": "2026-07-20T11:00:03.000Z",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Running it."}],
            },
        },
        {
            "type": "response_item",
            "timestamp": "2026-07-20T11:00:04.000Z",
            "payload": {
                "type": "function_call",
                "name": "exec_command",
                "call_id": "call_1",
                "arguments": json.dumps(
                    {"cmd": "python3 -c 'import uuid; print(uuid.uuid4())'"}
                ),
            },
        },
        {
            "type": "response_item",
            "timestamp": "2026-07-20T11:00:05.000Z",
            "payload": {
                "type": "function_call_output",
                "call_id": "call_1",
                "output": f"{lore_uuid}\nProcess exited with code 0",
            },
        },
        # cumulative token counts — the LAST one is the session total
        {
            "type": "event_msg",
            "timestamp": "2026-07-20T11:00:03.500Z",
            "payload": {
                "type": "token_count",
                "info": {
                    "total_token_usage": {
                        "input_tokens": 100,
                        "cached_input_tokens": 20,
                        "output_tokens": 50,
                        "reasoning_output_tokens": 10,
                        "total_tokens": 180,
                    }
                },
            },
        },
        {
            "type": "event_msg",
            "timestamp": "2026-07-20T11:00:06.000Z",
            "payload": {
                "type": "token_count",
                "info": {
                    "total_token_usage": {
                        "input_tokens": 300,
                        "cached_input_tokens": 60,
                        "output_tokens": 120,
                        "reasoning_output_tokens": 30,
                        "total_tokens": 510,
                    }
                },
            },
        },
    ]


def write_codex_log(path, session_id="codex-fixture-session",
                    cwd="/tmp/fixture", lore_uuid="LORE-UUID-CODEX-5678"):
    recs = _codex_records(session_id, cwd, lore_uuid)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return {
        "path": path,
        "session_id": session_id,
        "lore_uuid": lore_uuid,
        # Expected from the LAST cumulative token_count record:
        "expected_tokens": {
            "input": 300,
            "output": 120 + 30,  # output + reasoning
            "cache_read": 60,
            "cache_creation": 0,
        },
    }


def codex_sessions_log(codex_home, session_id, lore_uuid):
    """Write a Codex rollout into a ~/.codex/sessions tree for discovery."""
    path = os.path.join(
        codex_home, "sessions", "2026", "07", "20",
        f"rollout-2026-07-20T11-00-00-{session_id}.jsonl",
    )
    write_codex_log(path, session_id=session_id, lore_uuid=lore_uuid)
    return path
