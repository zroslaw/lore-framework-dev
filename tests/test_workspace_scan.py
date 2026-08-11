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


class TestS13DirnameCollisions(unittest.TestCase):
    """Two declared URLs deriving to one directory must not silently cancel out.

    `declared_repos` dedupes by URL, so both survive into `build_findings`. A
    dirname-keyed map that kept the last one would hide the collision *and* check
    the child's origin against the wrong declaration.
    """

    def _declared(self):
        return [
            {"url": "git@a.example.com:team/shared.git", "dirname": "shared",
             "source": "workspace"},
            {"url": "git@b.example.com:other/shared.git", "dirname": "shared",
             "source": "domain"},
        ]

    def test_collision_is_reported(self):
        data = base_data(descriptors={**base_data()["descriptors"],
                                      "declared": self._declared()})
        f = findings_by_id(ws.build_findings(data))
        self.assertIn("S13", f)
        reasons = [c["reason"] for c in f["S13"]["data"]]
        self.assertIn("two declared URLs derive to the same directory name", reasons)

    def test_first_declarer_wins_the_origin_check(self):
        # The child matches the FIRST declaration; keeping the last one instead
        # would produce a spurious "origin does not match" conflict.
        declared = self._declared()
        data = base_data(
            descriptors={**base_data()["descriptors"], "declared": declared},
            children=[{"dirname": "shared", "git": True, "ignorable": True,
                       "escapes_workspace": False, "declared": True,
                       "lore_repo": True, "ignored": True,
                       "default_branch": "main", "current_branch": "main",
                       "origin": declared[0]["url"]}])
        f = findings_by_id(ws.build_findings(data))
        reasons = [c["reason"] for c in f["S13"]["data"]]
        self.assertNotIn("origin does not match declaration", reasons)

    def test_collided_dirname_is_not_also_reported_missing(self):
        # S6's remedy is "run workspace-pull", and pull refuses to place either URL
        # until a descriptor is edited. Only S13 may own this state.
        data = base_data(descriptors={**base_data()["descriptors"],
                                      "declared": self._declared()})
        f = findings_by_id(ws.build_findings(data))
        self.assertNotIn("S6", f)
        self.assertIn("S13", f)

    def test_uncollided_missing_repo_still_reports_s6(self):
        declared = self._declared() + [{"url": "git@x:t/solo.git", "dirname": "solo",
                                        "source": "workspace"}]
        data = base_data(descriptors={**base_data()["descriptors"],
                                      "declared": declared})
        f = findings_by_id(ws.build_findings(data))
        self.assertEqual([m["dirname"] for m in f["S6"]["data"]], ["solo"])

    def test_child_cloned_from_second_declarer_yields_one_row(self):
        # The collision entry names both URLs. Also reporting "origin does not match
        # declaration" against the first declarer would be two rows for one problem,
        # naming a URL the user never cloned from.
        declared = self._declared()
        data = base_data(
            descriptors={**base_data()["descriptors"], "declared": declared},
            children=[{"dirname": "shared", "git": True, "ignorable": True,
                       "escapes_workspace": False, "declared": True,
                       "lore_repo": True, "ignored": True,
                       "default_branch": "main", "current_branch": "main",
                       "origin": declared[1]["url"]}])
        rows = findings_by_id(ws.build_findings(data))["S13"]["data"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"],
                         "two declared URLs derive to the same directory name")

    def test_no_collision_when_dirnames_differ(self):
        declared = [{"url": "git@x:t/a.git", "dirname": "a", "source": "workspace"},
                    {"url": "git@x:t/b.git", "dirname": "b", "source": "workspace"}]
        data = base_data(descriptors={**base_data()["descriptors"],
                                      "declared": declared})
        self.assertNotIn("S13", findings_by_id(ws.build_findings(data)))


