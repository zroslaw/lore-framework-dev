#!/usr/bin/env python3
"""Deterministic tests for transcript-backed reflection preparation.

Run: python3 tests/test_transcript_reflection.py -v
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_DIR = os.environ.get(
    "LR_FRAMEWORK_DIR",
    os.path.abspath(os.path.join(HERE, "..", "..", "lore-framework")),
)
SCRIPT = os.path.join(FRAMEWORK_DIR, "scripts", "session-takeover")
sys.path.insert(0, os.path.join(HERE, "fixtures"))
from archive_fixture import claude_projects_session, codex_sessions_log, write_codex_log  # noqa: E402
from cursor_takeover_fixture import redacted_session  # noqa: E402


def load_mod(**env):
    for key, value in env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    loader = SourceFileLoader("session_takeover", SCRIPT)
    spec = importlib.util.spec_from_loader("session_takeover", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def unit(user, *following):
    return [
        {"role": "user", "content": user},
        *following,
    ]


class TranscriptReflectionInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-transcript-reflection-")
        self.mod = load_mod()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        for key in ("CLAUDE_PROJECTS", "CODEX_HOME", "CURSOR_HOME"):
            os.environ.pop(key, None)

    def test_dialogue_units_keep_assistant_and_tools_with_their_user(self):
        messages = unit(
            "First request",
            {"role": "assistant", "content": "I will inspect it."},
            {"role": "assistant", "tool": "Read", "args": "role.md", "result": "ok"},
        ) + unit("Second request", {"role": "assistant", "content": "Done."})
        units = self.mod.reflection_dialogue_units(messages)
        self.assertEqual([len(item) for item in units], [3, 2])
        self.assertEqual(units[0][2]["tool"], "Read")

    def test_sidechain_and_leading_assistant_messages_are_not_units(self):
        messages = [
            {"role": "assistant", "content": "engine preface"},
            {"role": "assistant", "content": "private", "sidechain": True},
            {"role": "user", "content": "Record this"},
            {"role": "assistant", "content": "Recorded"},
            {"role": "assistant", "content": "sidechain", "sidechain": True},
        ]
        units = self.mod.reflection_dialogue_units(messages)
        self.assertEqual(len(units), 1)
        self.assertEqual([entry["content"] for entry in units[0]], ["Record this", "Recorded"])

    def test_packing_keeps_complete_units_and_one_unit_overlap(self):
        messages = unit("A" * 4700, {"role": "assistant", "content": "a" * 4700})
        messages += unit("B" * 4700, {"role": "assistant", "content": "b" * 4700})
        messages += unit("C" * 4700, {"role": "assistant", "content": "c" * 4700})
        chunks, count = self.mod.build_reflection_chunks(messages, "codex", 10000)
        self.assertEqual(count, 3)
        self.assertEqual(len(chunks), 3)
        self.assertEqual([c["source_units"][0][0] for c in chunks], [1, 2, 3])
        self.assertEqual([c["overlap_units"] for c in chunks[1:]], [[chunks[0]["source_units"][-1]], [chunks[1]["source_units"][-1]]])
        self.assertTrue(all("## Source dialogue" in c["text"] for c in chunks))

    def test_oversize_unit_is_preserved_and_flagged(self):
        messages = unit("A" * 12000, {"role": "assistant", "content": "B" * 12000})
        chunks, count = self.mod.build_reflection_chunks(messages, "claude", 10000)
        self.assertEqual(count, 1)
        self.assertEqual(len(chunks), 1)
        self.assertTrue(chunks[0]["oversize"])
        self.assertIn("A" * 100, chunks[0]["text"])
        self.assertIn("B" * 100, chunks[0]["text"])

    def test_manifest_chars_include_rendered_headers_and_overlap(self):
        messages = unit("first", {"role": "assistant", "content": "answer"})
        messages += unit("second", {"role": "assistant", "content": "answer"})
        out = os.path.join(self.tmp, "run")
        manifest = self.mod.write_reflection_input(
            out, "codex", {"source": self.tmp, "session_id": "fixture"}, messages, 10000
        )
        for chunk in manifest["chunks"]:
            with open(chunk["path"], encoding="utf-8") as fh:
                self.assertEqual(chunk["chars"], len(fh.read()))

    def test_existing_output_path_and_symlink_are_rejected_without_writes(self):
        messages = unit("request", {"role": "assistant", "content": "answer"})
        existing = os.path.join(self.tmp, "existing")
        os.mkdir(existing)
        with self.assertRaises(ValueError):
            self.mod.write_reflection_input(existing, "codex", {"source": self.tmp}, messages)
        target = os.path.join(self.tmp, "target")
        os.mkdir(target)
        symlink = os.path.join(self.tmp, "linked")
        os.symlink(target, symlink)
        with self.assertRaises(ValueError):
            self.mod.write_reflection_input(symlink, "codex", {"source": self.tmp}, messages)
        self.assertEqual(os.listdir(target), [])

    def test_failed_chunk_write_removes_only_this_runs_directory(self):
        messages = unit("request", {"role": "assistant", "content": "answer"})
        original = self.mod._exclusive_write_text
        calls = []

        def fail_manifest(path, text):
            calls.append(path.name)
            if path.name == "manifest.json":
                raise OSError("fixture write failure")
            return original(path, text)

        self.mod._exclusive_write_text = fail_manifest
        try:
            with self.assertRaises(OSError):
                self.mod.write_reflection_input(
                    os.path.join(self.tmp, "run"), "codex", {"source": self.tmp}, messages
                )
        finally:
            self.mod._exclusive_write_text = original
        self.assertEqual(calls, ["chunk-0001.md", "manifest.json"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "run")))

    def test_partial_exclusive_write_unlinks_its_own_file(self):
        path = os.path.join(self.tmp, "partial.md")
        original_fdopen = self.mod.os.fdopen

        class FailingFile:
            def __init__(self, wrapped):
                self.wrapped = wrapped

            def __enter__(self):
                self.wrapped.__enter__()
                return self

            def __exit__(self, *args):
                return self.wrapped.__exit__(*args)

            def write(self, _text):
                raise OSError("fixture disk full")

        self.mod.os.fdopen = lambda fd, *args, **kwargs: FailingFile(
            original_fdopen(fd, *args, **kwargs)
        )
        try:
            with self.assertRaises(OSError):
                self.mod._exclusive_write_text(path, "private transcript")
        finally:
            self.mod.os.fdopen = original_fdopen
        self.assertFalse(os.path.lexists(path))

    def test_cursor_redactions_are_counted_but_not_rendered(self):
        cursor_home = os.path.join(self.tmp, "cursor")
        os.mkdir(cursor_home)
        log, _store = redacted_session(cursor_home)
        mod = load_mod(CURSOR_HOME=cursor_home)
        meta, messages = mod.parse_cursor(log)
        self.assertEqual(meta["assistant_redactions"], 1)
        chunks, _ = mod.build_reflection_chunks(messages, "cursor", 10000)
        self.assertNotIn("[REDACTED]", chunks[0]["text"])


class VerifiedResolverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-transcript-resolver-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        for key in ("CLAUDE_PROJECTS", "CODEX_HOME", "CURSOR_HOME"):
            os.environ.pop(key, None)

    def test_strict_cli_accepts_marker_and_rejects_heuristic(self):
        codex_home = os.path.join(self.tmp, "codex")
        codex_sessions_log(codex_home, "session-one", "lr-transcript-good")
        env = {**os.environ, "CODEX_HOME": codex_home}
        good = subprocess.run(
            [sys.executable, SCRIPT, "--find-by-uuid", "lr-transcript-good", "--engine", "codex", "--require-verified"],
            text=True, capture_output=True, env=env,
        )
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("rollout-", good.stdout)
        bad = subprocess.run(
            [sys.executable, SCRIPT, "--find-by-uuid", "lr-transcript-missing", "--engine", "codex", "--require-verified"],
            text=True, capture_output=True, env=env,
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(bad.stdout, "")
        self.assertIn("verified resolution is required", bad.stderr)

    def test_permissive_resolver_keeps_heuristic_fallback(self):
        codex_home = os.path.join(self.tmp, "codex")
        codex_sessions_log(codex_home, "session-one", "lr-transcript-good")
        env = {**os.environ, "CODEX_HOME": codex_home}
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--find-by-uuid", "lr-transcript-missing", "--engine", "codex"],
            text=True, capture_output=True, env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("rollout-", proc.stdout)
        self.assertIn("falling back", proc.stderr)

    def test_marker_is_found_in_native_tool_arguments_for_all_engines(self):
        marker = "lr-transcript-literal-marker"
        claude_projects = os.path.join(self.tmp, "claude-projects")
        claude_path = claude_projects_session(claude_projects, "claude-a", marker)
        codex_home = os.path.join(self.tmp, "codex")
        codex_path = codex_sessions_log(codex_home, "codex-a", marker)
        cursor_home = os.path.join(self.tmp, "cursor")
        os.mkdir(cursor_home)
        cursor_path, _store = redacted_session(cursor_home)
        # The fixture's tool result carries the marker; add a literal second-call
        # argument to each raw native log and assert the resolver sees it.
        for path in (claude_path, codex_path, cursor_path):
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"marker_argument": marker}) + "\n")
        mod = load_mod(
            CLAUDE_PROJECTS=claude_projects,
            CODEX_HOME=codex_home,
            CURSOR_HOME=cursor_home,
        )
        for engine, expected in (
            ("claude", claude_path),
            ("codex", codex_path),
            ("cursor", cursor_path),
        ):
            path, confidence = mod.find_native_log_by_uuid(marker, engine)
            self.assertEqual(confidence, "verified")
            self.assertEqual(os.path.realpath(path), os.path.realpath(expected))


class ReflectionInputCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-transcript-cli-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_cli_writes_private_manifest_and_chunks(self):
        log = os.path.join(self.tmp, "rollout.jsonl")
        write_codex_log(log)
        output = os.path.join(self.tmp, "run")
        proc = subprocess.run(
            [sys.executable, SCRIPT, "reflection-input", log, "--engine", "codex", "--output-dir", output],
            text=True, capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("wrote 1 reflection chunks from 1 dialogue units", proc.stdout)
        self.assertEqual(oct(os.stat(output).st_mode & 0o777), "0o700")
        with open(os.path.join(output, "manifest.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["engine"], "codex")
        self.assertEqual(len(manifest["chunks"]), 1)

    def test_cli_rejects_too_small_bound(self):
        log = os.path.join(self.tmp, "rollout.jsonl")
        write_codex_log(log)
        proc = subprocess.run(
            [sys.executable, SCRIPT, "reflection-input", log, "--engine", "codex", "--output-dir", os.path.join(self.tmp, "run"), "--max-chars", "9999"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("at least 10000", proc.stderr)


class FinalizeProcedureContractTests(unittest.TestCase):
    def test_finalize_routes_transcript_flag_to_the_focused_procedure(self):
        with open(os.path.join(FRAMEWORK_DIR, "docs", "finalize.md"), encoding="utf-8") as fh:
            finalize = fh.read()
        with open(os.path.join(FRAMEWORK_DIR, "docs", "process-transcript-reflection.md"), encoding="utf-8") as fh:
            procedure = fh.read()
        with open(os.path.join(FRAMEWORK_DIR, "skills", "finalize", "SKILL.md"), encoding="utf-8") as fh:
            skill = fh.read()
        self.assertIn("--transcript", skill)
        self.assertIn("process-transcript-reflection.md", finalize)
        self.assertIn("must complete verified transcript resolution", finalize)
        self.assertIn("--require-verified", procedure)
        self.assertIn("fork_turns: \"none\"", procedure)
        self.assertIn("never copied into `agents/`, `sessions/`, `archive/`", procedure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
