#!/usr/bin/env python3
"""Unit tests for the session-archive + usage features of session-takeover.

Run:  python3 tests/test_session_archive.py -v

Points at the framework script via LR_FRAMEWORK_DIR (default: sibling
lore-framework). Uses synthetic Claude/Codex parse fixtures in fixtures/.
"""

import gzip
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
from archive_fixture import (  # noqa: E402
    claude_projects_session,
    codex_sessions_log,
    write_claude_log,
    write_codex_log,
)


def load_mod(**env):
    for k, v in env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    loader = SourceFileLoader("session_takeover", SCRIPT)
    spec = importlib.util.spec_from_loader("session_takeover", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class ClaudeParseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-archive-claude-")
        self.log = os.path.join(self.tmp, "claude.jsonl")
        self.info = write_claude_log(self.log)
        self.mod = load_mod()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_raw_args_untruncated(self):
        meta, messages = self.mod.parse_claude(self.log)
        tool = next(m for m in messages if m.get("tool") == "Bash")
        # raw_args keeps the full original dict; clipped args is a string
        self.assertIsInstance(tool["raw_args"], dict)
        self.assertIn("command", tool["raw_args"])
        self.assertIn("uuid", tool["raw_args"]["command"])
        self.assertIsInstance(tool["args"], str)

    def test_raw_result_untruncated(self):
        meta, messages = self.mod.parse_claude(self.log)
        tool = next(m for m in messages if m.get("tool") == "Bash")
        self.assertEqual(tool["raw_result"], self.info["lore_uuid"])

    def test_sidechain_tagged_and_included(self):
        meta, messages = self.mod.parse_claude(self.log)
        sidechain_msgs = [m for m in messages if m.get("sidechain")]
        self.assertTrue(sidechain_msgs)
        self.assertTrue(
            any("SUBAGENT-SECRET" in m.get("content", "") for m in sidechain_msgs)
        )

    def test_models_list_includes_sidechain_model(self):
        meta, _ = self.mod.parse_claude(self.log)
        self.assertEqual(meta["models_source"], "per-message")
        self.assertIn("claude-sonnet-5", meta["models"])
        self.assertIn("claude-haiku-4-5", meta["models"])
        # meta["model"] (singular, digest field) stays the first main-thread model
        self.assertEqual(meta["model"], "claude-sonnet-5")

    def test_usage_aggregates_including_sidechain(self):
        meta, _ = self.mod.parse_claude(self.log)
        self.assertEqual(meta["usage"], self.info["expected_tokens_with_sidechain"])

    def test_usage_by_model_split(self):
        meta, _ = self.mod.parse_claude(self.log)
        by = meta["usage_by_model"]
        self.assertEqual(by["claude-haiku-4-5"]["input"], 4000)
        self.assertEqual(by["claude-sonnet-5"]["input"], 2200)

    def test_digest_excludes_sidechain(self):
        meta, messages = self.mod.parse_claude(self.log)
        digest = self.mod.render_markdown(meta, messages)
        self.assertNotIn("SUBAGENT-SECRET", digest)
        self.assertIn("Done — agent booted", digest)

    def test_digest_byte_identical_to_sidechain_free_source(self):
        # render(full-with-sidechain) must equal render(same log minus sidechain).
        # Reuse the SAME path so meta["source"] (shown in the digest) matches;
        # the only intended difference is the presence of sidechain records.
        d_full = self.mod.render_markdown(*self.mod.parse_claude(self.log))
        write_claude_log(self.log, with_sidechain=False)
        d_main = self.mod.render_markdown(*self.mod.parse_claude(self.log))
        self.assertEqual(d_full, d_main)


class CodexParseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-archive-codex-")
        self.log = os.path.join(self.tmp, "rollout-codex.jsonl")
        self.info = write_codex_log(self.log)
        self.mod = load_mod()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_token_count_last_wins(self):
        meta, _ = self.mod.parse_codex(self.log)
        self.assertEqual(meta["usage"], self.info["expected_tokens"])

    def test_raw_capture(self):
        meta, messages = self.mod.parse_codex(self.log)
        tool = next(m for m in messages if "tool" in m)
        self.assertIn("uuid", tool["raw_args"])
        self.assertIn(self.info["lore_uuid"], tool["raw_result"])

    def test_models(self):
        meta, _ = self.mod.parse_codex(self.log)
        self.assertEqual(meta["models"], ["gpt-5-codex"])
        self.assertEqual(meta["models_source"], "per-message")


class StatsAndCostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-archive-stats-")
        self.mod = load_mod()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_claude_cost_computed(self):
        log = os.path.join(self.tmp, "c.jsonl")
        write_claude_log(log)
        meta, messages = self.mod.parse_claude(log)
        stats = self.mod.compute_stats(meta, messages)
        self.assertEqual(stats["cost_source"], "computed")
        # sonnet-5: (2200*2 + 500*10 + 1400*0.2 + 100*2.5)/1e6 = 0.00993
        # haiku-4.5: (4000*1 + 800*5)/1e6 = 0.008  -> total 0.01793
        self.assertAlmostEqual(stats["cost_usd"], 0.0179, places=4)
        self.assertEqual(stats["models_source"], "per-message")
        self.assertIn("claude-sonnet-5", stats["models"])

    def test_claude_unknown_model_unavailable(self):
        log = os.path.join(self.tmp, "c.jsonl")
        write_claude_log(log)
        meta, messages = self.mod.parse_claude(log)
        # inject a model with no price -> whole-session cost unavailable
        meta["usage_by_model"]["claude-nonexistent-9"] = {
            "input": 1, "output": 1, "cache_read": 0, "cache_creation": 0,
        }
        stats = self.mod.compute_stats(meta, messages)
        self.assertEqual(stats["cost_source"], "unavailable")
        self.assertIsNone(stats["cost_usd"])

    def test_codex_tokens_present_cost_unavailable(self):
        log = os.path.join(self.tmp, "rollout.jsonl")
        write_codex_log(log)
        meta, messages = self.mod.parse_codex(log)
        stats = self.mod.compute_stats(meta, messages)
        self.assertIsNotNone(stats["tokens"])
        self.assertEqual(stats["tokens"]["input"], 300)
        self.assertEqual(stats["cost_source"], "unavailable")
        self.assertIsNone(stats["cost_usd"])

    def test_cursor_tokens_unavailable(self):
        # A cursor meta with no usage -> tokens None, cost unavailable
        meta = {"engine": "cursor", "model": "haiku",
                "models": ["haiku"], "models_source": "session-level-last-used"}
        stats = self.mod.compute_stats(meta, [])
        self.assertIsNone(stats["tokens"])
        self.assertEqual(stats["cost_source"], "unavailable")
        self.assertEqual(stats["models_source"], "session-level-last-used")


class ArchiveBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-archive-build-")
        self.mod = load_mod()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_header_and_gzip_roundtrip(self):
        log = os.path.join(self.tmp, "c.jsonl")
        info = write_claude_log(log)
        meta, messages = self.mod.parse_claude(log)
        header, lines = self.mod.build_archive(meta, messages, info["lore_uuid"])
        self.assertEqual(header["schema_version"], self.mod.ARCHIVE_SCHEMA_VERSION)
        self.assertEqual(header["engine"], "claude")
        self.assertEqual(header["lore_uuid"], info["lore_uuid"])
        self.assertIn("generated_at", header)

        out = os.path.join(self.tmp, "a.jsonl.gz")
        self.mod.write_archive(out, header, lines)
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            recs = [json.loads(ln) for ln in fh if ln.strip()]
        self.assertEqual(recs[0]["schema_version"], self.mod.ARCHIVE_SCHEMA_VERSION)
        self.assertEqual(len(recs) - 1, len(lines))

    def test_archive_preserves_raw_and_sidechain(self):
        log = os.path.join(self.tmp, "c.jsonl")
        info = write_claude_log(log)
        meta, messages = self.mod.parse_claude(log)
        _, lines = self.mod.build_archive(meta, messages, info["lore_uuid"])
        tool = next(r for r in lines if r["type"] == "tool_call")
        # raw (untruncated) args/results, not the clipped one-liners
        self.assertIsInstance(tool["args"], dict)
        self.assertEqual(tool["result"], info["lore_uuid"])
        self.assertTrue(any(r.get("sidechain") for r in lines))
        self.assertTrue(
            any("SUBAGENT-SECRET" in (r.get("text") or "") for r in lines)
        )


class FindByUuidTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-archive-find-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        for k in ("CLAUDE_PROJECTS", "CODEX_HOME"):
            os.environ.pop(k, None)

    def test_claude_verified_match(self):
        projects = os.path.join(self.tmp, "claude-projects")
        target = claude_projects_session(projects, "sess-A", "UUID-AAA-111")
        # a decoy session without the uuid
        claude_projects_session(projects, "sess-B", "UUID-BBB-222")
        mod = load_mod(CLAUDE_PROJECTS=projects)
        path, conf = mod.find_native_log_by_uuid("UUID-AAA-111", "claude")
        self.assertEqual(conf, "verified")
        self.assertEqual(os.path.realpath(path), os.path.realpath(target))

    def test_codex_verified_match(self):
        codex_home = os.path.join(self.tmp, "codex")
        target = codex_sessions_log(codex_home, "codexsess", "UUID-CDX-999")
        mod = load_mod(CODEX_HOME=codex_home)
        path, conf = mod.find_native_log_by_uuid("UUID-CDX-999", "codex")
        self.assertEqual(conf, "verified")
        self.assertEqual(os.path.realpath(path), os.path.realpath(target))

    def test_heuristic_fallback_when_no_match(self):
        projects = os.path.join(self.tmp, "claude-projects")
        claude_projects_session(projects, "sess-A", "UUID-AAA-111")
        mod = load_mod(CLAUDE_PROJECTS=projects)
        path, conf = mod.find_native_log_by_uuid("UUID-NOT-PRESENT", "claude")
        self.assertEqual(conf, "heuristic")
        self.assertTrue(path.endswith(".jsonl"))

    def test_no_candidates_returns_none(self):
        projects = os.path.join(self.tmp, "empty-projects")
        os.makedirs(projects, exist_ok=True)
        mod = load_mod(CLAUDE_PROJECTS=projects)
        path, conf = mod.find_native_log_by_uuid("UUID-X", "claude")
        self.assertIsNone(path)
        self.assertIsNone(conf)


class CliArchiveVerbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-archive-cli-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_archive_verb_writes_gz_and_stats(self):
        log = os.path.join(self.tmp, "rollout.jsonl")
        info = write_codex_log(log)
        out = os.path.join(self.tmp, "2026", "07", "sess.jsonl.gz")
        stats = os.path.join(self.tmp, "stats.json")
        proc = subprocess.run(
            [sys.executable, SCRIPT, "archive", log,
             "-o", out, "--stats", stats,
             "--lore-uuid", "LORE-CLI-1", "--engine", "codex"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.isfile(out))  # dirs auto-created
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            header = json.loads(fh.readline())
        self.assertEqual(header["lore_uuid"], "LORE-CLI-1")
        self.assertEqual(header["engine"], "codex")
        with open(stats) as fh:
            s = json.load(fh)
        self.assertEqual(s["tokens"]["input"], 300)
        self.assertEqual(s["cost_source"], "unavailable")
        self.assertEqual(s["models"], ["gpt-5-codex"])
        # stats carries the archive locator for frontmatter assembly
        self.assertEqual(s["archive"]["path"], out)
        self.assertEqual(s["archive"]["schema_version"], 1)

    def test_find_by_uuid_cli_exit_codes(self):
        codex_home = os.path.join(self.tmp, "codex")
        codex_sessions_log(codex_home, "s1", "UUID-FIND-CLI")
        env = {**os.environ, "CODEX_HOME": codex_home}
        # match -> prints path, exit 0
        ok = subprocess.run(
            [sys.executable, SCRIPT, "--find-by-uuid", "UUID-FIND-CLI",
             "--engine", "codex"],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("rollout-", ok.stdout)
        # missing engine -> error exit
        bad = subprocess.run(
            [sys.executable, SCRIPT, "--find-by-uuid", "X"],
            capture_output=True, text=True, env=env,
        )
        self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
