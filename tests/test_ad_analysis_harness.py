import datetime as dt
import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "ad_analysis_harness.py"
INITIALIZER = ROOT / "scripts" / "init-brand-folder.py"


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


class AdAnalysisHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.brand = pathlib.Path(self.temp.name) / "acme-sleep"
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

    def test_initialises_a_brand_scoped_analysis_run(self):
        harness = load_harness()

        run = self.create_run(harness)

        self.assertEqual("ADR-20260827-001", run.name)
        intake = json.loads((run / "intake.json").read_text())
        self.assertEqual("acme-sleep", intake["brand_slug"])
        self.assertEqual("creative-audit", intake["mode"])

    def test_refuses_to_overwrite_an_existing_analysis_run(self):
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

    def test_sequences_run_identifiers_for_the_same_day(self):
        harness = load_harness()
        self.create_run(harness)

        second = self.create_run(harness)

        self.assertEqual("ADR-20260827-002", second.name)

    def test_marks_complete_creative_inputs_ready(self):
        harness = load_harness()
        run = self.create_run(harness)
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
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)

    def test_blocks_incomplete_performance_inputs(self):
        harness = load_harness()
        run = self.create_run(harness, mode="performance-diagnosis")

        result = harness.validate_run(self.brand, run)

        self.assertEqual("blocked", result.status)
        self.assertIn("performance sources are required", result.errors)

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
        target = pathlib.Path(self.temp.name) / "ad-one.mp4"
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
