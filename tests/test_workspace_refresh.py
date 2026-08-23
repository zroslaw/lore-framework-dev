#!/usr/bin/env python3
"""Tests for lr_core.workspace_refresh — the workspace-level auto-refresh leg.

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only
(unittest), matching test_lr_core.py and test_workspace_scan.py. The plugin
under test is located via $LR_FRAMEWORK_DIR, defaulting to the sibling
../lore-framework. That default is wrong under the worktree convention
(docs/worktrees.md) — set the variable explicitly there.

Most of this module's logic (state store, lock, git-derived pulled/dirty/
blocked facts, the bounded subprocess) is exercised as white-box unit tests
against `lr_core.workspace_refresh` directly — no subprocess, no CLI. A
smaller set of `TestPreflightIntegration` tests drives the real `lr-core`
CLI end to end, using the real $LR_FRAMEWORK_DIR so `scripts/workspace-pull`
is genuinely invoked.

Everything runs in per-test tempdirs with local-only git remotes and
scripts — no network, nothing touching the real workspace.

Run:  python3 tests/test_workspace_refresh.py -v
  or: python3 -m unittest discover -s tests -v
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
LR_CORE = os.path.join(FRAMEWORK_DIR, "scripts", "lr-core")

sys.path.insert(0, os.path.join(FRAMEWORK_DIR, "scripts"))
from lr_core import workspace_refresh as wr  # noqa: E402

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


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def run_core(*args):
    proc = subprocess.run(
        [sys.executable, LR_CORE] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    raw = proc.stdout.decode()
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = None
    return proc.returncode, parsed, raw


def fake_script(directory, exit_code, sleep_seconds=0, name="fake-pull.sh"):
    """A minimal stand-in for scripts/workspace-pull: ignores its argv and
    exits with a fixed code, optionally after a delay."""
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("#!/bin/bash\n")
        if sleep_seconds:
            fh.write("sleep %s\n" % sleep_seconds)
        fh.write("exit %d\n" % exit_code)
    os.chmod(path, 0o755)
    return path


def is_root():
    return hasattr(os, "geteuid") and os.geteuid() == 0


def make_git_repo(path, origin=None):
    os.makedirs(path, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    write(os.path.join(path, "f.md"), "x\n")
    git(path, "add", "-A")
    git(path, "commit", "-qm", "initial")
    if origin:
        os.makedirs(os.path.dirname(origin), exist_ok=True)
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
        git(path, "remote", "add", "origin", origin)
        git(path, "push", "-q", "-u", "origin", "main")
    return path


# --------------------------------------------------------------------------
# resolve_workspace_root
# --------------------------------------------------------------------------

class TestResolveWorkspaceRoot(unittest.TestCase):
    def test_plain_cwd_resolves_to_itself(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(wr.resolve_workspace_root(d), os.path.realpath(d))

    def test_worktree_cwd_resolves_to_parent_of_worktrees(self):
        with tempfile.TemporaryDirectory() as d:
            deep = os.path.join(d, ".worktrees", "lore-framework", "my-slug")
            os.makedirs(deep)
            self.assertEqual(wr.resolve_workspace_root(deep), os.path.realpath(d))

    def test_worktree_segment_need_not_have_both_repo_and_slug_present(self):
        with tempfile.TemporaryDirectory() as d:
            shallow = os.path.join(d, ".worktrees")
            os.makedirs(shallow)
            self.assertEqual(wr.resolve_workspace_root(shallow), os.path.realpath(d))

    def test_missing_dir_returns_none(self):
        self.assertIsNone(wr.resolve_workspace_root("/definitely/not/a/real/path/xyz"))

    def test_relative_path_is_resolved(self):
        with tempfile.TemporaryDirectory() as d:
            cwd = os.getcwd()
            try:
                os.chdir(d)
                self.assertEqual(wr.resolve_workspace_root("."), os.path.realpath(d))
            finally:
                os.chdir(cwd)


# --------------------------------------------------------------------------
# State store
# --------------------------------------------------------------------------

class WorkspaceTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-")
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)


class TestStateStore(WorkspaceTestBase):
    def test_missing_state_needs_refresh(self):
        self.assertTrue(wr.needs_refresh(self.workspace, 3600))

    def test_write_then_read_roundtrip(self):
        wr.write_state(self.workspace, last_attempt="2026-08-23T08:00:00+07:00",
                       last_success="2026-08-22T08:00:00+07:00", result="ok")
        state = wr.read_state(self.workspace)
        self.assertEqual(state["last-attempt"], "2026-08-23T08:00:00+07:00")
        self.assertEqual(state["last-success"], "2026-08-22T08:00:00+07:00")
        self.assertEqual(state["result"], "ok")

    def test_unparseable_state_file_needs_refresh(self):
        path = wr._state_path(self.workspace)
        write(path, "last-attempt: not-a-timestamp\n")
        self.assertTrue(wr.needs_refresh(self.workspace, 3600))

    def test_future_timestamp_needs_refresh(self):
        future = (datetime.datetime.now(datetime.timezone.utc)
                  + datetime.timedelta(hours=5)).astimezone().isoformat(timespec="seconds")
        wr.write_state(self.workspace, last_attempt=future)
        self.assertTrue(wr.needs_refresh(self.workspace, 3600))

    def test_naive_timestamp_without_offset_needs_refresh(self):
        path = wr._state_path(self.workspace)
        write(path, 'last-attempt: "2026-08-23T08:00:00"\n')
        self.assertTrue(wr.needs_refresh(self.workspace, 3600))

    def test_age_just_under_ttl_is_fresh(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        recent = (now - datetime.timedelta(seconds=10)).astimezone().isoformat(timespec="seconds")
        wr.write_state(self.workspace, last_attempt=recent)
        self.assertFalse(wr.needs_refresh(self.workspace, 3600))

    def test_age_just_over_ttl_needs_refresh(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        old = (now - datetime.timedelta(seconds=3700)).astimezone().isoformat(timespec="seconds")
        wr.write_state(self.workspace, last_attempt=old)
        self.assertTrue(wr.needs_refresh(self.workspace, 3600))

    def test_ttl_zero_always_refreshes(self):
        wr.write_state(self.workspace, last_attempt=wr._now_iso())
        self.assertTrue(wr.needs_refresh(self.workspace, 0))

    def test_write_is_atomic_no_tmp_file_left_behind(self):
        wr.write_state(self.workspace, last_attempt="2026-08-23T08:00:00+07:00")
        state_dir = os.path.dirname(wr._state_path(self.workspace))
        leftovers = [f for f in os.listdir(state_dir) if f.endswith(".tmp")]
        self.assertEqual(leftovers, [])

    def test_prior_last_success_survives_a_later_failed_write(self):
        wr.write_state(self.workspace, last_attempt="A", last_success="B", result="ok")
        wr.write_state(self.workspace, last_attempt="C", last_success="B",
                       result="failed", reason="pull-failed")
        state = wr.read_state(self.workspace)
        self.assertEqual(state["last-success"], "B")
        self.assertEqual(state["result"], "failed")
        self.assertEqual(state["reason"], "pull-failed")

    def test_timestamps_are_quoted_result_and_reason_are_not(self):
        wr.write_state(self.workspace, last_attempt="2026-08-23T08:00:00+07:00",
                       result="partial", reason="pull-failed")
        with open(wr._state_path(self.workspace), encoding="utf-8") as fh:
            raw = fh.read()
        self.assertIn('last-attempt: "2026-08-23T08:00:00+07:00"', raw)
        self.assertIn("result: partial", raw)
        self.assertIn("reason: pull-failed", raw)

    def test_empty_fields_are_simply_omitted(self):
        wr.write_state(self.workspace, last_attempt="2026-08-23T08:00:00+07:00")
        state = wr.read_state(self.workspace)
        self.assertNotIn("last-success", state)
        self.assertNotIn("result", state)
        self.assertNotIn("reason", state)


# --------------------------------------------------------------------------
# Lock
# --------------------------------------------------------------------------

class TestLock(WorkspaceTestBase):
    def test_first_ever_claim_succeeds_even_without_the_state_dir(self):
        # Regression: os.open(O_CREAT|O_EXCL) on a nonexistent parent
        # directory raises ENOENT, which a bare `except OSError` would
        # otherwise misreport as "another session holds the lock".
        lock_path = wr._lock_path(self.workspace)
        self.assertFalse(os.path.isdir(os.path.dirname(lock_path)))
        self.assertEqual(wr._claim_lock(lock_path), "claimed")

    def test_two_concurrent_claims_only_one_proceeds(self):
        lock_path = wr._lock_path(self.workspace)
        self.assertEqual(wr._claim_lock(lock_path), "claimed")
        self.assertEqual(wr._claim_lock(lock_path), "in-progress")

    def test_stale_lock_is_reclaimed(self):
        lock_path = wr._lock_path(self.workspace)
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        open(lock_path, "w").close()
        old = time.time() - (wr.WORKSPACE_LOCK_STALE_SEC + 10)
        os.utime(lock_path, (old, old))
        self.assertEqual(wr._claim_lock(lock_path), "claimed")

    def test_young_lock_blocks_and_does_not_wait(self):
        lock_path = wr._lock_path(self.workspace)
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        open(lock_path, "w").close()
        start = time.time()
        result = wr._claim_lock(lock_path)
        elapsed = time.time() - start
        self.assertEqual(result, "in-progress")
        self.assertLess(elapsed, 1.0, "a blocked claim must not wait")

    def test_lock_file_is_empty(self):
        lock_path = wr._lock_path(self.workspace)
        wr._claim_lock(lock_path)
        self.assertEqual(os.path.getsize(lock_path), 0)

    def test_sigkill_simulated_by_a_stale_lock_reclaims_immediately(self):
        """A SIGKILLed refresh leaves the lock behind; the mtime staleness
        check is what lets the next boot reclaim it and refresh right away,
        rather than silently going dark for a full TTL window."""
        lock_path = wr._lock_path(self.workspace)
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        open(lock_path, "w").close()
        old = time.time() - (wr.WORKSPACE_LOCK_STALE_SEC + 5)
        os.utime(lock_path, (old, old))
        self.assertEqual(wr._claim_lock(lock_path), "claimed")

    def test_unexpected_lock_contents_are_still_honoured_never_parsed(self):
        lock_path = wr._lock_path(self.workspace)
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        write(lock_path, "garbage that is not empty at all\n")
        # Young: still blocks, regardless of contents.
        self.assertEqual(wr._claim_lock(lock_path), "in-progress")

    def test_readonly_state_dir_is_an_error_not_in_progress(self):
        if is_root():
            self.skipTest("permission bits are not enforced against root")
        os.makedirs(self.workspace, exist_ok=True)
        os.chmod(self.workspace, 0o500)
        try:
            lock_path = wr._lock_path(self.workspace)
            self.assertEqual(wr._claim_lock(lock_path), "error")
        finally:
            os.chmod(self.workspace, 0o700)

    def test_lock_released_even_when_do_refresh_raises(self):
        original = wr._do_refresh
        wr._do_refresh = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            result = wr.run_workspace_refresh(
                self.workspace, ttl=0, framework_root=FRAMEWORK_DIR)
        finally:
            wr._do_refresh = original
        self.assertEqual(result["status"], "failed")
        self.assertFalse(os.path.exists(wr._lock_path(self.workspace)),
                         "the lock must be released on the exception path too")


# --------------------------------------------------------------------------
# Bounded subprocess with process-group kill
# --------------------------------------------------------------------------

class TestSubprocessBounding(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-bound-")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def test_fast_success_returns_rc_zero(self):
        script = fake_script(self.tmp, 0)
        rc, out, err = wr._run_workspace_pull(script, self.tmp, timeout=5)
        self.assertEqual(rc, 0)

    def test_nonzero_exit_is_reported_verbatim(self):
        script = fake_script(self.tmp, 1)
        rc, out, err = wr._run_workspace_pull(script, self.tmp, timeout=5)
        self.assertEqual(rc, 1)

    def test_timeout_returns_none_rc_with_a_timeout_message(self):
        script = fake_script(self.tmp, 0, sleep_seconds=10)
        rc, out, err = wr._run_workspace_pull(script, self.tmp, timeout=1)
        self.assertIsNone(rc)
        self.assertIn("timed out", err)

    def test_missing_script_returns_none_rc_not_an_exception(self):
        rc, out, err = wr._run_workspace_pull(
            os.path.join(self.tmp, "does-not-exist.sh"), self.tmp, timeout=5)
        self.assertIsNone(rc)

    def test_orphaned_child_is_killed_via_the_process_group(self):
        """workspace-pull forks parallel git jobs with `&`; a plain
        subprocess timeout only kills the bash parent, leaving orphaned
        children writing to the workspace after this call has reported
        failure. start_new_session + a process-group kill must prevent that.
        """
        marker = os.path.join(self.tmp, "child-ran")
        script = os.path.join(self.tmp, "slow.sh")
        with open(script, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/bash\n")
            fh.write("( sleep 2 && touch %s ) &\n" % marker)
            fh.write("sleep 30\n")
        os.chmod(script, 0o755)

        rc, out, err = wr._run_workspace_pull(script, self.tmp, timeout=1)
        self.assertIsNone(rc)
        time.sleep(2.5)
        self.assertFalse(os.path.exists(marker),
                         "the orphaned child must be killed, not left running")


# --------------------------------------------------------------------------
# Top-level repo enumeration + pull/dirty/blocked derivation
# --------------------------------------------------------------------------

class TestTopLevelGitRepos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-toplevel-")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def test_finds_repos_skips_hidden_dirs_symlinks_and_plain_dirs(self):
        make_git_repo(os.path.join(self.tmp, "repo-one"))
        make_git_repo(os.path.join(self.tmp, ".hidden-repo"))
        os.makedirs(os.path.join(self.tmp, "plain-dir"))
        target = make_git_repo(os.path.join(self.tmp, "real-target"))
        os.symlink(target, os.path.join(self.tmp, "linked-repo"))

        found = wr._top_level_git_repos(self.tmp)
        names = sorted(n for n, _ in found)
        self.assertEqual(names, ["real-target", "repo-one"])


class TestPullDerivation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-pull-")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def _repo(self, name):
        return make_git_repo(os.path.join(self.tmp, name))

    def test_head_advanced_appears_in_pulled(self):
        path = self._repo("r1")
        before = {"r1": {"head": wr._head(path), "dirty": False}}
        write(os.path.join(path, "g.md"), "y\n")
        git(path, "add", "-A")
        git(path, "commit", "-qm", "second")
        self.assertEqual(wr._pulled_list([("r1", path)], before),
                         [{"repo": "r1", "dirty": False}])

    def test_head_unchanged_is_absent_from_pulled(self):
        path = self._repo("r1")
        before = {"r1": {"head": wr._head(path), "dirty": False}}
        self.assertEqual(wr._pulled_list([("r1", path)], before), [])

    def test_dirty_before_and_advanced_carries_dirty_true(self):
        path = self._repo("r1")
        write(os.path.join(path, "uncommitted.md"), "wip\n")
        before = {"r1": {"head": wr._head(path), "dirty": wr._is_dirty(path)}}
        self.assertTrue(before["r1"]["dirty"])
        write(os.path.join(path, "g.md"), "y\n")
        git(path, "add", "-A")
        git(path, "commit", "-qm", "second")
        self.assertEqual(wr._pulled_list([("r1", path)], before),
                         [{"repo": "r1", "dirty": True}])

    def test_dirty_but_not_advanced_is_absent_from_pulled(self):
        path = self._repo("r1")
        before = {"r1": {"head": wr._head(path), "dirty": False}}
        write(os.path.join(path, "uncommitted.md"), "wip\n")
        self.assertEqual(wr._pulled_list([("r1", path)], before), [])

    def test_dirtied_after_the_snapshot_does_not_retroactively_flip_the_flag(self):
        """The snapshot is the record — dirtying the repo after it was taken,
        even if the repo also advances, must not change the reported flag."""
        path = self._repo("r1")
        before = {"r1": {"head": wr._head(path), "dirty": False}}
        write(os.path.join(path, "uncommitted.md"), "wip\n")
        write(os.path.join(path, "g.md"), "y\n")
        git(path, "add", "-A")
        git(path, "commit", "-qm", "second")
        self.assertEqual(wr._pulled_list([("r1", path)], before),
                         [{"repo": "r1", "dirty": False}])

    def test_repo_absent_from_the_snapshot_is_never_reported_pulled(self):
        # A repo workspace-pull might have cloned mid-run (this leg never
        # asks it to, but derivation must not assume `before` is complete).
        path = self._repo("new-repo")
        self.assertEqual(wr._pulled_list([("new-repo", path)], {}), [])


class TestBlockedRepos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-blocked-")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def test_dirty_and_behind_is_blocked(self):
        origin = os.path.join(self.tmp, "remotes", "shared.git")
        clone = make_git_repo(os.path.join(self.tmp, "clone"), origin=origin)

        other = os.path.join(self.tmp, "other")
        subprocess.run(["git", "clone", "-q", origin, other], check=True)
        write(os.path.join(other, "g.md"), "y\n")
        git(other, "add", "-A")
        git(other, "commit", "-qm", "second")
        git(other, "push", "-q")

        write(os.path.join(clone, "uncommitted.md"), "wip\n")
        # `@{u}` reflects the last fetch, not the remote's live state — a real
        # `git pull --ff-only` fetches even when it then refuses to merge, so
        # simulate that here rather than asserting against stale local refs.
        git(clone, "fetch", "-q")
        self.assertEqual(wr._blocked_repos([("clone", clone)]), ["clone"])

    def test_dirty_but_not_behind_is_not_blocked(self):
        path = make_git_repo(os.path.join(self.tmp, "solo"))
        write(os.path.join(path, "uncommitted.md"), "wip\n")
        self.assertEqual(wr._blocked_repos([("solo", path)]), [])

    def test_behind_but_clean_is_not_blocked(self):
        origin = os.path.join(self.tmp, "remotes", "shared2.git")
        clone = make_git_repo(os.path.join(self.tmp, "clone2"), origin=origin)

        other = os.path.join(self.tmp, "other2")
        subprocess.run(["git", "clone", "-q", origin, other], check=True)
        write(os.path.join(other, "g.md"), "y\n")
        git(other, "add", "-A")
        git(other, "commit", "-qm", "second")
        git(other, "push", "-q")

        self.assertEqual(wr._blocked_repos([("clone2", clone)]), [])


# --------------------------------------------------------------------------
# _do_refresh: exit-code derivation and the setup-required short-circuit
# --------------------------------------------------------------------------

class TestDoRefresh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-doref-")
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def test_exit_0_is_refreshed(self):
        script = fake_script(self.tmp, 0)
        result = wr._do_refresh(self.workspace, None, script)
        self.assertEqual(result["status"], "refreshed")

    def test_exit_1_is_partial_pull_failed(self):
        script = fake_script(self.tmp, 1)
        result = wr._do_refresh(self.workspace, None, script)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["reason"], "pull-failed")

    def test_exit_2_is_failed_invocation(self):
        script = fake_script(self.tmp, 2)
        result = wr._do_refresh(self.workspace, None, script)
        self.assertEqual(result, {"status": "failed", "reason": "invocation"})

    def test_unexpected_exit_code_is_failed_invocation(self):
        script = fake_script(self.tmp, 17)
        result = wr._do_refresh(self.workspace, None, script)
        self.assertEqual(result, {"status": "failed", "reason": "invocation"})

    def test_missing_script_is_failed_invocation(self):
        result = wr._do_refresh(
            self.workspace, None, os.path.join(self.tmp, "nope.sh"))
        self.assertEqual(result, {"status": "failed", "reason": "invocation"})

    def test_declared_repo_missing_short_circuits_before_any_script_check(self):
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\nrepos:\n  - git@example.com:t/missing.git\n---\n")
        # A script path that does not even exist: if this returns
        # setup-required anyway, the S6 check ran and returned before the
        # script-existence check was ever reached.
        result = wr._do_refresh(
            self.workspace, None, os.path.join(self.tmp, "does-not-exist.sh"))
        self.assertEqual(result, {"status": "setup-required",
                                  "missing_repos": ["missing"]})

    def test_findings_are_filtered_to_warn_severity(self):
        script = fake_script(self.tmp, 0)
        result = wr._do_refresh(self.workspace, None, script)
        for finding in result.get("findings", []):
            self.assertEqual(finding["severity"], "warn")


# --------------------------------------------------------------------------
# run_workspace_refresh: end-to-end through the module's own public API
# --------------------------------------------------------------------------

class TestRunWorkspaceRefresh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-run-")
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def test_disabled_flag_short_circuits_before_any_disk_io(self):
        result = wr.run_workspace_refresh(
            self.workspace, do_refresh=False, framework_root=FRAMEWORK_DIR)
        self.assertEqual(result, {"status": "disabled"})
        self.assertFalse(os.path.isdir(os.path.join(self.workspace, ".tmp")))

    def test_unresolvable_workspace_root_is_skipped(self):
        result = wr.run_workspace_refresh(
            "/definitely/not/a/real/path", framework_root=FRAMEWORK_DIR)
        self.assertEqual(result, {"status": "skipped"})

    def test_second_call_within_ttl_is_fresh(self):
        script = fake_script(self.tmp, 0)
        first = wr.run_workspace_refresh(
            self.workspace, ttl=3600, framework_root=FRAMEWORK_DIR,
            script_path=script)
        self.assertNotEqual(first["status"], "fresh")
        second = wr.run_workspace_refresh(
            self.workspace, ttl=3600, framework_root=FRAMEWORK_DIR,
            script_path=script)
        self.assertEqual(second["status"], "fresh")

    def test_fresh_flag_bypasses_the_ttl(self):
        script = fake_script(self.tmp, 0)
        wr.run_workspace_refresh(self.workspace, ttl=3600,
                                 framework_root=FRAMEWORK_DIR, script_path=script)
        forced = wr.run_workspace_refresh(
            self.workspace, ttl=3600, fresh=True,
            framework_root=FRAMEWORK_DIR, script_path=script)
        self.assertNotEqual(forced["status"], "fresh")

    def test_state_file_records_the_attempt(self):
        script = fake_script(self.tmp, 0)
        wr.run_workspace_refresh(self.workspace, ttl=0,
                                 framework_root=FRAMEWORK_DIR, script_path=script)
        state = wr.read_state(self.workspace)
        self.assertIn("last-attempt", state)
        self.assertIn("last-success", state)
        self.assertEqual(state["result"], "ok")

    def test_failed_run_does_not_stamp_last_success(self):
        script = fake_script(self.tmp, 2)
        wr.run_workspace_refresh(self.workspace, ttl=0,
                                 framework_root=FRAMEWORK_DIR, script_path=script)
        state = wr.read_state(self.workspace)
        self.assertNotIn("last-success", state)
        self.assertEqual(state["result"], "failed")
        self.assertEqual(state["reason"], "invocation")

    def test_ensure_tmp_ignored_runs_before_the_first_write_when_git_tracked(self):
        git(self.workspace, "init", "-q", "-b", "main")
        script = fake_script(self.tmp, 0)
        wr.run_workspace_refresh(self.workspace, ttl=0,
                                 framework_root=FRAMEWORK_DIR, script_path=script)
        with open(os.path.join(self.workspace, ".gitignore"), encoding="utf-8") as fh:
            gitignore = fh.read()
        self.assertIn("/.tmp/", gitignore.split("\n"))

    def test_non_git_workspace_skips_gitignore_but_still_refreshes(self):
        script = fake_script(self.tmp, 0)
        result = wr.run_workspace_refresh(
            self.workspace, ttl=0, framework_root=FRAMEWORK_DIR,
            script_path=script)
        self.assertEqual(result["status"], "refreshed")
        self.assertFalse(os.path.isfile(os.path.join(self.workspace, ".gitignore")))

    def test_uncaught_exception_in_a_step_still_returns_a_status(self):
        original = wr._do_refresh
        wr._do_refresh = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            result = wr.run_workspace_refresh(
                self.workspace, ttl=0, framework_root=FRAMEWORK_DIR)
        finally:
            wr._do_refresh = original
        self.assertEqual(result["status"], "failed")

    def test_state_file_deleted_forces_a_refresh_the_documented_gesture(self):
        script = fake_script(self.tmp, 0)
        wr.run_workspace_refresh(self.workspace, ttl=3600,
                                 framework_root=FRAMEWORK_DIR, script_path=script)
        fresh = wr.run_workspace_refresh(
            self.workspace, ttl=3600, framework_root=FRAMEWORK_DIR,
            script_path=script)
        self.assertEqual(fresh["status"], "fresh")
        os.remove(wr._state_path(self.workspace))
        forced = wr.run_workspace_refresh(
            self.workspace, ttl=3600, framework_root=FRAMEWORK_DIR,
            script_path=script)
        self.assertNotEqual(forced["status"], "fresh")

    def test_readonly_workspace_root_degrades_to_a_status_never_raises(self):
        if is_root():
            self.skipTest("permission bits are not enforced against root")
        os.chmod(self.workspace, 0o500)
        try:
            result = wr.run_workspace_refresh(
                self.workspace, ttl=0, framework_root=FRAMEWORK_DIR)
        finally:
            os.chmod(self.workspace, 0o700)
        self.assertIn(result["status"], ("failed", "skipped"))


# --------------------------------------------------------------------------
# Full preflight CLI integration
# --------------------------------------------------------------------------

class TestPreflightIntegration(unittest.TestCase):
    """Drives the real `lr-core preflight` CLI with the real
    $LR_FRAMEWORK_DIR, so `scripts/workspace-pull` is genuinely invoked.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-wsrefresh-preflight-")
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def core(self, *args):
        return run_core("--framework-root", FRAMEWORK_DIR, *args)

    def agent_dir(self, base=None, name="alpha"):
        agent_dir = os.path.join(base or self.workspace, "agents", name)
        write(os.path.join(agent_dir, "role.md"),
             "---\ndescription: %s\n---\n" % name)
        return agent_dir

    def test_no_workspace_refresh_flag_disables_only_that_leg(self):
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace,
            "--no-workspace-refresh")
        self.assertEqual(rc, 0, raw)
        self.assertEqual(out["data"]["workspace_refresh"], {"status": "disabled"})
        self.assertFalse(os.path.isdir(os.path.join(self.workspace, ".tmp")))

    def test_no_pull_disables_both_legs(self):
        repo = os.path.join(self.workspace, "repo-one")
        write(os.path.join(repo, "lore-repo.md"),
             '---\ndescription: t\nversion: "1"\n---\n')
        write(os.path.join(repo, "agents", "alpha", "role.md"),
             "---\ndescription: alpha\n---\n")
        rc, out, raw = self.core(
            "preflight", "--agent", "alpha", "--workspace", self.workspace,
            "--no-pull")
        self.assertEqual(rc, 0, raw)
        self.assertEqual(out["data"]["pull"]["status"], "disabled")
        self.assertEqual(out["data"]["workspace_refresh"], {"status": "disabled"})

    def test_workspace_ttl_zero_always_refreshes(self):
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        rc1, out1, raw1 = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace,
            "--workspace-ttl", "0")
        rc2, out2, raw2 = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace,
            "--workspace-ttl", "0")
        self.assertNotEqual(out1["data"]["workspace_refresh"]["status"], "fresh", raw1)
        self.assertNotEqual(out2["data"]["workspace_refresh"]["status"], "fresh", raw2)

    def test_fresh_flag_bypasses_the_workspace_ttl(self):
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        self.core("preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        self.assertEqual(out["data"]["workspace_refresh"]["status"], "fresh", raw)
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace,
            "--fresh")
        self.assertNotEqual(out["data"]["workspace_refresh"]["status"], "fresh", raw)

    def test_non_git_workspace_runs_the_leg_but_skips_gitignore(self):
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        self.assertEqual(out["data"]["workspace_refresh"]["status"], "refreshed", raw)
        self.assertFalse(os.path.isfile(os.path.join(self.workspace, ".gitignore")))

    def test_declared_repo_missing_yields_setup_required_and_never_pulls(self):
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\nrepos:\n"
             "  - git@example.com:test/missing-repo.git\n---\n")
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        wsr = out["data"]["workspace_refresh"]
        self.assertEqual(wsr["status"], "setup-required", raw)
        self.assertEqual(wsr["missing_repos"], ["missing-repo"])
        self.assertFalse(os.path.isdir(os.path.join(self.workspace, "missing-repo")),
                         "workspace-pull must never be invoked for setup-required")

    def test_state_deleted_with_repos_present_is_normal_refresh_not_setup_required(self):
        agent_dir = self.agent_dir()
        origin = os.path.join(self.tmp, "remotes", "child-repo.git")
        make_git_repo(os.path.join(self.workspace, "child-repo"), origin=origin)
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\nrepos:\n  - %s\n---\n" % origin)

        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        self.assertNotEqual(out["data"]["workspace_refresh"]["status"],
                            "setup-required", raw)

        os.remove(os.path.join(self.workspace, ".tmp", "lr-state", "workspace-refresh"))
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        self.assertNotEqual(out["data"]["workspace_refresh"]["status"],
                            "setup-required",
                            "deleting the state file is the documented "
                            "force-refresh gesture, not a request to reclone")

    def test_agent_outside_any_repo_still_runs_the_leg(self):
        agent_dir = self.agent_dir()  # no lore-repo.md two levels up
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        self.assertEqual(out["data"]["pull"]["status"], "skipped")
        self.assertEqual(out["data"]["workspace_refresh"]["status"], "refreshed", raw)

    def test_cwd_inside_worktree_resolves_to_the_real_workspace_root(self):
        fake_worktree = os.path.join(self.workspace, ".worktrees", "some-repo", "slug")
        os.makedirs(fake_worktree)
        agent_dir = self.agent_dir(base=fake_worktree)
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", fake_worktree)
        self.assertEqual(out["data"]["workspace_refresh"]["status"], "refreshed", raw)
        self.assertTrue(os.path.isfile(os.path.join(
            self.workspace, ".tmp", "lr-state", "workspace-refresh")),
            "state must land at the real workspace root")
        self.assertFalse(os.path.isdir(os.path.join(fake_worktree, ".tmp")),
                         "state must NOT land inside the disposable worktree")

    def test_readonly_state_dir_degrades_without_exit_2(self):
        if is_root():
            self.skipTest("permission bits are not enforced against root")
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        tmp_dir = os.path.join(self.workspace, ".tmp")
        os.makedirs(tmp_dir)
        os.chmod(tmp_dir, 0o500)
        try:
            rc, out, raw = self.core(
                "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        finally:
            os.chmod(tmp_dir, 0o700)
        self.assertEqual(rc, 0, raw)
        self.assertIn(out["data"]["workspace_refresh"]["status"], ("failed", "skipped"))

    def test_readonly_gitignore_does_not_block_the_refresh(self):
        if is_root():
            self.skipTest("permission bits are not enforced against root")
        agent_dir = self.agent_dir()
        write(os.path.join(self.workspace, "lore-workspace.md"),
             "---\ndescription: w\n---\n")
        git(self.workspace, "init", "-q", "-b", "main")
        gitignore = os.path.join(self.workspace, ".gitignore")
        write(gitignore, "# nothing ignored yet\n")
        os.chmod(gitignore, 0o400)
        try:
            rc, out, raw = self.core(
                "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace)
        finally:
            os.chmod(gitignore, 0o600)
        self.assertEqual(rc, 0, raw)
        self.assertNotEqual(out["data"]["workspace_refresh"]["status"], "failed", raw)

    def test_workspace_refresh_key_always_present_in_the_envelope(self):
        agent_dir = self.agent_dir()
        rc, out, raw = self.core(
            "preflight", "--agent-dir", agent_dir, "--workspace", self.workspace,
            "--no-pull")
        self.assertIn("workspace_refresh", out["data"], raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
