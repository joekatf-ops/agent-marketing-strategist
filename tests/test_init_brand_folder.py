import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "init-brand-folder.py"


def load_initializer():
    if not SCRIPT.exists():
        raise AssertionError("scripts/init-brand-folder.py should exist")
    spec = importlib.util.spec_from_file_location("init_brand_folder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BrandFolderInitializerTests(unittest.TestCase):
    def test_creates_complete_portable_brand_folder(self):
        initializer = load_initializer()
        with tempfile.TemporaryDirectory() as temp:
            destination = pathlib.Path(temp) / "acme-sleep"

            result = initializer.initialise(destination, "Acme Sleep", "acme-sleep")

            self.assertEqual(destination, result)
            required = {
                "brand.yml",
                "README.md",
                "context/brand-core.md",
                "context/voice.md",
                "context/visual.md",
                "products/catalog.yml",
                "products/offers.yml",
                "products/economics.yml",
                "products/claims.yml",
                "products/proof-library.yml",
                "research/evidence-ledger/evidence.jsonl",
                "research/evidence-ledger/manifest.json",
                "research/customer-intelligence.md",
                "sources/website/crawl-state.json",
                "sources/website/README.md",
                "sources/customer/reviews/README.md",
                "sources/market/README.md",
                "strategy/concept-register.yml",
                "strategy/hypothesis-backlog.yml",
                "strategy/test-register.yml",
                "strategy/winner-library.yml",
                "outputs/README.md",
                "outputs/ad-analysis/README.md",
                "learning/learning-events.jsonl",
                "learning/active-memory.json",
                "learning/revisions/README.md",
                "learning/approved-rules.yml",
                "learning/preference-signals.yml",
                "learning/rejected-patterns.yml",
                "learning/decisions.md",
                "connectors/capabilities.yml",
            }
            actual = {
                str(path.relative_to(destination))
                for path in destination.rglob("*")
                if path.is_file()
            }
            self.assertTrue(required.issubset(actual), required - actual)

            analysis_instructions = (
                destination / "outputs/ad-analysis/README.md"
            ).read_text()
            self.assertIn("raw assets and exports may be placed or referenced", analysis_instructions)
            self.assertIn("excluded from generated brand bundles", analysis_instructions)

            crawl_state = (destination / "sources/website/crawl-state.json").read_text()
            self.assertIn('"brand_slug": "acme-sleep"', crawl_state)
            self.assertIn('"full_refresh_days": 7', crawl_state)
            evidence_manifest = (
                destination / "research/evidence-ledger/manifest.json"
            ).read_text()
            self.assertIn('"brand_slug": "acme-sleep"', evidence_manifest)
            self.assertIn('"evidence_version": 0', evidence_manifest)

    def test_substitutes_brand_identity_without_leaving_template_tokens(self):
        initializer = load_initializer()
        with tempfile.TemporaryDirectory() as temp:
            destination = pathlib.Path(temp) / "acme-sleep"

            initializer.initialise(destination, "Acme Sleep", "acme-sleep")

            manifest = (destination / "brand.yml").read_text()
            readme = (destination / "README.md").read_text()
            self.assertIn('name: "Acme Sleep"', manifest)
            self.assertIn('slug: "acme-sleep"', manifest)
            self.assertIn("# Acme Sleep brand folder", readme)
            self.assertNotIn("__BRAND_", manifest + readme)

    def test_initializes_current_v04_testing_memory(self):
        initializer = load_initializer()
        with tempfile.TemporaryDirectory() as temp:
            destination = pathlib.Path(temp) / "acme-sleep"

            initializer.initialise(destination, "Acme Sleep", "acme-sleep")

            manifest = (destination / "brand.yml").read_text()
            self.assertIn('method_version: "0.4.0"', manifest)
            self.assertIn('test_prefix: "CONTST"', manifest)
            self.assertIn("next_test_number: 1", manifest)
            self.assertIn('brand_code: ""', manifest)
            self.assertIn("product_codes: {}", manifest)
            self.assertIn("region_codes: {}", manifest)
            self.assertIn('budget_type: "ABO"', manifest)
            self.assertIn("daily_ad_set_floor: 50", manifest)
            self.assertIn("preferred_daily_ad_set_budget: 100", manifest)
            self.assertIn("planned_observation_full_days: 5", manifest)
            self.assertNotIn("concept_code:", manifest)
            self.assertNotIn("next_concept_number:", manifest)

            concept_register = (
                destination / "strategy/concept-register.yml"
            ).read_text()
            test_register = (destination / "strategy/test-register.yml").read_text()
            winner_library = (
                destination / "strategy/winner-library.yml"
            ).read_text()
            for register in (concept_register, test_register, winner_library):
                self.assertIn('brand_slug: "acme-sleep"', register)

            self.assertIn("coordinates: []", concept_register)
            self.assertIn("coordinate_key", concept_register)
            self.assertIn("linked_test_ids", concept_register)
            self.assertIn("tests: []", test_register)
            self.assertIn("Initial NNT and INSPO batches contain", test_register)
            for awareness_code in ("UWA", "PRA", "SLA", "PDA"):
                self.assertIn(awareness_code, test_register)
            self.assertIn("ITR batches may be narrower", test_register)
            self.assertIn("explanation_confidence", test_register)
            self.assertIn("winners: []", winner_library)
            self.assertIn("real_post_id", winner_library)
            self.assertIn("scaling_history", winner_library)
            self.assertIn("linked_itr_test_ids", winner_library)

    def test_refuses_to_overwrite_a_non_empty_destination(self):
        initializer = load_initializer()
        with tempfile.TemporaryDirectory() as temp:
            destination = pathlib.Path(temp) / "acme-sleep"
            destination.mkdir()
            (destination / "keep.txt").write_text("owned by user")

            with self.assertRaises(FileExistsError):
                initializer.initialise(destination, "Acme Sleep", "acme-sleep")

            self.assertEqual("owned by user", (destination / "keep.txt").read_text())

    def test_rejects_an_invalid_slug(self):
        initializer = load_initializer()
        with tempfile.TemporaryDirectory() as temp:
            destination = pathlib.Path(temp) / "bad"

            with self.assertRaisesRegex(ValueError, "lowercase hyphenated"):
                initializer.initialise(destination, "Bad Brand", "Bad Brand")

    def test_escapes_a_quoted_brand_name_in_yaml_only(self):
        initializer = load_initializer()
        with tempfile.TemporaryDirectory() as temp:
            destination = pathlib.Path(temp) / "quoted-brand"

            initializer.initialise(
                destination, 'Joe\'s "Carry" Co', "quoted-brand"
            )

            manifest = (destination / "brand.yml").read_text()
            readme = (destination / "README.md").read_text()
            self.assertIn('name: "Joe\'s \\"Carry\\" Co"', manifest)
            self.assertIn('# Joe\'s "Carry" Co brand folder', readme)
            self.assertIn('output_dir: "outputs"', manifest)


if __name__ == "__main__":
    unittest.main()
