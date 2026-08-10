#!/usr/bin/env python3
"""Tests for lr_core.workspace_scan — the deterministic workspace scanner.

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only
(unittest), matching test_lr_core.py. The plugin under test is located via
$LR_FRAMEWORK_DIR, defaulting to the sibling ../lore-framework.

Focus: the v37 Codex-shortcut relocation. Codex loads skills from both the repo
root and the user's home directory, so the framework writes them to
`<workspace>/.codex/skills/` (publishable) and reports leftovers in
`~/.codex/skills/` (not publishable) as finding S15.

`shortcut_inventory` reads the real `~/.codex/skills` through `expanduser`, so
every test that touches it repoints HOME at a tempdir first. A test that forgets
would report the developer's own registered agents.

Run:  python3 tests/test_workspace_scan.py -v
  or: python3 -m unittest discover -s tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
LR_CORE = os.path.join(FRAMEWORK_DIR, "scripts", "lr-core")

sys.path.insert(0, os.path.join(FRAMEWORK_DIR, "scripts"))
from lr_core import workspace_scan as ws  # noqa: E402

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}

BOOT_LINE = ("Read the `SKILL.md` for the installed `lr:boot` skill available in this "
             "session. Follow its self-location instruction to resolve "
             "`<framework-root>`, then read its `docs/agent-boot.md` and boot as agent "
             "`%s` from `%s`.\n")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def write_codex_shortcut(root, agent, agent_dir):
    """A Codex per-agent shortcut under `<root>/lr-<agent>-agent/SKILL.md`."""
    write(os.path.join(root, "lr-%s-agent" % agent, "SKILL.md"),
          "---\nname: lr-%s-agent\ndescription: \"Boot %s\"\n---\n\n%s"
          % (agent, agent, BOOT_LINE % (agent, agent_dir)))


def make_agent(workspace, repo, agent):
    repo_dir = os.path.join(workspace, repo)
    write(os.path.join(repo_dir, "lore-repo.md"),
          "---\ndescription: Test repo\nversion: \"37\"\n---\n\n# %s\n" % repo)
    agent_dir = os.path.join(repo_dir, "agents", agent)
    write(os.path.join(agent_dir, "role.md"),
          "---\ndescription: The %s agent\n---\n\n# %s\n" % (agent, agent))
    write(os.path.join(agent_dir, "lore-context.md"), "# Lore Context\n")
    os.makedirs(os.path.join(agent_dir, "lore"), exist_ok=True)
    os.makedirs(os.path.join(agent_dir, "workdir"), exist_ok=True)
    return agent_dir


def findings_by_id(findings):
    return {f["id"]: f for f in findings}


def base_data(**overrides):
    """The minimum `build_findings` input, with everything quiet by default."""
    data = {
        "applicable": True,
        "engine": "claude",
        "git": {"tracked": True, "own_root": True, "detached": False,
                "ahead": 0, "behind": 0, "origin": "git@example.com:x/y.git",
                "upstream": "origin/main", "enclosing_root": None},
        "descriptors": {"lore_workspace": True, "sharing": None, "declared": [],
                        "gitignore_lines": list(ws.STANDARD_IGNORE_LINES)},
        "children": [],
        "memory": {
            "agents_md": {"present": True, "format": "v3",
                          "sections": {k: "present" for k, _ in ws.MEMORY_SECTIONS}},
            "claude_md": {"present": True, "import_stub": True,
                          "payload_in_claude_md": False},
        },
        "shortcuts": {"claude": [], "codex": [], "cursor": [], "codex_home": []},
        "agents": [],
        "agents_by_repo": {},
        "worktrees": [],
        "managed_paths": {"set": list(ws.MANAGED_PATHS), "dirty": [], "other_dirty": []},
    }
    data.update(overrides)
    return data


class TestManagedPaths(unittest.TestCase):
    """The framework-managed path set — what `/lr:workspace-push` may stage."""

    def test_all_three_engines_shortcuts_are_managed(self):
        for pattern in (".claude/commands/lr-*-agent.md",
                        ".codex/skills/lr-*-agent/SKILL.md",
                        ".cursor/skills/lr-*-agent/SKILL.md"):
            self.assertIn(pattern, ws.MANAGED_PATHS)

    def test_home_codex_path_is_not_managed(self):
        # It is outside the workspace repo; git can never carry it.
        for pattern in ws.MANAGED_PATHS:
            self.assertFalse(pattern.startswith("~"), pattern)

    def test_is_managed_matches_codex_workspace_shortcut(self):
        self.assertTrue(ws.is_managed(".codex/skills/lr-alpha-agent/SKILL.md"))

    def test_is_managed_rejects_nested_and_foreign_codex_paths(self):
        # The segment-count guard: `*` must not swallow a `/`.
        self.assertFalse(ws.is_managed(".codex/skills/nested/lr-alpha-agent/SKILL.md"))
        self.assertFalse(ws.is_managed(".codex/skills/lr-alpha-agent/reference.md"))
        self.assertFalse(ws.is_managed(".codex/skills/some-other-skill/SKILL.md"))
        self.assertFalse(ws.is_managed(".codex/config.toml"))


class TestShortcutInventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-ws-scan-")
        self.workspace = os.path.join(self.tmp, "workspace")
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.workspace)
        os.makedirs(self.home)
        self._real_home = os.environ.get("HOME")
        os.environ["HOME"] = self.home

    def tearDown(self):
        if self._real_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self._real_home
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def test_workspace_and_home_codex_shortcuts_are_separate_keys(self):
        write_codex_shortcut(os.path.join(self.workspace, ".codex", "skills"),
                             "alpha", "/x/agents/alpha")
        write_codex_shortcut(os.path.join(self.home, ".codex", "skills"),
                             "legacy", "/x/agents/legacy")
        inv = ws.shortcut_inventory(self.workspace)
        self.assertEqual(inv["codex"], ["alpha"])
        self.assertEqual(inv["codex_home"], ["legacy"])

    def test_codex_key_ignores_non_shortcut_skills(self):
        root = os.path.join(self.workspace, ".codex", "skills")
        write_codex_shortcut(root, "alpha", "/x/agents/alpha")
        write(os.path.join(root, "some-other-skill", "SKILL.md"), "---\n---\n")
        os.makedirs(os.path.join(root, "lr-noskill-agent"))  # no SKILL.md
        self.assertEqual(ws.shortcut_inventory(self.workspace)["codex"], ["alpha"])

    def test_missing_directories_are_empty_not_an_error(self):
        inv = ws.shortcut_inventory(self.workspace)
        self.assertEqual(inv, {"claude": [], "codex": [], "cursor": [],
                               "codex_home": []})


class TestS15LegacyCodexShortcuts(unittest.TestCase):
    """S15 — Codex shortcuts still in the unpublishable home location."""

    def test_fires_for_a_workspace_agent_with_a_home_shortcut(self):
        data = base_data(agents=["alpha"],
                         shortcuts={"claude": [], "codex": [], "cursor": [],
                                    "codex_home": ["alpha"]})
        f = findings_by_id(ws.build_findings(data))
        self.assertIn("S15", f)
        self.assertEqual(f["S15"]["severity"], "info")
        self.assertEqual(f["S15"]["data"]["agents"], ["alpha"])
        self.assertEqual(f["S15"]["data"]["also_workspace_local"], [])

    def test_reports_duplicates_separately(self):
        data = base_data(agents=["alpha", "beta"],
                         shortcuts={"claude": [], "codex": ["alpha"], "cursor": [],
                                    "codex_home": ["alpha", "beta"]})
        f = findings_by_id(ws.build_findings(data))
        self.assertEqual(f["S15"]["data"]["agents"], ["alpha", "beta"])
        self.assertEqual(f["S15"]["data"]["also_workspace_local"], ["alpha"])

    def test_silent_when_the_home_name_is_not_an_agent_here(self):
        # `~/.codex/skills` is user-global; an unmatched name is another
        # workspace's shortcut, and telling this user to relocate it is wrong.
        data = base_data(agents=["alpha"],
                         shortcuts={"claude": [], "codex": ["alpha"], "cursor": [],
                                    "codex_home": ["somebody-elses-agent"]})
        self.assertNotIn("S15", findings_by_id(ws.build_findings(data)))

    def test_silent_once_relocated(self):
        data = base_data(agents=["alpha"],
                         shortcuts={"claude": [], "codex": ["alpha"], "cursor": [],
                                    "codex_home": []})
        self.assertNotIn("S15", findings_by_id(ws.build_findings(data)))

    def test_not_gated_on_the_running_engine(self):
        # The remedy is a workspace-local write, correct from any engine — and a
        # mixed-engine team benefits from the Claude session noticing.
        for engine in ("claude", "codex", "cursor", "unknown"):
            data = base_data(engine=engine, agents=["alpha"],
                             shortcuts={"claude": [], "codex": [], "cursor": [],
                                        "codex_home": ["alpha"]})
            self.assertIn("S15", findings_by_id(ws.build_findings(data)), engine)

    def test_s11_counts_a_home_shortcut_as_registered(self):
        # A home shortcut still boots the agent, so "no shortcut anywhere" is
        # false. S15 is the finding that owns this state, not S11.
        data = base_data(agents=["alpha"],
                         shortcuts={"claude": [], "codex": [], "cursor": [],
                                    "codex_home": ["alpha"]})
        f = findings_by_id(ws.build_findings(data))
        self.assertNotIn("S11", f)
        self.assertIn("S15", f)

    def test_s11_fires_when_no_location_has_it(self):
        data = base_data(agents=["alpha"])
        self.assertIn("S11", findings_by_id(ws.build_findings(data)))


class TestScanEndToEnd(unittest.TestCase):
    """The CLI path: a dirty Codex shortcut must classify as managed, not other."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="lr-ws-scan-e2e-")
        self.workspace = os.path.join(self.tmp, "workspace")
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.workspace)
        os.makedirs(self.home)
        self.agent_dir = make_agent(self.workspace, "test-agents", "alpha")
        write(os.path.join(self.workspace, "lore-workspace.md"),
              "---\ndescription: Test workspace\n---\n\n# Workspace\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-qm", "initial")

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.tmp], check=False)

    def git(self, *args):
        env = os.environ.copy()
        env.update(GIT_ENV)
        return subprocess.run(["git", "-C", self.workspace] + list(args),
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              env=env, check=False)

    def scan(self):
        env = os.environ.copy()
        env.update(GIT_ENV)
        env["HOME"] = self.home
        proc = subprocess.run(
            [sys.executable, LR_CORE, "workspace-scan",
             "--workspace", self.workspace],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        return json.loads(proc.stdout.decode())["data"]

    def test_dirty_codex_shortcut_is_managed_and_publishable(self):
        write_codex_shortcut(os.path.join(self.workspace, ".codex", "skills"),
                             "alpha", self.agent_dir)
        data = self.scan()
        self.assertIn(".codex/skills/lr-alpha-agent/SKILL.md",
                      data["managed_paths"]["dirty"])
        self.assertEqual(data["managed_paths"]["other_dirty"], [])
        self.assertEqual(data["shortcuts"]["codex"], ["alpha"])
        self.assertIn(".codex/skills/lr-*-agent/SKILL.md",
                      data["managed_paths"]["set"])

    def test_home_shortcut_is_inventoried_but_never_staged(self):
        write_codex_shortcut(os.path.join(self.home, ".codex", "skills"),
                             "alpha", self.agent_dir)
        data = self.scan()
        self.assertEqual(data["shortcuts"]["codex_home"], ["alpha"])
        self.assertEqual(data["managed_paths"]["dirty"], [])
        self.assertIn("S15", findings_by_id(data["findings"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
