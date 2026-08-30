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

LAUNCH_INVARIANTS = """## Upload-runtime routing

For manual Meta launch asks, load `contracts/campaign-launch-plan.md` and
`references/09-testing-and-diagnosis.md`. For destination asks, load
`contracts/destination-handoff.md`.

## Launch invariants

- Creative testing uses one CT campaign per product and region, ABO, and exactly one CONTST batch per ad set.
- Every initial NNT or INSPO batch contains exactly four ads: UWA, PRA, SLA and PDA.
- The daily ad-set budget has an absolute $50 floor and an approximately $100 preferred starting point.
- Protect five full days of observation. A five-day read is still directional or too early unless every active validity threshold is met.
- Scaling uses a separate SC campaign with CBO, and graduated ads retain their real Post IDs.
- Campaign names use `[BRAND]_[PRODUCT]_[CT|SC]_[ABO|CBO]_[REGION]_[YYYYMMDD]`.
- Ad-set names use `[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]`.
- Ad names use `[FULL_AD_SET_NAME]_[UWA|PRA|SLA|PDA]_[FORMAT]_[LP|PDP|HP|CP]_[POSTID]`.
- UWA and PRA default to LP; SLA and PDA default to PDP. Every exception maps to LP, PDP, HP or CP through a Destination Handoff.
- Every new ad name ends in `POSTIDXXX`; after publication, preserve the real Post ID.
- Launch plans and changes are manual only. Never publish ads or change budgets automatically.
- Generic count overrides cannot change the locked four initial NNT or INSPO ads or one selected hook per launch ad. Only a human-reviewed universal-method change can alter these invariants.
"""

