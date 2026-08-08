#!/usr/bin/env python3
"""Static contracts for the v35 unified ``lr:style`` command.

Run: ``LR_FRAMEWORK_DIR=/path/to/lore-framework python3 tests/test_style_skills.py -v``
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest


def default_framework_dir():
    """Find the paired framework checkout for either a main checkout or a worktree."""
    dev_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if os.path.basename(os.path.dirname(dev_root)) == "lore-framework-dev":
        return os.path.join(
            os.path.dirname(os.path.dirname(dev_root)), "lore-framework", os.path.basename(dev_root)
        )
    return os.path.join(os.path.dirname(dev_root), "lore-framework")


FRAMEWORK_DIR = os.path.abspath(os.environ.get("LR_FRAMEWORK_DIR") or default_framework_dir())
if not os.path.isfile(os.path.join(FRAMEWORK_DIR, "VERSION")):
    raise RuntimeError(
        f"Lore framework not found at {FRAMEWORK_DIR}; set LR_FRAMEWORK_DIR to the framework under test."
    )


def read(relative_path):
    with open(os.path.join(FRAMEWORK_DIR, relative_path), encoding="utf-8") as fh:
        return fh.read()


class StyleSkillContractTests(unittest.TestCase):
    def test_single_public_skill_and_internal_components(self):
        self.assertTrue(os.path.isfile(os.path.join(FRAMEWORK_DIR, "skills", "style", "SKILL.md")))
        for old in ("plain-language", "dialogue", "follow-me"):
            self.assertFalse(os.path.exists(os.path.join(FRAMEWORK_DIR, "skills", old)), old)

        skill = read("skills/style/SKILL.md")
        self.assertIn("docs/style.md", skill)
        self.assertNotIn("docs/plain-language.md", skill)
        style = read("docs/style.md")
        for component in ("docs/plain-language.md", "docs/dialogue.md", "docs/follow-me.md"):
            self.assertIn(component, style)

    def test_selector_contract_is_explicit_and_complete_set_based(self):
        style = read("docs/style.md")
        for selector in ("`plain`", "`dialogue`", "`follow`", "`all`", "`off`"):
            self.assertIn(selector, style)
        self.assertIn("With no selector, use `all`.", style)
        self.assertIn("must be used alone", style)
        self.assertIn("unknown selector, a duplicate selector", style)
        self.assertIn("Replace the session's active style set", style)
        self.assertIn("Explicitly disable any previously", style)

    def test_all_engine_catalogs_publish_style_and_not_old_commands(self):
        self.assertTrue(os.path.isfile(os.path.join(FRAMEWORK_DIR, ".cursor-skills", "lr-style", "SKILL.md")))
        for old in ("lr-plain-language", "lr-dialogue", "lr-follow-me"):
            self.assertFalse(os.path.exists(os.path.join(FRAMEWORK_DIR, ".cursor-skills", old)), old)

        readme = read("README.md")
        self.assertIn("/lr:style", readme)
        for old in ("/lr:plain-language", "/lr:dialogue", "/lr:follow-me"):
            self.assertNotIn(old, readme)

        wrapper = read(".cursor-skills/lr-style/SKILL.md")
        self.assertIn("name: lr-style", wrapper)
        self.assertIn("/lr-style", wrapper)

        self.assertIn("/lr:style", read("README.md"))
        self.assertIn("$lr:style", read("docs/style.md"))
        self.assertIn("$lr:<skill>", read("docs/engines/codex.md"))

    def test_component_docs_are_internal_not_command_documentation(self):
        for path in ("docs/plain-language.md", "docs/dialogue.md", "docs/follow-me.md"):
            content = read(path)
            self.assertIn("canonical", content, path)
            self.assertIn("/lr:style", content, path)
        self.assertNotIn("/lr:plain-language", read("docs/plain-language.md"))
        self.assertNotIn("/lr:dialogue", read("docs/dialogue.md"))
        self.assertNotIn("/lr:follow-me", read("docs/follow-me.md"))

    def test_cursor_sync_check_is_read_only_and_detects_drift(self):
        tmp = tempfile.mkdtemp(prefix="lr-style-sync-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        copy = os.path.join(tmp, "framework")
        shutil.copytree(FRAMEWORK_DIR, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        script = os.path.join(copy, "scripts", "sync-cursor-skills")

        clean = subprocess.run([sys.executable, script, "--check"], capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)

        wrapper = os.path.join(copy, ".cursor-skills", "lr-style", "SKILL.md")
        with open(wrapper, "w", encoding="utf-8") as fh:
            fh.write("deliberately stale wrapper\n")
        stale = subprocess.run([sys.executable, script, "--check"], capture_output=True, text=True)
        self.assertEqual(stale.returncode, 1, stale.stdout + stale.stderr)
        with open(wrapper, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "deliberately stale wrapper\n")


if __name__ == "__main__":
    unittest.main()
