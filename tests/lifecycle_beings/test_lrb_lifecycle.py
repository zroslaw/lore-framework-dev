#!/usr/bin/env python3
"""Being Keeper real-engine lifecycle scenarios (design: lore-architect
workdir/draft-lrb-lifecycle-tests.md).

11 of the design's 13 scenarios. B2/B3 (codex/cursor process-tree-kill
variants of B1) added 2026-07-20 — the killpg mechanism is engine-agnostic
in the Keeper's own code, but whether a given engine's OWN shell tool
actually spawns a real subprocess tree the same shape claude's Bash tool
does is an empirical question about THAT ENGINE, not provable from claude
coverage alone (see lore `lore-beings-mvp-takeover-review.md`). D2/D3
(codex/cursor PID-identity variants of D1) remain deferred: unlike B1's
killpg, `_pid_identity`'s `ps` call is pure OS-level process inspection —
it does not depend on which engine spawned the PID, so D1's claude proof is
the representative case there. Add D2/D3 only on a real incident.

Gated behind LR_LIFECYCLE_BEINGS=1 (separate from the framework's own
LR_LIFECYCLE=1 — see keeper_harness.py's module docstring for why). Costs real
API money and, for a few scenarios, briefly runs a real background process on
this machine (always torn down via KeeperFixture, even on assertion failure).

  LR_LIFECYCLE_BEINGS=1 LR_ENGINE=claude python3 tests/lifecycle_beings/test_lrb_lifecycle.py -v
  LR_LIFECYCLE_BEINGS=1 LR_ENGINE=codex  python3 tests/lifecycle_beings/test_lrb_lifecycle.py -v -k "a2 or b2"
  LR_LIFECYCLE_BEINGS=1 LR_ENGINE=cursor python3 tests/lifecycle_beings/test_lrb_lifecycle.py -v -k "a3 or b3"

LR_ENGINE selects which single engine's scenarios run, same convention as
every other file in this directory: claude-only scenarios (C1/C4/D1/E1)
skip cleanly under LR_ENGINE=codex or =cursor, and B2/B3 skip cleanly
outside their own engine the same way A2/A3 do.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_harness as kh  # noqa: E402


class TestCoreLoop(unittest.TestCase):
    """A1-A3: does the Keeper actually invoke each real engine correctly
    end-to-end (argv, headless flags, result capture, cost reporting) and
    does a full tick cycle (spawn -> run -> record result -> next tick)
    work? Not re-covered by the stub-engine suite by construction — a stub
    can't prove anything about a real engine's own contract."""

    def test_a1_core_loop_claude(self):
        reason = kh.skip_reason("claude")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            claude_bin = shutil.which("claude")
            wrapper = os.path.join(fx.tmp, "claude-wrapper.sh")
            kh.write_claude_wrapper(wrapper, claude_bin, kh.FRAMEWORK_DIR)
            codeword = "KEEPER-A1-CLAUDE-OK"
            task = (
                "Attempt the boot instructions above as best you can; if any step fails or a "
                "file is missing, note it briefly and move on. Regardless of outcome, end your "
                "final output message with exactly this line:\n%s\n" % codeword
            )
            being_id = fx.build_being(
                repo="a1repo", agent="a1being", engine="claude", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=3,
            )
            cfg = fx.write_config({
                "claude": {"command": wrapper, "kind": "claude", "permission_mode": "full"},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running") and bstate.get("last_runs")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished),
                             "A1: session did not finish within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "A1: no finished ledger entry")
            last = finished_lines[-1]
            kh.debug_dump("a1", last.get("log_path"))
            self.assertEqual(last["outcome"], "ok", "A1 outcome: %r" % last)
            self.assertIsInstance(last["cost_usd"], float)
            self.assertGreater(last["cost_usd"], 0.0)  # real total_cost_usd, not a stub's canned value

            state = kh.lrb.load_state(fx.workspace)
            self.assertAlmostEqual(state["beings"][being_id]["spent_today_usd"],
                                    last["cost_usd"], places=4)

            log_path = last["log_path"]
            with open(log_path, encoding="utf-8", errors="replace") as f:
                self.assertIn(codeword, f.read())
            self.assertTrue(os.path.exists(log_path + ".stderr.log"))  # sibling stderr file always created

            status = fx.run_lrb_cli(["status", "--json"])
            self.assertEqual(status.returncode, 0, status.stderr)
            payload = json.loads(status.stdout)
            b = payload["workspaces"][fx.workspace]["beings"][being_id]
            self.assertEqual(b["last_outcome"], "ok")
            self.assertTrue(b["log_dir"])

    def test_a2_core_loop_codex(self):
        reason = kh.skip_reason("codex")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            codex_bin = shutil.which("codex")
            codeword = "KEEPER-A2-CODEX-OK"
            task = (
                "Attempt the boot instructions above as best you can; if any step fails or a "
                "file/skill is missing, note it briefly and move on. Regardless of outcome, "
                "end your final output message with exactly this line:\n%s\n" % codeword
            )
            being_id = fx.build_being(
                repo="a2repo", agent="a2being", engine="codex", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=3,
            )
            cfg = fx.write_config({
                "codex": {"command": codex_bin, "kind": "codex", "permission_mode": "full",
                          "session_cost_usd": kh.CODEX_SESSION_COST_USD},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running") and bstate.get("last_runs")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished),
                             "A2: session did not finish within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "A2: no finished ledger entry")
            last = finished_lines[-1]
            kh.debug_dump("a2", last.get("log_path"))
            self.assertEqual(last["outcome"], "ok", "A2 outcome: %r" % last)
            # codex reports no USD itself — the flat session_cost_usd fallback must be charged
            # exactly, and real token usage must be present (JSONL turn.completed parsing).
            self.assertAlmostEqual(last["cost_usd"], kh.CODEX_SESSION_COST_USD, places=4)
            self.assertIn("usage", last)

            log_path = last["log_path"]
            with open(log_path, encoding="utf-8", errors="replace") as f:
                self.assertIn(codeword, f.read())
            # H2 regression, real codex: docs/beings.md documents codex writing spurious stderr
            # noise on successful runs — the sibling .stderr.log must exist and cost parsing
            # above must still have succeeded despite it (stdout/stderr are separate files).
            self.assertTrue(os.path.exists(log_path + ".stderr.log"))

    def test_a3_core_loop_cursor(self):
        reason = kh.skip_reason("cursor")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            cursor_bin = shutil.which("cursor-agent")
            codeword = "KEEPER-A3-CURSOR-OK"
            task = (
                "Attempt the boot instructions above as best you can; if any step fails or a "
                "file/skill is missing, note it briefly and move on. Regardless of outcome, "
                "end your final output message with exactly this line:\n%s\n" % codeword
            )
            being_id = fx.build_being(
                repo="a3repo", agent="a3being", engine="cursor", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=5,
            )
            # REAL FINDING (2026-07-20, real cursor-agent/composer-2.5): the live JSON result had
            # NO total_cost_usd field at all (only token usage) — contradicting the original
            # build's real-verification note that cursor reports real total_cost_usd. Per
            # spawn_session's own cursor-kind cost logic, that meant a cursor engine configured
            # WITHOUT session_cost_usd would silently charge $0.00 forever, never tripping the
            # daily budget cap — the same "prompt-theater" gap the code already prevented for
            # codex by dying at `engines add` time if --session-cost-usd is missing. FIXED
            # 2026-07-20: `cmd_engines_add` now requires --session-cost-usd for cursor too (see
            # docs/beings.md). This fixture still sets it explicitly (bypassing the CLI's own
            # `engines add` validation via write_config) so the scenario exercises the flat
            # fallback path regardless of CLI enforcement.
            cfg = fx.write_config({
                "cursor": {"command": cursor_bin, "kind": "cursor", "permission_mode": "full",
                           "plugin_dir": kh.FRAMEWORK_DIR, "session_cost_usd": kh.CODEX_SESSION_COST_USD},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running") and bstate.get("last_runs")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished),
                             "A3: session did not finish within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "A3: no finished ledger entry")
            last = finished_lines[-1]
            kh.debug_dump("a3", last.get("log_path"))
            self.assertEqual(last["outcome"], "ok", "A3 outcome: %r" % last)
            # >= not >: real cursor currently reports no total_cost_usd (see note above), so this
            # is the configured flat session_cost_usd fallback, not a real per-token charge.
            self.assertGreaterEqual(last["cost_usd"], kh.CODEX_SESSION_COST_USD)

            log_path = last["log_path"]
            with open(log_path, encoding="utf-8", errors="replace") as f:
                self.assertIn(codeword, f.read())

            status = fx.run_lrb_cli(["status", "--json"])
            self.assertEqual(status.returncode, 0, status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(
                payload["workspaces"][fx.workspace]["beings"][being_id]["last_outcome"], "ok")


class TestProcessTreeKill(unittest.TestCase):
    """B1/B2/B3: the round-1 review finding ('a kill signaled only the direct
    child... Bash/MCP-server grandchildren could survive a hard kill') was
    fixed with process-group killpg — but the stub engine is a flat single
    process and structurally cannot expose that regression. This is the
    first test in the suite that gives the Keeper something with real
    grandchildren to kill."""

    def test_b1_timeout_kills_real_process_tree_claude(self):
        reason = kh.skip_reason("claude")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            claude_bin = shutil.which("claude")
            wrapper = os.path.join(fx.tmp, "claude-wrapper.sh")
            kh.write_claude_wrapper(wrapper, claude_bin, kh.FRAMEWORK_DIR)
            marker = os.path.join(fx.tmp, "b1-sleep.pid")
            task = (
                "Using your Bash tool, run exactly this single command as ONE blocking tool "
                "call (do not run it in the background, do not shorten it, do not work around "
                "it — the long wait is required for this test):\n\n"
                "sh -c 'sleep 180 & echo $! > %s; wait $!'\n\n"
                "Wait for that tool call to return before doing anything else. Under normal "
                "circumstances it will not return before this session is stopped — that is "
                "expected." % marker
            )
            being_id = fx.build_being(
                repo="b1repo", agent="b1being", engine="claude", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=1,
            )
            cfg = fx.write_config({
                "claude": {"command": wrapper, "kind": "claude", "permission_mode": "full"},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            got_marker = fx.run_tick_loop_until(
                keeper, cfg, lambda: os.path.exists(marker), deadline_s=180)
            self.assertTrue(got_marker, "B1: sleep child never wrote its pid marker")
            with open(marker) as f:
                sleep_pid = int(f.read().strip())
            self.assertTrue(kh._pid_alive(sleep_pid), "B1: sleep child not alive right after spawn")

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished, deadline_s=180),
                             "B1: session was not reaped within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "B1: no finished ledger entry")
            self.assertEqual(finished_lines[-1]["outcome"], "timeout", "B1: %r" % finished_lines[-1])

            self.assertFalse(
                kh._pid_alive(sleep_pid),
                "B1 REGRESSION: sleep grandchild survived the Keeper's hard kill — a kill that "
                "only signals the direct child leaves detached descendants running.")

    def test_b2_timeout_kills_real_process_tree_codex(self):
        # B1's kill mechanism (killpg on the whole process group, see _kill
        # in scripts/lrb.py) is Keeper-side and engine-agnostic in the
        # Keeper's own code — but whether a given engine's OWN shell tool
        # actually spawns its subprocess tree the same shape claude's Bash
        # tool does is an empirical question about that engine, not the
        # Keeper. This proves it for codex rather than assuming it.
        reason = kh.skip_reason("codex")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            codex_bin = shutil.which("codex")
            marker = os.path.join(fx.tmp, "b2-sleep.pid")
            task = (
                "Using your shell/command-execution tool, run exactly this single command as "
                "ONE blocking tool call (do not run it in the background yourself, do not "
                "shorten it, do not work around it — the long wait is required for this test):"
                "\n\nsh -c 'sleep 180 & echo $! > %s; wait $!'\n\n"
                "Wait for that tool call to return before doing anything else. Under normal "
                "circumstances it will not return before this session is stopped — that is "
                "expected." % marker
            )
            being_id = fx.build_being(
                repo="b2repo", agent="b2being", engine="codex", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=1,
            )
            cfg = fx.write_config({
                "codex": {"command": codex_bin, "kind": "codex", "permission_mode": "full",
                          "session_cost_usd": kh.CODEX_SESSION_COST_USD},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            got_marker = fx.run_tick_loop_until(
                keeper, cfg, lambda: os.path.exists(marker), deadline_s=180)
            self.assertTrue(got_marker, "B2: sleep child never wrote its pid marker")
            with open(marker) as f:
                sleep_pid = int(f.read().strip())
            self.assertTrue(kh._pid_alive(sleep_pid), "B2: sleep child not alive right after spawn")

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished, deadline_s=180),
                             "B2: session was not reaped within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "B2: no finished ledger entry")
            self.assertEqual(finished_lines[-1]["outcome"], "timeout", "B2: %r" % finished_lines[-1])

            self.assertFalse(
                kh._pid_alive(sleep_pid),
                "B2 REGRESSION: sleep grandchild survived the Keeper's hard kill under codex — "
                "codex's own subprocess tree shape does not behave like claude's here.")

    def test_b3_timeout_kills_real_process_tree_cursor(self):
        # See test_b2's docstring — same question, cursor's own shell tool.
        reason = kh.skip_reason("cursor")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            cursor_bin = shutil.which("cursor-agent")
            marker = os.path.join(fx.tmp, "b3-sleep.pid")
            task = (
                "Using your shell/command-execution tool, run exactly this single command as "
                "ONE blocking tool call (do not run it in the background yourself, do not "
                "shorten it, do not work around it — the long wait is required for this test):"
                "\n\nsh -c 'sleep 180 & echo $! > %s; wait $!'\n\n"
                "Wait for that tool call to return before doing anything else. Under normal "
                "circumstances it will not return before this session is stopped — that is "
                "expected." % marker
            )
            being_id = fx.build_being(
                repo="b3repo", agent="b3being", engine="cursor", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=1,
            )
            cfg = fx.write_config({
                "cursor": {"command": cursor_bin, "kind": "cursor", "permission_mode": "full",
                           "plugin_dir": kh.FRAMEWORK_DIR, "session_cost_usd": kh.CODEX_SESSION_COST_USD},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            got_marker = fx.run_tick_loop_until(
                keeper, cfg, lambda: os.path.exists(marker), deadline_s=180)
            self.assertTrue(got_marker, "B3: sleep child never wrote its pid marker")
            with open(marker) as f:
                sleep_pid = int(f.read().strip())
            self.assertTrue(kh._pid_alive(sleep_pid), "B3: sleep child not alive right after spawn")

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished, deadline_s=180),
                             "B3: session was not reaped within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "B3: no finished ledger entry")
            self.assertEqual(finished_lines[-1]["outcome"], "timeout", "B3: %r" % finished_lines[-1])

            self.assertFalse(
                kh._pid_alive(sleep_pid),
                "B3 REGRESSION: sleep grandchild survived the Keeper's hard kill under cursor — "
                "cursor's own subprocess tree shape does not behave like claude's here.")


class TestSelfScheduling(unittest.TestCase):
    """C1/C4: the design draft's own named 'genuine, not-yet-closed gap' —
    `lrb` is never on PATH, so a being must use the concrete invocation from
    its own spawn prompt, with correct quoting, under real permission
    semantics. Only a real engine call can prove this actually happens."""

    def test_c1_self_scheduling_round_trip_claude(self):
        reason = kh.skip_reason("claude")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            claude_bin = shutil.which("claude")
            wrapper = os.path.join(fx.tmp, "claude-wrapper.sh")
            kh.write_claude_wrapper(wrapper, claude_bin, kh.FRAMEWORK_DIR)
            repo, agent = "c1repo", "c1being"
            being_id_str = "%s/%s" % (repo, agent)
            at = (datetime.now() + timedelta(seconds=75)).strftime("%Y-%m-%dT%H:%M:%S")
            # The "OUTBOX-ROUNDTRIP-OK" string below becomes the SECOND session's entire task
            # instruction (build_spawn_prompt's task_text) once the outbox request fires — that
            # prompt also always includes the self-scheduling boilerplate paragraph, so a bare,
            # unexplained codeword is ambiguous enough that a real model can fixate on the
            # boilerplate instead (observed once: it called `lrb schedule` again rather than just
            # answering). Make it an explicit, unambiguous instruction instead.
            # ASCII-only, short, imperative — avoids giving a real model any punctuation/quoting
            # surface to mangle while copying this into the outer shell-quoted Bash command below.
            second_session_prompt = (
                "Do not schedule anything else. Just reply with exactly: OUTBOX-ROUNDTRIP-OK"
            )
            task = (
                "Using your Bash tool, run exactly this command once (use exactly this literal "
                "datetime — do not compute your own):\n\n"
                "%s schedule --agent %s --at \"%s\" --timeout-minutes 5 \"%s\"\n\n"
                "Then end your final output message with exactly:\nKEEPER-C1-SCHEDULED\n"
            ) % (kh.lrb_invocation(), being_id_str, at, second_session_prompt)
            being_id = fx.build_being(
                repo=repo, agent=agent, engine="claude", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=3,
            )
            cfg = fx.write_config({
                "claude": {"command": wrapper, "kind": "claude", "permission_mode": "full"},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            def accepted():
                acc = kh.lrb.outbox_accepted_dir(fx.workspace)
                return os.path.isdir(acc) and len(os.listdir(acc)) >= 1

            got_accept = fx.run_tick_loop_until(keeper, cfg, accepted, deadline_s=180)
            if not got_accept:
                probe_lines = [l for l in kh.read_ledger(fx.workspace, being_id) if l.get("task") == "probe"]
                if probe_lines:
                    kh.debug_dump("c1-probe-failed", probe_lines[-1].get("log_path"))
                self.fail("C1: no outbox request was ever accepted; probe ledger: %r" % probe_lines)

            def second_session_landed():
                lines = kh.read_ledger(fx.workspace, being_id)
                return any(l.get("task") == "work-session" and l.get("outcome") in kh.FINISHED_OUTCOMES
                           for l in lines)

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, second_session_landed, deadline_s=240),
                             "C1: the self-scheduled work-session never fired/finished")

            work_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                          if l.get("task") == "work-session" and l.get("outcome") in kh.FINISHED_OUTCOMES]
            last = work_lines[-1]
            kh.debug_dump("c1-work", last.get("log_path"))
            self.assertEqual(last["outcome"], "ok", "C1 work-session outcome: %r" % last)
            with open(last["log_path"], encoding="utf-8", errors="replace") as f:
                self.assertIn("OUTBOX-ROUNDTRIP-OK", f.read())

    def test_c4_self_scheduling_denied_under_default_permission_claude(self):
        reason = kh.skip_reason("claude")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            claude_bin = shutil.which("claude")
            wrapper = os.path.join(fx.tmp, "claude-wrapper.sh")
            kh.write_claude_wrapper(wrapper, claude_bin, kh.FRAMEWORK_DIR)
            repo, agent = "c4repo", "c4being"
            being_id_str = "%s/%s" % (repo, agent)
            at = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
            task = (
                "Using your Bash tool, attempt to run exactly this command once:\n\n"
                "%s schedule --agent %s --at \"%s\" --timeout-minutes 5 \"should-be-denied\"\n\n"
                "If that tool call is denied by your permission settings, do not retry it, do "
                "not attempt any workaround, and do not block waiting for approval — simply "
                "note the denial. Regardless of whether it succeeded or was denied, end your "
                "final output message with exactly:\nKEEPER-C4-DENIED-HANDLED\n"
            ) % (kh.lrb_invocation(), being_id_str, at)
            being_id = fx.build_being(
                repo=repo, agent=agent, engine="claude", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=3,
            )
            # permission_mode "default" -> spawn_session does NOT append
            # --dangerously-skip-permissions -> headless with no user
            # present to approve -> the Bash call must be denied, not hang.
            cfg = fx.write_config({
                "claude": {"command": wrapper, "kind": "claude", "permission_mode": "default"},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            def finished():
                bstate = kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {})
                return not bstate.get("running") and bstate.get("last_runs")

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, finished),
                             "C4: session did not finish within the poll deadline")

            finished_lines = [l for l in kh.read_ledger(fx.workspace, being_id)
                               if l.get("outcome") in kh.FINISHED_OUTCOMES]
            self.assertTrue(finished_lines, "C4: no finished ledger entry")
            last = finished_lines[-1]
            kh.debug_dump("c4", last.get("log_path"))
            self.assertEqual(
                last["outcome"], "ok",
                "C4: the session itself should complete normally even though the Bash call "
                "inside it was denied: %r" % last)

            # The actual regression check: a genuinely denied Bash call must leave NO trace in
            # the outbox at all (not even a rejected/ file — that would mean the schedule
            # command DID run and was rejected by lrb itself, a different case entirely).
            for get_dir in (kh.lrb.outbox_accepted_dir, kh.lrb.outbox_rejected_dir, kh.lrb.outbox_done_dir):
                d = get_dir(fx.workspace)
                if os.path.isdir(d):
                    self.assertEqual(os.listdir(d), [], "C4: %s should be empty" % d)


class TestPidIdentity(unittest.TestCase):
    """D1: the fourth-review-pass lesson (macos-ps-o-multi-field-single-
    line.md) — a sandboxed test environment that blocks `ps` forces every
    PID-identity check down the 'unknown' branch and can never exercise the
    confirmed-match/confirmed-mismatch logic at all. This scenario proves
    the confirmed-match branch fires for real, against a real engine's real
    `ps` output — and skips (rather than passing weakly) if it can't."""

    def test_d1_real_pid_identity_confirmed_match_claude(self):
        reason = kh.skip_reason("claude")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            claude_bin = shutil.which("claude")
            wrapper = os.path.join(fx.tmp, "claude-wrapper.sh")
            kh.write_claude_wrapper(wrapper, claude_bin, kh.FRAMEWORK_DIR)
            codeword = "KEEPER-D1-CLAUDE-OK"
            task = (
                "Wait about 20 seconds (e.g. by running `sleep 20` via your Bash tool) before "
                "doing anything else — this delay is required for this test. Then end your "
                "final output message with exactly:\n%s\n" % codeword
            )
            being_id = fx.build_being(
                repo="d1repo", agent="d1being", engine="claude", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=3,
            )
            cfg = fx.write_config({
                "claude": {"command": wrapper, "kind": "claude", "permission_mode": "full"},
            })
            keeper = fx.track_keeper(kh.lrb.Keeper())

            def running_entry():
                return bool(kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {}).get("running"))

            self.assertTrue(fx.run_tick_loop_until(keeper, cfg, running_entry, deadline_s=120),
                             "D1: session never showed up as running")

            state = kh.lrb.load_state(fx.workspace)
            entry = state["beings"][being_id]["running"][0]
            pid = entry["pid"]
            self.assertTrue(kh._pid_alive(pid), "D1: recorded pid is not alive right after spawn")

            real_command = kh.lrb._ps_field(pid, "command")
            self.assertIsNot(real_command, False, "D1: ps reports the pid as already dead")
            if real_command is None:
                self.skipTest("D1: ps identity inspection unavailable in this environment "
                               "(sandboxed shell?) — see keeper_harness.py's module docstring")
            self.assertIn(entry["command"], real_command,
                          "D1: recorded command %r not found in real ps output %r" % (
                              entry["command"], real_command))

            # Simulate a Keeper restart: _pid_matches_entry is a pure module
            # function (not tied to any Keeper instance's live_procs), so
            # calling it directly against the just-observed entry exercises
            # exactly the re-adopted-PID code path a fresh Keeper() would
            # take after a real restart — while the session is still
            # genuinely running, this must be a CONFIRMED match.
            match = kh.lrb._pid_matches_entry(pid, entry)
            self.assertIs(
                match, True,
                "D1 REGRESSION: confirmed-match branch did not fire for a genuinely running "
                "real-engine session (got %r)." % match)

            fx.run_tick_loop_until(
                keeper, cfg,
                lambda: not kh.lrb.load_state(fx.workspace)["beings"].get(being_id, {}).get("running"),
                deadline_s=120,
            )


