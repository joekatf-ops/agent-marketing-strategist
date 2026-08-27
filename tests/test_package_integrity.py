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
        validator = load_validator()

        errors = validator.validate(ROOT)

        policy_errors = [
            error
            for error in errors
            if error.startswith("contracts/campaign-launch-plan.md must")
        ]
        self.assertEqual([], policy_errors)

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

    def test_frozen_hook_batch_uses_controlled_formats_and_selected_route(self):
        hook_example = (ROOT / "examples" / "hook-batch.md").read_text()
        hook_formats = [
            line.split("**Hook format:**", 1)[1].strip()
            for line in hook_example.splitlines()
            if "**Hook format:**" in line
        ]
        execution_formats = [
            line.split("**Execution format:**", 1)[1].strip()
            for line in hook_example.splitlines()
            if "**Execution format:**" in line
        ]

        self.assertEqual(
            [
                "Demonstration",
                "Comparison",
                "Confession",
                "POV situation",
                "Contrarian statement",
                "Product in action",
            ],
            hook_formats,
        )
        self.assertEqual(
            [
                "Product demonstration",
                "Comparison",
                "Problem to solution narrative",
                "Problem to solution narrative",
                "Comparison",
                "Product demonstration",
            ],
            execution_formats,
        )

        selected = hook_example.split("### Hook 2:", 1)[1].split("### Hook 3:", 1)[0]
        package_routes = [
            line.split("**Awareness and messaging route:**", 1)[1].strip()
            for line in hook_example.splitlines()
            if "**Awareness and messaging route:**" in line
        ]
        self.assertIn("Messaging route: proof that can be seen", hook_example)
        self.assertEqual(
            ["SLA, differentiation; proof that can be seen"] * 6,
            package_routes,
        )
        self.assertIn(
            "SLA, differentiation; proof that can be seen", selected
        )
        self.assertIn(
            'Primary hook:** "Same six cables. Two very different ways to find one"',
            selected,
        )

        launch = (ROOT / "examples" / "campaign-launch-plan.md").read_text()
        destination = (ROOT / "examples" / "destination-handoff.md").read_text()
        sla_handoff = destination.split("## SLA handoff card", 1)[1].split(
            "## PDA handoff card", 1
        )[0]
        self.assertIn(
            '| SLA, differentiation | proof that can be seen | "Same six cables. Two very different ways to find one" |',
            launch,
        )
        self.assertIn("Messaging route: proof that can be seen", sla_handoff)
        self.assertIn(
            'Primary hook: "Same six cables. Two very different ways to find one"',
            sla_handoff,
        )

    def test_frozen_launch_manifest_preserves_full_traceability(self):
        launch = (ROOT / "examples" / "campaign-launch-plan.md").read_text()
        manifest = launch.split("## 5. Ad manifest", 1)[1].split(
            "## 6. Destination validation", 1
        )[0]
        rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in manifest.splitlines()
            if line.startswith(("| 1 |", "| 2 |", "| 3 |", "| 4 |"))
        ]

        self.assertEqual(4, len(rows))
        expected_who = (
            "remote workers who carry charging gear between home and shared workspaces"
        )
        expected_problem = (
            "finding the required cable means searching through a mixed pouch"
        )
        self.assertEqual([expected_who] * 4, [row[4] for row in rows])
        self.assertEqual([expected_problem] * 4, [row[5] for row in rows])

        required_evidence = (
            {"EVD-MKT-021", "EVD-PROD-001", "EVD-CLAIM-006"},
            {"EVD-MKT-022", "EVD-PROD-001", "EVD-CLAIM-006"},
            {"EVD-PROD-001", "EVD-OFFER-003", "EVD-CLAIM-006"},
            {"EVD-PROD-001", "EVD-OFFER-003", "EVD-CLAIM-006"},
        )
        for row, evidence_ids in zip(rows, required_evidence):
            with self.subTest(ad=row[1]):
                for evidence_id in evidence_ids:
                    self.assertIn(evidence_id, row[11])

    def test_standard_ad_contracts_exclude_most_aware_rows(self):
        for relative in (
            "contracts/ad-copy.md",
            "contracts/hook-batch.md",
            "contracts/video-script.md",
            "contracts/static-spec.md",
        ):
            with self.subTest(relative=relative):
                self.assertNotIn("| MWA |", (ROOT / relative).read_text())

    def test_hook_contract_separates_hook_and_execution_formats(self):
        contract = (ROOT / "contracts" / "hook-batch.md").read_text()

        self.assertIn("Hook format from `references/16-hook-formats.md`", contract)
        self.assertIn("Execution format from `references/08-formats.md`", contract)
        self.assertIn("FORMAT token from `references/07-naming.md`", contract)
        self.assertNotIn(
            "Media type and execution format from `references/16-hook-formats.md`",
            contract,
        )

    def test_video_contract_locks_destination_defaults_and_exceptions(self):
        contract = (ROOT / "contracts" / "video-script.md").read_text()

        for row in (
            "| UWA | LP |",
            "| PRA | LP |",
            "| SLA | PDP |",
            "| PDA | PDP |",
        ):
            self.assertIn(row, contract)
        self.assertIn("Destination Handoff", contract)
        self.assertIn("congruent", contract)
        self.assertNotIn("to an educational destination", contract)
        self.assertNotIn("To education or PDP", contract)

    def test_diagnosis_decisions_have_one_literal_top_level_action(self):
        reference = (ROOT / "references" / "09-testing-and-diagnosis.md").read_text()
        section = reference.split("## Six-decision taxonomy", 1)[1].split(
            "## Scaling stage", 1
        )[0]
        rows = [line for line in section.splitlines() if line.startswith("|")][2:]
        actions = [row.split("|")[3].strip() for row in rows]

        self.assertEqual(6, len(rows))
        self.assertEqual(
            ["scale", "ITR", "keep", "stop", "stop", "keep"], actions
        )
        self.assertTrue(all(action in {"keep", "ITR", "stop", "scale"} for action in actions))

    def test_destination_exceptions_always_use_a_controlled_name_token(self):
        relatives = (
            "references/07-naming.md",
            "references/09-testing-and-diagnosis.md",
            "contracts/campaign-launch-plan.md",
            "contracts/concept-batch.md",
            "contracts/destination-handoff.md",
        )
        forbidden = ("other destination", "another destination")

        for relative in relatives:
            with self.subTest(relative=relative):
                contract = (ROOT / relative).read_text()
                self.assertTrue(
                    all(phrase not in contract.lower() for phrase in forbidden),
                    f"{relative} permits a destination that cannot be named",
                )
                self.assertIn("controlled destination token", contract.lower())

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

    def test_reports_opposite_campaign_launch_policies(self):
        validator = load_validator()
        compliant_contract = (
            "## Creative testing\n\n"
            "- Budget type: ABO.\n"
            "- Absolute floor: $50 per ad set per day.\n"
            "- Preferred starting point: approximately $100 per ad set per day.\n"
            "- Planned observation window: five full days.\n\n"
            "## Scaling\n\n"
            "- Budget type: CBO.\n"
            "- Graduated ads keep their real Post ID.\n"
        )
        cases = (
            (
                "- Budget type: ABO.",
                "- Budget type: CBO.",
                "contracts/campaign-launch-plan.md must require ABO creative testing",
            ),
            (
                "- Absolute floor: $50 per ad set per day.",
                "- $50 per ad set per day is not a floor.",
                "contracts/campaign-launch-plan.md must set an absolute $50 per-ad-set daily floor",
            ),
            (
                "- Preferred starting point: approximately $100 per ad set per day.",
                "- Approximately $100 per ad set per day is not preferred.",
                "contracts/campaign-launch-plan.md must make approximately $100 the preferred per-ad-set daily starting point",
            ),
            (
                "- Planned observation window: five full days.",
                "- Planned observation window: four full days.",
                "contracts/campaign-launch-plan.md must set a five-full-day planned observation window",
            ),
            (
                "- Budget type: CBO.",
                "- Budget type: ABO.",
                "contracts/campaign-launch-plan.md must require CBO scaling",
            ),
            (
                "- Graduated ads keep their real Post ID.",
                "- Graduated ads do not preserve their real Post ID.",
                "contracts/campaign-launch-plan.md must preserve graduated ads' real Post ID",
            ),
        )

        for expected, opposite, error in cases:
            with self.subTest(opposite=opposite):
                temp, root = self.make_root()
                self.addCleanup(temp.cleanup)
                contract = root / "contracts" / "campaign-launch-plan.md"
                contract.parent.mkdir()
                contract.write_text(compliant_contract.replace(expected, opposite))

                errors = validator.validate(root)

                self.assertIn(error, errors)

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
