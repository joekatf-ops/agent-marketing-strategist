import ast
import copy
import csv
import datetime as dt
import importlib.util
import json
import math
import os
import pathlib
import re
import subprocess
import sys
import sysconfig
import stat
import tempfile
import unittest
from unittest import mock
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "ad_analysis_harness.py"
CONTENT_SAFETY = ROOT / "scripts" / "content_safety.py"
INITIALIZER = ROOT / "scripts" / "init-brand-folder.py"
VALIDATOR = ROOT / "scripts" / "validate-ad-analysis-run.py"
INTAKE_SCHEMA = ROOT / "schemas" / "ad-analysis-intake.schema.json"
INTAKE_PORTABLE_CONFORMANCE = (
    ROOT / "schemas" / "ad-analysis-intake.conformance.json"
)
INTAKE_CONFORMANCE = (
    ROOT / "tests" / "fixtures" / "ad-analysis-intake-conformance.json"
)
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
DIAGNOSIS_FIXTURES = {
    "intake": ROOT / "examples" / "ad-diagnosis-intake.json",
    "audit": ROOT / "examples" / "ad-diagnosis-input-audit.md",
    "performance": ROOT / "examples" / "ad-diagnosis-performance.csv",
    "report": ROOT / "examples" / "ad-diagnosis.md",
}


def markdown_table(text, heading, next_heading):
    section = text.split(heading, 1)[1].split(next_heading, 1)[0]
    lines = [line for line in section.splitlines() if line.startswith("|")]
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    return [
        dict(zip(headers, [cell.strip() for cell in line.strip("|").split("|")]))
        for line in lines[2:]
    ]


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


def load_validator(harness):
    spec = importlib.util.spec_from_file_location("validate_ad_analysis_run", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, {"ad_analysis_harness": harness}):
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


def apply_json_pointer(document, pointer, value, *, remove=False):
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
    target = document
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = parts[-1]
    if remove:
        if isinstance(target, list):
            del target[int(final)]
        else:
            del target[final]
    elif isinstance(target, list):
        target[int(final)] = value
    else:
        target[final] = value


def json_pointer_value(document, pointer):
    target = document
    for part in pointer.split("/")[1:]:
        part = part.replace("~1", "/").replace("~0", "~")
        target = target[int(part)] if isinstance(target, list) else target[part]
    return target


def materialize_conformance_case(corpus, case):
    document = copy.deepcopy(corpus["bases"][case["base"]])
    for pointer in case.get("remove", []):
        apply_json_pointer(document, pointer, None, remove=True)
    for pointer, value in case.get("set", {}).items():
        apply_json_pointer(document, pointer, value)
    for operation in case.get("append_copy", []):
        source = copy.deepcopy(json_pointer_value(document, operation["from"]))
        json_pointer_value(document, operation["to"]).append(source)
    for pointer, values in case.get("append", {}).items():
        json_pointer_value(document, pointer).extend(copy.deepcopy(values))
    return document


def portable_conformance_errors(instance, contract, context):
    """Execute the governed relational operations declared by the portable contract."""
    errors = []
    for rule in contract.get("rules", []):
        identifier = rule["id"]
        operation = rule["operation"]
        if operation == "valid_run_id":
            value = instance.get(rule["field"])
            match = re.fullmatch(
                r"ADR-(?P<date>\d{8})-(?P<number>\d{3})", value or ""
            )
            valid = bool(match and int(match.group("number")) >= 1)
            if match:
                try:
                    dt.datetime.strptime(match.group("date"), "%Y%m%d")
                except ValueError:
                    valid = False
            if not valid:
                errors.append(identifier)
        elif operation == "equals_context":
            if instance.get(rule["field"]) != context[rule["context"]]:
                errors.append(identifier)
        elif operation == "unique_field":
            values = instance.get(rule["array"], [])
            if isinstance(values, list):
                seen = set()
                for item in values:
                    value = item.get(rule["field"]) if isinstance(item, dict) else None
                    if isinstance(value, str) and value in seen:
                        errors.append(identifier)
                        break
                    if isinstance(value, str):
                        seen.add(value)
        elif operation == "known_references":
            targets = instance.get(rule["target_array"], [])
            known = {
                item.get(rule["target_field"])
                for item in targets
                if isinstance(item, dict)
                and isinstance(item.get(rule["target_field"]), str)
            }
            container = instance
            for field in rule["source_path"]:
                if not isinstance(container, dict) or field not in container:
                    container = None
                    break
                container = container[field]
            references = []
            if rule["source_kind"] == "array_object_lists" and isinstance(
                container, list
            ):
                for item in container:
                    if isinstance(item, dict) and isinstance(
                        item.get(rule["reference_field"]), list
                    ):
                        references.extend(item[rule["reference_field"]])
            elif rule["source_kind"] == "array_values" and isinstance(
                container, list
            ):
                references.extend(container)
            elif rule["source_kind"] == "mapping_values" and isinstance(
                container, dict
            ):
                references.extend(container.values())
            elif rule["source_kind"] == "array_object_field" and isinstance(
                container, list
            ):
                references.extend(
                    item.get(rule["reference_field"])
                    for item in container
                    if isinstance(item, dict)
                )
            if any(
                isinstance(reference, str) and reference not in known
                for reference in references
            ):
                errors.append(identifier)
        elif operation == "ordered_dates":
            value = instance
            for field in rule["object_path"]:
                if not isinstance(value, dict) or field not in value:
                    value = None
                    break
                value = value[field]
            if isinstance(value, dict):
                try:
                    start = dt.date.fromisoformat(value[rule["start_field"]])
                    end = dt.date.fromisoformat(value[rule["end_field"]])
                except (KeyError, TypeError, ValueError):
                    pass
                else:
                    if end < start:
                        errors.append(identifier)
        else:
            raise AssertionError(f"unsupported portable conformance operation: {operation}")
    return errors


