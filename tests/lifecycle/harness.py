#!/usr/bin/env python3
"""Layer-3 lifecycle test harness (design: lore-architect workdir/draft-testing-pipeline.md).

Fixture builder + headless engine driver. Scenarios live in test_*.py next to
this module and are engine-neutral; this module binds the engine specifics.
Currently implemented engines: Claude Code (`claude -p`), Cursor Agent (`cursor-agent -p`),
and Codex (`codex exec`).

These tests call a real engine and cost API money, so they are gated:
skipped unless LR_LIFECYCLE=1 and the engine binary is on PATH.

Environment:
  LR_LIFECYCLE=1        enable the tests (required)
  LR_FRAMEWORK_DIR      plugin under test (default: sibling ../lore-framework)
  LR_ENGINE             engine to drive (default: claude; supported: claude, cursor, codex)
  LR_TEST_MODEL         model for the engine run (default: sonnet; codex default: gpt-5.4-mini)
  LR_RUN_TIMEOUT        per-run timeout in seconds (default: 420)

TODO(parallelization): Scenarios are independent (each test gets its own temp fixture +
local bare origin; FRAMEWORK_DIR is read-only). Today unittest discover runs them strictly
sequentially (~15–45 min per full pass). Future improvement: parallelize by test file or via
LR_LIFECYCLE_JOBS (ProcessPoolExecutor), or run engines in separate terminals. Cap concurrency
to avoid API rate limits. See lore `lifecycle-harness-parallelization.md`.
"""

import json
import os
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
RUN_TIMEOUT = int(os.environ.get("LR_RUN_TIMEOUT", "420"))

LIFECYCLE_ENABLED = os.environ.get("LR_LIFECYCLE") == "1"
ENGINE_BIN = {
    "claude": "claude",
    "codex": "codex",
    "cursor": "cursor-agent",
}.get(ENGINE, ENGINE)
ENGINE_AVAILABLE = shutil.which(ENGINE_BIN) is not None
SKIP_REASON = (
    "lifecycle tests disabled (set LR_LIFECYCLE=1)" if not LIFECYCLE_ENABLED
    else f"engine binary '{ENGINE_BIN}' not on PATH" if not ENGINE_AVAILABLE
    else ""
)

# Canary tokens planted in fixture files. A canary appearing in the engine's
# final output proves the corresponding file was actually read.
ROLE_CANARY = "ROLE-CANARY-7431"      # in role.md
CTX_CANARY = "CTX-CANARY-9182"        # in lore-context.md
FRESH_CANARY = "FRESH-CANARY-5566"    # in a commit that exists only on origin
BUILD_TOOL_FACT = "espresso-tamper"   # in lore/espresso-build-tool.md; recall target
REFLECT_TOOL_CANARY = "kestrel-deploy-4471"  # fact to be captured into reflections/
MERGE_TOOL_CANARY = "otter-deploy-8823"      # pre-seeded reflection fact to be merged in
HELPER_FACT = "flux-widget-6620"      # in helper-agent's lore; consult/attach target
FINALIZE_TOOL_CANARY = "juniper-monitor-3390"  # fact reflected+merged by finalize e2e
BROKEN_REF = "nonexistent-topic-xyz.md"        # seeded broken cross-reference for /lr:check

AGENT_NAME = "test-agent"
HELPER_AGENT_NAME = "helper-agent"
REPO_NAME = "test-lore"

BOOT_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    "Follow the boot procedure exactly. After boot completes, print two lines:\n"
    "BOOT-CODEWORD: <the boot codeword stated in your role>\n"
    "CONTEXT-CODEWORD: <the context codeword stated in your lore-context>\n"
    "If boot fails, print BOOT-FAILED followed by the reason. "
    "Do not reflect, merge, finalize, commit, or push."
)

RECALL_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    "Once booted, invoke the lr:recall skill with hint \"build tool\" to search "
    "your lore. Print the synthesis you get back verbatim. "
    "Do not reflect, merge, finalize, commit, or push."
)

