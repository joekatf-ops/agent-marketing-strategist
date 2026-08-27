import ast
import datetime as dt
import importlib.util
import json
import pathlib
import sysconfig
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "ad_analysis_harness.py"
INITIALIZER = ROOT / "scripts" / "init-brand-folder.py"
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
        run = self.create_run(harness)
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
        run = self.create_run(harness, mode="performance-diagnosis")
        self.write_intake(run, self.complete_performance_intake(harness, run))

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)

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

    def test_renders_a_deterministic_input_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = harness.load_intake(run)

        first = harness.render_input_audit(intake, harness.validate_run(self.brand, run))
        second = harness.render_input_audit(intake, harness.validate_run(self.brand, run))

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("# Ad analysis input audit\n"))


if __name__ == "__main__":
    unittest.main()
