#!/usr/bin/env python3
"""Layer-3 Keeper lifecycle test harness (design: lore-architect
workdir/draft-lrb-lifecycle-tests.md).

Fixture builder + real-engine driver for Being Keeper (`lrb`) lifecycle
scenarios — the mechanics ONLY a real engine subprocess can validate (real
argv, real headless result-JSON shape, real cost fields, real process trees
to kill, real `ps` output to parse identity from). Complements the
deterministic stub-engine suite in ../test_lrb.py, which already covers
scheduling math, budget gating, outbox validation, and PID-identity *logic*
against a zero-cost stub — this module deliberately does not re-test any of
that.

Gated as the separate Lore Beings lifecycle suite (see ../README.md's Layer-3
table): Keeper scenarios have a strictly higher
blast-radius class than "one headless call that costs money" — some spawn a
real background process (a real process tree to kill, or a real `lrb
daemon` subprocess) that can outlive a naive test if teardown isn't
guaranteed. Skipped unless LR_LIFECYCLE_BEINGS=1.

Sandboxing: every scenario redirects $LRB_HOME/$LRB_LAUNCHAGENTS_DIR into a
throwaway tempdir via KeeperFixture — never the real machine's
~/.lore-beings or ~/Library/LaunchAgents. `lrb install --launchd` (loading a
real persistent launchd job) is never invoked anywhere in this file; that
stays a deliberate, separate, user-triggered action (see draft-lore-
beings.md §5/§12).

Hard prerequisite: run this on a real shell with a working `ps` binary, not
inside a permission-sandboxed CI runner or agent environment that blocks
it. A sandbox that blocks `ps` forces every PID-identity check down the
"unknown, can't verify" branch and can never exercise the confirmed-match/
confirmed-mismatch logic (see test_d1_*) — a green run there proves nothing
about that code path. See lore `macos-ps-o-multi-field-single-line.md` and
`lore-beings-mvp-takeover-review.md` for the concrete bug this cost the
framework once already.

Environment:
  LR_LIFECYCLE_BEINGS=1   enable these tests (required)
  LR_FRAMEWORK_DIR        plugin under test (default: sibling ../../../lore-framework)
  LR_ENGINE               engine to drive (default: claude; claude/codex/cursor)
  LR_TEST_MODEL           model override (default: cheapest per-engine, see MODEL_DEFAULTS)
  LR_RUN_TIMEOUT          per-scenario poll deadline in seconds (default: 420)
  LR_KEEP_FIXTURES=1      keep throwaway workspaces after a test (debugging)
  LR_DEBUG_DIR=<path>     dump each finished session's log content here
"""
import importlib.util
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_DIR = os.path.abspath(
    os.environ.get("LR_FRAMEWORK_DIR", os.path.join(HERE, "..", "..", "..", "lore-framework"))
)
LRB = os.path.join(FRAMEWORK_DIR, "scripts", "lrb.py")

ENGINE = os.environ.get("LR_ENGINE", "claude")
LIFECYCLE_BEINGS_ENABLED = (
    os.environ.get("LR_LIFECYCLE_BEINGS") == "1"
    or os.environ.get("LR_LIFECYCLE_KEEPER") == "1"  # legacy alias
)

# Cheapest model real-verified through the Keeper tick loop during the
# original build for each engine kind (draft-lore-beings.md §16).
MODEL_DEFAULTS = {"claude": "haiku", "codex": "gpt-5.4-mini", "cursor": "composer-2.5"}
MODEL = os.environ.get("LR_TEST_MODEL", MODEL_DEFAULTS.get(ENGINE, "haiku"))

RUN_DEADLINE_S = int(os.environ.get("LR_RUN_TIMEOUT", "420"))
CODEX_SESSION_COST_USD = 0.05

FINISHED_OUTCOMES = {"ok", "error", "timeout", "unparseable", "crashed", "invalid-cost", "failed-to-spawn"}