AD_ANALYSIS_ROUTING = """## Ad-analysis routing

For supplied first-party ads, load `references/19-ad-analysis-harness.md`, validate `intake.json`
and consume the input audit before conclusions. Route exactly:

- no adequate performance data -> Creative Audit;
- adequate performance data -> Ad Diagnosis;
- competitor ad -> competitor research;
- human edit -> Learning Update.

Combined adequate creative and performance produces one Ad Diagnosis. Incomplete performance
material produces the input audit first; do not silently infer a performance explanation. Creative
Audit makes no performance prediction and cannot assign `keep`, `ITR`, `stop` or `scale`. Reports
may be written to the run folder, but controlled records require human confirmation, and diagnosis
does not reserve a new CONTST.
"""


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

    def make_release_policy_root(self):
        temp = tempfile.TemporaryDirectory()
        root = pathlib.Path(temp.name)
        relatives = (
            "SKILL.md",
            "AGENTS.md",
            "PROMPT.md",
            "VERSION",
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

    def test_reports_entrypoint_drift(self):
        validator = load_validator()
        temp, root = self.make_root(
            skill_body="# Marketing Strategist\n\nOne body.\n",
            agents_body="# Marketing Strategist\n\nAnother body.\n",
        )
        self.addCleanup(temp.cleanup)

        errors = validator.validate(root)

        self.assertIn("SKILL.md and AGENTS.md operating bodies have drifted", errors)

    def test_reports_launch_invariant_drift_in_all_three_entrypoints(self):
        validator = load_validator()
        cases = (
            (
                "Creative testing uses one CT campaign per product and region, ABO, and exactly one CONTST batch per ad set.",
                "Creative testing uses CBO and mixes CONTST batches in an ad set.",
                "must require CT/ABO with one CONTST batch per ad set",
            ),
            (
                "Generic count overrides cannot change the locked four initial NNT or INSPO ads or one selected hook per launch ad.",
                "Generic count overrides may change every launch count.",
                "must protect locked initial-ad and selected-hook counts",
            ),
        )

        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            for expected, opposite, error_suffix in cases:
                with self.subTest(relative=relative, error=error_suffix):
                    temp, root = self.make_root(
                        skill_body="# Marketing Strategist\n\n" + LAUNCH_INVARIANTS,
                        agents_body="# Marketing Strategist\n\n" + LAUNCH_INVARIANTS,
                    )
                    self.addCleanup(temp.cleanup)
                    (root / "PROMPT.md").write_text(LAUNCH_INVARIANTS)
                    path = root / relative
                    path.write_text(path.read_text().replace(expected, opposite))

                    errors = validator.validate(root)

                    self.assertIn(f"{relative} {error_suffix}", errors)

    def test_reports_each_missing_prompt_launch_invariant(self):
        validator = load_validator()
        required_lines = [
            line
            for line in LAUNCH_INVARIANTS.splitlines()
            if line.startswith(("For manual Meta", "- "))
        ]

        for line in required_lines:
            with self.subTest(line=line):
                temp, root = self.make_root(
                    skill_body="# Marketing Strategist\n\n" + LAUNCH_INVARIANTS,
                    agents_body="# Marketing Strategist\n\n" + LAUNCH_INVARIANTS,
                )
                self.addCleanup(temp.cleanup)
                (root / "PROMPT.md").write_text(LAUNCH_INVARIANTS.replace(line, ""))

                errors = validator.validate(root)

                self.assertTrue(
                    any(error.startswith("PROMPT.md must") for error in errors),
                    f"missing semantic error for: {line}",
                )

    def test_reports_additive_policy_contradictions_with_canonical_text_intact(self):
        validator = load_validator()
        cases = (
            (
                "PROMPT.md",
                "Initial NNT uses five ads.\n",
                "PROMPT.md contains contradictory initial-ad count",
            ),
            (
                "PROMPT.md",
                "Launch plans may auto-publish ads.\n",
                "PROMPT.md permits automatic Meta publishing or budget changes",
            ),
            (
                "references/09-testing-and-diagnosis.md",
                "High volume on day three permits a Verdict.\n",
                "references/09-testing-and-diagnosis.md permits a Verdict before five full days",
            ),
            (
                "references/12-meta-platform.md",
                "Default test duration is seven days.\n",
                "references/12-meta-platform.md sets a seven-day default test duration",
            ),
            (
                "references/06-concept-model.md",
                "MWA is a standard ad, not a landing-page role.\n",
                "references/06-concept-model.md prescribes a Most Aware standard ad",
            ),
        )

        for relative, addition, expected_error in cases:
            with self.subTest(relative=relative, addition=addition):
                temp, root = self.make_release_policy_root()
                self.addCleanup(temp.cleanup)
                target = root / relative
                target.write_text(target.read_text() + "\n" + addition)

                errors = validator.validate(root)

                self.assertIn(expected_error, errors)

    def test_reports_likely_additive_policy_phrasing_variants(self):
        validator = load_validator()
        cases = (
            (
                "PROMPT.md",
                "Every initial INSPO test contains 5 standalone ads.\n",
                "PROMPT.md contains contradictory initial-ad count",
            ),
            (
                "PROMPT.md",
                "Budgets can be changed automatically after launch.\n",
                "PROMPT.md permits automatic Meta publishing or budget changes",
            ),
            (
                "references/09-testing-and-diagnosis.md",
                "A day-3 read can qualify as a Verdict when volume is high.\n",
                "references/09-testing-and-diagnosis.md permits a Verdict before five full days",
            ),
            (
                "references/12-meta-platform.md",
                "Use 7 days as the standard test duration.\n",
                "references/12-meta-platform.md sets a seven-day default test duration",
            ),
            (
                "references/06-concept-model.md",
                "Every initial batch should include an MWA standard ad.\n",
                "references/06-concept-model.md prescribes a Most Aware standard ad",
            ),
            (
                "references/06-concept-model.md",
                "MWA is a standard ad—not a landing-page role.\n",
                "references/06-concept-model.md prescribes a Most Aware standard ad",
            ),
        )

        for relative, addition, expected_error in cases:
            with self.subTest(relative=relative, addition=addition):
                temp, root = self.make_release_policy_root()
                self.addCleanup(temp.cleanup)
                target = root / relative
                target.write_text(target.read_text() + "\n" + addition)

                errors = validator.validate(root)

                self.assertIn(expected_error, errors)

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
            "schemas/ad-analysis-intake.schema.json",
            "examples/ad-analysis-intake.json",
            "examples/creative-audit.md",
            "examples/ad-diagnosis.md",
            "scripts/init-ad-analysis-run.py",
            "scripts/validate-ad-analysis-run.py",
        }

        self.assertEqual(set(), {path for path in governed if not (ROOT / path).is_file()})
        self.assertEqual(set(), {path for path in routed if not (ROOT / path).is_file()})

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

    def test_validator_rejects_ad_analysis_router_mutations_in_every_entrypoint(self):
        validator = load_validator()
        contradictions = (
            "Adequate performance data may route to Creative Audit.",
            "Combined adequate creative and performance produces two reports: Ad Diagnosis and Creative Audit.",
            "Combined adequate creative and performance uses both Creative Audit and Ad Diagnosis.",
            "Combined adequate creative and performance automatically uses both Creative Audit and Ad Diagnosis.",
            "Combined adequate creative and performance creates two reports: Creative Audit and Ad Diagnosis.",
            "Incomplete performance may produce conclusions before the input audit.",
            "Adequate performance data must not use preliminary notes before it routes to Creative Audit.",
            "Combined adequate creative and performance must not use preliminary notes before it produces two reports: Ad Diagnosis and Creative Audit.",
            "Incomplete performance must not use preliminary notes before it produces conclusions before the input audit.",
            "Adequate performance data routes to a mode that must not use preliminary notes: Creative Audit.",
            "Combined adequate creative and performance produces two reports: Ad Diagnosis must not use preliminary notes and Creative Audit.",
            "Incomplete performance produces conclusions that must not use preliminary notes before the input audit.",
        )

        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            for contradiction in contradictions:
                with self.subTest(relative=relative, contradiction=contradiction):
                    body = "# Marketing Strategist\n\n" + LAUNCH_INVARIANTS + AD_ANALYSIS_ROUTING
                    temp, root = self.make_root(skill_body=body, agents_body=body)
                    self.addCleanup(temp.cleanup)
                    (root / "PROMPT.md").write_text(body)
                    path = root / relative
                    path.write_text(path.read_text() + "\n" + contradiction + "\n")

                    errors = validator.validate(root)

                    self.assertIn(
                        f"{relative} contains contradictory ad-analysis routing",
                        errors,
                    )

    def test_validator_accepts_explicit_ad_analysis_router_prohibitions(self):
        validator = load_validator()
        safeguards = (
            "Adequate performance data must not route to Creative Audit.",
            "Combined adequate creative and performance never produces two reports: Ad Diagnosis and Creative Audit.",
            "Combined adequate creative and performance never uses both Creative Audit and Ad Diagnosis.",
            "Combined adequate creative and performance never automatically uses both Creative Audit and Ad Diagnosis.",
            "Combined adequate creative and performance must not create two reports: Creative Audit and Ad Diagnosis.",
            "Incomplete performance must not produce conclusions before the input audit.",
        )

        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            for safeguard in safeguards:
                with self.subTest(relative=relative, safeguard=safeguard):
                    body = "# Marketing Strategist\n\n" + LAUNCH_INVARIANTS + AD_ANALYSIS_ROUTING
                    temp, root = self.make_root(skill_body=body, agents_body=body)
                    self.addCleanup(temp.cleanup)
                    (root / "PROMPT.md").write_text(body)
                    path = root / relative
                    path.write_text(path.read_text() + "\n" + safeguard + "\n")

                    errors = validator.validate(root)

                    self.assertNotIn(
                        f"{relative} contains contradictory ad-analysis routing",
                        errors,
                    )

    def test_validator_rejects_normalized_ad_analysis_router_drift(self):
        validator = load_validator()
        body = "# Marketing Strategist\n\n" + LAUNCH_INVARIANTS + AD_ANALYSIS_ROUTING

        for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
            with self.subTest(relative=relative):
                temp, root = self.make_root(skill_body=body, agents_body=body)
                self.addCleanup(temp.cleanup)
                (root / "PROMPT.md").write_text(body)
                path = root / relative
                path.write_text(
                    path.read_text().replace(
                        "does not reserve a new CONTST.",
                        "does not reserve a new CONTST. This entrypoint alone adds a route note.",
                    )
                )

                errors = validator.validate(root)

                self.assertIn(
                    f"{relative} ad-analysis routing section has drifted",
                    errors,
                )

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
            (
                "performance action",
                original + "\nCreative Audit recommendation: `keep`.\n",
                "examples/creative-audit.md assigns a performance action",
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
        self.assertFalse(validator.creative_audit_assigns_performance_action(example))
        self.assertFalse(validator.creative_audit_predicts_performance(example))
        self.assertIsNone(
            re.search(r"\b(?:keep|ITR|stop|scale)\b", example, re.IGNORECASE)
        )

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
            "CONTST: unreserved — human decision required",
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

    def test_diagnosis_persistence_distinguishes_attached_winner_negation(self):
        validator = load_validator()

        self.assertFalse(
            validator.contradicts_diagnosis_persistence(
                "Winner graduation does not proceed without a real Post ID and confirmation."
            )
        )
        self.assertTrue(
            validator.contradicts_diagnosis_persistence(
                "Winner graduation may proceed without a real Post ID or confirmation."
            )
        )
        self.assertTrue(
            validator.contradicts_diagnosis_persistence(
                "Winner graduation may proceed without a real Post ID and does not proceed without confirmation."
            )
        )
        self.assertTrue(
            validator.contradicts_diagnosis_persistence(
                "Winner graduation does not proceed without a real Post ID, but winner graduation may proceed without confirmation."
            )
        )

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

    def test_validator_rejects_v04_analysis_policy_mutations(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        for relative in (
            "contracts/creative-audit.md",
            "contracts/ad-diagnosis.md",
            "references/19-ad-analysis-harness.md",
            "scripts/ad_analysis_harness.py",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# harness\n" if path.suffix == ".py" else "Governed analysis policy.\n"
            )

        mutations = (
            (
                "contracts/ad-diagnosis.md",
                "",
                "contracts/ad-diagnosis.md must allow only keep, ITR, stop or scale",
            ),
            (
                "contracts/creative-audit.md",
                "Creative Audit predicts winning performance.\n",
                "contracts/creative-audit.md predicts winning performance",
            ),
            (
                "contracts/ad-diagnosis.md",
                "Performance data is optional for a keep, ITR, stop or scale decision.\n",
                "contracts/ad-diagnosis.md permits performance decisions without performance data",
            ),
            (
                "references/19-ad-analysis-harness.md",
                "Diagnosis automatically reserves the next CONTST.\n",
                "references/19-ad-analysis-harness.md automatically reserves a CONTST",
            ),
            (
                "references/19-ad-analysis-harness.md",
                "Diagnosis automatically increments next_test_number.\n",
                "references/19-ad-analysis-harness.md automatically reserves a CONTST",
            ),
            (
                "contracts/ad-diagnosis.md",
                "A diagnosis may reserve a new CONTST for a recommended ITR.\n",
                "contracts/ad-diagnosis.md contradicts diagnosis persistence boundaries",
            ),
            (
                "references/19-ad-analysis-harness.md",
                "A proposed test observation automatically becomes approved revision learning.\n",
                "references/19-ad-analysis-harness.md contradicts diagnosis persistence boundaries",
            ),
            (
                "references/19-ad-analysis-harness.md",
                "Winner graduation may proceed without a real Post ID or human confirmation.\n",
                "references/19-ad-analysis-harness.md contradicts diagnosis persistence boundaries",
            ),
            (
                "references/19-ad-analysis-harness.md",
                "Upload-only output persists controlled records.\n",
                "references/19-ad-analysis-harness.md contradicts diagnosis persistence boundaries",
            ),
            (
                "contracts/creative-audit.md",
                "Creative Audit recommendation: `keep`.\n",
                "contracts/creative-audit.md assigns a performance action",
            ),
            (
                "contracts/creative-audit.md",
                "Outcome: `scale`.\n",
                "contracts/creative-audit.md assigns a performance action",
            ),
            (
                "examples/creative-audit.md",
                "These ads will win, convert, lower CAC and scale profitably.\n",
                "examples/creative-audit.md predicts performance",
            ),
            (
                "examples/creative-audit.md",
                "This ad will win without revisions.\n",
                "examples/creative-audit.md predicts performance",
            ),
            (
                "examples/creative-audit.md",
                "This ad should win.\n",
                "examples/creative-audit.md predicts performance",
            ),
            (
                "examples/creative-audit.md",
                "This ad is likely a winner.\n",
                "examples/creative-audit.md predicts performance",
            ),
            (
                "examples/creative-audit.md",
                "This ad will outperform the others.\n",
                "examples/creative-audit.md predicts performance",
            ),
            (
                "PROMPT.md",
                "Creative Audit may assign `keep`, `ITR`, `stop` or `scale`.\n",
                "PROMPT.md permits Creative Audit performance actions",
            ),
            (
                "PROMPT.md",
                "Creative Audit may assign `keep` without performance data.\n",
                "PROMPT.md permits Creative Audit performance actions",
            ),
            (
                "PROMPT.md",
                "Creative Audit cannot inspect the attachment and may assign keep.\n",
                "PROMPT.md permits Creative Audit performance actions",
            ),
            (
                "PROMPT.md",
                "Creative Audit must not invent evidence and may assign scale.\n",
                "PROMPT.md permits Creative Audit performance actions",
            ),
            (
                "examples/creative-audit.md",
                "Creative Audit will not review the destination and will win.\n",
                "examples/creative-audit.md predicts performance",
            ),
            (
                "contracts/ad-diagnosis.md",
                "`Top-level action` contains exactly one literal value: `keep`, `ITR`, `stop`, `scale` or `pause`.\n",
                "contracts/ad-diagnosis.md must allow only keep, ITR, stop or scale",
            ),
            (
                "scripts/ad_analysis_harness.py",
                "import requests\n",
                "scripts/ad_analysis_harness.py imports a non-standard or network dependency: requests",
            ),
            (
                "scripts/ad_analysis_harness.py",
                "import socket\n",
                "scripts/ad_analysis_harness.py imports a non-standard or network dependency: socket",
            ),
        )
        for relative, addition, expected_error in mutations:
            with self.subTest(relative=relative):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                prefix = "# harness\n" if path.suffix == ".py" else "Governed analysis policy.\n"
                path.write_text(prefix + addition)

                errors = validator.validate(root)

                self.assertIn(expected_error, errors)

                path.write_text(
                    "# harness\n" if path.suffix == ".py" else "Governed analysis policy.\n"
                )

    def test_validator_accepts_explicit_creative_audit_prohibitions(self):
        validator = load_validator()
        cases = (
            (
                "contracts/creative-audit.md",
                "Creative Audit makes no prediction that an ad will win.\n",
                "contracts/creative-audit.md predicts winning performance",
            ),
            (
                "PROMPT.md",
                "Creative Audit assigns no keep action.\n",
                "PROMPT.md permits Creative Audit performance actions",
            ),
        )

        for relative, addition, prohibited_error in cases:
            with self.subTest(relative=relative):
                temp, root = self.make_root()
                self.addCleanup(temp.cleanup)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Governed analysis policy.\n" + addition)

                errors = validator.validate(root)

                self.assertNotIn(prohibited_error, errors)

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

    def test_package_declares_v04_and_portable_brand_folder(self):
        self.assertEqual("0.4.0", (ROOT / "VERSION").read_text().strip())
        readme = (ROOT / "README.md").read_text()

        self.assertIn("brand folder", readme.lower())
        self.assertIn("Firecrawl", readme)
        self.assertIn("Grok Agents", readme)

    def test_v04_public_release_documents_complete_ad_analysis_workflow(self):
        readme = (ROOT / "README.md").read_text()
        normalized = " ".join(readme.split()).lower()

        self.assertIn("**Version:** 0.4.0", readme)
        self.assertIn("twelve governed artefacts", readme)
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
        self.assertIn("<!-- source: schemas/ad-analysis-intake.schema.json -->", content)
        self.assertIn(
            "<!-- source: schemas/ad-analysis-intake.conformance.json -->", content
        )
        self.assertIn('"performance-diagnosis"', content)
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

    def test_reports_positive_most_aware_standard_ad_prose_in_active_instructions(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        reference = root / "references" / "06-concept-model.md"
        reference.parent.mkdir()
        reference.write_text(
            "Every initial test must include a Most Aware standard ad for the offer.\n"
        )

        errors = validator.validate(root)

        self.assertIn(
            "references/06-concept-model.md prescribes a Most Aware standard ad",
            errors,
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

    def test_reports_legacy_platform_observations_recast_as_active_policy(self):
        validator = load_validator()
        cases = (
            ("Default duration 7 days.\n", "legacy seven-day test default"),
            (
                "The current standard shape is 10 concepts x 5 to 10 hook variations; the hook is the actual test variable.\n",
                "legacy volume-first hook test standard",
            ),
        )

        for content, error_suffix in cases:
            with self.subTest(error=error_suffix):
                temp, root = self.make_root()
                self.addCleanup(temp.cleanup)
                reference = root / "references" / "12-meta-platform.md"
                reference.parent.mkdir()
                reference.write_text(content)

                errors = validator.validate(root)

                self.assertIn(
                    f"references/12-meta-platform.md contains {error_suffix}", errors
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

    def test_reports_overlapping_read_validity_policy(self):
        validator = load_validator()
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        reference = root / "references" / "09-testing-and-diagnosis.md"
        reference.parent.mkdir()
        reference.write_text(
            "## Read validity\n\n"
            "| Validity | Rule |\n|---|---|\n"
            "| Verdict | Meets spend and purchase thresholds |\n"
            "| Direction | Misses a threshold |\n"
            "| Too early | Misses spend or purchase thresholds |\n"
        )

        errors = validator.validate(root)

        self.assertIn(
            "references/09-testing-and-diagnosis.md must define ordered non-overlapping read validity",
            errors,
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

    def test_package_contst_lexeme_accepts_only_ascii_digits(self):
        validator = load_validator()

        self.assertIsNotNone(
            validator.CONTST_TEST_ID.search("  - test_id: CONTST001")
        )
        self.assertIsNone(
            validator.CONTST_TEST_ID.search("  - test_id: CONTST٠٠١")
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

        self.assertIn("VERSION must declare 0.4.0", errors)


if __name__ == "__main__":
    unittest.main()
