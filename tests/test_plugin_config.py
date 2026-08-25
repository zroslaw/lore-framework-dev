#!/usr/bin/env python3
"""Tests for lr_core.plugin_config — committed project-scope plugin settings.

Lives in lore-framework-dev (dev repo), not the plugin repo — see
lore-framework/docs/conventions.md § Dev-Only Artifacts. Stdlib-only
(unittest), matching test_workspace_scan.py. The plugin under test is located
via $LR_FRAMEWORK_DIR, defaulting to the sibling ../lore-framework.

What these tests are actually defending. The module writes into two files it
does not own — `.claude/settings.json` and `.cursor/settings.json` carry a
team's permissions, hooks and env. The failure that matters is not "the plugin
was not enabled", it is "someone's hooks disappeared during a converge". So the
preservation and refusal cases below are the load-bearing ones; the happy path
is the cheap part.

Run:  python3 tests/test_plugin_config.py -v
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
from lr_core import plugin_config as pc  # noqa: E402


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write(path, text):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class TempWorkspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ws = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    @property
    def claude(self):
        return os.path.join(self.ws, pc.CLAUDE_SETTINGS_REL)

    @property
    def cursor(self):
        return os.path.join(self.ws, pc.CURSOR_SETTINGS_REL)


class TestFreshWorkspace(TempWorkspace):
    def test_creates_both_files(self):
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertEqual(errors, [])
        actions = {row["engine"]: row["action"] for row in data["files"]}
        self.assertEqual(actions, {"claude": "created", "cursor": "created"})
        self.assertTrue(os.path.isfile(self.claude))
        self.assertTrue(os.path.isfile(self.cursor))

    def test_claude_payload_shape(self):
        pc.apply_plugin_config(self.ws)
        doc = read_json(self.claude)
        self.assertIs(doc["enabledPlugins"][pc.CLAUDE_PLUGIN_KEY], True)
        market = doc["extraKnownMarketplaces"][pc.MARKETPLACE_NAME]
        self.assertEqual(market["source"],
                         {"source": "git", "url": pc.GIT_URL_FETCH})
        self.assertIs(market["autoUpdate"], True)

    def test_cursor_payload_shape(self):
        pc.apply_plugin_config(self.ws)
        entry = read_json(self.cursor)["plugins"][pc.CURSOR_PLUGIN_KEY]
        self.assertIs(entry["enabled"], True)
        self.assertEqual(entry["gitUrl"], pc.GIT_URL)

    def test_no_git_ref_pins_the_payload(self):
        # Omitting gitRef tracks the default branch. A pinned ref here would
        # silently freeze every teammate at one commit forever.
        pc.apply_plugin_config(self.ws)
        entry = read_json(self.cursor)["plugins"][pc.CURSOR_PLUGIN_KEY]
        self.assertNotIn("gitRef", entry)

    def test_keys_are_not_interchangeable(self):
        # `<plugin>@<marketplace>` on Claude, `<marketplace>/<plugin>` on
        # Cursor. The order is genuinely reversed; a "consistency" fix breaks
        # one engine silently.
        self.assertEqual(pc.CLAUDE_PLUGIN_KEY, "lr@lore-framework")
        self.assertEqual(pc.CURSOR_PLUGIN_KEY, "lore-framework/lr")

    def test_files_end_with_single_newline(self):
        pc.apply_plugin_config(self.ws)
        for path in (self.claude, self.cursor):
            with open(path, "r", encoding="utf-8") as handle:
                raw = handle.read()
            self.assertTrue(raw.endswith("\n"))
            self.assertFalse(raw.endswith("\n\n"))


class TestIdempotency(TempWorkspace):
    def test_second_run_is_unchanged(self):
        pc.apply_plugin_config(self.ws)
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertEqual(errors, [])
        actions = {row["action"] for row in data["files"]}
        self.assertEqual(actions, {"unchanged"})

    def test_second_run_does_not_rewrite_bytes(self):
        pc.apply_plugin_config(self.ws)
        before = {p: open(p, "rb").read() for p in (self.claude, self.cursor)}
        mtimes = {p: os.stat(p).st_mtime_ns for p in before}
        pc.apply_plugin_config(self.ws)
        for path, blob in before.items():
            self.assertEqual(open(path, "rb").read(), blob)
            self.assertEqual(os.stat(path).st_mtime_ns, mtimes[path])

    def test_existing_keys_leave_formatting_untouched(self):
        # A hand-written file that already carries our keys is left exactly as
        # the team wrote it. Normalising it to our layout would push a
        # whitespace-only diff through a shared settings file for no gain.
        raw = ('{"plugins":{"%s":{"enabled":true,"gitUrl":"%s"}}}'
               % (pc.CURSOR_PLUGIN_KEY, pc.GIT_URL))
        write(self.cursor, raw)
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertEqual(errors, [])
        row = [r for r in data["files"] if r["engine"] == "cursor"][0]
        self.assertEqual(row["action"], "unchanged")
        with open(self.cursor, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), raw)

    def test_partial_file_is_completed_without_losing_layout_elsewhere(self):
        # Only the missing key is added; the write is a real one.
        write(self.claude, json.dumps({"hooks": {"Stop": []}}, indent=2) + "\n")
        data, _ = pc.apply_plugin_config(self.ws)
        row = [r for r in data["files"] if r["engine"] == "claude"][0]
        self.assertEqual(row["action"], "updated")
        doc = read_json(self.claude)
        self.assertEqual(doc["hooks"], {"Stop": []})
        self.assertIs(doc["enabledPlugins"][pc.CLAUDE_PLUGIN_KEY], True)


class TestPreservation(TempWorkspace):
    """The reason this module exists as code rather than prose."""

    def test_preserves_unrelated_claude_keys(self):
        write(self.claude, json.dumps({
            "permissions": {"allow": ["Bash(ls)"], "deny": ["Bash(rm)"]},
            "hooks": {"Stop": [{"command": "echo done"}]},
            "env": {"FOO": "bar"},
        }, indent=2) + "\n")
        pc.apply_plugin_config(self.ws)
        doc = read_json(self.claude)
        self.assertEqual(doc["permissions"], {"allow": ["Bash(ls)"],
                                              "deny": ["Bash(rm)"]})
        self.assertEqual(doc["hooks"], {"Stop": [{"command": "echo done"}]})
        self.assertEqual(doc["env"], {"FOO": "bar"})
        self.assertIs(doc["enabledPlugins"][pc.CLAUDE_PLUGIN_KEY], True)

    def test_preserves_unrelated_cursor_keys(self):
        write(self.cursor, json.dumps({
            "permissions": {"allow": ["Shell(ls)"]},
            "plugins": {"other-market/other": {"enabled": True}},
        }, indent=2) + "\n")
        pc.apply_plugin_config(self.ws)
        doc = read_json(self.cursor)
        self.assertEqual(doc["permissions"], {"allow": ["Shell(ls)"]})
        self.assertEqual(doc["plugins"]["other-market/other"], {"enabled": True})
        self.assertIs(doc["plugins"][pc.CURSOR_PLUGIN_KEY]["enabled"], True)

    def test_preserves_sibling_marketplaces(self):
        write(self.claude, json.dumps({
            "extraKnownMarketplaces": {
                "someone-else": {"source": {"source": "git", "url": "https://x/y.git"}}
            },
            "enabledPlugins": {"other@someone-else": True},
        }, indent=2) + "\n")
        pc.apply_plugin_config(self.ws)
        doc = read_json(self.claude)
        self.assertIn("someone-else", doc["extraKnownMarketplaces"])
        self.assertIs(doc["enabledPlugins"]["other@someone-else"], True)
        self.assertIn(pc.MARKETPLACE_NAME, doc["extraKnownMarketplaces"])

    def test_respects_a_deliberate_disable(self):
        # A user who set this false turned the plugin off on purpose.
        # Converging it back to true would make the choice unstickable.
        write(self.claude, json.dumps(
            {"extraKnownMarketplaces": {pc.MARKETPLACE_NAME: {"source": {}}},
             "enabledPlugins": {pc.CLAUDE_PLUGIN_KEY: False}}, indent=2) + "\n")
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertEqual(errors, [])
        self.assertIs(read_json(self.claude)["enabledPlugins"][pc.CLAUDE_PLUGIN_KEY],
                      False)
        row = [r for r in data["files"] if r["engine"] == "claude"][0]
        self.assertIn("enabledPlugins.%s" % pc.CLAUDE_PLUGIN_KEY, row["kept"])

    def test_respects_a_customised_cursor_entry(self):
        write(self.cursor, json.dumps({"plugins": {
            pc.CURSOR_PLUGIN_KEY: {"enabled": True, "gitUrl": pc.GIT_URL,
                                   "gitRef": "release"}}}, indent=2) + "\n")
        pc.apply_plugin_config(self.ws)
        entry = read_json(self.cursor)["plugins"][pc.CURSOR_PLUGIN_KEY]
        self.assertEqual(entry["gitRef"], "release")


class TestRefusals(TempWorkspace):
    def test_unparseable_file_is_never_clobbered(self):
        raw = '{\n  // a comment Cursor allows and json.loads does not\n  "plugins": {}\n}\n'
        write(self.cursor, raw)
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertTrue(errors)
        with open(self.cursor, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), raw)
        row = [r for r in data["files"] if r["engine"] == "cursor"][0]
        self.assertEqual(row["action"], "error")

    def test_one_bad_file_does_not_block_the_other(self):
        write(self.cursor, "{ not json")
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertTrue(errors)
        actions = {row["engine"]: row["action"] for row in data["files"]}
        self.assertEqual(actions["cursor"], "error")
        self.assertEqual(actions["claude"], "created")

    def test_non_object_top_level_is_refused(self):
        write(self.claude, "[1, 2, 3]\n")
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertTrue(errors)
        row = [r for r in data["files"] if r["engine"] == "claude"][0]
        self.assertEqual(row["action"], "error")
        with open(self.claude, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "[1, 2, 3]\n")

    def test_conflicting_section_type_is_refused(self):
        write(self.claude, json.dumps({"enabledPlugins": "yes"}, indent=2) + "\n")
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertTrue(errors)
        row = [r for r in data["files"] if r["engine"] == "claude"][0]
        self.assertEqual(row["action"], "error")
        self.assertEqual(read_json(self.claude), {"enabledPlugins": "yes"})

    def test_empty_file_is_treated_as_empty_object(self):
        write(self.claude, "")
        data, errors = pc.apply_plugin_config(self.ws)
        self.assertEqual(errors, [])
        self.assertIs(read_json(self.claude)["enabledPlugins"][pc.CLAUDE_PLUGIN_KEY],
                      True)


class TestDryRun(TempWorkspace):
    def test_dry_run_writes_nothing(self):
        data, errors = pc.apply_plugin_config(self.ws, dry_run=True)
        self.assertEqual(errors, [])
        self.assertTrue(data["dry_run"])
        self.assertFalse(os.path.exists(self.claude))
        self.assertFalse(os.path.exists(self.cursor))

    def test_dry_run_reports_would_be_outcomes(self):
        # A dry run whose counters read "nothing to do" is worse than no dry
        # run at all: it reports the outcome of not acting.
        data, _ = pc.apply_plugin_config(self.ws, dry_run=True)
        actions = {row["engine"]: row["action"] for row in data["files"]}
        self.assertEqual(actions, {"claude": "created", "cursor": "created"})
        row = [r for r in data["files"] if r["engine"] == "claude"][0]
        self.assertIn("enabledPlugins.%s" % pc.CLAUDE_PLUGIN_KEY, row["added"])


class TestCoverageHonesty(TempWorkspace):
    def test_codex_is_reported_unsupported(self):
        # Two engines out of three reads as "all of them" to anyone who does
        # not already know there are three.
        data, _ = pc.apply_plugin_config(self.ws)
        self.assertIn("codex", data["unsupported_engines"])
        self.assertNotIn("codex", {row["engine"] for row in data["files"]})


class TestCheck(TempWorkspace):
    def test_reports_both_missing_on_a_fresh_workspace(self):
        result = pc.check_plugin_config(self.ws)
        self.assertEqual(sorted(result["missing"]),
                         sorted([pc.CLAUDE_SETTINGS_REL, pc.CURSOR_SETTINGS_REL]))
        self.assertEqual(result["disabled"], [])
        self.assertEqual(result["unreadable"], [])

    def test_clean_after_apply(self):
        pc.apply_plugin_config(self.ws)
        result = pc.check_plugin_config(self.ws)
        self.assertEqual(result, {"missing": [], "unreadable": [], "disabled": []})

    def test_disabled_is_not_reported_as_missing(self):
        pc.apply_plugin_config(self.ws)
        doc = read_json(self.claude)
        doc["enabledPlugins"][pc.CLAUDE_PLUGIN_KEY] = False
        write(self.claude, json.dumps(doc, indent=2) + "\n")
        result = pc.check_plugin_config(self.ws)
        self.assertEqual(result["disabled"], [pc.CLAUDE_SETTINGS_REL])
        self.assertEqual(result["missing"], [])

    def test_marketplace_without_enable_counts_as_missing(self):
        write(self.claude, json.dumps(
            {"extraKnownMarketplaces": {pc.MARKETPLACE_NAME: {"source": {}}}},
            indent=2) + "\n")
        result = pc.check_plugin_config(self.ws)
        self.assertIn(pc.CLAUDE_SETTINGS_REL, result["missing"])

    def test_enable_without_marketplace_counts_as_missing(self):
        # Claude can only enable a plugin whose marketplace it knows, so an
        # enable line on its own is not a working configuration.
        write(self.claude, json.dumps(
            {"enabledPlugins": {pc.CLAUDE_PLUGIN_KEY: True}}, indent=2) + "\n")
        result = pc.check_plugin_config(self.ws)
        self.assertIn(pc.CLAUDE_SETTINGS_REL, result["missing"])

    def test_unreadable_is_not_silently_clean(self):
        write(self.cursor, "{ not json")
        result = pc.check_plugin_config(self.ws)
        self.assertEqual(result["unreadable"], [pc.CURSOR_SETTINGS_REL])


class TestS18Finding(TempWorkspace):
    """The scanner wiring: `plugin_config` facts becoming finding S18."""

    def build(self, plugin_cfg):
        """Re-derive findings from a real scan, with plugin_config swapped.

        Built from `run_workspace_scan` rather than a hand-written dict so the
        fixture cannot drift out of shape as the scanner grows keys.
        """
        from lr_core import workspace_scan as ws
        os.environ["HOME"] = self.ws  # keep shortcut_inventory off the real home
        # A directory with no descriptor short-circuits to applicable:false and
        # emits no findings at all, so the fixture needs a real one.
        write(os.path.join(self.ws, "lore-workspace.md"),
              "---\ndescription: fixture workspace\n---\n\n# fixture\n")
        data, _ = ws.run_workspace_scan(self.ws)
        self.assertTrue(data["applicable"])
        if plugin_cfg is None:
            data.pop("plugin_config", None)
        else:
            data["plugin_config"] = plugin_cfg
        return [f for f in ws.build_findings(data) if f["id"] == "S18"]

    def setUp(self):
        super().setUp()
        self._home = os.environ.get("HOME")
        self.addCleanup(lambda: os.environ.__setitem__("HOME", self._home)
                        if self._home is not None else None)

    def test_missing_fires(self):
        rows = self.build({"missing": [pc.CLAUDE_SETTINGS_REL],
                           "unreadable": [], "disabled": []})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["severity"], "info")
        self.assertEqual(rows[0]["data"]["missing"], [pc.CLAUDE_SETTINGS_REL])

    def test_unreadable_fires(self):
        rows = self.build({"missing": [], "unreadable": [pc.CURSOR_SETTINGS_REL],
                           "disabled": []})
        self.assertEqual(len(rows), 1)

    def test_disabled_alone_does_not_fire(self):
        # An explicit false is a user's choice, not drift. Reporting it would
        # route them to a fix that undoes what they meant.
        rows = self.build({"missing": [], "unreadable": [],
                           "disabled": [pc.CLAUDE_SETTINGS_REL]})
        self.assertEqual(rows, [])

    def test_clean_does_not_fire(self):
        rows = self.build({"missing": [], "unreadable": [], "disabled": []})
        self.assertEqual(rows, [])

    def test_absent_block_does_not_crash(self):
        self.assertEqual(self.build(None), [])


class TestManagedPaths(TempWorkspace):
    def test_both_settings_files_are_managed(self):
        # They must be in MANAGED_PATHS or `workspace-push` never publishes
        # them and the whole feature stops at the author's own machine.
        from lr_core import workspace_scan as ws
        for rel in (pc.CLAUDE_SETTINGS_REL, pc.CURSOR_SETTINGS_REL):
            self.assertIn(rel, ws.MANAGED_PATHS)
            self.assertTrue(ws.is_managed(rel))


class TestCliEnvelope(TempWorkspace):
    def run_cli(self, *extra):
        proc = subprocess.run(
            [sys.executable, LR_CORE, "workspace-plugin-config",
             "--workspace", self.ws] + list(extra),
            capture_output=True, text=True)
        return proc, json.loads(proc.stdout)

    def test_success_envelope(self):
        proc, payload = self.run_cli()
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["data"]["workspace"], os.path.realpath(self.ws)
                         if os.path.realpath(self.ws) == payload["data"]["workspace"]
                         else payload["data"]["workspace"])

    def test_bad_file_is_ok_false_but_exit_zero(self):
        # A determinate negative answer, not a fatal: the caller can still act
        # on the engine that did converge.
        write(self.cursor, "{ not json")
        proc, payload = self.run_cli()
        self.assertEqual(proc.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["errors"])
        self.assertNotIn("fatal", payload)

    def test_missing_workspace_is_ok_false(self):
        proc = subprocess.run(
            [sys.executable, LR_CORE, "workspace-plugin-config",
             "--workspace", os.path.join(self.ws, "nope")],
            capture_output=True, text=True)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["data"]["applicable"])

    def test_dry_run_via_cli_writes_nothing(self):
        proc, payload = self.run_cli("--dry-run")
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(payload["data"]["dry_run"])
        self.assertFalse(os.path.exists(self.claude))


if __name__ == "__main__":
    unittest.main(verbosity=2)