def load_lrb_module():
    spec = importlib.util.spec_from_file_location("lrb", LRB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lrb = load_lrb_module()


# ---- engine availability ---------------------------------------------------


def _cursor_logged_in(bin_name="cursor-agent"):
    try:
        r = subprocess.run([bin_name, "status"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return False
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode == 0 and "not logged in" not in out.lower()


def _codex_logged_in(bin_name="codex"):
    try:
        r = subprocess.run([bin_name, "login", "status"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return r.returncode == 0


def engine_available(kind=None):
    """True if `kind` (default: ENGINE) is present AND, best-effort,
    authenticated. Claude has no cheap non-interactive auth probe available
    here, so presence-on-PATH is treated as available — matching
    ../lifecycle/harness.py's own ENGINE_AVAILABLE convention (a bare
    shutil.which) and this dev environment's existing precedent of already
    running real `claude -p` lifecycle calls under LR_LIFECYCLE=1."""
    kind = kind or ENGINE
    bin_name = {"claude": "claude", "codex": "codex", "cursor": "cursor-agent"}.get(kind, kind)
    path = shutil.which(bin_name)
    if not path:
        return False
    if kind == "cursor":
        return _cursor_logged_in(bin_name)
    if kind == "codex":
        return _codex_logged_in(bin_name)
    return True


def skip_reason(required_kind=None):
    """Non-empty reason string if a Keeper lifecycle scenario for
    `required_kind` (default: ENGINE) should be skipped, else ''."""
    if not LIFECYCLE_BEINGS_ENABLED:
        return "Lore Beings lifecycle tests disabled (set LR_LIFECYCLE_BEINGS=1)"
    kind = required_kind or ENGINE
    if kind != ENGINE:
        return "scenario is %s-only (LR_ENGINE=%s)" % (kind, ENGINE)
    if not engine_available(kind):
        return "engine %r not available/authenticated" % kind
    return ""


# ---- misc helpers -----------------------------------------------------------


def write_claude_wrapper(path, claude_bin, framework_dir):
    """`claude`-kind spawn_session never passes --plugin-dir (only `cursor`
    kind has that config field — see spawn_session in scripts/lrb.py), so
    the ONLY way a Keeper-spawned claude being can load the lr: skills at
    all is for the configured engine `command` to already bake it in. This
    wrapper does that once at fixture-build time."""
    with open(path, "w") as f:
        f.write("#!/bin/sh\nexec %s --plugin-dir %s \"$@\"\n" % (
            shlex.quote(claude_bin), shlex.quote(framework_dir)))
    os.chmod(path, 0o755)


def lrb_invocation():
    """Mirrors scripts/lrb.py's own lrb_invocation() — the concrete command
    a spawned being should run, since bare `lrb` is never on PATH."""
    return "%s %s" % (shlex.quote(sys.executable), shlex.quote(LRB))


def this_minute_cron():
    now = datetime.now()
    return "%d %d * * *" % (now.minute, now.hour)


def read_ledger(workspace, being_id):
    path = lrb.ledger_path(workspace, being_id)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


_DEBUG_SEQ = [0]


def debug_dump(label, log_path):
    dbg = os.environ.get("LR_DEBUG_DIR")
    if not dbg or not log_path or not os.path.exists(log_path):
        return
    os.makedirs(dbg, exist_ok=True)
    _DEBUG_SEQ[0] += 1
    dest = os.path.join(dbg, "%s-%s-%02d.txt" % (ENGINE, label, _DEBUG_SEQ[0]))
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as src, \
                open(dest, "w", encoding="utf-8") as out:
            out.write(src.read())
    except OSError:
        pass


# ---- fixture -----------------------------------------------------------------


class KeeperFixture(object):
    """Context manager: sandboxes LRB_HOME/LRB_LAUNCHAGENTS_DIR into a
    throwaway tempdir (never the real machine home — see module docstring),
    builds a throwaway workspace, and guarantees teardown of anything real a
    scenario spawned — a live tick-loop child (this run's own Popen
    handles), a re-adopted running entry (identified via the Keeper's own
    lrb._pid_matches_entry, never a bare kill), or a real `lrb daemon`
    subprocess registered via track_daemon() — even when the test's own
    assertions raise mid-scenario."""

    def __init__(self):
        self.tmp = None
        self._saved_env = {}
        self._keepers = []
        self._daemons = []

    def __enter__(self):
        self.tmp = tempfile.mkdtemp(prefix="lrb-lifecycle-")
        self.home = os.path.join(self.tmp, "home")
        self.launchagents = os.path.join(self.tmp, "launchagents")
        for k, v in (("LRB_HOME", self.home), ("LRB_LAUNCHAGENTS_DIR", self.launchagents)):
            self._saved_env[k] = os.environ.get(k)
            os.environ[k] = v
        self.workspace = os.path.join(self.tmp, "workspace")
        os.makedirs(self.workspace)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self._teardown_processes()
        finally:
            for k, v in self._saved_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            if os.environ.get("LR_KEEP_FIXTURES") == "1":
                print("lrb-lifecycle: keeping fixture at %s" % self.tmp, file=sys.stderr)
            else:
                shutil.rmtree(self.tmp, ignore_errors=True)
        return False  # never swallow the test's own exception

    def track_keeper(self, keeper):
        self._keepers.append(keeper)
        return keeper

    def track_daemon(self, proc):
        self._daemons.append(proc)
        return proc

    def _teardown_processes(self):
        # This run's own spawns: Popen handles are authoritative, kill the
        # whole process group directly.
        for keeper in self._keepers:
            for proc in list(keeper.live_procs.values()):
                if proc.poll() is None:
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    except OSError:
                        proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                        except OSError:
                            proc.kill()
                        proc.wait(timeout=5)
            keeper.live_procs.clear()
        # Re-adopted entries (no live Popen handle in THIS run — e.g. a
        # simulated-restart scenario): only ever signal a CONFIRMED identity
        # match, exactly like the Keeper's own _can_signal — never a bare
        # os.kill on an unverified PID.
        try:
            state = lrb.load_state(self.workspace)
        except Exception:
            state = None
        if state:
            for bstate in state.get("beings", {}).values():
                for entry in bstate.get("running", []):
                    pid = entry.get("pid")
                    if not pid:
                        continue
                    if lrb._pid_matches_entry(pid, entry) is True:
                        try:
                            os.killpg(os.getpgid(pid), signal.SIGKILL)
                        except OSError:
                            pass
        for proc in self._daemons:
            if proc.poll() is None:
                try:
                    proc.send_signal(signal.SIGTERM)
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
                except OSError:
                    pass

    # ---- fixture building ----------------------------------------------

    def build_being(self, repo, agent, engine, model, daily_usd, task_name, task_text,
                     schedule=None, timeout_minutes=3):
        """Minimal being fixture — being.md + task prompt only (no
        role.md/lore-context.md: the Keeper's own spawn prompt tells the
        being to attempt agent-boot.md, but the Keeper mechanics under test
        here don't depend on that boot actually succeeding — every task
        prompt in this suite ends with an unconditional codeword)."""
        if schedule is None:
            schedule = this_minute_cron()
        repo_dir = os.path.join(self.workspace, repo)
        agent_dir = os.path.join(repo_dir, "agents", agent)
        os.makedirs(agent_dir, exist_ok=True)
        with open(os.path.join(repo_dir, "lore-repo.md"), "w") as f:
            f.write('---\ndescription: Keeper lifecycle fixture\nversion: "1"\n---\n')
        with open(os.path.join(agent_dir, "being.md"), "w") as f:
            f.write(
                "---\ndescription: Keeper lifecycle fixture being\nengine: %s\nmodel: %s\n"
                "daily-usd: %s\nexistential-tasks:\n  - name: %s\n    schedule: \"%s\"\n"
                "    prompt: task.md\n    timeout-minutes: %d\n---\n\n# Being — %s\n\n"
                "Fixture being for Keeper lifecycle tests.\n" % (
                    engine, model, daily_usd, task_name, schedule, timeout_minutes, agent)
            )
        with open(os.path.join(agent_dir, "task.md"), "w") as f:
            f.write(task_text)
        return "%s/%s" % (repo, agent)

    def write_config(self, engines):
        cfg = {"workspaces": [self.workspace], "engines": engines}
        lrb.save_config(cfg)
        return cfg

    def run_lrb_cli(self, args, timeout=30):
        return subprocess.run(
            [sys.executable, LRB] + list(args), cwd=self.workspace,
            capture_output=True, text=True, timeout=timeout,
        )

    def run_tick_loop_until(self, keeper, cfg, predicate, deadline_s=None, interval=2.0):
        """Drives keeper.tick(cfg) until predicate() is true or the deadline
        elapses (default: RUN_DEADLINE_S). Returns True iff predicate() was
        satisfied before the deadline."""
        deadline = time.monotonic() + (deadline_s if deadline_s is not None else RUN_DEADLINE_S)
        while True:
            keeper.tick(cfg)
            if predicate():
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(interval)
