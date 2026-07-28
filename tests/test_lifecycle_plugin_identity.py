#!/usr/bin/env python3
"""Unit tests for lifecycle plugin-identity gating (A7).

No engine / no network — covers parse + assert helpers and the Codex
marketplace source preflight that catches the 2026-07-27 silent-v30 bug.
"""

import os
import sys
import tempfile
import unittest

LIFECYCLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lifecycle")
sys.path.insert(0, LIFECYCLE)
import harness  # noqa: E402


class ParsePluginIdentity(unittest.TestCase):
    def test_extracts_root_and_version(self):
        root, version = harness.parse_plugin_identity(
            "noise\nFRAMEWORK-ROOT: /tmp/fw\nPLUGIN-VERSION: 31\nmore\n"
        )
        self.assertEqual(root, "/tmp/fw")
        self.assertEqual(version, "31")

    def test_missing_lines_yield_none(self):
        root, version = harness.parse_plugin_identity("nope")
        self.assertIsNone(root)
        self.assertIsNone(version)

    def test_empty_text(self):
        self.assertEqual(harness.parse_plugin_identity(""), (None, None))
        self.assertEqual(harness.parse_plugin_identity(None), (None, None))


class NormalizeFrameworkVersion(unittest.TestCase):
    def test_bare_integer(self):
        self.assertEqual(harness.normalize_framework_version("30"), "30")
        self.assertEqual(harness.normalize_framework_version(" 31\n"), "31")

    def test_manifest_form(self):
        self.assertEqual(harness.normalize_framework_version("1.30.0"), "30")
        self.assertEqual(harness.normalize_framework_version("1.31"), "31")

    def test_unknown_passthrough(self):
        self.assertEqual(harness.normalize_framework_version("2.30.0"), "2.30.0")
        self.assertIsNone(harness.normalize_framework_version(None))
        self.assertIsNone(harness.normalize_framework_version(""))


class AssertPluginIdentityMatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-id-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        with open(os.path.join(self.tmp, "VERSION"), "w", encoding="utf-8") as f:
            f.write("31\n")

    def test_match_passes(self):
        harness.assert_plugin_identity_match("31", self.tmp, self.tmp)

    def test_manifest_version_matches_bare_version(self):
        harness.assert_plugin_identity_match("1.31.0", self.tmp, self.tmp)

    def test_version_mismatch_raises(self):
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.assert_plugin_identity_match("30", self.tmp, self.tmp)
        msg = str(ctx.exception)
        self.assertIn("PLUGIN-VERSION '30' != expected '31'", msg)
        self.assertIn("LR_SKIP_PLUGIN_IDENTITY", msg)

    def test_missing_version_raises(self):
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.assert_plugin_identity_match(None, self.tmp, self.tmp)
        self.assertIn("PLUGIN-VERSION line missing", str(ctx.exception))

    def test_root_mismatch_raises(self):
        other = tempfile.mkdtemp(prefix="lr-id-other-")
        self.addCleanup(lambda: __import__("shutil").rmtree(other, ignore_errors=True))
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.assert_plugin_identity_match("31", other, self.tmp)
        self.assertIn("FRAMEWORK-ROOT", str(ctx.exception))

    def test_root_optional_when_version_matches(self):
        harness.assert_plugin_identity_match("31", None, self.tmp)

    def test_require_root_false_ignores_path_mismatch(self):
        other = tempfile.mkdtemp(prefix="lr-id-other-")
        self.addCleanup(lambda: __import__("shutil").rmtree(other, ignore_errors=True))
        harness.assert_plugin_identity_match(
            "31", other, self.tmp, require_root=False,
        )