REFLECT_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    "During this session you learned a new fact: the fixture project's deployment "
    f"tool is called '{REFLECT_TOOL_CANARY}', replacing the previous tool "
    "'ristretto-ci' because of faster rollback times. Now invoke the lr:reflect "
    "skill to reflect on this session and capture that fact as a reflection topic. "
    "After reflection completes, print DONE. Do not merge, finalize, commit, or push."
)

MERGE_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    "A reflection topic already exists in your reflections/ directory, ready to be "
    "integrated. Invoke the lr:merge skill to integrate it into your lore. "
    "After merge completes, print DONE. Do not finalize, commit, or push."
)

BOOT_UNKNOWN_PROMPT = (
    "Invoke the lr:boot skill to boot as lore agent 'does-not-exist-agent'. "
    "Follow the boot procedure exactly. If boot fails, print BOOT-FAILED followed "
    "by the reason and the list of available agents."
)

CONSULT_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    f"Once booted, invoke the lr:consult skill to consult '{HELPER_AGENT_NAME}' "
    "with hint \"caching layer\". Print the consultant's synthesis verbatim. "
    "Do not reflect, merge, finalize, commit, or push."
)

ATTACH_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    f"Once booted, invoke the lr:attach skill to attach '{HELPER_AGENT_NAME}' as a "
    "guest. Then invoke the lr:recall skill with hint \"caching layer\" to search "
    "lore across active agents. Print the attach confirmation and the recall "
    "synthesis verbatim. Do not reflect, merge, finalize, commit, or push."
)

SUMMARIZE_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    "Then use the Write tool to create a file at workdir/session-note.md "
    "containing the text 'fixture session note'. Then invoke the lr:summarize "
    "skill to write a session summary for this session. "
    "Do not reflect, merge, finalize, commit, or push."
)

FINALIZE_PROMPT = (
    f"Invoke the lr:boot skill to boot as lore agent '{AGENT_NAME}'. "
    "During this session you learned a new fact: the fixture project's monitoring "
    f"tool is called '{FINALIZE_TOOL_CANARY}', replacing the previous tool because "
    "of better alerting. Now invoke the lr:finalize skill to run the full session "
    "finalization: reflect, merge, summarize, then commit and push. Print DONE "
    "when finalize completes."
)

CREATE_REPO_PROMPT = (
    "Invoke the lr:create-repo skill to scaffold a new lore agent repo named "
    "'new-fixture-repo' in this workspace. If asked for a description, use "
    "'Fixture repo created by lifecycle tests'. Do not ask for confirmation — "
    "proceed directly using that description. Print DONE when complete."
)

CREATE_AGENT_PROMPT = (
    "Invoke the lr:create-agent skill to add a new agent named "
    "'second-fixture-agent' to the existing lore agent repo in this workspace. "
    "Its responsibility: 'Handles fixture testing tasks.' Do not ask for "
    "confirmation — proceed directly using that description. Print DONE when complete."
)

INIT_PROMPT = (
    "Invoke the lr:workspace-init skill in this directory. Do not pause for confirmation "
    "or interview questions — proceed directly with sensible defaults (no additional "
    "repositories) and accept the confirmation gate. Print DONE when complete."
)

WORKSPACE_PULL_PROMPT = (
    "Invoke the lr:workspace-pull skill in this workspace. Print DONE when complete."
)

CHECK_PROMPT = (
    "Invoke the lr:check skill to run consistency checks on the lore agent repos in "
    "this workspace. In your report, explicitly list any broken lore topic or "
    "lore-context.md cross-references you find, by filename. Focus on the workspace's "
    "own agent repos — you do not need to reproduce every check section verbatim."
)

UPDATE_DRYRUN_PROMPT = (
    "Invoke the lr:update skill with --dry-run in this workspace. "
    "Print the full report verbatim."
)

