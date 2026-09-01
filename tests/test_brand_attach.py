"""Tests for attaching a brand: scaffold, seed, check readiness, build the upload bundle.

The path a non-technical person takes is: hand over a brand, get usable copy. Mechanically that
is four steps, and every one of them had a way to fail silently. `init-brand-folder.py` created
thirty empty files and reported success, so a folder carrying nothing looked identical to a
folder carrying everything. This module holds the checks that make each step's answer honest.

`examples/brand-folder/` is the fictional Acme Trailworks fixture. It is the only brand folder in
this repository and it is not a real brand.
"""

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "brand-folder"
TEMPLATE = ROOT / "templates" / "brand-folder"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def initializer():
    return load("init_brand_folder", ROOT / "scripts" / "init-brand-folder.py")


def checker():
    return load("check_brand_folder", ROOT / "scripts" / "check-brand-folder.py")


def run_checker(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check-brand-folder.py"), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


class SeedTests(unittest.TestCase):
    """A connector read should reach the folder without anybody hand-editing YAML."""

    SEED = {
        "canonical_url": "https://example.com",
        "default_market": "AU",
        "markets": ["AU", "NZ"],
        "currency": "AUD",
        "products": [
            {
                "id": "sku-1",
                "name": "Test Product",
                "status": "active",
                "price": "34.00",
                "currency": "AUD",
                "variants": ["Default"],
                "source": "store read",
            }
        ],
    }

    def seeded(self, directory, seed=None):
        module = initializer()
        destination = pathlib.Path(directory) / "brand"
        module.initialise(destination, "Acme Sleep", "acme-sleep")
        module.apply_seed(destination, self.SEED if seed is None else seed)
        return destination

    def test_seed_writes_brand_fields_and_the_catalogue(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = self.seeded(directory)
            brand = (folder / "brand.yml").read_text()
            catalog = (folder / "products" / "catalog.yml").read_text()

        self.assertIn('canonical_url: "https://example.com"', brand)
        self.assertIn('default_market: "AU"', brand)
        self.assertIn('markets: ["AU", "NZ"]', brand)
        self.assertIn('currency: "AUD"', brand)
        self.assertIn('name: "Test Product"', catalog)
        self.assertIn('price: "34.00"', catalog)

    def test_a_seed_never_writes_a_claim_or_a_proof_point(self):
        # The defect this prevents is the important one. A store listing carries the brand's own
        # published marketing copy, which is not evidence that a claim is approved for a market.
        # If a seed could write claims.yml, connecting a store would silently approve every
        # sentence on it.
        hostile = dict(self.SEED)
        hostile["claims"] = [{"exact_claim": "cures everything", "status": "approved"}]
        hostile["proof"] = [{"detail": "9,000 five-star reviews"}]

        with tempfile.TemporaryDirectory() as directory:
            folder = self.seeded(directory, hostile)
            claims = (folder / "products" / "claims.yml").read_text()
            proof = (folder / "products" / "proof-library.yml").read_text()

        self.assertIn("claims: []", claims)
        self.assertNotIn("cures everything", claims)
        self.assertNotIn("9,000", proof)

    def test_a_product_description_from_the_store_is_kept_as_source_text(self):
        # It is useful context and it is not an approved claim, so it is recorded under a field
        # name that says which of the two it is.
        seed = json.loads(json.dumps(self.SEED))
        seed["products"][0]["description_from_source"] = "Helps you sleep deeply."

        with tempfile.TemporaryDirectory() as directory:
            folder = self.seeded(directory, seed)
            catalog = (folder / "products" / "catalog.yml").read_text()

        self.assertIn("description_from_source:", catalog)
        self.assertNotIn("approved_wording", catalog)

    def test_seeding_is_repeatable_without_corrupting_the_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = self.seeded(directory)
            once = (folder / "brand.yml").read_text()
            initializer().apply_seed(folder, self.SEED)
            twice = (folder / "brand.yml").read_text()

        self.assertEqual(once, twice)

    def test_asset_directories_exist_so_a_photograph_has_somewhere_to_go(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = self.seeded(directory)
            for relative in initializer().ASSET_DIRECTORIES:
                with self.subTest(relative=relative):
                    self.assertTrue((folder / relative).is_dir())

    def test_a_seeded_folder_still_builds_a_bundle(self):
        # The bundle builder enforces a canonical YAML subset, so a seed that renders slightly
        # off produces a folder that cannot be uploaded anywhere.
        builder = ROOT / "scripts" / "build-brand-bundle.py"
        with tempfile.TemporaryDirectory() as directory:
            folder = self.seeded(directory)
            output = pathlib.Path(directory) / "bundle.md"
            result = subprocess.run(
                [sys.executable, str(builder), str(folder), str(output)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Test Product", output.read_text())


class ReadinessTests(unittest.TestCase):
    def test_an_empty_folder_reports_thin_rather_than_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = pathlib.Path(directory) / "brand"
            initializer().initialise(destination, "Acme Sleep", "acme-sleep")
            state, _, missing = checker().report(destination, "copy")

        self.assertEqual("thin", state)
        self.assertTrue(missing)

    def test_a_template_file_left_untouched_does_not_count_as_content(self):
        # The regression: research/customer-intelligence.md ships with two sentences of
        # instruction, so a length threshold reported the customer language as present on every
        # new folder. A checker that claims a brand has its voice of customer when it has none
        # is worse than no checker.
        module = checker()
        for relative in (
            "context/brand-core.md",
            "context/voice.md",
            "context/visual.md",
            "research/customer-intelligence.md",
        ):
            with self.subTest(relative=relative):
                shipped = (TEMPLATE / relative).read_text()
                self.assertFalse(module.prose_is_filled(shipped, relative))
                self.assertTrue(
                    module.prose_is_filled(shipped + "\n\nA real fact about a real reader " * 3, relative)
                )

    def test_the_fixture_is_ready_for_copy(self):
        # A checker that has never returned ready has not been shown to work.
        state, have, missing = checker().report(FIXTURE, "copy")

        self.assertEqual("ready", state, f"missing: {[item.label for item in missing]}")
        self.assertGreaterEqual(len(have), 9)

    def test_the_fixture_cannot_be_ready_for_images_and_that_is_correct(self):
        # A fictional product has no real photograph, and a generated one would invent the
        # product. The gate is supposed to stop here.
        state, _, missing = checker().report(FIXTURE, "image")

        self.assertNotEqual("ready", state)
        self.assertIn("assets/product/", [item.where for item in missing])

    def test_readiness_differs_by_deliverable(self):
        module = checker()
        copy_state, _, _ = module.report(FIXTURE, "copy")
        launch_state, _, launch_missing = module.report(FIXTURE, "launch")

        self.assertEqual("ready", copy_state)
        self.assertNotEqual("ready", launch_state)
        self.assertIn("products/economics.yml", [item.where for item in launch_missing])

    def test_missing_input_is_a_report_and_not_a_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = pathlib.Path(directory) / "brand"
            initializer().initialise(destination, "Acme Sleep", "acme-sleep")
            plain = run_checker(str(destination))
            strict = run_checker(str(destination), "--strict")

        self.assertEqual(0, plain.returncode, plain.stdout)
        self.assertEqual(1, strict.returncode)
        self.assertIn("never stops a draft", plain.stdout)

    def test_a_path_that_is_not_a_brand_folder_says_so(self):
        result = run_checker(str(ROOT / "scripts"))

        self.assertEqual(2, result.returncode)
        self.assertIn("brand.yml is missing", result.stderr)

    def test_every_input_states_why_it_matters(self):
        for item in checker().inputs_for(FIXTURE):
            with self.subTest(label=item.label):
                self.assertGreater(len(item.why), 40, "an input without a reason is a checklist")
                self.assertTrue(set(item.needed_for) <= set(checker().DELIVERABLES))


class FixtureIsolationTests(unittest.TestCase):
    """The fixture is a second brand living inside the repository, so it needs a fence."""

    def test_the_fixture_is_labelled_fictional_in_every_file_a_reader_opens(self):
        for relative in (
            "README.md",
            "brand.yml",
            "products/catalog.yml",
            "products/claims.yml",
            "products/proof-library.yml",
            "products/offers.yml",
            "context/brand-core.md",
            "context/voice.md",
            "context/visual.md",
            "research/customer-intelligence.md",
        ):
            with self.subTest(relative=relative):
                text = (FIXTURE / relative).read_text().lower()
                self.assertTrue(
                    "fictional" in text or "fixture" in text,
                    f"{relative} does not say it is fixture data",
                )

    def test_the_fixture_never_reaches_a_shipped_bundle(self):
        # dist/ is what people paste into a chat surface. A fictional brand's claims arriving
        # there would be another brand's facts in the universal method, which is hard rule 5.
        for relative in ("dist/craft-bundle.md", "dist/knowledge-bundle.md"):
            with self.subTest(bundle=relative):
                text = (ROOT / relative).read_text()
                self.assertNotIn("Acme Trailworks", text)
                self.assertNotIn("Ridgeline", text)

    def test_the_fixture_carries_a_refused_claim(self):
        # The record that makes it a useful fixture: the claim the category always reaches for,
        # on file as rejected, so the answer is not re-argued every time.
        claims = (FIXTURE / "products" / "claims.yml").read_text()

        self.assertIn('status: "rejected"', claims)
        self.assertIn("blister", claims.lower())

    def test_the_repository_holds_exactly_one_brand_folder(self):
        found = sorted(
            path.parent.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("brand.yml")
            if ".git" not in path.parts
        )

        self.assertEqual(["examples/brand-folder", "templates/brand-folder"], found)


if __name__ == "__main__":
    unittest.main()
