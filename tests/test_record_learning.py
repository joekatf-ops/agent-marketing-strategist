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
        "learning": "Never use a guaranteed product outcome without approved evidence.",
        "memory_key": "claims.guaranteed_outcomes",
        "scope": "brand",
        "classification": "compliance_correction",
        "status": "approved",
        "confidence": 1.0,
        "author": "Joe",
        "approved_by": "Joe",
        "timestamp": "2026-08-26T10:00:00+10:00",
    }
    event.update(overrides)
    return event


class LearningRecorderTests(unittest.TestCase):
    def make_brand_folder(self, slug="acme-sleep", approvers=("Joe",)):
        temp = tempfile.TemporaryDirectory()
        folder = pathlib.Path(temp.name) / slug
        (folder / "learning").mkdir(parents=True)
        quoted_approvers = ", ".join(f'"{name}"' for name in approvers)
        (folder / "brand.yml").write_text(
            f'schema_version: 2\nbrand:\n  name: "Acme Sleep"\n  slug: "{slug}"\n'
            f'approvals:\n  rule_approvers: [{quoted_approvers}]\n'
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
        memory = json.loads((folder / "learning" / "active-memory.json").read_text())
        self.assertEqual(1, memory["learning_version"])
        self.assertEqual(event_id, memory["active_rules"][0]["event_id"])
        self.assertEqual(
            "Never use a guaranteed product outcome without approved evidence.",
            memory["active_rules"][0]["rule"],
        )

    def test_reports_missing_required_fields(self):
        recorder = load_recorder()
        event = valid_event()
        event.pop("reason")

        errors = recorder.validate_event(event)

        self.assertIn("missing required field: reason", errors)

    def test_rejects_values_that_do_not_match_the_schema(self):
        recorder = load_recorder()
        event = valid_event(
            event_id="bad-id",
            brand_slug="Bad Brand",
            market="A",
            product_id="",
            reason="",
            learning="",
            author="",
            timestamp="2026-08-26",
            classification=[],
            status={},
            scope=1,
            memory_key="",
        )

        errors = recorder.validate_event(event)

        self.assertIn("event_id must match LEARN-[A-Z0-9]+", errors)
        self.assertIn("brand_slug must be lowercase hyphenated text", errors)
        self.assertIn("market must contain at least 2 characters", errors)
        self.assertIn("product_id must not be empty", errors)
        self.assertIn("reason must not be empty", errors)
        self.assertIn("learning must not be empty", errors)
        self.assertIn("author must not be empty", errors)
        self.assertIn("timestamp must be an ISO 8601 date-time", errors)
        self.assertIn("invalid classification: []", errors)
        self.assertIn("invalid status: {}", errors)
        self.assertIn("invalid scope: 1", errors)
        self.assertIn("memory_key must use lowercase dot, underscore or hyphen tokens", errors)

        approved_bad_classification = recorder.validate_event(
            valid_event(classification=[])
        )
        self.assertIn("invalid classification: []", approved_bad_classification)

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

    def test_refuses_a_duplicate_event_id(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        event = valid_event(event_id="LEARN-FIXED1")

        recorder.append_event(folder, event)

        with self.assertRaisesRegex(ValueError, "event_id already exists"):
            recorder.append_event(folder, event)

    def test_requires_a_known_superseded_event(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        with self.assertRaisesRegex(ValueError, "supersedes event does not exist"):
            recorder.append_event(
                folder,
                valid_event(supersedes="LEARN-UNKNOWN1"),
            )

        first_id = recorder.append_event(folder, valid_event(event_id="LEARN-BASE1"))
        with self.assertRaisesRegex(ValueError, "same memory_key"):
            recorder.append_event(
                folder,
                valid_event(
                    event_id="LEARN-WRONGKEY1",
                    source_asset_id="ACME002_PRA_VID",
                    memory_key="voice.hype",
                    supersedes=first_id,
                ),
            )

    def test_refuses_unconfigured_or_unauthorized_approvers(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder(approvers=())
        self.addCleanup(temp.cleanup)

        with self.assertRaisesRegex(ValueError, "no rule approvers configured"):
            recorder.append_event(folder, valid_event())

        temp_allowed, allowed_folder = self.make_brand_folder(approvers=("Alice",))
        self.addCleanup(temp_allowed.cleanup)
        with self.assertRaisesRegex(ValueError, "approved_by is not a configured rule approver"):
            recorder.append_event(allowed_folder, valid_event(approved_by="Joe"))

    def test_refuses_unauthorized_historical_approved_events(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder(approvers=("Joe",))
        self.addCleanup(temp.cleanup)
        event = valid_event(event_id="LEARN-MALLORY1", approved_by="Mallory")
        (folder / "learning" / "learning-events.jsonl").write_text(
            json.dumps(event) + "\n"
        )

        with self.assertRaisesRegex(
            ValueError, "approved_by is not a configured rule approver"
        ):
            recorder.rebuild_active_memory(folder)

    def test_rejects_noncanonical_memory_keys(self):
        recorder = load_recorder()

        errors = recorder.validate_event(valid_event(memory_key="claims:loss prevention"))

        self.assertIn(
            "memory_key must use lowercase dot, underscore or hyphen tokens", errors
        )

    def test_surfaces_conflicting_active_rules_by_memory_key(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        first_id = recorder.append_event(folder, valid_event(event_id="LEARN-RULE1"))
        recorder.append_event(
            folder,
            valid_event(
                event_id="LEARN-RULE2",
                source_asset_id="ACME002_PRA_VID",
                learning="Guaranteed outcomes are allowed in headlines.",
            ),
        )
        memory = json.loads((folder / "learning" / "active-memory.json").read_text())
        self.assertEqual(1, len(memory["unresolved_conflicts"]))

        recorder.append_event(
            folder,
            valid_event(
                event_id="LEARN-RULE3",
                source_asset_id="ACME003_PRA_VID",
                learning="Never promise guaranteed outcomes without approved evidence.",
                supersedes=first_id,
            ),
        )
        memory = json.loads((folder / "learning" / "active-memory.json").read_text())
        self.assertNotIn(first_id, [rule["event_id"] for rule in memory["active_rules"]])

    def test_frozen_learning_patch_contains_valid_event_objects(self):
        recorder = load_recorder()
        example = (ROOT / "examples" / "learning-update.md").read_text()
        objects = [
            json.loads(section.split("```", 1)[0])
            for section in example.split("```json\n")[1:]
        ]

        self.assertEqual(3, len(objects))
        for event in objects:
            self.assertEqual([], recorder.validate_event(event))

    def test_preference_needs_three_distinct_approved_signals(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        for number in range(1, 4):
            recorder.append_event(
                folder,
                valid_event(
                    source_asset_id=f"ACME00{number}_PRA_VID",
                    before=f"Hype line {number}",
                    after="Use the quieter approved voice.",
                    reason="Joe removed hype from the approved version.",
                    learning="Prefer quieter approved language over hype.",
                    scope="brand",
                    classification="preference",
                    status="approved",
                ),
            )
            memory = json.loads(
                (folder / "learning" / "active-memory.json").read_text()
            )
            self.assertEqual([], memory["active_rules"])
            expected_candidates = 1 if number == 3 else 0
            self.assertEqual(expected_candidates, len(memory["preference_candidates"]))

        candidate = memory["preference_candidates"][0]
        self.assertEqual(3, candidate["signal_count"])
        self.assertEqual("proposed", candidate["status"])

    def test_proposed_and_accidental_events_do_not_become_active(self):
        recorder = load_recorder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)

        recorder.append_event(folder, valid_event(status="proposed"))
        recorder.append_event(
            folder,
            valid_event(
                event_id="LEARN-ACCIDENTAL1",
                source_asset_id="ACME002_PRA_VID",
                classification="accidental_edit",
                status="approved",
            ),
        )

        memory = json.loads((folder / "learning" / "active-memory.json").read_text())
        self.assertEqual([], memory["active_rules"])
        self.assertEqual([], memory["approved_insights"])


if __name__ == "__main__":
    unittest.main()