REGISTER_AGENT_PROMPT = (
    f"Invoke the lr:register-agent skill to create a direct boot shortcut for agent "
    f"'{AGENT_NAME}' in repo '{REPO_NAME}'. Print DONE when complete."
)

REGISTER_REPO_PROMPT = (
    f"Invoke the lr:register-repo skill to create direct boot shortcuts for every agent in "
    f"repo '{REPO_NAME}'. Print DONE when complete."
)

UNREGISTER_AGENT_PROMPT = (
    f"Invoke the lr:unregister-agent skill to remove the direct boot shortcut for agent "
    f"'{AGENT_NAME}' in repo '{REPO_NAME}'. Print DONE when complete."
)

UNREGISTER_REPO_PROMPT = (
    f"Invoke the lr:unregister-repo skill to remove every direct boot shortcut for repo "
    f"'{REPO_NAME}'. Print DONE when complete."
)


def _codex_boot_prompt(agent_name, extra):
    """Codex's reliable path is doc-driven rather than slash-skill dispatch."""
    return (
        f"Read the file at '{FRAMEWORK_DIR}/docs/agent-boot.md' and boot as lore agent "
        f"'{agent_name}'. Follow the boot procedure exactly. {extra}"
    )


def codex_prompt(prompt):
    """Translate engine-neutral harness prompts into the Codex doc-driven path."""
    if prompt == BOOT_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            "After boot completes, print two lines:\n"
            "BOOT-CODEWORD: <the boot codeword stated in your role>\n"
            "CONTEXT-CODEWORD: <the context codeword stated in your lore-context>\n"
            "If boot fails, print BOOT-FAILED followed by the reason. "
            "Do not reflect, merge, finalize, commit, or push.",
        )
    if prompt == RECALL_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            f"Once booted, read '{FRAMEWORK_DIR}/docs/recall.md' and follow it with hint "
            "\"build tool\" to search your lore. Print the synthesis verbatim. "
            "Do not reflect, merge, finalize, commit, or push.",
        )
    if prompt == REFLECT_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            "During this session you learned a new fact: the fixture project's deployment "
            f"tool is called '{REFLECT_TOOL_CANARY}', replacing the previous tool "
            "'ristretto-ci' because of faster rollback times. Then read "
            f"'{FRAMEWORK_DIR}/docs/process-reflection.md' and follow it to reflect on this "
            "session and capture that fact as a reflection topic. After reflection completes, "
            "print DONE. Do not merge, finalize, commit, or push.",
        )
    if prompt == MERGE_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            "A reflection topic already exists in your reflections/ directory, ready to be "
            f"integrated. Read '{FRAMEWORK_DIR}/docs/process-merge.md' and follow it to "
            "integrate that reflection into your lore. After merge completes, print DONE. "
            "Do not finalize, commit, or push.",
        )
    if prompt == BOOT_UNKNOWN_PROMPT:
        return _codex_boot_prompt(
            "does-not-exist-agent",
            "If boot fails, print BOOT-FAILED followed by the reason and the list of "
            "available agents.",
        )
    if prompt == CONSULT_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            f"Once booted, read '{FRAMEWORK_DIR}/docs/consult.md' and follow it to consult "
            f"'{HELPER_AGENT_NAME}' with hint \"caching layer\". Print the consultant's "
            "synthesis verbatim. Do not reflect, merge, finalize, commit, or push.",
        )
    if prompt == ATTACH_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            f"Once booted, read '{FRAMEWORK_DIR}/docs/attach.md' and follow it to attach "
            f"'{HELPER_AGENT_NAME}' as a guest. Then read '{FRAMEWORK_DIR}/docs/recall.md' and "
            "follow it with hint \"caching layer\" to search lore across active agents. Print "
            "the attach confirmation and the recall synthesis verbatim. Do not reflect, merge, "
            "finalize, commit, or push.",
        )
    if prompt == SUMMARIZE_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            "Then use the Write tool to create a file at workdir/session-note.md containing "
            "the text 'fixture session note'. Then read "
            f"'{FRAMEWORK_DIR}/docs/summarize.md' and follow it to write a session summary for "
            "this session. Do not reflect, merge, finalize, commit, or push.",
        )
    if prompt == FINALIZE_PROMPT:
        return _codex_boot_prompt(
            AGENT_NAME,
            "During this session you learned a new fact: the fixture project's monitoring "
            f"tool is called '{FINALIZE_TOOL_CANARY}', replacing the previous tool because of "
            f"better alerting. Then read '{FRAMEWORK_DIR}/docs/finalize.md' and follow it to "
            "run the full session finalization: reflect, merge, summarize, then commit and push. "
            "Print DONE when finalize completes.",
        )
    if prompt == CREATE_REPO_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/create-repo.md' and follow it to scaffold a new lore "
            "agent repo named 'new-fixture-repo' in this workspace. If a description is needed, "
            "use 'Fixture repo created by lifecycle tests'. Do not ask for confirmation. Print "
            "DONE when complete."
        )
    if prompt == CREATE_AGENT_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/create-agent.md' and follow it to add a new agent "
            "named 'second-fixture-agent' to the existing lore agent repo in this workspace. "
            "Its responsibility: 'Handles fixture testing tasks.' Do not ask for confirmation. "
            "Print DONE when complete."
        )
    if prompt == INIT_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/workspace-init.md' and follow it in this directory. "
            "Do not pause for confirmation or interview questions — proceed directly with "
            "sensible defaults (no additional repositories) and accept the confirmation gate. "
            "Print DONE when complete."
        )
    if prompt == WORKSPACE_PULL_PROMPT:
        return f"Read '{FRAMEWORK_DIR}/docs/workspace-pull.md' and follow it in this workspace. Print DONE when complete."
    if prompt == CHECK_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/check.md' and follow it to run consistency checks on the lore "
            "agent repos in this workspace. In your report, explicitly list any broken lore topic or "
            "lore-context.md cross-references you find, by filename. Focus on the workspace's own agent "
            "repos — you do not need to reproduce every check section verbatim."
        )
    if prompt == UPDATE_DRYRUN_PROMPT:
        return f"Read '{FRAMEWORK_DIR}/docs/update.md' and follow it with --dry-run in this workspace. Print the full report verbatim."
    if prompt == REGISTER_AGENT_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/register-repo.md' and follow the Register Agent "
            f"instructions for repo '{REPO_NAME}' and agent '{AGENT_NAME}'. Print DONE when "
            "complete."
        )
    if prompt == REGISTER_REPO_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/register-repo.md' and follow the Register Repo "
            f"instructions for repo '{REPO_NAME}'. Print DONE when complete."
        )
    if prompt == UNREGISTER_AGENT_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/register-repo.md' and follow the Unregister Agent "
            f"instructions for repo '{REPO_NAME}' and agent '{AGENT_NAME}'. Print DONE when "
            "complete."
        )
    if prompt == UNREGISTER_REPO_PROMPT:
        return (
            f"Read '{FRAMEWORK_DIR}/docs/register-repo.md' and follow the Unregister Repo "
            f"instructions for repo '{REPO_NAME}'. Print DONE when complete."
        )
    return prompt


