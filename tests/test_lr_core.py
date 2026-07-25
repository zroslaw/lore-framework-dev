#!/usr/bin/env python3
"""Tests for lr-core (lore-framework/scripts/lr-core).

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only
(unittest), matching test_lrb.py. The plugin under test is located via
$LR_FRAMEWORK_DIR, defaulting to the sibling ../lore-framework.

Everything runs in per-test tempdirs with local-only git remotes — no network,
nothing touching the real workspace.

Run:  python3 tests/test_lr_core.py -v
  or: python3 -m unittest discover -s tests -v
"""
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
LR_CORE = os.path.join(FRAMEWORK_DIR, "scripts", "lr-core")

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def git(repo, *args):
    env = os.environ.copy()
    env.update(GIT_ENV)
    return subprocess.run(
        ["git", "-C", repo] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def run_core(*args):
    """Invoke lr-core; return (exit_code, parsed_json_or_None, raw_stdout)."""
    proc = subprocess.run(
        [sys.executable, LR_CORE] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    raw = proc.stdout.decode()
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = None
    return proc.returncode, parsed, raw


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(textwrap.dedent(content).lstrip("\n"))


def make_repo(workspace, name, version="30", agents=("alpha",), description="Test repo"):
    """A lore agent repo with descriptor + agents, not yet a git repo."""
    repo = os.path.join(workspace, name)
    write(os.path.join(repo, "lore-repo.md"), """
        ---
        description: %s
        version: "%s"
        ---

        # %s
        """ % (description, version, name))
    for agent in agents:
        agent_dir = os.path.join(repo, "agents", agent)
        write(os.path.join(agent_dir, "role.md"), """
            ---
            description: The %s agent
            ---

            # %s
            """ % (agent, agent))
        write(os.path.join(agent_dir, "lore-context.md"), "# Lore Context\n")
        write(os.path.join(agent_dir, "lore", "first-topic.md"),
              "# First topic\n\nBody.\n")
        write(os.path.join(agent_dir, "lore", "second-topic.md"),
              "Second topic without a heading\n")
    return repo


def git_init(repo, with_origin=True):
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "initial")
    if not with_origin:
        return None
    origin = repo + "-origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
    git(repo, "remote", "add", "origin", origin)
    git(repo, "push", "-q", "-u", "origin", "main")
    return origin


class LrCoreTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-core-test-")
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)
        # A stand-in framework root so version comparison is deterministic.
        self.fw = os.path.join(self.tmp, "framework")
        os.makedirs(self.fw)
        write(os.path.join(self.fw, "VERSION"), "30\n")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def core(self, *args):
        return run_core("--framework-root", self.fw, *args)


