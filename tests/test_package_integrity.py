import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-package.py"
BUNDLE_SCRIPT = ROOT / "scripts" / "build-knowledge-bundle.py"


def load_validator():
    if not SCRIPT.exists():
        raise AssertionError("scripts/validate-package.py should exist")
    spec = importlib.util.spec_from_file_location("validate_package", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_bundle_builder():
    spec = importlib.util.spec_from_file_location("build_knowledge_bundle", BUNDLE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackageIntegrityTests(unittest.TestCase):
    def make_root(self, skill_body=None, agents_body=None):
        temp = tempfile.TemporaryDirectory()
        root = pathlib.Path(temp.name)
        skill_body = skill_body or "# Marketing Strategist\n\nShared body\n"
        agents_body = agents_body or "# Marketing Strategist\n\nShared body\n"
        (root / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test.\n---\n\n" + skill_body
        )
        (root / "AGENTS.md").write_text(agents_body)
        (root / "PROMPT.md").write_text("Prompt\n")
        return temp, root

    def test_reports_a_missing_routed_file(self):
        validator = load_validator()
        temp, root = self.make_root(
            skill_body="# Marketing Strategist\n\nRead `references/missing.md`.\n",
            agents_body="# Marketing Strategist\n\nRead `references/missing.md`.\n",
        )
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn(
            "SKILL.md references missing path: references/missing.md", errors
        )

    def test_reports_unfinished_placeholders_in_frozen_examples(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        examples = root / "examples"
        examples.mkdir()
        (examples / "sample.md").write_text("Headline: {{TODO}}\n")

        errors = validator.validate(root)

        self.assertIn(
            "examples/sample.md contains an unfinished placeholder", errors
        )

    def test_reports_entrypoint_drift(self):
        validator = load_validator()
        temp, root = self.make_root(
            skill_body="# Marketing Strategist\n\nOne body.\n",
            agents_body="# Marketing Strategist\n\nAnother body.\n",
        )
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn("SKILL.md and AGENTS.md operating bodies have drifted", errors)

    def test_v02_operating_references_exist(self):
        required = {
            "references/13-brand-folder.md",
            "references/14-learning-system.md",
            "references/15-connectors.md",
            "references/16-hook-formats.md",
            "references/17-runtime-portability.md",
        }

        missing = {relative for relative in required if not (ROOT / relative).is_file()}

        self.assertEqual(set(), missing)

    def test_connector_and_runtime_guides_exist(self):
        required = {
            "connectors/README.md",
            "connectors/firecrawl.md",
            "connectors/trendtrack.md",
            "connectors/foreplay.md",
            "connectors/runtime-codex.md",
            "connectors/runtime-claude.md",
            "connectors/runtime-claude-code.md",
            "connectors/runtime-chatgpt.md",
            "connectors/runtime-gemini.md",
            "connectors/runtime-grok.md",
            "connectors/runtime-grok-agents.md",
        }

        missing = {relative for relative in required if not (ROOT / relative).is_file()}

        self.assertEqual(set(), missing)

    def test_v02_contracts_and_frozen_examples_exist(self):
        required = {
            "contracts/brand-readiness.md",
            "contracts/hook-batch.md",
            "contracts/learning-update.md",
            "examples/brand-readiness.md",
            "examples/hook-batch.md",
            "examples/learning-update.md",
        }

        missing = {relative for relative in required if not (ROOT / relative).is_file()}

        self.assertEqual(set(), missing)

    def test_ad_copy_contract_requires_length_variants(self):
        contract = (ROOT / "contracts" / "ad-copy.md").read_text()

        self.assertIn("Short version", contract)
        self.assertIn("Medium version", contract)
        self.assertIn("Long version", contract)
        self.assertIn("exactly 5", contract)

    def test_concept_contract_uses_portfolio_awareness_coverage(self):
        contract = (ROOT / "contracts" / "concept-batch.md").read_text()

        self.assertIn("portfolio", contract.lower())
        self.assertIn("Most aware", contract)
        self.assertNotIn("exactly 4, one per awareness state", contract)

    def test_diagnosis_contract_accepts_manual_exports(self):
        contract = (ROOT / "contracts" / "ad-diagnosis.md").read_text()

        self.assertIn("manual", contract.lower())
        self.assertIn("does not require a live Meta connection", contract)

    def test_package_declares_v02_and_portable_brand_folder(self):
        self.assertEqual("0.2.0", (ROOT / "VERSION").read_text().strip())
        readme = (ROOT / "README.md").read_text()

        self.assertIn("brand folder", readme.lower())
        self.assertIn("Firecrawl", readme)
        self.assertIn("Grok Agents", readme)

    def test_concept_reference_removes_rigid_launch_mix(self):
        reference = (ROOT / "references" / "06-concept-model.md").read_text()

        self.assertNotIn("Every launch concept covers four awareness states", reference)
        self.assertNotIn("Three videos and one static per concept", reference)
        self.assertIn("Most aware", reference)
        self.assertIn("portfolio", reference.lower())

    def test_legacy_config_points_to_portable_brand_folder(self):
        config = (ROOT / "config" / "brand.example.yml").read_text()

        self.assertIn("scripts/init-brand-folder.py", config)
        self.assertIn("legacy", config.lower())
        self.assertNotIn("This file is the ONLY place", config)

    def test_universal_bundle_includes_connector_guides(self):
        builder = load_bundle_builder()

        content = builder.build_body()

        self.assertIn("# PART: CONNECTOR AND RUNTIME GUIDES", content)
        self.assertIn("<!-- source: connectors/runtime-grok-agents.md -->", content)


if __name__ == "__main__":
    unittest.main()
