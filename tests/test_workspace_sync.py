#!/usr/bin/env python3
"""Tests for lr_core.workspace_sync — the workspace-wide git reconciliation command.

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only (unittest),
matching test_workspace_refresh.py. The plugin under test is located via
$LR_FRAMEWORK_DIR, defaulting to the sibling ../lore-framework; that default is wrong
under the worktree convention, so set it explicitly there.

Every test builds a real workspace in a tempdir: bare repos standing in for origin,
clones standing in for the working copies. No network, nothing touching the real
workspace. Assertions are on observable git state (what is committed, what origin
holds, what survived) as well as on the JSON report, because the report is a claim
about the repository and the repository is the fact.

Run:  python3 tests/test_workspace_sync.py -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
LR_CORE = os.path.join(FRAMEWORK_DIR, "scripts", "lr-core")

sys.path.insert(0, os.path.join(FRAMEWORK_DIR, "scripts"))
from lr_core import workspace_sync as ws  # noqa: E402

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
    "HOME": "/nonexistent-home-for-tests",
}


def git(repo, *args):
    env = os.environ.copy()
    env.update(GIT_ENV)
    return subprocess.run(["git", "-C", repo] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          env=env, timeout=60)


def git_out(repo, *args):
    proc = git(repo, *args)
    return proc.stdout.decode().strip()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class SyncCase(unittest.TestCase):
    """A workspace with an origin server directory and a working checkout."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="lr-sync-"))
        self.origins = os.path.join(self.tmp, "origins")
        self.ws = os.path.join(self.tmp, "workspace")
        os.makedirs(self.origins)
        os.makedirs(self.ws)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- fixture helpers ---------------------------------------------------

    def make_repo(self, name, lore=True, clone_name=None):
        """A bare origin with one initial commit, plus a clone in the workspace."""
        bare = os.path.join(self.origins, name + ".git")
        subprocess.run(["git", "init", "--bare", "-b", "main", bare],
                       stdout=subprocess.DEVNULL, check=True)
        seed = os.path.join(self.tmp, "seed-" + name)
        subprocess.run(["git", "init", "-b", "main", seed],
                       stdout=subprocess.DEVNULL, check=True)
        write(os.path.join(seed, "README.md"), "seed\n")
        if lore:
            write(os.path.join(seed, "lore-repo.md"),
                  "---\ndescription: test repo\nversion: 45\n---\n")
        git(seed, "add", "-A")
        git(seed, "commit", "-m", "seed")
        git(seed, "remote", "add", "origin", bare)
        git(seed, "push", "-u", "origin", "main")
        shutil.rmtree(seed)

        checkout = os.path.join(self.ws, clone_name or name)
        subprocess.run(["git", "clone", bare, checkout],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        git(checkout, "config", "user.name", "test")
        git(checkout, "config", "user.email", "test@example.com")
        return bare, checkout

    def other_clone(self, name):
        """A second checkout of the same origin — stands in for another session."""
        path = os.path.join(self.tmp, "other-" + name)
        subprocess.run(["git", "clone", os.path.join(self.origins, name + ".git"), path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        git(path, "config", "user.name", "other")
        git(path, "config", "user.email", "other@example.com")
        return path

    def sync(self, *flags, **kwargs):
        """Drive the real CLI and return the parsed report."""
        workspace = kwargs.pop("workspace", self.ws)
        env = os.environ.copy()
        env.update(GIT_ENV)
        proc = subprocess.run(
            [sys.executable, LR_CORE, "workspace-sync", "--workspace", workspace] + list(flags),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=180)
        self.assertNotEqual(proc.returncode, 2,
                            "lr-core exited fatal: %s" % proc.stderr.decode()[:500])
        return json.loads(proc.stdout.decode())

    def repo_report(self, report, name):
        for entry in report["data"]["repos"]:
            if entry["name"] == name:
                return entry
        self.fail("no report entry for %s (got %s)"
                  % (name, [e["name"] for e in report["data"]["repos"]]))


class TestPublishPath(SyncCase):

    def test_dirty_lore_repo_is_committed_and_pushed(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")
        write(os.path.join(checkout, "README.md"), "seed\nedited\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(entry["push"], "pushed")
        self.assertIn("lore/finding.md", entry["committed"])
        self.assertIn("README.md", entry["committed"])
        # The fact, not the claim: origin now holds the file.
        self.assertIn("lore/finding.md", git_out(bare, "ls-tree", "-r", "--name-only", "HEAD"))
        self.assertEqual(git_out(checkout, "status", "--porcelain"), "")

    def test_clean_repo_does_nothing(self):
        _, checkout = self.make_repo("lore-a")
        before = git_out(checkout, "rev-parse", "HEAD")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(entry["committed"], [])
        self.assertEqual(entry["integrate"], "up-to-date")
        self.assertEqual(entry["push"], "nothing-to-push")
        self.assertEqual(git_out(checkout, "rev-parse", "HEAD"), before)

    def test_remote_ahead_is_integrated_then_local_published(self):
        bare, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "theirs.md"), "theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")

        write(os.path.join(checkout, "lore", "mine.md"), "mine\n")
        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(entry["integrate"], "merged")
        self.assertEqual(entry["push"], "pushed")
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("lore/theirs.md", tree)
        self.assertIn("lore/mine.md", tree)

    def test_fast_forward_when_nothing_local(self):
        _, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "theirs.md"), "theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertEqual(entry["integrate"], "fast-forward")
        self.assertTrue(os.path.exists(os.path.join(checkout, "lore", "theirs.md")))

    def test_junk_is_neither_committed_nor_deleted(self):
        _, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "lore", "real.md"), "real\n")
        junk = os.path.join(checkout, ".notes.md.swp")
        write(junk, "binary junk\n")
        write(os.path.join(checkout, ".DS_Store"), "junk\n")
        write(os.path.join(checkout, "__pycache__", "x.pyc"), "junk\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertEqual(entry["committed"], ["lore/real.md"])
        self.assertEqual(sorted(entry["left_dirty"]),
                         [".DS_Store", ".notes.md.swp", "__pycache__/x.pyc"])
        self.assertTrue(all(h["reason"] for h in entry["held"]))
        self.assertTrue(os.path.exists(junk), "junk must be left alone, never deleted")

    def test_deletions_and_renames_are_published(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "lore", "old.md"), "content\n")
        git(checkout, "add", "-A")
        git(checkout, "commit", "-m", "add old")
        git(checkout, "push")

        os.rename(os.path.join(checkout, "lore", "old.md"),
                  os.path.join(checkout, "lore", "new.md"))
        os.remove(os.path.join(checkout, "README.md"))

        report = self.sync()
        self.assertTrue(report["ok"], report["errors"])
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("lore/new.md", tree)
        self.assertNotIn("lore/old.md", tree)
        self.assertNotIn("README.md", tree)

    def test_no_push_leaves_work_local_and_says_so(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")

        report = self.sync("--no-push")
        entry = self.repo_report(report, "lore-a")

        self.assertEqual(entry["push"], "local-only")
        self.assertEqual(entry["status"], "local-only")
        self.assertFalse(report["ok"], "local-only is pending publication, not success")
        self.assertNotIn("lore/finding.md", git_out(bare, "ls-tree", "-r", "--name-only", "HEAD"))
        self.assertNotEqual(git_out(checkout, "log", "-1", "--pretty=%s"), "seed")


class TestConflicts(SyncCase):

    def _conflicting_workspace(self):
        bare, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "topic.md"), "their version\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        write(os.path.join(checkout, "lore", "topic.md"), "my version\n")
        return bare, checkout

    def test_conflict_blocks_and_preserves_both_sides(self):
        bare, checkout = self._conflicting_workspace()
        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertFalse(report["ok"])
        self.assertEqual(entry["integrate"], "conflict")
        self.assertEqual(entry["conflicts"], ["lore/topic.md"])
        # Local work was committed before the merge, so it is safe in history...
        self.assertTrue(entry["commit"])
        body = open(os.path.join(checkout, "lore", "topic.md")).read()
        self.assertIn("my version", body)
        self.assertIn("their version", body)
        self.assertIn("<<<<<<<", body)

    def test_rerun_after_resolution_commits_and_pushes(self):
        bare, checkout = self._conflicting_workspace()
        self.sync()  # leaves the merge in progress

        write(os.path.join(checkout, "lore", "topic.md"), "my version\ntheir version\n")
        git(checkout, "add", "lore/topic.md")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertIn("committed the resolved merge", entry["actions"])
        self.assertEqual(entry["push"], "pushed")
        merged = git_out(bare, "show", "HEAD:lore/topic.md")
        self.assertIn("my version", merged)
        self.assertIn("their version", merged)

    def test_rerun_while_still_conflicted_stays_blocked(self):
        self._conflicting_workspace()
        self.sync()
        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertFalse(report["ok"])
        self.assertEqual(entry["conflicts"], ["lore/topic.md"])

    def test_foreign_operation_in_progress_is_refused(self):
        _, checkout = self.make_repo("lore-a")
        # A cherry-pick stopped at a conflict is somebody else's half-done work.
        git(checkout, "checkout", "-b", "side")
        write(os.path.join(checkout, "lore", "topic.md"), "side\n")
        git(checkout, "add", "-A")
        git(checkout, "commit", "-m", "side")
        side = git_out(checkout, "rev-parse", "HEAD")
        git(checkout, "checkout", "main")
        write(os.path.join(checkout, "lore", "topic.md"), "main\n")
        git(checkout, "add", "-A")
        git(checkout, "commit", "-m", "main")
        git(checkout, "cherry-pick", side)

        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertFalse(report["ok"])
        self.assertIn("cherry-pick", entry["blocked"])
        self.assertEqual(entry["committed"], [])


