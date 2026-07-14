#!/usr/bin/env python3
"""Unit tests for lore-framework/scripts/session-takeover (Cursor path).

Run:  python3 tests/test_session_takeover.py -v
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_DIR = os.environ.get(
    "LR_FRAMEWORK_DIR",
    os.path.abspath(os.path.join(HERE, "..", "..", "lore-framework")),
)
SCRIPT = os.path.join(FRAMEWORK_DIR, "scripts", "session-takeover")
sys.path.insert(0, os.path.join(HERE, "fixtures"))
from cursor_takeover_fixture import (  # noqa: E402
    SESSION_ID,
    interrupted_session,
    minimal_session,
    redacted_session,
    same_name_parallel_session,
)


def load_session_takeover(cursor_home=None):
    if cursor_home is not None:
        os.environ["CURSOR_HOME"] = cursor_home
    from importlib.machinery import SourceFileLoader

    loader = SourceFileLoader("session_takeover", SCRIPT)
    spec = importlib.util.spec_from_loader("session_takeover", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class CursorTakeoverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-cursor-takeover-")
        self.cursor_home = os.path.join(self.tmp, "cursor")
        os.makedirs(self.cursor_home)
        self.jsonl_path, self.store_db = minimal_session(self.cursor_home)
        self.mod = load_session_takeover(self.cursor_home)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.environ.pop("CURSOR_HOME", None)

    def test_parse_cursor_user_query_and_title(self):
        meta, messages = self.mod.parse_cursor(self.jsonl_path)
        self.assertEqual(meta["engine"], "cursor")
        self.assertEqual(meta["title"], "Fixture Takeover")
        self.assertEqual(meta["model"], "haiku")
        self.assertEqual(meta["status"], "completed")
        users = [m for m in messages if m["role"] == "user"]
        self.assertEqual(len(users), 1)
        self.assertIn("Boot test-agent", users[0]["content"])

    def test_parallel_batch_tool_result_pairing(self):
        meta, messages = self.mod.parse_cursor(self.jsonl_path)
        tools = [m for m in messages if "tool" in m]
        self.assertEqual(len(tools), 3)
        self.assertEqual(meta["tool_results_paired"], 3)
        self.assertEqual(meta["tool_calls_total"], 3)
        glob_msg = next(m for m in tools if m["tool"] == "Glob")
        read_msgs = [m for m in tools if m["tool"] == "Read"]
        self.assertIn("3 files", glob_msg["result"])
        self.assertTrue(any("espresso-build-tool" in m["result"] for m in read_msgs))
        self.assertTrue(any("boot" in m["result"].lower() for m in read_msgs))

    def test_render_markdown_includes_cursor_footer(self):
        meta, messages = self.mod.parse_cursor(self.jsonl_path)
        digest = self.mod.render_markdown(meta, messages)
        self.assertIn("espresso-tamper", digest)
        self.assertIn("Cursor transcript note", digest)
        self.assertIn("3/3", digest)

    def test_db_path_redirects_to_jsonl(self):
        digest = os.path.join(self.tmp, "out.md")
        env = {**os.environ, "CURSOR_HOME": self.cursor_home}
        proc = subprocess.run(
            [sys.executable, SCRIPT, self.store_db, "-o", digest],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.isfile(digest))
        with open(digest) as fh:
            text = fh.read()
        self.assertIn("espresso-tamper", text)

    def test_resolve_session_by_uuid_prefix(self):
        path = self.mod.resolve_session(SESSION_ID[:12])
        self.assertEqual(os.path.realpath(path), os.path.realpath(self.jsonl_path))

    def test_resolve_session_ambiguous_prefix_exits(self):
        session_id = SESSION_ID
        dst_dir = os.path.join(
            self.cursor_home,
            "projects",
            "fixture-project-2",
            "agent-transcripts",
            session_id,
        )
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(
            self.jsonl_path, os.path.join(dst_dir, f"{session_id}.jsonl")
        )
        with self.assertRaises(SystemExit):
            self.mod.resolve_session(session_id[:12])

    def test_list_cursor_enriched_fields(self):
        sessions = self.mod.list_cursor(limit=10, include_all=True)
        match = next(s for s in sessions if s["id"] == SESSION_ID)
        self.assertEqual(match["title"], "Fixture Takeover")
        self.assertEqual(match["model"], "haiku")
        self.assertEqual(match["status"], "completed")
        self.assertFalse(match["is_subagent"])
        self.assertTrue(str(match["path"]).endswith(".jsonl"))

    def test_interrupted_session_pairing_uncertain(self):
        jsonl_path, _ = interrupted_session(self.cursor_home)
        mod = load_session_takeover(self.cursor_home)
        meta, messages = mod.parse_cursor(jsonl_path)
        self.assertEqual(meta["status"], "in-progress")
        self.assertTrue(meta.get("pairing_uncertain"))
        tools = [m for m in messages if "tool" in m]
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["result"], "")
        digest = mod.render_markdown(meta, messages)
        self.assertIn("Pairing may be incomplete", digest)

    def test_detect_engine_cursor_jsonl(self):
        self.assertEqual(self.mod.detect_engine(self.jsonl_path), "cursor")

    def test_same_name_parallel_batch_pairing_uncertain(self):
        jsonl_path, _ = same_name_parallel_session(self.cursor_home)
        mod = load_session_takeover(self.cursor_home)
        meta, messages = mod.parse_cursor(jsonl_path)
        self.assertTrue(meta.get("pairing_uncertain"))
        tools = [m for m in messages if "tool" in m]
        self.assertEqual(len(tools), 2)
        self.assertEqual(meta["tool_results_paired"], 2)
        self.assertIn("ALPHA-CONTENT-9912", tools[0]["result"])
        self.assertIn("BETA-CONTENT-8831", tools[1]["result"])
        digest = mod.render_markdown(meta, messages)
        self.assertIn("same tool name", digest)

    def test_redacted_assistant_text_omitted(self):
        jsonl_path, _ = redacted_session(self.cursor_home)
        mod = load_session_takeover(self.cursor_home)
        meta, messages = mod.parse_cursor(jsonl_path)
        assistant_text = "\n".join(
            m["content"] for m in messages if m["role"] == "assistant"
        )
        self.assertNotIn("[REDACTED]", assistant_text)
        self.assertIn("espresso-tamper", assistant_text)
        digest = mod.render_markdown(meta, messages)
        self.assertIn("Cursor transcript note", digest)
        self.assertIn("espresso-tamper", digest)


if __name__ == "__main__":
    unittest.main()
