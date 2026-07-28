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

    def test_bootstrap_body_is_a_single_line(self):
        """A generated shortcut is one line, so the template must be one line.

        `migrations/33.md` reports an existing shortcut as `current` only on a
        byte-for-byte match against a freshly generated artifact, and Claude Code
        renders a command's description from the file's first line. A profile
        whose fenced bootstrap is wrapped for readability gets copied verbatim,
        and both of those break quietly.
        """
        for path in ("docs/engines/claude.md", "docs/engines/cursor.md",
                     "docs/engines/codex.md"):
            content = read(path)
            marker = "## Registered shortcut bootstrap"
            section = content.split(marker, 1)[1]
            fence_start = section.index("```markdown") + len("```markdown\n")
            body = section[fence_start:section.index("```", fence_start)]
            self.assertEqual(
                len(body.strip().splitlines()), 1,
                f"{path}: bootstrap body must be a single unwrapped line")

    def test_check_flags_a_wrapped_bootstrap(self):
        """A shortcut can be correct in content and wrong in shape.

        `/lr:check` is what a user runs against their own workspace, so the
        single-line rule has to be enforceable there and not only in the
        generator's own docs.
        """
        check = read("docs/check.md")
        section = check.split("## 18. Legacy registered shortcut formats", 1)[1]
        section = section.split("\n## ", 1)[0]
        self.assertIn("more than one line", section)

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