class TestDiscover(LrCoreTestBase):
    def test_finds_repos_and_agents(self):
        make_repo(self.workspace, "repo-one", agents=("alpha", "beta"))
        make_repo(self.workspace, "repo-two", agents=("gamma",))
        rc, out, _ = self.core("discover", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(len(out["data"]["repos"]), 2)
        names = sorted(a["name"] for a in out["data"]["agents"])
        self.assertEqual(names, ["alpha", "beta", "gamma"])

    def test_parses_descriptor_frontmatter(self):
        repo = make_repo(self.workspace, "repo-one", version="28",
                         description="Quoted: description")
        write(os.path.join(repo, "lore-repo.md"), """
            ---
            description: "A quoted description"
            version: "28"
            repos:
              - git@github.com:example/one.git
              - git@github.com:example/two.git
            ---
            """)
        rc, out, _ = self.core("discover", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        repo_info = out["data"]["repos"][0]
        self.assertEqual(repo_info["description"], "A quoted description")
        self.assertEqual(repo_info["version"], "28")
        self.assertEqual(len(repo_info["repos"]), 2)

    def test_skips_hidden_and_nested_dirs(self):
        make_repo(self.workspace, "repo-one")
        # Hidden dir (the .worktrees convention lives here) — must be invisible.
        make_repo(self.workspace, ".worktrees")
        # Nested repo — discovery is top-level only by design.
        make_repo(os.path.join(self.workspace, "repo-one"), "nested")
        rc, out, _ = self.core("discover", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual([r["name"] for r in out["data"]["repos"]], ["repo-one"])

    def test_empty_workspace_is_ok_false_not_an_exception(self):
        rc, out, _ = self.core("discover", "--workspace", self.workspace)
        self.assertEqual(rc, 0, "an empty workspace is a result, not a script failure")
        self.assertFalse(out["ok"])
        self.assertTrue(out["errors"])

    def test_missing_workspace(self):
        rc, out, _ = self.core("discover", "--workspace",
                               os.path.join(self.tmp, "nope"))
        self.assertEqual(rc, 0)
        self.assertFalse(out["ok"])


class TestPreflight(LrCoreTestBase):
    def test_resolves_agent_and_lists_files_to_read(self):
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["agent"]["name"], "alpha")
        self.assertEqual(out["data"]["agent"]["description"], "The alpha agent")
        self.assertEqual(len(out["data"]["read_next"]), 2)
        for path in out["data"]["read_next"]:
            self.assertTrue(os.path.isfile(path))

    def test_agent_not_found_returns_available_agents(self):
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("preflight", "--agent", "nope",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(rc, 0, "a missing agent is a determinate answer, not a crash")
        self.assertFalse(out["ok"])
        self.assertEqual([a["name"] for a in out["data"]["available_agents"]], ["alpha"])

    def test_agent_dir_bypasses_discovery(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        agent_dir = os.path.join(repo, "agents", "alpha")
        rc, out, _ = self.core("preflight", "--agent-dir", agent_dir, "--no-pull")
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["agent"]["repo"], repo)

    def test_agent_dir_without_role_md(self):
        rc, out, _ = self.core("preflight", "--agent-dir", self.workspace, "--no-pull")
        self.assertEqual(rc, 0)
        self.assertFalse(out["ok"])

    def test_version_verdicts(self):
        make_repo(self.workspace, "match-repo", version="30", agents=("a-match",))
        make_repo(self.workspace, "behind-repo", version="27", agents=("a-behind",))
        make_repo(self.workspace, "ahead-repo", version="99", agents=("a-ahead",))
        for agent, verdict in (("a-match", "match"), ("a-behind", "repo-behind"),
                               ("a-ahead", "repo-ahead")):
            rc, out, _ = self.core("preflight", "--agent", agent,
                                   "--workspace", self.workspace, "--no-pull")
            self.assertEqual(rc, 0)
            self.assertEqual(out["data"]["version"]["verdict"], verdict, agent)

    def test_missing_version_stamp_is_unknown_not_fatal(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        write(os.path.join(repo, "lore-repo.md"), "# no frontmatter here\n")
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["version"]["verdict"], "unknown")

    def test_missing_lore_context_warns_but_succeeds(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        os.remove(os.path.join(repo, "agents", "alpha", "lore-context.md"))
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(len(out["data"]["read_next"]), 1)
        self.assertTrue(out["warnings"])

    def test_teammate_verdict_is_always_one_of_three(self):
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertIn(out["data"]["teammate"]["verdict"], ("yes", "no", "unknown"))

    def test_teammate_check_can_be_suppressed(self):
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull",
                               "--no-teammate-check")
        self.assertEqual(out["data"]["teammate"]["verdict"], "unknown")

    def test_requires_agent_or_agent_dir(self):
        rc, out, _ = self.core("preflight", "--workspace", self.workspace)
        self.assertEqual(rc, 2, "unusable invocation must trigger the fallback contract")
        self.assertFalse(out["ok"])


class TestPreflightPull(LrCoreTestBase):
    def test_non_git_repo_is_skipped_not_failed(self):
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["pull"]["status"], "skipped")
        self.assertIn("not a git repo", out["data"]["pull"]["detail"])

    def test_git_repo_without_origin_is_skipped(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo, with_origin=False)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["pull"]["status"], "skipped")
        self.assertIn("no origin", out["data"]["pull"]["detail"])

    def test_pull_up_to_date_then_ttl_cached(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(out["data"]["pull"]["status"], "up-to-date")
        # Second call within the TTL window must not touch the network.
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(out["data"]["pull"]["status"], "fresh")

    def test_fresh_flag_bypasses_ttl(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo)
        self.core("preflight", "--agent", "alpha", "--workspace", self.workspace)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--fresh")
        self.assertEqual(out["data"]["pull"]["status"], "up-to-date")

    def test_ttl_zero_disables_cache(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo)
        self.core("preflight", "--agent", "alpha", "--workspace", self.workspace)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--ttl", "0")
        self.assertEqual(out["data"]["pull"]["status"], "up-to-date")

    def test_pull_fast_forwards_and_counts_commits(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        origin = git_init(repo)
        # A second clone pushes a commit; our repo must fast-forward to it.
        other = os.path.join(self.tmp, "other")
        subprocess.run(["git", "clone", "-q", origin, other], check=True)
        write(os.path.join(other, "new-file.md"), "# new\n")
        git(other, "add", "-A")
        git(other, "commit", "-qm", "second")
        git(other, "push", "-q")

        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(out["data"]["pull"]["status"], "pulled")
        self.assertEqual(out["data"]["pull"].get("commits"), 1)
        self.assertTrue(os.path.isfile(os.path.join(repo, "new-file.md")))

    def test_diverged_branch_fails_without_aborting(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        origin = git_init(repo)
        other = os.path.join(self.tmp, "other")
        subprocess.run(["git", "clone", "-q", origin, other], check=True)
        write(os.path.join(other, "theirs.md"), "# theirs\n")
        git(other, "add", "-A")
        git(other, "commit", "-qm", "theirs")
        git(other, "push", "-q")
        # Local commit that is not an ancestor of origin/main -> non-fast-forward.
        write(os.path.join(repo, "mine.md"), "# mine\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "mine")

        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(rc, 0, "a failed pull is degraded mode, not a script failure")
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["pull"]["status"], "failed")
        self.assertTrue(out["warnings"])
        # The agent is still fully resolved — boot can continue.
        self.assertEqual(out["data"]["agent"]["name"], "alpha")

    def test_bare_repo_is_skipped_with_its_own_reason(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        subprocess.run(["git", "init", "-q", "--bare", os.path.join(repo, ".git")],
                       check=True)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["pull"]["status"], "skipped")
        self.assertIn("bare", out["data"]["pull"]["detail"])

    def test_missing_git_binary_is_failed_not_skipped(self):
        """A broken toolchain must not masquerade as 'not a git repo'.

        Reporting it as a skip would let exit 0 carry a silently wrong answer,
        which is exactly what the output contract promises never happens.
        """
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo)
        empty_bin = os.path.join(self.tmp, "empty-bin")
        os.makedirs(empty_bin)
        env = os.environ.copy()
        env["PATH"] = empty_bin
        proc = subprocess.run(
            [sys.executable, LR_CORE, "--framework-root", self.fw, "preflight",
             "--agent", "alpha", "--workspace", self.workspace],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
        out = json.loads(proc.stdout.decode())
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out["data"]["pull"]["status"], "failed")
        self.assertTrue(out["warnings"], "a broken toolchain must be surfaced")

    def test_no_pull_flag(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(out["data"]["pull"]["status"], "disabled")

    def test_stamp_lives_inside_the_git_dir(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo)
        self.core("preflight", "--agent", "alpha", "--workspace", self.workspace)
        self.assertTrue(os.path.isfile(os.path.join(repo, ".git", "lr-last-pull")))
        status = git(repo, "status", "--porcelain").stdout.decode()
        self.assertEqual(status.strip(), "", "the stamp must not dirty the working tree")


class TestScan(LrCoreTestBase):
    def test_lists_topics_with_titles(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["count"], 2)
        by_file = {t["file"]: t for t in out["data"]["topics"]}
        self.assertEqual(by_file["first-topic.md"]["title"], "First topic")
        self.assertEqual(by_file["second-topic.md"]["title"],
                         "Second topic without a heading")

    def test_git_dates_and_staleness(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo, with_origin=False)
        rc, out, _ = self.core("scan", "--agent", "alpha",
                               "--workspace", self.workspace, "--stale-days", "180")
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["undated_count"], 0)
        for topic in out["data"]["topics"]:
            self.assertIsNotNone(topic["last_modified"])
            self.assertIsNotNone(topic["age_days"])
            self.assertFalse(topic["stale"])
        # A zero-day threshold makes every just-committed topic stale.
        rc, out, _ = self.core("scan", "--agent", "alpha",
                               "--workspace", self.workspace, "--stale-days", "-1")
        self.assertEqual(out["data"]["stale_count"], 2)

    def test_untracked_topics_are_undated_not_errors(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo, with_origin=False)
        write(os.path.join(repo, "agents", "alpha", "lore", "brand-new.md"),
              "# Brand new\n")
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["undated_count"], 1)
        self.assertTrue(out["warnings"])

    def test_missing_lore_dir(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        subprocess.run(["rm", "-rf", os.path.join(repo, "agents", "alpha", "lore")],
                       check=True)
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertFalse(out["ok"])

    def test_directory_named_like_a_topic_is_skipped(self):
        """A directory called `something.md` is not a topic.

        Without the isfile guard it survives as a title-less row with the
        directory's inode size — garbage that reads as plausible data.
        """
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        os.makedirs(os.path.join(repo, "agents", "alpha", "lore", "weird-dir.md"))
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["count"], 2)
        self.assertNotIn("weird-dir.md", [t["file"] for t in out["data"]["topics"]])

    def test_non_md_files_ignored(self):
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        write(os.path.join(repo, "agents", "alpha", "lore", "notes.txt"), "ignore me")
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(out["data"]["count"], 2)


class TestTeammateMarkerMatching(unittest.TestCase):
    """The marker must match as a flag, not as a substring.

    `--agent-idle-timeout=30` in some unrelated ancestor process must not read
    as the Agent-Teams marker and silently switch the session into teammate mode.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_loader(
            "lr_core", importlib.machinery.SourceFileLoader("lr_core", LR_CORE))
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_matches_real_marker(self):
        for args in (
            "claude --agent-id abc123 --parent-session-id xyz",
            "claude --agent-id=abc123",
            "--agent-id abc",
        ):
            self.assertTrue(self.mod.TEAMMATE_MARKER_RE.search(args), args)

    def test_rejects_longer_flags_and_substrings(self):
        for args in (
            "some-tool --agent-idle-timeout=30",
            "some-tool --agent-identity foo",
            "claude --no--agent-idx",
        ):
            self.assertFalse(self.mod.TEAMMATE_MARKER_RE.search(args), args)


class TestOutputContract(LrCoreTestBase):
    def test_every_subcommand_emits_the_four_keys(self):
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        invocations = [
            ("discover", "--workspace", self.workspace),
            ("preflight", "--agent", "alpha", "--workspace", self.workspace, "--no-pull"),
            ("scan", "--agent", "alpha", "--workspace", self.workspace),
        ]
        for args in invocations:
            rc, out, raw = self.core(*args)
            self.assertIsNotNone(out, "non-JSON output from %s: %r" % (args[0], raw))
            for key in ("ok", "data", "warnings", "errors"):
                self.assertIn(key, out, args[0])
            self.assertIsInstance(out["warnings"], list)
            self.assertIsInstance(out["errors"], list)

    def test_no_subcommand_exits_2(self):
        rc, _, _ = self.core()
        self.assertEqual(rc, 2)

    def test_usage_errors_still_emit_json(self):
        """Even argparse-level failures honor the one-JSON-object contract."""
        for args in (("bogus",), ("preflight", "--agent", "a", "--ttl", "not-a-number")):
            rc, out, raw = self.core(*args)
            self.assertEqual(rc, 2, args)
            self.assertIsNotNone(out, "no JSON on stdout for %s: %r" % (args, raw))
            self.assertFalse(out["ok"])
            self.assertTrue(out["errors"])

    def test_missing_version_file_warns_but_completes(self):
        os.remove(os.path.join(self.fw, "VERSION"))
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["data"]["version"]["verdict"], "unknown")
        self.assertTrue(out["warnings"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