class TestS4EnclosingRepo(unittest.TestCase):
    """A workspace nested in someone else's repo is not one more info line."""

    def _data(self, enclosing):
        git = {**base_data()["git"], "own_root": False,
               "enclosing_root": enclosing}
        return base_data(git=git)

    def test_local_only_workspace_stays_info(self):
        f = findings_by_id(ws.build_findings(self._data(None)))
        self.assertEqual(f["S4"]["severity"], "info")

    def test_enclosed_workspace_warns(self):
        f = findings_by_id(ws.build_findings(self._data("/somewhere/other-repo")))
        self.assertEqual(f["S4"]["severity"], "warn")


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

    def scan_envelope(self):
        """The whole envelope — `warnings` live outside `data`."""
        env = os.environ.copy()
        env.update(GIT_ENV)
        env["HOME"] = self.home
        proc = subprocess.run(
            [sys.executable, LR_CORE, "workspace-scan",
             "--workspace", self.workspace],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        return json.loads(proc.stdout.decode())

    def test_unterminated_descriptor_frontmatter_warns_through_the_cli(self):
        # v38: the helper is unit-tested, but the wiring into the envelope is
        # what an executor actually reads. A finding is not a warning — this
        # must arrive in `warnings`, and the scan must still exit 0.
        write(os.path.join(self.workspace, "lore-workspace.md"),
              "---\ndescription: Test workspace\nrepos:\n  - git@x:o/a.git\n\nprose\n")
        envelope = self.scan_envelope()
        self.assertTrue(any("no closing ---" in w for w in envelope["warnings"]),
                        envelope["warnings"])

    def test_terminated_descriptor_produces_no_such_warning(self):
        envelope = self.scan_envelope()
        self.assertFalse([w for w in envelope["warnings"] if "no closing ---" in w],
                         envelope["warnings"])

    def test_detached_workspace_head_reports_s16_through_the_cli(self):
        self.git("checkout", "-q", "--detach", "HEAD")
        data = self.scan()
        found = findings_by_id(data["findings"])
        self.assertIn("S16", found)
        self.assertTrue(found["S16"]["data"]["head"])

    def test_attached_workspace_head_reports_no_s16(self):
        self.assertNotIn("S16", findings_by_id(self.scan()["findings"]))

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


class TestDuplicateBlockKey(unittest.TestCase):
    """A repeated `repos:` block must not discard the first block's URLs.

    v38 fix. `parse_frontmatter` reset the list on every `key:` header, so a
    hand-merged descriptor declaring repos in two blocks lost the first block
    silently — while `workspace-pull`'s awk parser kept both. The two parsers
    disagreeing about the declared repo set is the actual defect; those repos
    then read as undeclared (S5) despite being declared.
    """

    def test_second_repos_block_does_not_erase_the_first(self):
        from lr_core.common import parse_frontmatter
        fm = parse_frontmatter(
            "---\n"
            "description: w\n"
            "repos:\n"
            "  - git@example.com:x/one.git\n"
            "repos:\n"
            "  - git@example.com:x/two.git\n"
            "---\n\nbody\n")
        self.assertEqual(fm["repos"], ["git@example.com:x/one.git",
                                       "git@example.com:x/two.git"])

    def test_single_block_is_unchanged(self):
        from lr_core.common import parse_frontmatter
        fm = parse_frontmatter("---\nrepos:\n  - a\n  - b\n---\n")
        self.assertEqual(fm["repos"], ["a", "b"])

    def test_scalar_key_still_overwrites(self):
        from lr_core.common import parse_frontmatter
        fm = parse_frontmatter("---\ndescription: first\ndescription: second\n---\n")
        self.assertEqual(fm["description"], "second")


class TestListItemComments(unittest.TestCase):
    """Block-sequence items must be comment-stripped like the awk parser.

    v38 fix. `workspace-pull` strips a trailing ` # comment` from an unquoted
    item; the Python parser did not, so a commented declaration produced a URL
    with the comment baked in. Its derived dirname then matched nothing on
    disk, and a correctly cloned repo was reported missing (S6) forever.
    """

    def _repos(self, item):
        from lr_core.common import parse_frontmatter
        return parse_frontmatter("---\nrepos:\n  - %s\n---\n" % item)["repos"][0]

    def test_trailing_comment_is_stripped(self):
        self.assertEqual(self._repos("https://x/y.git  # primary repo"),
                         "https://x/y.git")

    def test_quoted_value_keeps_its_hash(self):
        # Inside quotes `#` is data, not a comment — the awk side agrees.
        self.assertEqual(self._repos('"https://x/y.git#frag"'),
                         "https://x/y.git#frag")

    def test_hash_without_leading_space_is_not_a_comment(self):
        # awk strips on `[[:space:]]+#` only, so this stays whole.
        self.assertEqual(self._repos("https://x/y.git#frag"),
                         "https://x/y.git#frag")

    def test_plain_url_is_untouched(self):
        self.assertEqual(self._repos("https://x/y.git"), "https://x/y.git")

    def test_commented_url_derives_a_usable_dirname(self):
        # The actual consequence the fix exists to prevent.
        self.assertEqual(ws.derive_dirname(self._repos("git@x:o/y.git  # note")),
                         "y")


class TestDeriveDirnameDotRule(unittest.TestCase):
    """A derived dirname may not start with a dot.

    v38 fix. `scan_children` skips dot-directories, so accepting `.hidden` here
    let `workspace-pull` clone a repo that every later pass treated as
    permanently missing (S6 forever) and that `.gitignore` maintenance never
    saw. Refusing the name reports it as S13 instead.
    """

    def test_leading_dot_is_refused(self):
        self.assertIsNone(ws.derive_dirname("git@example.com:x/.hidden.git"))
        self.assertIsNone(ws.derive_dirname("https://example.com/x/.config"))

    def test_dot_elsewhere_in_the_name_is_fine(self):
        self.assertEqual(ws.derive_dirname("git@example.com:x/my.repo.git"),
                         "my.repo")

    def test_ordinary_names_still_derive(self):
        self.assertEqual(ws.derive_dirname("git@example.com:x/lore-agents.git"),
                         "lore-agents")


class TestUnterminatedFrontmatter(unittest.TestCase):
    """The Python parser must warn where the awk parser already warns.

    v38 fix. `parse_frontmatter` degrades by consuming the rest of the file, so
    a descriptor that lost its closing `---` yields a plausible but wrong repo
    set with no signal at all on the Python side.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)

    def _write(self, content):
        path = os.path.join(self.tmp, "lore-workspace.md")
        write(path, content)
        return path

    def test_unterminated_is_detected(self):
        path = self._write("---\ndescription: w\nrepos:\n  - a\n\nprose\n")
        self.assertTrue(ws.frontmatter_unterminated(path))

    def test_terminated_is_not_flagged(self):
        path = self._write("---\ndescription: w\n---\n\nprose\n")
        self.assertFalse(ws.frontmatter_unterminated(path))

    def test_file_without_frontmatter_is_not_flagged(self):
        path = self._write("# just a heading\n")
        self.assertFalse(ws.frontmatter_unterminated(path))

    def test_missing_file_is_not_flagged(self):
        self.assertFalse(
            ws.frontmatter_unterminated(os.path.join(self.tmp, "nope.md")))


class TestS16DetachedWorkspaceHead(unittest.TestCase):
    """S16 — the workspace root itself on a detached HEAD.

    v38 addition. `git_state` recorded `detached` from the start but no finding
    ever read it. It is the one root state that makes the git section quiet
    rather than loud: no upstream means S2/S14 cannot fire, so their silence
    proves nothing, and a commit made detached is dropped by the next checkout.
    """

    def test_detached_root_reports_s16(self):
        data = base_data(git=dict(base_data()["git"], detached=True,
                                  head="abc1234", upstream=None,
                                  ahead=None, behind=None))
        found = findings_by_id(ws.build_findings(data))
        self.assertIn("S16", found)
        self.assertEqual(found["S16"]["severity"], "warn")
        self.assertEqual(found["S16"]["data"]["head"], "abc1234")

    def test_attached_root_is_quiet(self):
        self.assertNotIn("S16", findings_by_id(ws.build_findings(base_data())))

    def test_untracked_workspace_does_not_report_s16(self):
        # Not a git repo at all: S4 owns that state, and a detached flag that
        # never came from a real repo must not surface as a git-health finding.
        data = base_data(git=dict(base_data()["git"], tracked=False,
                                  own_root=False, detached=True))
        self.assertNotIn("S16", findings_by_id(ws.build_findings(data)))


class TestS8DetachedChild(unittest.TestCase):
    """S8 must cover a detached child, not just one on another branch.

    v38 fix. The off-branch comprehension required a truthy `current_branch`,
    which a detached child never has — silently exempting the worse state.
    """

    def _child(self, **kw):
        base = {"dirname": "repo", "git": True, "declared": True,
                "ignorable": True, "ignored": True, "origin": None,
                "default_branch": "main", "current_branch": None,
                "detached": False, "lore_repo": False,
                "escapes_workspace": False}
        base.update(kw)
        return base

    def test_detached_child_is_reported(self):
        data = base_data(children=[self._child(detached=True)])
        found = findings_by_id(ws.build_findings(data))
        self.assertIn("S8", found)
        self.assertTrue(found["S8"]["data"][0]["detached"])

    def test_detached_child_reported_even_without_known_default(self):
        data = base_data(children=[self._child(detached=True,
                                               default_branch=None)])
        self.assertIn("S8", findings_by_id(ws.build_findings(data)))

    def test_child_on_default_branch_is_quiet(self):
        data = base_data(children=[self._child(current_branch="main")])
        self.assertNotIn("S8", findings_by_id(ws.build_findings(data)))

    def test_child_on_other_branch_still_reported(self):
        data = base_data(children=[self._child(current_branch="feature")])
        found = findings_by_id(ws.build_findings(data))
        self.assertIn("S8", found)
        self.assertFalse(found["S8"]["data"][0]["detached"])

    def test_unknown_branch_without_detached_stays_quiet(self):
        # git could not answer: ignorance, not a detached head.
        data = base_data(children=[self._child()])
        self.assertNotIn("S8", findings_by_id(ws.build_findings(data)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
