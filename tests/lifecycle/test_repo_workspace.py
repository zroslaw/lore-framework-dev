#!/usr/bin/env python3
"""Lifecycle scenarios 16-27: repo & workspace skills (catalog: workdir/draft-testing-pipeline.md).

create-repo, create-agent, the four workspace commands (init, pull, push, status), check,
update --dry-run, and the registration flows.

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
    AGENT_NAME, BROKEN_REF, CHECK_PROMPT, CLAUDE_IMPORT_LINE, CREATE_AGENT_PROMPT,
    CREATE_REPO_PROMPT, ENGINE, HELPER_AGENT_NAME, INIT_PROMPT, MANAGED_PROVENANCE,
    MEMORY_SECTIONS, REGISTER_AGENT_PROMPT, REGISTER_REPO_PROMPT,
    SKIP_REASON, UNREGISTER_AGENT_PROMPT, UNREGISTER_REPO_PROMPT,
    UPDATE_APPLY_PROMPT, UPDATE_DRYRUN_PROMPT, WORKSPACE_PULL_PROMPT,
    WORKSPACE_PUSH_PROMPT, WORKSPACE_STATUS_PROMPT,
    add_undeclared_child_repo, build_empty_workspace, build_fixture,
    declare_sibling_repo, dirty_managed_and_unmanaged, head, make_origin_ahead,
    make_workspace_meta_repo, memory_files, read_gitignore, read_repo_version,
    run_engine, seed_broken_reference,
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

        new_repo = os.path.join(workspace, ".tmp", "new-fixture-repo")
        self.assertTrue(
            os.path.isfile(os.path.join(new_repo, "lore-repo.md")),
            "lore-repo.md was not created under .tmp/new-fixture-repo",
        )
        self.assertTrue(
            os.path.isdir(os.path.join(new_repo, "agents")),
            "agents/ was not created under .tmp/new-fixture-repo",
        )
        self.assertFalse(
            os.path.exists(os.path.join(workspace, "new-fixture-repo")),
            "create-repo wrote a top-level new-fixture-repo; disposable fixtures belong under .tmp/",
        )
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
        with open(os.path.join(new_agent_dir, "lore-context.md"), encoding="utf-8") as f:
            context = f.read()
        self.assertIn("lore: 1", context, "new agent root is not Lore v1")
        self.assertIn("type: context", context, "new agent root lacks context type")

    def test_18_workspace_init(self):
        """workspace-init writes the v3 sectioned payload into AGENTS.md, on every engine."""
        workspace = build_empty_workspace(self.tmp)
        r = run_engine(workspace, INIT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        canonical, _stub = memory_files()
        memory_file = os.path.join(workspace, canonical)
        self.assertTrue(os.path.isfile(memory_file), f"{canonical} was not created")
        with open(memory_file, encoding="utf-8") as f:
            content = f.read()

        for heading in MEMORY_SECTIONS:
            self.assertIn(heading, content, f"missing canonical section heading {heading!r}")
        self.assertIn(MANAGED_PROVENANCE, content,
                      "managed sections carry no lr:managed provenance comment")
        # The v3 payload replaced the marker protocol outright; a marker here
        # means the executor followed a pre-v37 doc.
        self.assertNotIn("<!-- lr:workspace-init:start -->", content,
                         "v3 payload must not carry the retired marker protocol")

    def test_18b_claude_md_import(self):
        """CLAUDE.md is a one-line @AGENTS.md import stub, never a second copy of the payload.

        This is the standing re-verification of the memory-file experiment: Claude
        Code does not read AGENTS.md, so the import line is the only thing making
        workspace memory reach a Claude Code session. It is engine behavior rather
        than a contract, so it is re-measured every run instead of assumed.
        """
        if ENGINE != "claude":
            self.skipTest("the CLAUDE.md import stub is only load-bearing on Claude Code")
        workspace = build_empty_workspace(self.tmp)
        r = run_engine(workspace, INIT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        _canonical, stub = memory_files()
        stub_path = os.path.join(workspace, stub)
        self.assertTrue(os.path.isfile(stub_path), f"{stub} was not created")
        with open(stub_path, encoding="utf-8") as f:
            lines = [line.strip() for line in f]

        imports = [line for line in lines if line == CLAUDE_IMPORT_LINE]
        self.assertEqual(len(imports), 1,
                         f"expected exactly one {CLAUDE_IMPORT_LINE} line, found {len(imports)}")
        stub_text = "\n".join(lines)
        for heading in MEMORY_SECTIONS:
            self.assertNotIn(heading, stub_text,
                             f"{stub} carries the payload section {heading!r} — "
                             "the payload belongs in AGENTS.md only, or it will drift")

    def test_19_workspace_pull(self):
        """workspace-pull clones a declared-but-missing sibling and pulls an existing repo."""
        fx = build_fixture(self.tmp)
        make_origin_ahead(fx)  # test-lore itself should get pulled up to date

        sibling_bare = os.path.join(self.tmp, "declared-sibling.git")
        subprocess.run(["git", "init", "--bare", "-b", "main", sibling_bare],
                        capture_output=True, text=True, check=True)
        declare_sibling_repo(fx, sibling_bare)

        # Phase 3 must ignore EVERY child git repo on disk, not only declared
        # ones: an undeclared clone can be committed into the workspace repo
        # just as easily as a declared one.
        make_workspace_meta_repo(fx)
        add_undeclared_child_repo(fx, "undeclared-child")

        r = run_engine(fx.workspace, WORKSPACE_PULL_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        cloned = os.path.join(fx.workspace, "declared-sibling")
        self.assertTrue(os.path.isdir(cloned), "declared sibling repo was not cloned")
        self.assertEqual(
            head(fx.repo), head(fx.origin, "main"),
            "existing repo (test-lore) was not pulled up to date",
        )

        ignore_lines = read_gitignore(fx.workspace)
        self.assertIn("/undeclared-child/", ignore_lines,
                      "phase 3 did not ignore an undeclared child git repo")

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
        # This scenario verifies dry-run non-mutation, not every historical
        # migration. Keep exactly one pending version so an engine spends its
        # budget exercising the contract under test instead of narrating the
        # entire release history.
        fx = build_fixture(self.tmp, version="35")
        r = run_engine(fx.workspace, UPDATE_DRYRUN_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertEqual(
            read_repo_version(fx), "35",
            "dry-run must not modify lore-repo.md",
        )
        self.assertIn("35", r.text)
        self.assertIn(harness.framework_version(), r.text)

    def test_21b_update_commits_and_pushes_owned_changes(self):
        """A successful update publishes its narrow commit to the existing upstream."""
        fx = build_fixture(self.tmp, version="35")
        subprocess.run(
            ["git", "-C", fx.repo, "config", "user.name", "lr-tests"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", fx.repo, "config", "user.email", "lr-tests@localhost"],
            check=True,
        )
        before = head(fx.repo)
        self.assertEqual(before, head(fx.origin, "refs/heads/main"))

        r = run_engine(fx.workspace, UPDATE_APPLY_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        after = head(fx.repo)
        self.assertNotEqual(after, before, "update must create a commit")
        self.assertEqual(
            after, head(fx.origin, "refs/heads/main"),
            "update commit must reach the existing upstream",
        )
        self.assertEqual(read_repo_version(fx), harness.framework_version())
        status = subprocess.run(
            ["git", "-C", fx.repo, "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertEqual(status, "", "published update must leave a clean fixture")
        subject = subprocess.run(
            ["git", "-C", fx.repo, "log", "-1", "--format=%s"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(
            subject,
            f"chore(lore): update framework to v{harness.framework_version()}",
        )
        git_dir = subprocess.run(
            ["git", "-C", fx.repo, "rev-parse", "--absolute-git-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertFalse(
            os.path.exists(os.path.join(git_dir, "lr-update-pending")),
            "successful push must clear its retry marker",
        )
        self.assertIn("committed and pushed", r.text)

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
        self.assertNotIn("plugins/cache/", content)
        self.assertNotIn("/docs/agent-boot.md", content)
        if harness.ENGINE == "cursor":
            self.assertIn("installed `/lr-boot` skill", content)
            self.assertIn("name: lr-test-agent-agent", content)
            self.assertIn("disable-model-invocation: true", content)
            self.assertIn(f'"{harness.REPO_NAME}/**"', content)
        elif harness.ENGINE == "claude":
            self.assertIn("installed `/lr:boot` skill", content)

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

    def test_26_workspace_push(self):
        """workspace-push commits only framework-managed paths, and a teammate receives them."""
        fx = build_fixture(self.tmp)
        workspace_origin = make_workspace_meta_repo(fx)
        managed, unmanaged = dirty_managed_and_unmanaged(fx)

        r = run_engine(fx.workspace, WORKSPACE_PUSH_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        committed = subprocess.run(
            ["git", "-C", fx.workspace, "show", "--name-only", "--format=", "HEAD"],
            capture_output=True, text=True,
        ).stdout.split()
        self.assertIn("AGENTS.md", committed,
                      f"the dirty framework-managed file was not committed: {committed}")
        self.assertNotIn(
            os.path.basename(unmanaged), committed,
            "workspace-push committed a path outside the framework-managed set — "
            "unrelated user work must never ship under a generic message",
        )
        self.assertTrue(
            os.path.isfile(unmanaged),
            "workspace-push must leave non-managed dirty files on disk untouched",
        )
        self.assertTrue(managed)  # named for readability of the failure above

        # The point of publishing is that somebody else receives it.
        teammate = os.path.join(self.tmp, "teammate-workspace")
        subprocess.run(["git", "clone", workspace_origin, teammate],
                       capture_output=True, text=True, check=True)
        self.assertTrue(
            os.path.isfile(os.path.join(teammate, "AGENTS.md")),
            "a fresh clone of the workspace origin did not receive the pushed memory file",
        )

    def test_27_workspace_status(self):
        """workspace-status reports the expected finding IDs on a deliberately messy workspace."""
        fx = build_fixture(self.tmp)
        make_workspace_meta_repo(fx)
        dirty_managed_and_unmanaged(fx)          # -> S1 (dirty managed), S12 (dirty other)
        add_undeclared_child_repo(fx, "undeclared-child")  # -> S5 (undeclared), S7 (unignored)

        r = run_engine(fx.workspace, WORKSPACE_STATUS_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        for finding in ("S1", "S5", "S7"):
            self.assertIn(finding, r.text,
                          f"status did not report {finding} on a workspace that exhibits it:\n{r.text}")
        self.assertNotIn(
            "workspace clean", r.text,
            "status reported a clean workspace while findings were present",
        )
        # Read-only: the messy state must survive the diagnosis untouched.
        self.assertTrue(
            os.path.isfile(os.path.join(fx.workspace, "my-private-notes.md")),
            "workspace-status is read-only and must not remove user files",
        )
        self.assertTrue(
            subprocess.run(["git", "-C", fx.workspace, "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip(),
            "workspace-status committed or cleaned something — it must write nothing",
        )


if __name__ == "__main__":
    unittest.main()
