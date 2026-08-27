#!/usr/bin/env python3
"""Build a compact brand knowledge bundle for upload-only LLM runtimes."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re


ALLOWED_EXACT = {
    "brand.yml",
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
    "research/customer-intelligence.md",
    "research/evidence-ledger/manifest.json",
    "sources/website/crawl-state.json",
    "learning/approved-rules.yml",
    "learning/active-memory.json",
    "learning/preference-signals.yml",
    "learning/rejected-patterns.yml",
    "learning/decisions.md",
    "connectors/capabilities.yml",
}
SENSITIVE_SAFE_NAMESPACES = ("context/", "products/", "strategy/")
ALLOWED_SUFFIXES = {".md", ".yml", ".yaml", ".json"}
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*[\"']?[A-Za-z0-9_.-]*(?:api[_-]?key|access[_-]?token|"
    r"refresh[_-]?token|client[_-]?secret|private[_-]?key|secret|password)"
    r"[\"']?\s*[:=]\s*\S+"
)
AUTHORIZATION_VALUE = re.compile(
    r"(?im)^\s*[\"']?authorization[\"']?\s*[:=]\s*[\"']?(?:bearer|basic)\s+\S+"
)
PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN (?:ENCRYPTED |RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
CREDENTIAL_FINGERPRINT = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"gh[pousr]_[A-Za-z0-9]{36,255}|"
    r"github_pat_[A-Za-z0-9_]{60,255}|"
    r"glpat-[A-Za-z0-9_-]{20,255}|"
    r"npm_[A-Za-z0-9]{36}|"
    r"(?:AKIA|ASIA)[A-Z0-9]{16}|"
    r"AIza[0-9A-Za-z_-]{35}|"
    r"xox[baprs]-[0-9A-Za-z-]{20,255}|"
    r"sk_live_[0-9A-Za-z]{20,255}|"
    r"sk-(?:proj-)?[0-9A-Za-z_-]{20,255}|"
    r"sk-ant-[0-9A-Za-z_-]{20,255}"
    r")(?![A-Za-z0-9])"
)
SENSITIVE_KEY_SUFFIXES = (
    "apikey",
    "accesstoken",
    "refreshtoken",
    "clientsecret",
    "privatekey",
    "password",
    "authorization",
    "secretaccesskey",
    "accesskeyid",
    "sessiontoken",
)
MANIFEST_SLUG = re.compile(r'(?m)^\s*slug:\s*["\']?([^"\'\s,}]+)')
BRAND_SLUG_FIELD = re.compile(
    r'(?m)^\s*["\']?brand_slug["\']?\s*:\s*["\']?([^"\'\s,}]+)'
)
ANY_TOP_LEVEL_NAMING = re.compile(r'^["\']?naming["\']?\s*:')
CANONICAL_TOP_LEVEL_NAMING = re.compile(r"^naming:\s*(?:#.*)?$")
ANY_TEST_PREFIX = re.compile(r"^\s*test_prefix\s*:")
CANONICAL_TEST_PREFIX = re.compile(
    r'^  test_prefix:\s*"CONTST"\s*(?:#.*)?$'
)
ANY_NEXT_TEST_NUMBER = re.compile(r"^\s*next_test_number\s*:")
CANONICAL_NEXT_TEST_NUMBER = re.compile(
    r"^  next_test_number:\s*(?P<number>[1-9]\d*)\s*(?:#.*)?$"
)
ANY_TOP_LEVEL_TESTS = re.compile(r'^["\']?tests["\']?\s*:')
CANONICAL_TOP_LEVEL_TESTS = re.compile(
    r"^tests:\s*(?P<value>\[\])?\s*(?:#.*)?$"
)
CANONICAL_TEST_ITEM = re.compile(
    r"^  - test_id:\s*(?P<identifier>CONTST(?P<number>\d{3}))\s*(?:#.*)?$"
)
ANY_TEST_ID_KEY = re.compile(r"^\s+test_id\s*:")


def selected_files(folder: pathlib.Path) -> list[pathlib.Path]:
    selected = []
    for path in folder.rglob("*"):
        if path.is_symlink():
            relative = path.relative_to(folder).as_posix()
            raise ValueError(f"symlink is not allowed in brand bundle sources: {relative}")
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(folder)
        except ValueError as error:
            raise ValueError(f"bundle source resolves outside brand folder: {path}") from error
        relative = path.relative_to(folder).as_posix()
        if relative.startswith(SENSITIVE_SAFE_NAMESPACES) and relative not in ALLOWED_EXACT:
            raise ValueError(
                f"unapproved bundle source in sensitive namespace: {relative}"
            )
        allowed = relative in ALLOWED_EXACT
        if allowed and path.suffix.lower() in ALLOWED_SUFFIXES:
            selected.append(path)
    return sorted(selected, key=lambda path: path.relative_to(folder).as_posix())


def fence_language(path: pathlib.Path) -> str:
    return {
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
    }.get(path.suffix.lower(), "markdown")


def digest_files(folder: pathlib.Path, files: list[pathlib.Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(folder).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def normalized_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def structured_contains_secret(value: object) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            key_name = normalized_key(key)
            if key_name.endswith(SENSITIVE_KEY_SUFFIXES) and nested not in (None, "", False):
                return True
            if structured_contains_secret(nested):
                return True
    elif isinstance(value, list):
        return any(structured_contains_secret(item) for item in value)
    return False


def block_end(lines: list[str], start: int) -> int:
    """Return the next non-comment top-level YAML line after ``start``."""
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == line.lstrip():
            return index
    return len(lines)


def parse_manifest_test_state(manifest_text: str) -> int:
    lines = manifest_text.splitlines()
    naming_indexes = [
        index for index, line in enumerate(lines) if ANY_TOP_LEVEL_NAMING.match(line)
    ]
    if (
        len(naming_indexes) != 1
        or not CANONICAL_TOP_LEVEL_NAMING.fullmatch(lines[naming_indexes[0]])
    ):
        raise ValueError("brand.yml must contain exactly one top-level naming block")

    naming_start = naming_indexes[0]
    naming_end = block_end(lines, naming_start)
    prefix_indexes = [
        index for index, line in enumerate(lines) if ANY_TEST_PREFIX.match(line)
    ]
    if (
        len(prefix_indexes) != 1
        or not naming_start < prefix_indexes[0] < naming_end
        or not CANONICAL_TEST_PREFIX.fullmatch(lines[prefix_indexes[0]])
    ):
        if (
            len(prefix_indexes) == 1
            and naming_start < prefix_indexes[0] < naming_end
        ):
            raise ValueError(
                "brand.yml naming.test_prefix must be literal uppercase CONTST"
            )
        raise ValueError(
            "brand.yml must contain exactly one naming.test_prefix inside top-level naming block"
        )

    next_indexes = [
        index for index, line in enumerate(lines) if ANY_NEXT_TEST_NUMBER.match(line)
    ]
    if (
        len(next_indexes) != 1
        or not naming_start < next_indexes[0] < naming_end
    ):
        raise ValueError(
            "brand.yml must contain exactly one naming.next_test_number inside top-level naming block"
        )
    next_match = CANONICAL_NEXT_TEST_NUMBER.fullmatch(lines[next_indexes[0]])
    if next_match is None:
        raise ValueError(
            "brand.yml naming.next_test_number must be a canonical positive integer"
        )
    return int(next_match.group("number"))


def parse_test_register(register_text: str) -> list[int]:
    lines = register_text.splitlines()
    tests_indexes = [
        index for index, line in enumerate(lines) if ANY_TOP_LEVEL_TESTS.match(line)
    ]
    if (
        len(tests_indexes) != 1
        or not CANONICAL_TOP_LEVEL_TESTS.fullmatch(lines[tests_indexes[0]])
    ):
        raise ValueError(
            "strategy/test-register.yml must contain exactly one canonical top-level tests key"
        )

    tests_start = tests_indexes[0]
    tests_match = CANONICAL_TOP_LEVEL_TESTS.fullmatch(lines[tests_start])
    assert tests_match is not None
    tests_end = block_end(lines, tests_start)
    block_lines = lines[tests_start + 1 : tests_end]
    if tests_match.group("value") == "[]":
        has_content = any(
            line.strip() and not line.lstrip().startswith("#") for line in block_lines
        )
        if has_content:
            raise ValueError(
                "strategy/test-register.yml tests must use an empty list or canonical block-style items"
            )
        return []

    numbers: list[int] = []
    seen: set[str] = set()
    current_item = False
    for line in block_lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  -"):
            item_match = CANONICAL_TEST_ITEM.fullmatch(line)
            if item_match is None:
                raise ValueError(
                    "strategy/test-register.yml tests must use canonical block-style "
                    "`  - test_id: CONTST###` items"
                )
            identifier = item_match.group("identifier")
            if identifier in seen:
                raise ValueError(f"strategy/test-register.yml reuses {identifier}")
            seen.add(identifier)
            numbers.append(int(item_match.group("number")))
            current_item = True
            continue
        if not current_item or not line.startswith("    "):
            raise ValueError(
                "strategy/test-register.yml tests must use canonical block-style "
                "`  - test_id: CONTST###` items"
            )
        if ANY_TEST_ID_KEY.match(line):
            raise ValueError(
                "strategy/test-register.yml has a duplicate test_id key within one item"
            )

    if not numbers:
        raise ValueError(
            "strategy/test-register.yml empty tests must use canonical `tests: []`"
        )
    return numbers


def validate_test_state(folder: pathlib.Path, manifest_text: str) -> None:
    register = folder / "strategy" / "test-register.yml"
    if not register.is_file():
        return

    actual_next = parse_manifest_test_state(manifest_text)
    numbers = parse_test_register(register.read_text())

    ordered = sorted(numbers)
    if ordered and ordered != list(range(1, ordered[-1] + 1)):
        raise ValueError(
            "strategy/test-register.yml must use sequential CONTST values from CONTST001"
        )
    expected_next = ordered[-1] + 1 if ordered else 1
    if actual_next != expected_next:
        raise ValueError(
            f"brand.yml naming.next_test_number must be {expected_next} for current test-register state"
        )


def build_bundle(folder: pathlib.Path, output: pathlib.Path) -> pathlib.Path:
    folder = pathlib.Path(folder).resolve()
    output = pathlib.Path(output)
    resolved_output = output.resolve()
    try:
        resolved_output.relative_to(folder)
    except ValueError:
        pass
    else:
        raise ValueError("bundle output must be outside brand folder")
    manifest = folder / "brand.yml"
    if not manifest.is_file():
        raise FileNotFoundError(f"brand.yml not found in {folder}")
    manifest_text = manifest.read_text()
    slug_match = MANIFEST_SLUG.search(manifest_text)
    if not slug_match:
        raise ValueError("brand.yml does not contain brand.slug")
    manifest_slug = slug_match.group(1)
    validate_test_state(folder, manifest_text)

    files = selected_files(folder)
    evidence_files = [
        path for path in files if not path.relative_to(folder).as_posix().startswith("learning/")
    ]
    learning_files = [
        path for path in files if path.relative_to(folder).as_posix().startswith("learning/")
    ]
    evidence_version = digest_files(folder, evidence_files)
    learning_version = digest_files(folder, learning_files)
    parts = [
        "# Brand knowledge bundle\n\n",
        "Generated from the canonical brand folder using an exact allowlist of approved summaries "
        "and state files. Raw evidence, revision history, unapproved sensitive-namespace files and "
        "secrets are excluded; generation fails when unsafe content is detected. Return a learning "
        "patch after approved human revisions.\n\n",
        f"Evidence version: `sha256:{evidence_version}`\n\n",
        f"Learning version: `sha256:{learning_version}`\n",
    ]
    for path in files:
        relative = path.relative_to(folder).as_posix()
        content = path.read_text().strip()
        structured = None
        if path.suffix.lower() == ".json":
            try:
                structured = json.loads(content)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON in bundle source: {relative}") from error
            scoped_slug_value = (
                structured.get("brand_slug") if isinstance(structured, dict) else None
            )
        else:
            scoped_slug = BRAND_SLUG_FIELD.search(content)
            scoped_slug_value = scoped_slug.group(1) if scoped_slug else None
        if scoped_slug_value and scoped_slug_value != manifest_slug:
            raise ValueError(
                f"{relative} brand {scoped_slug_value} does not match manifest brand "
                f"{manifest_slug}"
            )
        if (
            SECRET_ASSIGNMENT.search(content)
            or AUTHORIZATION_VALUE.search(content)
            or PRIVATE_KEY_BLOCK.search(content)
            or CREDENTIAL_FINGERPRINT.search(content)
            or structured_contains_secret(structured)
        ):
            raise ValueError(f"possible secret found in bundle source: {relative}")
        parts.extend(
            [
                f"\n\n## Source: `{relative}`\n\n",
                f"```{fence_language(path)}\n",
                content,
                "\n```\n",
            ]
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(parts))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brand_folder", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    result = build_bundle(args.brand_folder, args.output)
    print(f"Wrote brand bundle: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
