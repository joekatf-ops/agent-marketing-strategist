import csv
import datetime
import importlib.util
import json
import pathlib
import re
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-package.py"
BUNDLE_SCRIPT = ROOT / "scripts" / "build-knowledge-bundle.py"
RUNTIME_GUIDES = (
    "connectors/runtime-codex.md",
    "connectors/runtime-claude.md",
    "connectors/runtime-claude-code.md",
    "connectors/runtime-chatgpt.md",
    "connectors/runtime-gemini.md",
    "connectors/runtime-grok.md",
    "connectors/runtime-grok-agents.md",
)
UPLOAD_WORKFLOW_DOCS = (
    "README.md",
    "references/17-runtime-portability.md",
    "references/19-ad-analysis-harness.md",
    *RUNTIME_GUIDES,
)
UPLOAD_CHECKLIST = (
    "`PROMPT.md`",
    "`intake.json`",
    "`dist/knowledge-bundle.md`",
    "the selected generated brand bundle",
    "every referenced attachment or source file whose content the runtime must inspect",
)
UPLOAD_LABEL_BOUNDARY = (
    "URL and table labels do not become uploaded files or prove connector access."
)


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


def load_module(path, name):
    if not path.exists():
        raise AssertionError(f"{path} should exist")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agents_builder():
    script = ROOT / "scripts" / "build-agents-md.py"
    if not script.exists():
        raise AssertionError("scripts/build-agents-md.py should exist")
    spec = importlib.util.spec_from_file_location("build_agents_md", script)
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

    def make_release_policy_root(self):
        temp = tempfile.TemporaryDirectory()
        root = pathlib.Path(temp.name)
        relatives = (
            "SKILL.md",
            "AGENTS.md",
            "PROMPT.md",
            "VERSION",
            "invariants.yml",
            "references/06-concept-model.md",
            "references/09-testing-and-diagnosis.md",
            "references/12-meta-platform.md",
        )
        for relative in relatives:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / relative).read_text())
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

    def test_reports_stale_generated_agents_file(self):
        validator = load_validator()
        temp, root = self.make_root(
            skill_body="# Marketing Strategist\n\nOne body.\n",
            agents_body="# Marketing Strategist\n\nAnother body.\n",
        )
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn(
            "AGENTS.md is stale; regenerate it with scripts/build-agents-md.py",
            errors,
        )

    def test_accepts_agents_file_rendered_from_skill(self):
        validator = load_validator()
        body = "# Marketing Strategist\n\nOne body.\n"
        temp, root = self.make_root(skill_body=body, agents_body=body)
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertNotIn(
            "AGENTS.md is stale; regenerate it with scripts/build-agents-md.py",
            errors,
        )

    def test_generated_agents_file_is_committed_and_current(self):
        builder = load_agents_builder()

        self.assertEqual(
            (ROOT / "AGENTS.md").read_text(),
            builder.render((ROOT / "SKILL.md").read_text()),
        )

    def test_agents_renderer_rejects_a_skill_file_without_frontmatter(self):
        builder = load_agents_builder()

        with self.assertRaises(ValueError):
            builder.render("# Marketing Strategist\n\nNo frontmatter.\n")


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

    def test_v04_governed_artefacts_and_analysis_routes_exist(self):
        governed = {
            "contracts/brand-readiness.md",
            "contracts/customer-intelligence.md",
            "contracts/concept-batch.md",
            "contracts/hook-batch.md",
            "contracts/ad-copy.md",
            "contracts/video-script.md",
            "contracts/static-spec.md",
            "contracts/learning-update.md",
            "contracts/campaign-launch-plan.md",
            "contracts/destination-handoff.md",
            "contracts/ad-diagnosis.md",
            "contracts/creative-audit.md",
        }
        routed = {
            "contracts/creative-audit.md",
            "references/19-ad-analysis-harness.md",
            "examples/ad-analysis-intake.json",
            "examples/creative-audit.md",
            "examples/ad-diagnosis.md",
        }
        # The run tooling moved to agent-ad-analysis-harness. The strategist keeps the
        # output contracts, the reference and the frozen examples, because analysing
        # supplied ads is a strategist capability. Only the harness left.
        extracted = {
            "scripts/ad_analysis_harness.py",
            "scripts/init-ad-analysis-run.py",
            "scripts/validate-ad-analysis-run.py",
            "schemas/ad-analysis-intake.schema.json",
            "tests/test_ad_analysis_harness.py",
        }

        self.assertEqual(set(), {path for path in governed if not (ROOT / path).is_file()})
        self.assertEqual(set(), {path for path in routed if not (ROOT / path).is_file()})
        self.assertEqual(set(), {path for path in extracted if (ROOT / path).is_file()})

    def test_analysis_mode_router(self):
        required_phrases = (
            "Analyse supplied ads",
            "no adequate performance data -> Creative Audit",
            "adequate performance data -> Ad Diagnosis",
            "competitor ad -> competitor research",
            "human edit -> Learning Update",
            "input audit",
            "no performance prediction",
            "human confirmation",
            "does not reserve",
            "contracts/creative-audit.md",
            "contracts/ad-diagnosis.md",
            "references/19-ad-analysis-harness.md",
        )

        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text()
                for phrase in required_phrases:
                    self.assertIn(phrase, text)


    def test_creative_audit_has_no_performance_decisions(self):
        path = ROOT / "contracts" / "creative-audit.md"
        self.assertTrue(path.is_file(), "Creative Audit should exist")
        creative = path.read_text()
        outcome_policy = re.search(
            r"`Outcome` contains exactly one literal value:\s*([^\n.]+)",
            creative,
        )

        self.assertIsNotNone(outcome_policy)
        self.assertEqual(
            {"ready", "revise", "block"},
            set(re.findall(r"`([^`]+)`", outcome_policy.group(1))),
        )
        self.assertIn(
            "| Ad | Outcome | Blocking or revision issue | Evidence | Exact change | Owner |",
            creative,
        )

        errors = load_validator().validate(ROOT)
        self.assertNotIn(
            "contracts/creative-audit.md assigns a performance action", errors
        )

    def test_creative_audit_blocks_identifiable_ads_with_missing_creative(self):
        reference = re.sub(
            r"\s+",
            " ",
            (ROOT / "references" / "19-ad-analysis-harness.md").read_text(),
        )

        self.assertIn(
            "An identifiable supplied ad whose creative is missing receives `block`.",
            reference,
        )
        self.assertIn(
            "A manifest-level failure that prevents ad enumeration blocks the report until identity is repaired.",
            reference,
        )

    def test_frozen_creative_audit_uses_only_frozen_input(self):
        intake = json.loads((ROOT / "examples" / "ad-analysis-intake.json").read_text())
        example = (ROOT / "examples" / "creative-audit.md").read_text()

        self.assertIn(f"- Brand: `{intake['brand_slug']}`", example)
        self.assertIn(f"- Market: `{intake['market']}`", example)
        self.assertIn(f"- Product: `{intake['product_id']}`", example)
        self.assertIn("- Evidence version: unavailable; not supplied", example)
        self.assertIn("- Approved-learning version: unavailable; not supplied", example)
        self.assertIn(
            "Visual conclusions: unavailable; attachment contents are not frozen inputs.",
            example,
        )
        self.assertIn(
            "Destination continuity: unavailable; the screenshot contents are not frozen inputs.",
            example,
        )
        self.assertNotRegex(example, r"`SRC-QA-\d{3}`\s+(?:shows|divides)")
        self.assertNotIn("Copy lead and designer", example)
        self.assertNotRegex(example, r"\| Mina Cole \|")
        outcome_owners = re.findall(
            r"^\| `AD-QA-\d{3}` \| `(?:ready|revise|block)` \|.*\| ([^|]+) \|$",
            example,
            re.MULTILINE,
        )
        self.assertEqual(["unassigned", "unassigned"], [owner.strip() for owner in outcome_owners])

    def test_validator_rejects_structural_creative_audit_drift(self):
        validator = load_validator()
        original = (ROOT / "examples" / "creative-audit.md").read_text()

        ready_row = next(
            line
            for line in original.splitlines()
            if line.startswith("| `AD-QA-001` | `ready` |")
        )
        cases = (
            (
                "missing ordered section",
                original.replace(
                    "## 5. Hook coherence and body handoff\n", "", 1
                ),
                "examples/creative-audit.md must contain all 11 sections exactly once and in order",
            ),
            (
                "duplicate intake-ad outcome",
                original.replace(ready_row, ready_row + "\n" + ready_row, 1),
                "examples/creative-audit.md outcome rows must correspond exactly once to intake ads",
            ),
            (
                "unresolved evidence reference",
                original.replace("`SRC-QA-003`", "`SRC-QA-999`", 1),
                "examples/creative-audit.md references unknown evidence source SRC-QA-999",
            ),
            (
                "missing ready example",
                original.replace(
                    "| `AD-QA-001` | `ready` |",
                    "| `AD-QA-001` | `revise` |",
                    1,
                ),
                "examples/creative-audit.md must demonstrate both ready and revise outcomes",
            ),
        )

        for name, mutated, expected_error in cases:
            with self.subTest(name=name):
                temp, root = self.make_root()
                self.addCleanup(temp.cleanup)
                examples = root / "examples"
                examples.mkdir()
                (examples / "creative-audit.md").write_text(mutated)
                (examples / "ad-analysis-intake.json").write_text(
                    (ROOT / "examples" / "ad-analysis-intake.json").read_text()
                )

                errors = validator.validate(root)

                self.assertIn(expected_error, errors)

    def test_frozen_creative_audit_has_complete_structural_correspondence(self):
        validator = load_validator()
        intake = json.loads((ROOT / "examples" / "ad-analysis-intake.json").read_text())
        example = (ROOT / "examples" / "creative-audit.md").read_text()

        self.assertEqual([], validator.creative_audit_example_errors(example, intake))

    def test_ad_diagnosis_allows_only_the_four_governed_actions(self):
        diagnosis = (ROOT / "contracts" / "ad-diagnosis.md").read_text()
        action_policy = re.search(
            r"`Top-level action` contains exactly one literal value:\s*([^\n.]+)",
            diagnosis,
        )

        self.assertIsNotNone(action_policy)
        self.assertEqual(
            {"keep", "ITR", "stop", "scale"},
            set(re.findall(r"`([^`]+)`", action_policy.group(1))),
        )

    def test_frozen_diagnosis_traces_classifications_and_action_thresholds(self):
        validator = load_validator()
        intake = json.loads(
            (ROOT / "examples" / "ad-diagnosis-intake.json").read_text()
        )
        report = (ROOT / "examples" / "ad-diagnosis.md").read_text()
        contract = (ROOT / "contracts" / "ad-diagnosis.md").read_text()

        self.assertIn(
            "Read-validity classification provenance: `strategist judgment`; "
            "the frozen intake does not supply a read-validity classification.",
            report,
        )
        self.assertIn("Classification provenance", contract)
        section = report.split("## 8. Six-decision taxonomy", 1)[1].split(
            "## 9. Ranked change list", 1
        )[0]
        table_lines = [line for line in section.splitlines() if line.startswith("|")]
        headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
        rows = [
            dict(
                zip(
                    headers,
                    [cell.strip() for cell in line.strip("|").split("|")],
                )
            )
            for line in table_lines[2:]
        ]
        self.assertEqual(
            {
                "Full ad name",
                "Decision",
                "Classification provenance",
                "Top-level action",
                "Numbers and thresholds",
                "Likely explanation",
                "Explanation confidence",
                "Execution instruction",
            },
            set(headers),
        )
        self.assertEqual(
            {ad["ad_id"] for ad in intake["ads"]},
            {row["Full ad name"].strip("`") for row in rows},
        )

        threshold_basis = {
            (
                item["metric"],
                str(item["baseline"]),
                item["comparison_window"],
                str(item["threshold"]),
                item["unit"],
            )
            for item in intake["performance"]["threshold_basis"]
        }
        threshold_pattern = re.compile(
            r"`metric=(?P<metric>[^;]+); baseline=(?P<baseline>[^;]+); "
            r"comparison_window=(?P<window>[^;]+); threshold=(?P<threshold>[^;]+); "
            r"unit=(?P<unit>[^`]+)`"
        )
        for row in rows:
            with self.subTest(ad=row["Full ad name"]):
                self.assertEqual(
                    "Strategist judgment; classification absent from frozen intake",
                    row["Classification provenance"],
                )
                match = threshold_pattern.search(row["Numbers and thresholds"])
                self.assertIsNotNone(match)
                self.assertIn(
                    (
                        match.group("metric"),
                        match.group("baseline"),
                        match.group("window"),
                        match.group("threshold"),
                        match.group("unit"),
                    ),
                    threshold_basis,
                )

        business_section = report.split(
            "## 3. What happened: business result", 1
        )[1].split("## 4. What happened: funnel result", 1)[0]
        self.assertNotIn("| Initial test |", business_section)
        self.assertIn("unavailable; not supplied by frozen intake", business_section)
        self.assertEqual(
            [], validator.diagnosis_example_traceability_errors(report, intake)
        )

    def test_validator_rejects_frozen_diagnosis_traceability_drift(self):
        validator = load_validator()
        original = (ROOT / "examples" / "ad-diagnosis.md").read_text()
        read_provenance = (
            "Read-validity classification provenance: `strategist judgment`; "
            "the frozen intake does not supply a read-validity classification."
        )
        cases = (
            (
                "unlabelled read classification",
                original.replace(read_provenance, "", 1),
                "examples/ad-diagnosis.md must label its derived read-validity "
                "classification as strategist judgment or unavailable",
            ),
            (
                "untraced decision classification",
                original.replace(
                    "Strategist judgment; classification absent from frozen intake",
                    "Supplied classification",
                    1,
                ),
                "examples/ad-diagnosis.md decision classifications must identify "
                "frozen-intake provenance or strategist judgment/unavailable",
            ),
            (
                "threshold not in frozen basis",
                original.replace("baseline=106.67", "baseline=999", 1),
                "examples/ad-diagnosis.md action thresholds must resolve exact metric, "
                "baseline, comparison window, threshold and unit from frozen intake",
            ),
            (
                "invented stage",
                original.replace(
                    "unavailable; not supplied by frozen intake", "Initial test", 1
                ),
                "examples/ad-diagnosis.md must not supply an unfrozen stage classification",
            ),
        )

        for name, mutated, expected_error in cases:
            with self.subTest(name=name):
                temp, root = self.make_root()
                self.addCleanup(temp.cleanup)
                examples = root / "examples"
                examples.mkdir()
                (examples / "ad-diagnosis.md").write_text(mutated)
                (examples / "ad-diagnosis-intake.json").write_text(
                    (ROOT / "examples" / "ad-diagnosis-intake.json").read_text()
                )

                errors = validator.validate(root)

                self.assertIn(expected_error, errors)

    def test_analysis_persistence_requires_human_confirmation(self):
        paths = (
            ROOT / "contracts" / "ad-diagnosis.md",
            ROOT / "references" / "19-ad-analysis-harness.md",
        )
        for path in paths:
            self.assertTrue(path.is_file(), f"{path.name} should exist")

        policy = "\n".join(path.read_text() for path in paths)
        for controlled_record in (
            "test-register",
            "winner-library",
            "approved-revision",
        ):
            self.assertIn(controlled_record, policy)
        self.assertIn("human confirmation", policy)

    def test_diagnosis_contract_and_harness_preserve_persistence_boundaries(self):
        required_boundaries = (
            "recommend ITR != reserve CONTST",
            "proposed test observation != approved revision learning",
            "winner graduation requires real Post ID and confirmation",
            "upload-only output is a patch, not persistence",
        )

        for relative in (
            "contracts/ad-diagnosis.md",
            "references/19-ad-analysis-harness.md",
        ):
            with self.subTest(relative=relative):
                policy = (ROOT / relative).read_text()
                for boundary in required_boundaries:
                    self.assertIn(boundary, policy)

    def test_diagnosis_contract_requires_run_provenance_and_patch_only_outputs(self):
        contract = (ROOT / "contracts" / "ad-diagnosis.md").read_text()
        section_one = contract.split("2. **What was tested**", 1)[0]

        for required in (
            "run ID",
            "intake path",
            "validator status",
            "input-audit path",
        ):
            self.assertIn(required, section_one)
        self.assertIn("## Persistence Summary", contract)
        self.assertIn("test-register-patch.yml", contract)
        self.assertIn("matching existing test", contract)
        self.assertIn("must not contain a new test ID", contract)
        self.assertIn(
            "CONTST: unreserved, human decision required",
            contract,
        )

    def test_frozen_diagnosis_patch_allows_only_an_existing_test_observation(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "diagnosis_patch_errors"),
            "package validator should validate diagnosis patches",
        )
        intake = json.loads(
            (ROOT / "examples" / "ad-diagnosis-intake.json").read_text()
        )
        patch_text = (
            ROOT / "examples" / "ad-diagnosis-test-register-patch.yml"
        ).read_text()
        existing_tests = {
            ad["ad_id"].split("_", 1)[0]
            for ad in intake["ads"]
        }

        self.assertEqual(
            [],
            validator.diagnosis_patch_errors(patch_text, existing_tests),
        )

        patch = json.loads(patch_text)
        supplied_results = patch["supplied_results"]
        mutations = (
            (
                {**patch, "owner": "Mina Cole"},
                "unsupported field: owner",
            ),
            (
                {**patch, "new_test_id": "CONTST043"},
                "unsupported field: new_test_id",
            ),
            (
                {**patch, "test_id": "CONTST043"},
                "unsupported field: test_id",
            ),
            (
                {**patch, "matching_existing_test": "CONTST043"},
                "matching_existing_test must identify an existing test",
            ),
            (
                {**patch, "winner_library": {"real_post_id": "991001"}},
                "unsupported field: winner_library",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "spend_aud": {"new_test_id": "CONTST043"},
                    },
                },
                "supplied_results contains forbidden controlled field: new_test_id",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "purchases": [
                            {"winner_library": {"real_post_id": "991001"}}
                        ],
                    },
                },
                "supplied_results contains forbidden controlled field: winner_library",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "commentary": "directional read",
                    },
                },
                "supplied_results unsupported field: commentary",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        key: value
                        for key, value in supplied_results.items()
                        if key != "purchase_value_aud"
                    },
                },
                "supplied_results missing required field: purchase_value_aud",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "window_full_days": False,
                    },
                },
                "supplied_results window_full_days must be a non-negative integer",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "target_cac_aud": "60",
                    },
                },
                "supplied_results target_cac_aud must be a non-negative number",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "spend_aud": float("nan"),
                    },
                },
                "supplied_results spend_aud must be finite",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "spend_aud": float("inf"),
                    },
                },
                "supplied_results spend_aud must be finite",
            ),
            (
                {
                    **patch,
                    "supplied_results": {
                        **supplied_results,
                        "spend_aud": float("-inf"),
                    },
                },
                "supplied_results spend_aud must be finite",
            ),
        )
        for mutation, expected in mutations:
            with self.subTest(expected=expected):
                errors = validator.diagnosis_patch_errors(
                    json.dumps(mutation), existing_tests
                )
                self.assertIn(expected, errors)

        valid_float_patch = {
            **patch,
            "supplied_results": {
                **supplied_results,
                "target_cac_aud": 60.5,
            },
        }
        self.assertEqual(
            [],
            validator.diagnosis_patch_errors(
                json.dumps(valid_float_patch), existing_tests
            ),
        )

        valid_large_integer_patch = {
            **patch,
            "supplied_results": {
                **supplied_results,
                "spend_aud": 10**1000,
            },
        }
        try:
            large_integer_errors = validator.diagnosis_patch_errors(
                json.dumps(valid_large_integer_patch), existing_tests
            )
        except OverflowError as error:
            self.fail(f"valid large JSON integers must not raise: {error}")
        self.assertEqual([], large_integer_errors)

    def test_frozen_diagnosis_patch_results_reconcile_to_csv_and_intake(self):
        patch = json.loads(
            (ROOT / "examples" / "ad-diagnosis-test-register-patch.yml").read_text()
        )
        intake = json.loads(
            (ROOT / "examples" / "ad-diagnosis-intake.json").read_text()
        )
        with (ROOT / "examples" / "ad-diagnosis-performance.csv").open(
            newline=""
        ) as source:
            rows = list(csv.DictReader(source))

        date_range = intake["performance"]["date_range"]
        window_full_days = (
            datetime.date.fromisoformat(date_range["end"])
            - datetime.date.fromisoformat(date_range["start"])
        ).days + 1
        target_cac_values = {int(row["Target CAC (AUD)"]) for row in rows}
        minimum_spend_values = {
            int(row["Minimum batch spend (AUD)"]) for row in rows
        }
        minimum_purchase_values = {
            int(row["Minimum batch purchases"]) for row in rows
        }
        self.assertEqual(1, len(target_cac_values))
        self.assertEqual(1, len(minimum_spend_values))
        self.assertEqual(1, len(minimum_purchase_values))

        expected_supplied_results = {
            "window_full_days": window_full_days,
            "spend_aud": sum(int(row["Amount spent (AUD)"]) for row in rows),
            "purchases": sum(int(row["Purchases"]) for row in rows),
            "purchase_value_aud": sum(
                int(row["Purchase value (AUD)"]) for row in rows
            ),
            "target_cac_aud": target_cac_values.pop(),
            "minimum_batch_spend_aud": minimum_spend_values.pop(),
            "minimum_batch_purchases": minimum_purchase_values.pop(),
        }
        self.assertEqual(expected_supplied_results, patch["supplied_results"])


    def test_diagnosis_raw_fixtures_stay_out_of_templates_and_generated_bundle(self):
        fixtures = (
            "examples/ad-diagnosis-intake.json",
            "examples/ad-diagnosis-input-audit.md",
            "examples/ad-diagnosis-performance.csv",
            "examples/ad-diagnosis-test-register-patch.yml",
        )
        for relative in fixtures:
            self.assertTrue((ROOT / relative).is_file())
            self.assertEqual(
                [],
                list((ROOT / "templates").rglob(pathlib.Path(relative).name)),
            )
        bundle = load_bundle_builder().build_body()
        for relative in fixtures:
            self.assertNotIn(relative, bundle)


    def test_reports_missing_v04_required_artefacts(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn(
            "missing v0.4 required file: contracts/creative-audit.md", errors
        )

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

    def test_option_counts_are_guidance_with_a_floor(self):
        # Forced counts produce filler. Only the CTA is fixed.
        ad_copy = (ROOT / "contracts" / "ad-copy.md").read_text()
        hook_batch = (ROOT / "contracts" / "hook-batch.md").read_text()

        self.assertNotIn("Headlines: exactly 5", ad_copy)
        self.assertNotIn("Lead routes: exactly 2", ad_copy)
        self.assertIn("CTA: exactly 1", ad_copy)
        self.assertIn("3 minimum", ad_copy)
        self.assertNotIn("Create exactly six hook packages", hook_batch)
        self.assertIn("Three is the floor.", hook_batch)

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

    def test_package_declares_v04_and_portable_brand_folder(self):
        self.assertRegex((ROOT / "VERSION").read_text().strip(), r"^\d+\.\d+\.\d+$")
        readme = (ROOT / "README.md").read_text()

        self.assertIn("brand folder", readme.lower())
        self.assertIn("Firecrawl", readme)
        self.assertIn("Grok Agents", readme)

    def test_v04_public_release_documents_complete_ad_analysis_workflow(self):
        readme = (ROOT / "README.md").read_text()
        normalized = " ".join(readme.split()).lower()

        declared = (ROOT / "VERSION").read_text().strip()
        self.assertIn(f"**Version:** {declared}", readme)
        self.assertIn("thirteen governed artefacts", readme)
        self.assertIn("| Creative Audit |", readme)
        self.assertIn("Analyse these ads for <brand>", readme)
        self.assertIn("creative-audit", readme)
        self.assertIn("performance-diagnosis", readme)
        self.assertIn("scripts/init-ad-analysis-run.py", readme)
        self.assertIn("scripts/validate-ad-analysis-run.py", readme)
        self.assertIn("outputs/ad-analysis/<RUN_ID>/creative-audit.md", readme)
        self.assertIn("outputs/ad-analysis/<RUN_ID>/diagnosis.md", readme)
        self.assertIn("upload-only output is a patch, not persistence", readme)
        self.assertIn("Migrating a v0.3 brand folder", readme)
        self.assertIn(
            "preserve all existing evidence, learning, test and strategy history",
            normalized,
        )

    def test_every_runtime_guide_supports_connected_and_upload_analysis(self):
        required = (
            "## Ad analysis: connected-folder mode",
            "## Ad analysis: upload-only mode",
            "creative-audit",
            "performance-diagnosis",
            "scripts/init-ad-analysis-run.py",
            "scripts/validate-ad-analysis-run.py",
            "intake.json",
            "dist/knowledge-bundle.md",
            "selected generated brand bundle",
            "every referenced attachment or source file",
            "creative-audit.md",
            "diagnosis.md",
            "upload-only output is a patch, not persistence",
            "read-only preflight",
        )

        for relative in RUNTIME_GUIDES:
            with self.subTest(relative=relative):
                guide = " ".join((ROOT / relative).read_text().split())
                for phrase in required:
                    self.assertIn(phrase, guide)

    def test_every_upload_workflow_uses_the_exact_five_part_pack(self):
        anchor = "The exact upload pack is:"

        for relative in UPLOAD_WORKFLOW_DOCS:
            with self.subTest(relative=relative):
                normalized = " ".join((ROOT / relative).read_text().split())
                self.assertIn(anchor, normalized)
                upload_section = normalized.split(anchor, 1)[1]
                for item in UPLOAD_CHECKLIST:
                    self.assertIn(item, upload_section)
                positions = [upload_section.index(item) for item in UPLOAD_CHECKLIST]
                self.assertEqual(sorted(positions), positions)
                self.assertIn(UPLOAD_LABEL_BOUNDARY, upload_section)

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

    def test_universal_bundle_includes_v04_contract_reference_and_schema_guidance(self):
        builder = load_bundle_builder()

        content = builder.build_body()

        self.assertIn("<!-- source: contracts/creative-audit.md -->", content)
        self.assertIn("<!-- source: references/19-ad-analysis-harness.md -->", content)
        self.assertIn("# PART: SCHEMA GUIDANCE", content)
        self.assertIn("<!-- source: schemas/swipe-entry.schema.json -->", content)
        self.assertIn("performance-diagnosis", content)
        self.assertNotIn("<!-- source: examples/ad-diagnosis-performance.csv -->", content)
        self.assertNotIn("<!-- source: outputs/ad-analysis/", content)

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


    def test_allows_most_aware_theory_and_explicit_standard_ad_negations(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        references = root / "references"
        references.mkdir()
        (references / "02-customer-state.md").write_text(
            "Most Aware remains part of customer-awareness theory.\n"
            "Most Aware is not a standard ad.\n"
            "Never turn Most Aware into a standard ad.\n"
        )

        errors = validator.validate(root)

        self.assertNotIn(
            "references/02-customer-state.md prescribes a Most Aware standard ad",
            errors,
        )


    def test_read_validity_boundaries_are_mutually_exclusive(self):
        validator = load_validator()
        cases = (
            ((3, True, True, False, False, False), "Too early"),
            ((5, False, False, False, False, False), "Too early"),
            ((5, True, False, False, False, False), "Direction"),
            ((5, False, True, False, False, False), "Direction"),
            ((5, True, True, False, False, False), "Verdict"),
            ((5, True, True, False, True, False), "Direction"),
            ((5, True, True, False, False, True), "Direction"),
            ((5, True, True, True, False, False), "Direction"),
        )

        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                self.assertEqual(
                    expected, validator.classify_read_validity(*arguments)
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

    def test_package_contst_lexeme_accepts_only_ascii_digits(self):
        validator = load_validator()

        self.assertIsNotNone(
            validator.CONTST_TEST_ID.search("  - test_id: CONTST001")
        )
        self.assertIsNone(
            validator.CONTST_TEST_ID.search("  - test_id: CONTST٠٠١")
        )


    def test_reports_missing_v04_release_requirements(self):
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

        self.assertNotIn(
            "VERSION must use major.minor.patch format, found '0.2.0'", errors
        )

    CRAFT_STACK = (
        "references/01-foundations.md",
        "references/02-customer-state.md",
        "references/03-strategy-and-offer.md",
        "references/04-persuasion.md",
        "references/05-copy-craft.md",
        "references/08-formats.md",
        "references/10-voice-and-claims.md",
        "references/12-meta-platform.md",
        "references/16-hook-formats.md",
        "references/20-hook-quality-standard.md",
        "references/21-evidence-and-doctrine.md",
        "references/22-swipe-corpus.md",
        "references/23-commercial-context.md",
        "references/24-writing-for-low-awareness.md",
    )

    def craft_stack_section(self):
        validator = load_validator()
        return validator.markdown_section(
            (ROOT / "SKILL.md").read_text(), "The craft stack, always loaded"
        )

    def test_craft_stack_is_complete_and_always_loaded(self):
        section = self.craft_stack_section()

        self.assertNotEqual("", section, "SKILL.md must declare an always-loaded stack")
        for relative in self.CRAFT_STACK:
            with self.subTest(relative=relative):
                self.assertIn(relative, section)
                self.assertTrue((ROOT / relative).is_file())

    def test_craft_references_are_not_gated_behind_the_ops_stack(self):
        validator = load_validator()
        ops = validator.markdown_section(
            (ROOT / "SKILL.md").read_text(), "The ops stack, loaded only when relevant"
        )

        self.assertNotEqual("", ops)
        for relative in self.CRAFT_STACK:
            with self.subTest(relative=relative):
                self.assertNotIn(relative, ops)

    def test_entrypoints_do_not_restrict_reference_loading(self):
        # The selective-loading rule is what kept the awareness model and the
        # platform data out of the modes that write ads.
        for relative in ("SKILL.md", "AGENTS.md"):
            with self.subTest(relative=relative):
                self.assertNotIn(
                    "Load only the references routed below",
                    (ROOT / relative).read_text(),
                )

    def test_strategist_read_is_an_available_format(self):
        contract = ROOT / "contracts" / "strategist-read.md"

        self.assertTrue(contract.is_file())
        for relative in ("SKILL.md", "OUTPUT-CONTRACT.md", "README.md"):
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text()
                self.assertTrue(
                    "contracts/strategist-read.md" in text
                    or "Strategist Read" in text,
                    f"{relative} does not offer the Strategist Read format",
                )

    def test_thin_input_is_marked_rather_than_refused(self):
        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text()
                self.assertIn("Never invent. Never refuse. Always mark.", text)
                self.assertIn("[CLAIM: needs approved wording]", text)

    def test_a_marker_may_not_wrap_a_guess(self):
        # The first eval run found the agent writing an invented statistic and
        # tagging it for removal. A marker that wraps a guess is worse than none.
        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text()
                self.assertIn("never wraps a guess", text)
                self.assertIn("[STAT: needs a real figure", text)

    def test_cold_traffic_may_not_be_answered_with_a_product_led_opening(self):
        # The same run found offer-led openings on a UWA brief, pulled by the
        # aggregate hit-rate data. The resolution states it as a constraint.
        resolution = (ROOT / "references" / "21-evidence-and-doctrine.md").read_text()

        self.assertIn("This is a constraint, not a trade-off.", resolution)
        self.assertIn("is a failure of the brief", resolution)

    def test_every_produced_artefact_has_a_frozen_example(self):
        # The package previously had no example of ad copy, a script or a static
        # spec: every artefact a customer would read was unexemplified while every
        # bookkeeping artefact had one.
        contracts = {path.name for path in (ROOT / "contracts").glob("*.md")}
        examples = {path.name for path in (ROOT / "examples").glob("*.md")}
        # Research and planning artefacts, exempt for now and named rather than silent.
        exempt = {"concept-batch.md", "customer-intelligence.md"}

        self.assertEqual(set(), contracts - examples - exempt)

    def test_the_worked_examples_share_one_execution(self):
        # Hook batch, video script and ad copy cover the same SLA execution so the
        # set reads as one case rather than three disconnected samples.
        for name in ("hook-batch.md", "video-script.md", "ad-copy.md"):
            with self.subTest(example=name):
                text = (ROOT / "examples" / name).read_text()
                self.assertIn("CONTST004", text)
                self.assertIn(
                    "Same six cables. Two very different ways to find one", text
                )
        static = (ROOT / "examples" / "static-spec.md").read_text()
        self.assertIn("CONTST004", static)
        self.assertIn("PRA, diagnosis", static)

    def test_the_static_example_clears_generated_imagery(self):
        static = (ROOT / "examples" / "static-spec.md").read_text()

        self.assertIn("Image-model prompt", static)
        self.assertIn("Generated imagery check", static)
        self.assertIn("Before and after", static)
        self.assertIn("Copy is composited, not generated", static)

    def test_the_read_example_disagrees_with_its_request(self):
        read = (ROOT / "examples" / "strategist-read.md").read_text()

        # The contract requires the finding first and permits disagreeing with the ask.
        self.assertIn("## 1. The read", read)
        self.assertIn("the offer is the problem", read)
        self.assertIn("[UNSOURCED, strategist judgement]", read)

    def test_craft_bundle_carries_the_stack_and_no_install_guides(self):
        builder = load_module(ROOT / "scripts" / "build-craft-bundle.py", "build_craft")
        bundle = builder.build()

        for relative in self.CRAFT_STACK:
            with self.subTest(relative=relative):
                self.assertIn(f"<!-- source: {relative} -->", bundle)
        self.assertIn("<!-- source: contracts/strategist-read.md -->", bundle)
        self.assertIn("<!-- source: PROMPT.md -->", bundle)
        # The point of the craft bundle is that it spends no context on setup.
        for excluded in (
            "connectors/runtime-chatgpt.md",
            "references/17-runtime-portability.md",
            "references/07-naming.md",
            "references/19-ad-analysis-harness.md",
        ):
            with self.subTest(excluded=excluded):
                self.assertNotIn(f"<!-- source: {excluded} -->", bundle)

    def test_craft_bundle_reads_the_stack_from_the_skill(self):
        builder = load_module(ROOT / "scripts" / "build-craft-bundle.py", "build_craft")

        self.assertEqual(list(self.CRAFT_STACK), builder.craft_stack())

    def test_craft_bundle_is_smaller_than_the_full_bundle(self):
        craft = load_module(ROOT / "scripts" / "build-craft-bundle.py", "build_craft")
        full = load_bundle_builder()

        self.assertLess(len(craft.build()), len(full.build_body()))

    def load_corpus(self):
        path = ROOT / "corpus" / "swipe" / "entries.json"
        self.assertTrue(path.is_file(), "corpus/swipe/entries.json should exist")
        return json.loads(path.read_text())["entries"]

    def test_corpus_entries_match_the_schema_shape(self):
        schema = json.loads(
            (ROOT / "schemas" / "swipe-entry.schema.json").read_text()
        )
        allowed = set(schema["properties"])
        required = set(schema["required"])
        codes = {"UWA", "PRA", "SLA", "PDA", None}
        bases = {"mention-ratio", "inferred-from-copy", "unavailable"}

        for entry in self.load_corpus():
            with self.subTest(entry=entry.get("id")):
                self.assertLessEqual(set(entry), allowed)
                self.assertLessEqual(required, set(entry))
                self.assertIn(entry["awareness"]["code"], codes)
                self.assertIn(entry["awareness"]["basis"], bases)
                self.assertEqual("behavioural", entry["evidence"]["class"])

    def test_corpus_annotations_are_unreviewed_until_a_human_confirms(self):
        entries = self.load_corpus()

        for entry in entries:
            with self.subTest(entry=entry.get("id")):
                self.assertIsInstance(entry["reviewed"], bool)
                if entry["reviewed"]:
                    self.assertIsNotNone(
                        entry["annotation"],
                        "an entry cannot be reviewed without an annotation",
                    )

    def test_awareness_proxy_bands_the_mention_ratio(self):
        sync = load_module(ROOT / "scripts" / "sync-swipe-corpus.py", "sync_swipe")

        self.assertEqual("PDA", sync.awareness_from(60.0, 3.0)["code"])
        self.assertEqual("SLA", sync.awareness_from(60.0, 18.0)["code"])
        self.assertEqual("PRA", sync.awareness_from(60.0, 30.0)["code"])
        self.assertEqual("UWA", sync.awareness_from(60.0, 50.0)["code"])
        self.assertEqual("UWA", sync.awareness_from(60.0, -1.0)["code"])
        self.assertEqual("unavailable", sync.awareness_from(None, None)["basis"])
        self.assertEqual("unavailable", sync.awareness_from(0, 5.0)["basis"])

    def test_corpus_sync_never_discards_human_annotation(self):
        sync = load_module(ROOT / "scripts" / "sync-swipe-corpus.py", "sync_swipe")
        existing = [
            {
                "id": "keep-me",
                "annotation": {"why_it_works": "a human wrote this"},
                "reviewed": True,
            },
            {"id": "off-the-board", "annotation": {"why_it_works": "also human"}, "reviewed": True},
        ]
        fetched = [
            {"id": "keep-me", "annotation": None, "reviewed": False, "evidence": {"running_days": 5}},
            {"id": "brand-new", "annotation": None, "reviewed": False, "evidence": {"running_days": 9}},
        ]

        merged, counts = sync.merge(existing, fetched)
        by_id = {entry["id"]: entry for entry in merged}

        self.assertEqual("a human wrote this", by_id["keep-me"]["annotation"]["why_it_works"])
        self.assertTrue(by_id["keep-me"]["reviewed"])
        self.assertIn("off-the-board", by_id, "an entry leaving the board must not be dropped")
        self.assertIsNone(by_id["brand-new"]["annotation"])
        self.assertEqual(1, counts["added"])
        self.assertEqual(1, counts["annotations_kept"])

    def test_swipe_digest_is_generated_and_current(self):
        builder = load_module(ROOT / "scripts" / "build-swipe-digest.py", "build_digest")
        entries = self.load_corpus()

        self.assertEqual(
            (ROOT / "references" / "22-swipe-corpus.md").read_text(),
            builder.build_digest(entries),
            "run scripts/build-swipe-digest.py",
        )
        self.assertEqual(
            (ROOT / "corpus" / "swipe" / "REVIEW.md").read_text(),
            builder.build_review(entries),
            "run scripts/build-swipe-digest.py",
        )

    def test_swipe_digest_states_the_evidence_class(self):
        digest = (ROOT / "references" / "22-swipe-corpus.md").read_text()

        self.assertIn("behavioural evidence, never performance", digest)
        self.assertIn("Awareness codes are a proxy", digest)
        self.assertIn("never-named sentinel is unreliable", digest)

    def test_repository_contains_no_em_or_en_dashes(self):
        validator = load_validator()

        self.assertEqual([], validator.dash_errors(ROOT))

    def test_dash_check_reports_the_offending_line(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        (root / "notes.md").write_text("fine line\nbad \u2014 line\nfine again\n")
        (root / "ranges.md").write_text("pages 2\u20135\n")

        errors = validator.dash_errors(root)

        self.assertIn("notes.md:2 contains an em dash", errors)
        self.assertIn("ranges.md:1 contains an en dash", errors)

    def test_dash_check_exempts_only_verbatim_third_party_copy(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        (root / "corpus" / "swipe").mkdir(parents=True)
        (root / "corpus" / "swipe" / "entries.json").write_text('{"copy": "as \u2014 it ran"}')
        (root / "references").mkdir()
        (root / "references" / "22-swipe-corpus.md").write_text("quoted \u2014 hook\n")
        (root / "references" / "05-copy-craft.md").write_text("our own \u2014 prose\n")

        errors = validator.dash_errors(root)

        self.assertEqual(["references/05-copy-craft.md:1 contains an em dash"], errors)

    def test_invariant_reader_handles_quoted_values_and_missing_keys(self):
        validator = load_validator()
        source = (ROOT / "invariants.yml").read_text()

        # The ad-set shape contains a hash and must not be read as a comment.
        self.assertEqual(
            "[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]",
            validator.read_invariant(source, "naming.ad_set"),
        )
        self.assertEqual(
            "ABO", validator.read_invariant(source, "creative_testing.budget_type")
        )
        self.assertEqual(
            "PDP", validator.read_invariant(source, "destinations.defaults.SLA")
        )
        self.assertIsNone(validator.read_invariant(source, "nothing.here"))

    def test_shipped_prose_carries_every_declared_invariant(self):
        validator = load_validator()

        self.assertEqual([], validator.invariant_drift_errors(ROOT))

    def test_reports_an_invariant_dropped_from_the_prose(self):
        validator = load_validator()
        temp, root = self.make_release_policy_root()
        self.addCleanup(temp.cleanup)
        skill = root / "SKILL.md"
        skill.write_text(
            skill.read_text().replace("an absolute $50 floor", "no floor")
        )

        errors = validator.invariant_drift_errors(root)

        self.assertIn(
            "SKILL.md launch invariants lost "
            "budget.absolute_floor_per_ad_set_per_day: '$50'",
            errors,
        )

    def test_reports_a_dropped_observation_window(self):
        validator = load_validator()
        temp, root = self.make_release_policy_root()
        self.addCleanup(temp.cleanup)
        skill = root / "SKILL.md"
        skill.write_text(
            skill.read_text().replace(
                "Protect five full days of observation.", "Read it whenever."
            )
        )

        errors = validator.invariant_drift_errors(root)

        self.assertIn(
            "SKILL.md launch invariants lost the five-full-day observation window",
            errors,
        )

    def test_reports_a_malformed_version(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        (root / "VERSION").write_text("v0.5\n")

        errors = validator.validate(root)

        self.assertIn(
            "VERSION must use major.minor.patch format, found 'v0.5'", errors
        )

    def test_reports_a_version_declaration_that_disagrees_with_version_file(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        (root / "VERSION").write_text("0.5.0\n")
        (root / "README.md").write_text("**Version:** 0.4.0\n")
        brand = root / "templates" / "brand-folder" / "brand.yml"
        brand.parent.mkdir(parents=True, exist_ok=True)
        brand.write_text('slug: "example"\nmethod_version: "0.4.0"\n')

        errors = validator.validate(root)

        self.assertIn(
            "README.md declares the package version '0.4.0' but VERSION is '0.5.0'",
            errors,
        )
        self.assertIn(
            "templates/brand-folder/brand.yml declares method_version '0.4.0' "
            "but VERSION is '0.5.0'",
            errors,
        )

    def test_accepts_version_declarations_that_agree(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        (root / "VERSION").write_text("0.5.0\n")
        (root / "README.md").write_text("**Version:** 0.5.0\n")
        brand = root / "templates" / "brand-folder" / "brand.yml"
        brand.parent.mkdir(parents=True, exist_ok=True)
        brand.write_text('slug: "example"\nmethod_version: "0.5.0"\n')

        errors = validator.validate(root)

        self.assertEqual(
            [], [error for error in errors if "VERSION" in error]
        )


if __name__ == "__main__":
    unittest.main()