def _git(repo, *args, check=True):
    """Run git against a repo path without cd (CWD safety)."""
    return subprocess.run(
        ["git", "-C", repo] + list(args),
        capture_output=True, text=True, check=check,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )


def _commit_all(repo, message):
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=lr-tests", "-c", "user.email=lr-tests@localhost",
         "commit", "-m", message)


def head(repo, ref="HEAD"):
    return _git(repo, "rev-parse", ref).stdout.strip()


class Fixture:
    """Throwaway workspace: one agent repo + a local bare origin (no network)."""

    def __init__(self, tmpdir):
        self.root = tmpdir
        self.workspace = os.path.join(tmpdir, "workspace")
        self.repo = os.path.join(self.workspace, REPO_NAME)
        self.origin = os.path.join(tmpdir, "origin.git")
        self.agent_dir = os.path.join(self.repo, "agents", AGENT_NAME)


def framework_version():
    with open(os.path.join(FRAMEWORK_DIR, "VERSION")) as f:
        return f.read().strip()


def memory_file_name():
    if ENGINE in ("codex", "cursor"):
        return "AGENTS.md"
    return "CLAUDE.md"


def build_fixture(tmpdir, version=None, second_agent=False):
    """Create the fixture workspace, commit it, and push to a local bare origin.

    version: stamp lore-repo.md at this version instead of the current framework
        version. Used by version-mismatch / upgrade-gate scenarios.
    second_agent: also scaffold `helper-agent` in the same repo, for consult/attach
        scenarios that need a second agent to reach across to.
    """
    fx = Fixture(tmpdir)
    lore_dir = os.path.join(fx.agent_dir, "lore")
    workdir = os.path.join(fx.agent_dir, "workdir")
    os.makedirs(lore_dir)
    os.makedirs(workdir)

    def write(rel, content):
        path = os.path.join(fx.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    # Stamp the current framework VERSION by default so boot's version check is
    # a no-op — pass version= explicitly to exercise the migration-walk path.
    write("lore-repo.md", (
        "---\n"
        "description: Fixture lore agent repo for lifecycle tests\n"
        f'version: "{version or framework_version()}"\n'
        "---\n\n"
        "# Test Lore\n\n"
        "Throwaway fixture repo built by tests/lifecycle/harness.py.\n"
    ))
    write(f"agents/{AGENT_NAME}/role.md", (
        "---\n"
        "description: Fixture agent for framework lifecycle tests\n"
        "---\n\n"
        "# Test Agent\n\n"
        "You are a fixture agent used to test the lore framework itself.\n\n"
        f"Boot codeword: {ROLE_CANARY}. When asked for the boot codeword, "
        "state it exactly as written.\n"
    ))
    write(f"agents/{AGENT_NAME}/lore-context.md", (
        "# Lore Context\n\n"
        f"Working knowledge for {AGENT_NAME}.\n\n"
        f"Context codeword: {CTX_CANARY}. When asked for the context codeword, "
        "state it exactly as written.\n\n"
        "Fixture facts live in `lore/` — see `espresso-build-tool.md`.\n"
    ))
    write(f"agents/{AGENT_NAME}/lore/espresso-build-tool.md", (
        "# Espresso Build Tool\n\n"
        "The fixture project's build tool is called **espresso-tamper**. "
        "It was chosen over 'portafilter' for its watch mode.\n"
    ))
    write(f"agents/{AGENT_NAME}/workdir/.gitkeep", "")

    if second_agent:
        write(f"agents/{HELPER_AGENT_NAME}/role.md", (
            "---\n"
            "description: Fixture helper agent for consult/attach lifecycle tests\n"
            "---\n\n"
            "# Helper Agent\n\n"
            "You are a second fixture agent, used to test cross-agent skills "
            "(consult, attach) in the lore framework.\n"
        ))
        write(f"agents/{HELPER_AGENT_NAME}/lore-context.md", (
            "# Lore Context\n\n"
            f"Working knowledge for {HELPER_AGENT_NAME}.\n\n"
            "Fixture facts live in `lore/` — see `caching-layer.md`.\n"
        ))
        write(f"agents/{HELPER_AGENT_NAME}/lore/caching-layer.md", (
            "# Caching Layer\n\n"
            f"The helper project's caching layer is called **{HELPER_FACT}**. "
            "It replaced an in-memory cache for better durability.\n"
        ))
        write(f"agents/{HELPER_AGENT_NAME}/workdir/.gitkeep", "")

    _git(fx.workspace, "init", "-b", "main", REPO_NAME, check=True)
    _commit_all(fx.repo, "fixture: initial agent repo")
    subprocess.run(["git", "init", "--bare", "-b", "main", fx.origin],
                   capture_output=True, text=True, check=True)
    _git(fx.repo, "remote", "add", "origin", fx.origin)
    _git(fx.repo, "push", "-u", "origin", "main")
    return fx


def build_empty_workspace(tmpdir):
    """A bare workspace directory with no agent repo — for create-repo / init tests."""
    workspace = os.path.join(tmpdir, "workspace")
    os.makedirs(workspace)
    return workspace


def make_origin_ahead(fx):
    """Push one extra commit to origin via a second clone, so origin is ahead."""
    clone2 = os.path.join(fx.root, "clone2")
    subprocess.run(["git", "clone", fx.origin, clone2],
                   capture_output=True, text=True, check=True)
    topic = os.path.join(clone2, "agents", AGENT_NAME, "lore", "fresh-fact.md")
    with open(topic, "w") as f:
        f.write(f"# Fresh Fact\n\nFreshness canary: {FRESH_CANARY}.\n")
    _commit_all(clone2, "fixture: teammate pushed a fresh topic")
    _git(clone2, "push", "origin", "main")


def break_origin(fx):
    """Point origin at a nonexistent path so auto-pull fails (degraded mode)."""
    _git(fx.repo, "remote", "set-url", "origin",
         os.path.join(fx.root, "no-such-origin.git"))


def seed_reflection(fx, filename, content):
    """Write a reflection topic directly (bypassing the model) so a merge
    scenario can test integration without depending on reflect having run
    correctly first. Left uncommitted, matching real post-reflect state."""
    reflections_dir = os.path.join(fx.agent_dir, "reflections")
    os.makedirs(reflections_dir, exist_ok=True)
    with open(os.path.join(reflections_dir, filename), "w") as f:
        f.write(content)


def reflections_dir(fx):
    return os.path.join(fx.agent_dir, "reflections")


def lore_snapshot(fx):
    """Filename -> content hash for every file under lore/, for before/after diffing."""
    import hashlib
    lore_dir = os.path.join(fx.agent_dir, "lore")
    snap = {}
    for name in os.listdir(lore_dir):
        path = os.path.join(lore_dir, name)
        if os.path.isfile(path):
            with open(path, "rb") as f:
                snap[name] = hashlib.sha256(f.read()).hexdigest()
    return snap


def dirty_role_md(fx, agent_name=AGENT_NAME):
    """Append an uncommitted line to role.md — collides with migration 2's
    write-set (agents/*/role.md), for the upgrade-gate-on-dirty-tree scenario."""
    path = os.path.join(fx.repo, "agents", agent_name, "role.md")
    with open(path, "a") as f:
        f.write("\nUncommitted local note (should block auto-upgrade).\n")


def seed_broken_reference(fx):
    """Append a reference to a nonexistent lore topic into lore-context.md,
    for the /lr:check broken-cross-reference scenario. Left uncommitted."""
    path = os.path.join(fx.agent_dir, "lore-context.md")
    with open(path, "a") as f:
        f.write(f"\nAlso see `{BROKEN_REF}`.\n")


def declare_sibling_repo(fx, sibling_bare_path):
    """Rewrite lore-repo.md to declare `repos:` pointing at a local bare repo not
    yet cloned into the workspace, for the workspace-pull scenario."""
    path = os.path.join(fx.repo, "lore-repo.md")
    with open(path) as f:
        content = f.read()
    content = content.replace(
        "---\n\n# Test Lore",
        f"repos:\n  - {sibling_bare_path}\n---\n\n# Test Lore",
    )
    with open(path, "w") as f:
        f.write(content)


def read_repo_version(fx):
    """Parse the `version` field out of the local (uncommitted-included) lore-repo.md."""
    path = os.path.join(fx.repo, "lore-repo.md")
    with open(path) as f:
        for line in f:
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def is_clean(repo):
    return _git(repo, "status", "--porcelain").stdout.strip() == ""


def grep_agent_dir(fx, needle):
    """True if `needle` appears in any file under the agent's lore/ or lore-context.md."""
    targets = [os.path.join(fx.agent_dir, "lore-context.md")]
    lore_dir = os.path.join(fx.agent_dir, "lore")
    targets += [os.path.join(lore_dir, n) for n in os.listdir(lore_dir)]
    for path in targets:
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="ignore") as f:
                if needle in f.read():
                    return True
    return False