def json_schema_errors(instance, schema, *, root=None, path="$"):
    """Evaluate the deterministic JSON-Schema subset used by the intake contract."""
    root = schema if root is None else root
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return json_schema_errors(instance, target, root=root, path=path)

    errors = []
    if "oneOf" in schema:
        matches = [
            not json_schema_errors(instance, subschema, root=root, path=path)
            for subschema in schema["oneOf"]
        ]
        if sum(matches) != 1:
            errors.append(f"{path} must match exactly one schema")
    for subschema in schema.get("allOf", []):
        errors.extend(json_schema_errors(instance, subschema, root=root, path=path))
    condition = schema.get("if")
    if condition is not None:
        branch = "then" if not json_schema_errors(instance, condition, root=root, path=path) else "else"
        if branch in schema:
            errors.extend(json_schema_errors(instance, schema[branch], root=root, path=path))

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path} does not equal the required constant")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path} is not in the allowed enum")

    allowed_types = schema.get("type")
    if allowed_types is not None:
        allowed_types = [allowed_types] if isinstance(allowed_types, str) else allowed_types

        def matches_type(type_name):
            return {
                "null": instance is None,
                "object": isinstance(instance, dict),
                "array": isinstance(instance, list),
                "string": isinstance(instance, str),
                "integer": type(instance) is int,
                "number": type(instance) in {int, float} and math.isfinite(instance),
                "boolean": isinstance(instance, bool),
            }[type_name]

        if not any(matches_type(type_name) for type_name in allowed_types):
            return errors + [f"{path} has the wrong type"]

    if isinstance(instance, dict):
        for required in schema.get("required", []):
            if required not in instance:
                errors.append(f"{path}.{required} is required")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(
                    json_schema_errors(value, properties[key], root=root, path=child_path)
                )
            elif additional is False:
                errors.append(f"{child_path} is not allowed")
            elif isinstance(additional, dict):
                errors.extend(
                    json_schema_errors(value, additional, root=root, path=child_path)
                )
        if len(instance) < schema.get("minProperties", 0):
            errors.append(f"{path} has too few properties")
        property_names = schema.get("propertyNames")
        if property_names:
            for key in instance:
                errors.extend(
                    json_schema_errors(
                        key,
                        property_names,
                        root=root,
                        path=f"{path} property name {key!r}",
                    )
                )

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path} has too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path} has too many items")
        if schema.get("uniqueItems"):
            canonical = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in instance]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{path} contains duplicate items")
        item_schema = schema.get("items")
        if item_schema:
            for index, value in enumerate(instance):
                errors.extend(
                    json_schema_errors(value, item_schema, root=root, path=f"{path}[{index}]")
                )

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path} is too short")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{path} does not match its pattern")
        if schema.get("format") == "date":
            try:
                dt.date.fromisoformat(instance)
            except ValueError:
                errors.append(f"{path} is not a calendar date")
        if schema.get("format") == "iana-timezone":
            try:
                ZoneInfo(instance)
            except (ValueError, ZoneInfoNotFoundError):
                errors.append(f"{path} is not an IANA timezone")

    if type(instance) in {int, float}:
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path} is below its minimum")
    return errors


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

    def create_modern_run(self, harness, mode="creative-audit"):
        return self.create_run(harness, mode)

    def create_legacy_run(self, harness, mode="creative-audit"):
        manifest = self.brand / "brand.yml"
        manifest.write_text(
            manifest.read_text().replace(
                'method_version: "0.4.0"', 'method_version: "0.3.0"'
            )
        )
        return self.create_run(harness, mode)

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
                        "asset_type": "video",
                        "primary_text": "Sleep through the night.",
                        "headline": "Wake up rested",
                        "description": "",
                        "cta": "Shop now",
                        "destination_url": "https://example.test/sleep-mask",
                        "destination_type": "PDP",
                        "coordinate_key": "travellers|light",
                        "contst": None,
                        "source": None,
                        "who": None,
                        "primary_problem": None,
                        "awareness_code": None,
                        "messaging_route": None,
                        "format": None,
                        "primary_hook": None,
                        "post_id": None,
                    }
                ],
            }
        )
        return intake

    def complete_performance_intake(self, harness, run):
        intake = self.complete_creative_intake(harness, run)
        intake["account_timezone"] = "Australia/Sydney"
        intake["ads"][0].update(
            {
                "contst": "CONTST001",
                "source": "NNT",
                "who": "Light-sensitive travellers",
                "primary_problem": "Hotel light interrupts sleep",
                "awareness_code": "PRA",
                "messaging_route": "Block unfamiliar room light",
                "format": "VSL",
                "primary_hook": "The hotel-room light you cannot switch off",
            }
        )
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
                "landing_page_views": "Landing page views",
                "video_3_second_plays": "3-second video plays",
            },
            "ad_mapping": {"Acme Sleep Mask AU": "AD-001"},
            "logged_interventions": [],
            "account_norms": [
                {
                    "metric": "target_cac",
                    "value": 60,
                    "unit": "AUD",
                    "comparison_window": "five full account days",
                    "source": "products/economics.yml",
                }
            ],
            "reference_ranges": {"status": "unavailable", "sources": []},
            "threshold_basis": [
                {
                    "metric": "target_cac",
                    "baseline": 90,
                    "comparison_window": "2026-08-20 through 2026-08-26",
                    "threshold": 60,
                    "unit": "AUD",
                    "source": "Meta export and products/economics.yml",
                    "ad_id": "AD-001",
                }
            ],
        }
        return intake

    def test_shared_schema_python_conformance_corpus(self):
        self.assertTrue(INTAKE_SCHEMA.is_file())
        self.assertTrue(INTAKE_CONFORMANCE.is_file())
        schema = json.loads(INTAKE_SCHEMA.read_text())
        corpus = json.loads(INTAKE_CONFORMANCE.read_text())
        portable_contract = (
            json.loads(INTAKE_PORTABLE_CONFORMANCE.read_text())
            if INTAKE_PORTABLE_CONFORMANCE.is_file()
            else {"rules": []}
        )
        harness = load_harness()

        for case in corpus["cases"]:
            with self.subTest(case=case["name"]):
                intake = materialize_conformance_case(corpus, case)
                run = self.create_modern_run(harness, mode=intake["mode"])
                if not case.get("preserve_run_id"):
                    intake["run_id"] = run.name
                self.write_intake(run, intake)

                schema_valid = not json_schema_errors(intake, schema)
                extension_errors = portable_conformance_errors(
                    intake,
                    portable_contract,
                    {
                        "run_id": run.name,
                        "brand_slug": "acme-sleep",
                        "method_version": "0.4.0",
                    },
                )
                portable_valid = schema_valid and not extension_errors
                result = harness.validate_run(self.brand, run)
                python_valid = result.status != "blocked"

                self.assertEqual(
                    case.get("base_schema_valid", case["valid"]), schema_valid
                )
                self.assertEqual(case["valid"], portable_valid)
                self.assertEqual(case["valid"], python_valid)
                if "extension_rule" in case:
                    self.assertIn(case["extension_rule"], extension_errors)
                if case["valid"]:
                    self.assertEqual(case["python_status"], result.status)
        self.assertTrue(
            INTAKE_PORTABLE_CONFORMANCE.is_file(),
            "portable relational conformance contract should exist",
        )

    def test_load_intake_rejects_duplicate_routing_keys_and_nonfinite_numbers(self):
        harness = load_harness()

        duplicate_run = self.create_run(harness)
        duplicate_text = (duplicate_run / "intake.json").read_text().replace(
            '  "mode": "creative-audit",',
            '  "mode": "creative-audit",\n  "mode": "performance-diagnosis",',
            1,
        )
        (duplicate_run / "intake.json").write_text(duplicate_text)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: mode"):
            harness.load_intake(duplicate_run)

        nonfinite_run = self.create_run(harness)
        nonfinite_text = (nonfinite_run / "intake.json").read_text().replace(
            '  "requester": "",', '  "requester": NaN,', 1
        )
        (nonfinite_run / "intake.json").write_text(nonfinite_text)
        with self.assertRaisesRegex(ValueError, "non-finite JSON number: NaN"):
            harness.load_intake(nonfinite_run)

    def test_load_intake_enforces_deterministic_size_and_depth_limits(self):
        harness = load_harness()
        oversized_run = self.create_run(harness)
        oversized = b'{"padding":"' + (b"x" * 1_048_576) + b'"}\n'
        (oversized_run / "intake.json").write_bytes(oversized)

        with self.assertRaisesRegex(ValueError, "maximum size of 1048576 bytes"):
            harness.load_intake(oversized_run)

        deep_run = self.create_run(harness)
        deep = '{"nested":' + ("[" * 33) + "0" + ("]" * 33) + "}\n"
        (deep_run / "intake.json").write_text(deep)
        with self.assertRaisesRegex(ValueError, "maximum depth of 32"):
            harness.load_intake(deep_run)

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

    def test_initialise_run_never_publishes_a_partial_canonical_directory(self):
        harness = load_harness()
        real_write = harness._write_new_regular_no_follow
        writes = 0

        def fail_second_initial_file(*args, **kwargs):
            nonlocal writes
            writes += 1
            if writes == 2:
                raise OSError("simulated README write failure")
            return real_write(*args, **kwargs)

        with mock.patch.object(
            harness,
            "_write_new_regular_no_follow",
            side_effect=fail_second_initial_file,
        ):
            with self.assertRaisesRegex(OSError, "simulated README write failure"):
                self.create_run(harness)

        analysis = self.brand / "outputs" / "ad-analysis"
        self.assertFalse((analysis / "ADR-20260827-001").exists())
        self.assertEqual([], list(analysis.glob(".*.staging-*")))

    def test_initialise_run_atomically_renames_one_complete_private_staging_run(self):
        harness = load_harness()
        real_rename = os.rename
        observations = []

        def inspect_then_rename(source, destination, *args, **kwargs):
            source_directory = kwargs["src_dir_fd"]
            destination_directory = kwargs["dst_dir_fd"]
            descriptor = os.open(
                source,
                os.O_RDONLY | os.O_DIRECTORY,
                dir_fd=source_directory,
            )
            try:
                observations.append(
                    (
                        source,
                        destination,
                        set(os.listdir(descriptor)),
                        os.stat("intake.json", dir_fd=descriptor).st_nlink,
                        os.stat("README.md", dir_fd=descriptor).st_nlink,
                    )
                )
                with self.assertRaises(FileNotFoundError):
                    os.stat(destination, dir_fd=destination_directory)
            finally:
                os.close(descriptor)
            return real_rename(source, destination, *args, **kwargs)

        with mock.patch("os.rename", side_effect=inspect_then_rename):
            run = self.create_run(harness)

        self.assertEqual(1, len(observations))
        staging, destination, files, intake_links, readme_links = observations[0]
        self.assertRegex(staging, r"^\.ADR-20260827-001\.staging-")
        self.assertEqual("ADR-20260827-001", destination)
        self.assertEqual({"intake.json", "README.md"}, files)
        self.assertEqual((1, 1), (intake_links, readme_links))
        self.assertEqual(run, self.brand / "outputs/ad-analysis/ADR-20260827-001")

    def test_automatic_run_id_retries_after_a_concurrent_atomic_publication(self):
        harness = load_harness()
        real_rename = os.rename
        raced = False

        def publish_competing_run_then_rename(source, destination, *args, **kwargs):
            nonlocal raced
            destination_directory = kwargs["dst_dir_fd"]
            if not raced:
                raced = True
                os.mkdir(destination, 0o755, dir_fd=destination_directory)
                run_descriptor = os.open(
                    destination,
                    os.O_RDONLY | os.O_DIRECTORY,
                    dir_fd=destination_directory,
                )
                try:
                    competitor = os.open(
                        "competitor.marker",
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                        0o644,
                        dir_fd=run_descriptor,
                    )
                    os.close(competitor)
                finally:
                    os.close(run_descriptor)
            return real_rename(source, destination, *args, **kwargs)

        with mock.patch("os.rename", side_effect=publish_competing_run_then_rename):
            run = self.create_run(harness)

        analysis = self.brand / "outputs" / "ad-analysis"
        self.assertEqual("ADR-20260827-002", run.name)
        self.assertTrue(
            (analysis / "ADR-20260827-001" / "competitor.marker").is_file()
        )
        self.assertEqual({"intake.json", "README.md"}, {path.name for path in run.iterdir()})
        self.assertEqual([], list(analysis.glob(".*.staging-*")))

    def test_atomic_run_publication_failure_leaves_no_run_or_staging_directory(self):
        harness = load_harness()

        with mock.patch("os.rename", side_effect=OSError("simulated rename failure")):
            with self.assertRaisesRegex(OSError, "simulated rename failure"):
                self.create_run(harness)

        analysis = self.brand / "outputs" / "ad-analysis"
        self.assertFalse((analysis / "ADR-20260827-001").exists())
        self.assertEqual([], list(analysis.glob(".*.staging-*")))

    def test_initialise_run_fsyncs_both_files_and_staging_then_parent_directories(self):
        harness = load_harness()
        real_fsync = os.fsync
        synced_modes = []

        def record_fsync(descriptor):
            synced_modes.append(os.fstat(descriptor).st_mode)
            return real_fsync(descriptor)

        with mock.patch("os.fsync", side_effect=record_fsync):
            self.create_run(harness)

        regular_syncs = sum(stat.S_ISREG(mode) for mode in synced_modes)
        directory_syncs = sum(stat.S_ISDIR(mode) for mode in synced_modes)
        self.assertGreaterEqual(regular_syncs, 2)
        self.assertGreaterEqual(directory_syncs, 2)

    def test_uses_the_current_brand_method_version_in_the_exact_skeleton(self):
        harness = load_harness()

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

    def test_rejects_datetime_today_before_creating_an_invalid_intake(self):
        harness = load_harness()

        with self.assertRaisesRegex(ValueError, "today must be a date"):
            harness.initialise_run(
                brand_folder=self.brand,
                mode="creative-audit",
                product_id="sleep-mask",
                market="AU",
                today=dt.datetime(2026, 8, 27, 14, 30),
            )

        self.assertFalse(
            (self.brand / "outputs/ad-analysis/ADR-20260827-001").exists()
        )

    def test_preserves_legacy_brand_version_and_records_migration_need(self):
        harness = load_harness()

        run = self.create_legacy_run(harness)

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

    def test_initialise_run_rejects_a_real_directory_brand_root_swap(self):
        harness = load_harness()
        original_brand = self.temp_root / "original-acme-sleep"
        replacement_brand = self.temp_root / "replacement-brand"
        load_initializer().initialise(
            replacement_brand, "Replacement Brand", "replacement-brand"
        )
        original_validate_method_version = harness._validate_method_version
        swapped = False

        def swap_brand_root(method_version):
            nonlocal swapped
            if not swapped:
                swapped = True
                self.brand.rename(original_brand)
                replacement_brand.rename(self.brand)
            return original_validate_method_version(method_version)

        with mock.patch.object(
            harness,
            "_validate_method_version",
            side_effect=swap_brand_root,
        ):
            with self.assertRaisesRegex(
                OSError, "brand directory changed during run initialisation"
            ):
                harness.initialise_run(
                    brand_folder=self.brand,
                    mode="creative-audit",
                    product_id="sleep-mask",
                    market="AU",
                    today=dt.date(2026, 8, 27),
                )

        self.assertFalse(
            (self.brand / "outputs/ad-analysis/ADR-20260827-001").exists()
        )
        self.assertFalse(
            (original_brand / "outputs/ad-analysis/ADR-20260827-001").exists()
        )

    def test_initialise_run_never_uses_a_swapped_analysis_directory(self):
        harness = load_harness()
        analysis_root = self.brand / "outputs/ad-analysis"
        moved_root = self.brand / "outputs/original-ad-analysis"
        outside = self.temp_root / "outside-analysis"
        outside.mkdir()
        original_limitations = harness._migration_limitations

        def swap_analysis_root(method_version):
            analysis_root.rename(moved_root)
            analysis_root.symlink_to(outside, target_is_directory=True)
            return original_limitations(method_version)

        with mock.patch.object(
            harness,
            "_migration_limitations",
            side_effect=swap_analysis_root,
        ):
            try:
                harness.initialise_run(
                    brand_folder=self.brand,
                    mode="creative-audit",
                    product_id="sleep-mask",
                    market="AU",
                    today=dt.date(2026, 8, 27),
                )
            except (OSError, ValueError):
                pass

        self.assertFalse(
            (outside / "ADR-20260827-001/intake.json").exists()
        )

    def test_initializer_cli_reports_an_unsafe_analysis_path_without_traceback(self):
        analysis_root = self.brand / "outputs/ad-analysis"
        analysis_root.rename(self.brand / "outputs/ad-analysis-template")
        analysis_root.write_text("not a directory\n")

        completed = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/init-ad-analysis-run.py"),
                str(self.brand),
                "--mode",
                "creative-audit",
                "--product-id",
                "sleep-mask",
                "--market",
                "AU",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("error:", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

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
        run = self.create_modern_run(harness)
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
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        self.write_intake(run, self.complete_performance_intake(harness, run))

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)

    def test_validation_result_is_immutable_and_uses_sorted_tuples(self):
        harness = load_harness()
        run = self.create_run(harness)

        result = harness.validate_run(self.brand, run)

        self.assertIsInstance(result, harness.ValidationResult)
        self.assertIsInstance(result.errors, tuple)
        self.assertIsInstance(result.limitations, tuple)
        self.assertIsInstance(result.inventory, tuple)
        self.assertEqual(tuple(sorted(result.errors)), result.errors)
        self.assertEqual(tuple(sorted(result.limitations)), result.limitations)
        with self.assertRaises((AttributeError, TypeError)):
            result.status = "ready"

    def test_blocks_creative_audit_without_ads_or_ad_identity_and_assets(self):
        harness = load_harness()
        run = self.create_run(harness)

        empty_result = harness.validate_run(self.brand, run)
        self.assertEqual("blocked", empty_result.status)
        self.assertIn("ads must contain at least one ad", empty_result.errors)

        intake = harness.load_intake(run)
        intake["ads"] = [{"ad_id": "", "asset_source_ids": []}]
        self.write_intake(run, intake)
        incomplete_result = harness.validate_run(self.brand, run)

        self.assertEqual("blocked", incomplete_result.status)
        self.assertIn("ads[0].ad_id must be non-empty text", incomplete_result.errors)
        self.assertIn(
            "ads[0].asset_source_ids must contain at least one source ID",
            incomplete_result.errors,
        )

    def test_limits_creative_audit_when_copy_destination_or_traceability_is_missing(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = harness.load_intake(run)
        intake["sources"] = [
            {
                "source_id": "SRC-001",
                "kind": "attachment",
                "label": "ad-one.mp4",
                "location": "attached:ad-one.mp4",
                "sha256": None,
            }
        ]
        intake["ads"] = [
            {
                "ad_id": "AD-001",
                "asset_source_ids": ["SRC-001"],
                "asset_type": None,
                "primary_text": None,
                "headline": None,
                "description": None,
                "cta": None,
                "destination_url": None,
                "destination_type": None,
                "coordinate_key": None,
                "contst": None,
                "source": None,
                "who": None,
                "primary_problem": None,
                "awareness_code": None,
                "messaging_route": None,
                "format": None,
                "primary_hook": None,
                "post_id": None,
            }
        ]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn("ads[0] copy is unavailable", result.limitations)
        self.assertIn("ads[0] destination is unavailable", result.limitations)
        self.assertIn("ads[0] strategic traceability is unavailable", result.limitations)

    def test_known_migration_need_limits_but_does_not_block_analysis(self):
        harness = load_harness()
        run = self.create_legacy_run(harness)
        self.write_intake(run, self.complete_creative_intake(harness, run))

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn(
            "Brand method version 0.3.0 requires reviewed migration before controlled persistence.",
            result.limitations,
        )

    def test_validator_derives_migration_need_from_the_brand_version(self):
        harness = load_harness()
        run = self.create_legacy_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["known_limitations"] = []
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn(
            "Brand method version 0.3.0 requires reviewed migration before controlled persistence.",
            result.limitations,
        )

    def test_performance_required_fields_each_block_diagnosis(self):
        harness = load_harness()
        required_cases = (
            ("source_ids", "performance sources are required"),
            ("date_range", "performance.date_range is required"),
            ("attribution", "performance.attribution is required"),
            ("currency", "performance.currency is required"),
            ("aggregation_level", "performance.aggregation_level is required"),
            ("field_mapping.ad_id", "performance.field_mapping.ad_id is required"),
            ("field_mapping.spend", "performance.field_mapping.spend is required"),
            ("field_mapping.purchases", "performance.field_mapping.purchases is required"),
            (
                "ad_mapping",
                "performance.ad_mapping must contain at least one spend-bearing source ad",
            ),
        )

        for field, expected in required_cases:
            with self.subTest(field=field):
                run = self.create_modern_run(harness, mode="performance-diagnosis")
                intake = self.complete_performance_intake(harness, run)
                if field.startswith("field_mapping."):
                    del intake["performance"]["field_mapping"][field.rsplit(".", 1)[1]]
                elif field == "ad_mapping":
                    intake["performance"][field] = {}
                else:
                    del intake["performance"][field]
                self.write_intake(run, intake)

                result = harness.validate_run(self.brand, run)

                self.assertEqual("blocked", result.status)
                self.assertIn(expected, result.errors)

    def test_missing_optional_funnel_and_video_mappings_limit_diagnosis(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        intake = self.complete_performance_intake(harness, run)
        del intake["performance"]["field_mapping"]["landing_page_views"]
        del intake["performance"]["field_mapping"]["video_3_second_plays"]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("limited", result.status)
        self.assertIn("optional funnel field mappings are unavailable", result.limitations)
        self.assertIn("optional video field mappings are unavailable", result.limitations)

    def test_frozen_performance_diagnosis_intake_and_audit_are_validator_backed(self):
        for label, path in DIAGNOSIS_FIXTURES.items():
            self.assertTrue(path.is_file(), f"frozen diagnosis {label} fixture should exist")

        harness = load_harness()
        brand = self.temp_root / "quiet-arc"
        load_initializer().initialise(brand, "Quiet Arc", "quiet-arc")
        run = harness.initialise_run(
            brand_folder=brand,
            mode="performance-diagnosis",
            product_id="folding-reading-lamp",
            market="AU",
            run_id="ADR-20260827-015",
            today=dt.date(2026, 8, 27),
        )
        intake = json.loads(DIAGNOSIS_FIXTURES["intake"].read_text())
        (run / "intake.json").write_text(json.dumps(intake, indent=2) + "\n")
        (run / DIAGNOSIS_FIXTURES["performance"].name).write_bytes(
            DIAGNOSIS_FIXTURES["performance"].read_bytes()
        )

        result = harness.validate_run(brand, run)

        self.assertEqual("limited", result.status)
        self.assertEqual((), result.errors)
        self.assertEqual(
            (
                "First-frame retention was not supplied for video ads; opening-frame claims are limited.",
            ),
            result.limitations,
        )
        self.maxDiff = None
        self.assertEqual(
            DIAGNOSIS_FIXTURES["audit"].read_text(),
            harness.render_input_audit(intake, result),
        )

    def test_frozen_performance_diagnosis_reconciles_every_supplied_value(self):
        for label in ("intake", "performance", "report"):
            self.assertTrue(
                DIAGNOSIS_FIXTURES[label].is_file(),
                f"frozen diagnosis {label} fixture should exist",
            )
        intake = json.loads(DIAGNOSIS_FIXTURES["intake"].read_text())
        report = DIAGNOSIS_FIXTURES["report"].read_text()
        with DIAGNOSIS_FIXTURES["performance"].open(newline="") as file:
            supplied = list(csv.DictReader(file))

        self.assertEqual(4, len(supplied))
        performance = intake["performance"]
        start = dt.date.fromisoformat(performance["date_range"]["start"])
        end = dt.date.fromisoformat(performance["date_range"]["end"])
        self.assertEqual(5, (end - start).days + 1)
        spend_bearing = {
            row["Ad name"] for row in supplied if float(row["Amount spent (AUD)"]) > 0
        }
        self.assertEqual(
            {ad_name: ad_name for ad_name in spend_bearing},
            performance["ad_mapping"],
        )
        self.assertEqual(spend_bearing, {ad["ad_id"] for ad in intake["ads"]})
        for mapped_column in performance["field_mapping"].values():
            self.assertIn(mapped_column, supplied[0])

        naming = re.compile(
            r"^CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_"
            r"(?P<awareness>UWA|PRA|SLA|PDA)_"
            r"(?P<format>VSL|STATIC|COMPARISON)_"
            r"(?P<destination>LP|PDP)_(?P<post_id>\d+)$"
        )
        governed_names = {row["Ad name"]: naming.fullmatch(row["Ad name"]) for row in supplied}
        self.assertTrue(all(governed_names.values()))
        self.assertEqual(
            {"UWA", "PRA", "SLA", "PDA"},
            {match.group("awareness") for match in governed_names.values()},
        )
        for match in governed_names.values():
            expected_destination = (
                "LP" if match.group("awareness") in {"UWA", "PRA"} else "PDP"
            )
            self.assertEqual(expected_destination, match.group("destination"))

        self.assertEqual(320.0, sum(float(row["Amount spent (AUD)"]) for row in supplied))
        self.assertEqual(3, sum(int(row["Purchases"]) for row in supplied))
        self.assertEqual(357.0, sum(float(row["Purchase value (AUD)"]) for row in supplied))
        self.assertEqual({"60"}, {row["Target CAC (AUD)"] for row in supplied})
        self.assertEqual({"300"}, {row["Minimum batch spend (AUD)"] for row in supplied})
        self.assertEqual({"6"}, {row["Minimum batch purchases"] for row in supplied})
        self.assertNotIn("First-frame retention", supplied[0])

        tested_rows = markdown_table(
            report,
            "## 2. What was tested",
            "## 3. What happened: business result",
        )
        business_rows = markdown_table(
            report,
            "## 3. What happened: business result",
            "## 4. What happened: funnel result",
        )
        funnel_rows = markdown_table(
            report,
            "## 4. What happened: funnel result",
            "## 5. What happened: creative result",
        )
        creative_rows = markdown_table(
            report,
            "## 5. What happened: creative result",
            "## 6. Strongest and weakest complete executions",
        )
        decision_rows = markdown_table(
            report,
            "## 8. Six-decision taxonomy",
            "## 9. Ranked change list",
        )
        for rows in (
            tested_rows,
            business_rows,
            funnel_rows,
            creative_rows,
            decision_rows,
        ):
            self.assertEqual(spend_bearing, {row["Full ad name"].strip("`") for row in rows})
            self.assertEqual(4, len(rows))
        for row in tested_rows:
            self.assertEqual("`CONTST042`", row["Existing test"])
            self.assertEqual("NNT", row["Source"])
            match = governed_names[row["Full ad name"].strip("`")]
            self.assertEqual(match.group("awareness"), row["Awareness"])
            self.assertEqual(match.group("destination"), row["Destination"])
        self.assertIn("`QUIETARC_READINGLAMP_CT_ABO_AU_20260820`", report)
        self.assertIn("`CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE`", report)
        self.assertRegex(
            report,
            r"no\s+Destination Handoff exception is applicable",
        )

        source_by_name = {row["Ad name"]: row for row in supplied}
        business_by_name = {row["Full ad name"].strip("`"): row for row in business_rows}
        funnel_by_name = {row["Full ad name"].strip("`"): row for row in funnel_rows}
        creative_by_name = {row["Full ad name"].strip("`"): row for row in creative_rows}
        for ad_name, source in source_by_name.items():
            with self.subTest(ad_name=ad_name):
                business = business_by_name[ad_name]
                funnel = funnel_by_name[ad_name]
                creative = creative_by_name[ad_name]
                spend = float(source["Amount spent (AUD)"])
                purchases = int(source["Purchases"])
                target_cac = float(source["Target CAC (AUD)"])
                self.assertEqual(f"`${source['Amount spent (AUD)']}`", business["Spend"])
                self.assertEqual(f"`{source['Purchases']}`", business["Purchases"])
                self.assertEqual(f"`${source['Purchase value (AUD)']}`", business["Revenue"])
                self.assertEqual(f"`{100 * spend / 320:.2f}%`", business["Spend share"])
                self.assertEqual(
                    f"`{spend / target_cac:.2f}`",
                    business["Expected purchases at target"],
                )
                if purchases:
                    cac = spend / purchases
                    self.assertEqual(
                        f"`${cac:.0f}`, `${cac - target_cac:.0f}` above target",
                        business["CAC vs `$60` target"],
                    )
                else:
                    self.assertEqual(
                        "unavailable; no purchases", business["CAC vs `$60` target"]
                    )

                impressions = int(source["Impressions"])
                clicks = int(source["Outbound clicks"])
                views = int(source["Landing page views"])
                carts = int(source["Adds to cart"])
                checkouts = int(source["Initiates checkout"])
                funnel_expectations = {
                    "Outbound CTR": f"`{100 * clicks / impressions:.2f}%` (`{clicks:,}/{impressions:,}`)",
                    "Landing-page-view rate": f"`{100 * views / clicks:.2f}%` (`{views:,}/{clicks:,}`)",
                    "Add-to-cart rate": f"`{100 * carts / views:.2f}%` (`{carts:,}/{views:,}`)",
                    "Checkout rate": f"`{100 * checkouts / carts:.2f}%` (`{checkouts:,}/{carts:,}`)",
                    "Purchase rate": (
                        f"`{100 * purchases / checkouts:.2f}%` (`{purchases:,}/{checkouts:,}`)"
                        if checkouts
                        else "unavailable; no checkout"
                    ),
                }
                for field, expected in funnel_expectations.items():
                    self.assertEqual(expected, funnel[field])

                self.assertEqual(f"`{source['Frequency']}`", creative["Frequency"])
                self.assertEqual(
                    f"`{100 * spend / 320:.2f}%`", creative["Spend share"]
                )
                self.assertEqual(
                    f"{source['Positive comments']} positive, "
                    f"{source['Delivery questions']} delivery question",
                    creative["Comments"],
                )
                if source["3-second video plays"]:
                    thumbstop = 100 * int(source["3-second video plays"]) / int(source["Impressions"])
                    hold = 100 * int(source["50% video plays"]) / int(source["3-second video plays"])
                    self.assertEqual(f"`{thumbstop:.2f}%`", creative["Thumbstop"])
                    self.assertEqual(
                        f"`{thumbstop:.2f}%` "
                        f"(`{int(source['3-second video plays']):,}/{impressions:,}`)",
                        creative["Three-second view rate"],
                    )
                    self.assertEqual(
                        f"`{hold:.2f}%` "
                        f"(`{int(source['50% video plays']):,}/"
                        f"{int(source['3-second video plays']):,}`)",
                        creative["Hold rate"],
                    )
                    self.assertEqual("unavailable", creative["First-frame retention"])
                else:
                    self.assertEqual(
                        "not applicable to static", creative["Three-second view rate"]
                    )
                    self.assertEqual("not applicable to static", creative["Thumbstop"])
                    self.assertEqual("not applicable to static", creative["Hold rate"])
                    self.assertEqual(
                        "not applicable to static", creative["First-frame retention"]
                    )

        allowed_actions = {"`keep`", "`ITR`", "`stop`", "`scale`"}
        for row in decision_rows:
            self.assertIn(row["Top-level action"], allowed_actions)
        uwa_name = next(name for name in spend_bearing if "_UWA_" in name)
        uwa_source = source_by_name[uwa_name]
        self.assertGreater(
            float(uwa_source["Amount spent (AUD)"]) / int(uwa_source["Purchases"]),
            float(uwa_source["Target CAC (AUD)"]),
        )
        uwa_decision = next(
            row for row in decision_rows if row["Full ad name"].strip("`") == uwa_name
        )
        self.assertEqual("Directional promise", uwa_decision["Decision"])
        self.assertEqual("`ITR`", uwa_decision["Top-level action"])

        summary = report.split("## Persistence Summary", 1)[1]
        for field in (
            "Proposed observation:",
            "Evidence:",
            "Explanation confidence:",
            "Verdict:",
            "Next action:",
        ):
            self.assertIn(field, summary)
        self.assertIn("Winner-library proposal: none", summary)
        self.assertIn("Graduation confirmation: not supplied", summary)
        self.assertIn("CONTST: unreserved — human decision required", summary)
        self.assertIn("Upload-only status: patch only; persistence not claimed", summary)

    def test_performance_mapping_can_omit_an_unserved_intake_ad(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        intake = self.complete_performance_intake(harness, run)
        intake["ads"].append(
            {
                "ad_id": "AD-002",
                "asset_source_ids": ["SRC-001"],
                "asset_type": "static",
                "primary_text": "Second ad",
                "headline": "Rest",
                "description": "",
                "cta": "Shop now",
                "destination_url": "https://example.test/sleep-mask",
                "destination_type": "PDP",
                "coordinate_key": "travellers|dark",
                "contst": "CONTST001",
                "source": "NNT",
                "who": "Light-sensitive travellers",
                "primary_problem": "Hotel light interrupts sleep",
                "awareness_code": "PDA",
                "messaging_route": "Choose darkness",
                "format": "STATIC",
                "primary_hook": "Sleep anywhere",
                "post_id": None,
            }
        )
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)
        self.assertFalse(any("AD-002" in error for error in result.errors))

    def test_rejects_duplicate_source_and_ad_ids_and_unknown_references(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = harness.load_intake(run)
        source = {
            "source_id": "SRC-001",
            "kind": "attachment",
            "label": "ad-one.mp4",
            "location": "attached:ad-one.mp4",
            "sha256": None,
        }
        intake["sources"] = [source, dict(source)]
        intake["ads"] = [
            {"ad_id": "AD-001", "asset_source_ids": ["SRC-404"]},
            {"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]},
        ]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertIn("sources[1].source_id duplicates SRC-001", result.errors)
        self.assertIn("ads[1].ad_id duplicates AD-001", result.errors)
        self.assertIn(
            "ads[0].asset_source_ids references unknown source SRC-404", result.errors
        )

    def test_rejects_unknown_keys_at_each_structured_level(self):
        harness = load_harness()
        run = self.create_modern_run(harness, mode="performance-diagnosis")
        intake = self.complete_performance_intake(harness, run)
        intake["surprise"] = True
        intake["sources"][0]["surprise"] = True
        intake["ads"][0]["surprise"] = True
        intake["performance"]["surprise"] = True
        intake["performance"]["date_range"]["surprise"] = True
        intake["performance"]["field_mapping"]["surprise"] = True
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        for error in (
            "surprise is not allowed",
            "sources[0].surprise is not allowed",
            "ads[0].surprise is not allowed",
            "performance.surprise is not allowed",
            "performance.date_range.surprise is not allowed",
            "performance.field_mapping.surprise is not allowed",
        ):
            with self.subTest(error=error):
                self.assertIn(error, result.errors)

    def test_rejects_and_redacts_a_credential_fingerprint_in_intake(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        credential = "ghp_" + "A" * 36
        intake["sources"][0]["label"] = credential
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)
        audit = harness.render_input_audit(intake, result)

        self.assertEqual("blocked", result.status)
        self.assertIn(
            "sources[0].label must not contain a credential or access token",
            result.errors,
        )
        self.assertNotIn(credential, audit)
        self.assertIn('"[REDACTED]"', audit)

    def test_validation_result_redacts_credentials_in_unknown_keys_and_references(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        unknown_key_credential = "github_pat_" + "K" * 60
        reference_credential = "ghp_" + "R" * 36
        intake[unknown_key_credential] = "unexpected"
        intake["ads"][0]["asset_source_ids"] = [reference_credential]
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)
        outward_result = json.dumps(result._asdict(), ensure_ascii=False)
        audit = harness.render_input_audit(intake, result)

        self.assertEqual("blocked", result.status)
        for credential in (unknown_key_credential, reference_credential):
            with self.subTest(credential=credential):
                self.assertNotIn(credential, outward_result)
                self.assertNotIn(credential, audit)
        self.assertIn("[REDACTED]", outward_result)

    def test_validator_cli_redacts_credentials_in_unknown_keys_and_references(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        unknown_key_credential = "github_pat_" + "K" * 60
        reference_credential = "ghp_" + "R" * 36
        intake[unknown_key_credential] = "unexpected"
        intake["ads"][0]["asset_source_ids"] = [reference_credential]
        self.write_intake(run, intake)

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        audit = (run / "input-audit.md").read_text()

        self.assertEqual(1, completed.returncode)
        outward_diagnostics = completed.stdout + completed.stderr + audit
        for credential in (unknown_key_credential, reference_credential):
            with self.subTest(credential=credential):
                self.assertNotIn(credential, outward_diagnostics)
        self.assertIn("[REDACTED]", completed.stdout)

    def test_rejects_and_redacts_every_supported_secret_form_before_results(self):
        harness = load_harness()
        private_key = (
            "-----BEGIN PRIVATE KEY-----\n"
            "PRIVATE-MATERIAL-ALPHA\n"
            "-----END PRIVATE KEY-----"
        )
        cases = (
            (
                "generic password assignment",
                lambda intake: intake["sources"][0].__setitem__(
                    "label", "db_password = ordinary-password-value"
                ),
                "sources[0].label",
                ("ordinary-password-value",),
            ),
            (
                "URL userinfo and sensitive query",
                lambda intake: intake["ads"][0].__setitem__(
                    "destination_url",
                    "https://joe:ordinary-pass@example.test/buy?token=query-secret-value",
                ),
                "ads[0].destination_url",
                ("ordinary-pass", "query-secret-value"),
            ),
            (
                "bearer token",
                lambda intake: intake["ads"][0].__setitem__(
                    "primary_text", "Use Bearer ordinary-bearer-token to continue"
                ),
                "ads[0].primary_text",
                ("ordinary-bearer-token",),
            ),
            (
                "complete private key",
                lambda intake: intake["sources"][0].__setitem__("label", private_key),
                "sources[0].label",
                ("PRIVATE-MATERIAL-ALPHA", "-----END PRIVATE KEY-----"),
            ),
            (
                "credential-like structural key",
                lambda intake: intake.__setitem__(
                    "integration", {"db_password": "ordinary-structural-value"}
                ),
                "integration.db_password",
                ("ordinary-structural-value",),
            ),
        )

        for name, change, error_path, raw_values in cases:
            with self.subTest(name=name):
                run = self.create_run(harness)
                intake = self.complete_creative_intake(harness, run)
                change(intake)
                self.write_intake(run, intake)

                result = harness.validate_run(self.brand, run)
                outward_result = json.dumps(result._asdict(), ensure_ascii=False)
                audit = harness.render_input_audit(intake, result)
                with harness._open_validation_session(self.brand, run) as session:
                    sanitized_intake = json.dumps(
                        session.intake, ensure_ascii=False
                    )

                self.assertEqual("blocked", result.status)
                self.assertIn(
                    f"{error_path} must not contain a credential or access token",
                    result.errors,
                )
                for raw_value in raw_values:
                    self.assertNotIn(raw_value, outward_result)
                    self.assertNotIn(raw_value, audit)
                    self.assertNotIn(raw_value, sanitized_intake)
                self.assertIn("[REDACTED]", sanitized_intake)

    def test_public_intake_loader_rejects_before_returning_a_secret_field(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0]["label"] = "db_password=loader-secret-value"
        self.write_intake(run, intake)

        with self.assertRaisesRegex(ValueError, "sources\[0\]\.label") as raised:
            harness.load_intake(run)

        self.assertNotIn("loader-secret-value", str(raised.exception))

    def test_validator_cli_rejects_and_redacts_a_generic_password_assignment(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        secret = "generic-cli-password-value"
        intake["sources"][0]["label"] = f"database_password = {secret}"
        self.write_intake(run, intake)

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        audit = (run / "input-audit.md").read_text()

        self.assertEqual(1, completed.returncode)
        self.assertNotIn(secret, completed.stdout + completed.stderr + audit)
        self.assertIn("[REDACTED]", completed.stdout + audit)

    def test_rejects_unknown_keys_in_optional_creative_mode_performance_metadata(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["performance"] = {
            "surprise": True,
            "source_ids": "SRC-002",
            "date_range": {"surprise": True},
            "field_mapping": {"surprise": True},
            "logged_interventions": "none",
        }
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertIn("performance.surprise is not allowed", result.errors)
        self.assertIn("performance.date_range.surprise is not allowed", result.errors)
        self.assertIn("performance.field_mapping.surprise is not allowed", result.errors)
        self.assertIn("performance.source_ids must be an array", result.errors)
        self.assertIn("performance.logged_interventions must be an array", result.errors)

    def test_rejects_local_file_traversal_absolute_paths_and_url_disguises(self):
        harness = load_harness()
        unsafe_locations = (
            ("../outside.mp4", "must not contain '..' traversal"),
            (str(self.temp_root / "outside.mp4"), "must be a relative path"),
            ("https://example.test/ad.mp4", "must not be a URL"),
        )

        for location, expected in unsafe_locations:
            with self.subTest(location=location):
                run = self.create_run(harness)
                intake = harness.load_intake(run)
                intake["sources"] = [
                    {
                        "source_id": "SRC-001",
                        "kind": "file",
                        "label": "ad-one.mp4",
                        "location": location,
                        "sha256": None,
                    }
                ]
                intake["ads"] = [
                    {"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]}
                ]
                self.write_intake(run, intake)

                result = harness.validate_run(self.brand, run)

                self.assertIn(f"sources[0].location {expected}", result.errors)

    def test_absolute_attachment_label_is_external_and_is_not_read(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0]["location"] = "/external/upload/ad-one.mp4"
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)
        self.assertFalse(any("location" in error for error in result.errors))

    def test_hashes_safe_local_files_without_mutating_intake(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        (run / "ad-one.mp4").write_bytes(b"trusted only as bytes")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)
        before = (run / "intake.json").read_bytes()

        result = harness.validate_run(self.brand, run)

        self.assertEqual("ready", result.status)
        self.assertEqual(before, (run / "intake.json").read_bytes())
        self.assertEqual(
            (
                (
                    "SRC-001",
                    "file",
                    "ad-one.mp4",
                    "ad-one.mp4",
                    "1d61ea2522ceb2b08423452be93795e189b4c2f06cc8f3776eba4c1ff0069780",
                ),
            ),
            result.inventory,
        )

    def test_rejects_hardlinked_local_sources(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        outside = self.temp_root / "outside-ad.mp4"
        outside.write_bytes(b"outside brand bytes")
        os.link(outside, run / "ad-one.mp4")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        self.assertEqual("blocked", result.status)
        self.assertIn(
            "sources[0].location must have exactly one hard link", result.errors
        )
        self.assertEqual("", result.inventory[0][4])

    def test_rejects_local_sources_that_change_while_hashed(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        asset = run / "ad-one.mp4"
        asset.write_bytes((b"a" * (1024 * 1024)) + (b"b" * (1024 * 1024)))
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)
        asset_identity = (asset.stat().st_dev, asset.stat().st_ino)
        original_read = harness.os.read
        mutated = False

        def mutate_after_first_asset_chunk(descriptor, size):
            nonlocal mutated
            content = original_read(descriptor, size)
            metadata = os.fstat(descriptor)
            if (metadata.st_dev, metadata.st_ino) == asset_identity and not mutated:
                mutated = True
                with asset.open("r+b") as file:
                    file.seek(0)
                    file.write(b"changed")
                    file.flush()
                    os.fsync(file.fileno())
            return content

        with mock.patch.object(harness.os, "read", side_effect=mutate_after_first_asset_chunk):
            result = harness.validate_run(self.brand, run)

        self.assertTrue(mutated)
        self.assertEqual("blocked", result.status)
        self.assertIn(
            "sources[0].location changed while it was being read", result.errors
        )
        self.assertEqual("", result.inventory[0][4])

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

        for name in imported - {"__future__", "content_safety", "scripts"}:
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

        safety_tree = ast.parse(CONTENT_SAFETY.read_text())
        safety_imports = set()
        for node in ast.walk(safety_tree):
            if isinstance(node, ast.Import):
                safety_imports.update(
                    alias.name.split(".")[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                safety_imports.add(node.module.split(".")[0])
        for name in safety_imports - {"__future__"}:
            with self.subTest(content_safety_module=name):
                self.assertTrue(is_standard_library_module(name))

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

    def test_rejects_non_string_values_instead_of_coercing_them(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["schema_version"] = "1"
        intake["market"] = 61
        intake["sources"][0]["kind"] = 1
        intake["ads"][0]["destination_type"] = 7
        self.write_intake(run, intake)

        result = harness.validate_run(self.brand, run)

        for error in (
            "schema_version must equal integer 1",
            "market must be non-empty text",
            "sources[0].kind must be one of: attachment, file, screenshot, table, url",
            "ads[0].destination_type must be null or one of: CP, HP, LP, PDP",
        ):
            with self.subTest(error=error):
                self.assertIn(error, result.errors)

    def test_rejects_list_and_object_source_kinds_without_raising(self):
        harness = load_harness()

        for kind in ([], {}):
            with self.subTest(kind=kind):
                run = self.create_run(harness)
                intake = harness.load_intake(run)
                intake["sources"] = [
                    {
                        "source_id": "SRC-001",
                        "kind": kind,
                        "label": "ad-one.mp4",
                        "location": "attached:ad-one.mp4",
                        "sha256": None,
                    }
                ]
                intake["ads"] = [
                    {"ad_id": "AD-001", "asset_source_ids": ["SRC-001"]}
                ]
                self.write_intake(run, intake)

                try:
                    result = harness.validate_run(self.brand, run)
                except Exception as error:
                    self.fail(f"validate_run raised {type(error).__name__}: {error}")

                self.assertEqual("blocked", result.status)
                self.assertIn(
                    "sources[0].kind must be one of: attachment, file, screenshot, table, url",
                    result.errors,
                )

    def test_local_source_read_never_uses_a_swapped_parent_directory(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        asset_parent = run / "assets"
        asset_parent.mkdir()
        (asset_parent / "ad-one.mp4").write_bytes(b"inside")
        outside_parent = self.temp_root / "outside-assets"
        outside_parent.mkdir()
        (outside_parent / "ad-one.mp4").write_bytes(b"outside")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "assets/ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)
        checked_file = asset_parent / "ad-one.mp4"
        original_open = harness.os.open
        swapped = False

        def swap_parent_before_file_open(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal swapped
            is_path_open = dir_fd is None and pathlib.Path(path) == checked_file
            is_anchored_open = dir_fd is not None and path == "ad-one.mp4"
            if (is_path_open or is_anchored_open) and not swapped:
                swapped = True
                asset_parent.rename(run / "original-assets")
                asset_parent.symlink_to(outside_parent, target_is_directory=True)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with mock.patch.object(
            harness, "_no_follow_flag", return_value=os.O_NOFOLLOW
        ), mock.patch.object(
            harness.os, "open", side_effect=swap_parent_before_file_open
        ):
            result = harness.validate_run(self.brand, run)

        outside_digest = "31207a2065f46a5b948fce6fe5c13e85abaf5631e2f894b47dcd4fce14f6c57b"
        self.assertNotEqual(outside_digest, result.inventory[0][4])

    def test_local_source_validation_fails_closed_without_no_follow_support(self):
        harness = load_harness()
        run = self.create_modern_run(harness)
        (run / "ad-one.mp4").write_bytes(b"inside")
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0].update(
            {"kind": "file", "location": "ad-one.mp4", "sha256": None}
        )
        self.write_intake(run, intake)

        with mock.patch.object(harness.os, "O_NOFOLLOW", None):
            try:
                result = harness.validate_run(self.brand, run)
            except Exception as error:
                self.fail(f"validate_run raised {type(error).__name__}: {error}")

        self.assertEqual("blocked", result.status)
        self.assertIn(
            "descriptor-anchored no-follow access is unavailable",
            result.errors,
        )

    def test_rejects_a_run_folder_outside_the_brand(self):
        harness = load_harness()
        canonical_run = self.create_run(harness)
        outside_run = self.temp_root / canonical_run.name
        outside_run.mkdir()
        self.write_intake(outside_run, harness.load_intake(canonical_run))

        result = harness.validate_run(self.brand, outside_run)

        self.assertEqual("blocked", result.status)
        self.assertIn("run folder must be inside the brand folder", result.errors)

    def test_validate_run_rejects_a_noncanonical_folder_inside_the_brand(self):
        harness = load_harness()
        canonical_run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, canonical_run)
        noncanonical_run = self.brand / "outputs" / "manual" / canonical_run.name
        noncanonical_run.mkdir(parents=True)
        self.write_intake(noncanonical_run, intake)

        result = harness.validate_run(self.brand, noncanonical_run)

        self.assertEqual("blocked", result.status)
        self.assertIn(
            "run folder must be outputs/ad-analysis/<RUN_ID>", result.errors
        )

    def test_validator_never_publishes_an_audit_after_run_directory_replacement(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        self.write_intake(run, intake)

        replacement = run.parent / ".replacement-run"
        replacement.mkdir()
        replacement_intake = copy.deepcopy(intake)
        replacement_intake["ads"][0]["ad_id"] = "AD-REPLACEMENT"
        self.write_intake(replacement, replacement_intake)
        original_run = run.parent / ".original-run"
        original_write = validator._write_input_audit
        swapped = False

        def swap_run_then_publish(*args, **kwargs):
            nonlocal swapped
            run.rename(original_run)
            replacement.rename(run)
            swapped = True
            return original_write(*args, **kwargs)

        arguments = mock.Mock(brand=self.brand, run=run, write_audit=True)
        with mock.patch.object(validator, "_arguments", return_value=arguments), mock.patch.object(
            validator, "_write_input_audit", side_effect=swap_run_then_publish
        ):
            return_code = validator.main()

        self.assertTrue(swapped)
        self.assertEqual(1, return_code)
        self.assertFalse((run / "input-audit.md").exists())
        self.assertFalse((original_run / "input-audit.md").exists())

    def test_renders_a_deterministic_input_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = harness.load_intake(run)

        first = harness.render_input_audit(intake, harness.validate_run(self.brand, run))
        second = harness.render_input_audit(intake, harness.validate_run(self.brand, run))

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("# Ad analysis input audit\n"))
        headings = (
            "## Run identity",
            "## Source inventory",
            "## Ad coverage",
            "## Performance coverage",
            "## Readiness",
            "## Errors",
            "## Limitations",
        )
        positions = [first.index(heading) for heading in headings]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Input readiness: `blocked`", first)

    def test_validator_cli_prints_issues_and_writes_only_the_input_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake_before = (run / "intake.json").read_bytes()
        controlled_before = {
            relative: (self.brand / relative).read_bytes()
            for relative in CONTROLLED_RECORDS
        }

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertIn("Input readiness: blocked", completed.stdout)
        self.assertIn("ads must contain at least one ad", completed.stdout)
        self.assertTrue((run / "input-audit.md").is_file())
        self.assertEqual(intake_before, (run / "intake.json").read_bytes())
        self.assertEqual(
            controlled_before,
            {
                relative: (self.brand / relative).read_bytes()
                for relative in CONTROLLED_RECORDS
            },
        )

    def test_validator_cli_audits_malformed_json_without_a_traceback(self):
        harness = load_harness()
        run = self.create_run(harness)
        (run / "intake.json").write_text("{not-json\n")

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertIn("Input readiness: blocked", completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertTrue((run / "input-audit.md").is_file())

    def test_validator_cli_encodes_unpaired_surrogates_before_truncating_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["sources"][0]["label"] = "ad-\ud800.mp4"
        self.write_intake(run, intake)
        audit = run / "input-audit.md"
        audit.write_text("existing audit\n")

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            errors="backslashreplace",
            check=False,
        )

        self.assertEqual(0, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn(b"ad-\\ud800.mp4", audit.read_bytes())
        self.assertGreater(audit.stat().st_size, 0)

    def test_validator_cli_safely_prints_surrogate_errors_and_writes_the_audit(self):
        harness = load_harness()
        run = self.create_run(harness)
        intake = self.complete_creative_intake(harness, run)
        intake["unexpected-\ud800"] = True
        self.write_intake(run, intake)

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            errors="backslashreplace",
            check=False,
        )
        audit = run / "input-audit.md"

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("unexpected-\\ud800 is not allowed", completed.stdout)
        self.assertTrue(audit.is_file())
        self.assertIn(b"unexpected-\\ud800 is not allowed", audit.read_bytes())

    def test_validator_cli_refuses_a_symlinked_audit_target(self):
        harness = load_harness()
        run = self.create_run(harness)
        controlled = self.brand / CONTROLLED_RECORDS[0]
        before = controlled.read_bytes()
        (run / "input-audit.md").symlink_to(controlled)

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("input audit was not written", completed.stdout)
        self.assertEqual(before, controlled.read_bytes())

    def test_validator_cli_refuses_a_hardlinked_audit_target(self):
        harness = load_harness()
        run = self.create_run(harness)
        controlled = self.brand / CONTROLLED_RECORDS[0]
        before = controlled.read_bytes()
        os.link(controlled, run / "input-audit.md")

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("input audit was not written", completed.stdout)
        self.assertEqual(before, controlled.read_bytes())

    def test_validator_cli_writes_audits_only_to_canonical_run_folders(self):
        run = self.brand / "strategy"
        audit = run / "input-audit.md"

        completed = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.brand),
                str(run),
                "--write-audit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("input audit was not written", completed.stdout)
        self.assertFalse(audit.exists())

    def test_audit_write_never_uses_a_swapped_parent_directory(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_run(harness)
        outside = self.temp_root / "outside-run"
        outside.mkdir()
        audit_path = run / "input-audit.md"
        original_open = validator.os.open
        swapped = False

        def swap_parent_before_audit_open(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal swapped
            is_path_open = dir_fd is None and pathlib.Path(path) == audit_path
            is_anchored_open = dir_fd is not None and path == "input-audit.md"
            if (is_path_open or is_anchored_open) and not swapped:
                swapped = True
                run.rename(run.parent / "original-run")
                run.symlink_to(outside, target_is_directory=True)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with mock.patch.object(
            harness, "_no_follow_flag", return_value=os.O_NOFOLLOW
        ), mock.patch.object(
            validator, "_no_follow_flag", return_value=os.O_NOFOLLOW
        ), mock.patch.object(
            validator.os, "open", side_effect=swap_parent_before_audit_open
        ):
            try:
                validator._write_input_audit(audit_path, "audit\n")
            except OSError:
                pass

        self.assertFalse((outside / "input-audit.md").exists())

    def test_audit_write_fails_closed_without_no_follow_support(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_run(harness)

        with mock.patch.object(validator.os, "O_NOFOLLOW", None):
            try:
                validator._write_input_audit(run / "input-audit.md", "audit\n")
            except OSError:
                pass
            except Exception as error:
                self.fail(f"audit write raised {type(error).__name__}: {error}")
            else:
                self.fail("audit write did not fail closed")

    def test_validator_rejects_staging_substitution_at_audit_replace_boundary(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_modern_run(harness)
        intake = self.complete_creative_intake(harness, run)
        self.write_intake(run, intake)
        audit = run / "input-audit.md"
        audit.write_text("previous safe audit\n")
        real_replace = os.replace
        substituted = False

        def substitute_then_replace(source, destination, *args, **kwargs):
            nonlocal substituted
            source_directory = kwargs["src_dir_fd"]
            if not substituted:
                substituted = True
                os.unlink(source, dir_fd=source_directory)
                attacker = os.open(
                    source,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=source_directory,
                )
                try:
                    os.write(attacker, b"attacker-controlled audit\n")
                finally:
                    os.close(attacker)
            return real_replace(source, destination, *args, **kwargs)

        arguments = mock.Mock(brand=self.brand, run=run, write_audit=True)
        with mock.patch.object(
            validator, "_arguments", return_value=arguments
        ), mock.patch.object(
            validator.os, "replace", side_effect=substitute_then_replace
        ):
            return_code = validator.main()

        self.assertTrue(substituted)
        self.assertEqual(1, return_code)
        self.assertFalse(audit.exists(), "failed CLI left an unrelated audit")

    def test_audit_staging_name_is_fresh_for_each_publication(self):
        harness = load_harness()
        validator = load_validator(harness)
        run = self.create_run(harness)
        audit = run / "input-audit.md"
        real_replace = os.replace
        staging_names = []

        def capture_staging_name(source, destination, *args, **kwargs):
            staging_names.append(source)
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            validator.os, "replace", side_effect=capture_staging_name
        ):
            validator._write_input_audit(audit, "first audit\n")
            validator._write_input_audit(audit, "second audit\n")

        self.assertEqual(2, len(staging_names))
        self.assertEqual(2, len(set(staging_names)))


if __name__ == "__main__":
    unittest.main()
