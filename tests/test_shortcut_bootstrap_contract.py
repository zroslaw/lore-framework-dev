#!/usr/bin/env python3
"""Static contract tests for version-independent registered boot shortcuts."""

import os
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


class ShortcutBootstrapContractTests(unittest.TestCase):
    def test_registration_template_has_no_boot_path_placeholder(self):
        content = read("docs/register-repo.md")
        self.assertNotIn("Read `<agent-boot-path>`", content)
        self.assertIn("<shortcut-bootstrap>", content)
        self.assertIn("Resolve the shortcut bootstrap", content)

    def test_each_engine_owns_an_active_boot_skill_binding(self):
        expected = {
            "docs/engines/claude.md": "installed `/lr:boot` skill",
            "docs/engines/cursor.md": "installed `/lr-boot` skill",
            "docs/engines/codex.md": "installed `lr:boot` skill",
        }
        for path, skill_name in expected.items():
            content = read(path)
            self.assertIn("## Registered shortcut bootstrap", content, path)
            self.assertIn(skill_name, content, path)
            self.assertIn("boot as agent `<agent-name>` from `<agent-dir>`", content, path)

    def test_doctor_and_check_reject_stale_cache_pins(self):
        doctor = read("docs/doctor.md")
        ailment = read("docs/doctor-stale-shortcut-bootstrap.md")
        check = read("docs/check.md")
        self.assertIn("doctor-stale-shortcut-bootstrap", doctor)
        self.assertIn("plugins/cache/", ailment)
        self.assertIn("plugins/cache/", check)
        self.assertIn("absolute `agent-boot.md` path", check)


if __name__ == "__main__":
    unittest.main()
