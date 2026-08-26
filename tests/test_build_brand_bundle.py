import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build-brand-bundle.py"


def load_builder():
    if not SCRIPT.exists():
        raise AssertionError("scripts/build-brand-bundle.py should exist")
    spec = importlib.util.spec_from_file_location("build_brand_bundle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BrandBundleTests(unittest.TestCase):
    def make_brand_folder(self):
        temp = tempfile.TemporaryDirectory()
        folder = pathlib.Path(temp.name) / "acme-sleep"
        files = {
            "brand.yml": 'brand:\n  name: "Acme Sleep"\n  slug: "acme-sleep"\n',
            "context/brand-core.md": "Brand core content\n",
            "context/voice.md": "Voice rules\n",
            "products/catalog.yml": "products: []\n",
            "research/customer-intelligence.md": "Customer synthesis\n",
            "strategy/concept-register.yml": "concepts: []\n",
            "learning/approved-rules.yml": "rules:\n  - Approved rule\n",
            "learning/learning-events.jsonl": '{"raw": "private revision history"}\n',
            "research/customer-reviews/raw.md": "raw review body\n",
            "connectors/capabilities.yml": "website_crawling: firecrawl\n",
            ".env": "FIRECRAWL_API_KEY=secret-value\n",
            "secrets/token.txt": "secret token\n",
        }
        for relative, content in files.items():
            target = folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        return temp, folder

    def test_builds_a_deterministic_upload_bundle(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        output = pathlib.Path(temp.name) / "brand-bundle.md"

        result = builder.build_bundle(folder, output)

        self.assertEqual(output, result)
        first = output.read_text()
        builder.build_bundle(folder, output)
        self.assertEqual(first, output.read_text())
        self.assertLess(first.index("context/brand-core.md"), first.index("products/catalog.yml"))

    def test_includes_approved_context_and_synthesis(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        output = pathlib.Path(temp.name) / "brand-bundle.md"

        builder.build_bundle(folder, output)

        bundle = output.read_text()
        self.assertIn("Brand core content", bundle)
        self.assertIn("Customer synthesis", bundle)
        self.assertIn("Approved rule", bundle)
        self.assertIn("website_crawling: firecrawl", bundle)

    def test_excludes_raw_evidence_revision_history_and_secrets(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        output = pathlib.Path(temp.name) / "brand-bundle.md"

        builder.build_bundle(folder, output)

        bundle = output.read_text()
        self.assertNotIn("raw review body", bundle)
        self.assertNotIn("private revision history", bundle)
        self.assertNotIn("secret-value", bundle)
        self.assertNotIn("secret token", bundle)

    def test_requires_a_brand_manifest(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temp:
            folder = pathlib.Path(temp) / "missing"
            folder.mkdir()

            with self.assertRaisesRegex(FileNotFoundError, "brand.yml"):
                builder.build_bundle(folder, pathlib.Path(temp) / "bundle.md")


if __name__ == "__main__":
    unittest.main()
