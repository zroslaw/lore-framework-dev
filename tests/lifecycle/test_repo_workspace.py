#!/usr/bin/env python3
"""Lifecycle scenarios 17-26: repo & workspace skills (catalog: workdir/draft-testing-pipeline.md).

create-repo, create-agent, workspace-init, workspace-pull, check, update --dry-run, and registration flows.

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_repo_workspace.py -v
One:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_repo_workspace.py -v -k 16
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import (
    AGENT_NAME, BROKEN_REF, CHECK_PROMPT, CREATE_AGENT_PROMPT, CREATE_REPO_PROMPT,
    HELPER_AGENT_NAME, INIT_PROMPT, REGISTER_AGENT_PROMPT, REGISTER_REPO_PROMPT,
    SKIP_REASON, UNREGISTER_AGENT_PROMPT, UNREGISTER_REPO_PROMPT,
    UPDATE_DRYRUN_PROMPT, WORKSPACE_PULL_PROMPT,
    build_empty_workspace, build_fixture, declare_sibling_repo, head,
    make_origin_ahead, memory_file_name, read_repo_version, run_engine, seed_broken_reference,
)


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class RepoWorkspaceScenarios(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        if os.environ.get("LR_KEEP_FIXTURES"):
            print(f"\n  [fixture kept] {self.tmp}", file=sys.stderr)
        else:
            self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_16_create_repo(self):
        """create-repo scaffolds a valid, git-initialized agent repo in an empty workspace."""
        workspace = build_empty_workspace(self.tmp)
        r = run_engine(workspace, CREATE_REPO_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        new_repo = os.path.join(workspace, "new-fixture-repo")
        self.assertTrue(
            os.path.isfile(os.path.join(new_repo, "lore-repo.md")),
            "lore-repo.md was not created",
        )
        self.assertTrue(os.path.isdir(os.path.join(new_repo, "agents")), "agents/ was not created")
        rev_parse = subprocess.run(
            ["git", "-C", new_repo, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True,
        )
        self.assertEqual(rev_parse.returncode, 0, "new repo was not git-initialized")
        log = subprocess.run(["git", "-C", new_repo, "log", "--oneline"], capture_output=True, text=True)
        self.assertTrue(log.stdout.strip(), "new repo has no initial commit")

    def test_17_create_agent(self):
        """create-agent adds a fully structured agent to an existing repo."""
        fx = build_fixture(self.tmp)
        r = run_engine(fx.workspace, CREATE_AGENT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        new_agent_dir = os.path.join(fx.repo, "agents", "second-fixture-agent")
        for required in ("role.md", "lore-context.md", "lore", "workdir"):
            self.assertTrue(
                os.path.exists(os.path.join(new_agent_dir, required)),
                f"new agent missing {required}",
            )

    def test_18_workspace_init(self):
        """workspace-init writes the marker-delimited framework section into the engine's memory file."""
        workspace = build_empty_workspace(self.tmp)
        r = run_engine(workspace, INIT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        memory_file = os.path.join(workspace, memory_file_name())
        self.assertTrue(os.path.isfile(memory_file), f"{memory_file_name()} was not created")
        with open(memory_file) as f:
            content = f.read()
        self.assertIn("<!-- lr:workspace-init:start -->", content)
        self.assertIn("<!-- lr:workspace-init:end -->", content)
        self.assertIn("Lore Framework Workspace", content)

    def test_19_workspace_pull(self):
        """workspace-pull clones a declared-but-missing sibling and pulls an existing repo."""
        fx = build_fixture(self.tmp)
        make_origin_ahead(fx)  # test-lore itself should get pulled up to date

        sibling_bare = os.path.join(self.tmp, "declared-sibling.git")
        subprocess.run(["git", "init", "--bare", "-b", "main", sibling_bare],
                        capture_output=True, text=True, check=True)
        declare_sibling_repo(fx, sibling_bare)

        r = run_engine(fx.workspace, WORKSPACE_PULL_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        cloned = os.path.join(fx.workspace, "declared-sibling")
        self.assertTrue(os.path.isdir(cloned), "declared sibling repo was not cloned")
        self.assertEqual(
            head(fx.repo), head(fx.origin, "main"),
            "existing repo (test-lore) was not pulled up to date",
        )

    def test_20_check_catches_seeded_violation(self):
        """check surfaces a deliberately broken lore-context.md cross-reference."""
        fx = build_fixture(self.tmp)
        seed_broken_reference(fx)
        r = run_engine(fx.workspace, CHECK_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn(
            BROKEN_REF, r.text,
            f"check did not flag the seeded broken cross-reference:\n{r.text}",
        )

    def test_21_update_dry_run_does_not_write(self):
        """update --dry-run reports the pending upgrade but leaves lore-repo.md untouched."""
        fx = build_fixture(self.tmp, version="17")
        r = run_engine(fx.workspace, UPDATE_DRYRUN_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertEqual(
            read_repo_version(fx), "17",
            "dry-run must not modify lore-repo.md",
        )
        self.assertIn("17", r.text)
        self.assertIn(harness.framework_version(), r.text)

    def _shortcut_paths(self, workspace, agent_name):
        if harness.ENGINE == "cursor":
            base = os.path.join(workspace, ".cursor", "skills", f"lr-{agent_name}-agent")
            return base, os.path.join(base, "SKILL.md")
        if harness.ENGINE == "claude":
            path = os.path.join(workspace, ".claude", "commands", f"lr-{agent_name}-agent.md")
            return path, path
        self.skipTest("registration lifecycle scenarios are not isolated on codex yet")

    def test_22_register_agent(self):
        """register-agent creates one engine-native shortcut with the current template."""
        fx = build_fixture(self.tmp)
        r = run_engine(fx.workspace, REGISTER_AGENT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        _, skill_file = self._shortcut_paths(fx.workspace, AGENT_NAME)
        self.assertTrue(os.path.isfile(skill_file), "agent shortcut was not created")
        with open(skill_file) as f:
            content = f.read()
        self.assertIn("boot as agent", content)
        self.assertIn("from", content)
        self.assertIn(os.path.join(fx.repo, "agents", AGENT_NAME), content)
        if harness.ENGINE == "cursor":
            self.assertIn("name: lr-test-agent-agent", content)
            self.assertIn("disable-model-invocation: true", content)
            self.assertIn(f'"{harness.REPO_NAME}/**"', content)

    def test_23_register_repo(self):
        """register-repo creates shortcuts for every agent in the repo."""
        fx = build_fixture(self.tmp, second_agent=True)
        r = run_engine(fx.workspace, REGISTER_REPO_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        for agent_name in (AGENT_NAME, HELPER_AGENT_NAME):
            _, skill_file = self._shortcut_paths(fx.workspace, agent_name)
            self.assertTrue(os.path.isfile(skill_file), f"missing shortcut for {agent_name}")

    def test_24_unregister_agent(self):
        """unregister-agent removes only the targeted shortcut."""
        fx = build_fixture(self.tmp, second_agent=True)
        r1 = run_engine(fx.workspace, REGISTER_REPO_PROMPT)
        self.assertEqual(r1.exit_code, 0, f"register run failed: {r1.stderr[-500:]}")

        r2 = run_engine(fx.workspace, UNREGISTER_AGENT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r2.summary()}")
        self.assertEqual(r2.exit_code, 0, f"engine run failed: {r2.stderr[-500:]}")

        target_dir, target_file = self._shortcut_paths(fx.workspace, AGENT_NAME)
        other_dir, other_file = self._shortcut_paths(fx.workspace, HELPER_AGENT_NAME)
        self.assertFalse(os.path.exists(target_dir), "target shortcut still exists")
        self.assertTrue(os.path.isfile(other_file), "non-target shortcut was removed too")

    def test_25_unregister_repo(self):
        """unregister-repo removes every shortcut associated with the repo."""
        fx = build_fixture(self.tmp, second_agent=True)
        r1 = run_engine(fx.workspace, REGISTER_REPO_PROMPT)
        self.assertEqual(r1.exit_code, 0, f"register run failed: {r1.stderr[-500:]}")

        r2 = run_engine(fx.workspace, UNREGISTER_REPO_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r2.summary()}")
        self.assertEqual(r2.exit_code, 0, f"engine run failed: {r2.stderr[-500:]}")

        for agent_name in (AGENT_NAME, HELPER_AGENT_NAME):
            target_dir, _ = self._shortcut_paths(fx.workspace, agent_name)
            self.assertFalse(os.path.exists(target_dir), f"shortcut still exists for {agent_name}")


if __name__ == "__main__":
    unittest.main()
