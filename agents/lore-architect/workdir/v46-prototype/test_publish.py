"""Adversarial acceptance tests for the executable design; no external remotes."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import publish as p


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.main = self.root / "main"
        self.main.mkdir()
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        p.git(self.main, "init", "-b", "main")
        p.git(self.main, "config", "user.name", "Design fixture")
        p.git(self.main, "config", "user.email", "fixture@example.invalid")
        p.git(self.main, "config", "commit.gpgsign", "false")
        p.git(self.main, "config", "core.hooksPath", str(self.root / "no-hooks"))
        self.topic = "agents/a/lore/topic.md"
        self.write(self.main, self.topic, "base\n")
        self.write(self.main, "lore-repo.md", "version: 45\n")
        p.git(self.main, "add", "--", self.topic, "lore-repo.md")
        p.git(self.main, "commit", "-m", "base")
        p.git(self.main, "remote", "add", "origin", str(self.remote))
        p.git(self.main, "push", "-u", "origin", "main")
        self.base = p.out(self.main, "rev-parse", "HEAD")
        self.seq = 0

    def write(self, repo, path, value):
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value)

    def session(self, **kwargs):
        self.seq += 1
        return p.Session.begin(self.main, self.root / ("session-%s" % self.seq), **kwargs)

    def snapshot(self, s, path=None, text="session\n"):
        path = path or self.topic
        self.write(s.repo, path, text)
        self.assertEqual(s.commit([path], "session snapshot")["status"], "pending")

    def advance(self, path="remote.md", text="remote\n"):
        s = self.session()
        self.snapshot(s, path, text)
        self.assertEqual(s.publish()["status"], "published")
        return s

    def conflict(self, path=None):
        s = self.session()
        self.snapshot(s, path)
        self.advance(path or self.topic, "incoming\n")
        self.assertEqual(s.publish()["status"], "conflict")
        return s

    def test_two_sessions_same_file_are_isolated_and_both_survive_merge(self):
        s = self.conflict()
        self.write(s.repo, self.topic, "session\nincoming\n")
        self.assertEqual(s.resolve("a")["status"], "pending")
        self.assertEqual(s.publish()["status"], "published")
        self.assertEqual(p.out(self.remote, "show", "main:" + self.topic), "session\nincoming")
        self.assertEqual(p.out(self.main, "rev-parse", "HEAD"), self.base)

    def test_next_canonical_pull_and_next_session_succeed(self):
        s = self.advance()
        p.git(self.main, "pull", "--ff-only")
        self.assertEqual(p.out(self.main, "rev-parse", "HEAD"), s.state["head"])
        self.assertFalse(p.git(self.main, "status", "--porcelain").stdout)
        nxt = self.session()
        self.assertEqual(nxt.state["base"], s.state["head"])

    def test_no_shared_commit_or_rollback_even_when_other_session_advances_main(self):
        s = self.session()
        self.snapshot(s)
        self.write(self.main, "other.md", "unreviewed\n")
        p.git(self.main, "add", "other.md")
        p.git(self.main, "commit", "-m", "other session")
        other = p.out(self.main, "rev-parse", "HEAD")
        self.assertEqual(s.publish()["status"], "published")
        self.assertEqual(p.out(self.main, "rev-parse", "HEAD"), other)
        self.assertNotEqual(p.git(self.remote, "merge-base", "--is-ancestor", other, "main", check=False).returncode, 0)

    def test_unrelated_canonical_staging_never_enters_merge(self):
        s = self.conflict()
        self.write(self.main, "foreign.md", "in progress\n")
        p.git(self.main, "add", "foreign.md")
        self.write(s.repo, self.topic, "session\nincoming\n")
        s.resolve("a")
        self.assertEqual(s.publish()["status"], "published")
        self.assertNotEqual(p.git(self.remote, "show", "main:foreign.md", check=False).returncode, 0)
        self.assertIn("foreign.md", p.out(self.main, "diff", "--cached", "--name-only"))

    def test_intruding_private_index_changes_are_refused_without_reset(self):
        s = self.conflict()
        head = p.out(s.repo, "rev-parse", "HEAD")
        self.write(s.repo, self.topic, "session\nincoming\n")
        self.write(s.repo, "foreign.md", "intrusion\n")
        p.git(s.repo, "add", "foreign.md")
        with self.assertRaisesRegex(p.Refused, "unrelated index"):
            s.resolve("a")
        self.assertEqual(p.out(s.repo, "rev-parse", "HEAD"), head)
        self.assertTrue((s.repo / "foreign.md").exists())

    def test_external_session_commit_is_detected_without_undoing_it(self):
        s = self.session()
        self.snapshot(s)
        self.write(s.repo, "external", "another writer\n")
        p.git(s.repo, "add", "external")
        p.git(s.repo, "commit", "-m", "outside protocol")
        external = p.out(s.repo, "rev-parse", "HEAD")
        with self.assertRaisesRegex(p.Refused, "HEAD changed"):
            s.publish()
        self.assertEqual(p.out(s.repo, "rev-parse", "HEAD"), external)

    def test_destination_ignores_push_default_refspec_and_pushurl(self):
        p.git(self.main, "config", "remote.origin.push", "HEAD:refs/heads/wrong")
        p.git(self.main, "config", "remote.origin.pushurl", str(self.root / "wrong.git"))
        s = self.advance()
        self.assertEqual(p.out(self.remote, "rev-parse", "main"), s.state["head"])
        self.assertNotEqual(p.git(self.remote, "rev-parse", "--verify", "wrong", check=False).returncode, 0)

    def test_update_defers_when_canonical_has_unpublished_commits(self):
        self.write(self.main, "unreviewed", "local\n")
        p.git(self.main, "add", "unreviewed")
        p.git(self.main, "commit", "-m", "unreviewed")
        with self.assertRaisesRegex(p.Refused, "update deferred"):
            self.session(kind="update")
        self.assertEqual(p.out(self.remote, "rev-parse", "main"), self.base)

    def test_update_defers_on_dirty_canonical_target_without_writing_it(self):
        self.write(self.main, "lore-repo.md", "custom\n")
        with self.assertRaisesRegex(p.Refused, "update deferred"):
            self.session(kind="update")
        self.assertEqual((self.main / "lore-repo.md").read_text(), "custom\n")

    def test_update_no_merge_preserves_snapshot_after_remote_race(self):
        s = self.session(kind="update")
        self.snapshot(s, "lore-repo.md", "version: 46\n")
        head = s.state["head"]
        self.advance()
        self.assertEqual(s.publish(mode="no-merge")["status"], "pending")
        self.assertEqual(p.out(s.repo, "rev-parse", "HEAD"), head)
        self.assertEqual(len(p.out(s.repo, "rev-list", "--parents", "-n", "1", "HEAD").split()), 2)

    def test_foreign_conflict_stays_visible_with_canonical_ahead_zero(self):
        s = self.conflict("workdir/draft.md")
        with self.assertRaisesRegex(p.Refused, "foreign conflict"):
            s.resolve("a")
        p.git(self.main, "pull", "--ff-only")
        self.assertEqual(p.out(self.main, "rev-list", "--count", "@{u}..HEAD"), "0")
        self.assertEqual(p.status(self.main)[0]["id"], s.state["id"])
        self.assertTrue(s.record.exists())

    def test_status_is_identical_across_main_and_worktree_branches(self):
        s = self.conflict()
        a = p.status(self.main)
        b = p.status(s.repo)
        self.assertEqual([(i["id"], i["reason"]) for i in a], [(i["id"], i["reason"]) for i in b])
        self.assertTrue(s.record.exists())

    def test_one_success_cannot_clear_another_sessions_failure(self):
        s = self.conflict()
        self.advance("separate.md")
        self.assertIn(s.state["id"], [r["id"] for r in p.status(self.main)])

    def test_unknown_version_and_invalid_json_are_retained_and_visible(self):
        directory = p.common(self.main) / "lr-publish"
        directory.mkdir()
        a, b = directory / "future.json", directory / "broken.json"
        a.write_text('{"version": 99}')
        b.write_text('not json')
        rows = p.status(self.main)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["status"] == "unknown" for r in rows))
        self.assertTrue(a.exists() and b.exists())

    def test_tampered_record_cannot_redirect_publisher_into_primary(self):
        s = self.session()
        s.state.update(worktree=str(self.main), branch="refs/heads/main", head=self.base)
        p.atomic_json(s.record, s.state)
        with self.assertRaisesRegex(p.Refused, "identity is invalid"):
            s.commit([self.topic], "must refuse")
        self.assertEqual(p.out(self.main, "rev-parse", "HEAD"), self.base)
        self.assertEqual(p.status(self.main)[0]["status"], "unknown")

    def test_incomplete_known_schema_cannot_claim_success(self):
        s = self.session()
        s.record.write_text('{"version": 1, "status": "published"}')
        self.assertEqual(p.status(self.main)[0]["status"], "unknown")
        self.assertTrue(s.record.exists())

    def test_slow_git_hook_is_bounded_and_leaves_interrupted_work_visible(self):
        s = self.session()
        hooks = self.root / "hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nsleep 30\nexit 0\n")
        hook.chmod(0o755)
        p.git(self.main, "config", "core.hooksPath", str(hooks))
        self.write(s.repo, self.topic, "new\n")
        with patch.object(p, "GIT_TIMEOUT", 1):
            self.assertEqual(s.commit([self.topic], "timeout")["status"], "unknown")
        self.assertEqual(p.out(self.remote, "rev-parse", "main"), self.base)
        self.assertTrue(p.status(self.main))

    def test_read_only_status_does_not_remove_a_concurrent_replacement(self):
        s = self.conflict()
        original = s.record.read_bytes()
        p.status(self.main)
        self.assertEqual(s.record.read_bytes(), original)

    def test_network_failure_retains_snapshot_and_reports_unknown(self):
        s = self.session()
        self.snapshot(s)
        self.remote.rename(self.root / "offline.git")
        self.assertEqual(s.publish()["status"], "unknown")
        self.assertEqual(p.out(s.repo, "rev-parse", "HEAD"), s.state["head"])
        self.assertTrue(p.status(self.main))
        (self.root / "offline.git").rename(self.remote)
        self.assertEqual(s.resume()["status"], "pending")
        self.assertEqual(s.publish()["status"], "published")

    def test_crash_after_commit_is_visible_and_does_not_adopt_unknown_tip(self):
        s = self.session()
        self.write(s.repo, self.topic, "new\n")
        real_write = p.atomic_json
        def die(path, value):
            if value.get("status") == "pending":
                raise KeyboardInterrupt("simulated process exit after Git commit")
            real_write(path, value)
        with patch.object(p, "atomic_json", side_effect=die):
            with self.assertRaises(KeyboardInterrupt):
                s.commit([self.topic], "durable snapshot")
        self.assertNotEqual(p.out(s.repo, "rev-parse", "HEAD"), self.base)
        self.assertEqual(p.status(self.main)[0]["activity"], "interrupted")
        with self.assertRaisesRegex(p.Refused, "HEAD changed"):
            s.resume()

    def test_crash_after_push_before_receipt_is_recovered(self):
        s = self.session()
        self.snapshot(s)
        real_write = p.atomic_json
        def die(path, value):
            if value.get("status") == "published":
                raise KeyboardInterrupt("simulated exit before receipt")
            real_write(path, value)
        with patch.object(p, "atomic_json", side_effect=die):
            with self.assertRaises(KeyboardInterrupt):
                s.publish()
        self.assertEqual(json.loads(s.record.read_text())["status"], "publishing")
        self.assertEqual(s.resume()["status"], "published")
        self.assertEqual(p.status(self.main), [])

    def test_repeated_remote_races_stop_after_three_actual_pushes(self):
        s = self.session()
        self.snapshot(s)
        remote_heads = [self.advance("racer.md", str(i)).state["head"] for i in range(3)]
        p.git(self.remote, "update-ref", "refs/heads/main", self.base)
        real_git, calls = p.git, []
        def race(repo, *args, **kwargs):
            if args[:1] == ("push",):
                real_git(self.remote, "update-ref", "refs/heads/main", remote_heads[len(calls)])
                calls.append(1)
            return real_git(repo, *args, **kwargs)
        with patch.object(p, "git", side_effect=race):
            self.assertEqual(s.publish()["status"], "pending")
        self.assertEqual(len(calls), 3)
        self.assertEqual(p.out(self.main, "rev-parse", "HEAD"), self.base)

    def test_record_first_failure_stays_stable_across_retries(self):
        s = self.session()
        self.snapshot(s)
        self.assertNotIn("first_failure", s.state)
        self.advance()
        first = s.publish(mode="no-merge")["first_failure"]
        self.assertEqual(s.publish(mode="no-merge")["first_failure"], first)

    def test_rebase_without_rebase_head_is_detected(self):
        s = self.session()
        gitdir = Path(p.out(s.repo, "rev-parse", "--absolute-git-dir"))
        (gitdir / "rebase-merge").mkdir()
        self.write(s.repo, self.topic, "new\n")
        with self.assertRaisesRegex(p.Refused, "another Git operation"):
            s.commit([self.topic], "blocked")

    def test_commit_hook_failure_preserves_work_and_does_not_push(self):
        s = self.session()
        hooks = self.root / "hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        p.git(self.main, "config", "core.hooksPath", str(hooks))
        self.write(s.repo, self.topic, "new\n")
        self.assertEqual(s.commit([self.topic], "blocked")["status"], "unknown")
        self.assertEqual((s.repo / self.topic).read_text(), "new\n")
        self.assertEqual(p.out(self.remote, "rev-parse", "main"), self.base)

    def test_lost_push_acknowledgment_recovers_without_duplicate_commit(self):
        s = self.session()
        self.snapshot(s)
        head = s.state["head"]
        real_git = p.git
        def lose_ack(repo, *args, **kwargs):
            result = real_git(repo, *args, **kwargs)
            if args[:1] == ("push",):
                return subprocess.CompletedProcess(result.args, 1, b"", b"connection lost")
            return result
        with patch.object(p, "git", side_effect=lose_ack):
            self.assertEqual(s.publish()["status"], "published")
        self.assertEqual(s.state["head"], head)

    def test_repeated_blocked_attempts_do_not_add_commits(self):
        s = self.session()
        self.snapshot(s)
        head = s.state["head"]
        self.advance()
        for unused in range(3):
            self.assertEqual(s.publish(mode="no-merge")["status"], "pending")
        self.assertEqual(p.out(s.repo, "rev-parse", "HEAD"), head)

    def test_nonconflicting_remote_change_merges_then_publishes(self):
        s = self.session()
        self.snapshot(s)
        self.advance()
        self.assertEqual(s.publish()["status"], "published")
        self.assertEqual(len(p.out(s.repo, "rev-list", "--parents", "-n", "1", "HEAD").split()), 3)

    def test_unrelated_work_in_private_session_prevents_push(self):
        s = self.session()
        self.snapshot(s)
        self.write(s.repo, "extra", "not in snapshot\n")
        self.assertEqual(s.publish()["status"], "pending")
        self.assertEqual(p.out(self.remote, "rev-parse", "main"), self.base)

    def test_commit_lock_never_gets_deleted_by_contender(self):
        s = self.session()
        with p.claim(s.lock):
            with self.assertRaisesRegex(p.Refused, "another command"):
                s.commit([self.topic], "blocked")
        self.assertTrue(s.lock.exists())
        self.assertEqual(p.out(s.repo, "rev-parse", "HEAD"), self.base)

    def test_bad_paths_refused_before_staging(self):
        for path in ("../outside", "agents", "/tmp/outside", "missing", ".git/config"):
            with self.subTest(path=path):
                s = self.session()
                with self.assertRaises(p.Refused):
                    s.commit([path], "invalid")
                self.assertFalse(p.git(s.repo, "diff", "--cached", "--name-only").stdout)

    def test_literal_magic_looking_filename_is_not_a_glob(self):
        s = self.session()
        self.snapshot(s, "[abc].md")
        self.assertEqual(s.publish()["status"], "published")
        self.assertEqual(p.out(self.remote, "show", "main:[abc].md"), "session")

    def test_creation_deletion_modes_and_symlinks_survive(self):
        s = self.session()
        (s.repo / self.topic).unlink()
        self.write(s.repo, "run.sh", "#!/bin/sh\nexit 0\n")
        os.chmod(s.repo / "run.sh", 0o755)
        (s.repo / "link").symlink_to("run.sh")
        self.assertEqual(s.commit([self.topic, "run.sh", "link"], "fidelity")["status"], "pending")
        self.assertEqual(s.publish()["status"], "published")
        tree = p.out(self.remote, "ls-tree", "main")
        self.assertIn("100755", tree)
        self.assertIn("120000", tree)
        self.assertNotEqual(p.git(self.remote, "show", "main:" + self.topic, check=False).returncode, 0)

    def test_pending_snapshot_is_not_recommitted_on_retry(self):
        s = self.session()
        self.snapshot(s)
        with self.assertRaisesRegex(p.Refused, "retry the existing"):
            s.commit([self.topic], "duplicate")

    def test_preexisting_index_lock_is_never_removed(self):
        s = self.session()
        gitdir = Path(p.out(s.repo, "rev-parse", "--absolute-git-dir"))
        lock = gitdir / "index.lock"
        lock.write_text("another writer")
        self.write(s.repo, self.topic, "new\n")
        self.assertEqual(s.commit([self.topic], "blocked")["status"], "unknown")
        self.assertEqual(lock.read_text(), "another writer")


class Refresh(unittest.TestCase):
    def test_setup_required_uses_its_own_cooldown_without_success_stamp(self):
        state = dict(result="setup-required", last_attempt=100, consecutive_failures=9)
        self.assertFalse(p.refresh_due(state, 101, 900))
        self.assertTrue(p.refresh_due(state, 1000, 900))

    def test_ttl_zero_forces_refresh_even_after_failure(self):
        self.assertTrue(p.refresh_due(dict(result="failed", last_attempt=100,
                                          consecutive_failures=30), 100, 0))

    def test_failure_uses_exponential_backoff(self):
        state = dict(result="failed", last_success=1, last_attempt=10000, consecutive_failures=2)
        self.assertFalse(p.refresh_due(state, 11799, 10000))
        self.assertTrue(p.refresh_due(state, 11800, 10000))

    def test_missing_success_does_not_bypass_failure_backoff(self):
        self.assertFalse(p.refresh_due(dict(result="failed", last_attempt=100,
                                           consecutive_failures=1), 101, 900))

    def test_huge_invalid_negative_and_future_fields_are_bounded(self):
        self.assertFalse(p.refresh_due(dict(result="failed", last_attempt=100,
                                           consecutive_failures=10**100), 101, 900))
        for value in (None, "garbage", -10, float("inf")):
            self.assertTrue(p.refresh_due(dict(result="failed", last_attempt=100,
                                              consecutive_failures=value), 101, 900))
        self.assertTrue(p.refresh_due(dict(result="failed", last_attempt=999,
                                          consecutive_failures=1), 101, 900))
        for value in (float("nan"), float("inf"), True, 10**1000):
            self.assertTrue(p.refresh_due(dict(result="failed", last_attempt=value,
                                              consecutive_failures=1), 101, 900))

    def test_recent_success_suppresses_refresh(self):
        self.assertFalse(p.refresh_due(dict(result="ok", last_success=100), 101, 900))


if __name__ == "__main__":
    unittest.main()