class CodexMarketplaceSource(unittest.TestCase):
    SAMPLE = """
[marketplaces.other]
source = "/elsewhere"

[marketplaces.lore-framework]
source_type = "local"
source = "/Users/me/agent-workspace/lore-framework"

[plugins."lr@lore-framework"]
enabled = true
"""

    def test_reads_source(self):
        self.assertEqual(
            harness.read_codex_lore_marketplace_source(self.SAMPLE),
            "/Users/me/agent-workspace/lore-framework",
        )

    def test_detects_enabled(self):
        self.assertTrue(harness.codex_lr_plugin_enabled(self.SAMPLE))
        self.assertFalse(harness.codex_lr_plugin_enabled("[plugins.\"lr@lore-framework\"]\nenabled = false\n"))
        self.assertFalse(harness.codex_lr_plugin_enabled(""))

    def test_mismatch_raises(self):
        fw = tempfile.mkdtemp(prefix="lr-id-fw-")
        self.addCleanup(lambda: __import__("shutil").rmtree(fw, ignore_errors=True))
        with open(os.path.join(fw, "VERSION"), "w", encoding="utf-8") as f:
            f.write("31\n")
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.check_codex_plugin_sources(
                fw, config_text=self.SAMPLE, cache_root=os.path.join(fw, "no-cache"),
            )
        self.assertIn("marketplace source", str(ctx.exception))

    def test_matching_source_passes_without_cache(self):
        fw = tempfile.mkdtemp(prefix="lr-id-fw-")
        self.addCleanup(lambda: __import__("shutil").rmtree(fw, ignore_errors=True))
        with open(os.path.join(fw, "VERSION"), "w", encoding="utf-8") as f:
            f.write("31\n")
        config = (
            "[marketplaces.lore-framework]\n"
            f'source = "{fw}"\n'
            '[plugins."lr@lore-framework"]\n'
            "enabled = true\n"
        )
        harness.check_codex_plugin_sources(
            fw, config_text=config, cache_root=os.path.join(fw, "no-cache"),
        )

    def test_cache_without_matching_version_raises(self):
        fw = tempfile.mkdtemp(prefix="lr-id-fw-")
        cache = tempfile.mkdtemp(prefix="lr-id-cache-")
        self.addCleanup(lambda: __import__("shutil").rmtree(fw, ignore_errors=True))
        self.addCleanup(lambda: __import__("shutil").rmtree(cache, ignore_errors=True))
        with open(os.path.join(fw, "VERSION"), "w", encoding="utf-8") as f:
            f.write("31\n")
        entry = os.path.join(cache, "1.30.0")
        os.makedirs(entry)
        with open(os.path.join(entry, "VERSION"), "w", encoding="utf-8") as f:
            f.write("30\n")
        config = (
            "[marketplaces.lore-framework]\n"
            f'source = "{fw}"\n'
            '[plugins."lr@lore-framework"]\n'
            "enabled = true\n"
        )
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.check_codex_plugin_sources(fw, config_text=config, cache_root=cache)
        self.assertIn("plugin cache", str(ctx.exception))

    def test_disabled_plugin_skips(self):
        fw = tempfile.mkdtemp(prefix="lr-id-fw-")
        self.addCleanup(lambda: __import__("shutil").rmtree(fw, ignore_errors=True))
        with open(os.path.join(fw, "VERSION"), "w", encoding="utf-8") as f:
            f.write("31\n")
        config = (
            "[marketplaces.lore-framework]\n"
            'source = "/wrong"\n'
            '[plugins."lr@lore-framework"]\n'
            "enabled = false\n"
        )
        harness.check_codex_plugin_sources(
            fw, config_text=config, cache_root=os.path.join(fw, "no-cache"),
        )


