#!/usr/bin/env python3
"""Tests for lr-core (lore-framework/scripts/lr-core).

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only
(unittest), matching test_lrb.py. The plugin under test is located via
$LR_FRAMEWORK_DIR, defaulting to the sibling ../lore-framework. That default is
wrong under the worktree convention (docs/worktrees.md) — set the variable
explicitly there, or every subprocess fails to find scripts/lr-core and the
suite reports bare "AssertionError: 2 != 0" instead of the real cause.

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


def load_lr_core():
    """Import lr-core as a module — it has no .py suffix, so load it by path."""
    spec = importlib.util.spec_from_loader(
        "lr_core_entry",
        importlib.machinery.SourceFileLoader("lr_core_entry", LR_CORE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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

    def test_skew_is_reported_through_data_only_never_as_a_warning(self):
        """version-check.md owns the user-facing skew message; preflight owns the data.

        The Codex repo-ahead lifecycle scenario printed the script's
        `version skew: repo=32 framework=31 (repo-ahead)` line verbatim and
        stopped, never reaching version-check.md's engine-specific plugin-refresh
        remedy — agent-boot.md tells the caller to surface warnings one line each,
        so a warning that reads like a finished message gets treated as one.
        A skew must leave `warnings` empty; the verdict alone routes the caller.
        """
        for version, verdict in (("99", "repo-ahead"), ("27", "repo-behind"),
                                 ("v2", "differs")):
            repo = make_repo(self.workspace, f"skew-{verdict}-{version}",
                             version=version, agents=(f"agent-{version}",))
            self.assertTrue(os.path.isdir(repo))
            rc, out, _ = self.core("preflight", "--agent", f"agent-{version}",
                                   "--workspace", self.workspace, "--no-pull")
            self.assertEqual(out["data"]["version"]["verdict"], verdict, version)
            self.assertEqual(
                [w for w in out["warnings"] if "skew" in w.lower()], [],
                f"{verdict} must not emit a skew warning: {out['warnings']}",
            )

    def test_unknown_version_still_warns(self):
        """The counterpart: `unknown` is not a skew and keeps its warning.

        Silence there would read as "versions agree" — a different and unearned
        claim — and that message deliberately does not point at version-check.md.
        """
        repo = make_repo(self.workspace, "no-stamp", agents=("beta",))
        write(os.path.join(repo, "lore-repo.md"), "no frontmatter here\n")
        rc, out, _ = self.core("preflight", "--agent", "beta",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(out["data"]["version"]["verdict"], "unknown")
        self.assertTrue(
            [w for w in out["warnings"] if "version stamp" in w],
            f"unknown must still warn: {out['warnings']}",
        )

    def test_int_equal_versions_spelled_differently_are_a_match(self):
        """`031` and `31` are the same version.

        Without an equality check after the int parse this lands in the
        `repo-ahead` branch, and version-check.md's R > F path tells the user to
        go reinstall a plugin that is already correct.
        """
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        write(os.path.join(repo, "lore-repo.md"), """
            ---
            description: T
            version: "030"
            ---
            """)
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(out["data"]["version"]["verdict"], "match")
        self.assertFalse([w for w in out["warnings"] if "skew" in w])

    def test_bom_does_not_silently_void_the_frontmatter(self):
        """A UTF-8 BOM used to make `lines[0] == "---"` fail, voiding every field.

        The result was `verdict: unknown` with no warning at all — silence that
        reads as "versions agree".
        """
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        with open(os.path.join(repo, "lore-repo.md"), "wb") as fh:
            fh.write(b'\xef\xbb\xbf---\ndescription: T\nversion: "30"\n---\n')
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(out["data"]["version"]["verdict"], "match")

    def test_unknown_version_verdict_is_warned_about(self):
        """`unknown` means "could not read a stamp" — staying silent implies agreement."""
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        write(os.path.join(repo, "lore-repo.md"), "# no frontmatter here\n")
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace, "--no-pull")
        self.assertEqual(out["data"]["version"]["verdict"], "unknown")
        self.assertTrue([w for w in out["warnings"] if "version" in w.lower()],
                        "an unreadable version stamp must be surfaced")

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


class TestGitUnrunnableAtEveryCallSite(unittest.TestCase):
    """A git that cannot *run* is "failed" at every call site, not just the first.

    `test_missing_git_binary_is_failed_not_skipped` empties PATH, so it aborts at
    the very first git call (`rev-parse`) and never reaches the second one. But a
    toolchain can also break *between* calls — a per-call timeout on a flaky
    network mount is the realistic case — and collapsing that into "no origin
    remote" would let a broken toolchain masquerade as a legitimate skip while
    exit 0 promises the data is authoritative.

    These drive `pull_repo` directly with a stubbed `git`, because the distinction
    under test is which of two rc values a call site branches on; a subprocess
    cannot be made to fail at one call site and succeed at another without
    contortions that test the contortion rather than the branch.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = load_lr_core()

    def _pull_with_stub(self, remote_result, repo="/tmp"):
        """Run the real pull_repo with every git call before `remote get-url` OK."""
        calls = []

        def fake_git(repo_arg, args, timeout=None, env_extra=None):
            calls.append(list(args))
            if args[:2] == ["rev-parse", "--is-inside-work-tree"]:
                return (0, "true\n", "")
            if args[:2] == ["rev-parse", "--show-toplevel"]:
                # Report this path as its own git root so the guard passes and
                # execution reaches the call actually under test.
                return (0, os.path.realpath(repo) + "\n", "")
            if args[:2] == ["remote", "get-url"]:
                return remote_result
            raise AssertionError("pull_repo should have stopped by now: %r" % (args,))

        original = self.mod.preflight.git
        self.mod.preflight.git = fake_git
        try:
            result = self.mod.pull_repo(repo, ttl=0)
        finally:
            self.mod.preflight.git = original
        return result, calls

    def test_unrunnable_remote_get_url_is_failed_not_no_origin(self):
        result, calls = self._pull_with_stub(
            (self.mod.GIT_UNRUNNABLE, "", "timed out after 15s"))
        self.assertEqual(result["status"], "failed")
        self.assertIn("could not run git", result["detail"])
        self.assertNotIn("no origin", result["detail"])
        self.assertEqual([" ".join(c[:2]) for c in calls],
                         ["rev-parse --is-inside-work-tree",
                          "rev-parse --show-toplevel",
                          "remote get-url"],
                         "must stop at the failed call, not press on to the pull")

    def test_signal_killed_git_is_failed_not_skipped(self):
        """A negative rc is a signal death, not an answer — and not `-1` alone.

        The unrunnable sentinel used to be the integer -1, which is also how
        `subprocess` reports death by SIGHUP; every other signal (SIGKILL -> -9)
        fell through to the `rc != 0` branch and became "not a git repo".
        """
        for signum in (1, 9, 11):
            calls = []

            def fake_git(repo_arg, args, timeout=None, env_extra=None):
                calls.append(list(args))
                return (-signum, "", "")

            original = self.mod.preflight.git
            self.mod.preflight.git = fake_git
            try:
                result = self.mod.pull_repo("/tmp", ttl=0)
            finally:
                self.mod.preflight.git = original
            self.assertEqual(result["status"], "failed", "signal %d" % signum)
            self.assertIn("killed by signal %d" % signum, result["detail"])

    def test_git_ran_and_said_no_origin_is_still_skipped(self):
        """The other side of the same distinction — this one really is a skip."""
        result, _ = self._pull_with_stub((2, "", "error: No such remote 'origin'"))
        self.assertEqual(result["status"], "skipped")
        self.assertIn("no origin remote", result["detail"])

    def test_rev_parse_failing_for_a_non_repo_reason_is_not_called_a_non_repo(self):
        """Only git's own "not a git repository" wording establishes a non-repo.

        A `git` wrapper that exits non-zero for its own reasons (a version
        manager with no git installed for this directory) otherwise becomes a
        silent `skipped — not a git repo`, which boot is documented to print
        nothing about at all.
        """
        def fake_git(repo_arg, args, timeout=None, env_extra=None):
            return (1, "", "mise: git is not installed for this directory")

        original = self.mod.preflight.git
        self.mod.preflight.git = fake_git
        try:
            result = self.mod.pull_repo("/tmp", ttl=0)
        finally:
            self.mod.preflight.git = original
        self.assertEqual(result["status"], "failed")
        self.assertIn("mise", result["detail"])

    def test_pull_failure_detail_names_the_cause_not_the_hint(self):
        """git prints the cause first and an indented hint block after it.

        Taking the last line yields a fragment of the suggested remedy and
        discards the reason — and both triggering states (detached HEAD, no
        upstream) are ordinary in the framework's own worktree convention.
        """
        stderr = (
            "fatal: You are not currently on a branch.\n"
            "To pull the remote branch, use:\n"
            "\n"
            "    git pull <remote> <branch>\n"
        )

        def fake_git(repo_arg, args, timeout=None, env_extra=None):
            if args[:2] == ["rev-parse", "--is-inside-work-tree"]:
                return (0, "true\n", "")
            if args[:2] == ["rev-parse", "--show-toplevel"]:
                return (0, os.path.realpath("/tmp") + "\n", "")
            if args[:2] == ["remote", "get-url"]:
                return (0, "git@example.com:x/y.git\n", "")
            if args[0] == "pull":
                return (1, "", stderr)
            return (0, "", "")

        original = self.mod.preflight.git
        self.mod.preflight.git = fake_git
        try:
            result = self.mod.pull_repo("/tmp", ttl=0)
        finally:
            self.mod.preflight.git = original
        self.assertEqual(result["status"], "failed")
        self.assertIn("not currently on a branch", result["detail"])
        self.assertNotIn("git pull <remote>", result["detail"])


