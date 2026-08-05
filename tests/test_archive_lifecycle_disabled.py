#!/usr/bin/env python3
"""Deterministic contract tests for disabled automatic transcript archiving."""

import os
import unittest


HERE = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_DIR = os.environ.get(
    "LR_FRAMEWORK_DIR",
    os.path.abspath(os.path.join(HERE, "..", "..", "lore-framework")),
)


def read_framework_file(relative_path):
    with open(os.path.join(FRAMEWORK_DIR, relative_path), encoding="utf-8") as fh:
        return fh.read()


class AutomaticArchiveDisabledTests(unittest.TestCase):
    def test_manual_archive_command_is_retained_and_marked_dormant(self):
        script = read_framework_file("scripts/session-takeover")
        self.assertIn("def cmd_archive", script)
        self.assertIn("archive (dormant manual primitive)", script)
        self.assertIn("Summarize and finalize must not invoke it", script)

    def test_summarize_collects_usage_without_exporting_a_transcript(self):
        summarize = read_framework_file("docs/summarize.md")
        self.assertIn("Resolve usage metadata from the native session log", summarize)
        self.assertIn("--stats <scratch>/session-stats.json", summarize)
        self.assertNotIn("session-takeover archive <resolved-log>", summarize)
        self.assertNotIn("--archive-output", summarize)
        self.assertNotIn("archive:\n", summarize)

    def test_finalize_does_not_require_or_commit_an_archive(self):
        finalize = read_framework_file("docs/finalize.md")
        self.assertIn("must not create or commit a transcript archive", finalize)
        self.assertNotIn("archive/YYYY/MM", finalize)
        self.assertNotIn("usage`/`archive", finalize)

    def test_boot_and_lore_search_have_no_archive_policy(self):
        boot = read_framework_file("docs/agent-boot.md")
        search = read_framework_file("docs/lore-search.md")
        self.assertNotIn("archive/", boot)
        self.assertNotIn("archive/", search)


if __name__ == "__main__":
    unittest.main()
