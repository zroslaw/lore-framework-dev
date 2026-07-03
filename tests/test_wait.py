#!/usr/bin/env python3
"""Tests for the lr-wait primitive (lore-framework/scripts/wait-server.py + lr-emit).

Lives in lore-framework-dev (the framework's dev repo), NOT in the plugin repo:
tests are dev artifacts and the plugin repo stays slim for marketplace
distribution. See lore-framework/docs/conventions.md § Dev-Only Artifacts.

Stdlib only (unittest) — no pytest, matching the framework's zero-dependency
ethos. The plugin under test is located via $LR_FRAMEWORK_DIR, defaulting to the
sibling ../lore-framework.

Run:  python3 tests/test_wait.py -v
  or: python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
SERVER = os.path.join(FRAMEWORK_DIR, "scripts", "wait-server.py")
EMIT = os.path.join(FRAMEWORK_DIR, "scripts", "lr-emit")


def load_server_module():
    """Import wait-server.py (hyphenated → not a normal import). Only defines
    functions; the server loop is __main__-gated, so import is side-effect-free."""
    spec = importlib.util.spec_from_file_location("wait_server", SERVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ws = load_server_module()


def write_event(inbox, name, content, mtime=None):
    """Drop an event file in the server's <name>.<ts>.<rand> shape, optionally
    pinning mtime so ordering tests are deterministic."""
    os.makedirs(inbox, exist_ok=True)
    fn = f"{name}.{int(time.time())}.{os.urandom(3).hex()}"
    path = os.path.join(inbox, fn)
    with open(path, "w") as f:
        f.write(content)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


class FakeStdin:
    """Stands in for real stdin in unit tests: never delivers a control message —
    readline() waits out its timeout and reports 'timed out' (None)."""

    def readline(self, timeout=None):
        if timeout:
            time.sleep(timeout)
        return None


class TestUnit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lrwait-ut-")
        self.inbox = os.path.join(self.tmp, "inbox")

    def test_resolve_inbox_arg(self):
        inbox, processed = ws.resolve_inbox(self.inbox)
        self.assertEqual(inbox, os.path.abspath(self.inbox))
        self.assertTrue(os.path.isdir(inbox))
        self.assertTrue(os.path.isdir(processed))
        self.assertEqual(processed, os.path.join(self.tmp, "processed"))

    def test_resolve_inbox_env(self):
        os.environ["LR_WAIT_INBOX"] = self.inbox
        try:
            inbox, _ = ws.resolve_inbox(None)
            self.assertEqual(inbox, os.path.abspath(self.inbox))
        finally:
            del os.environ["LR_WAIT_INBOX"]

    def test_list_matches_orders_by_mtime_not_name(self):
        # 'b.*' older than 'a.*' -> arrival order (b, a), the opposite of lexical.
        write_event(self.inbox, "b", "old", mtime=1000)
        write_event(self.inbox, "a", "new", mtime=2000)
        names = [n.split(".", 1)[0] for n in ws.list_matches(self.inbox, None)]
        self.assertEqual(names, ["b", "a"])

    def test_list_matches_skips_dotfiles(self):
        os.makedirs(self.inbox)
        open(os.path.join(self.inbox, ".tmp-inflight"), "w").close()
        open(os.path.join(self.inbox, ".hidden"), "w").close()
        write_event(self.inbox, "real", "x")
        got = ws.list_matches(self.inbox, None)
        self.assertEqual(len(got), 1)
        self.assertTrue(got[0].startswith("real."))

    def test_by_name_prefix_boundary(self):
        # name='deploy' must NOT catch 'deployment' (match is on the "deploy." prefix).
        write_event(self.inbox, "deploy", "D")
        write_event(self.inbox, "deployment", "M")
        deploy = ws.list_matches(self.inbox, "deploy")
        self.assertEqual(len(deploy), 1)
        self.assertTrue(deploy[0].startswith("deploy."))
        deployment = ws.list_matches(self.inbox, "deployment")
        self.assertEqual(len(deployment), 1)
        self.assertTrue(deployment[0].startswith("deployment."))

    def test_consume_moves_and_returns(self):
        inbox, processed = ws.resolve_inbox(self.inbox)
        path = write_event(inbox, "note", "hello world")
        fn = os.path.basename(path)
        ev = ws.consume(inbox, processed, fn)
        self.assertEqual(ev["content"], "hello world")
        self.assertEqual(ev["name"], "note")
        self.assertEqual(ev["source_file"], fn)
        self.assertIn("received_at", ev)
        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists(os.path.join(processed, fn)))

    def test_consume_second_consumer_gets_none(self):
        # Claim-first: two consumers of the same file — one wins, the loser gets
        # None (not a duplicate delivery).
        inbox, processed = ws.resolve_inbox(self.inbox)
        path = write_event(inbox, "note", "once")
        fn = os.path.basename(path)
        first = ws.consume(inbox, processed, fn)
        second = ws.consume(inbox, processed, fn)
        self.assertEqual(first["content"], "once")
        self.assertIsNone(second)

    def test_content_capped_and_flagged(self):
        inbox, processed = ws.resolve_inbox(self.inbox)
        big = "x" * (ws.MAX_EVENT_BYTES + 100)
        path = write_event(inbox, "big", big)
        ev = ws.consume(inbox, processed, os.path.basename(path))
        self.assertEqual(len(ev["content"]), ws.MAX_EVENT_BYTES)
        self.assertTrue(ev.get("truncated"))

    def test_as_float(self):
        self.assertEqual(ws._as_float("2.5", 0), 2.5)
        self.assertEqual(ws._as_float(None, 7), 7)
        self.assertEqual(ws._as_float("nope", 3), 3)

    def test_do_wait_mode_one_returns_oldest(self):
        write_event(self.inbox, "e", "first", mtime=1000)
        write_event(self.inbox, "e", "second", mtime=2000)
        r = ws.do_wait({"inbox": self.inbox, "mode": "one"}, 1, FakeStdin())
        self.assertEqual(r["status"], "ok")
        self.assertEqual([e["content"] for e in r["events"]], ["first"])

    def test_do_wait_mode_all_drains(self):
        write_event(self.inbox, "e", "a", mtime=1000)
        write_event(self.inbox, "e", "b", mtime=2000)
        write_event(self.inbox, "e", "c", mtime=3000)
        r = ws.do_wait({"inbox": self.inbox, "mode": "all"}, 1, FakeStdin())
        self.assertEqual([e["content"] for e in r["events"]], ["a", "b", "c"])
        self.assertEqual(ws.list_matches(self.inbox, None), [])

    def test_do_wait_timeout(self):
        t0 = time.monotonic()
        r = ws.do_wait({"inbox": self.inbox, "timeout_seconds": 0.3}, 1, FakeStdin())
        self.assertEqual(r["status"], "timeout")
        self.assertEqual(r["events"], [])
        self.assertLess(time.monotonic() - t0, 2.0)

    def test_do_sleep(self):
        t0 = time.monotonic()
        r = ws.do_sleep({"seconds": 0.2}, 1, FakeStdin())
        self.assertEqual(r["status"], "slept")
        self.assertGreaterEqual(time.monotonic() - t0, 0.15)


class TestEmit(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(EMIT), f"lr-emit not found: {EMIT}")
        self.tmp = tempfile.mkdtemp(prefix="lrwait-emit-")

    def test_missing_option_value_exits_not_hangs(self):
        # Regression: `--name` as the final arg must exit(2), never infinite-loop.
        r = subprocess.run([EMIT, "--name"], input="", text=True, capture_output=True, timeout=5)
        self.assertEqual(r.returncode, 2)

    def test_emit_filenames_are_unique(self):
        inbox = os.path.join(self.tmp, ".lr-wait", "inbox")
        n = 20
        for i in range(n):
            subprocess.run([EMIT, "--inbox", inbox, "--name", "x"],
                           input=str(i), text=True, check=True, capture_output=True, timeout=5)
        self.assertEqual(len(os.listdir(inbox)), n)  # no same-second collisions


class ServerProc:
    """Drives a live wait-server.py subprocess over real JSON-RPC stdio."""

    def __init__(self):
        self.p = subprocess.Popen(
            [sys.executable, SERVER],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
        self._id = 0

    def _send(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def _read(self):
        line = self.p.stdout.readline()
        if line == "":
            raise AssertionError("server closed stdout; stderr:\n" + self.p.stderr.read())
        return json.loads(line)

    def request(self, method, params=None):
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        r = self._read()
        assert r.get("id") == self._id, f"id mismatch: {r}"
        return r

    def notify(self, method, params=None):
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def tool(self, name, args):
        r = self.request("tools/call", {"name": name, "arguments": args})
        assert "result" in r, f"tool error: {r}"
        return json.loads(r["result"]["content"][0]["text"])

    def close(self):
        if self.p.poll() is None:
            try:
                self.p.stdin.close()
            except Exception:
                pass
            try:
                self.p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.p.kill()
                self.p.wait()
        for stream in (self.p.stdin, self.p.stdout, self.p.stderr):
            try:
                if stream and not stream.closed:
                    stream.close()
            except Exception:
                pass
        return self.p.returncode


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(SERVER), f"server not found: {SERVER}")
        self.assertTrue(os.path.exists(EMIT), f"lr-emit not found: {EMIT}")
        self.tmp = tempfile.mkdtemp(prefix="lrwait-it-")
        self.srv = ServerProc()
        r = self.srv.request("initialize", {"protocolVersion": "2025-06-18"})
        self.assertEqual(r["result"]["serverInfo"]["name"], "lr-wait")
        self.srv.notify("notifications/initialized")

    def tearDown(self):
        self.srv.close()

    def inbox(self, tag):
        return os.path.join(self.tmp, tag, ".lr-wait", "inbox")

    def emit(self, text, tag, name=None):
        args = [EMIT, "--inbox", self.inbox(tag)]
        if name:
            args += ["--name", name]
        subprocess.run(args, input=text, text=True, check=True, capture_output=True)

    def test_tools_list(self):
        r = self.srv.request("tools/list")
        names = sorted(t["name"] for t in r["result"]["tools"])
        self.assertEqual(names, ["sleep", "wait_for_event"])

    def test_sleep(self):
        self.assertEqual(self.srv.tool("sleep", {"seconds": 0.5})["status"], "slept")

    def test_timeout(self):
        res = self.srv.tool("wait_for_event", {"inbox": self.inbox("t"), "timeout_seconds": 0.5})
        self.assertEqual(res["status"], "timeout")

    def test_emit_then_one_oldest_first(self):
        self.emit("first", "one", name="note")
        time.sleep(0.05)
        self.emit("second", "one", name="note")
        r1 = self.srv.tool("wait_for_event", {"inbox": self.inbox("one"), "mode": "one"})
        r2 = self.srv.tool("wait_for_event", {"inbox": self.inbox("one"), "mode": "one"})
        self.assertEqual(r1["events"][0]["content"], "first")
        self.assertEqual(r2["events"][0]["content"], "second")

    def test_all_and_by_name(self):
        self.emit("DEPLOY", "b", name="deploy")
        time.sleep(0.02)
        self.emit("CI", "b", name="ci")
        res = self.srv.tool("wait_for_event", {"inbox": self.inbox("b"), "name": "deploy"})
        self.assertEqual([e["content"] for e in res["events"]], ["DEPLOY"])
        left = os.listdir(self.inbox("b"))
        self.assertEqual(len(left), 1)
        self.assertTrue(left[0].startswith("ci."))

    def test_blocking_wait_woken_by_late_emit(self):
        def late():
            time.sleep(0.4)
            self.emit("woke", "w", name="go")

        threading.Thread(target=late, daemon=True).start()
        t0 = time.monotonic()
        res = self.srv.tool("wait_for_event", {"inbox": self.inbox("w"), "name": "go", "timeout_seconds": 0})
        self.assertEqual(res["events"][0]["content"], "woke")
        self.assertLess(time.monotonic() - t0, 3.0)

    def test_stray_request_midwait_gets_busy_error(self):
        # A stray id-bearing request during a wait must be answered (busy error),
        # not silently dropped (which would hang the host for that id).
        inbox = self.inbox("busy")
        self.srv._id += 1
        wait_id = self.srv._id
        self.srv._send({"jsonrpc": "2.0", "id": wait_id, "method": "tools/call",
                        "params": {"name": "wait_for_event",
                                   "arguments": {"inbox": inbox, "name": "go", "timeout_seconds": 0}}})
        self.srv._id += 1
        stray_id = self.srv._id
        self.srv._send({"jsonrpc": "2.0", "id": stray_id, "method": "tools/list", "params": {}})
        r = self.srv._read()
        self.assertEqual(r.get("id"), stray_id)
        self.assertIn("error", r)
        self.assertEqual(r["error"]["code"], -32603)
        self.emit("done", "busy", name="go")  # release the blocked wait
        r2 = self.srv._read()
        self.assertEqual(r2.get("id"), wait_id)
        payload = json.loads(r2["result"]["content"][0]["text"])
        self.assertEqual(payload["events"][0]["content"], "done")

    def test_eof_shutdown(self):
        self.assertEqual(self.srv.close(), 0)  # idempotent; tearDown close() is safe


if __name__ == "__main__":
    unittest.main()
