import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "record-learning.py"


def load_recorder():
    if not SCRIPT.exists():
        raise AssertionError("scripts/record-learning.py should exist")
    spec = importlib.util.spec_from_file_location("record_learning", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_event(**overrides):
    event = {
        "brand_slug": "acme-sleep",
        "market": "AU",
        "product_id": "pillow-01",
        "source_asset_id": "ACME001_PRA_VID",
        "before": "This pillow fixes every sleep problem.",
        "after": "A supportive pillow built for side sleepers.",
        "reason": "The original outran the approved claim ceiling.",
        "scope": "brand",
        "classification": "compliance_correction",
        "status": "approved",
        "confidence": 1.0,
        "author": "Joe",
        "timestamp": "2026-08-26T10:00:00+10:00",
    }
    event.update(overrides)
    return event


class LearningRecorderTests(unittest.TestCase):
    def make_brand_folder(self, slug="acme-sleep"):
        temp = tempfile.TemporaryDirectory()
        folder = pathlib.Path(temp.name) / slug
        (folder / "learning").mkdir(parents=True)
        (folder / "brand.yml").write_text(
            f'schema_version: 2\nbrand:\n  name: "Acme Sleep"\n  slug: "{slug}"\n'
        )
        (folder / "learning" / "learning-events.jsonl").touch()
        return temp, folder

    def test_appends_a_valid_learning_event(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        event_id = recorder.append_event(folder, valid_event())

        lines = (folder / "learning" / "learning-events.jsonl").read_text().splitlines()
        self.assertEqual(1, len(lines))
        stored = json.loads(lines[0])
        self.assertEqual(event_id, stored["event_id"])
        self.assertTrue(event_id.startswith("LEARN-"))
        self.assertEqual("approved", stored["status"])

    def test_reports_missing_required_fields(self):
        recorder = load_recorder()
        event = valid_event()
        event.pop("reason")

        errors = recorder.validate_event(event)

        self.assertIn("missing required field: reason", errors)

    def test_refuses_cross_brand_learning(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        with self.assertRaisesRegex(ValueError, "does not match connected brand"):
            recorder.append_event(folder, valid_event(brand_slug="other-brand"))

    def test_storage_is_append_only(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        first_id = recorder.append_event(folder, valid_event())
        second_id = recorder.append_event(
            folder,
            valid_event(
                source_asset_id="ACME002_PDA_IMG",
                before="Old headline",
                after="Approved headline",
                classification="voice_rule",
            ),
        )

        stored = [
            json.loads(line)
            for line in (folder / "learning" / "learning-events.jsonl")
            .read_text()
            .splitlines()
        ]
        self.assertEqual([first_id, second_id], [row["event_id"] for row in stored])


if __name__ == "__main__":
    unittest.main()
