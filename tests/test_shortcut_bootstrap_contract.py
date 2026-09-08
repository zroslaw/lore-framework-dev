#!/usr/bin/env python3
"""Static contract tests for version-independent registered boot shortcuts."""

import os
import sys
import tempfile
from pathlib import Path
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
            self.assertIn(
                "boot as agent `<agent-name>` from `<agent-dir-rel>`", content, path)

    def test_bootstrap_emits_a_relative_agent_dir(self):
        """A generated shortcut is committed, so its agent path must be relative.

        An absolute `<agent-dir>` is true only on the machine that generated it.
        A teammate cloning the workspace gets a shortcut pointing at a directory
        they do not have, and `workspace-status` — which matches shortcuts by
        their embedded target — reports every such agent as unregistered while
        the shortcut sits in git. See `conventions.md` § Committed Artifacts
        Carry Relative Paths, and `migrations/44.md`.

        Asserting the negative matters as much as the positive here: a profile
        that gained the relative form while leaving the absolute one in an
        adjacent example would satisfy the positive assertion alone.
        """
        for path in ("docs/engines/claude.md", "docs/engines/cursor.md",
                     "docs/engines/codex.md"):
            content = read(path)
            marker = "## Registered shortcut bootstrap"
            section = content.split(marker, 1)[1]
            fence_start = section.index("```markdown") + len("```markdown\n")
            body = section[fence_start:section.index("```", fence_start)]
            self.assertIn("<agent-dir-rel>", body, path)
            self.assertNotIn("from `<agent-dir>`", body, path)

    def check_shortcut_body(self, transform):
        sys.path.insert(0, os.path.join(FRAMEWORK_DIR, "scripts"))
        from lr_core.repo_scan import bootstrap_template, check_shortcuts
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            agent = root / "repo/agents/test"
            agent.mkdir(parents=True)
            (agent / "role.md").write_text("# Test\n")
            body = bootstrap_template(FRAMEWORK_DIR, "codex").replace(
                "<agent-name>", "test").replace("<agent-dir-rel>", "repo/agents/test")
            path = root / ".codex/skills/lr-test-agent/SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\nname: lr-test-agent\ndescription: Test\n---\n\n" +
                            transform(body, str(agent)) + "\n")
            findings, warnings = [], []
            check_shortcuts(str(root), FRAMEWORK_DIR, findings, warnings)
            return findings

    def test_check_flags_an_absolute_from_target(self):
        rows = self.check_shortcut_body(lambda body, target: body.replace("repo/agents/test", target))
        self.assertTrue(any(row["id"] == "R12" and
                            "absolute_workspace_target" in row["data"]["reasons"] for row in rows))

    def test_conventions_owns_the_relative_path_rule(self):
        """The rule is stated once, where both the profiles and check.md point."""
        conventions = read("docs/conventions.md")
        self.assertIn("## Committed Artifacts Carry Relative Paths", conventions)
        self.assertIn("<agent-dir-rel>", conventions)

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
        rows = self.check_shortcut_body(lambda body, _: body.replace("then read", "then\nread"))
        self.assertTrue(any(row["id"] == "R12" for row in rows))

    def test_check_rejects_stale_cache_pins(self):
        rows = self.check_shortcut_body(lambda body, _: body.replace(
            "its `docs/agent-boot.md`", "`/tmp/plugins/cache/lr/docs/agent-boot.md`"))
        self.assertTrue(any(row["id"] == "R12" for row in rows))
        self.assertIn("fix-stale-shortcut-bootstrap.md", read("docs/findings-catalog.md"))
        self.assertIn("plugins/cache/", read("docs/fix-stale-shortcut-bootstrap.md"))


if __name__ == "__main__":
    unittest.main()