class TestSourceRepos(SyncCase):

    def test_source_repo_is_pulled_but_never_published(self):
        bare, checkout = self.make_repo("product-api", lore=False)
        other = self.other_clone("product-api")
        write(os.path.join(other, "src.py"), "upstream\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "upstream")
        git(other, "push")
        write(os.path.join(checkout, "wip.py"), "my work in progress\n")

        report = self.sync()
        entry = self.repo_report(report, "product-api")

        self.assertEqual(entry["kind"], "source")
        self.assertEqual(entry["integrate"], "fast-forward")
        self.assertEqual(entry["committed"], [])
        self.assertIsNone(entry["push"])
        self.assertIn("wip.py", entry["left_dirty"])
        # The upstream change arrived and the WIP file is untouched on disk.
        self.assertTrue(os.path.exists(os.path.join(checkout, "src.py")))
        self.assertEqual(open(os.path.join(checkout, "wip.py")).read(),
                         "my work in progress\n")
        self.assertNotIn("wip.py", git_out(bare, "ls-tree", "-r", "--name-only", "HEAD"))


class TestRefusals(SyncCase):

    def test_detached_head_is_blocked_not_guessed(self):
        _, checkout = self.make_repo("lore-a")
        git(checkout, "checkout", "--detach", "HEAD")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertFalse(report["ok"])
        self.assertIn("detached", entry["blocked"])
        self.assertEqual(entry["committed"], [])

    def test_no_origin_is_skipped_not_failed(self):
        _, checkout = self.make_repo("lore-a")
        git(checkout, "remote", "remove", "origin")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertTrue(report["ok"], "an ordinary local-only repo is not a failure")
        self.assertIsNone(entry["blocked"])
        self.assertIn("no remote configured", entry["skipped"])

    def test_branch_with_no_remote_counterpart_commits_but_does_not_publish(self):
        bare, checkout = self.make_repo("lore-a")
        git(checkout, "checkout", "-b", "private-branch")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertFalse(report["ok"])
        self.assertEqual(entry["status"], "local-only")
        self.assertIn("no upstream", entry["blocked"])
        self.assertIn("push -u", entry["blocked"], "the remedy must be named")
        # The work is safe in local history, and origin never grew a new branch.
        self.assertIn("lore/finding.md", entry["committed"])
        self.assertNotIn("private-branch", git_out(bare, "branch", "--list"))

    def test_untracked_upstream_falls_back_to_origin_branch(self):
        bare, checkout = self.make_repo("lore-a")
        git(checkout, "branch", "--unset-upstream")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(entry["target"], "origin/main")
        self.assertEqual(entry["push"], "pushed")


class TestDryRun(SyncCase):

    def test_dry_run_writes_nothing(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")
        before_head = git_out(checkout, "rev-parse", "HEAD")
        before_origin = git_out(bare, "rev-parse", "HEAD")

        report = self.sync("--dry-run")
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["data"]["dry_run"])
        self.assertIn("would commit 1 path(s)", entry["actions"])
        self.assertEqual(entry["committed"], [])
        self.assertEqual(git_out(checkout, "rev-parse", "HEAD"), before_head)
        self.assertEqual(git_out(bare, "rev-parse", "HEAD"), before_origin)
        self.assertNotEqual(git_out(checkout, "status", "--porcelain"), "")


class TestWorktrees(SyncCase):

    def test_dead_registration_is_pruned(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-dead")
        git(checkout, "worktree", "add", "-b", "dead-branch", wt)
        shutil.rmtree(wt)

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertEqual(entry["worktrees"]["pruned"], [wt])
        self.assertNotIn("wt-dead", git_out(checkout, "worktree", "list"))

    def test_live_worktree_is_kept_without_the_flag(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-live")
        git(checkout, "worktree", "add", "-b", "live-branch", wt)

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertEqual(entry["worktrees"]["removed"], [])
        self.assertTrue(os.path.isdir(wt))
        self.assertEqual([r["path"] for r in entry["worktrees"]["retained"]], [wt])

    def test_dirty_worktree_survives_prune_flag(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-dirty")
        git(checkout, "worktree", "add", "-b", "dirty-branch", wt)
        write(os.path.join(wt, "scratch.md"), "unsaved work\n")

        entry = self.repo_report(self.sync("--prune-worktrees"), "lore-a")
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertIn(wt, retained)
        self.assertIn("uncommitted", retained[wt])
        self.assertTrue(os.path.exists(os.path.join(wt, "scratch.md")))

    def test_unmerged_worktree_survives_prune_flag(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-unmerged")
        git(checkout, "worktree", "add", "-b", "unmerged-branch", wt)
        write(os.path.join(wt, "work.md"), "committed but unmerged\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-m", "work")

        entry = self.repo_report(self.sync("--prune-worktrees"), "lore-a")
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertIn(wt, retained)
        self.assertIn("not in", retained[wt])
        self.assertTrue(os.path.isdir(wt))

    def test_clean_merged_worktree_is_removed_with_the_flag(self):
        _, checkout = self.make_repo("lore-a")
        # origin/HEAD is what the merged check compares against; a fresh clone has it.
        self.assertTrue(git_out(checkout, "symbolic-ref", "--short",
                                "refs/remotes/origin/HEAD"))
        wt = os.path.join(self.tmp, "wt-clean")
        git(checkout, "worktree", "add", "-b", "clean-branch", wt)

        entry = self.repo_report(self.sync("--prune-worktrees"), "lore-a")
        self.assertEqual(entry["worktrees"]["removed"], [wt])
        self.assertFalse(os.path.isdir(wt))


class TestPushRetry(SyncCase):
    """The rejection path, driven by a real race with another checkout."""

    def test_push_rejection_is_reintegrated_and_retried(self):
        bare, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(checkout, "lore", "mine.md"), "mine\n")

        # A pre-push hook on the bare repo advances origin exactly once, after this
        # run has already fetched — the real shape of "somebody pushed while I worked".
        hook = os.path.join(bare, "hooks", "pre-receive")
        write(hook, "#!/bin/sh\nexit 0\n")
        os.chmod(hook, 0o755)

        def advance_origin():
            write(os.path.join(other, "lore", "theirs.md"), "theirs\n")
            git(other, "add", "-A")
            git(other, "commit", "-m", "theirs")
            git(other, "push")

        # Deterministic race: advance origin after the module has fetched but before
        # it pushes, by wrapping the module's own push call once.
        original_git = ws.git
        state = {"advanced": False}

        def racing_git(repo, args, **kwargs):
            if args and args[0] == "push" and not state["advanced"]:
                state["advanced"] = True
                advance_origin()
            return original_git(repo, args, **kwargs)

        ws.git = racing_git
        try:
            entry = ws.sync_repo({"name": "lore-a", "path": checkout, "kind": "lore"})
        finally:
            ws.git = original_git

        self.assertEqual(entry["push"], "pushed")
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("lore/mine.md", tree)
        self.assertIn("lore/theirs.md", tree)


class TestInvariants(unittest.TestCase):
    """The prohibitions are easier to break than to notice, so they are asserted.

    Parsed from the AST rather than grepped from the text: the module's own header
    names every forbidden operation *because* it forbids them, so a text search either
    trips on the prose or gets weakened until it proves nothing. Walking the actual
    `git(...)` call sites asserts what the module can execute.
    """

    ALLOWED_SUBCOMMANDS = {
        "add", "branch", "cat-file", "commit", "config", "diff-tree", "fetch", "log",
        "merge",
        "push", "remote", "rev-list", "rev-parse", "show", "status", "symbolic-ref",
        "worktree",
    }
    FORBIDDEN_SUBCOMMANDS = {"reset", "clean", "rebase", "stash", "checkout",
                             "restore", "filter-branch", "gc", "prune"}
    FORBIDDEN_FLAGS = {"--force", "-f", "--force-with-lease", "--hard", "--autostash",
                       "--allow-empty"}

    def _git_argv_literals(self):
        import ast
        path = os.path.join(FRAMEWORK_DIR, "scripts", "lr_core", "workspace_sync.py")
        tree = ast.parse(open(path, encoding="utf-8").read())
        argvs = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None)
            if name != "git" or len(node.args) < 2:
                continue
            arg = node.args[1]
            self.assertIsInstance(arg, ast.List,
                                  "git() argv must be a literal list so it can be audited")
            argvs.append([e.value if isinstance(e, ast.Constant) else "<dynamic>"
                          for e in arg.elts])
        self.assertTrue(argvs, "no git() call sites found — the audit would be vacuous")
        return argvs

    def test_every_git_subcommand_is_allowlisted(self):
        for argv in self._git_argv_literals():
            sub = argv[0]
            self.assertNotIn(sub, self.FORBIDDEN_SUBCOMMANDS,
                             "forbidden git subcommand: %s" % " ".join(map(str, argv)))
            self.assertIn(sub, self.ALLOWED_SUBCOMMANDS,
                          "unreviewed git subcommand: %s" % " ".join(map(str, argv)))

    def test_no_destructive_flags(self):
        for argv in self._git_argv_literals():
            for token in argv[1:]:
                base = str(token).split("=")[0]
                self.assertNotIn(base, self.FORBIDDEN_FLAGS,
                                 "forbidden flag in: %s" % " ".join(map(str, argv)))

    def test_worktree_calls_are_restricted_to_list_prune_and_remove(self):
        for argv in self._git_argv_literals():
            if argv[0] == "worktree":
                self.assertIn(argv[1], ("list", "prune", "remove"), argv)

    def test_junk_filter_boundaries(self):
        self.assertTrue(ws.is_junk("notes/.x.md.swp"))
        self.assertTrue(ws.is_junk(".DS_Store"))
        self.assertTrue(ws.is_junk("a/__pycache__/b.pyc"))
        self.assertTrue(ws.is_junk("lore/topic.md.orig"))
        self.assertFalse(ws.is_junk("lore/topic.md"))
        self.assertFalse(ws.is_junk("lore/swap-notes.md"))
        self.assertFalse(ws.is_junk("workdir/cache/data.json"))

    def test_unmerged_paths_detects_every_conflict_code(self):
        entries = [("UU", "a"), ("AA", "b"), ("DD", "c"), ("AU", "d"),
                   ("UD", "e"), (" M", "clean"), ("??", "new")]
        self.assertEqual(ws.unmerged_paths(entries), ["a", "b", "c", "d", "e"])


class TestClassification(SyncCase):

    def test_lore_source_and_workspace_repos_are_told_apart(self):
        self.make_repo("lore-a", lore=True)
        self.make_repo("product-api", lore=False)
        # The workspace root is its own repo here.
        subprocess.run(["git", "init", "-b", "main", self.ws],
                       stdout=subprocess.DEVNULL, check=True)
        kinds = {r["name"]: r["kind"] for r in ws.classify_repos(self.ws)}
        self.assertEqual(kinds["lore-a"], "lore")
        self.assertEqual(kinds["product-api"], "source")
        self.assertEqual(kinds["workspace"], "workspace")

    def test_plain_directory_is_not_a_repo(self):
        os.makedirs(os.path.join(self.ws, "notes"))
        names = {r["name"] for r in ws.classify_repos(self.ws)}
        self.assertNotIn("notes", names)


class TestHolds(SyncCase):
    """Paths that must never reach a shared remote, whatever else is true."""

    def test_nested_repository_is_held_not_published_as_an_empty_gitlink(self):
        bare, checkout = self.make_repo("lore-a")
        nested = os.path.join(checkout, "workdir", "vendored")
        subprocess.run(["git", "init", "-b", "main", nested],
                       stdout=subprocess.DEVNULL, check=True)
        write(os.path.join(nested, "file.md"), "content\n")
        git(nested, "add", "-A")
        git(nested, "commit", "-m", "inner")
        write(os.path.join(checkout, "lore", "real.md"), "real\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertEqual(entry["committed"], ["lore/real.md"])
        held = {h["path"]: h["reason"] for h in entry["held"]}
        self.assertTrue(any("vendored" in p for p in held), held)
        # The decisive fact: origin holds no gitlink entry for the nested repo.
        raw = git_out(bare, "ls-tree", "-r", "HEAD")
        self.assertNotIn("160000", raw)

    def test_credential_shaped_names_are_held(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, ".env"), "TOKEN=secret\n")
        write(os.path.join(checkout, "keys", "deploy.pem"), "PRIVATE KEY\n")
        write(os.path.join(checkout, "agents", "a", "id_ed25519"), "KEY\n")
        write(os.path.join(checkout, "lore", "real.md"), "real\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertEqual(entry["committed"], ["lore/real.md"])
        held = sorted(h["path"] for h in entry["held"])
        self.assertEqual(held, [".env", "agents/a/id_ed25519", "keys/deploy.pem"])
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        for path in held:
            self.assertNotIn(path, tree)
            self.assertTrue(os.path.exists(os.path.join(checkout, path)),
                            "a held file is left on disk, never deleted")

    def test_oversized_file_is_held(self):
        _, checkout = self.make_repo("lore-a")
        big = os.path.join(checkout, "workdir", "dump.bin")
        os.makedirs(os.path.dirname(big), exist_ok=True)
        with open(big, "wb") as fh:
            fh.write(b"\0" * (ws.MAX_COMMIT_BYTES + 1))

        entry = self.repo_report(self.sync(), "lore-a")
        held = {h["path"]: h["reason"] for h in entry["held"]}
        self.assertIn("workdir/dump.bin", held)
        self.assertIn("MB", held["workdir/dump.bin"])
        self.assertEqual(entry["committed"], [])

    def test_another_sessions_staged_file_is_not_swept_into_the_commit(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "lore", "mine.md"), "mine\n")
        # A concurrent session staged something of its own between scan and commit.
        write(os.path.join(checkout, "lore", "theirs-wip.md"), "half written\n")
        git(checkout, "add", "lore/theirs-wip.md")

        # Scan happens inside the command; simulate the race by staging first and
        # driving the module against an entry list that predates it.
        entries = [("??", "lore/mine.md")]
        result = ws.commit_local(checkout, entries)
        self.assertEqual(result["committed"], ["lore/mine.md"])
        committed = git_out(checkout, "show", "--name-only", "--pretty=format:", "HEAD")
        self.assertIn("lore/mine.md", committed)
        self.assertNotIn("theirs-wip.md", committed)


class TestMergeOwnership(SyncCase):

    def test_foreign_merge_is_refused(self):
        _, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "theirs.md"), "theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        git(checkout, "fetch", "origin")
        # A human inspecting a merge before accepting it: MERGE_HEAD present, no
        # unmerged paths, and emphatically not this command's business to commit.
        git(checkout, "merge", "--no-commit", "--no-ff", "origin/main")
        self.assertTrue(os.path.exists(
            os.path.join(checkout, ".git", "MERGE_HEAD")))

        report = self.sync()
        entry = self.repo_report(report, "lore-a")
        self.assertFalse(report["ok"])
        self.assertIn("did not start", entry["blocked"])
        self.assertEqual(git_out(checkout, "log", "-1", "--pretty=%s"), "seed")

    def test_staged_but_unresolved_markers_block_the_resume(self):
        _, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "topic.md"), "their version\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        write(os.path.join(checkout, "lore", "topic.md"), "my version\n")
        self.sync()  # leaves a claimed conflict

        # `git add` clears the unmerged entry even with the markers still in place.
        git(checkout, "add", "lore/topic.md")
        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertFalse(report["ok"])
        self.assertIn("conflict markers", entry["blocked"])
        self.assertEqual(entry["conflicts"], ["lore/topic.md"])
        self.assertIn("<<<<<<<", open(os.path.join(checkout, "lore", "topic.md")).read())

    def test_source_repo_mid_merge_is_never_committed(self):
        _, checkout = self.make_repo("product-api", lore=False)
        other = self.other_clone("product-api")
        write(os.path.join(other, "src.py"), "theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        write(os.path.join(checkout, "src.py"), "mine\n")
        git(checkout, "add", "-A")
        git(checkout, "commit", "-m", "mine")
        git(checkout, "fetch", "origin")
        git(checkout, "merge", "origin/main")  # conflicts, left in progress

        report = self.sync()
        entry = self.repo_report(report, "product-api")
        self.assertFalse(report["ok"])
        self.assertIn("source repository", entry["blocked"])
        self.assertEqual(git_out(checkout, "log", "-1", "--pretty=%s"), "mine")


class TestMergeRefused(SyncCase):

    def test_untracked_junk_colliding_with_an_incoming_file_is_reported_not_pushed(self):
        bare, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, ".DS_Store"), "theirs\n")
        git(other, "add", "-f", ".DS_Store")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        # Held back locally by the junk filter, so it is still untracked here.
        write(os.path.join(checkout, ".DS_Store"), "mine\n")
        write(os.path.join(checkout, "lore", "real.md"), "real\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertFalse(report["ok"])
        self.assertEqual(entry["integrate"], "refused")
        self.assertIn("declined to merge", entry["blocked"])
        self.assertIsNone(entry["push"], "a refused merge must never be followed by a push")
        self.assertEqual(open(os.path.join(checkout, ".DS_Store")).read(), "mine\n")


class TestUpstreamResolution(SyncCase):

    def test_publishes_to_the_tracked_branch_not_the_local_branch_name(self):
        bare, checkout = self.make_repo("lore-a")
        git(checkout, "checkout", "-b", "work")
        git(checkout, "branch", "--set-upstream-to", "origin/main")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(entry["target"], "origin/main")
        self.assertEqual(entry["push"], "pushed")
        self.assertIn("lore/finding.md",
                      git_out(bare, "ls-tree", "-r", "--name-only", "refs/heads/main"))
        self.assertNotIn("work", git_out(bare, "branch", "--list"))

    def test_a_non_origin_remote_is_used_for_both_fetch_and_push(self):
        _, checkout = self.make_repo("lore-a")
        fork_bare = os.path.join(self.origins, "fork.git")
        subprocess.run(["git", "init", "--bare", "-b", "main", fork_bare],
                       stdout=subprocess.DEVNULL, check=True)
        git(checkout, "remote", "add", "fork", fork_bare)
        git(checkout, "push", "fork", "main")
        git(checkout, "fetch", "fork")
        git(checkout, "branch", "--set-upstream-to", "fork/main")
        write(os.path.join(checkout, "lore", "finding.md"), "a finding\n")

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertEqual(entry["target"], "fork/main")
        self.assertEqual(entry["push"], "pushed")
        self.assertIn("lore/finding.md",
                      git_out(fork_bare, "ls-tree", "-r", "--name-only", "HEAD"))
        # origin, the remote it does NOT track, was left alone.
        self.assertNotIn("lore/finding.md",
                         git_out(os.path.join(self.origins, "lore-a.git"),
                                 "ls-tree", "-r", "--name-only", "HEAD"))


class TestPruneSafety(SyncCase):

    def test_registration_whose_parent_is_absent_is_not_pruned(self):
        _, checkout = self.make_repo("lore-a")
        holder = os.path.join(self.tmp, "volume", "wt")
        os.makedirs(os.path.dirname(holder))
        git(checkout, "worktree", "add", "-b", "vol-branch", holder)
        # The signature of an unmounted volume: the whole parent path is gone.
        shutil.rmtree(os.path.join(self.tmp, "volume"))

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertEqual(entry["worktrees"]["pruned"], [])
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertIn("unmounted", retained.get(holder, ""))
        self.assertIn("wt", git_out(checkout, "worktree", "list"))

    def test_registration_holding_unreferenced_commits_is_not_pruned(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-detached")
        git(checkout, "worktree", "add", "--detach", wt)
        write(os.path.join(wt, "work.md"), "orphan work\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-m", "orphan")
        sha = git_out(wt, "rev-parse", "HEAD")
        shutil.rmtree(wt)

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertEqual(entry["worktrees"]["pruned"], [])
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertIn("no branch points at", retained.get(wt, ""))
        # The commit is still there to be recovered.
        self.assertEqual(git_out(checkout, "cat-file", "-t", sha), "commit")


class TestRoundOneRegressions(SyncCase):
    """One test per finding from the pre-release review rounds."""

    def test_dry_run_survives_a_dead_worktree_registration(self):
        """The dry-run branch used to crash on any prunable worktree, aborting the run."""
        _, checkout = self.make_repo("lore-a")
        self.make_repo("lore-b")
        wt = os.path.join(self.tmp, "wt-dead")
        git(checkout, "worktree", "add", "-b", "dead-branch", wt)
        shutil.rmtree(wt)

        report = self.sync("--dry-run")
        entry = self.repo_report(report, "lore-a")
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertIn("would be pruned", retained.get(wt, ""))
        self.assertEqual(entry["worktrees"]["pruned"], [], "a dry run prunes nothing")
        self.assertIn("wt-dead", git_out(checkout, "worktree", "list"))
        # The whole run survived: the other repo still has its own entry.
        self.repo_report(report, "lore-b")

    def test_dry_run_previews_a_worktree_removal(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-clean")
        git(checkout, "worktree", "add", "-b", "clean-branch", wt)

        entry = self.repo_report(self.sync("--dry-run", "--prune-worktrees"), "lore-a")
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertEqual(retained.get(wt), "would be removed")
        self.assertTrue(os.path.isdir(wt))

    def test_one_unsafe_registration_names_itself_not_its_neighbour(self):
        _, checkout = self.make_repo("lore-a")
        safe = os.path.join(self.tmp, "wt-safe")
        unsafe_parent = os.path.join(self.tmp, "volume", "wt-unsafe")
        os.makedirs(os.path.dirname(unsafe_parent))
        git(checkout, "worktree", "add", "-b", "safe-branch", safe)
        git(checkout, "worktree", "add", "-b", "unsafe-branch", unsafe_parent)
        shutil.rmtree(safe)
        shutil.rmtree(os.path.join(self.tmp, "volume"))

        entry = self.repo_report(self.sync(), "lore-a")
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertEqual(entry["worktrees"]["pruned"], [])
        self.assertIn("unmounted", retained[unsafe_parent])
        self.assertIn("another registration", retained[safe],
                      "a safe entry must not be labelled as the unsafe one")

    def test_deleting_a_credential_shaped_file_is_published(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, ".env"), "TOKEN=secret\n")
        git(checkout, "add", "-f", ".env")
        git(checkout, "commit", "-m", "oops")
        git(checkout, "push")
        self.assertIn(".env", git_out(bare, "ls-tree", "-r", "--name-only", "HEAD"))

        os.remove(os.path.join(checkout, ".env"))
        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertIn(".env", entry["committed"])
        self.assertEqual(entry["held"], [])
        self.assertNotIn(".env", git_out(bare, "ls-tree", "-r", "--name-only", "HEAD"),
                         "removing a leaked credential must reach the remote")

    def test_a_path_held_twice_is_reported_once(self):
        _, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, ".env"), "TOKEN=secret\n")
        git(checkout, "add", "-f", ".env")
        git(checkout, "commit", "-m", "oops")
        # `git rm --cached` leaves the same path as both a deletion and untracked.
        git(checkout, "rm", "--cached", ".env")

        entry = self.repo_report(self.sync(), "lore-a")
        paths = [h["path"] for h in entry["held"]]
        self.assertEqual(len(paths), len(set(paths)), paths)

    def test_a_merge_interrupted_before_the_claim_lands_is_still_ours(self):
        """The claim is written before `git merge`, so a kill in between cannot orphan it."""
        _, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "topic.md"), "their version\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        write(os.path.join(checkout, "lore", "topic.md"), "my version\n")

        self.sync()  # conflicts and leaves the merge claimed
        marker = os.path.join(checkout, ".git", ws.MERGE_MARKER)
        self.assertTrue(os.path.exists(marker))
        claim = json.load(open(marker))
        merge_head = open(os.path.join(checkout, ".git", "MERGE_HEAD")).read().strip()
        self.assertEqual(claim["target"], merge_head,
                         "the claim must name the commit git is actually merging")

    def test_a_clean_merge_clears_the_claim(self):
        _, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "theirs.md"), "theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        write(os.path.join(checkout, "lore", "mine.md"), "mine\n")

        self.sync()
        self.assertFalse(os.path.exists(os.path.join(checkout, ".git", ws.MERGE_MARKER)),
                         "a completed merge must not leave a claim behind")

    def test_foreign_merge_refusal_names_commands_that_end_the_state(self):
        _, checkout = self.make_repo("lore-a")
        other = self.other_clone("lore-a")
        write(os.path.join(other, "lore", "theirs.md"), "theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-m", "theirs")
        git(other, "push")
        git(checkout, "fetch", "origin")
        git(checkout, "merge", "--no-commit", "--no-ff", "origin/main")

        entry = self.repo_report(self.sync(), "lore-a")
        self.assertIn("git -C", entry["blocked"])
        self.assertIn("commit", entry["blocked"])
        self.assertIn("merge --abort", entry["blocked"])

    def test_one_repos_failure_does_not_erase_the_runs_report(self):
        infos = [{"name": "boom", "path": "/nonexistent", "kind": "lore"}]

        class Args(object):
            workspace = self.ws
            dry_run = True
            no_push = False
            prune_worktrees = False

        original = ws.sync_repo

        def exploding(info, **kwargs):
            if info["name"] == "boom":
                raise RuntimeError("synthetic failure")
            return original(info, **kwargs)

        self.make_repo("lore-a")
        original_classify = ws.classify_repos
        ws.sync_repo = exploding
        ws.classify_repos = lambda w: original_classify(w) + infos
        try:
            from lr_core.common import Result
            res = Result()
            ws.cmd_workspace_sync(Args(), res)
        finally:
            ws.sync_repo = original
            ws.classify_repos = original_classify

        names = {r["name"]: r for r in res.data["repos"]}
        self.assertIn("lore-a", names, "a healthy repo keeps its entry")
        self.assertEqual(names["boom"]["status"], "blocked")
        self.assertIn("synthetic failure", names["boom"]["blocked"])
        self.assertFalse(res.ok)

    def test_index_lock_is_not_relayed_as_delete_the_lock_file(self):
        raw = ("fatal: Unable to create '/x/.git/index.lock': File exists.\n\n"
               "Another git process seems to be running in this repository...\n"
               "remove the file manually to continue.")
        explained = ws.explain_git_failure(raw, "git add failed")
        self.assertIn("concurrent session", explained)
        self.assertNotIn("remove the file manually", explained)

    def test_pathspec_file_is_written_inside_the_repo(self):
        _, checkout = self.make_repo("lore-a")
        spec = ws._pathspec_file(checkout, ["a", "b"], "commit-paths")
        other = ws._pathspec_file(checkout, ["a"], "add-paths")
        try:
            self.assertTrue(spec.startswith(os.path.realpath(checkout)), spec)
            self.assertEqual(open(spec).read(), "a\0b")
            self.assertNotEqual(spec, other,
                                "two live pathspecs must never share a filename")
            self.assertEqual(open(spec).read(), "a\0b",
                             "writing the second must not disturb the first")
        finally:
            os.remove(spec)
            os.remove(other)

    def test_interrupted_worktree_removal_is_named_as_wreckage(self):
        _, checkout = self.make_repo("lore-a")
        wt = os.path.join(self.tmp, "wt-half")
        git(checkout, "worktree", "add", "-b", "half-branch", wt)
        os.remove(os.path.join(wt, ".git"))  # what a killed `worktree remove` leaves

        entry = self.repo_report(self.sync("--prune-worktrees"), "lore-a")
        retained = {r["path"]: r["reason"] for r in entry["worktrees"]["retained"]}
        self.assertIn("interrupted removal", retained.get(wt, ""))
        self.assertEqual(entry["worktrees"]["pruned"], [],
                         "a directory that still holds files keeps its registration")
        self.assertTrue(os.path.isdir(wt))


