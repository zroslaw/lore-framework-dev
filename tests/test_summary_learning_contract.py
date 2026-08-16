#!/usr/bin/env python3
"""Deterministic contract checks for the session-summary Learning audit."""

import os
import unittest


HERE = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_DIR = os.path.abspath(
    os.environ.get("LR_FRAMEWORK_DIR")
    or os.path.join(HERE, "..", "..", "lore-framework")
)


def read_framework_file(relative_path):
    with open(os.path.join(FRAMEWORK_DIR, relative_path), encoding="utf-8") as fh:
        return fh.read()


class SummaryLearningContractTests(unittest.TestCase):
    def test_host_summary_requires_a_compact_learning_audit(self):
        summarize = read_framework_file("docs/summarize.md")

        self.assertIn("The **Learning** section is mandatory", summarize)
        self.assertIn("## Learning", summarize)
        self.assertIn("**What mattered:**", summarize)
        self.assertIn("**Lore changes:**", summarize)
        self.assertIn("**Not merged:**", summarize)
        self.assertIn("**Issues:**", summarize)
        self.assertIn("consolidated or simplified", summarize)
        self.assertIn("category-only phrase", summarize)
        self.assertIn("one subsection per active agent", summarize)

    def test_merge_and_finalize_preserve_the_evidence_handoff(self):
        merge = read_framework_file("docs/process-merge.md")
        finalize = read_framework_file("docs/finalize.md")
        cursor = read_framework_file("docs/engines/cursor.md")
        cursor_words = " ".join(cursor.split())
        summarize = read_framework_file("docs/summarize.md")

        self.assertIn("Merge handoff", merge)
        self.assertIn("- What mattered:", merge)
        self.assertIn("- Unmerged:", merge)
        self.assertIn("- Anomalies:", merge)
        self.assertIn("consolidation or simplification", merge)
        self.assertIn("current-session topic set as authoritative", merge)
        self.assertIn("Only with that complete set", merge)
        self.assertIn("If the caller marked the set `Failed`", merge)
        self.assertIn("If it marked", merge)
        self.assertIn("Preserve one Reflection outcome", finalize)
        self.assertIn("current-session reflection paths", finalize)
        self.assertIn("mark the set `Failed`", finalize)
        self.assertIn("Preserve every Merge handoff", finalize)
        self.assertIn("required Merge handoff", cursor_words)
        self.assertIn("Current-session reflection topics", cursor_words)
        self.assertIn("Retain every return", cursor_words)
        self.assertIn("`updated`, `consolidated`, or `simplified`", summarize)
        self.assertIn("Earlier missing or failed phase evidence always takes precedence", summarize)

    def test_absence_is_not_reported_as_no_learning(self):
        summarize = read_framework_file("docs/summarize.md")

        self.assertIn(
            "Learning was not assessed because no completed reflection-and-merge handoff was available.",
            summarize,
        )
        self.assertIn("Never translate absence into \"no learning.\"", summarize)

if __name__ == "__main__":
    unittest.main()