class RunResult:
    def __init__(self, exit_code, text, cost_usd, duration_ms, stderr):
        self.exit_code = exit_code
        self.text = text
        self.cost_usd = cost_usd
        self.duration_ms = duration_ms
        self.stderr = stderr

    def summary(self):
        cost = f"${self.cost_usd:.4f}" if self.cost_usd is not None else "cost=?"
        secs = f"{self.duration_ms / 1000:.0f}s" if self.duration_ms else "?s"
        return f"exit={self.exit_code} {cost} {secs} model={MODEL}"


_DEBUG_SEQ = [0]


def _debug_dump(result):
    """When LR_DEBUG_DIR is set, persist each engine run's final message + stderr for
    post-mortem diagnosis (fixtures are otherwise torn down). Off by default."""
    dbg = os.environ.get("LR_DEBUG_DIR")
    if not dbg:
        return
    os.makedirs(dbg, exist_ok=True)
    _DEBUG_SEQ[0] += 1
    path = os.path.join(dbg, f"{ENGINE}-{MODEL}-{_DEBUG_SEQ[0]:02d}.txt")
    with open(path, "w", encoding="utf-8", errors="ignore") as fh:
        fh.write(
            f"exit={result.exit_code}\n\n=== FINAL MESSAGE ===\n{result.text}\n\n"
            f"=== STDERR (tail) ===\n{(result.stderr or '')[-2000:]}\n"
        )


