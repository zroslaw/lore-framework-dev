#!/usr/bin/env python3
"""Tests for the Being Keeper (lore-framework/scripts/lrb.py).

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only
(unittest), matching test_wait.py. The plugin under test is located via
$LR_FRAMEWORK_DIR, defaulting to the sibling ../lore-framework.

All state (LRB_HOME, workspaces) is confined to per-test tempdirs — nothing
here touches the real machine's ~/.lore-beings or ~/Library/LaunchAgents.

Run:  python3 tests/test_lrb.py -v
  or: python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from datetime import datetime, timedelta, date

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
LRB = os.path.join(FRAMEWORK_DIR, "scripts", "lrb.py")
STUB = os.path.join(os.path.dirname(__file__), "fixtures", "stub_engine.py")


def load_lrb_module():
    spec = importlib.util.spec_from_file_location("lrb", LRB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lrb = load_lrb_module()


BEING_MD = """---
description: Being definition for testbeing
engine: stub
model: stub-model
daily-usd: {daily_usd}
existential-tasks:
  - name: morning-wakeup
    schedule: "{schedule}"
    prompt: task.md
    timeout-minutes: 1
---

# Being — testbeing

Test fixture being.
"""


class LrbTestCase(unittest.TestCase):
    """Base: sandboxes LRB_HOME/LRB_LAUNCHAGENTS_DIR and builds a throwaway
    workspace with one discoverable being backed by the stub engine."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lrb-test-")
        self.home = os.path.join(self.tmp, "home")
        self.launchagents = os.path.join(self.tmp, "launchagents")
        os.environ["LRB_HOME"] = self.home
        os.environ["LRB_LAUNCHAGENTS_DIR"] = self.launchagents
        for k in ("STUB_COST", "STUB_IS_ERROR", "STUB_SLEEP_SECONDS", "STUB_RESULT_TEXT", "STUB_CRASH"):
            os.environ.pop(k, None)
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        for k in ("LRB_HOME", "LRB_LAUNCHAGENTS_DIR", "STUB_COST", "STUB_IS_ERROR",
                  "STUB_SLEEP_SECONDS", "STUB_RESULT_TEXT", "STUB_CRASH"):
            os.environ.pop(k, None)

    NEVER_SCHEDULE = "0 0 1 1 *"  # Jan 1 00:00 — effectively never due during a test run

    @staticmethod
    def this_minute_cron():
        """A cron matching only the current machine-local minute, so a task
        fires on the very next tick without being misclassified as
        'late' (which compares against the day's first occurrence — see
        next_occurrence_for_date; a wide-open '* * * * *' would spuriously
        read as hours-late since its first daily occurrence is midnight)."""
        now = datetime.now()
        return "%d %d * * *" % (now.minute, now.hour)

    def make_being(self, repo="testrepo", agent="testbeing", daily_usd=1.0, schedule=None,
                    task_text="Do the test task."):
        if schedule is None:
            schedule = self.NEVER_SCHEDULE
        repo_dir = os.path.join(self.workspace, repo)
        agent_dir = os.path.join(repo_dir, "agents", agent)
        os.makedirs(agent_dir, exist_ok=True)
        with open(os.path.join(repo_dir, "lore-repo.md"), "w") as f:
            f.write("---\ndescription: test\nversion: \"1\"\n---\n")
        with open(os.path.join(agent_dir, "being.md"), "w") as f:
            f.write(BEING_MD.format(daily_usd=daily_usd, schedule=schedule))
        with open(os.path.join(agent_dir, "task.md"), "w") as f:
            f.write(task_text)
        return "%s/%s" % (repo, agent)

    def cfg(self):
        return {
            "workspaces": [self.workspace],
            "engines": {"stub": {"command": STUB, "permission_mode": "default"}},
        }


