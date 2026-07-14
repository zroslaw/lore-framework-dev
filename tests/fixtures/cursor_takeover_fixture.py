"""Build a minimal Cursor on-disk layout for session-takeover unit tests."""

import binascii
import contextlib
import hashlib
import json
import os
import sqlite3

SESSION_ID = "a1111111-1111-4111-8111-111111111111"
INTERRUPTED_SESSION_ID = "b2222222-2222-4222-8222-222222222222"
SAME_NAME_SESSION_ID = "c3333333-3333-4333-8333-333333333333"
REDACTED_SESSION_ID = "d4444444-4444-4444-8444-444444444444"
WORKSPACE_HASH = "fixtureworkspace000000000000000001"
PROJECT_SLUG = "fixture-project"


def _insert_blob(conn, payload: bytes) -> str:
    blob_id = hashlib.sha256(payload).hexdigest()
    conn.execute("INSERT INTO blobs (id, data) VALUES (?, ?)", (blob_id, payload))
    return blob_id


def write_cursor_session(
    cursor_home,
    *,
    session_id=SESSION_ID,
    workspace_cwd="/tmp/fixture-workspace",
    title="Fixture Takeover",
    model="haiku",
    jsonl_records,
    tool_results,
):
    """Write chats/ + projects/ trees under `cursor_home` (CURSOR_HOME)."""
    chats_dir = os.path.join(
        cursor_home, "chats", WORKSPACE_HASH, session_id
    )
    jsonl_dir = os.path.join(
        cursor_home,
        "projects",
        PROJECT_SLUG,
        "agent-transcripts",
        session_id,
    )
    os.makedirs(chats_dir, exist_ok=True)
    os.makedirs(jsonl_dir, exist_ok=True)

    meta = {
        "schemaVersion": 1,
        "createdAtMs": 1783860082620,
        "updatedAtMs": 1783860114731,
        "cwd": workspace_cwd,
        "hasConversation": True,
    }
    with open(os.path.join(chats_dir, "meta.json"), "w") as fh:
        json.dump(meta, fh)

    jsonl_path = os.path.join(jsonl_dir, f"{session_id}.jsonl")
    with open(jsonl_path, "w") as fh:
        for record in jsonl_records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    store_db = os.path.join(chats_dir, "store.db")
    if os.path.exists(store_db):
        os.remove(store_db)
    with contextlib.closing(sqlite3.connect(store_db)) as conn:
        conn.execute("CREATE TABLE blobs (id TEXT PRIMARY KEY, data BLOB NOT NULL)")
        conn.execute("CREATE TABLE meta (key INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        for idx, item in enumerate(tool_results):
            payload = json.dumps(
                {
                    "role": "tool",
                    "content": [
                        {
                            "type": "tool-result",
                            "toolCallId": f"tool_{idx:04d}",
                            "toolName": item["name"],
                            "result": item["result"],
                        }
                    ],
                },
                ensure_ascii=False,
            ).encode()
            _insert_blob(conn, payload)
        store_meta = json.dumps(
            {
                "agentId": session_id,
                "latestRootBlobId": "0" * 64,
                "name": title,
                "mode": "default",
                "lastUsedModel": model,
                "createdAt": 1783860082620,
            }
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (0, ?)",
            (binascii.hexlify(store_meta.encode()).decode(),),
        )
        conn.commit()
    return jsonl_path, store_db


def minimal_session(cursor_home, workspace_cwd="/tmp/fixture-workspace"):
    """Boot + parallel tool batch + completed turn."""
    jsonl_records = [
        {
            "role": "user",
            "message": {
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "<timestamp>Monday, Jul 14, 2026</timestamp>\n"
                            "<user_query>\nBoot test-agent and recall the build tool.\n"
                            "</user_query>"
                        ),
                    }
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "Booting test-agent."},
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"path": "docs/agent-boot.md"},
                    },
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Glob",
                        "input": {"glob_pattern": "**/*.md"},
                    },
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"path": "lore/espresso-build-tool.md"},
                    },
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [
                    {
                        "type": "text",
                        "text": "The build tool is **espresso-tamper**.",
                    }
                ]
            },
        },
        {"type": "turn_ended", "status": "success"},
    ]
    tool_results = [
        {"name": "Read", "result": "# Agent boot instructions"},
        {"name": "Read", "result": "espresso-build-tool.md contents"},
        {"name": "Glob", "result": "Result: 3 files"},
    ]
    return write_cursor_session(
        cursor_home,
        workspace_cwd=workspace_cwd,
        jsonl_records=jsonl_records,
        tool_results=tool_results,
    )


def interrupted_session(cursor_home, workspace_cwd="/tmp/fixture-workspace"):
    """In-progress session: no turn_ended; last tool result missing (crash mid-call)."""
    jsonl_records = [
        {
            "role": "user",
            "message": {
                "content": [
                    {
                        "type": "text",
                        "text": "<user_query>\nRun the deploy script.\n</user_query>",
                    }
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "Running deploy."},
                    {
                        "type": "tool_use",
                        "name": "Shell",
                        "input": {"command": "./deploy.sh"},
                    },
                ]
            },
        },
    ]
    tool_results = []
    return write_cursor_session(
        cursor_home,
        session_id=INTERRUPTED_SESSION_ID,
        workspace_cwd=workspace_cwd,
        title="Interrupted Deploy",
        jsonl_records=jsonl_records,
        tool_results=tool_results,
    )


def same_name_parallel_session(cursor_home, workspace_cwd="/tmp/fixture-workspace"):
    """Parallel Read+Read in one batch — pairing by name is ambiguous."""
    jsonl_records = [
        {
            "role": "user",
            "message": {
                "content": [
                    {
                        "type": "text",
                        "text": "<user_query>\nCompare two files.\n</user_query>",
                    }
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"path": "alpha.md"},
                    },
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"path": "beta.md"},
                    },
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [{"type": "text", "text": "Files compared."}],
            },
        },
        {"type": "turn_ended", "status": "success"},
    ]
    tool_results = [
        {"name": "Read", "result": "ALPHA-CONTENT-9912"},
        {"name": "Read", "result": "BETA-CONTENT-8831"},
    ]
    return write_cursor_session(
        cursor_home,
        session_id=SAME_NAME_SESSION_ID,
        workspace_cwd=workspace_cwd,
        title="Same Name Parallel",
        jsonl_records=jsonl_records,
        tool_results=tool_results,
    )


def redacted_session(cursor_home, workspace_cwd="/tmp/fixture-workspace"):
    """Assistant prose stored as [REDACTED] at rest."""
    jsonl_records = [
        {
            "role": "user",
            "message": {
                "content": [
                    {
                        "type": "text",
                        "text": "<user_query>\nSummarize the secret plan.\n</user_query>",
                    }
                ]
            },
        },
        {
            "role": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "[REDACTED]"},
                    {
                        "type": "text",
                        "text": "The public summary is **espresso-tamper**.",
                    },
                ]
            },
        },
        {"type": "turn_ended", "status": "success"},
    ]
    return write_cursor_session(
        cursor_home,
        session_id=REDACTED_SESSION_ID,
        workspace_cwd=workspace_cwd,
        title="Redacted Assistant",
        jsonl_records=jsonl_records,
        tool_results=[],
    )
