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
                "research/customer-intelligence.md",
                "strategy/concept-register.yml",
                "strategy/hypothesis-backlog.yml",
                "learning/learning-events.jsonl",
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


if __name__ == "__main__":
    unittest.main()