class TestFrontmatter(unittest.TestCase):
    def test_parse_flat_scalars(self):
        fm = lrb.parse_yaml_frontmatter('description: hello world\nengine: claude\ndaily-usd: 1.5\n')
        self.assertEqual(fm["description"], "hello world")
        self.assertEqual(fm["engine"], "claude")
        self.assertEqual(fm["daily-usd"], 1.5)

    def test_parse_quoted_scalar(self):
        fm = lrb.parse_yaml_frontmatter('schedule: "30 8 * * *"\n')
        self.assertEqual(fm["schedule"], "30 8 * * *")

    def test_parse_list_of_mappings(self):
        text = textwrap.dedent("""\
            existential-tasks:
              - name: morning-wakeup
                schedule: "30 8 * * *"
                prompt: being/morning-wakeup.md
                timeout-minutes: 15
              - name: evening
                schedule: "0 20 * * *"
                prompt: being/evening.md
                timeout-minutes: 10
        """)
        fm = lrb.parse_yaml_frontmatter(text)
        tasks = fm["existential-tasks"]
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["name"], "morning-wakeup")
        self.assertEqual(tasks[0]["timeout-minutes"], 15)
        self.assertEqual(tasks[1]["schedule"], "0 20 * * *")

    def test_load_being_file_full(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w") as f:
                f.write(BEING_MD.format(daily_usd=1, schedule="30 8 * * *"))
            being = lrb.load_being_file(path)
            self.assertEqual(being["engine"], "stub")
            self.assertEqual(being["daily_usd"], 1.0)
            self.assertEqual(len(being["existential_tasks"]), 1)
            self.assertIn("Test fixture being.", being["body"])

    def test_load_being_file_missing_keys_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w") as f:
                f.write("---\ndescription: incomplete\n---\nbody\n")
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_load_being_file_missing_frontmatter_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w") as f:
                f.write("# not a being file\n")
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_load_being_file_extra_top_level_key_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            text = BEING_MD.format(daily_usd=1, schedule="30 8 * * *").replace(
                "daily-usd: 1", "daily-usd: 1\ntimezone: Asia/Bangkok")
            with open(path, "w") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_load_being_file_extra_task_key_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            text = BEING_MD.format(daily_usd=1, schedule="30 8 * * *").replace(
                "    timeout-minutes: 1", "    timeout-minutes: 1\n    retry: true")
            with open(path, "w") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_docs_example_with_inline_comments_parses_cleanly(self):
        # Regression test for H5: docs/beings.md's own being.md example uses
        # inline ' # comment' annotations on value lines (as does the design
        # draft). Verbatim from docs/beings.md's "The being descriptor"
        # section — the parser shipped with the docs must actually handle
        # the docs' own example, not silently corrupt it.
        text = textwrap.dedent("""\
            ---
            description: Being definition for chronicler
            engine: claude                # must be configured (`lrb engines add`)
            model: haiku                  # concrete model name for that engine
            daily-usd: 1                  # hard daily spend cap — the spawn gate
            existential-tasks:
              - name: morning-wakeup
                schedule: "30 8 * * *"    # cron, machine-local time
                prompt: being/morning-wakeup.md   # path inside this agent's directory
                timeout-minutes: 15       # wall-clock hard kill
            ---

            # Being — chronicler
            body text
        """)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            being = lrb.load_being_file(path)
        self.assertEqual(being["engine"], "claude")
        self.assertEqual(being["model"], "haiku")
        self.assertEqual(being["daily_usd"], 1.0)
        task = being["existential_tasks"][0]
        self.assertEqual(task["schedule"], "30 8 * * *")
        self.assertEqual(task["prompt"], "being/morning-wakeup.md")
        self.assertEqual(task["timeout-minutes"], 15)

    def test_bad_schedule_syntax_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w") as f:
                f.write(BEING_MD.format(daily_usd=1, schedule="junk"))
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_bad_timeout_minutes_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            text = BEING_MD.format(daily_usd=1, schedule="30 8 * * *").replace(
                "timeout-minutes: 1", "timeout-minutes: abc")
            with open(path, "w") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_bad_timeout_minutes_bounds_raise(self):
        for timeout in ("0", str(lrb.MAX_TIMEOUT_MINUTES + 1)):
            with self.subTest(timeout=timeout), tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "being.md")
                text = BEING_MD.format(daily_usd=1, schedule="30 8 * * *").replace(
                    "timeout-minutes: 1", "timeout-minutes: %s" % timeout)
                with open(path, "w") as f:
                    f.write(text)
                with self.assertRaises(ValueError):
                    lrb.load_being_file(path)

    def test_bad_daily_usd_raises(self):
        for daily_usd in ("-1", "nan", "inf"):
            with self.subTest(daily_usd=daily_usd), tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "being.md")
                with open(path, "w") as f:
                    f.write(BEING_MD.format(daily_usd=daily_usd, schedule="30 8 * * *"))
                with self.assertRaises(ValueError):
                    lrb.load_being_file(path)

    def test_bad_task_name_raises(self):
        for name in ("../escape", "/tmp/escape", "bad name"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "being.md")
                text = BEING_MD.format(daily_usd=1, schedule="30 8 * * *").replace(
                    "  - name: morning-wakeup", "  - name: %s" % name)
                with open(path, "w") as f:
                    f.write(text)
                with self.assertRaises(ValueError):
                    lrb.load_being_file(path)

    def test_multi_occurrence_schedule_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w") as f:
                f.write(BEING_MD.format(daily_usd=1, schedule="0 9,21 * * *"))
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_garbage_after_valid_comma_part_rejected(self):
        # Regression test for cycle-2 M-NEW1: _cron_field_matches
        # short-circuits on the first matching comma-part, so a single-value
        # syntax probe (e.g. only checking value=1) never reaches "junk" in
        # "1,junk" — it matches "1" immediately. The day/month/weekday
        # syntax check must probe the FULL legal range so some value falls
        # through to every part.
        for schedule in ("30 8 1,junk * *", "30 8 * 1,junk *", "30 8 * * 1,junk"):
            with tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "being.md")
                with open(path, "w") as f:
                    f.write(BEING_MD.format(daily_usd=1, schedule=schedule))
                with self.assertRaises(ValueError, msg=schedule):
                    lrb.load_being_file(path)

    def test_zero_step_rejected_as_valueerror(self):
        # */0 must raise ValueError (a config error), not ZeroDivisionError.
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "being.md")
            with open(path, "w") as f:
                f.write(BEING_MD.format(daily_usd=1, schedule="*/0 8 * * *"))
            with self.assertRaises(ValueError):
                lrb.load_being_file(path)

    def test_cron_out_of_range_and_reversed_fields_rejected(self):
        for schedule in ("60 8 * * *", "0 24 * * *", "0 8 * * 7", "0 9-8 * * *"):
            with self.subTest(schedule=schedule), tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "being.md")
                with open(path, "w") as f:
                    f.write(BEING_MD.format(daily_usd=1, schedule=schedule))
                with self.assertRaises(ValueError):
                    lrb.load_being_file(path)


class TestCron(unittest.TestCase):
    def test_exact_match(self):
        dt = datetime(2026, 7, 19, 8, 30)
        self.assertTrue(lrb.cron_matches("30 8 * * *", dt))
        self.assertFalse(lrb.cron_matches("31 8 * * *", dt))

    def test_star_and_list(self):
        dt = datetime(2026, 7, 19, 14, 5)
        self.assertTrue(lrb.cron_matches("5,10,15 * * * *", dt))
        self.assertFalse(lrb.cron_matches("6,10,15 * * * *", dt))

    def test_range_and_step(self):
        dt = datetime(2026, 7, 19, 14, 20)
        self.assertTrue(lrb.cron_matches("*/10 9-17 * * *", dt))
        dt2 = datetime(2026, 7, 19, 14, 21)
        self.assertFalse(lrb.cron_matches("*/10 9-17 * * *", dt2))
        dt3 = datetime(2026, 7, 19, 20, 20)
        self.assertFalse(lrb.cron_matches("*/10 9-17 * * *", dt3))

    def test_weekday_field(self):
        # 2026-07-19 is a Sunday (cron weekday 0)
        sunday = datetime(2026, 7, 19, 9, 0)
        monday = datetime(2026, 7, 20, 9, 0)
        self.assertTrue(lrb.cron_matches("0 9 * * 0", sunday))
        self.assertFalse(lrb.cron_matches("0 9 * * 0", monday))
        self.assertTrue(lrb.cron_matches("0 9 * * 1", monday))

    def test_bad_expression_raises(self):
        with self.assertRaises(ValueError):
            lrb.cron_matches("bad expr", datetime.now())

    def test_next_occurrence_for_date(self):
        d = date(2026, 7, 19)
        occ = lrb.next_occurrence_for_date("30 8 * * *", d)
        self.assertEqual(occ, datetime(2026, 7, 19, 8, 30))

    def test_next_occurrence_none_when_weekday_excluded(self):
        # 2026-07-19 is Sunday; weekday field 1-5 (Mon-Fri) never matches it
        d = date(2026, 7, 19)
        occ = lrb.next_occurrence_for_date("0 9 * * 1-5", d)
        self.assertIsNone(occ)


