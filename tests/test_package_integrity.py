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

    def test_v03_operating_references_exist(self):
        required = {
            "references/13-brand-folder.md",
            "references/14-learning-system.md",
            "references/15-connectors.md",
            "references/16-hook-formats.md",
            "references/17-runtime-portability.md",
            "references/18-master-creative-strategy.md",
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

    def test_v03_contracts_and_governance_guides_exist(self):
        required = {
            "contracts/brand-readiness.md",
            "contracts/hook-batch.md",
            "contracts/learning-update.md",
            "contracts/campaign-launch-plan.md",
            "contracts/destination-handoff.md",
            "examples/brand-readiness.md",
            "examples/campaign-launch-plan.md",
            "examples/destination-handoff.md",
            "examples/hook-batch.md",
            "examples/learning-update.md",
            "connectors/notion-composio.md",
        }

        missing = {relative for relative in required if not (ROOT / relative).is_file()}

        self.assertEqual(set(), missing)

    def test_campaign_launch_contract_protects_testing_and_scaling_rules(self):
        contract_path = ROOT / "contracts" / "campaign-launch-plan.md"
        self.assertTrue(contract_path.is_file(), "Campaign Launch Plan should exist")
        contract = contract_path.read_text()

        for required in (
            "ABO",
            "$50",
            "approximately $100",
            "five full days",
            "CBO",
            "real Post ID",
        ):
            with self.subTest(required=required):
                self.assertIn(required, contract)

    def test_ad_copy_contract_requires_length_variants(self):
        contract = (ROOT / "contracts" / "ad-copy.md").read_text()

        self.assertIn("Short version", contract)
        self.assertIn("Medium version", contract)
        self.assertIn("Long version", contract)
        self.assertIn("exactly 5", contract)

    def test_concept_contract_requires_four_initial_awareness_ads(self):
        contract = (ROOT / "contracts" / "concept-batch.md").read_text()

        self.assertIn("Who x Primary Problem", contract)
        self.assertIn("exactly four", contract.lower())
        for awareness in ("UWA", "PRA", "SLA", "PDA"):
            self.assertIn(awareness, contract)
        self.assertNotIn("MWA", contract)

    def test_diagnosis_contract_accepts_manual_exports(self):
        contract = (ROOT / "contracts" / "ad-diagnosis.md").read_text()

        self.assertIn("manual", contract.lower())
        self.assertIn("does not require a live Meta connection", contract)

    def test_package_declares_v03_and_portable_brand_folder(self):
        self.assertEqual("0.3.0", (ROOT / "VERSION").read_text().strip())
        readme = (ROOT / "README.md").read_text()

        self.assertIn("brand folder", readme.lower())
        self.assertIn("Firecrawl", readme)
        self.assertIn("Grok Agents", readme)

    def test_concept_reference_uses_who_by_primary_problem(self):
        reference = (ROOT / "references" / "06-concept-model.md").read_text()

        self.assertIn("Who x Primary Problem", reference)
        self.assertNotIn("Persona x Outcome x Angle", reference)
        self.assertIn("CONTST", reference)

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

    def test_gemini_guide_uses_supported_firecrawl_oauth(self):
        guide = (ROOT / "connectors" / "runtime-gemini.md").read_text()

        self.assertIn("https://mcp.firecrawl.dev/v2/mcp-oauth", guide)
        self.assertIn("/mcp auth firecrawl", guide)
        self.assertNotIn("Bearer $FIRECRAWL_API_KEY", guide)

    def test_learning_example_targets_the_append_only_ledger(self):
        example = (ROOT / "examples" / "learning-update.md").read_text()

        self.assertIn("learning/learning-events.jsonl", example)
        self.assertNotIn("learning/events/", example)
        self.assertIn('"learning":', example)
        self.assertIn('"memory_key":', example)

    def test_standard_ad_contracts_exclude_most_aware_rows(self):
        for relative in (
            "contracts/ad-copy.md",
            "contracts/hook-batch.md",
            "contracts/video-script.md",
            "contracts/static-spec.md",
        ):
            with self.subTest(relative=relative):
                self.assertNotIn("| MWA |", (ROOT / relative).read_text())

    def test_naming_reference_uses_locked_v03_shapes(self):
        naming = (ROOT / "references" / "07-naming.md").read_text()

        self.assertIn(
            "[BRAND]_[PRODUCT]_[CT|SC]_[ABO|CBO]_[REGION]_[YYYYMMDD]", naming
        )
        self.assertIn("[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]", naming)
        self.assertIn(
            "[FULL_AD_SET_NAME]_[UWA|PRA|SLA|PDA]_[FORMAT]_[LP|PDP|HP|CP]_[POSTID]",
            naming,
        )

    def test_reports_superseded_concept_model_in_skill(self):
        validator = load_validator()
        temp, root = self.make_root(
            skill_body="# Marketing Strategist\n\nPersona x Outcome x Angle\n",
        )
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn("SKILL.md contains superseded concept model", errors)

    def test_reports_most_aware_rows_in_standard_ad_contracts(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        contracts = root / "contracts"
        contracts.mkdir()
        (contracts / "ad-copy.md").write_text("| MWA | Offer reminder |\n")

        errors = validator.validate(root)

        self.assertIn(
            "contracts/ad-copy.md contains a Most Aware standard-ad row", errors
        )

    def test_reports_indented_and_named_most_aware_rows_in_standard_ad_contracts(self):
        validator = load_validator()
        rows = (
            "    | MWA | Offer reminder |\n",
            "| Most Aware | Offer reminder |\n",
            "| Mwa | Offer reminder |\n",
        )

        for row in rows:
            with self.subTest(row=row):
                temp, root = self.make_root()
                self.addCleanup(temp.cleanup)
                contracts = root / "contracts"
                contracts.mkdir()
                (contracts / "ad-copy.md").write_text(row)
                (root / "references").mkdir()
                (root / "references" / "02-customer-state.md").write_text(
                    "| Most Aware | Conversion environment |\n"
                )

                errors = validator.validate(root)

                self.assertIn(
                    "contracts/ad-copy.md contains a Most Aware standard-ad row",
                    errors,
                )
                self.assertNotIn(
                    "references/02-customer-state.md contains a Most Aware standard-ad row",
                    errors,
                )

    def test_reports_reused_or_gapped_contst_test_batches(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        register = root / "templates" / "brand-folder" / "strategy" / "test-register.yml"
        register.parent.mkdir(parents=True)
        register.write_text(
            "tests:\n"
            "  - test_id: CONTST001\n"
            "    source: NNT\n"
            "  - test_id: CONTST003\n"
            "    source: INSPO\n"
            "  - test_id: CONTST003\n"
            "    source: ITR\n"
        )

        errors = validator.validate(root)

        self.assertIn(
            "templates/brand-folder/strategy/test-register.yml reuses CONTST003",
            errors,
        )
        self.assertIn(
            "templates/brand-folder/strategy/test-register.yml must use sequential CONTST values",
            errors,
        )

    def test_reports_missing_v03_release_requirements(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn("missing required file: VERSION", errors)
        self.assertIn(
            "missing v0.3 required file: references/18-master-creative-strategy.md",
            errors,
        )

        (root / "VERSION").write_text("0.2.0\n")

        errors = validator.validate(root)

        self.assertIn("VERSION must declare 0.3.0", errors)


if __name__ == "__main__":
    unittest.main()
