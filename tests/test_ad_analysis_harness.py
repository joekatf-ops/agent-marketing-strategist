import ast
import datetime as dt
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import sysconfig
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "ad_analysis_harness.py"
INITIALIZER = ROOT / "scripts" / "init-brand-folder.py"
VALIDATOR = ROOT / "scripts" / "validate-ad-analysis-run.py"
CONTROLLED_RECORDS = (
    "strategy/test-register.yml",
    "strategy/winner-library.yml",
    "learning/approved-rules.yml",
)
PUBLIC_HARNESS_API = {
    "load_brand_identity",
    "initialise_run",
    "load_intake",
    "ValidationResult",
    "validate_run",
    "render_input_audit",
}


def load_harness():
    if not MODULE.exists():
        raise AssertionError("scripts/ad_analysis_harness.py should exist")
    spec = importlib.util.spec_from_file_location("ad_analysis_harness", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_initializer():
    spec = importlib.util.spec_from_file_location("init_brand_folder", INITIALIZER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_validator(harness):
    spec = importlib.util.spec_from_file_location("validate_ad_analysis_run", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, {"ad_analysis_harness": harness}):
        spec.loader.exec_module(module)
    return module


def is_standard_library_module(name):
    spec = importlib.util.find_spec(name)
    if spec is None:
        return False
    if spec.origin in {"built-in", "frozen"}:
        return True
    try:
        origin = pathlib.Path(spec.origin).resolve()
        origin.relative_to(
            pathlib.Path(sysconfig.get_paths()["stdlib"]).resolve()
        )
    except ValueError:
        return False
    return "site-packages" not in origin.parts


class AdAnalysisHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.temp_root = pathlib.Path(self.temp.name).resolve()
        self.brand = self.temp_root / "acme-sleep"
        load_initializer().initialise(self.brand, "Acme Sleep", "acme-sleep")

    def create_run(self, harness, mode="creative-audit"):
        return harness.initialise_run(
            brand_folder=self.brand,
            mode=mode,
            product_id="sleep-mask",
            market="AU",
            today=dt.date(2026, 8, 27),
        )

    def create_modern_run(self, harness, mode="creative-audit"):
        manifest = self.brand / "brand.yml"
        manifest.write_text(
            manifest.read_text().replace(
                'method_version: "0.3.0"', 'method_version: "0.4.0"'
            )
        )
        return self.create_run(harness, mode)

    def write_intake(self, run, intake):
        (run / "intake.json").write_text(json.dumps(intake, indent=2) + "\n")

    def complete_creative_intake(self, harness, run):
        intake = harness.load_intake(run)
        intake.update(
            {
                "sources": [
                    {
                        "source_id": "SRC-001",
                        "kind": "attachment",
                        "label": "ad-one.mp4",
                        "location": "attached:ad-one.mp4",
                        "sha256": None,
                    }
                ],
                "ads": [
                    {
                        "ad_id": "AD-001",
                        "asset_source_ids": ["SRC-001"],
                        "primary_text": "Sleep through the night.",
                        "headline": "Wake up rested",
                        "description": "",
                        "cta": "Shop now",
                        "destination_url": "https://example.test/sleep-mask",
                        "destination_type": "PDP",
                        "coordinate_key": "travellers|light",
                    }
                ],
            }
        )
        return intake

    def complete_performance_intake(self, harness, run):
        intake = self.complete_creative_intake(harness, run)
        intake["sources"].append(
            {
                "source_id": "SRC-002",
                "kind": "table",
                "label": "Meta ad export, 20-26 August",
                "location": "attached:meta-export.csv",
                "sha256": None,
            }
        )
        intake["performance"] = {
            "source_ids": ["SRC-002"],
            "date_range": {"start": "2026-08-20", "end": "2026-08-26"},
            "attribution": "7-day click",
            "currency": "AUD",
            "aggregation_level": "ad",
            "field_mapping": {
                "ad_id": "Ad name",
                "spend": "Amount spent (AUD)",
                "purchases": "Purchases",
                "landing_page_views": "Landing page views",
                "video_3_second_plays": "3-second video plays",
            },
            "ad_mapping": {"Acme Sleep Mask AU": "AD-001"},
            "logged_interventions": [],
        }
        return intake

    def test_initialises_sequential_run(self):
        harness = load_harness()

        run = self.create_run(harness)
        second = self.create_run(harness)

        self.assertEqual("ADR-20260827-001", run.name)
        intake = json.loads((run / "intake.json").read_text())
        self.assertEqual("acme-sleep", intake["brand_slug"])
        self.assertEqual("creative-audit", intake["mode"])
        self.assertEqual("sleep-mask", intake["product_id"])
        self.assertEqual("AU", intake["market"])
        self.assertEqual({"README.md", "intake.json"}, {path.name for path in run.iterdir()})
        self.assertEqual("ADR-20260827-002", second.name)

    def test_uses_the_current_brand_method_version_in_the_exact_skeleton(self):
        harness = load_harness()
        manifest = self.brand / "brand.yml"
        manifest.write_text(manifest.read_text().replace('method_version: "0.3.0"', 'method_version: "0.4.0"'))

        run = self.create_run(harness)

        self.assertEqual(
            {
                "schema_version": 1,
                "run_id": "ADR-20260827-001",
                "mode": "creative-audit",
                "brand_slug": "acme-sleep",
                "method_version": "0.4.0",
                "market": "AU",
                "product_id": "sleep-mask",
                "account_timezone": "",
                "requester": "",
                "requested_at": "2026-08-27",
                "ads": [],
                "sources": [],
                "performance": None,
                "known_limitations": [],
            },
            json.loads((run / "intake.json").read_text()),
        )

    def test_preserves_legacy_brand_version_and_records_migration_need(self):
        harness = load_harness()

        run = self.create_run(harness)

        intake = harness.load_intake(run)
        self.assertEqual("0.3.0", intake["method_version"])
        self.assertEqual(
            [
                "Brand method version 0.3.0 requires reviewed migration before controlled persistence."
            ],
            intake["known_limitations"],
        )

    def test_refuses_a_brand_folder_below_a_symlinked_parent(self):
        harness = load_harness()
        real_parent = self.temp_root / "real-brands"
        real_brand = real_parent / "acme-sleep"
        real_parent.mkdir()
        load_initializer().initialise(real_brand, "Acme Sleep", "acme-sleep")
        alias = self.temp_root / "brand-alias"
        alias.symlink_to(real_parent, target_is_directory=True)
        supplied_brand = alias / "acme-sleep"

        with self.assertRaisesRegex(ValueError, "symlink"):
            harness.initialise_run(
                brand_folder=supplied_brand,
                mode="creative-audit",
                product_id="sleep-mask",
                market="AU",
                today=dt.date(2026, 8, 27),
            )

        self.assertFalse(
            (real_brand / "outputs/ad-analysis/ADR-20260827-001").exists()
        )

    def test_requires_exactly_one_non_empty_product_and_market(self):
        harness = load_harness()
        cases = (("", "AU"), ("sleep-mask", ""))

        for product_id, market in cases:
            with self.subTest(product_id=product_id, market=market):
                with self.assertRaises(ValueError):
                    harness.initialise_run(
                        brand_folder=self.brand,
                        mode="creative-audit",
                        product_id=product_id,
                        market=market,
                    )

        run = self.create_run(harness)
        intake = harness.load_intake(run)
        intake["product_id"] = ["sleep-mask", "travel-mask"]
        intake["market"] = ["AU", "NZ"]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("blocked", result.status)
        self.assertTrue(any("product_id" in error for error in result.errors))
        self.assertTrue(any("market" in error for error in result.errors))

    def test_refuses_existing_or_invalid_run(self):
        harness = load_harness()
        run = self.create_run(harness)

        with self.assertRaises(FileExistsError):
            harness.initialise_run(
                brand_folder=self.brand,
                mode="creative-audit",
                product_id="sleep-mask",
                market="AU",
                run_id=run.name,
            )

        for kwargs in (
            {"mode": "unsupported"},
            {"run_id": "not-an-analysis-run"},
            {"run_id": "ADR-20261327-001"},
        ):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    parameters = {
                        "brand_folder": self.brand,
                        "mode": "creative-audit",
                        "product_id": "sleep-mask",
                        "market": "AU",
                    }
                    parameters.update(kwargs)
                    harness.initialise_run(**parameters)

        explicit = harness.initialise_run(
            brand_folder=self.brand,
            mode="creative-audit",
            product_id="sleep-mask",
            market="AU",
            run_id="ADR-20260827-003",
        )
        self.assertEqual("ADR-20260827-003", explicit.name)

    def test_marks_complete_creative_inputs_ready(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)

    def test_blocks_incomplete_performance_inputs(self):
        harness = load_harness()
        run = self.create_run(harness, mode="performance-diagnosis")

        result = harness.validate_run(self.brand, run)

        self.assertEqual("blocked", result.status)
        self.assertIn("performance sources are required", result.errors)

    def test_marks_complete_performance_inputs_ready(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        self.write_intake(run, self.complete_performance_intake(harness, run))

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)

    def test_validation_result_is_immutable_and_uses_sorted_tuples(self):
        harness = load_harness()
        run = self.create_run(harness)

        result = harness.validate_run(self.brand, run)

        self.assertIsInstance(result, harness.ValidationResult)
        self.assertIsInstance(result.errors, tuple)
        self.assertIsInstance(result.limitations, tuple)
        self.assertIsInstance(result.inventory, tuple)
        self.assertEqual(tuple(sorted(result.errors)), result.errors)
        self.assertEqual(tuple(sorted(result.limitations)), result.limitations)
        with self.assertRaises((AttributeError, TypeError)):
            result.status = "ready"

    def test_blocks_creative_audit_without_ads_or_ad_identity_and_assets(self):
        harness = load_harness()
        run = self.create_run(harness)

        empty_result = harness.validate_run(self.brand, run)
        self.assertEqual("blocked", empty_result.status)
        self.assertIn("ads must contain at least one ad", empty_result.errors)

        intake = harness.load_intake(run)
        intake["ads"] = [{"ad_id": "", "asset_source_ids": []}]
        self.write_intake(run, intake)
        incomplete_result = harness.validate_run(self.brand, run)

        self.assertEqual("blocked", incomplete_result.status)
        self.assertIn("ads[0].ad_id must be non-empty text", incomplete_result.errors)
        self.assertIn(
            "ads[0].asset_source_ids must contain at least one source ID",
            incomplete_result.errors,
        )

    def test_limits_creative_audit_when_copy_destination_or_traceability_is_missing(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = harness.load_intake(run)
        intake["sources"] = [
            {
                "source_id": "SRC-001",
                "kind": "attachment",
                "label": "ad-one.mp4",
                "location": "attached:ad-one.mp4",
                "sha256": None,
            }
        ]
        intake["ads"] = [{"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]}]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn("ads[0] copy is unavailable", result.limitations)
        self.assertIn("ads[0] destination is unavailable", result.limitations)
        self.assertIn("ads[0] strategic traceability is unavailable", result.limitations)

    def test_known_migration_need_limits_but_does_not_block_analysis(self):
        harness = load_harness()
        run = self.create_run(harness)
        self.write_intake(run, self.complete_creative_intake(harness, run))

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn(
            "Brand method version 0.3.0 requires reviewed migration before controlled persistence.",
            result.limitations,
        )

    def test_validator_derives_migration_need_from_the_brand_version(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["known_limitations"] = []
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn(
            "Brand method version 0.3.0 requires reviewed migration before controlled persistence.",
            result.limitations,
        )

    def test_performance_required_fields_each_block_diagnosis(self):
        harness = load_harness()
        required_cases = (
            ("source_ids", "performance sources are required"),
            ("date_range", "performance.date_range is required"),
            ("attribution", "performance.attribution is required"),
            ("currency", "performance.currency is required"),
            ("aggregation_level", "performance.aggregation_level is required"),
            ("field_mapping.ad_id", "performance.field_mapping.ad_id is required"),
            ("field_mapping.spend", "performance.field_mapping.spend is required"),
            ("field_mapping.purchases", "performance.field_mapping.purchases is required"),
            (
                "ad_mapping",
                "performance.ad_mapping must contain at least one spend-bearing source ad",
            ),
        )

        for field, expected in required_cases:
            with self.subTest(field=field):
                run = self.create_modern_run(harness, mode="performance-diagnosis")
                intake = self.complete_performance_intake(harness, run)
                if field.startswith("field_mapping."):
                    del intake["performance"]["field_mapping"][field.rsplit(".", 1)[1]]
                elif field == "ad_mapping":
                    intake["performance"][field] = {}
                else:
                    del intake["performance"][field]
                self.write_intake(run, intake)

                result = harness.validate_run(self.brand, run)

                self.assertEqual("blocked", result.status)
                self.assertIn(expected, result.errors)

    def test_missing_optional_funnel_and_video_mappings_limit_diagnosis(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        intake = self.complete_performance_intake(harness, run)
        del intake["performance"]["field_mapping"]["landing_page_views"]
        del intake["performance"]["field_mapping"]["video_3_second_plays"]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn("optional funnel field mappings are unavailable", result.limitations)
        self.assertIn("optional video field mappings are unavailable", result.limitations)

    def test_performance_mapping_can_omit_an_unserved_intake_ad(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        intake = self.complete_performance_intake(harness, run)
        intake["ads"].append(
            {
                "ad_id": "AD-002",
                "asset_source_ids": ["SRC-001"],
                "primary_text": "Second ad",
                "headline": "Rest",
                "description": "",
                "cta": "Shop now",
                "destination_url": "https://example.test/sleep-mask",
                "destination_type": "PDP",
                "coordinate_key": "travellers|dark",
            }
        )
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)
        self.assertFalse(any("AD-002" in error for error in result.errors))

    def test_rejects_duplicate_source_and_ad_ids_and_unknown_references(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = harness.load_intake(run)
        source = {
            "source_id": "SRC-001",
            "kind": "attachment",
            "label": "ad-one.mp4",
            "location": "attached:ad-one.mp4",
            "sha256": None,
        }
        intake["sources"] = [source, dict(source)]
        intake["ads"] = [
            {"ad_id": "AD-001", "asset_source_ids": ["SRC-404"]},
            {"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]},
        ]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertIn("sources[1].source_id duplicates SRC-001", result.errors)
        self.assertIn("ads[1].ad_id duplicates AD-001", result.errors)
        self.assertIn(
            "ads[0].asset_source_ids references unknown source SRC-404", result.errors
        )

    def test_rejects_unknown_keys_at_each_structured_level(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        intake = self.complete_performance_intake(harness, run)
        intake["surprise"] = True
        intake["sources"][0]["surprise"] = True
        intake["ads"][0]["surprise"] = True
        intake["performance"]["surprise"] = True
        intake["performance"]["date_range"]["surprise"] = True
        intake["performance"]["field_mapping"]["surprise"] = True
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        for error in (
            "surprise is not allowed",
            "sources[0].surprise is not allowed",
            "ads[0].surprise is not allowed",
            "performance.surprise is not allowed",
            "performance.date_range.surprise is not allowed",
            "performance.field_mapping.surprise is not allowed",
        ):
            with self.subTest(error=error):
                self.assertIn(error, result.errors)

    def test_rejects_unknown_keys_in_optional_creative_mode_performance_metadata(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["performance"] = {
            "surprise": True,
            "source_ids": "SRC-002",
            "date_range": {"surprise": True},
            "field_mapping": {"surprise": True},
            "logged_interventions": "none",
        }
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertIn("performance.surprise is not allowed", result.errors)
        self.assertIn("performance.date_range.surprise is not allowed", result.errors)
        self.assertIn("performance.field_mapping.surprise is not allowed", result.errors)
        self.assertIn("performance.source_ids must be an array", result.errors)
        self.assertIn("performance.logged_interventions must be an array", result.errors)

    def test_rejects_local_file_traversal_absolute_paths_and_url_disguises(self):
        harness = load_harness()
        unsafe_locations = (
            ("../outside.mp4", "must not contain '..' traversal"),
            (str(self.temp_root / "outside.mp4"), "must be a relative path"),
            ("https://example.test/ad.mp4", "must not be a URL"),
        )

        for location, expected in unsafe_locations:
            with self.subTest(location=location):
                run = self.create_run(harness)
                intake = harness.load_intake(run)
                intake["sources"] = [
                    {
                        "source_id": "SRC-001",
                        "kind": "file",
                        "label": "ad-one.mp4",
                        "location": location,
                        "sha256": None,
                    }
                ]
                intake["ads"] = [
                    {"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]}
                ]
                self.write_intake(run, intake)

                result = harness.validate_run(self.brand, run)

                self.assertIn(f"sources[0].location {expected}", result.errors)

    def test_absolute_attachment_label_is_external_and_is_not_read(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0]["location"] = "/external/upload/ad-one.mp4"
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)
        self.assertFalse(any("location" in error for error in result.errors))

    def test_hashes_safe_local_files_without_mutating_intake(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        (run / "ad-one.mp4").write_bytes(b"trusted only as bytes")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)
        before = (run / "intake.json").read_bytes()

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)
        self.assertEqual(before, (run / "intake.json").read_bytes())
        self.assertEqual(
            (
                (
                    "SRC-001",
                    "file",
                    "ad-one.mp4",
                    "ad-one.mp4",
                    "1d61ea2522ceb2b08423452be93795e189b4c2f06cc8f3776eba4c1ff0069780",
                ),
            ),
            result.inventory,
        )

    def test_connected_and_upload_intakes_share_one_versioned_shape(self):
        harness = load_harness()
        connected_run = self.create_run(harness)
        connected = harness.load_intake(connected_run)
        upload_run = self.temp_root / "uploaded-analysis"
        upload_run.mkdir()
        self.write_intake(upload_run, connected)

        uploaded = harness.load_intake(upload_run)

        self.assertEqual(connected, uploaded)
        self.assertEqual(1, connected["schema_version"])
        self.assertEqual(
            {
                "schema_version",
                "run_id",
                "mode",
                "brand_slug",
                "method_version",
                "market",
                "product_id",
                "account_timezone",
                "requester",
                "requested_at",
                "ads",
                "sources",
                "performance",
                "known_limitations",
            },
            set(connected),
        )

    def test_harness_uses_only_standard_library_non_network_dependencies(self):
        load_harness()
        tree = ast.parse(MODULE.read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])

        for name in imported - {"__future__"}:
            with self.subTest(module=name):
                self.assertTrue(is_standard_library_module(name))
        self.assertFalse(
            imported
            & {
                "ftplib",
                "http",
                "imaplib",
                "nntplib",
                "poplib",
                "requests",
                "smtplib",
                "socket",
                "subprocess",
                "telnetlib",
                "urllib",
                "webbrowser",
                "xmlrpc",
            }
        )

    def test_initialisation_and_validation_do_not_write_controlled_records(self):
        harness = load_harness()
        before = {
            relative: (self.brand / relative).read_text()
            for relative in CONTROLLED_RECORDS
        }
        run = self.create_run(harness)

        harness.validate_run(self.brand, run)

        after = {
            relative: (self.brand / relative).read_text()
            for relative in CONTROLLED_RECORDS
        }
        self.assertEqual(before, after)

    def test_exposes_only_the_declared_non_mutating_public_api(self):
        harness = load_harness()
        exposed = {
            name
            for name, value in vars(harness).items()
            if callable(value)
            and getattr(value, "__module__", None) == harness.__name__
            and not name.startswith("_")
        }

        self.assertEqual(PUBLIC_HARNESS_API, exposed)

    def test_rejects_an_intake_for_a_different_brand(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = harness.load_intake(run)
        intake["brand_slug"] = "other-brand"
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertIn(
            "intake brand other-brand does not match manifest brand acme-sleep",
            result.errors,
        )

    def test_rejects_symlinked_local_sources(self):
        harness = load_harness()
        run = self.create_run(harness)
        target = self.temp_root / "ad-one.mp4"
        target.write_text("not an ad")
        (run / "linked-ad.mp4").symlink_to(target)
        intake = harness.load_intake(run)
        intake.update(
            {
                "sources": [
                    {
                        "source_id": "SRC-001",
                        "kind": "file",
                        "label": "linked-ad.mp4",
                        "location": "linked-ad.mp4",
                        "sha256": None,
                    }
                ],
                "ads": [{"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]}],
            }
        )
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertIn("sources[0].location must not be a symlink", result.errors)

    def test_rejects_non_string_values_instead_of_coercing_them(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["schema_version"] = "1"
        intake["market"] = 61
        intake["sources"][0]["kind"] = 1
        intake["ads"][0]["destination_type"] = 7
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        for error in (
            "schema_version must equal integer 1",
            "market must be non-empty text",
            "sources[0].kind must be one of: attachment, file, screenshot, table, url",
            "ads[0].destination_type must be text or null",
        ):
            with self.subTest(error=error):
                self.assertIn(error, result.errors)

    def test_rejects_list_and_object_source_kinds_without_raising(self):
        harness = load_harness()

        for kind in ([], {}):
            with self.subTest(kind=kind):
                run = self.create_run(harness)
                intake = harness.load_intake(run)
                intake["sources"] = [
                    {
                        "source_id": "SRC-001",
                        "kind": kind,
                        "label": "ad-one.mp4",
                        "location": "attached:ad-one.mp4",
                        "sha256": None,
                    }
                ]
                intake["ads"] = [
                    {"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]}
                ]
                self.write_intake(run, intake)

                try:
                    result = harness.validate_run(self.brand, run)
                except Exception as error:
                    self.fail(f"validate_run raised {type(error).__name__}: {error}")

                self.assertEqual("blocked", result.status)
                self.assertIn(
                    "sources[0].kind must be one of: attachment, file, screenshot, table, url",
                    result.errors,
                )

    def test_local_source_read_never_uses_a_swapped_parent_directory(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        asset_parent = run / "assets"
        asset_parent.mkdir()
        (asset_parent / "ad-one.mp4").write_bytes(b"inside")
        outside_parent = self.temp_root / "outside-assets"
        outside_parent.mkdir()
        (outside_parent / "ad-one.mp4").write_bytes(b"outside")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "assets/ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)
        checked_file = asset_parent / "ad-one.mp4"
        original_open = harness.os.open
        swapped = False

        def swap_parent_before_file_open(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal swapped
            is_path_open = dir_fd is None and pathlib.Path(path) == checked_file
            is_anchored_open = dir_fd is not None and path == "ad-one.mp4"
            if (is_path_open or is_anchored_open) and not swapped:
                swapped = True
                asset_parent.rename(run / "original-assets")
                asset_parent.symlink_to(outside_parent, target_is_directory=True)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with mock.patch.object(
            harness, "_no_follow_flag", return_value=os.O_NOFOLLOW
        ), mock.patch.object(
            harness.os, "open", side_effect=swap_parent_before_file_open
        ):
            result = harness.validate_run(self.brand, run)

        outside_digest = "31207a2065f46a5b948fce6fe5c13e85abaf5631e2f894b47dcd4fce14f6c57b"
        self.assertNotEqual(outside_digest, result.inventory[0][4])

    def test_local_source_validation_fails_closed_without_no_follow_support(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        (run / "ad-one.mp4").write_bytes(b"inside")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)

        with mock.patch.object(harness.os, "O_NOFOLLOW", None):
            try:
                result = harness.validate_run(self.brand, run)
            except Exception as error:
                self.fail(f"validate_run raised {type(error).__name__}: {error}")

        self.assertEqual("blocked", result.status)
        self.assertIn(
            "descriptor-anchored no-follow access is unavailable",
            result.errors,
        )

    def test_rejects_a_run_folder_outside_the_brand(self):
        harness = load_harness()
        canonical_run = self.create_run(harness)
        outside_run = self.temp_root / canonical_run.name
        outside_run.mkdir()
        self.write_intake(outside_run, harness.load_intake(canonical_run))

        result = harness.validate_run(self.brand, outside_run)

        self.assertEqual("blocked", result.status)
        self.assertIn("run folder must be inside the brand folder", result.errors)

    def test_renders_a_deterministic_input_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = harness.load_intake(run)

        first = harness.render_input_audit(intake, harness.validate_run(self.brand, run))
        second = harness.render_input_audit(intake, harness.validate_run(self.brand, run))

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("# Ad analysis input audit\n"))
        headings = (
            "## Run identity",
            "## Source inventory",
            "## Ad coverage",
            "## Performance coverage",
            "## Readiness",
            "## Errors",
            "## Limitations",
        )
        positions = [first.index(heading) for heading in headings]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Input readiness: `blocked`", first)

    def test_validator_cli_prints_issues_and_writes_only_the_input_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake_before = (run / "intake.json").read_bytes()
        controlled_before = {
            relative: (self.brand / relative).read_bytes()
            for relative in CONTROLLED_RECORDS
        }

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertIn("Input readiness: blocked", completed.stdout)
        self.assertIn("ads must contain at least one ad", completed.stdout)
        self.assertTrue((run / "input-audit.md").is_file())
        self.assertEqual(intake_before, (run / "intake.json").read_bytes())
        self.assertEqual(
            controlled_before,
            {
                relative: (self.brand / relative).read_bytes()
                for relative in CONTROLLED_RECORDS
            },
        )

    def test_validator_cli_audits_malformed_json_without_a_traceback(self):
        harness = load_harness()
        run = self.create_run(harness)
        (run / "intake.json").write_text("{not-json\n")

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertIn("Input readiness: blocked", completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertTrue((run / "input-audit.md").is_file())

    def test_validator_cli_refuses_a_symlinked_audit_target(self):
        harness = load_harness()
        run = self.create_run(harness)
        controlled = self.brand / CONTROLLED_RECORDS[0]
        before = controlled.read_bytes()
        (run / "input-audit.md").symlink_to(controlled)

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("input audit was not written", completed.stdout)
        self.assertEqual(before, controlled.read_bytes())

    def test_validator_cli_refuses_a_hardlinked_audit_target(self):
        harness = load_harness()
        run = self.create_run(harness)
        controlled = self.brand / CONTROLLED_RECORDS[0]
        before = controlled.read_bytes()
        os.link(controlled, run / "input-audit.md")

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("input audit was not written", completed.stdout)
        self.assertEqual(before, controlled.read_bytes())

    def test_validator_cli_writes_audits_only_to_canonical_run_folders(self):
        run = self.brand / "strategy"
        audit = run / "input-audit.md"

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("input audit was not written", completed.stdout)
        self.assertFalse(audit.exists())

    def test_audit_write_never_uses_a_swapped_parent_directory(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_run(harness)
        outside = self.temp_root / "outside-run"
        outside.mkdir()
        audit_path = run / "input-audit.md"
        original_open = validator.os.open
        swapped = False

        def swap_parent_before_audit_open(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal swapped
            is_path_open = dir_fd is None and pathlib.Path(path) == audit_path
            is_anchored_open = dir_fd is not None and path == "input-audit.md"
            if (is_path_open or is_anchored_open) and not swapped:
                swapped = True
                run.rename(run.parent / "original-run")
                run.symlink_to(outside, target_is_directory=True)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with mock.patch.object(
            harness, "_no_follow_flag", return_value=os.O_NOFOLLOW
        ), mock.patch.object(
            validator, "_no_follow_flag", return_value=os.O_NOFOLLOW
        ), mock.patch.object(
            validator.os, "open", side_effect=swap_parent_before_audit_open
        ):
            try:
                validator._write_input_audit(audit_path, "audit\n")
            except OSError:
                pass

        self.assertFalse((outside / "input-audit.md").exists())

    def test_audit_write_fails_closed_without_no_follow_support(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_run(harness)

        with mock.patch.object(validator.os, "O_NOFOLLOW", None):
            try:
                validator._write_input_audit(run / "input-audit.md", "audit\n")
            except OSError:
                pass
            except Exception as error:
                self.fail(f"audit write raised {type(error).__name__}: {error}")
            else:
                self.fail("audit write did not fail closed")


if __name__ == "__main__":
    unittest.main()