class TestRealDaemon(unittest.TestCase):
    """E1: the only scenario in this suite that touches the actual code
    path `launchd` runs in production (`lrb daemon`, not the in-process
    Keeper().tick() every other test drives directly) — daemon.lock,
    SIGTERM shutdown, one real spawn inside it. Deliberately does NOT probe
    minimal-PATH shebang resolution (the M7 launchd-PATH-capture concern) —
    that's a separate, more environment-fragile check left for a future
    pass; this scope is limited to the daemon-process lifecycle itself.
    `lrb install --launchd` is never invoked — see module docstring."""

    def test_e1_real_daemon_subprocess_claude(self):
        reason = kh.skip_reason("claude")
        if reason:
            self.skipTest(reason)
        with kh.KeeperFixture() as fx:
            claude_bin = shutil.which("claude")
            wrapper = os.path.join(fx.tmp, "claude-wrapper.sh")
            kh.write_claude_wrapper(wrapper, claude_bin, kh.FRAMEWORK_DIR)
            codeword = "KEEPER-E1-CLAUDE-OK"
            task = ("Regardless of anything else, end your final output message with exactly "
                     "this line:\n%s\n" % codeword)
            being_id = fx.build_being(
                repo="e1repo", agent="e1being", engine="claude", model=kh.MODEL,
                daily_usd=1.0, task_name="probe", task_text=task, timeout_minutes=3,
            )
            fx.write_config({
                "claude": {"command": wrapper, "kind": "claude", "permission_mode": "full"},
            })

            daemon = subprocess.Popen(
                [sys.executable, kh.LRB, "daemon"], cwd=fx.workspace, env=dict(os.environ),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
            )
            fx.track_daemon(daemon)

            deadline = time.monotonic() + 240
            last_outcome = None
            while time.monotonic() < deadline:
                self.assertIsNone(daemon.poll(), "E1: daemon subprocess exited early")
                status = fx.run_lrb_cli(["status", "--json"])
                if status.returncode == 0:
                    payload = json.loads(status.stdout)
                    ws_out = payload.get("workspaces", {}).get(fx.workspace, {})
                    outcome = ws_out.get("beings", {}).get(being_id, {}).get("last_outcome")
                    # last_outcome reflects whatever the LAST ledger line says, including the
                    # "spawned" line written at spawn time — wait for an actually-finished outcome,
                    # not just any truthy value (a bare `if outcome:` fires on "spawned" itself).
                    if outcome in kh.FINISHED_OUTCOMES:
                        last_outcome = outcome
                        break
                time.sleep(3)
            self.assertTrue(last_outcome, "E1: daemon never completed a session")
            self.assertEqual(last_outcome, "ok", "E1: unexpected outcome %r" % last_outcome)

            daemon.send_signal(signal.SIGTERM)
            try:
                daemon.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.fail("E1 REGRESSION: daemon did not shut down gracefully within 15s of SIGTERM")
            self.assertIn(daemon.returncode, (0, -signal.SIGTERM))

            # Lock release: a second `daemon --once` right after must not refuse to start.
            second = fx.run_lrb_cli(["daemon", "--once"], timeout=60)
            self.assertEqual(
                second.returncode, 0,
                "E1 REGRESSION: daemon.lock was not released on shutdown: %s" % second.stderr)


if __name__ == "__main__":
    unittest.main()