def run_engine(workspace, prompt):
    """Run the engine headless in `workspace` and return a RunResult."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    if ENGINE == "claude":
        cmd = [
            "claude", "-p", prompt,
            "--plugin-dir", FRAMEWORK_DIR,
            "--model", MODEL,
            "--output-format", "json",
            "--dangerously-skip-permissions",
        ]
        proc = subprocess.run(
            cmd, cwd=workspace, capture_output=True, text=True, timeout=RUN_TIMEOUT,
            env=env,
        )
    elif ENGINE == "cursor":
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
            cmd, cwd=workspace, capture_output=True, text=True, timeout=RUN_TIMEOUT,
            env=env, stdin=subprocess.DEVNULL,
        )
    elif ENGINE == "codex":
        prompt = codex_prompt(prompt)
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
                cmd, cwd=workspace, capture_output=True, text=True, timeout=RUN_TIMEOUT,
                env=env, stdin=subprocess.DEVNULL,
            )
            text = proc.stdout
            if os.path.exists(output_last_message):
                with open(output_last_message, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read() or proc.stdout
        finally:
            try:
                os.unlink(output_last_message)
            except FileNotFoundError:
                pass
        rr = RunResult(proc.returncode, text or "", None, None, proc.stderr)
        _debug_dump(rr)
        return rr
    else:
        raise NotImplementedError(f"no driver for engine '{ENGINE}' yet")
    text, cost, duration = proc.stdout, None, None
    try:
        payload = json.loads(proc.stdout)
        text = payload.get("result", proc.stdout)
        cost = payload.get("total_cost_usd")
        duration = payload.get("duration_ms")
    except (json.JSONDecodeError, AttributeError):
        pass  # keep raw stdout as text
    rr = RunResult(proc.returncode, text or "", cost, duration, proc.stderr)
    _debug_dump(rr)
    return rr