class TestDiscovery(LrbTestCase):
    def test_discover_finds_valid_being(self):
        being_id = self.make_being()
        beings, errors = lrb.discover_beings(self.workspace)
        self.assertIn(being_id, beings)
        self.assertEqual(errors, {})
        self.assertEqual(beings[being_id]["engine"], "stub")

    def test_discover_reports_config_error_without_crashing(self):
        good_id = self.make_being(repo="goodrepo", agent="good")
        bad_dir = os.path.join(self.workspace, "badrepo", "agents", "bad")
        os.makedirs(bad_dir, exist_ok=True)
        with open(os.path.join(self.workspace, "badrepo", "lore-repo.md"), "w") as f:
            f.write("---\ndescription: bad\nversion: \"1\"\n---\n")
        with open(os.path.join(bad_dir, "being.md"), "w") as f:
            f.write("---\ndescription: broken\n---\nno other keys\n")
        beings, errors = lrb.discover_beings(self.workspace)
        self.assertIn(good_id, beings)
        self.assertIn("badrepo/bad", errors)

    def test_discover_rejects_prompt_path_escape(self):
        for prompt_path in ("../outside.md", "/tmp/outside.md"):
            with self.subTest(prompt_path=prompt_path):
                shutil.rmtree(self.workspace)
                os.makedirs(self.workspace)
                being_id = self.make_being(task_text="safe")
                agent_dir = os.path.join(self.workspace, "testrepo", "agents", "testbeing")
                with open(os.path.join(agent_dir, "being.md"), "w") as f:
                    f.write(BEING_MD.format(daily_usd=1, schedule=self.NEVER_SCHEDULE).replace(
                        "prompt: task.md", "prompt: %s" % prompt_path))
                beings, errors = lrb.discover_beings(self.workspace)
                self.assertNotIn(being_id, beings)
                self.assertIn(being_id, errors)

    def test_discover_ignores_dirs_without_lore_repo_md(self):
        os.makedirs(os.path.join(self.workspace, "not-a-repo", "agents", "x"), exist_ok=True)
        beings, errors = lrb.discover_beings(self.workspace)
        self.assertEqual(beings, {})
        self.assertEqual(errors, {})


class TestOutboxValidation(LrbTestCase):
    def test_accepts_valid_request(self):
        being_id = self.make_being()
        beings, _ = lrb.discover_beings(self.workspace)
        state = lrb.default_state()
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, being_id, (now + timedelta(hours=1)).isoformat(timespec="seconds"),
                                  10, "do it")
        lrb.process_outbox(self.workspace, beings, state, now)
        accepted = os.listdir(lrb.outbox_accepted_dir(self.workspace))
        self.assertEqual(len(accepted), 1)
        self.assertEqual(os.listdir(lrb.outbox_rejected_dir(self.workspace)), [])

    def test_rejects_unknown_being(self):
        beings = {}
        state = lrb.default_state()
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, "nobody/here", (now + timedelta(hours=1)).isoformat(timespec="seconds"),
                                  10, "do it")
        lrb.process_outbox(self.workspace, beings, state, now)
        rejected = os.listdir(lrb.outbox_rejected_dir(self.workspace))
        self.assertEqual(len(rejected), 1)
        with open(os.path.join(lrb.outbox_rejected_dir(self.workspace), rejected[0])) as f:
            req = json.load(f)
        self.assertIn("unknown being", req["rejected_reason"])

    def test_rejects_beyond_24h_horizon(self):
        being_id = self.make_being()
        beings, _ = lrb.discover_beings(self.workspace)
        state = lrb.default_state()
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, being_id, (now + timedelta(hours=30)).isoformat(timespec="seconds"),
                                  10, "too far out")
        lrb.process_outbox(self.workspace, beings, state, now)
        rejected = os.listdir(lrb.outbox_rejected_dir(self.workspace))
        self.assertEqual(len(rejected), 1)

    def test_rejects_when_budget_exhausted(self):
        being_id = self.make_being(daily_usd=0.01)
        beings, _ = lrb.discover_beings(self.workspace)
        state = lrb.default_state()
        lrb.being_state(state, being_id)["spent_today_usd"] = 0.02
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, being_id, (now + timedelta(hours=1)).isoformat(timespec="seconds"),
                                  10, "over budget")
        lrb.process_outbox(self.workspace, beings, state, now)
        rejected = os.listdir(lrb.outbox_rejected_dir(self.workspace))
        self.assertEqual(len(rejected), 1)
        with open(os.path.join(lrb.outbox_rejected_dir(self.workspace), rejected[0])) as f:
            req = json.load(f)
        self.assertIn("budget", req["rejected_reason"])

    def test_rejects_timezone_aware_at(self):
        being_id = self.make_being()
        beings, _ = lrb.discover_beings(self.workspace)
        state = lrb.default_state()
        lrb.write_outbox_request(self.workspace, being_id, "2026-07-19T15:00:00+07:00", 10, "do it")
        lrb.process_outbox(self.workspace, beings, state, datetime.now())
        rejected = os.listdir(lrb.outbox_rejected_dir(self.workspace))
        self.assertEqual(len(rejected), 1)
        with open(os.path.join(lrb.outbox_rejected_dir(self.workspace), rejected[0])) as f:
            req = json.load(f)
        self.assertIn("without a timezone", req["rejected_reason"])

    def test_rejects_bad_timeout_minutes(self):
        being_id = self.make_being()
        beings, _ = lrb.discover_beings(self.workspace)
        state = lrb.default_state()
        now = datetime.now()
        for timeout in (0, lrb.MAX_TIMEOUT_MINUTES + 1, "abc"):
            with self.subTest(timeout=timeout):
                lrb.write_outbox_request(self.workspace, being_id,
                                          (now + timedelta(hours=1)).isoformat(timespec="seconds"),
                                          timeout, "do it")
                lrb.process_outbox(self.workspace, beings, state, now)
        self.assertEqual(len(os.listdir(lrb.outbox_rejected_dir(self.workspace))), 3)


