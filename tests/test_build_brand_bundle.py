import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock


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
            "brand.yml": (
                'brand:\n  name: "Acme Sleep"\n  slug: "acme-sleep"\n'
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1\n'
            ),
            "context/brand-core.md": "Brand core content\n",
            "context/voice.md": "Voice rules\n",
            "context/visual.md": "Visual rules\n",
            "products/catalog.yml": "products: []\n",
            "products/offers.yml": "offers: []\n",
            "products/economics.yml": "economics: {}\n",
            "products/proof-library.yml": "proof: []\n",
            "products/claims.yml": "claims: []\n",
            "research/customer-intelligence.md": "Customer synthesis\n",
            "research/evidence-ledger/manifest.json": '{"evidence_version":4}\n',
            "sources/website/crawl-state.json": '{"last_full_crawl":"2026-08-26"}\n',
            "strategy/concept-register.yml": "concepts: []\n",
            "strategy/test-register.yml": "tests: []\n",
            "strategy/winner-library.yml": "winners: []\n",
            "strategy/hypothesis-backlog.yml": "hypotheses: []\n",
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
        self.assertIn('"last_full_crawl":"2026-08-26"', bundle)
        self.assertIn('"evidence_version":4', bundle)
        self.assertIn("tests: []", bundle)
        self.assertIn("winners: []", bundle)
        self.assertIn("Evidence version: `sha256:", bundle)
        self.assertIn("Learning version: `sha256:", bundle)

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

    def test_explicitly_excludes_analysis_runs_raw_assets_and_csv_files(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        unsafe = {
            "outputs/ad-analysis/ADR-20260827-001/intake.json": (
                '{"brand_slug":"acme-sleep","run_id":"ADR-20260827-001"}\n'
            ),
            "outputs/ad-analysis/ADR-20260827-001/diagnosis.md": (
                "temporary diagnosis output\n"
            ),
            "assets/raw-ad.png": "raw creative asset\n",
            "exports/performance.csv": "ad_id,spend\nad-1,100\n",
        }
        for relative, content in unsafe.items():
            target = folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)

        output = pathlib.Path(temp.name) / "brand-bundle.md"
        with mock.patch.object(
            builder, "ALLOWED_EXACT", builder.ALLOWED_EXACT | set(unsafe)
        ), mock.patch.object(
            builder, "ALLOWED_SUFFIXES", builder.ALLOWED_SUFFIXES | {".csv", ".png"}
        ):
            builder.build_bundle(folder, output)

        bundle = output.read_text()
        for relative, content in unsafe.items():
            with self.subTest(relative=relative):
                self.assertNotIn(f"## Source: `{relative}`", bundle)
                self.assertNotIn(content.strip(), bundle)

    def test_requires_a_brand_manifest(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temp:
            folder = pathlib.Path(temp) / "missing"
            folder.mkdir()

            with self.assertRaisesRegex(FileNotFoundError, "brand.yml"):
                builder.build_bundle(folder, pathlib.Path(temp) / "bundle.md")

    def test_refuses_secret_assignments_inside_allowed_sources(self):
        builder = load_builder()
        cases = (
            ("products/claims.yml", 'client_secret: "hidden-value"\n'),
            ("context/brand-core.md", "Authorization: Bearer hidden-token\n"),
            ("learning/active-memory.json", '{"oauth":{"clientSecret":"hidden-json"}}\n'),
            ("context/voice.md", "FIRECRAWL_API_KEY=hidden-prefixed\n"),
            ("context/visual.md", (
                "-----BEGIN PRIVATE KEY-----\nsecret-material\n"
                "-----END PRIVATE KEY-----\n"
            )),
            ("context/brand-core.md", (
                "-----BEGIN ENCRYPTED PRIVATE KEY-----\nsecret-material\n"
                "-----END ENCRYPTED PRIVATE KEY-----\n"
            )),
        )

        for relative, content in cases:
            with self.subTest(relative=relative):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                target = folder / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)

                with self.assertRaisesRegex(ValueError, "possible secret"):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_unapproved_files_in_sensitive_safe_namespaces(self):
        builder = load_builder()
        cases = (
            ("strategy/raw-review.md", "raw review body that must not travel\n"),
            ("context/other-brand-notes.md", "unapproved cross-brand prose\n"),
            ("products/private-pricing.yml", "unapproved: true\n"),
        )

        for relative, content in cases:
            with self.subTest(relative=relative):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                target = folder / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)

                with self.assertRaisesRegex(ValueError, "unapproved bundle source"):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_github_token_fingerprints_in_approved_prose(self):
        builder = load_builder()
        token_cases = (
            "gh" + "p_" + ("A" * 36),
            "github_" + "pat_" + ("B" * 72),
        )

        for token in token_cases:
            with self.subTest(prefix=token.split("_", 1)[0]):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                (folder / "context" / "brand-core.md").write_text(
                    f"Accidentally pasted credential: {token}\n"
                )

                with self.assertRaisesRegex(ValueError, "possible secret"):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_rejects_output_inside_brand_folder_before_self_inclusion(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        output = folder / "strategy" / "generated-brand-bundle.md"

        for _attempt in range(2):
            with self.assertRaisesRegex(ValueError, "output must be outside brand folder"):
                builder.build_bundle(folder, output)
            self.assertFalse(output.exists())

    def test_refuses_gapped_or_reused_real_brand_test_ids(self):
        builder = load_builder()
        cases = (
            (
                "  - test_id: CONTST001\n  - test_id: CONTST003\n",
                4,
                "sequential CONTST",
            ),
            (
                "  - test_id: CONTST001\n  - test_id: CONTST001\n",
                2,
                "reuses CONTST001",
            ),
        )

        for rows, next_number, error in cases:
            with self.subTest(error=error):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                manifest = (folder / "brand.yml").read_text().replace(
                    "next_test_number: 1", f"next_test_number: {next_number}"
                )
                (folder / "brand.yml").write_text(manifest)
                (folder / "strategy" / "test-register.yml").write_text(
                    "tests:\n" + rows
                )

                with self.assertRaisesRegex(ValueError, error):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_next_test_number_that_does_not_follow_real_state(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        manifest = (folder / "brand.yml").read_text().replace(
            "next_test_number: 1", "next_test_number: 2"
        )
        (folder / "brand.yml").write_text(manifest)

        with self.assertRaisesRegex(ValueError, "next_test_number must be 1"):
            builder.build_bundle(folder, pathlib.Path(temp.name) / "brand-bundle.md")

    def test_refuses_noncanonical_test_register_item_forms(self):
        builder = load_builder()
        cases = (
            (
                "tests:\n  - {test_id: CONTST001, source: NNT}\n",
                "canonical block-style",
            ),
            (
                "tests:\n  - test_id: contst001\n    source: NNT\n",
                "canonical block-style",
            ),
            (
                "tests:\n  - source: NNT\n",
                "canonical block-style",
            ),
            (
                "tests:\n"
                "  - test_id: CONTST001\n"
                "    source: NNT\n"
                "  - {test_id: CONTST002, source: INSPO}\n",
                "canonical block-style",
            ),
        )

        for register, error in cases:
            with self.subTest(register=register):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                manifest = (folder / "brand.yml").read_text().replace(
                    "next_test_number: 1", "next_test_number: 2"
                )
                (folder / "brand.yml").write_text(manifest)
                (folder / "strategy" / "test-register.yml").write_text(register)

                with self.assertRaisesRegex(ValueError, error):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_lowercase_or_duplicate_naming_state_keys(self):
        builder = load_builder()
        cases = (
            (
                'test_prefix: "CONTST"',
                'test_prefix: "contst"',
                "test_prefix must be literal uppercase CONTST",
            ),
            (
                'test_prefix: "CONTST"',
                'test_prefix: "CONTST"\n  test_prefix: "CONTST"',
                "exactly one naming.test_prefix",
            ),
            (
                "next_test_number: 1",
                "next_test_number: 1\n  next_test_number: 1",
                "exactly one naming.next_test_number",
            ),
            (
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1',
                'test_prefix: "CONTST"\nnaming:\n  next_test_number: 1',
                "exactly one naming.test_prefix",
            ),
            (
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1',
                'next_test_number: 1\nnaming:\n  test_prefix: "CONTST"',
                "exactly one naming.next_test_number",
            ),
            (
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1',
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1\n'
                'naming: {test_prefix: "CONTST", next_test_number: 1}',
                "exactly one top-level naming block",
            ),
        )

        for original, replacement, error in cases:
            with self.subTest(error=error):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                manifest = (folder / "brand.yml").read_text().replace(
                    original, replacement
                )
                (folder / "brand.yml").write_text(manifest)

                with self.assertRaisesRegex(ValueError, error):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_duplicate_test_id_key_within_one_item(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        manifest = (folder / "brand.yml").read_text().replace(
            "next_test_number: 1", "next_test_number: 2"
        )
        (folder / "brand.yml").write_text(manifest)
        (folder / "strategy" / "test-register.yml").write_text(
            "tests:\n"
            "  - test_id: CONTST001\n"
            "    test_id: CONTST002\n"
        )

        with self.assertRaisesRegex(ValueError, "duplicate test_id key"):
            builder.build_bundle(folder, pathlib.Path(temp.name) / "brand-bundle.md")

    def test_refuses_additional_noncanonical_top_level_tests_key(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        (folder / "strategy" / "test-register.yml").write_text(
            "tests: []\n"
            "tests: {archived: []}\n"
        )

        with self.assertRaisesRegex(
            ValueError, "exactly one canonical top-level tests key"
        ):
            builder.build_bundle(folder, pathlib.Path(temp.name) / "brand-bundle.md")

    def test_refuses_ambiguous_or_malformed_yaml_in_state_files(self):
        builder = load_builder()
        cases = (
            (
                "strategy/test-register.yml",
                "tests:\n"
                "  - test_id: CONTST001\n"
                '    "test_id": CONTST002\n',
            ),
            (
                "strategy/test-register.yml",
                "tests:\n"
                "  - test_id: CONTST001\n"
                "    ? test_id\n"
                "    : CONTST002\n",
            ),
            (
                "brand.yml",
                'brand:\n  name: "Acme Sleep"\n  slug: "acme-sleep"\n'
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1\n'
                '  "next_test_number": 99\n',
            ),
            (
                "brand.yml",
                'brand:\n  name: "Acme Sleep"\n  slug: "acme-sleep"\n'
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1\n'
                '  "test_prefix": "OTHER"\n',
            ),
            (
                "strategy/test-register.yml",
                "tests:\n"
                "  - test_id: CONTST001\n"
                "    ads: [UWA, PRA\n",
            ),
            (
                "brand.yml",
                'brand:\n  name: "Acme Sleep"\n  slug: "acme-sleep"\n'
                '  markets: ["AU"\n'
                'naming:\n  test_prefix: "CONTST"\n  next_test_number: 1\n',
            ),
        )

        for relative, content in cases:
            with self.subTest(relative=relative, content=content):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                (folder / "brand.yml").write_text(
                    (folder / "brand.yml").read_text().replace(
                        "next_test_number: 1", "next_test_number: 2"
                    )
                )
                (folder / relative).write_text(content)

                with self.assertRaisesRegex(ValueError, "invalid canonical YAML"):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_unsupported_yaml_key_and_indentation_syntax(self):
        builder = load_builder()
        cases = (
            '    !!str test_id: CONTST002\n',
            '    &duplicate test_id: CONTST002\n',
            '    *test_id: CONTST002\n',
            '     source: NNT\n',
            '    source value without a mapping key\n',
        )

        for addition in cases:
            with self.subTest(addition=addition):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                manifest = (folder / "brand.yml").read_text().replace(
                    "next_test_number: 1", "next_test_number: 2"
                )
                (folder / "brand.yml").write_text(manifest)
                (folder / "strategy" / "test-register.yml").write_text(
                    "tests:\n  - test_id: CONTST001\n" + addition
                )

                with self.assertRaisesRegex(ValueError, "invalid canonical YAML"):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_refuses_yaml_indicator_prefixed_plain_scalars(self):
        builder = load_builder()
        values = (
            "- NNT",
            "@NNT",
            "%NNT",
            "`NNT",
            ",NNT",
            "NNT#INSPO",
            "NNT,INSPO",
            "NNT: INSPO",
        )

        for value in values:
            with self.subTest(value=value):
                temp, folder = self.make_brand_folder()
                self.addCleanup(temp.cleanup)
                manifest = (folder / "brand.yml").read_text().replace(
                    "next_test_number: 1", "next_test_number: 2"
                )
                (folder / "brand.yml").write_text(manifest)
                (folder / "strategy" / "test-register.yml").write_text(
                    "tests:\n"
                    "  - test_id: CONTST001\n"
                    f"    source: {value}\n"
                )

                with self.assertRaisesRegex(ValueError, "invalid canonical YAML"):
                    builder.build_bundle(
                        folder, pathlib.Path(temp.name) / "brand-bundle.md"
                    )

    def test_accepts_canonical_quoted_scalars_and_json_style_flow_values(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        (folder / "brand.yml").write_text(
            "brand:\n"
            "  name: 'Joe''s Sleep' # YAML single-quoted scalar\n"
            '  slug: "acme-sleep"\n'
            '  markets: ["AU", "NZ"]\n'
            "  attributes: {}\n"
            "naming:\n"
            '  test_prefix: "CONTST"\n'
            "  next_test_number: 1\n"
        )

        output = pathlib.Path(temp.name) / "brand-bundle.md"
        builder.build_bundle(folder, output)

        bundle = output.read_text()
        self.assertIn("name: 'Joe''s Sleep'", bundle)
        self.assertIn('markets: ["AU", "NZ"]', bundle)

    def test_accepts_realistic_canonical_nonempty_register_with_nested_ads(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        manifest = (folder / "brand.yml").read_text().replace(
            "next_test_number: 1", "next_test_number: 3"
        )
        (folder / "brand.yml").write_text(manifest)
        (folder / "strategy" / "test-register.yml").write_text(
            "tests:\n"
            "  - test_id: CONTST001\n"
            "    source: NNT # canonical inline comment\n"
            "    spend: -12.5\n"
            "    valid: true\n"
            "    result: null\n"
            "    coordinate_key: sleep/UWA-v1\n"
            "    ads:\n"
            "      - awareness_code: UWA\n"
            "        ad_name: ACME_PRODUCT_CT_UWA\n"
            "      - awareness_code: PRA\n"
            "        ad_name: ACME_PRODUCT_CT_PRA\n"
            "  - test_id: CONTST002\n"
            "    source: ITR\n"
            "    ads:\n"
            "      - awareness_code: SLA\n"
            "        ad_name: ACME_PRODUCT_CT_SLA\n"
        )
        output = pathlib.Path(temp.name) / "brand-bundle.md"

        result = builder.build_bundle(folder, output)

        self.assertEqual(output, result)
        bundle = output.read_text()
        self.assertIn("test_id: CONTST001", bundle)
        self.assertIn("test_id: CONTST002", bundle)
        self.assertIn("awareness_code: UWA", bundle)

    def test_bundles_every_supported_canonical_sensitive_file(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        output = pathlib.Path(temp.name) / "brand-bundle.md"

        builder.build_bundle(folder, output)

        bundle = output.read_text()
        supported = (
            "context/brand-core.md",
            "context/voice.md",
            "context/visual.md",
            "products/catalog.yml",
            "products/offers.yml",
            "products/economics.yml",
            "products/proof-library.yml",
            "products/claims.yml",
            "strategy/concept-register.yml",
            "strategy/test-register.yml",
            "strategy/winner-library.yml",
            "strategy/hypothesis-backlog.yml",
        )
        for relative in supported:
            with self.subTest(relative=relative):
                self.assertIn(f"## Source: `{relative}`", bundle)

    def test_refuses_cross_brand_scoped_state(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        (folder / "learning" / "active-memory.json").write_text(
            '{"brand_slug":"other-brand","active_rules":[]}\n'
        )

        with self.assertRaisesRegex(ValueError, "does not match manifest brand"):
            builder.build_bundle(folder, pathlib.Path(temp.name) / "brand-bundle.md")

    def test_refuses_symlinked_bundle_sources(self):
        builder = load_builder()
        temp, folder = self.make_brand_folder()
        self.addCleanup(temp.cleanup)
        outside = pathlib.Path(temp.name) / "outside.md"
        outside.write_text("content outside the brand folder\n")
        link = folder / "context" / "linked.md"
        link.symlink_to(outside)

        with self.assertRaisesRegex(ValueError, "symlink"):
            builder.build_bundle(folder, pathlib.Path(temp.name) / "brand-bundle.md")


if __name__ == "__main__":
    unittest.main()