class TestRoundTwoRegressions(SyncCase):
    """One test per finding from review round 2."""

    def _workspace_repo(self):
        """The workspace root as its own repo with a remote, as a real workspace has."""
        bare = os.path.join(self.origins, "ws.git")
        subprocess.run(["git", "init", "--bare", "-b", "main", bare],
                       stdout=subprocess.DEVNULL, check=True)
        subprocess.run(["git", "init", "-b", "main", self.ws],
                       stdout=subprocess.DEVNULL, check=True)
        git(self.ws, "config", "user.name", "test")
        git(self.ws, "config", "user.email", "test@example.com")
        write(os.path.join(self.ws, "README.md"), "workspace\n")
        git(self.ws, "add", "-A")
        git(self.ws, "commit", "-m", "seed")
        git(self.ws, "remote", "add", "origin", bare)
        git(self.ws, "push", "-u", "origin", "main")
        return bare

    def test_workspace_root_publishes_only_framework_managed_paths(self):
        bare = self._workspace_repo()
        # A framework-managed path and a personal one, both dirty.
        write(os.path.join(self.ws, ".claude", "commands", "lr-x-agent.md"), "shortcut\n")
        write(os.path.join(self.ws, "my-private-draft.md"), "not for sharing\n")

        report = self.sync()
        entry = self.repo_report(report, os.path.basename(self.ws))

        self.assertIn(".claude/commands/lr-x-agent.md", entry["committed"])
        held = {h["path"]: h["reason"] for h in entry["held"]}
        self.assertIn("my-private-draft.md", held)
        self.assertIn("framework-managed", held["my-private-draft.md"])
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertNotIn("my-private-draft.md", tree,
                         "workspace-push's contract: unmanaged root files are left alone")
        self.assertTrue(os.path.exists(os.path.join(self.ws, "my-private-draft.md")))

    def test_a_repo_whose_worktree_points_elsewhere_is_refused(self):
        _, checkout = self.make_repo("lore-a")
        decoy = os.path.join(self.tmp, "decoy-home")
        os.makedirs(decoy)
        write(os.path.join(decoy, "tax-return.pdf"), "private\n")
        git(checkout, "config", "core.worktree", decoy)

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertFalse(report["ok"])
        self.assertEqual(entry["status"], "blocked")
        self.assertIn("working tree is configured elsewhere", entry["blocked"])
        self.assertEqual(entry["committed"], [])
        bare = os.path.join(self.origins, "lore-a.git")
        self.assertNotIn("tax-return.pdf",
                         git_out(bare, "ls-tree", "-r", "--name-only", "HEAD"))

    def test_a_tracked_submodule_pointer_is_held(self):
        bare, checkout = self.make_repo("lore-a")
        sub_bare, sub_checkout = self.make_repo("subproject", lore=False,
                                                clone_name="subproject-src")
        env = os.environ.copy()
        env.update(GIT_ENV)
        env["GIT_ALLOW_PROTOCOL"] = "file"
        subprocess.run(["git", "-C", checkout, "-c", "protocol.file.allow=always",
                        "submodule", "add", sub_bare, "sub"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        git(checkout, "add", "-A")
        git(checkout, "commit", "-m", "add submodule")
        git(checkout, "push")
        # Move the submodule to a commit that exists nowhere else.
        sub = os.path.join(checkout, "sub")
        write(os.path.join(sub, "local.md"), "never pushed\n")
        git(sub, "add", "-A")
        git(sub, "commit", "-m", "local only")

        entry = self.repo_report(self.sync(), "lore-a")
        held = {h["path"]: h["reason"] for h in entry["held"]}
        self.assertIn("sub", held, entry["held"])
        self.assertIn("nested git repository", held["sub"])
        self.assertNotIn("sub", entry["committed"])

    def test_a_symlink_is_held_rather_than_publishing_its_target(self):
        _, checkout = self.make_repo("lore-a")
        secret = os.path.join(self.tmp, "elsewhere", "private-notes.pem")
        os.makedirs(os.path.dirname(secret))
        write(secret, "KEY\n")
        os.symlink(secret, os.path.join(checkout, "notes-link.md"))

        entry = self.repo_report(self.sync(), "lore-a")
        held = {h["path"]: h["reason"] for h in entry["held"]}
        self.assertIn("notes-link.md", held)
        self.assertIn("symlink", held["notes-link.md"])
        self.assertEqual(entry["committed"], [])


    def test_renaming_away_from_a_secret_name_completes(self):
        """The origin of a rename is a deletion, so the hold must not strand it."""
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "credentials.json"), "{}\n")
        git(checkout, "add", "-f", "credentials.json")
        git(checkout, "commit", "-m", "oops")
        git(checkout, "push")
        git(checkout, "mv", "credentials.json", "config.json")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        self.assertIn("credentials.json", entry["committed"],
                      "the removal must be recorded, not held")
        self.assertIn("config.json", entry["committed"])
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertNotIn("credentials.json", tree)
        self.assertIn("config.json", tree)
        # And the repo is not left permanently dirty by a stranded staged deletion.
        self.assertEqual(git_out(checkout, "status", "--porcelain"), "")


    def test_mixing_staged_and_unstaged_paths_commits_both(self):
        """Two live pathspecs must not share a filename; the staged side gets dropped."""
        bare, checkout = self.make_repo("lore-a")
        # One path already staged by hand (as a hook or a person would leave it)...
        write(os.path.join(checkout, "lore", "staged.md"), "staged by hand\n")
        git(checkout, "add", "lore/staged.md")
        # ...and one with something still unstaged, so both pathspecs are in play.
        write(os.path.join(checkout, "lore", "untracked.md"), "untracked\n")

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("lore/staged.md", tree, "an already-staged path must reach the remote")
        self.assertIn("lore/untracked.md", tree)
        self.assertIn("lore/staged.md", entry["committed"])
        self.assertEqual(git_out(checkout, "status", "--porcelain"), "")

    def test_rename_with_a_further_edit_commits_both_sides(self):
        bare, checkout = self.make_repo("lore-a")
        write(os.path.join(checkout, "credentials.json"), "{}\n")
        git(checkout, "add", "-f", "credentials.json")
        git(checkout, "commit", "-m", "oops")
        git(checkout, "push")
        git(checkout, "mv", "credentials.json", "config.json")
        # Editing the destination after the move mixes a staged deletion with an
        # unstaged modification — the shape that exposed the shared-pathspec bug.
        write(os.path.join(checkout, "config.json"), '{"edited": true}\n')

        report = self.sync()
        entry = self.repo_report(report, "lore-a")

        self.assertTrue(report["ok"], report["errors"])
        tree = git_out(bare, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertNotIn("credentials.json", tree,
                         "the credential must actually leave the remote")
        self.assertIn("config.json", tree)
        self.assertIn("edited", git_out(bare, "show", "HEAD:config.json"))
        self.assertEqual(git_out(checkout, "status", "--porcelain"), "")

    def test_our_own_timeout_is_not_reported_as_someone_elses_lock(self):
        timed_out = ws.explain_git_failure("timed out after 120s", "git commit failed")
        self.assertIn("did not finish in time", timed_out)
        self.assertNotIn("concurrent session", timed_out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