class TestKeeperIntegration(LrbTestCase):
    """Drives the real Keeper.tick() loop against the stub engine — real
    subprocesses, real files, zero API cost."""

    def _wait_until(self, predicate, timeout=5.0, interval=0.1):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(interval)
        return predicate()

    def _terminate_keeper_children(self, keeper):
        for proc in list(keeper.live_procs.values()):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
        keeper.live_procs.clear()

    def test_existential_task_fires_and_ledger_records_cost(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_COST"] = "0.05"
        keeper = lrb.Keeper()
        cfg = self.cfg()

        keeper.tick(cfg)  # tick 1: fires the existential task (due this minute)
        state = lrb.load_state(self.workspace)
        bstate = state["beings"][being_id]
        self.assertEqual(len(bstate["running"]), 1)
        self.assertIn("morning-wakeup", bstate["last_runs"])

        ledger = lrb.ledger_path(self.workspace, being_id)
        self.assertTrue(self._wait_until(lambda: os.path.exists(ledger)))

        def finished():
            keeper.tick(cfg)
            st = lrb.load_state(self.workspace)
            return len(st["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(finished, timeout=10))
        state = lrb.load_state(self.workspace)
        self.assertAlmostEqual(state["beings"][being_id]["spent_today_usd"], 0.05, places=4)

        with open(ledger) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        outcomes = [l["outcome"] for l in lines]
        self.assertIn("spawned", outcomes)
        self.assertIn("ok", outcomes)

    def test_existential_task_does_not_refire_same_day(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        keeper = lrb.Keeper()
        cfg = self.cfg()
        keeper.tick(cfg)
        time.sleep(0.3)  # let the (near-instant) stub subprocess actually exit before the next tick reaps it
        keeper.tick(cfg)  # reaps the first
        state_after_first = lrb.load_state(self.workspace)
        first_last_run = state_after_first["beings"][being_id]["last_runs"]["morning-wakeup"]

        keeper.tick(cfg)  # would fire again if same-day guard were broken
        state = lrb.load_state(self.workspace)
        self.assertEqual(state["beings"][being_id]["last_runs"]["morning-wakeup"], first_last_run)
        self.assertEqual(len(state["beings"][being_id]["running"]), 0)

    def test_error_result_recorded_as_error_outcome(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_IS_ERROR"] = "1"
        keeper = lrb.Keeper()
        cfg = self.cfg()
        keeper.tick(cfg)

        def finished():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(finished, timeout=10))
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("error", [l["outcome"] for l in lines])

    def test_invalid_result_cost_does_not_poison_budget(self):
        for i, cost in enumerate(("-1", "nan")):
            with self.subTest(cost=cost):
                being_id = self.make_being(
                    repo="costrepo%d" % i, agent="costbeing%d" % i,
                    daily_usd=1.0, schedule=self.this_minute_cron())
                os.environ["STUB_COST"] = cost
                keeper = lrb.Keeper()
                cfg = self.cfg()
                keeper.tick(cfg)

                def finished():
                    keeper.tick(cfg)
                    return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

                self.assertTrue(self._wait_until(finished, timeout=10))
                state = lrb.load_state(self.workspace)
                self.assertEqual(state["beings"][being_id]["spent_today_usd"], 0.0)
                with open(lrb.ledger_path(self.workspace, being_id)) as f:
                    lines = [json.loads(l) for l in f if l.strip()]
                self.assertIn("invalid-cost", [l["outcome"] for l in lines])

    def test_hard_crash_with_no_output_recorded_as_crashed(self):
        # STUB_CRASH writes nothing to stdout or stderr and exits 1 — the
        # true "no output at all" crash path.
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_CRASH"] = "1"
        keeper = lrb.Keeper()
        cfg = self.cfg()
        keeper.tick(cfg)

        def finished():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(finished, timeout=10))
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("crashed", [l["outcome"] for l in lines])
        self.assertEqual(lrb.load_state(self.workspace)["beings"][being_id]["spent_today_usd"], 0.0)

    def test_stderr_noise_does_not_break_cost_capture(self):
        # Regression test for H2: stdout used to be merged with stderr, so
        # ANY stderr noise (a CLI update notice, a warning) made the
        # whole-file JSON parse fail -> cost read as $0.00 -> the daily
        # budget cap silently never trips. stderr now goes to a sibling
        # file; this proves a noisy-but-successful engine still bills
        # correctly.
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_STDERR_NOISE"] = "1"
        os.environ["STUB_COST"] = "0.07"
        keeper = lrb.Keeper()
        cfg = self.cfg()
        keeper.tick(cfg)

        def finished():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(finished, timeout=10))
        state = lrb.load_state(self.workspace)
        self.assertAlmostEqual(state["beings"][being_id]["spent_today_usd"], 0.07, places=4)
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("ok", [l["outcome"] for l in lines])
        stderr_logs = [l for l in os.listdir(os.path.dirname(lrb.ledger_path(self.workspace, being_id)))
                        if l.endswith(".stderr.log")]
        self.assertEqual(len(stderr_logs), 1)  # the noise landed in its own file, not the JSON log

    def test_garbage_stdout_recorded_as_unparseable(self):
        # Genuine non-JSON content on stdout itself (not stderr noise) is a
        # distinct, real "unparseable" case.
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_RESULT_TEXT"] = "ok"
        # Sabotage by pointing the engine at a script that prints garbage.
        garbage = os.path.join(self.tmp, "garbage_engine.py")
        with open(garbage, "w") as f:
            f.write("#!/usr/bin/env python3\nimport sys\n"
                     "if '--version' in sys.argv:\n    print('garbage 1.0')\nelse:\n    print('not json')\n")
        os.chmod(garbage, 0o755)
        cfg = self.cfg()
        cfg["engines"]["stub"]["command"] = garbage
        keeper = lrb.Keeper()
        keeper.tick(cfg)

        def finished():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(finished, timeout=10))
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("unparseable", [l["outcome"] for l in lines])

    def test_missing_engine_binary_fails_to_spawn_without_crashing_tick(self):
        # A configured engine whose binary went missing/broke after `engines
        # add` must not raise out of spawn_session and take the whole tick
        # loop down with it (regression: this used to be an unguarded
        # subprocess.Popen call).
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        cfg = self.cfg()
        cfg["engines"]["stub"]["command"] = os.path.join(self.tmp, "does-not-exist")
        keeper = lrb.Keeper()
        keeper.tick(cfg)  # must not raise
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"][being_id]["running"]), 0)  # never entered running
        self.assertIn("morning-wakeup", state["beings"][being_id]["last_runs"])  # no retry storm
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("failed-to-spawn", [l["outcome"] for l in lines])

    def test_outbox_self_schedule_full_path(self):
        being_id = self.make_being(daily_usd=1.0)
        keeper = lrb.Keeper()
        cfg = self.cfg()
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, being_id, now.isoformat(timespec="seconds"), 1, "one-shot work")

        keeper.tick(cfg)  # validates -> accepted, spawns AND moves to done/ within the same tick
        new_files = [d for d in os.listdir(lrb.outbox_new_dir(self.workspace))
                     if d not in ("accepted", "rejected", "done")]
        self.assertEqual(new_files, [])  # the request moved out of new/
        done_dir = lrb.outbox_done_dir(self.workspace)
        self.assertEqual(len(os.listdir(done_dir)), 1)  # moved to done/ at spawn time, not at finish

        def finished():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(finished, timeout=10))
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"][being_id]["running"]), 0)

    def test_stale_accepted_one_shot_is_dropped_not_fired_late(self):
        # Regression test for M1: spec says missed fires are dropped past
        # midnight for existential tasks; the same must hold for accepted
        # one-shots (a laptop closed over the request's own day must not
        # fire it days later against the wrong day's budget/prompt context).
        being_id = self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        yesterday = datetime.now() - timedelta(days=1)
        req = {
            "being": being_id, "at": yesterday.isoformat(timespec="seconds"),
            "timeout_minutes": 5, "prompt": "stale request",
            "requested_at": yesterday.isoformat(timespec="seconds"),
        }
        lrb.ensure_ws_dirs(self.workspace)
        lrb.atomic_write_json(os.path.join(lrb.outbox_accepted_dir(self.workspace), "stale.json"), req)

        keeper = lrb.Keeper()
        keeper.tick(self.cfg())
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"].get(being_id, {}).get("running", [])), 0)  # never spawned
        self.assertEqual(os.listdir(lrb.outbox_accepted_dir(self.workspace)), [])  # no longer pending
        self.assertEqual(len(os.listdir(lrb.outbox_done_dir(self.workspace))), 1)
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("missed", [l["outcome"] for l in lines])

    def test_unparseable_at_fails_safe_not_immediately(self):
        # Regression test for M1: an unparseable 'at' used to default to
        # "now", firing the request immediately instead of erroring visibly
        # — the wrong failure direction for a scheduling bug.
        being_id = self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        req = {
            "being": being_id, "at": "not-a-real-timestamp",
            "timeout_minutes": 5, "prompt": "malformed request",
            "requested_at": datetime.now().isoformat(timespec="seconds"),
        }
        lrb.ensure_ws_dirs(self.workspace)
        lrb.atomic_write_json(os.path.join(lrb.outbox_accepted_dir(self.workspace), "bad.json"), req)

        keeper = lrb.Keeper()
        keeper.tick(self.cfg())
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"].get(being_id, {}).get("running", [])), 0)  # NOT fired
        self.assertEqual(os.listdir(lrb.outbox_accepted_dir(self.workspace)), [])
        self.assertEqual(len(os.listdir(lrb.outbox_done_dir(self.workspace))), 1)

    def test_malformed_accepted_request_moves_to_done(self):
        lrb.ensure_ws_dirs(self.workspace)
        for name, req in {
            "missing-prompt.json": {"being": "x/y", "at": datetime.now().isoformat(timespec="seconds")},
            "not-object.json": ["not", "an", "object"],
        }.items():
            lrb.atomic_write_json(os.path.join(lrb.outbox_accepted_dir(self.workspace), name), req)
        keeper = lrb.Keeper()
        keeper.tick(self.cfg())
        self.assertEqual(os.listdir(lrb.outbox_accepted_dir(self.workspace)), [])
        self.assertEqual(len(os.listdir(lrb.outbox_done_dir(self.workspace))), 2)

    def test_budget_gate_blocks_spawn_once_cap_recorded(self):
        being_id = self.make_being(daily_usd=0.02)
        os.environ["STUB_COST"] = "0.05"  # first session alone blows the cap
        keeper = lrb.Keeper()
        cfg = self.cfg()
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, being_id, now.isoformat(timespec="seconds"), 1, "first")
        keeper.tick(cfg)  # accept + spawn #1

        def first_done():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(first_done, timeout=10))
        state = lrb.load_state(self.workspace)
        self.assertGreaterEqual(state["beings"][being_id]["spent_today_usd"], 0.02)

        lrb.write_outbox_request(self.workspace, being_id, now.isoformat(timespec="seconds"), 1, "second")
        keeper.tick(cfg)  # outbox validation itself rejects: budget already exhausted
        rejected = os.listdir(lrb.outbox_rejected_dir(self.workspace))
        self.assertEqual(len(rejected), 1)
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"][being_id]["running"]), 0)

    def test_timeout_kills_long_running_session(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_SLEEP_SECONDS"] = "30"
        keeper = lrb.Keeper()
        cfg = self.cfg()
        keeper.tick(cfg)
        state = lrb.load_state(self.workspace)
        entry = state["beings"][being_id]["running"][0]
        pid = entry["pid"]
        self.assertTrue(self._is_process_alive(pid))

        # Fast-forward: back-date "started" past the 1-minute timeout so the
        # very next tick's overdue check fires without a real 60s wait.
        entry["started"] = (datetime.now() - timedelta(minutes=5)).isoformat(timespec="seconds")
        lrb.save_state(self.workspace, state)

        keeper.tick(cfg)  # detects overdue, sends SIGTERM
        state = lrb.load_state(self.workspace)
        self.assertTrue(len(state["beings"][being_id]["running"]) == 1)
        self.assertIn("kill_sent_at", state["beings"][being_id]["running"][0])

        # The process is this Keeper instance's own child (tracked in
        # live_procs), so it stays a zombie — and still answers os.kill(pid,
        # 0) — until the Keeper itself reaps it via proc.poll() on a later
        # tick. Give the OS a moment to actually deliver/act on SIGTERM, then
        # let the Keeper reap it the normal way rather than polling raw PID
        # liveness from outside (which would never observe a same-process
        # zombie's death).
        time.sleep(0.3)

        def reaped():
            keeper.tick(cfg)
            return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

        self.assertTrue(self._wait_until(reaped, timeout=10))
        with open(lrb.ledger_path(self.workspace, being_id)) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertIn("timeout", [l["outcome"] for l in lines])

    def test_missed_fire_marked_on_rollover_and_todays_still_fires(self):
        # this_minute_cron() ("MM HH * * *") fires once/day at the same
        # clock time every day (day/month/weekday are all "*"), so it has a
        # real occurrence on both yesterday and today — unlike "* * * * *",
        # which is >1/day and now correctly rejected as a config error by
        # load_being_file's once-daily validation (M6).
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        state = lrb.default_state()
        state["date"] = (date.today() - timedelta(days=2)).isoformat()
        lrb.ensure_ws_dirs(self.workspace)
        lrb.save_state(self.workspace, state)

        keeper = lrb.Keeper()
        try:
            cfg = self.cfg()
            keeper.tick(cfg)  # rollover: date jumps to today, yesterday's occurrence marked missed

            with open(lrb.ledger_path(self.workspace, being_id)) as f:
                lines = [json.loads(l) for l in f if l.strip()]
            self.assertIn("missed", [l["outcome"] for l in lines])

            state = lrb.load_state(self.workspace)
            self.assertEqual(state["date"], date.today().isoformat())
            # today's own fire still happens in the same tick (this_minute_cron matches today too)
            self.assertEqual(len(state["beings"][being_id]["running"]), 1)
        finally:
            self._terminate_keeper_children(keeper)

    def test_rollover_missed_check_survives_a_bad_schedule(self):
        # Defense-in-depth regression test for cycle-2 M-NEW1: even if a bad
        # schedule somehow reaches this code path (bypassing
        # load_being_file's own validation — a future schema relaxation, a
        # direct construction like this test's), the rollover must not raise
        # and wedge the workspace's tick forever. Constructs the being dict
        # directly rather than through load_being_file, which is exactly the
        # validation this being's schedule would otherwise fail.
        beings = {
            "fake/being": {
                "existential_tasks": [
                    {"name": "bad-task", "schedule": "not a cron", "prompt": "x.md", "timeout-minutes": 5},
                ],
            },
        }
        state = lrb.default_state()
        keeper = lrb.Keeper()
        today = date.today()
        prev_date = today - timedelta(days=1)
        keeper._check_missed_from_prev_day(self.workspace, beings, state, prev_date, today)  # must not raise

    def test_daily_budget_resets_on_rollover(self):
        being_id = self.make_being(daily_usd=1.0)
        state = lrb.default_state()
        state["date"] = (date.today() - timedelta(days=1)).isoformat()
        lrb.being_state(state, being_id)["spent_today_usd"] = 0.9
        lrb.ensure_ws_dirs(self.workspace)
        lrb.save_state(self.workspace, state)

        keeper = lrb.Keeper()
        keeper.tick(self.cfg())
        state = lrb.load_state(self.workspace)
        self.assertEqual(state["beings"][being_id]["spent_today_usd"], 0.0)

    def test_session_started_before_midnight_does_not_charge_new_day(self):
        being_id = self.make_being(daily_usd=1.0)
        state = lrb.default_state()
        yesterday = date.today() - timedelta(days=1)
        state["date"] = yesterday.isoformat()
        lrb.ensure_ws_dirs(self.workspace)
        log_path = lrb.log_path_for(self.workspace, being_id, "morning-wakeup", datetime.now())
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w") as f:
            json.dump({"result": "ok", "total_cost_usd": 0.25, "is_error": False}, f)
        bstate = lrb.being_state(state, being_id)
        bstate["running"].append({
            "task": "morning-wakeup", "pid": 99999999,
            "started": datetime.combine(yesterday, datetime.min.time()).isoformat(timespec="seconds"),
            "timeout_minutes": 30, "log_path": log_path,
        })
        lrb.save_state(self.workspace, state)

        keeper = lrb.Keeper()
        keeper.tick(self.cfg())
        state = lrb.load_state(self.workspace)
        self.assertEqual(state["date"], date.today().isoformat())
        self.assertEqual(state["beings"][being_id]["spent_today_usd"], 0.0)

    def test_crash_recovery_reaping_of_re_adopted_pid(self):
        """Simulates a Keeper restart: a running entry with no live Popen
        handle in the new process. A real subprocess is used so pid liveness
        is genuine, not mocked."""
        being_id = self.make_being(daily_usd=1.0)
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.4)"])
        state = lrb.default_state()
        lrb.ensure_ws_dirs(self.workspace)
        log_path = lrb.log_path_for(self.workspace, being_id, "morning-wakeup", datetime.now())
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w") as f:
            json.dump({"result": "ok", "total_cost_usd": 0.03, "is_error": False}, f)
        bstate = lrb.being_state(state, being_id)
        bstate["running"].append({
            "task": "morning-wakeup", "pid": proc.pid,
            "started": datetime.now().isoformat(timespec="seconds"),
            "timeout_minutes": 30, "log_path": log_path,
        })
        lrb.save_state(self.workspace, state)

        keeper = lrb.Keeper()  # fresh instance: live_procs is empty, as after a restart
        keeper._poll_running(self.workspace, state, datetime.now())
        self.assertEqual(len(state["beings"][being_id]["running"]), 1)  # still alive

        proc.wait(timeout=5)
        self._wait_until(lambda: not self._is_process_alive(proc.pid), timeout=3)
        keeper._poll_running(self.workspace, state, datetime.now())
        self.assertEqual(len(state["beings"][being_id]["running"]), 0)
        self.assertAlmostEqual(bstate["spent_today_usd"], 0.03, places=4)

    def test_pause_blocks_all_spawning(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        now = datetime.now()
        lrb.write_outbox_request(self.workspace, being_id, now.isoformat(timespec="seconds"), 1, "one-shot")
        lrb.atomic_write_text(lrb.paused_path(), "")
        try:
            keeper = lrb.Keeper()
            keeper.tick(self.cfg())
            state = lrb.load_state(self.workspace)
            self.assertEqual(len(state["beings"].get(being_id, {}).get("running", [])), 0)
            self.assertEqual(state["beings"].get(being_id, {}).get("last_runs", {}), {})
            # the outbox request wasn't even validated while paused
            self.assertEqual(os.listdir(lrb.outbox_accepted_dir(self.workspace)), [])
        finally:
            os.unlink(lrb.paused_path())

    def test_concurrency_cap_limits_spawns_across_beings(self):
        id_a = self.make_being(repo="repoa", agent="a", daily_usd=1.0, schedule=self.this_minute_cron())
        id_b = self.make_being(repo="repob", agent="b", daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_SLEEP_SECONDS"] = "5"  # stay running long enough to count both attempts
        cfg = self.cfg()
        cfg["concurrency_cap"] = 1
        keeper = lrb.Keeper()
        try:
            keeper.tick(cfg)
            state = lrb.load_state(self.workspace)
            total_running = (len(state["beings"].get(id_a, {}).get("running", [])) +
                              len(state["beings"].get(id_b, {}).get("running", [])))
            self.assertEqual(total_running, 1)  # cap=1 across the whole tick, not per-being
        finally:
            self._terminate_keeper_children(keeper)

    def test_existential_task_budget_gate_blocks_spawn(self):
        being_id = self.make_being(daily_usd=0.01, schedule=self.this_minute_cron())
        state = lrb.default_state()
        lrb.being_state(state, being_id)["spent_today_usd"] = 0.02  # already over the cap
        lrb.ensure_ws_dirs(self.workspace)
        lrb.save_state(self.workspace, state)
        keeper = lrb.Keeper()
        keeper.tick(self.cfg())
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"][being_id]["running"]), 0)
        self.assertEqual(state["beings"][being_id]["last_runs"], {})  # never fired at all

    def test_sigkill_after_grace_period_when_sigterm_is_ignored(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.this_minute_cron())
        os.environ["STUB_IGNORE_SIGTERM"] = "1"
        os.environ["STUB_SLEEP_SECONDS"] = "30"
        # lrb is the dynamically-loaded module object (see load_lrb_module at
        # module scope) — a plain attribute set, not a real re-import.
        original_grace = lrb.KILL_GRACE_SECONDS
        lrb.KILL_GRACE_SECONDS = 0.2  # real grace is 60s; shrink it so this test stays fast
        try:
            keeper = lrb.Keeper()
            cfg = self.cfg()
            keeper.tick(cfg)
            state = lrb.load_state(self.workspace)
            entry = state["beings"][being_id]["running"][0]
            pid = entry["pid"]
            entry["started"] = (datetime.now() - timedelta(minutes=5)).isoformat(timespec="seconds")
            lrb.save_state(self.workspace, state)

            keeper.tick(cfg)  # overdue -> SIGTERM (ignored by the stub)
            state = lrb.load_state(self.workspace)
            self.assertEqual(len(state["beings"][being_id]["running"]), 1)
            self.assertTrue(self._is_process_alive(pid))  # SIGTERM was ignored, still alive

            time.sleep(0.3)  # past the shrunk grace period
            keeper.tick(cfg)  # SIGKILL — cannot be ignored

            def reaped():
                keeper.tick(cfg)
                return len(lrb.load_state(self.workspace)["beings"][being_id]["running"]) == 0

            self.assertTrue(self._wait_until(reaped, timeout=10))
            self.assertFalse(self._is_process_alive(pid))
            with open(lrb.ledger_path(self.workspace, being_id)) as f:
                lines = [json.loads(l) for l in f if l.strip()]
            self.assertIn("timeout", [l["outcome"] for l in lines])
        finally:
            lrb.KILL_GRACE_SECONDS = original_grace

    def test_pid_reuse_does_not_signal_the_wrong_process(self):
        # Regression test for H1: a re-adopted running entry (no live Popen
        # handle — as after a Keeper restart) whose recorded pid is alive
        # but belongs to a DIFFERENT command than what was spawned must be
        # treated as dead, never signaled. Uses this test process's own pid
        # (genuinely alive) with a deliberately wrong recorded "command".
        being_id = self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        state = lrb.default_state()
        bstate = lrb.being_state(state, being_id)
        impersonated_pid = os.getpid()  # this test process: definitely alive
        entry = {
            "task": "morning-wakeup", "pid": impersonated_pid,
            "started": datetime.now().isoformat(timespec="seconds"),
            "timeout_minutes": 30, "log_path": os.path.join(self.tmp, "nonexistent.log"),
            "command": "/definitely/not/this/test/process",
            "process_start": (lrb._pid_identity(impersonated_pid) or {}).get("start"),
        }
        bstate["running"].append(entry)
        lrb.ensure_ws_dirs(self.workspace)
        lrb.save_state(self.workspace, state)

        keeper = lrb.Keeper()  # fresh: impersonated_pid is not in live_procs
        keeper._poll_running(self.workspace, state, datetime.now())
        # When ps is available, a confirmed identity mismatch is treated as
        # dead and reaped. In restricted sandboxes (Codex), ps can be blocked;
        # then the Keeper cannot prove mismatch, so it keeps the stale entry
        # visible but still must not signal it. Judge via the saved `entry`
        # reference — on the reaped path bstate["running"] is already empty.
        if lrb._pid_matches_entry(impersonated_pid, entry) is None:
            self.assertEqual(len(state["beings"][being_id]["running"]), 1)
        else:
            self.assertEqual(len(state["beings"][being_id]["running"]), 0)
        self.assertTrue(self._is_process_alive(impersonated_pid))  # and, critically, still alive

    def test_pid_reuse_check_recognizes_a_genuine_match(self):
        # Companion to the test above: a re-adopted entry whose recorded
        # "command" DOES genuinely match the running process must be kept as
        # running, not lost. Uses a real subprocess of the actual stub
        # engine (the same shape every configured engine takes: a script
        # invoked by path, possibly through shebang resolution) rather than
        # a synthetic command string, since the exact ps-output shape is
        # what the identity check depends on.
        being_id = self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        os.environ["STUB_SLEEP_SECONDS"] = "3"
        proc = subprocess.Popen([STUB, "-p", "hi", "--output-format", "json", "--model", "x"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            state = lrb.default_state()
            bstate = lrb.being_state(state, being_id)
            bstate["running"].append({
                "task": "morning-wakeup", "pid": proc.pid,
                "started": datetime.now().isoformat(timespec="seconds"),
                "timeout_minutes": 30, "log_path": os.path.join(self.tmp, "nonexistent.log"),
                "command": STUB,  # the genuinely correct command
                "process_start": (lrb._pid_identity(proc.pid) or {}).get("start"),
            })
            lrb.ensure_ws_dirs(self.workspace)
            lrb.save_state(self.workspace, state)

            keeper = lrb.Keeper()  # fresh: proc.pid is not in live_procs, forcing the identity-check path
            keeper._poll_running(self.workspace, state, datetime.now())
            self.assertEqual(len(state["beings"][being_id]["running"]), 1)  # correctly recognized as alive
        finally:
            proc.terminate()
            proc.wait(timeout=5)

    def test_unverified_readopted_pid_is_not_signaled_when_overdue(self):
        # If the OS/sandbox lets os.kill(pid, 0) prove that a re-adopted PID
        # is alive but blocks the command identity check, the Keeper must not
        # guess and signal it. It keeps the entry visible with an explicit
        # reason instead.
        being_id = self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        original = lrb._pid_matches_entry
        try:
            lrb._pid_matches_entry = lambda pid, entry: None
            state = lrb.default_state()
            bstate = lrb.being_state(state, being_id)
            bstate["running"].append({
                "task": "morning-wakeup", "pid": proc.pid,
                "started": (datetime.now() - timedelta(minutes=5)).isoformat(timespec="seconds"),
                "timeout_minutes": 1, "log_path": os.path.join(self.tmp, "nonexistent.log"),
                "command": "/unknown/because/ps/is/blocked",
            })
            keeper = lrb.Keeper()
            keeper._poll_running(self.workspace, state, datetime.now())
            running = state["beings"][being_id]["running"]
            self.assertEqual(len(running), 1)
            self.assertEqual(running[0]["kill_blocked_reason"], "pid identity check unavailable")
            self.assertTrue(self._is_process_alive(proc.pid))
        finally:
            lrb._pid_matches_entry = original
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

    def test_reused_pid_with_same_command_but_different_start_is_not_signaled(self):
        being_id = self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        state = lrb.default_state()
        bstate = lrb.being_state(state, being_id)
        bstate["running"].append({
            "task": "morning-wakeup", "pid": os.getpid(),
            "started": (datetime.now() - timedelta(minutes=5)).isoformat(timespec="seconds"),
            "timeout_minutes": 1, "log_path": os.path.join(self.tmp, "nonexistent.log"),
            "command": STUB,
            "process_start": "Mon Jul 19 08:30:00 2026",
        })
        original = lrb._pid_identity
        try:
            lrb._pid_identity = lambda pid: {
                "command": "%s -p hi --output-format json --model x" % STUB,
                "start": "Mon Jul 19 08:31:00 2026",
            }
            keeper = lrb.Keeper()
            keeper._poll_running(self.workspace, state, datetime.now())
            self.assertEqual(len(state["beings"][being_id]["running"]), 0)
        finally:
            lrb._pid_identity = original

    @staticmethod
    def _is_process_alive(pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


class TestCliSubprocess(LrbTestCase):
    """A thin end-to-end slice through the actual `lrb` CLI as a subprocess,
    matching how a real being (or a human) invokes it — not just internal
    function calls."""

    def run_lrb(self, *args):
        env = dict(os.environ)
        return subprocess.run([sys.executable, LRB] + list(args), capture_output=True, text=True,
                               env=env, timeout=30)

    def test_install_is_sandboxed_and_idempotent(self):
        r = self.run_lrb("install")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.home, "lrb.py")))
        self.assertTrue(os.path.exists(os.path.join(self.launchagents, "com.lore-beings.keeper.plist")))
        real_launchagents = os.path.expanduser("~/Library/LaunchAgents/com.lore-beings.keeper.plist")
        self.assertFalse(os.path.exists(real_launchagents))

    def test_workspaces_and_engines_roundtrip(self):
        self.run_lrb("install")
        r = self.run_lrb("workspaces", "add", self.workspace)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_lrb("engines", "add", "stub", "--command", STUB)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_lrb("status", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertIn(os.path.realpath(self.workspace), out["workspaces"])

    def test_schedule_requires_registered_workspace(self):
        self.run_lrb("install")
        os.chdir(self.workspace)
        try:
            r = self.run_lrb("schedule", "--agent", "x/y", "--at", "2099-01-01T00:00:00", "hello")
        finally:
            os.chdir(FRAMEWORK_DIR if os.path.isdir(FRAMEWORK_DIR) else "/")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not a registered workspace", r.stderr)

    def test_schedule_rejects_timezone_and_bad_timeout(self):
        self.run_lrb("install")
        self.run_lrb("workspaces", "add", self.workspace)
        os.chdir(self.workspace)
        try:
            r = self.run_lrb("schedule", "--agent", "x/y", "--at", "2026-07-19T15:00:00+07:00", "hello")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("without a timezone", r.stderr)
            r = self.run_lrb("schedule", "--agent", "x/y", "--at", "2026-07-19T15:00:00",
                             "--timeout-minutes", "0", "hello")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("between 1", r.stderr)
        finally:
            os.chdir(FRAMEWORK_DIR if os.path.isdir(FRAMEWORK_DIR) else "/")

    def test_pause_resume(self):
        self.run_lrb("install")
        r = self.run_lrb("pause")
        self.assertEqual(r.returncode, 0)
        self.assertTrue(os.path.exists(lrb.paused_path()))
        r = self.run_lrb("resume")
        self.assertEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(lrb.paused_path()))

    def test_daemon_once(self):
        self.run_lrb("install")
        self.run_lrb("workspaces", "add", self.workspace)
        self.run_lrb("engines", "add", "stub", "--command", STUB)
        self.make_being(daily_usd=1.0)
        r = self.run_lrb("daemon", "--once")
        self.assertEqual(r.returncode, 0, r.stderr)
        state = lrb.load_state(self.workspace)
        self.assertEqual(len(state["beings"]), 1)

    def test_second_daemon_refuses_to_start_while_first_holds_the_lock(self):
        # Regression test for M4: two concurrent Keepers would double-spawn
        # due tasks and race on state.json's read-modify-write.
        self.run_lrb("install")
        self.run_lrb("workspaces", "add", self.workspace)
        self.run_lrb("engines", "add", "stub", "--command", STUB)
        self.make_being(daily_usd=1.0, schedule=self.NEVER_SCHEDULE)
        env = dict(os.environ)
        first = subprocess.Popen([sys.executable, LRB, "daemon"], env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 5
            lock_path = os.path.join(self.home, "daemon.lock")
            while time.time() < deadline and not os.path.exists(lock_path):
                time.sleep(0.05)
            time.sleep(0.2)  # flock is acquired a moment after the file is created; avoid a race
            second = self.run_lrb("daemon", "--once")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("already holds the lock", second.stderr)
        finally:
            first.terminate()
            try:
                first.wait(timeout=5)
            except subprocess.TimeoutExpired:
                first.kill()
                first.wait()
            if first.stdout:
                first.stdout.close()
            if first.stderr:
                first.stderr.close()

    def test_status_detects_a_running_daemon(self):
        # Regression test for L4: status must actually recognize a live
        # daemon (not just report the CLI's own version) — a prior version
        # of the self-identity check compared the daemon's own
        # sys.executable against `ps`, which can legitimately mismatch for
        # the very same process (macOS framework Python re-exec quirk) and
        # always read as "not detected".
        self.run_lrb("install")
        env = dict(os.environ)
        daemon_proc = subprocess.Popen([sys.executable, LRB, "daemon"], env=env,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            info_path = os.path.join(self.home, "daemon.info")
            deadline = time.time() + 5
            while time.time() < deadline and not os.path.exists(info_path):
                time.sleep(0.05)
            r = self.run_lrb("status", "--json")
            self.assertEqual(r.returncode, 0, r.stderr)
            out = json.loads(r.stdout)
            self.assertTrue(out["daemon"]["running"])
            self.assertEqual(out["daemon"]["pid"], daemon_proc.pid)
        finally:
            daemon_proc.terminate()
            try:
                daemon_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                daemon_proc.kill()
                daemon_proc.wait()
            if daemon_proc.stdout:
                daemon_proc.stdout.close()
            if daemon_proc.stderr:
                daemon_proc.stderr.close()


if __name__ == "__main__":
    unittest.main()
