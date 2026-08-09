#!/usr/bin/env python3
"""Deterministic lr-core contracts for Lore v1 maps and grooming worksets."""

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest


FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework"))
LR_CORE = os.path.join(FRAMEWORK_DIR, "scripts", "lr-core")


def load_lr_core():
    spec = importlib.util.spec_from_loader(
        "lr_core_lore_v1_entry",
        importlib.machinery.SourceFileLoader("lr_core_lore_v1_entry", LR_CORE))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(textwrap.dedent(content).lstrip("\n"))


def frontmatter(kind, summary, parent=None, lore=1):
    lines = ["---", "lore: %s" % lore, "type: %s" % kind,
             'summary: "%s"' % summary]
    if parent is not None:
        lines.append("parent: %s" % parent)
    return "\n".join(lines + ["---", ""])


class LoreV1Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lore-v1-")
        self.agent = os.path.join(self.tmp.name, "agents", "alpha")
        os.makedirs(os.path.join(self.agent, "lore"))
        self.core = load_lr_core()

    def tearDown(self):
        self.tmp.cleanup()

    def complete_fixture(self):
        write(os.path.join(self.agent, "lore-context.md"),
              frontmatter("context", "Root navigation.") +
              "# Context\n\n[Engineering](lore/engineering.md)\n")
        write(os.path.join(self.agent, "lore", "engineering.md"),
              frontmatter("area", "Engineering decisions.", "lore-context.md") +
              "# Engineering\n\n[Build](build.md)\n")
        write(os.path.join(self.agent, "lore", "build.md"),
              frontmatter("topic", "How builds work.", "lore/engineering.md") +
              "# Build\n\nSee [context](../lore-context.md).\n")

    def test_token_estimate_counts_unicode_characters(self):
        self.assertEqual(self.core.estimate_tokens("abcde"), 2)
        self.assertEqual(self.core.estimate_tokens("😀😀😀😀"), 1)
        self.assertEqual(self.core.estimate_tokens(""), 0)

    def test_frontmatter_accepts_bom_crlf_and_free_key_order(self):
        text = ("\ufeff---\r\nsummary: \"Useful summary.\"\r\n"
                "parent: lore/parent.md\r\ntype: topic\r\nlore: 1\r\n---\r\n# T\r\n")
        parsed = self.core.parse_lore_frontmatter(text, "lore/t.md")
        self.assertEqual(parsed["kind"], "candidate_v1")
        self.assertFalse(parsed["issues"])
        self.assertEqual(parsed["metadata"]["parent"], "lore/parent.md")

    def test_frontmatter_accepts_trailing_scalar_whitespace(self):
        text = ("---\nlore: 1  \ntype: topic \t\n"
                "summary: \"Useful summary.\"   \n"
                "parent: lore/parent.md  \n---\n# T\n")
        parsed = self.core.parse_lore_frontmatter(text, "lore/t.md")
        self.assertFalse(parsed["issues"])
        self.assertEqual(parsed["metadata"]["type"], "topic")
        self.assertEqual(parsed["metadata"]["summary"], "Useful summary.")
        self.assertEqual(parsed["metadata"]["parent"], "lore/parent.md")

    def test_malformed_summary_produces_one_finding(self):
        text = ("---\nlore: 1\ntype: topic\nsummary: \"bad\\q\"\n"
                "parent: lore/parent.md\n---\n# T\n")
        parsed = self.core.parse_lore_frontmatter(text, "lore/t.md")
        issues = [item[0] for item in parsed["issues"]]
        self.assertEqual(issues.count("invalid_summary"), 1)

    def test_frontmatter_rejects_unknown_duplicate_and_unsafe_values(self):
        cases = [
            ("unknown_frontmatter_key", "extra: value\n"),
            ("duplicate_frontmatter_key", "summary: \"Again.\"\n"),
            ("invalid_parent_path", "", "../escape.md"),
            ("summary_too_long", "", None, "x" * 241),
            ("invalid_summary", "", None, "\\ud800"),
        ]
        for case in cases:
            issue = case[0]
            parent = case[2] if len(case) > 2 and case[2] is not None else "lore/area.md"
            summary = case[3] if len(case) > 3 else "Summary."
            encoded = ('"\\ud800"' if summary == "\\ud800"
                       else self.core.json.dumps(summary))
            text = ("---\nlore: 1\ntype: topic\nsummary: %s\nparent: %s\n%s---\n"
                    % (encoded, parent, case[1]))
            parsed = self.core.parse_lore_frontmatter(text, "lore/t.md")
            self.assertIn(issue, [item[0] for item in parsed["issues"]], case)

    def test_no_lore_field_is_legacy_even_with_other_frontmatter(self):
        parsed = self.core.parse_lore_frontmatter(
            "---\ntags: [old]\n---\n# Legacy\n", "lore/legacy.md")
        self.assertEqual(parsed["kind"], "legacy")
        self.assertFalse(parsed["issues"])

    def test_recursive_discovery_skips_hidden_files_dirs_and_symlinks(self):
        write(os.path.join(self.agent, "lore-context.md"), "# Legacy\n")
        write(os.path.join(self.agent, "lore", "nested", "topic.md"), "# Topic\n")
        write(os.path.join(self.agent, "lore", ".hidden.md"), "# Hidden\n")
        write(os.path.join(self.agent, "lore", ".hidden", "topic.md"), "# Hidden\n")
        os.symlink(os.path.join(self.agent, "lore", "nested", "topic.md"),
                   os.path.join(self.agent, "lore", "linked.md"))
        paths = [path for path, _ in self.core.discover_lore_files(self.agent)]
        self.assertEqual(paths, ["lore-context.md", "lore/nested/topic.md"])

    def test_legacy_scan_also_finds_nested_topics(self):
        write(os.path.join(self.agent, "lore", "nested", "topic.md"), "# Nested\n")
        data, error = self.core.scan_lore(self.agent)
        self.assertIsNone(error)
        self.assertEqual([item["file"] for item in data["topics"]],
                         ["nested/topic.md"])

    def test_complete_nested_taxonomy_metrics_and_links(self):
        self.complete_fixture()
        graph = self.core.build_lore_graph(self.agent)
        coverage = self.core.lore_coverage(graph)
        self.assertEqual(coverage["status"], "complete")
        self.assertIn("expand compact entries", coverage["guidance"])
        self.assertEqual(coverage["files"]["mapped"], 3)
        self.assertEqual(graph["nodes"]["lore-context.md"]["children"],
                         ["lore/engineering.md"])
        self.assertEqual(graph["nodes"]["lore/engineering.md"]["children"],
                         ["lore/build.md"])
        expected = sum(graph["nodes"][path]["estimated_tokens"] for path in graph["nodes"])
        self.assertEqual(graph["nodes"]["lore-context.md"]["subtree_estimated_tokens"],
                         expected)
        self.assertIn("lore/engineering.md",
                      graph["nodes"]["lore-context.md"]["outbound"])
        self.assertIn("lore/build.md",
                      graph["nodes"]["lore/engineering.md"]["outbound"])

    def test_taxonomy_depth_is_not_limited_by_python_recursion(self):
        write(os.path.join(self.agent, "lore-context.md"),
              frontmatter("context", "Deep root.") + "# Context\n")
        parent = "lore-context.md"
        depth = 1050
        for index in range(depth):
            rel = "lore/deep-%04d.md" % index
            write(os.path.join(self.agent, *rel.split("/")),
                  frontmatter("area", "Depth %d." % index, parent) +
                  "# Depth %d\n" % index)
            parent = rel
        graph = self.core.build_lore_graph(self.agent)
        detailed = self.core.detailed_lore_map(graph)
        current = detailed["root"]
        for _ in range(depth):
            current = current["children"][0]
        self.assertEqual(current["file"], "lore/deep-1049.md")
        rendered = self.core.yaml_dump(detailed)
        self.assertIn('file: "lore/deep-1049.md"', rendered)

    def test_snapshot_hashes_exact_bytes_including_bom_and_crlf(self):
        self.complete_fixture()
        path = os.path.join(self.agent, "lore", "build.md")
        raw = ("\ufeff---\r\nlore: 1\r\ntype: topic\r\n"
               "summary: \"Raw byte hash.\"\r\nparent: lore/engineering.md\r\n"
               "---\r\n# Raw\r\n").encode("utf-8")
        with open(path, "wb") as handle:
            handle.write(raw)
        graph = self.core.build_lore_graph(self.agent)
        self.assertEqual(graph["nodes"]["lore/build.md"]["sha256"],
                         self.core.hashlib.sha256(raw).hexdigest())

    def test_uncommitted_unicode_path_is_detected_without_git_quoting(self):
        self.complete_fixture()
        write(os.path.join(self.tmp.name, "lore-repo.md"),
              "---\ndescription: Fixture\nversion: 36\n---\n")
        unicode_path = os.path.join(self.agent, "lore", "café.md")
        write(unicode_path,
              frontmatter("topic", "Unicode path.", "lore/engineering.md") + "# Café\n")
        subprocess.run(["git", "init", "-q", self.tmp.name], check=True)
        subprocess.run(["git", "-C", self.tmp.name, "add", "-A"], check=True)
        subprocess.run([
            "git", "-C", self.tmp.name, "-c", "user.name=Test",
            "-c", "user.email=test@example.com", "commit", "-qm", "fixture",
        ], check=True)
        with open(unicode_path, "a", encoding="utf-8") as handle:
            handle.write("Changed.\n")
        graph = self.core.build_lore_graph(self.agent)
        self.assertTrue(graph["nodes"]["lore/café.md"]["uncommitted"])
        detailed = self.core.detailed_lore_map(graph)
        records = {}
        pending = [detailed["root"]]
        while pending:
            record = pending.pop()
            records[record["file"]] = record
            pending.extend(record["children"])
        self.assertTrue(records["lore/café.md"]["uncommitted"])

    def test_context_size_findings_do_not_change_coverage(self):
        self.complete_fixture()
        root_path = os.path.join(self.agent, "lore-context.md")
        write(root_path, frontmatter("context", "Large root.") +
              "# Context\n" + ("x" * 41000))
        graph = self.core.build_lore_graph(self.agent)
        self.assertEqual(self.core.lore_coverage(graph)["status"], "complete")
        self.assertIn("context_size_warning", [f["issue"] for f in graph["findings"]])
        write(root_path, frontmatter("context", "Huge root.") +
              "# Context\n" + ("x" * 81000))
        graph = self.core.build_lore_graph(self.agent)
        self.assertIn("context_size_error", [f["issue"] for f in graph["findings"]])
        self.assertEqual(self.core.lore_coverage(graph)["status"], "complete")

    def test_legacy_context_retains_fifty_thousand_token_ceiling(self):
        root_path = os.path.join(self.agent, "lore-context.md")
        write(root_path, "# Legacy context\n\n" + ("x" * 200001))
        graph = self.core.build_lore_graph(self.agent)
        findings = [f for f in graph["findings"]
                    if f["file"] == "lore-context.md"]
        self.assertIn("context_size_error", [f["issue"] for f in findings])
        self.assertEqual(self.core.lore_coverage(graph)["status"], "legacy")

    def test_missing_root_is_reported_without_hiding_topics(self):
        write(os.path.join(self.agent, "lore", "legacy.md"), "# Legacy\n")
        graph = self.core.build_lore_graph(self.agent)
        self.assertIn(("lore-context.md", "missing_context"),
                      {(f["file"], f["issue"]) for f in graph["findings"]})
        self.assertEqual(self.core.lore_coverage(graph)["files"]["total"], 1)

    def test_coverage_reasons_are_disjoint_and_follow_precedence(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "legacy.md"), "# Legacy\n")
        write(os.path.join(self.agent, "lore", "future.md"),
              frontmatter("topic", "Future.", "lore/engineering.md", lore=2) + "# F\n")
        write(os.path.join(self.agent, "lore", "invalid.md"),
              "---\nlore: 1\ntype: topic\nsummary: \"Invalid.\"\n---\n# I\n")
        write(os.path.join(self.agent, "lore", "unreachable.md"),
              frontmatter("area", "Disconnected.", "lore/unreachable-parent.md") + "# U\n")
        write(os.path.join(self.agent, "lore", "unreachable-parent.md"),
              frontmatter("area", "Disconnected parent.", "lore/unreachable.md") + "# P\n")
        graph = self.core.build_lore_graph(self.agent)
        coverage = self.core.lore_coverage(graph)
        self.assertEqual(coverage["uncovered"]["legacy"], 1)
        self.assertEqual(coverage["uncovered"]["unsupported_version"], 1)
        self.assertEqual(coverage["uncovered"]["invalid_v1"], 3)
        self.assertEqual(coverage["uncovered"]["unreachable_v1"], 0)
        self.assertEqual(sum(coverage["uncovered"].values()),
                         coverage["files"]["uncovered"])

    def test_v1_child_of_fixed_legacy_root_is_unreachable_not_invalid(self):
        write(os.path.join(self.agent, "lore-context.md"), "# Legacy root\n")
        write(os.path.join(self.agent, "lore", "new.md"),
              frontmatter("topic", "New knowledge.", "lore-context.md") + "# New\n")
        graph = self.core.build_lore_graph(self.agent)
        self.assertEqual(graph["nodes"]["lore/new.md"]["coverage_reason"],
                         "unreachable_v1")
        self.assertNotIn("invalid_parent", [f["issue"] for f in graph["findings"]
                                             if f["file"] == "lore/new.md"])
        self.assertEqual(self.core.lore_coverage(graph)["status"], "legacy")

    def test_missing_parent_and_topic_child_are_invalid(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "missing.md"),
              frontmatter("topic", "Missing parent.", "lore/nope.md") + "# M\n")
        write(os.path.join(self.agent, "lore", "child.md"),
              frontmatter("topic", "Illegal child.", "lore/build.md") + "# C\n")
        graph = self.core.build_lore_graph(self.agent)
        self.assertEqual(graph["nodes"]["lore/missing.md"]["coverage_reason"], "invalid_v1")
        self.assertEqual(graph["nodes"]["lore/child.md"]["coverage_reason"], "invalid_v1")
        issues = {(f["file"], f["issue"]) for f in graph["findings"]}
        self.assertIn(("lore/missing.md", "missing_parent"), issues)
        self.assertIn(("lore/child.md", "parent_is_topic"), issues)

    def test_scoped_grooming_of_a_cycle_terminates(self):
        write(os.path.join(self.agent, "lore-context.md"),
              frontmatter("context", "Root.") + "# Root\n")
        write(os.path.join(self.agent, "lore", "a.md"),
              frontmatter("area", "Cycle A.", "lore/b.md") + "# A\n")
        write(os.path.join(self.agent, "lore", "b.md"),
              frontmatter("area", "Cycle B.", "lore/a.md") + "# B\n")
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.select_lore_workset(
            graph, scope="lore/a.md", budget=1000)["workset"]
        self.assertEqual({item["file"] for item in result["editable"]},
                         {"lore/a.md", "lore/b.md"})

    def test_formal_links_ignore_code_but_legacy_safety_keeps_inline_code(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "links.md"),
              frontmatter("topic", "Link forms.", "lore/engineering.md") +
              """# Links

[inline](build.md "Build details")
[ref][context]
[context]: ../lore-context.md 'Root details'
[[build.md]]
`build.md`

```md
[ignored](build.md)
```
""")
        graph = self.core.build_lore_graph(self.agent)
        node = graph["nodes"]["lore/links.md"]
        self.assertEqual(node["outbound"], ["lore-context.md", "lore/build.md"])
        self.assertIn("lore/build.md", node["safety_outbound"])

    def test_detailed_map_exposes_conservative_references_for_mapped_nodes(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "links.md"),
              frontmatter("topic", "Non-link references.", "lore/engineering.md") +
              "# Links\n\nRun `build.md` when needed.\n")
        graph = self.core.build_lore_graph(self.agent)
        detailed = self.core.detailed_lore_map(graph)
        records = {}
        pending = [detailed["root"]]
        while pending:
            record = pending.pop()
            records[record["file"]] = record
            pending.extend(record["children"])
        build = records["lore/build.md"]
        links = records["lore/links.md"]
        self.assertIn("lore/links.md", build["legacy_references"]["inbound"])
        self.assertIn("lore/build.md", links["legacy_references"]["outbound"])
        self.assertIn("uncommitted", build)

    def test_wiki_media_embed_is_not_a_formal_graph_edge(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "links.md"),
              frontmatter("topic", "Embedded reference.", "lore/engineering.md") +
              "# Links\n\n![[build.md]]\n")
        graph = self.core.build_lore_graph(self.agent)
        node = graph["nodes"]["lore/links.md"]
        self.assertEqual(node["outbound"], [])
        self.assertIn("lore/build.md", node["safety_outbound"])

    def test_broken_escaping_and_absolute_links_are_findings(self):
        self.complete_fixture()
        path = os.path.join(self.agent, "lore", "build.md")
        write(path, frontmatter("topic", "Links.", "lore/engineering.md") +
              "# Links\n\n[missing](missing.md) [escape](../../outside.md) "
              "[absolute](/tmp/outside.md) [windows](C:/outside.md)\n")
        graph = self.core.build_lore_graph(self.agent)
        issues = [f["issue"] for f in graph["findings"] if f["file"] == "lore/build.md"]
        self.assertIn("broken_lore_link", issues)
        self.assertGreaterEqual(issues.count("unsafe_lore_link"), 3)

    def test_ambiguous_basename_is_a_safety_finding(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "one", "same.md"), "# Legacy one\n")
        write(os.path.join(self.agent, "lore", "two", "same.md"), "# Legacy two\n")
        write(os.path.join(self.agent, "lore", "mentions.md"), "# M\n\n`same.md`\n")
        graph = self.core.build_lore_graph(self.agent)
        self.assertIn(("lore/mentions.md", "ambiguous_legacy_reference"),
                      {(f["file"], f["issue"]) for f in graph["findings"]})

    def test_scoped_detailed_map_keeps_ancestors_and_descendants(self):
        self.complete_fixture()
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.detailed_lore_map(graph, "lore/engineering.md")
        self.assertEqual(result["scope"], "lore/engineering.md")
        self.assertEqual(result["root"]["file"], "lore-context.md")
        area = result["root"]["children"][0]
        self.assertEqual(area["file"], "lore/engineering.md")
        self.assertEqual(area["children"][0]["file"], "lore/build.md")

    def test_scope_rejects_absolute_traversal_and_empty_segments(self):
        self.complete_fixture()
        graph = self.core.build_lore_graph(self.agent)
        for unsafe in ("/lore/build.md", "../lore/build.md", "lore//build.md",
                       "lore/./build.md", "C:/lore/build.md"):
            with self.assertRaisesRegex(ValueError, "unsafe Lore scope"):
                self.core.detailed_lore_map(graph, unsafe)

    def test_boot_map_keeps_mandatory_areas_and_truncates_optional_tiers(self):
        self.complete_fixture()
        for index in range(6):
            write(os.path.join(self.agent, "lore", "root-%d.md" % index),
                  frontmatter("topic", "Root topic %d with useful detail." % index,
                              "lore-context.md") + "# Root\n")
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.boot_lore_map(graph, budget=230)
        self.assertEqual(result["stats"]["lore_files"], 8)
        self.assertEqual(
            result["stats"]["lore_context_estimated_tokens"],
            graph["nodes"]["lore-context.md"]["estimated_tokens"],
        )
        self.assertEqual([a["file"] for a in result["areas"]],
                         ["lore/engineering.md"])
        self.assertGreater(result["omitted"]["direct_topics"], 0)
        self.assertLessEqual(result["estimated_tokens"], result["budget"])

    def test_boot_map_reports_mandatory_core_overflow(self):
        self.complete_fixture()
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.boot_lore_map(graph, budget=10)
        self.assertTrue(result["over_budget"])
        self.assertEqual(len(result["areas"]), 1)

    def test_boot_footprint_sums_always_loaded_files_and_generated_map(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "role.md"),
              "---\ndescription: Fixture agent\n---\n\n# Role\n")
        graph = self.core.build_lore_graph(self.agent)
        system_prompts = self.core._boot_system_prompts_estimated_tokens(
            self.agent, FRAMEWORK_DIR, "codex")
        role = self.core._boot_role_estimated_tokens(self.agent)
        self.assertIsNotNone(system_prompts)
        self.assertIsNotNone(role)
        result = self.core.boot_lore_map(
            graph, system_prompt_tokens=system_prompts, role_tokens=role)
        context = graph["nodes"]["lore-context.md"]["estimated_tokens"]
        self.assertEqual(
            result["stats"]["boot_system_prompts_estimated_tokens"],
            system_prompts,
        )
        self.assertEqual(
            result["stats"]["boot_role_estimated_tokens"], role)
        self.assertEqual(
            result["stats"]["boot_footprint_estimated_tokens"],
            system_prompts + role + context + result["estimated_tokens"],
        )
        self.assertEqual(
            result["estimated_tokens"],
            self.core.estimate_tokens(self.core.yaml_dump(result)),
        )

    def test_boot_footprint_treats_absent_optional_context_as_zero(self):
        write(os.path.join(self.agent, "role.md"), "# Role\n")
        write(os.path.join(self.agent, "lore", "first.md"), "# First topic\n")
        system_prompts = self.core._boot_system_prompts_estimated_tokens(
            self.agent, FRAMEWORK_DIR, "codex")
        role = self.core._boot_role_estimated_tokens(self.agent)
        self.assertIsNotNone(system_prompts)
        self.assertIsNotNone(role)
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.boot_lore_map(
            graph, system_prompt_tokens=system_prompts, role_tokens=role)
        self.assertEqual(
            result["stats"]["boot_footprint_estimated_tokens"],
            system_prompts + role + result["estimated_tokens"],
        )

    def test_invalid_utf8_is_anonymous_partial_coverage_not_map_failure(self):
        self.complete_fixture()
        corrupt = os.path.join(self.agent, "lore", "corrupt.md")
        with open(corrupt, "wb") as handle:
            handle.write(b"# Corrupt\n\xff\n")

        graph = self.core.build_lore_graph(self.agent)
        coverage = self.core.lore_coverage(graph)
        self.assertEqual(coverage["status"], "partial")
        self.assertEqual(coverage["uncovered"]["invalid_utf8"], 1)

        detailed = self.core.yaml_dump(self.core.detailed_lore_map(graph))
        self.assertNotIn("lore/corrupt.md", detailed)
        self.assertIn("invalid_utf8: 1", detailed)

        workset = self.core.select_lore_workset(graph, budget=10000)["workset"]
        surfaced = [item["file"] for key in ("editable", "halo", "snapshot")
                    for item in workset[key]]
        self.assertNotIn("lore/corrupt.md", surfaced)

        result = subprocess.run(
            [sys.executable, LR_CORE, "lore-map", "--agent-dir", self.agent,
             "--view", "boot"], stdout=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"invalid_utf8: 1", result.stdout)
        self.assertNotIn(b"lore/corrupt.md", result.stdout)

    def test_workset_budget_halo_hashes_and_future_read_only(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "future.md"),
              frontmatter("topic", "Future.", "lore/engineering.md", lore=2) +
              "# Future\n")
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.select_lore_workset(
            graph, scope="lore/build.md", budget=1000)["workset"]
        self.assertEqual(result["editable"][0]["file"], "lore/build.md")
        self.assertNotIn("lore/future.md", [i["file"] for i in result["editable"]])
        self.assertEqual([i["reason"] for i in result["halo"]],
                         ["ancestor", "ancestor"])
        self.assertEqual({i["file"] for i in result["snapshot"]},
                         {"lore-context.md", "lore/engineering.md", "lore/build.md"})
        self.assertTrue(all(len(i["sha256"]) == 64 for i in result["snapshot"]))
        self.assertLessEqual(result["estimated_tokens"], result["budget"])

        with self.assertRaisesRegex(ValueError, "read-only"):
            self.core.select_lore_workset(
                graph, scope="lore/future.md", budget=1000)

    def test_map_findings_are_prioritized_for_grooming(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "broken.md"),
              frontmatter("topic", "Has a broken route.", "lore/engineering.md") +
              "# Broken\n\n[missing](missing.md)\n")
        graph = self.core.build_lore_graph(self.agent)
        for node in graph["nodes"].values():
            node["uncommitted"] = False
            node["last_modified_iso"] = None
        workset = self.core.select_lore_workset(graph, budget=10000)["workset"]
        reasons = {item["file"]: item["reason"] for item in workset["editable"]}
        self.assertEqual(reasons["lore/broken.md"], "structural_finding")

    def test_naive_cursor_timestamp_is_ignored_instead_of_crashing(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "workdir", "lore-grooming-state.yaml"),
              """lore_grooming: 1
last_successful_at: "2026-08-08T12:00:00"
last_successful_commit: null
reviewed: []
""")
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.select_lore_workset(graph, budget=1000)["workset"]
        self.assertTrue(result["editable"])

    def test_future_file_references_are_scanned_but_never_editable(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "future.md"),
              frontmatter("topic", "Future.", "lore/engineering.md", lore=2) +
              "# Future\n\n[Build](build.md)\n")
        graph = self.core.build_lore_graph(self.agent)
        self.assertIn("lore/future.md", graph["nodes"]["lore/build.md"]["inbound"])
        workset = self.core.select_lore_workset(graph, budget=10000)["workset"]
        self.assertNotIn("lore/future.md", [i["file"] for i in workset["editable"]])

    def test_scope_plus_mandatory_ancestors_cannot_silently_break_budget(self):
        self.complete_fixture()
        graph = self.core.build_lore_graph(self.agent)
        with self.assertRaisesRegex(ValueError, "mandatory ancestor"):
            self.core.select_lore_workset(graph, scope="lore/build.md", budget=40)

    def test_oversized_topic_is_singleton_with_explicit_overflow(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "lore", "huge.md"),
              frontmatter("topic", "Oversized.", "lore/engineering.md") +
              "# Huge\n" + ("x" * 1000))
        graph = self.core.build_lore_graph(self.agent)
        result = self.core.select_lore_workset(
            graph, scope="lore/huge.md", budget=100)["workset"]
        self.assertTrue(result["over_budget"])
        self.assertEqual([i["file"] for i in result["editable"]], ["lore/huge.md"])

    def test_yaml_is_deterministic_json_quoted_and_lf_terminated(self):
        payload = {"a": "café", "items": [{"file": "lore/a.md", "ok": True}],
                   "none": None, "percent": 30.0}
        first = self.core.yaml_dump(payload)
        self.assertEqual(first, self.core.yaml_dump(payload))
        self.assertIn('a: "café"', first)
        self.assertIn("percent: 30.0", first)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)

    def test_cli_emits_yaml_and_scope_errors_exit_two(self):
        self.complete_fixture()
        write(os.path.join(self.agent, "role.md"),
              "---\ndescription: Fixture agent\n---\n\n# Role\n")
        good = subprocess.run(
            [sys.executable, LR_CORE, "lore-map", "--agent-dir", self.agent,
             "--view", "boot", "--engine", "codex"],
            stdout=subprocess.PIPE, check=False)
        self.assertEqual(good.returncode, 0)
        self.assertTrue(good.stdout.decode().startswith("lore_map: 1\n"))
        self.assertRegex(good.stdout.decode(),
                         r"boot_footprint_estimated_tokens: [1-9][0-9]*")
        self.assertRegex(
            good.stdout.decode(),
            r"boot_system_prompts_estimated_tokens: [1-9][0-9]*")
        self.assertRegex(good.stdout.decode(),
                         r"boot_role_estimated_tokens: [1-9][0-9]*")
        repeated = subprocess.run(
            [sys.executable, LR_CORE, "lore-map", "--agent-dir", self.agent,
             "--view", "boot", "--engine", "codex"],
            stdout=subprocess.PIPE, check=False)
        self.assertEqual(repeated.stdout, good.stdout)
        bad = subprocess.run(
            [sys.executable, LR_CORE, "lore-map", "--agent-dir", self.agent,
             "--view", "detailed", "--scope", "lore/nope.md"],
            stdout=subprocess.PIPE, check=False)
        self.assertEqual(bad.returncode, 2)
        self.assertTrue(bad.stdout.decode().startswith("lore_map:\n  ok: false\n"))

    def test_scoped_area_cursor_advances_across_bounded_partitions(self):
        self.complete_fixture()
        for index in range(3):
            write(os.path.join(self.agent, "lore", "part-%d.md" % index),
                  frontmatter("topic", "Partition %d." % index, "lore/engineering.md") +
                  "# Part %d\n\n%s\n" % (index, "x" * 420))
        graph = self.core.build_lore_graph(self.agent)
        first = self.core.select_lore_workset(
            graph, scope="lore/engineering.md", budget=260)["workset"]
        first_paths = [item["file"] for item in first["editable"]]
        self.assertIn("lore/engineering.md", first_paths)
        self.assertLess(len(first_paths), 4)

        reviewed = "\n".join(
            '  - {file: %s, at: "2026-08-08T12:00:00Z"}' % path
            for path in first_paths)
        write(os.path.join(self.agent, "workdir", "lore-grooming-state.yaml"),
              """lore_grooming: 1
last_successful_at: "2026-08-08T12:00:00Z"
last_successful_commit: null
reviewed:
%s
""" % reviewed)
        second = self.core.select_lore_workset(
            graph, scope="lore/engineering.md", budget=260)["workset"]
        second_paths = [item["file"] for item in second["editable"]]
        self.assertFalse(set(first_paths) & set(second_paths))
        self.assertTrue(all(path.startswith("lore/") for path in second_paths))


