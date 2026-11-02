"""Required-context regressions using the actual callback and disposable files."""

import copy
import json
import os
import sys
import unittest

import test_preparation_guard as existing


class RequiredContextTest(unittest.TestCase):
    def setUp(self):
        self.f = existing.PreparationGuardTest()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def include(self, record, path):
        record["sources"] = [item for item in record["sources"] if existing.guard.absolute(item["path"]) != path.resolve()]
        record["sources"].append({"path": str(path.resolve()), "sha256": existing.guard.digest(path), "purpose": "Selected fixture context"})

    def run_record(self, record):
        existing.guard.write_json(self.f.record_path, record)
        return self.f.process()

    def test_high_risk_cannot_omit_security_even_when_declared_irrelevant(self):
        record = self.f.ready()
        record.update(type="feature", risk="high")
        record["sources"] = [item for item in record["sources"] if not item["path"].endswith("security.md")]
        result = self.run_record(record)
        self.assertTrue(self.f.denied(result), result)
        self.assertIn("security.md", str(result))

    def test_primary_type_and_declared_secondary_concern_require_sources(self):
        baseline = self.f.ready()
        for kind, concern, name in [("feature", None, "coding.md"), ("documentation", "architecture", "architecture.md"), ("analysis", "change-review", "engineering-method.md")]:
            with self.subTest(name=name):
                record = copy.deepcopy(baseline)
                record["type"] = kind
                if concern:
                    record["concerns"][concern] = {"applies": True, "reason": "Fixture affects this subject"}
                record["sources"] = [item for item in record["sources"] if not item["path"].endswith(name)]
                self.assertTrue(self.f.denied(self.run_record(record)))

    def test_missing_transitive_dependency_denies_even_with_all_checks_not_applicable(self):
        record = self.f.ready()
        workflow = self.f.kit / "docs/implementation/workflow.md"
        workflow.write_text("---\ndepends_on: [required-policy.md]\n---\nFixture workflow", encoding="utf-8")
        self.include(record, workflow)
        for key in ("requirements", "pre_execution_checks"):
            record[key][0]["status"] = "not_applicable"
        result = self.run_record(record)
        self.assertTrue(self.f.denied(result), result)
        self.assertIn("required-policy.md", str(result))

    def test_existing_dependency_must_be_loaded_and_current(self):
        record = self.f.ready()
        selected = self.f.workspace / "selected.md"
        needed = self.f.workspace / "required policy.md"
        selected.write_text("---\ndepends_on:\n  - 'required policy.md'\n---\nSelected", encoding="utf-8")
        needed.write_text("Required policy", encoding="utf-8")
        self.include(record, selected)
        self.assertTrue(self.f.denied(self.run_record(record)))
        self.include(record, needed)
        self.assertFalse(self.f.denied(self.run_record(record)))
        needed.write_text("Changed policy", encoding="utf-8")
        self.assertTrue(self.f.denied(self.run_record(record)))

    def test_concern_assessment_cannot_be_omitted_or_placeholder(self):
        baseline = self.f.ready()
        for invalid in (None, {}, {"security": {"applies": False, "reason": "unknown"}}):
            record = dict(baseline, concerns=invalid)
            self.assertTrue(self.f.denied(self.run_record(record)))

    def test_cycle_needs_review_but_is_not_automatically_invalid(self):
        record = self.f.ready()
        first, second = self.f.workspace / "first.md", self.f.workspace / "second.md"
        first.write_text("---\ndepends_on: [second.md]\n---\nFirst", encoding="utf-8")
        second.write_text("---\ndepends_on: [first.md]\n---\nSecond", encoding="utf-8")
        for path in (first, second):
            self.include(record, path)
        self.assertTrue(self.f.denied(self.run_record(record)))
        record["context_cycles"] = [{"paths": [str(first), str(second), str(first)], "resolution": "Both complete sources are usable together; no unresolved guidance"}]
        self.assertFalse(self.f.denied(self.run_record(record)))

    def test_nested_operation_instructions_resolve_their_dependencies(self):
        record = self.f.ready()
        (self.f.workspace / ".git").mkdir()
        folder = self.f.workspace / "nested"
        folder.mkdir()
        instructions = folder / "AGENTS.md"
        instructions.write_text("---\ndepends_on: [missing.md]\n---\nNested instructions", encoding="utf-8")
        self.include(record, instructions)
        record["write_paths"] = [str(folder)]
        existing.guard.write_json(self.f.record_path, record)
        event = dict(self.f.event, tool_input={"command": "*** Begin Patch\n*** Add File: " + str(folder / "file.txt") + "\n+data\n*** End Patch"})
        self.assertTrue(self.f.denied(self.f.process(event)))

    def test_malformed_metadata_and_duplicate_dependencies_fail_explicitly(self):
        baseline = self.f.ready()
        selected = self.f.workspace / "selected.md"
        for metadata in ("depends_on: *alias", "depends_on: [missing.md", "depends_on: []\ndepends_on: []", "depends_on:\n  missing: mapping", "  depends_on: [missing.md]"):
            record = copy.deepcopy(baseline)
            selected.write_text("---\n" + metadata + "\n---\nSelected", encoding="utf-8")
            self.include(record, selected)
            self.assertTrue(self.f.denied(self.run_record(record)), metadata)

    def test_resolve_submission_discovers_context_but_never_grants_readiness(self):
        record = self.f.ready()
        record.update(status="resolve", risk="high")
        record["sources"] = []
        event = dict(self.f.event, tool_name="update_plan", tool_input={"explanation": existing.guard.SUBMISSION_PREFIX + json.dumps(record), "plan": []})
        result = self.f.process(event)
        self.assertFalse(self.f.denied(result), result)
        resolved = existing.guard.read_json(self.f.record_path)
        self.assertEqual("draft", resolved["status"])
        self.assertEqual([], resolved["pre_execution_checks"])
        self.assertIn(str(self.f.kit / "docs/practices/security.md"), [item["path"] for item in resolved["sources"]])
        self.assertIn("preparation remains draft", str(result))
        self.assertTrue(self.f.denied(self.f.process()))

    def test_shared_dependency_is_loaded_once_without_becoming_a_cycle(self):
        record = self.f.ready()
        paths = [self.f.workspace / name for name in ("first.md", "second.md", "shared.md")]
        for path in paths[:2]:
            path.write_text("---\ndepends_on: [shared.md, ./shared.md]\n---\nSelected", encoding="utf-8")
        paths[-1].write_text("Shared", encoding="utf-8")
        for path in paths:
            self.include(record, path)
        resolved, cycles = existing.guard.required_context(self.f.config, self.f.workspace, record)
        self.assertEqual(1, resolved.count(paths[-1]))
        self.assertEqual([], cycles)
        self.assertFalse(self.f.denied(self.run_record(record)))

    def test_unrelated_files_are_not_scanned_and_analysis_avoids_method(self):
        record = self.f.ready()
        record.update(type="analysis", sources=[])
        unrelated = self.f.workspace / "unrelated.md"
        unrelated.write_text("---\ndepends_on: [missing.md]\n---\nUnselected", encoding="utf-8")
        paths, cycles = existing.guard.required_context(self.f.config, self.f.workspace, record)
        self.assertNotIn(unrelated, paths)
        self.assertNotIn(self.f.kit / "docs/implementation/engineering-method.md", paths)
        self.assertNotIn(self.f.kit / "docs/practices/coding.md", paths)
        self.assertEqual([], cycles)

    def test_route_edits_are_applied_without_changing_validator_code(self):
        record = self.f.ready()
        path = self.f.kit / "docs/implementation/context-routing.json"
        registry = existing.guard.read_json(path)
        extra = self.f.kit / "docs/implementation/extra.md"
        extra.write_text("New required route", encoding="utf-8")
        registry["routes"].append({"id": "extra", "any": [{"type": "tests"}], "paths": ["extra.md"]})
        existing.guard.write_json(path, registry)
        self.include(record, path)
        self.assertTrue(self.f.denied(self.run_record(record)))
        self.include(record, extra)
        self.assertFalse(self.f.denied(self.run_record(record)))

    def test_missing_registry_blocks_mutation_but_keeps_diagnostics(self):
        self.f.ready()
        (self.f.kit / "docs/implementation/context-routing.json").unlink()
        self.assertTrue(self.f.denied(self.f.process()))
        event = dict(self.f.event, tool_name="Bash", tool_input={"command": "Get-Location"})
        self.assertFalse(self.f.denied(self.f.process(event)))

    def test_changed_cycle_and_pending_resolution_are_not_silently_reused(self):
        record = self.f.ready()
        record["context_cycles"] = [{"paths": [str(self.f.workspace / "old.md")] * 2, "resolution": "Previously reviewed"}]
        self.assertTrue(self.f.denied(self.run_record(record)))

    def test_actual_package_resolves_without_an_authoring_dependency(self):
        # The temporary workspace lives below this authoring checkout. A root
        # marker makes it a distinct target, as an installed project would be.
        (self.f.workspace / ".git").mkdir()
        record = self.f.ready()
        record.update(type="feature", risk="high", sources=[])
        config = dict(self.f.config, kit_root=str(existing.SCRIPT.parents[1]))
        paths, cycles = existing.guard.required_context(config, self.f.workspace, record)
        self.assertIn(existing.SCRIPT.parents[1] / "docs/implementation/engineering-method.md", paths)
        self.assertIn(existing.SCRIPT.parents[1] / "docs/practices/security.md", paths)
        self.assertEqual([], cycles)
        for path in paths:
            self.assertTrue(existing.guard.under(path, existing.SCRIPT.parents[1]) or existing.guard.under(path, self.f.root), path)

    def test_invalid_registry_selectors_do_not_silently_disable_a_route(self):
        record = self.f.ready()
        path = self.f.kit / "docs/implementation/context-routing.json"
        registry = existing.guard.read_json(path)
        registry["routes"][0]["any"] = [{"unknown": "ignored"}]
        existing.guard.write_json(path, registry)
        self.include(record, path)
        self.assertTrue(self.f.denied(self.run_record(record)))

    def test_new_dependency_is_detected_after_its_parent_hash_is_refreshed(self):
        record = self.f.ready()
        parent = self.f.kit / "docs/implementation/workflow.md"
        child = parent.parent / "new.md"
        child.write_text("Newly required guidance", encoding="utf-8")
        parent.write_text("---\ndepends_on: [new.md]\n---\nUpdated workflow", encoding="utf-8")
        self.include(record, parent)
        self.assertTrue(self.f.denied(self.run_record(record)))
        self.include(record, child)
        self.assertFalse(self.f.denied(self.run_record(record)))

    def test_dependency_identity_uses_platform_path_equivalence(self):
        record = self.f.ready()
        path = self.f.workspace / "needed.md"
        path.write_text("Required guidance", encoding="utf-8")
        root = self.f.workspace / "selected.md"
        root.write_text('---\ndepends_on: ["needed.md", \'./needed.md\']\n---\nSelected', encoding="utf-8")
        self.include(record, root)
        self.include(record, path)
        record["sources"][-1]["path"] = str(path).upper() if os.name == "nt" else str(path.parent / ".." / path.parent.name / path.name)
        self.assertFalse(self.f.denied(self.run_record(record)))

    def test_dependency_chain_does_not_depend_on_python_recursion_depth(self):
        roots = [self.f.workspace / ("doc" + str(index) + ".md") for index in range(120)]
        for index, path in enumerate(roots):
            following = roots[index + 1].name if index + 1 < len(roots) else ""
            path.write_text("---\ndepends_on: [" + following + "]\n---\nDocument", encoding="utf-8")
        previous = sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(100)
            paths, cycles = existing.guard.dependency_graph([roots[0]])
        finally:
            sys.setrecursionlimit(previous)
        self.assertEqual(set(roots), set(paths))
        self.assertEqual([], cycles)

    def test_resolve_rejects_foreign_generation_without_changing_target_files(self):
        record = self.f.ready()
        record.update(status="resolve", generation="another-generation")
        event = dict(self.f.event, tool_name="update_plan", tool_input={"explanation": existing.guard.SUBMISSION_PREFIX + json.dumps(record), "plan": []})
        self.assertTrue(self.f.denied(self.f.process(event)))
        self.assertFalse(self.f.target.exists())
        self.assertEqual("draft", existing.guard.read_json(self.f.record_path)["status"])


if __name__ == "__main__":
    unittest.main()
