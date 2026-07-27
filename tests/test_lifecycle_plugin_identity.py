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


class CodexPromptPassthrough(unittest.TestCase):
    def test_identity_probe_does_not_inject_framework_dir(self):
        rewritten = harness.codex_prompt(harness.PLUGIN_IDENTITY_PROMPT)
        self.assertNotIn(harness.FRAMEWORK_DIR, rewritten)
        self.assertIn("FRAMEWORK-ROOT:", rewritten)
        self.assertIn("PLUGIN-VERSION:", rewritten)


if __name__ == "__main__":
    unittest.main()