class TestNestedLoreRepo(LrCoreTestBase):
    """A lore repo that is a plain directory inside someone else's git repo.

    `git -C <dir>` silently walks UP to the enclosing repository, so without an
    explicit root check every git operation retargets at the outer repo while
    the output still names the lore repo — a mutating pull attributed to a path
    it never touched, under exit 0.
    """

    def setUp(self):
        super(TestNestedLoreRepo, self).setUp()
        self.repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        # The WORKSPACE is the git repo; repo-one is just a directory in it.
        git_init(self.workspace, with_origin=False)

    def test_pull_refuses_rather_than_acting_on_the_enclosing_repo(self):
        before = git(self.workspace, "rev-parse", "HEAD").stdout
        rc, out, _ = self.core("preflight", "--agent", "alpha",
                               "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["pull"]["status"], "skipped")
        self.assertIn("not the root of its own git repo", out["data"]["pull"]["detail"])
        self.assertEqual(git(self.workspace, "rev-parse", "HEAD").stdout, before,
                         "the enclosing repo must not be touched")
        self.assertFalse(os.path.isfile(
            os.path.join(self.workspace, ".git", "lr-last-pull")),
            "the TTL stamp must not land on the enclosing repo either")

    def test_scan_still_reads_dates_via_the_real_git_toplevel(self):
        """scan is read-only, so it resolves against the toplevel rather than refusing."""
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        self.assertEqual(out["data"]["undated_count"], 0,
                         "committed topics must not read as untracked")
        for topic in out["data"]["topics"]:
            self.assertIsNotNone(topic["last_modified"])


class TestScan(LrCoreTestBase):
    def test_non_ascii_topic_filenames_get_dates(self):
        """git C-quotes non-ASCII paths in --name-only unless quotepath is off.

        The quoted key never matches the raw filename, so the topic reads as
        never committed and is permanently exempt from the staleness flag that
        recall acts on. LC_ALL=C does not affect quotepath.
        """
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        write(os.path.join(repo, "agents", "alpha", "lore", "café-naïve.md"),
              "# Café naïve\n")
        git_init(repo, with_origin=False)
        rc, out, _ = self.core("scan", "--agent", "alpha", "--workspace", self.workspace)
        self.assertEqual(rc, 0)
        by_file = {t["file"]: t for t in out["data"]["topics"]}
        self.assertIn("café-naïve.md", by_file)
        self.assertIsNotNone(by_file["café-naïve.md"]["last_modified"],
                             "a committed non-ASCII topic must not read as undated")
        self.assertEqual(out["data"]["undated_count"], 0)

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

    def test_unreadable_git_history_is_not_reported_as_untracked(self):
        """Committed topics must never be described as "uncommitted or untracked".

        Every topic here IS committed; only git is unavailable. "No dates could
        be read" and "these files were never committed" are different claims, and
        emitting the second one turns a broken toolchain into a confident wrong
        explanation that a caller would act on (e.g. by "fixing" it with a commit).
        """
        repo = make_repo(self.workspace, "repo-one", agents=("alpha",))
        git_init(repo, with_origin=False)
        empty_bin = os.path.join(self.tmp, "empty-bin")
        os.makedirs(empty_bin)
        env = os.environ.copy()
        env["PATH"] = empty_bin
        proc = subprocess.run(
            [sys.executable, LR_CORE, "--framework-root", self.fw, "scan",
             "--agent", "alpha", "--workspace", self.workspace],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
        out = json.loads(proc.stdout.decode())
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(out["ok"], "an unreadable history still yields a usable manifest")
        self.assertTrue(out["data"]["git_error"],
                        "the git failure must be recorded in data, not only in prose")
        # The topics are still listed — only their dates are unavailable.
        self.assertEqual(out["data"]["count"], 2)
        warnings = " ".join(out["warnings"])
        self.assertIn("could not read git history", warnings)
        self.assertNotIn("uncommitted or untracked", warnings)

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
        cls.mod = load_lr_core()

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


class TestEngineDetection(unittest.TestCase):
    """The engine profile decides invocation syntax, subagent mechanism, memory
    file, and runtime bounding for the whole session. It must be decided by
    observation, never by what the running model believes it is.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = load_lr_core()

    def test_program_name_identifies_the_engine(self):
        for args, expected in (
            ("claude --dangerously-skip-permissions", "claude"),
            ("/usr/local/bin/claude", "claude"),
            ("codex exec --sandbox danger-full-access", "codex"),
            ("cursor-agent --plugin-dir ./lore-framework", "cursor"),
            # Engine shipped as a script: the program is the interpreter.
            ("/opt/homebrew/bin/node /opt/homebrew/bin/claude --print", "claude"),
        ):
            self.assertEqual(self.mod._engine_from_args(args), expected, args)

    def test_engine_name_inside_a_path_is_not_a_signal(self):
        """A path mentioning an engine is not evidence that engine is running."""
        for args in (
            # The shell Claude Code runs its own Bash tool through.
            "/bin/zsh -c source /Users/x/.claude/shell-snapshots/snapshot-zsh-1.sh",
            "/bin/zsh -c cd ~/.codex && ls",
            # Another engine running inside Cursor's integrated terminal has the
            # Cursor *application* in its ancestry; only `cursor-agent` counts.
            "/Applications/Cursor.app/Contents/MacOS/Cursor",
            "-zsh",
            "login -fp someone",
            "",
        ):
            self.assertIsNone(self.mod._engine_from_args(args), args)

    def test_signal_precedence_and_default(self):
        mod = self.mod
        root = FRAMEWORK_DIR
        saved_walk = mod.preflight._walk_ancestors
        saved_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        try:
            # An explicit override outranks everything.
            self.assertEqual(
                mod.detect_engine(root, override="codex")["name"], "codex")

            mod.preflight._walk_ancestors = lambda: iter(())
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)

            # Containment: the tree lives inside an engine's plugin store.
            for home, expected in mod.ENGINE_HOME_DIRS:
                installed = os.path.join(
                    os.path.expanduser(home), "plugins", "cache", "lr", "1")
                result = mod.detect_engine(installed)
                self.assertEqual(
                    (result["name"], result["signal"]), (expected, "containment"))

            # No signal at all: the reference profile, explicitly marked assumed.
            result = mod.detect_engine("/nowhere/lore-framework")
            self.assertEqual(result["name"], mod.DEFAULT_ENGINE)
            self.assertEqual(result["signal"], "default")
            self.assertEqual(result["confidence"], "assumed")

            # Ancestry beats containment: a Claude Code session may be launched
            # with --plugin-dir against a checkout inside another engine's store.
            mod.preflight._walk_ancestors = lambda: iter([(42, "claude --print")])
            inside_codex = os.path.join(
                os.path.expanduser("~/.codex"), "plugins", "cache", "lr", "1")
            result = mod.detect_engine(inside_codex)
            self.assertEqual((result["name"], result["signal"]),
                             ("claude", "ancestry"))

            # The env var is checked before ancestry.
            os.environ["CLAUDE_PLUGIN_ROOT"] = "/some/plugin/root"
            mod.preflight._walk_ancestors = lambda: iter([(42, "codex exec")])
            self.assertEqual(mod.detect_engine(root)["signal"], "env")
        finally:
            mod.preflight._walk_ancestors = saved_walk
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            if saved_env is not None:
                os.environ["CLAUDE_PLUGIN_ROOT"] = saved_env

    def test_another_engine_being_installed_is_never_a_signal(self):
        """The regression this replaced.

        The prose ladder had a rung reading "else if a ~/.codex/ directory
        exists -> codex". That fires on any workstation with Codex installed,
        for every session, whatever is actually running — it routed real Claude
        Code sessions to the codex profile.
        """
        mod = self.mod
        saved_walk = mod.preflight._walk_ancestors
        saved_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        try:
            mod.preflight._walk_ancestors = lambda: iter(())
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            with tempfile.TemporaryDirectory() as home:
                # Every engine's home dir exists; the framework is in none of them.
                for name in (".codex", ".cursor", ".claude"):
                    os.makedirs(os.path.join(home, name))
                real_home = os.environ.get("HOME")
                os.environ["HOME"] = home
                try:
                    result = mod.detect_engine(
                        os.path.join(home, "checkouts", "lore-framework"))
                finally:
                    if real_home is not None:
                        os.environ["HOME"] = real_home
            self.assertEqual(result["signal"], "default")
            self.assertEqual(result["confidence"], "assumed")
        finally:
            mod.preflight._walk_ancestors = saved_walk
            if saved_env is not None:
                os.environ["CLAUDE_PLUGIN_ROOT"] = saved_env

    def test_containment_sees_through_a_symlinked_plugin_dir(self):
        """Cursor's local plugin surface is a symlink to an arbitrary checkout.

        Resolving the root before comparing lands outside ~/.cursor and misses
        exactly the layout this signal is named for. Resolving neither side
        reintroduces the /var -> /private/var trap, so both forms have to count.
        """
        mod = self.mod
        saved_walk = mod.preflight._walk_ancestors
        saved_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        with tempfile.TemporaryDirectory() as tmp:
            home = os.path.join(tmp, "home")
            checkout = os.path.join(tmp, "checkouts", "lore-framework")
            local = os.path.join(home, ".cursor", "plugins", "local")
            os.makedirs(checkout)
            os.makedirs(local)
            link = os.path.join(local, "lore-framework")
            os.symlink(checkout, link)
            real_home = os.environ.get("HOME")
            try:
                mod.preflight._walk_ancestors = lambda: iter(())
                os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
                os.environ["HOME"] = home
                through_link = mod.detect_engine(link)
                # The same tree reached by its real path is NOT under ~/.cursor,
                # and must not be claimed by containment.
                direct = mod.detect_engine(checkout)
            finally:
                mod.preflight._walk_ancestors = saved_walk
                if real_home is not None:
                    os.environ["HOME"] = real_home
                if saved_env is not None:
                    os.environ["CLAUDE_PLUGIN_ROOT"] = saved_env

        self.assertEqual((through_link["name"], through_link["signal"]),
                         ("cursor", "containment"))
        self.assertEqual(direct["signal"], "default")

    def test_no_signal_distinguishes_blocked_ps_from_empty_ancestry(self):
        """The two ways of reaching the default need different remedies.

        Codex blocks `ps` and installs under ~/.codex; a Codex session against a
        worktree or dev checkout therefore matches no rung at all and lands on
        the claude profile. That case has to be legible in the detail string —
        it is the one the removed "~/.codex exists" rung used to catch by
        accident.
        """
        mod = self.mod
        saved_walk = mod.preflight._walk_ancestors
        saved_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        try:
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)

            mod.preflight._walk_ancestors = lambda: iter(())
            blocked = mod.detect_engine("/nowhere/lore-framework")

            mod.preflight._walk_ancestors = lambda: iter([(7, "/bin/zsh -c true")])
            readable = mod.detect_engine("/nowhere/lore-framework")
        finally:
            mod.preflight._walk_ancestors = saved_walk
            if saved_env is not None:
                os.environ["CLAUDE_PLUGIN_ROOT"] = saved_env

        for result in (blocked, readable):
            self.assertEqual(result["confidence"], "assumed")
        self.assertIn("ps could not be read", blocked["detail"])
        self.assertNotIn("ps could not be read", readable["detail"])
        self.assertIn("readable ancestor", readable["detail"])

    def test_assumed_engine_is_warned_with_the_override_flag(self):
        """A silent wrong profile is the failure mode; the warning must name the fix.

        Driven through cmd_preflight with the signals stubbed out rather than as
        a subprocess: the test host is itself a real engine, so a subprocess run
        would detect that engine and never reach the branch under test.
        """
        mod = self.mod
        saved_walk = mod.preflight._walk_ancestors
        saved_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        try:
            mod.preflight._walk_ancestors = lambda: iter(())
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            args = mod.build_parser().parse_args([
                "preflight",
                "--agent-dir", os.path.dirname(os.path.abspath(__file__)),
                "--no-pull",
            ])
            res = mod.cmd_preflight(args, mod.Result())
        finally:
            mod.preflight._walk_ancestors = saved_walk
            if saved_env is not None:
                os.environ["CLAUDE_PLUGIN_ROOT"] = saved_env

        self.assertEqual(res.data["engine"]["confidence"], "assumed")
        self.assertTrue(any("--engine" in w for w in res.warnings), res.warnings)

    def test_preflight_reports_engine_with_a_profile_path(self):
        code, payload, raw = run_core(
            "preflight", "--agent-dir", os.path.dirname(os.path.abspath(__file__)),
            "--no-pull", "--engine", "cursor")
        self.assertEqual(code, 0, raw)
        engine = payload["data"]["engine"]
        self.assertEqual(engine["name"], "cursor")
        self.assertTrue(engine["profile"].endswith("docs/engines/cursor.md"), engine)
        self.assertTrue(os.path.isfile(engine["profile"]), engine["profile"])


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

    def test_fatal_payloads_are_distinguishable_from_determinate_negatives(self):
        """Exit 2 and a determinate `ok:false` demand opposite handling.

        `ok:false` at exit 0 means stop the boot ("no such agent"); exit 2 means
        take over by hand. With identical payload shapes the exit code was the
        only discriminator, and a caller reading stdout alone would abort a boot
        the contract says to complete manually.
        """
        make_repo(self.workspace, "repo-one", agents=("alpha",))
        rc_fatal, fatal, _ = self.core("preflight")          # unusable invocation
        rc_determinate, determinate, _ = self.core(
            "preflight", "--agent", "nope", "--workspace", self.workspace, "--no-pull")

        self.assertEqual(rc_fatal, 2)
        self.assertEqual(rc_determinate, 0)
        self.assertFalse(fatal["ok"])
        self.assertFalse(determinate["ok"])
        # ...and the payloads themselves must differ, not just the exit codes.
        self.assertTrue(fatal.get("fatal"))
        self.assertFalse(determinate.get("fatal", False))

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


class TestModuleLayout(unittest.TestCase):
    """Keep the stable CLI small and fallback procedures focused."""

    def test_entry_point_is_a_thin_compatibility_wrapper(self):
        with open(LR_CORE, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        self.assertLessEqual(len(lines), 40)
        self.assertTrue(any("from lr_core import *" in line for line in lines))

    def test_responsibilities_live_in_focused_modules(self):
        module_dir = os.path.join(FRAMEWORK_DIR, "scripts", "lr_core")
        expected = {
            "common.py", "preflight.py", "scan.py", "lore_graph.py",
            "lore_map.py", "lore_workset.py", "cli.py", "__init__.py",
        }
        self.assertTrue(expected.issubset(set(os.listdir(module_dir))))

        core = load_lr_core()
        self.assertEqual(core.pull_repo.__module__, "lr_core.preflight")
        self.assertEqual(core.scan_lore.__module__, "lr_core.scan")
        self.assertEqual(core.build_lore_graph.__module__, "lr_core.lore_graph")
        self.assertEqual(core.boot_lore_map.__module__, "lr_core.lore_map")
        self.assertEqual(core.select_lore_workset.__module__,
                         "lr_core.lore_workset")


if __name__ == "__main__":
    unittest.main(verbosity=2)
