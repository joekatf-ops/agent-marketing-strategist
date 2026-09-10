import copy
import importlib.util
import json
import pathlib
import struct
import subprocess
import tempfile
import unittest
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png(width, height):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\0" + b"\xff\xff\xff" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class ImageRunTests(unittest.TestCase):
    def setUp(self):
        self.validator = load("validate-image-ad")
        self.record = json.loads((ROOT / "examples/image-ad-run.json").read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = pathlib.Path(self.temp.name)

    def errors(self):
        return self.validator.validate(self.record, self.base)

    def render(self, width=32, height=32):
        (self.base / "asset.png").write_bytes(png(width, height))
        self.record["outputs"][0].update(status="generated", file="asset.png")

    def test_product_only_unrendered_record_is_valid(self):
        self.assertEqual([], self.errors())

    def test_generated_requires_an_actual_asset(self):
        self.record["outputs"][0]["status"] = "generated"
        self.assertTrue(any("no actual asset" in e for e in self.errors()))

    def test_requested_square_does_not_hide_non_square_pixels(self):
        self.render(40, 32)
        self.assertTrue(any("40x32, not square" in e for e in self.errors()))

    def test_recorded_dimensions_do_not_override_actual_file(self):
        self.render()
        self.record["outputs"][0].update(width=2048, height=2048)
        self.assertTrue(any("disagree" in e for e in self.errors()))

    def test_verified_requires_human_or_vision_checks(self):
        self.render()
        self.record["outputs"][0].update(status="verified", width=32, height=32)
        self.assertTrue(any("recorded inspection" in e for e in self.errors()))
        self.record["outputs"][0]["checks"] = dict.fromkeys(("text", "product", "layout", "claims"), True)
        self.assertEqual([], self.errors())

    def test_url_alone_cannot_claim_local_verification(self):
        self.record["outputs"][0].update(status="verified", result_url="https://example.com/image.png")
        self.assertTrue(any("requires a file" in e for e in self.errors()))

    def test_missing_markers_never_reach_production(self):
        for field in ("copy_on_image", "prompt"):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record["outputs"][0][field] = "Price [PRICE: confirm]"
                self.assertTrue(any("missing-fact marker" in e for e in self.validator.validate(record, self.base)))

    def test_duplicate_jobs_and_indices_rejected(self):
        self.record["outputs"][0]["job_id"] = "test-job"
        self.record["outputs"].append(copy.deepcopy(self.record["outputs"][0]))
        errors = self.errors()
        self.assertTrue(any("duplicate index" in e for e in errors))
        self.assertTrue(any("duplicate job ID" in e for e in errors))

    def test_invalid_shape_fails_without_crashing(self):
        for record in ([], {}, {"schema_version": "1.0", "product": "Desk organiser", "outputs": [None]}):
            with self.subTest(record=record):
                self.assertTrue(self.validator.validate(record, self.base))

    def test_non_square_requested_ratio_rejected(self):
        self.record["outputs"][0]["aspect_ratio"] = "4:5"
        self.assertTrue(self.errors())

    def test_truncated_or_non_image_file_rejected(self):
        for content in (b"", b"not an image", b"\xff\xd8\xff\xc0\x00\x11"):
            with self.subTest(content=content):
                path = self.base / "bad.jpg"
                path.write_bytes(content)
                with self.assertRaises(ValueError):
                    self.validator.dimensions(path)

    def test_jpeg_and_webp_headers_measured(self):
        # Minimal frame/header fixtures exercise each supported dimension path.
        jpeg = b"\xff\xd8\xff\xc0\x00\x0b\x08" + struct.pack(">HH", 25, 25) + b"\x01\x01\x11\x00\xff\xd9"
        webp = b"RIFF" + (22).to_bytes(4, "little") + b"WEBPVP8X" + (10).to_bytes(4, "little") + b"\0"*4 + (24).to_bytes(3, "little")*2
        for name, data in (("a.jpg", jpeg), ("b.webp", webp)):
            (self.base / name).write_bytes(data)
            self.assertEqual((25, 25), self.validator.dimensions(self.base / name))


class SwipeTeachingTests(unittest.TestCase):
    def test_unreviewed_annotation_does_not_enter_teaching_digest(self):
        builder = load("build-swipe-digest")
        entries = json.loads((ROOT / "corpus/swipe/entries.json").read_text())
        if isinstance(entries, dict):
            entries = entries["entries"]
        entry = copy.deepcopy(next(e for e in entries if e.get("annotation")))
        entry["content"]["headline"] = "UNREVIEWED_SENTINEL"
        entry["reviewed"] = False
        self.assertNotIn("UNREVIEWED_SENTINEL", builder.build_digest([entry]))
        entry["reviewed"] = True
        self.assertIn("UNREVIEWED_SENTINEL", builder.build_digest([entry]))

    def test_sync_preserves_visual_inspection(self):
        sync = load("sync-swipe-corpus")
        entries = json.loads((ROOT / "corpus/swipe/entries.json").read_text())
        if isinstance(entries, dict):
            entries = entries["entries"]
        old = copy.deepcopy(entries[0])
        old["annotation"] = None
        old["visual_analysis"] = {"inspection_status": "not-inspected", "observations": [], "interpretations": []}
        old["media"] = [{"source": "https://example.com/ref.png", "kind": "image"}]
        refreshed = copy.deepcopy(old)
        refreshed.pop("visual_analysis")
        refreshed.pop("media")
        merged, counts = sync.merge([old], [refreshed])
        self.assertEqual(old["visual_analysis"], merged[0]["visual_analysis"])
        self.assertEqual(old["media"], merged[0]["media"])


class ImageBundleTests(unittest.TestCase):
    def test_committed_bundle_matches_all_sources(self):
        builder = load("build-image-ad-bundle")
        self.assertEqual(builder.build(), builder.OUT.read_text())

    def test_image_bundle_can_ship_in_git(self):
        result = subprocess.run(["git", "check-ignore", "dist/image-ad-bundle.md"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

    def test_image_bundle_is_compact_and_brand_agnostic(self):
        body = load("build-image-ad-bundle").build()
        self.assertLess(len(body.encode()), 70000)
        self.assertNotIn("# Cadian:", body)
        self.assertIn("<!-- source: config/copy-lexicon.yml -->", body)


if __name__ == "__main__":
    unittest.main()
