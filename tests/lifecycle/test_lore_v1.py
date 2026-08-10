#!/usr/bin/env python3
"""Lifecycle scenarios 30-34: Lore v1 boot, merge adoption, and grooming."""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import (
    AGENT_NAME, GROOM_ALL_PROPOSAL_PROMPT, GROOM_APPLY_PROMPT,
    GROOM_DRY_RUN_PROMPT, LORE_MAP_BOOT_PROMPT, LORE_MERGE_PROMPT,
    SKIP_REASON, build_fixture, run_engine, seed_reflection,
)


DURABLE_GROOM_FACT = "The deployment timeout is exactly 47 seconds because the proxy closes at 50."


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def _commit_fixture(fx, message):
    subprocess.run(["git", "-C", fx.repo, "add", "-A"], check=True)
    subprocess.run([
        "git", "-C", fx.repo,
        "-c", "user.name=lr-tests", "-c", "user.email=lr-tests@localhost",
        "commit", "-m", message,
    ], check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "-C", fx.repo, "push", "origin", "main"],
                   check=True, stdout=subprocess.PIPE)


def make_v1(fx, verbose=False):
    _write(os.path.join(fx.agent_dir, "lore-context.md"), (
        "---\n"
        "lore: 1\n"
        "type: context\n"
        "summary: \"Fixture working knowledge and navigation.\"\n"
        "---\n\n"
        "# Lore Context\n\n"
        "Context codeword: CTX-CANARY-9182.\n\n"
        "[Build knowledge](lore/build.md)\n"
    ))
    _write(os.path.join(fx.agent_dir, "lore", "build.md"), (
        "---\n"
        "lore: 1\n"
        "type: area\n"
        "summary: \"Build and deployment tools used by the fixture project.\"\n"
        "parent: lore-context.md\n"
        "---\n\n"
        "# Build\n\n"
        "The fixture uses explicit build and deployment tooling.\n\n"
        "[Build tool](espresso-build-tool.md)\n"
    ))
    _write(os.path.join(fx.agent_dir, "lore", "espresso-build-tool.md"), (
        "---\n"
        "lore: 1\n"
        "type: topic\n"
        "summary: \"Records the fixture project's selected build tool.\"\n"
        "parent: lore/build.md\n"
        "---\n\n"
        "# Espresso Build Tool\n\n"
        "The fixture project's build tool is called **espresso-tamper**. It was chosen over "
        "portafilter for its watch mode.\n"
    ))
    if verbose:
        filler = ("This is an important topic and it is useful to remember. " * 14)
        _write(os.path.join(fx.agent_dir, "lore", "verbose.md"), (
            "---\n"
            "lore: 1\n"
            "type: topic\n"
            "summary: \"Defines the deployment timeout and why it is bounded.\"\n"
            "parent: lore/build.md\n"
            "---\n\n"
            "# Deployment Timeout\n\n"
            + DURABLE_GROOM_FACT + "\n\n" + filler + "\n\n" + filler + "\n"
        ))
    _commit_fixture(fx, "fixture: convert to Lore v1")


def tree_hash(agent_dir):
    digest = hashlib.sha256()
    for root, dirs, files in os.walk(agent_dir):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            path = os.path.join(root, name)
            digest.update(os.path.relpath(path, agent_dir).encode())
            with open(path, "rb") as handle:
                digest.update(handle.read())
    return digest.hexdigest()


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class LoreV1Scenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-lore-v1-")
        if os.environ.get("LR_KEEP_FIXTURES"):
            print(f"\n  [fixture kept] {tmp}", file=sys.stderr)
        else:
            self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.tmp = tmp

    def test_30_boot_receives_compact_complete_map(self):
        fx = build_fixture(self.tmp)
        make_v1(fx)
        result = run_engine(fx.workspace, LORE_MAP_BOOT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {result.summary()}")
        self.assertEqual(result.exit_code, 0, result.stderr[-500:])
        self.assertIn(
            "Booted: test-agent — Fixture agent for framework lifecycle tests",
            result.text,
        )
        self.assertRegex(
            result.text,
            re.compile(
                r"Agent Lore: 2 topics · ~[1-9][0-9]*k tokens total "
                r"· coverage 100\.0% \(complete\)\n"
                r"Context Footprint: ~[1-9][0-9]*k tokens total "
                r"· ~[1-9][0-9]*k lore context · ~[1-9][0-9]*k lore map "
                r"· ~[1-9][0-9]*k role · ~[1-9][0-9]*k system prompts"
            ),
        )
        self.assertIn("LORE-COVERAGE: complete", result.text)
        self.assertIn("TOP-AREA: lore/build.md", result.text)

    def test_31_merge_integrates_into_a_legacy_agent(self):
        fx = build_fixture(self.tmp)
        seed_reflection(fx, "release-tool.md", (
            "# Release Tool\n\n"
            "The fixture now deploys with **lore-release-7319** because it provides atomic "
            "rollback. This is a new durable release-operations fact.\n"
        ))
        result = run_engine(fx.workspace, LORE_MERGE_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {result.summary()}")
        self.assertEqual(result.exit_code, 0, result.stderr[-500:])
        found = []
        for dirpath, _, files in os.walk(os.path.join(fx.agent_dir, "lore")):
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as handle:
                    content = handle.read()
                if "lore-release-7319" in content:
                    found.append(content)
        self.assertTrue(found, "merged durable fact not found")

    def test_32_groom_dry_run_is_byte_identical(self):
        fx = build_fixture(self.tmp)
        make_v1(fx, verbose=True)
        before = tree_hash(fx.agent_dir)
        result = run_engine(fx.workspace, GROOM_DRY_RUN_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {result.summary()}")
        self.assertEqual(result.exit_code, 0, result.stderr[-500:])
        self.assertIn("GROOM-DRY-RUN-DONE", result.text)
        self.assertEqual(tree_hash(fx.agent_dir), before,
                         "groom --dry-run changed agent files")

    def test_33_groom_apply_removes_slop_and_preserves_durable_fact(self):
        fx = build_fixture(self.tmp)
        make_v1(fx, verbose=True)
        path = os.path.join(fx.agent_dir, "lore", "verbose.md")
        with open(path, encoding="utf-8") as handle:
            before = handle.read()
        result = run_engine(fx.workspace, GROOM_APPLY_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {result.summary()}")
        self.assertEqual(result.exit_code, 0, result.stderr[-500:])
        with open(path, encoding="utf-8") as handle:
            after = handle.read()
        self.assertIn(DURABLE_GROOM_FACT, after)
        self.assertLess(len(after), len(before), "grooming did not remove planted filler")
        self.assertIn("lore: 1", after)

    def test_34_whole_lore_requires_approval_before_writes(self):
        fx = build_fixture(self.tmp)
        make_v1(fx, verbose=True)
        before = tree_hash(fx.agent_dir)
        result = run_engine(fx.workspace, GROOM_ALL_PROPOSAL_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {result.summary()}")
        self.assertEqual(result.exit_code, 0, result.stderr[-500:])
        self.assertIn("GROOM-PROPOSAL-DONE", result.text)
        self.assertEqual(tree_hash(fx.agent_dir), before,
                         "whole-Lore mode wrote before proposal approval")


if __name__ == "__main__":
    unittest.main()
