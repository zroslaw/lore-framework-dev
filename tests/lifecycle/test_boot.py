#!/usr/bin/env python3
"""Lifecycle scenarios 1-7: boot (catalog: workdir/draft-testing-pipeline.md).

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_boot.py -v
One:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_boot.py -v -k 01
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import (
    AGENT_NAME, BOOT_PROMPT, BOOT_UNKNOWN_PROMPT, CTX_CANARY, FRESH_CANARY,
    ROLE_CANARY, SKIP_REASON, break_origin, build_fixture, dirty_role_md, head,
    is_clean, make_origin_ahead, read_repo_version, run_engine,
)


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class BootScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.fx = build_fixture(tmp)

    def _boot(self):
        r = run_engine(self.fx.workspace, BOOT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        return r

    def _assert_booted(self, r):
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertNotIn("BOOT-FAILED", r.text, f"boot reported failure:\n{r.text}")
        self.assertIn(ROLE_CANARY, r.text, f"role.md canary missing:\n{r.text}")
        self.assertIn(CTX_CANARY, r.text, f"lore-context.md canary missing:\n{r.text}")

    def test_01_boot_happy_path(self):
        """Boot confirms role; role.md and lore-context.md actually read."""
        before = head(self.fx.repo)
        r = self._boot()
        self._assert_booted(r)
        self.assertEqual(head(self.fx.repo), before, "boot must not create commits")

    def test_02_boot_pulls_fresh_commits(self):
        """Origin is one commit ahead; boot auto-pull fast-forwards to it."""
        make_origin_ahead(self.fx)
        r = self._boot()
        self._assert_booted(r)
        self.assertEqual(
            head(self.fx.repo), head(self.fx.origin, "main"),
            "local repo not fast-forwarded to origin after boot",
        )
        fresh = os.path.join(self.fx.agent_dir, "lore", "fresh-fact.md")
        self.assertTrue(os.path.exists(fresh), "pulled topic file missing")
        with open(fresh) as f:
            self.assertIn(FRESH_CANARY, f.read())

    def test_03_boot_degraded_remote_unreachable(self):
        """Origin unreachable; auto-pull fails but boot still completes."""
        break_origin(self.fx)
        r = self._boot()
        self._assert_booted(r)

    def test_04_boot_unknown_agent(self):
        """Booting a nonexistent agent fails cleanly and lists real agents."""
        r = run_engine(self.fx.workspace, BOOT_UNKNOWN_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn("BOOT-FAILED", r.text, f"unknown-agent boot did not fail cleanly:\n{r.text}")
        self.assertIn(
            AGENT_NAME, r.text,
            f"error did not list the real available agent '{AGENT_NAME}':\n{r.text}",
        )


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class BootUpgradeScenarios(unittest.TestCase):
    """Scenarios 5-6: version-mismatch auto-upgrade at boot time."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_05_boot_version_mismatch_release_notes_only(self):
        """Repo one version behind (release-notes-only bump); boot upgrades and stamps it."""
        fx = build_fixture(self.tmp, version="17")
        r = run_engine(fx.workspace, BOOT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertNotIn("BOOT-FAILED", r.text, f"boot reported failure:\n{r.text}")
        self.assertIn(ROLE_CANARY, r.text)
        self.assertIn(CTX_CANARY, r.text)
        self.assertEqual(
            read_repo_version(fx), harness.framework_version(),
            "lore-repo.md was not stamped to the current framework version",
        )
        self.assertFalse(
            is_clean(fx.repo),
            "version stamp must be left uncommitted for the user to review",
        )

    def test_06_boot_upgrade_gate_on_dirty_tree(self):
        """Repo far behind with a dirty file in the upgrade's write-set; boot defers, doesn't overwrite."""
        fx = build_fixture(self.tmp, version="1")
        dirty_role_md(fx)  # collides with migration 2's write-set: agents/*/role.md
        with open(os.path.join(fx.agent_dir, "role.md")) as f:
            dirty_content = f.read()

        r = run_engine(fx.workspace, BOOT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertNotIn("BOOT-FAILED", r.text, f"boot reported failure:\n{r.text}")
        # Boot must still load the agent in degraded mode despite the deferred upgrade.
        self.assertIn(ROLE_CANARY, r.text)

        self.assertEqual(
            read_repo_version(fx), "1",
            "upgrade should have deferred (dirty-tree collision) — version must stay at 1",
        )
        with open(os.path.join(fx.agent_dir, "role.md")) as f:
            self.assertEqual(
                f.read(), dirty_content,
                "the dirty role.md must be left untouched when the upgrade defers",
            )

    def test_07_boot_repo_newer_than_framework_codex_guidance(self):
        """Codex warns with the engine-specific plugin refresh remedy when R > F."""
        if harness.ENGINE != "codex":
            self.skipTest("Codex-specific mismatch guidance scenario")

        expected_repo_version = str(int(harness.framework_version()) + 1)
        fx = build_fixture(self.tmp, version=expected_repo_version)
        prompt = harness._codex_boot_prompt(
            AGENT_NAME,
            "If boot emits a version-mismatch warning, print that warning verbatim before "
            "anything else. Then print two lines:\n"
            "BOOT-CODEWORD: <the boot codeword stated in your role>\n"
            "CONTEXT-CODEWORD: <the context codeword stated in your lore-context>\n"
            "If boot fails, print BOOT-FAILED followed by the reason. "
            "Do not reflect, merge, finalize, commit, or push.",
        )

        r = run_engine(fx.workspace, prompt)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertNotIn("BOOT-FAILED", r.text, f"boot reported failure:\n{r.text}")
        self.assertIn(ROLE_CANARY, r.text)
        self.assertIn(CTX_CANARY, r.text)
        self.assertIn("your Codex plugin is older than the repo", r.text)
        self.assertIn("codex plugin add lr@lore-framework", r.text)
        self.assertIn("codex plugin marketplace upgrade lore-framework", r.text)
        self.assertEqual(
            read_repo_version(fx), expected_repo_version,
            "R > F guidance must not rewrite the repo version",
        )
        self.assertTrue(
            is_clean(fx.repo),
            "R > F guidance must not modify tracked files in the repo",
        )


if __name__ == "__main__":
    unittest.main()