class LoreV1DistributionTest(unittest.TestCase):
    def read(self, relative):
        with open(os.path.join(FRAMEWORK_DIR, relative), encoding="utf-8") as handle:
            return handle.read()

    def test_public_skill_and_cursor_wrapper_exist(self):
        canonical = self.read("skills/groom/SKILL.md")
        cursor = self.read(".cursor-skills/lr-groom/SKILL.md")
        self.assertIn("docs/groom.md", canonical)
        self.assertIn("docs/groom.md", cursor)
        self.assertIn("name: lr-groom", cursor)

    def test_no_write_migration_preserves_existing_lore(self):
        migration = self.read("migrations/36.md")
        self.assertIn("## Write Paths\n\n```\n(none)\n```", migration)
        self.assertIn("Do not add frontmatter to existing Lore files", migration)

    def test_creation_boot_merge_search_and_check_are_wired(self):
        self.assertIn("lore: 1", self.read("docs/create-agent.md"))
        boot = self.read("docs/agent-boot.md")
        self.assertIn("lore-map --agent-dir", boot)
        self.assertIn("Codex bootstrap", boot)
        self.assertIn("append `--engine codex`", boot)
        self.assertNotIn("Pass no engine flag", boot)
        self.assertIn("Booted: <agent-name> — <role description>", boot)
        self.assertIn("Agent Lore: <lore_files> topics", boot)
        self.assertIn("~<map_k>k lore map", boot)
        self.assertIn("~<role_k>k role", boot)
        self.assertIn("~<system_prompts_k>k system prompts", boot)
        attach = self.read("docs/attach.md")
        self.assertIn("Added Context: ~<added_context_k>k tokens total", attach)
        self.assertIn("Do not add system prompts", attach)
        self.assertIn('preflight --agent "<guest-name>" --workspace "<cwd>" --engine "<engine>"',
                      attach)
        self.assertIn('lore-map --agent-dir "<guest-agent-dir>" --view boot --engine "<engine>"',
                      attach)
        self.assertIn("data.agent.lore_context_file` is non-null", attach)
        update = self.read("docs/update.md")
        self.assertIn("## Automatic Publication", update)
        self.assertIn("commit and push only those update-owned repo changes", update)
        self.assertIn("Never force-push", update)
        self.assertIn("An explicit update is not", update)
        self.assertIn("permission to overwrite uncommitted work", update)
        self.assertIn("Immediately before writing the pending marker or pushing", update)
        self.assertIn("that commit is the sole commit ahead", update)
        version_check = self.read("docs/version-check.md")
        self.assertIn("#### 1d. Capture publication pre-state", version_check)
        self.assertIn("docs/update.md` § **Automatic Publication**", version_check)
        self.assertIn("Both paths use the same write-aware collision rule", version_check)
        self.assertNotIn("writes through dirty files unconditionally", version_check)
        self.assertIn("Step 3 generates the Lore", version_check)
        self.assertIn("lazy-migration candidate", self.read("docs/process-merge.md"))
        self.assertIn("Start With the Lore Map", self.read("docs/lore-search.md"))
        self.assertIn("lore-map --agent-dir", self.read("docs/check.md"))

    def test_codex_spawn_guidance_matches_portable_tool_schema(self):
        paths = (
            "docs/engines/codex.md",
            "docs/lore-search.md",
            "docs/consult.md",
            "docs/process-merge.md",
            "docs/recall.md",
        )
        combined = "\n".join(self.read(path) for path in paths)
        self.assertNotIn("role `worker`", combined)
        self.assertNotIn("role `explorer`", combined)
        self.assertNotIn("(role `worker`)", combined)
        self.assertNotIn("(role `explorer`, read-only)", combined)
        self.assertIn("do not invent a `role` argument", combined)
        self.assertIn("explicitly require read-only work", combined)

    def test_future_versions_are_read_only_at_semantic_write_sites(self):
        self.assertIn("future-version files are read-only", self.read("docs/groom.md"))
        self.assertIn("future-version file", self.read("docs/process-merge.md"))
        self.assertIn("leave that reflection unmerged", self.read("docs/process-merge.md"))

    def test_cursor_wrapper_tree_is_in_sync(self):
        result = subprocess.run(
            [sys.executable, os.path.join(FRAMEWORK_DIR, "scripts", "sync-cursor-skills"),
             "--check"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0, result.stdout.decode() + result.stderr.decode())


if __name__ == "__main__":
    unittest.main(verbosity=2)
