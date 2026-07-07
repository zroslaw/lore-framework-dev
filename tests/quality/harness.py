#!/usr/bin/env python3
"""Lore-agent quality benchmark harness (PoC).

Design: lore-architect workdir/draft-lore-quality-benchmark.md.
Sibling of tests/lifecycle/harness.py — same gating and fixture discipline,
different question: lifecycle asks "did the agent follow the procedure?",
quality asks "did the lore make the agent's output better?".

These tests call a real engine and cost API money, so they are gated:
skipped unless LR_QUALITY=1 and the engine binary is on PATH.

Environment:
  LR_QUALITY=1        enable the benchmark (required)
  LR_FRAMEWORK_DIR    plugin under test (default: sibling ../lore-framework)
  LR_ENGINE           engine to drive (default: claude; supported: claude,
                      cursor, codex)
  LR_TEST_MODEL       model for the agent runs (default: sonnet;
                      codex default: gpt-5.4-mini)
  LR_JUDGE_MODEL      model for S3 judging — always runs on the claude CLI so
                      the judge is identical across engines (default: haiku)
  LR_RUN_TIMEOUT      per-run timeout in seconds (default: 420)
  LR_QUALITY_JOBS     parallel engine runs (default: 3)

S1 (retrieval) tracing per engine:
  claude — stream-json trace; tool_use INPUTS only (outputs would false-
           positive: lore-context.md lists every topic filename).
  codex  — the --json event stream; command/path-like fields only, same
           input-not-output rule.
  cursor — no headless tool trace available (json output carries only the
           final result); S1 is unscored ("-") and excluded from LUS points.
           Cross-engine comparisons should use the S3 pass rate / behavior
           uplift, which every engine scores.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_DIR = os.path.abspath(
    os.environ.get("LR_FRAMEWORK_DIR", os.path.join(HERE, "..", "..", "..", "lore-framework"))
)
ENGINE = os.environ.get("LR_ENGINE", "claude")
MODEL = os.environ.get(
    "LR_TEST_MODEL",
    "gpt-5.4-mini" if ENGINE == "codex" else "sonnet",
)
JUDGE_MODEL = os.environ.get("LR_JUDGE_MODEL", "haiku")
RUN_TIMEOUT = int(os.environ.get("LR_RUN_TIMEOUT", "420"))
JOBS = int(os.environ.get("LR_QUALITY_JOBS", "3"))

QUALITY_ENABLED = os.environ.get("LR_QUALITY") == "1"
ENGINE_BIN = {
    "claude": "claude",
    "codex": "codex",
    "cursor": "cursor-agent",
}.get(ENGINE, ENGINE)
ENGINE_AVAILABLE = shutil.which(ENGINE_BIN) is not None
JUDGE_AVAILABLE = shutil.which("claude") is not None
SKIP_REASON = (
    "quality benchmark disabled (set LR_QUALITY=1)" if not QUALITY_ENABLED
    else f"engine binary '{ENGINE_BIN}' not on PATH" if not ENGINE_AVAILABLE
    else "judge binary 'claude' not on PATH" if not JUDGE_AVAILABLE
    else ""
)

# Which engines expose a tool-call trace in headless mode (needed for S1).
TRACES_TOOLS = ENGINE in ("claude", "codex")

AGENT_NAME = "test-agent"
REPO_NAME = "test-lore"


def _git(repo, *args, check=True):
    return subprocess.run(
        ["git", "-C", repo] + list(args),
        capture_output=True, text=True, check=check,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )


def framework_version():
    with open(os.path.join(FRAMEWORK_DIR, "VERSION")) as f:
        return f.read().strip()


def build_quality_fixture(tmpdir, arm, needle_topics, distractor_topics):
    """Throwaway workspace with one agent repo + local bare origin.

    arm: "treatment" (needles present) or "control" (needles neutralized).
    Topic filenames and lore-context.md are identical across arms, so S1
    retrieval is equally possible in both — only the knowledge differs.
    """
    workspace = os.path.join(tmpdir, "workspace")
    repo = os.path.join(workspace, REPO_NAME)
    agent_dir = os.path.join(repo, "agents", AGENT_NAME)
    os.makedirs(os.path.join(agent_dir, "lore"))
    os.makedirs(os.path.join(agent_dir, "workdir"))

    def write(rel, content):
        path = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    write("lore-repo.md", (
        "---\n"
        "description: Fixture lore agent repo for quality benchmark\n"
        f'version: "{framework_version()}"\n'
        "---\n\n"
        "# Test Lore\n\n"
        "Throwaway fixture repo built by tests/quality/harness.py.\n"
    ))
    write(f"agents/{AGENT_NAME}/role.md", (
        "---\n"
        "description: Engineering assistant for the fixture project\n"
        "---\n\n"
        "# Test Agent\n\n"
        "You are the fixture project's engineering assistant. You write code "
        "and answer questions for the team, applying the project's "
        "accumulated conventions, decisions, and gotchas.\n"
    ))
    all_topics = dict(distractor_topics)
    for name, arms in needle_topics.items():
        all_topics[name] = arms[arm]
    topic_list = ", ".join(f"`{n}`" for n in sorted(all_topics))
    write(f"agents/{AGENT_NAME}/lore-context.md", (
        "# Lore Context\n\n"
        f"Working knowledge for {AGENT_NAME}.\n\n"
        "Project conventions, decisions, and gotchas live in `lore/`: "
        f"{topic_list}. Consult the relevant topic before coding against a "
        "project system.\n"
    ))
    for name, content in sorted(all_topics.items()):
        write(f"agents/{AGENT_NAME}/lore/{name}", content)
    write(f"agents/{AGENT_NAME}/workdir/.gitkeep", "")

    _git(workspace, "init", "-b", "main", REPO_NAME)
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=lr-tests", "-c", "user.email=lr-tests@localhost",
         "commit", "-m", "fixture: quality benchmark agent repo")
    origin = os.path.join(tmpdir, "origin.git")
    subprocess.run(["git", "init", "--bare", "-b", "main", origin],
                   capture_output=True, text=True, check=True)
    _git(repo, "remote", "add", "origin", origin)
    _git(repo, "push", "-u", "origin", "main")
    return workspace


TASK_SUFFIX = (
    "Print your complete answer. "
    "Do not reflect, merge, finalize, commit, or push."
)


def probe_prompt(task):
    """Engine-neutral prompt: boot, then do the task."""
    if ENGINE == "codex":
        # Codex's reliable headless path is doc-driven, not slash-skill
        # dispatch (see lore codex-testing-methodology.md).
        return (
            f"Read the file at '{FRAMEWORK_DIR}/docs/agent-boot.md' and boot "
            f"as lore agent '{AGENT_NAME}'. Follow the boot procedure "
            f"exactly. Once booted, perform this task:\n\n{task}\n\n"
            + TASK_SUFFIX
        )
    return (
        f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
        f"Once booted, perform this task:\n\n{task}\n\n"
        + TASK_SUFFIX
    )


class ProbeRun:
    def __init__(self, exit_code, text, tool_inputs, cost_usd, duration_ms, stderr):
        self.exit_code = exit_code
        self.text = text
        self.tool_inputs = tool_inputs  # serialized tool-call INPUTS, or None
        self.cost_usd = cost_usd
        self.duration_ms = duration_ms
        self.stderr = stderr


# Keys that carry tool-call *inputs* in codex's --json event stream. Outputs
# (stdout, file contents) must never be collected — lore-context.md lists all
# topic filenames, so any echoed file content would false-positive S1.
_CODEX_INPUT_KEYS = {"command", "cmd", "path", "file_path", "arguments", "args", "pattern"}


def _collect_input_strings(node, out):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _CODEX_INPUT_KEYS:
                out.append(json.dumps(value))
            else:
                _collect_input_strings(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_input_strings(item, out)


def run_probe(workspace, task):
    """Run the engine headless in `workspace`; capture final text and (where
    the engine supports it) a tool-input trace for S1."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    prompt = probe_prompt(task)

    if ENGINE == "claude":
        cmd = [
            "claude", "-p", prompt,
            "--plugin-dir", FRAMEWORK_DIR,
            "--model", MODEL,
            "--output-format", "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
        ]
        proc = subprocess.run(
            cmd, cwd=workspace, capture_output=True, text=True,
            timeout=RUN_TIMEOUT, env=env,
        )
        tool_inputs, text, cost, duration = [], "", None, None
        for line in proc.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_inputs.append(json.dumps(block.get("input", {})))
            elif ev.get("type") == "result":
                text = ev.get("result") or ""
                cost = ev.get("total_cost_usd")
                duration = ev.get("duration_ms")
        return ProbeRun(proc.returncode, text, tool_inputs, cost, duration, proc.stderr)

    if ENGINE == "cursor":
        cmd = [
            "cursor-agent", "-p", prompt,
            "--plugin-dir", FRAMEWORK_DIR,
            "--model", MODEL,
            "--output-format", "json",
            "--force",
            "--trust",
            "--sandbox", "disabled",
            "--workspace", workspace,
        ]
        proc = subprocess.run(
            cmd, cwd=workspace, capture_output=True, text=True,
            timeout=RUN_TIMEOUT, env=env, stdin=subprocess.DEVNULL,
        )
        text, duration = proc.stdout, None
        try:
            payload = json.loads(proc.stdout)
            text = payload.get("result", proc.stdout)
            duration = payload.get("duration_ms")
        except (json.JSONDecodeError, AttributeError):
            pass
        # No tool trace in cursor's headless json output → S1 unscorable.
        return ProbeRun(proc.returncode, text or "", None, None, duration, proc.stderr)

    if ENGINE == "codex":
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as f:
            output_last_message = f.name
        try:
            cmd = [
                "codex", "exec", prompt,
                "-C", workspace,
                "--model", MODEL,
                "--skip-git-repo-check",
                "--dangerously-bypass-approvals-and-sandbox",
                "--json",
                "--output-last-message", output_last_message,
            ]
            proc = subprocess.run(
                cmd, cwd=workspace, capture_output=True, text=True,
                timeout=RUN_TIMEOUT, env=env, stdin=subprocess.DEVNULL,
            )
            tool_inputs = []
            for line in proc.stdout.splitlines():
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                _collect_input_strings(ev, tool_inputs)
            text = ""
            if os.path.exists(output_last_message):
                with open(output_last_message, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            return ProbeRun(proc.returncode, text or proc.stdout or "",
                            tool_inputs, None, None, proc.stderr)
        finally:
            try:
                os.unlink(output_last_message)
            except FileNotFoundError:
                pass

    raise NotImplementedError(f"no driver for engine '{ENGINE}'")


def score_s1(run, target_filename):
    """Retrieval: the load-bearing lore file appears in some tool call's input
    (Read path, grep pattern, cat command — any access counts). Returns None
    when the engine produced no trace (S1 unscorable)."""
    if run.tool_inputs is None:
        return None
    return any(target_filename in ti for ti in run.tool_inputs)


def score_s2(run, s2_check):
    """Grounding: the planted fact surfaces in the final output."""
    if s2_check["type"] == "substring":
        return s2_check["value"].lower() in run.text.lower()
    if s2_check["type"] == "regex":
        return re.search(s2_check["value"], run.text) is not None
    raise ValueError(f"unknown s2 check type: {s2_check['type']}")


def judge_s3(task, response, rubric):
    """Application: binary LLM-judge label against a one-paragraph rubric.
    The judge always runs on the claude CLI with a fixed model
    (LR_JUDGE_MODEL), independent of LR_ENGINE, so scores stay comparable
    across engines and benchmark runs.

    Returns (passed, judge_line). `passed` is None when the judge call itself
    failed (non-zero exit, usage limit, or a reply that is not PASS/FAIL) —
    a broken judge must INVALIDATE the score, never count as FAIL. Learned
    the hard way: a session-limit message scored as FAIL corrupts every S3
    silently."""
    prompt = (
        "You are a strict, literal test evaluator. An AI agent was given a "
        "task; you grade its response against a rubric.\n\n"
        f"--- TASK GIVEN TO THE AGENT ---\n{task}\n\n"
        f"--- AGENT'S RESPONSE ---\n{response}\n\n"
        f"--- RUBRIC ---\n{rubric}\n\n"
        "Reply with exactly one line: the word PASS or FAIL, then ' - ' and "
        "one short reason. No other text."
    )
    first = ""
    for _attempt in range(2):  # one retry for transient failures
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", JUDGE_MODEL, "--output-format", "json"],
            capture_output=True, text=True, timeout=120,
        )
        verdict_line = ""
        try:
            verdict_line = (json.loads(proc.stdout).get("result") or "").strip()
        except json.JSONDecodeError:
            verdict_line = proc.stdout.strip()
        first = verdict_line.splitlines()[0].strip() if verdict_line else ""
        up = first.upper()
        if proc.returncode == 0 and (up.startswith("PASS") or up.startswith("FAIL")):
            return up.startswith("PASS"), first
    return None, first or f"judge call failed (exit={proc.returncode})"