class CursorPluginSources(unittest.TestCase):
    """The 2026-07-27 silent-v30 bug, from the Cursor side.

    Cursor's identity gate was a model self-report only: the probe reported
    `PLUGIN-IDENTITY-OK 31 <worktree>` while cached v30 trees served the actual
    run. These cover the deterministic filesystem preflight that catches it.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-cursor-id-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.fw = os.path.join(self.tmp, "worktree")
        os.makedirs(self.fw)
        with open(os.path.join(self.fw, "VERSION"), "w", encoding="utf-8") as f:
            f.write("31\n")
        self.plugins = os.path.join(self.tmp, "plugins")

    def _tree(self, relpath, version):
        path = os.path.join(self.plugins, relpath)
        os.makedirs(path)
        with open(os.path.join(path, "VERSION"), "w", encoding="utf-8") as f:
            f.write(f"{version}\n")
        return path

    def test_missing_plugins_root_is_a_noop(self):
        harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)

    def test_matching_version_passes(self):
        self._tree("local/lore-framework", "31")
        harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)

    def test_cached_stale_tree_is_a_conflict(self):
        self._tree("cache/zroslaw-lore-framework/lr/11ec0df", "30")
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)
        self.assertIn("outrank --plugin-dir", str(ctx.exception))
        self.assertIn("v30", str(ctx.exception))

    def test_marketplace_tree_is_a_conflict(self):
        self._tree("marketplaces/github.com/zroslaw/lore-framework/11ec0df", "30")
        with self.assertRaises(harness.PluginIdentityError):
            harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)

    def test_reproduces_the_20260727_layout(self):
        """v31 local worktree link alongside two v30 trees — the run that lied."""
        self._tree("cache/zroslaw-lore-framework/lr/11ec0df", "30")
        self._tree("marketplaces/github.com/zroslaw/lore-framework/11ec0df", "30")
        self._tree("local/lore-framework", "31")
        with self.assertRaises(harness.PluginIdentityError) as ctx:
            harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)
        detail = str(ctx.exception)
        # Both stale trees must be named; a partial report sends the user to move
        # one aside and re-run into the same failure.
        self.assertIn("cache/zroslaw-lore-framework", detail)
        self.assertIn("marketplaces/github.com", detail)
        self.assertNotIn("local/lore-framework", detail)

    def test_tree_resolving_to_framework_dir_is_not_a_conflict(self):
        """`local/` is normally a link to the tree under test; realpath equality wins."""
        os.makedirs(os.path.join(self.plugins, "local"))
        link = os.path.join(self.plugins, "local", "lore-framework")
        os.symlink(self.fw, link)
        harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)

    def test_manifest_form_version_normalizes(self):
        self._tree("cache/zroslaw-lore-framework/lr/abc", "1.31.0")
        harness.check_cursor_plugin_sources(self.fw, plugins_root=self.plugins)


class CodexAgentMessages(unittest.TestCase):
    """Transcript extraction from Codex's --json stream.

    `text` comes from --output-last-message, so anything the agent said mid-run
    is absent from it. test_08 asserts the Script Fallback notice, which is
    emitted mid-boot — it needs the transcript or a compliant run reads as a
    violation. Event shape verified live against gpt-5.4-mini.
    """

    STREAM = (
        '{"type": "thread.started", "thread_id": "019fa606"}\n'
        '{"type": "turn.started"}\n'
        '{"type": "item.completed", "item": {"id": "item_0", '
        '"type": "agent_message", "text": "lr-core preflight failed"}}\n'
        '{"type": "item.completed", "item": {"id": "item_1", '
        '"type": "agent_message", "text": "BOOT-CODEWORD: X"}}\n'
        '{"type": "turn.completed", "usage": {"output_tokens": 43}}\n'
    )

    def test_extracts_agent_messages_in_order(self):
        self.assertEqual(
            harness.codex_agent_messages(self.STREAM),
            ["lr-core preflight failed", "BOOT-CODEWORD: X"],
        )

    def test_ignores_non_agent_items(self):
        """A token in a tool call or file path must not count as telling the user."""
        stream = (
            '{"type": "item.completed", "item": {"type": "command_execution", '
            '"command": "python3 /fw/scripts/lr-core preflight"}}\n'
            '{"type": "item.completed", "item": {"type": "reasoning", '
            '"text": "I should mention lr-core"}}\n'
        )
        self.assertEqual(harness.codex_agent_messages(stream), [])

    def test_tolerates_noise_and_empty(self):
        self.assertEqual(harness.codex_agent_messages(""), [])
        self.assertEqual(harness.codex_agent_messages(None), [])
        self.assertEqual(harness.codex_agent_messages("not json\n\n"), [])
        self.assertEqual(harness.codex_agent_messages('{"type": "turn.started"}'), [])

    def test_run_result_transcript_defaults_to_text(self):
        """Claude and Cursor expose no event stream; transcript must not be empty."""
        r = harness.RunResult(0, "final only", None, None, "")
        self.assertEqual(r.transcript, "final only")

    def test_run_result_keeps_explicit_transcript(self):
        r = harness.RunResult(0, "final", None, None, "", transcript="said\nfinal")
        self.assertEqual(r.text, "final")
        self.assertEqual(r.transcript, "said\nfinal")


class CodexPromptPassthrough(unittest.TestCase):
    def test_identity_probe_does_not_inject_framework_dir(self):
        rewritten = harness.codex_prompt(harness.PLUGIN_IDENTITY_PROMPT)
        self.assertNotIn(harness.FRAMEWORK_DIR, rewritten)
        self.assertIn("FRAMEWORK-ROOT:", rewritten)
        self.assertIn("PLUGIN-VERSION:", rewritten)


if __name__ == "__main__":
    unittest.main()
