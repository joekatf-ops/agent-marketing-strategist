#!/usr/bin/env python3
"""Build a compact brand knowledge bundle for upload-only LLM runtimes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import secrets
import stat
from typing import NamedTuple

try:
    from content_safety import structure_contains_secret, text_contains_secret
except ModuleNotFoundError:  # Loaded by repository tests rather than as a script.
    import importlib.util as _importlib_util

    _content_safety_spec = _importlib_util.spec_from_file_location(
        "content_safety", pathlib.Path(__file__).with_name("content_safety.py")
    )
    if _content_safety_spec is None or _content_safety_spec.loader is None:
        raise ImportError("content_safety.py could not be loaded")
    _content_safety = _importlib_util.module_from_spec(_content_safety_spec)
    _content_safety_spec.loader.exec_module(_content_safety)
    structure_contains_secret = _content_safety.structure_contains_secret
    text_contains_secret = _content_safety.text_contains_secret


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
FORBIDDEN_PREFIXES = (
    "assets/",
    "exports/",
    "outputs/ad-analysis/",
    "raw-assets/",
)
FORBIDDEN_SUFFIXES = {".csv"}
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
CANONICAL_MAPPING_ENTRY = re.compile(
    r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:\s+(?P<value>.*))?$"
)
CANONICAL_NUMBER = re.compile(
    r"^[+-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$"
)
CANONICAL_BOOL_OR_NULL = re.compile(r"^(?:true|false|null|~)$", re.IGNORECASE)
CANONICAL_PLAIN_SCALAR = re.compile(
    r"^[A-Za-z0-9_./][A-Za-z0-9_./:+-]*(?: [A-Za-z0-9_./:+-]+)*$"
)
YAML_LEADING_INDICATORS = "-?:,[]{}#&*!|>'\"%@`"
RESERVED_STATE_KEYS = {"naming", "test_prefix", "next_test_number", "tests", "test_id"}


class YamlEntry(NamedTuple):
    line_index: int
    indent: int
    sequence: bool
    key: str | None


class SourceSnapshot(NamedTuple):
    relative: str
    suffix: str
    content: bytes


DIRECTORY_OPEN_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
NOFOLLOW_OPEN_FLAG = getattr(os, "O_NOFOLLOW", 0)
NONBLOCK_OPEN_FLAG = getattr(os, "O_NONBLOCK", 0)


def _absolute_path(path: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(os.path.abspath(os.fspath(path)))


def _same_directory(first: os.stat_result, second: os.stat_result) -> bool:
    return (
        stat.S_ISDIR(first.st_mode)
        and stat.S_ISDIR(second.st_mode)
        and first.st_dev == second.st_dev
        and first.st_ino == second.st_ino
    )


def _open_absolute_directory_no_follow(
    directory: pathlib.Path, *, create: bool = False
) -> int:
    lexical = _absolute_path(directory)
    if not lexical.is_absolute():
        raise ValueError(f"directory must be absolute: {directory}")
    try:
        lexical_final = os.lstat(lexical)
    except FileNotFoundError:
        if not create:
            raise
    else:
        if stat.S_ISLNK(lexical_final.st_mode):
            raise ValueError(f"symlinked directory is not allowed: {lexical}")

    # macOS exposes system aliases such as /var -> /private/var. Canonicalise the
    # directory boundary once, then retain descriptors and disallow every link below it.
    absolute = pathlib.Path(os.path.realpath(lexical))

    descriptor = os.open(absolute.anchor, DIRECTORY_OPEN_FLAGS | NOFOLLOW_OPEN_FLAG)
    try:
        for component in absolute.parts[1:]:
            try:
                before = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, mode=0o755, dir_fd=descriptor)
                before = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode):
                raise ValueError(f"symlinked directory is not allowed: {absolute}")
            child = os.open(
                component,
                DIRECTORY_OPEN_FLAGS | NOFOLLOW_OPEN_FLAG,
                dir_fd=descriptor,
            )
            try:
                opened = os.fstat(child)
                after = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
                if not _same_directory(before, opened) or not _same_directory(
                    opened, after
                ):
                    raise ValueError(f"directory identity changed while opening: {absolute}")
            except Exception:
                os.close(child)
                raise
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _file_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_nlink,
    )


def _snapshot_file(
    directory_descriptor: int,
    name: str,
    relative: str,
    before: os.stat_result,
) -> SourceSnapshot:
    if before.st_nlink != 1:
        raise ValueError(f"hardlinked bundle source is not allowed: {relative}")
    descriptor = os.open(
        name,
        os.O_RDONLY | NOFOLLOW_OPEN_FLAG | NONBLOCK_OPEN_FLAG,
        dir_fd=directory_descriptor,
    )
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"bundle source is not a regular file: {relative}")
        if _file_identity(opened) != _file_identity(before):
            raise ValueError(f"bundle source changed while being opened: {relative}")
        if opened.st_nlink != 1:
            raise ValueError(f"hardlinked bundle source is not allowed: {relative}")

        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)

        after_read = os.fstat(descriptor)
        try:
            after_path = os.stat(
                name, dir_fd=directory_descriptor, follow_symlinks=False
            )
        except FileNotFoundError as error:
            raise ValueError(
                f"bundle source changed while being read: {relative}"
            ) from error
        if (
            not stat.S_ISREG(after_path.st_mode)
            or _file_identity(after_read) != _file_identity(opened)
            or _file_identity(after_path) != _file_identity(opened)
        ):
            raise ValueError(f"bundle source changed while being read: {relative}")
        return SourceSnapshot(
            relative=relative,
            suffix=pathlib.PurePosixPath(relative).suffix.lower(),
            content=b"".join(chunks),
        )
    finally:
        os.close(descriptor)


def _directory_is_forbidden(relative: str) -> bool:
    prefix = relative.rstrip("/") + "/"
    return any(prefix.startswith(forbidden) for forbidden in FORBIDDEN_PREFIXES)


def _snapshot_directory(
    directory_descriptor: int,
    relative_directory: str,
    selected: list[SourceSnapshot],
) -> None:
    for name in sorted(os.listdir(directory_descriptor)):
        relative = f"{relative_directory}/{name}" if relative_directory else name
        before = os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode):
            raise ValueError(
                f"symlink is not allowed in brand bundle sources: {relative}"
            )
        if stat.S_ISDIR(before.st_mode):
            if _directory_is_forbidden(relative):
                continue
            child = os.open(
                name,
                DIRECTORY_OPEN_FLAGS | NOFOLLOW_OPEN_FLAG,
                dir_fd=directory_descriptor,
            )
            try:
                opened = os.fstat(child)
                after = os.stat(
                    name, dir_fd=directory_descriptor, follow_symlinks=False
                )
                if not _same_directory(before, opened) or not _same_directory(
                    opened, after
                ):
                    raise ValueError(
                        f"bundle source directory changed while opening: {relative}"
                    )
                _snapshot_directory(child, relative, selected)
            finally:
                os.close(child)
            continue
        if not stat.S_ISREG(before.st_mode):
            if relative in ALLOWED_EXACT:
                raise ValueError(f"bundle source is not a regular file: {relative}")
            continue

        suffix = pathlib.PurePosixPath(relative).suffix.lower()
        if relative.startswith(FORBIDDEN_PREFIXES) or suffix in FORBIDDEN_SUFFIXES:
            continue
        if (
            relative.startswith(SENSITIVE_SAFE_NAMESPACES)
            and relative not in ALLOWED_EXACT
        ):
            raise ValueError(
                f"unapproved bundle source in sensitive namespace: {relative}"
            )
        if relative in ALLOWED_EXACT and suffix in ALLOWED_SUFFIXES:
            selected.append(
                _snapshot_file(directory_descriptor, name, relative, before)
            )


def selected_files(folder: pathlib.Path) -> list[SourceSnapshot]:
    descriptor = _open_absolute_directory_no_follow(folder)
    try:
        selected: list[SourceSnapshot] = []
        _snapshot_directory(descriptor, "", selected)
        return sorted(selected, key=lambda source: source.relative)
    finally:
        os.close(descriptor)


def fence_language(path: SourceSnapshot | pathlib.Path) -> str:
    return {
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
    }.get(path.suffix.lower(), "markdown")


def digest_files(folder: pathlib.Path, files: list[SourceSnapshot]) -> str:
    digest = hashlib.sha256()
    for source in files:
        digest.update(source.relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source.content)
        digest.update(b"\0")
    return digest.hexdigest()


def invalid_yaml(source: str, line_number: int, detail: str) -> ValueError:
    return ValueError(
        f"invalid canonical YAML in {source} at line {line_number}: {detail}"
    )


def strip_inline_comment(text: str) -> str:
    quote = ""
    escaped = False
    index = 0
    while index < len(text):
        character = text[index]
        if quote == '"':
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            index += 1
            continue
        if quote == "'":
            if character == quote:
                if index + 1 < len(text) and text[index + 1] == quote:
                    index += 2
                    continue
                quote = ""
            index += 1
            continue
        if character in {'"', "'"}:
            quote = character
        elif character == "#" and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip()
        index += 1
    return text.rstrip()


def flow_contains_reserved_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            key in RESERVED_STATE_KEYS or flow_contains_reserved_key(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(flow_contains_reserved_key(item) for item in value)
    return False


def validate_yaml_value(value: str, source: str, line_number: int) -> None:
    if not value:
        return
    if value[0] in "[{":
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise invalid_yaml(source, line_number, "invalid or unbalanced flow value") from error
        if not isinstance(parsed, (list, dict)):
            raise invalid_yaml(source, line_number, "flow value must be a list or object")
        if flow_contains_reserved_key(parsed):
            raise invalid_yaml(source, line_number, "quoted reserved key in flow value")
        return
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise invalid_yaml(source, line_number, "invalid double-quoted scalar") from error
        if not isinstance(parsed, str):
            raise invalid_yaml(source, line_number, "quoted scalar must contain text")
        return
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise invalid_yaml(source, line_number, "invalid single-quoted scalar")
        inner = value[1:-1]
        if "'" in inner.replace("''", ""):
            raise invalid_yaml(source, line_number, "invalid single-quoted scalar")
        return
    if CANONICAL_NUMBER.fullmatch(value) or CANONICAL_BOOL_OR_NULL.fullmatch(value):
        return
    if value[0] in YAML_LEADING_INDICATORS:
        raise invalid_yaml(source, line_number, "plain scalar starts with a YAML indicator")
    if re.search(r":(?:\s|$)", value):
        raise invalid_yaml(source, line_number, "plain scalar contains a mapping marker")
    if CANONICAL_PLAIN_SCALAR.fullmatch(value) is None:
        raise invalid_yaml(
            source,
            line_number,
            "plain scalar contains unsupported or ambiguous characters",
        )


def validate_canonical_yaml_subset(text: str, source: str) -> list[YamlEntry]:
    entries: list[YamlEntry] = []
    contexts: dict[int, tuple[str, set[str]]] = {}
    previous_indent: int | None = None
    previous_can_descend = False

    for line_index, raw_line in enumerate(text.splitlines()):
        line_number = line_index + 1
        if "\t" in raw_line:
            raise invalid_yaml(source, line_number, "tabs are unsupported")
        line = strip_inline_comment(raw_line)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2:
            raise invalid_yaml(source, line_number, "indentation must use two-space steps")
        if previous_indent is None:
            if indent != 0:
                raise invalid_yaml(source, line_number, "first entry must be top-level")
        elif indent > previous_indent and (
            not previous_can_descend or indent != previous_indent + 2
        ):
            raise invalid_yaml(source, line_number, "invalid indentation transition")

        for level in [level for level in contexts if level > indent]:
            del contexts[level]

        content = line[indent:]
        sequence = content == "-" or content.startswith("- ")
        if content.startswith("-") and not sequence:
            raise invalid_yaml(source, line_number, "invalid sequence item")
        item = content[2:].strip() if content.startswith("- ") else ""
        candidate = item if sequence else content
        mapping_match = CANONICAL_MAPPING_ENTRY.fullmatch(candidate)
        key: str | None = None
        value = ""
        inline_mapping = False
        if mapping_match is not None:
            key = mapping_match.group("key")
            value = (mapping_match.group("value") or "").strip()
            inline_mapping = sequence
            validate_yaml_value(value, source, line_number)
        elif sequence and item:
            value = item
            validate_yaml_value(value, source, line_number)
        elif not sequence:
            raise invalid_yaml(source, line_number, "mapping keys must be unquoted bare names")

        line_kind = "sequence" if sequence else "mapping"
        context = contexts.get(indent)
        if context is not None and context[0] != line_kind:
            raise invalid_yaml(source, line_number, "cannot mix mapping and sequence entries")
        if context is None:
            contexts[indent] = (line_kind, set())

        if key is not None:
            key_indent = indent + 2 if inline_mapping else indent
            key_context = contexts.get(key_indent)
            if key_context is not None and key_context[0] != "mapping":
                raise invalid_yaml(source, line_number, "mapping entry has an invalid parent")
            if key_context is None:
                key_context = ("mapping", set())
                contexts[key_indent] = key_context
            if key in key_context[1]:
                raise invalid_yaml(source, line_number, f"duplicate mapping key: {key}")
            key_context[1].add(key)

        entries.append(YamlEntry(line_index, indent, sequence, key))
        previous_indent = indent
        previous_can_descend = (key is not None and not value) or inline_mapping or (
            sequence and not item
        )

    if not entries:
        raise invalid_yaml(source, 1, "state file must not be empty")
    return entries


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


def validate_test_state(manifest_text: str, register_text: str | None) -> None:
    if register_text is None:
        return

    actual_next = parse_manifest_test_state(manifest_text)
    numbers = parse_test_register(register_text)
    manifest_entries = validate_canonical_yaml_subset(manifest_text, "brand.yml")
    register_entries = validate_canonical_yaml_subset(
        register_text, "strategy/test-register.yml"
    )

    for key in ("naming", "test_prefix", "next_test_number"):
        occurrences = [entry for entry in manifest_entries if entry.key == key]
        if len(occurrences) != 1:
            raise invalid_yaml("brand.yml", 1, f"reserved key must occur once: {key}")
    tests_entries = [entry for entry in register_entries if entry.key == "tests"]
    if len(tests_entries) != 1 or tests_entries[0].indent != 0:
        raise invalid_yaml(
            "strategy/test-register.yml", 1, "reserved tests key must occur once at top level"
        )
    test_id_entries = [entry for entry in register_entries if entry.key == "test_id"]
    if len(test_id_entries) != len(numbers) or any(
        entry.indent != 2 or not entry.sequence for entry in test_id_entries
    ):
        raise invalid_yaml(
            "strategy/test-register.yml",
            1,
            "test_id is only valid as a canonical top-level tests item",
        )

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


def _decode_source(source: SourceSnapshot) -> str:
    try:
        return source.content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"bundle source is not valid UTF-8: {source.relative}") from error


def _output_destination_identity(
    directory_descriptor: int, name: str
) -> tuple[int, int, int, int, int, int] | None:
    try:
        destination = os.stat(
            name, dir_fd=directory_descriptor, follow_symlinks=False
        )
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(destination.st_mode):
        raise ValueError(f"linked output destination is not allowed: {name}")
    if not stat.S_ISREG(destination.st_mode):
        raise ValueError(f"bundle output destination is not a regular file: {name}")
    if destination.st_nlink != 1:
        raise ValueError(f"hardlinked output destination is not allowed: {name}")
    return _file_identity(destination)


def _write_all(descriptor: int, content: bytes) -> None:
    remaining = memoryview(content)
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("failed to write staged brand bundle")
        remaining = remaining[written:]


def _verified_descriptor_state(
    descriptor: int, content: bytes
) -> os.stat_result | None:
    """Return a stable descriptor state only when it contains the exact bytes."""
    before = os.fstat(descriptor)
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
        or before.st_size != len(content)
    ):
        return None
    offset = 0
    while offset < len(content):
        chunk = os.pread(
            descriptor, min(1024 * 1024, len(content) - offset), offset
        )
        if not chunk or chunk != content[offset : offset + len(chunk)]:
            return None
        offset += len(chunk)
    if os.pread(descriptor, 1, offset):
        return None
    after = os.fstat(descriptor)
    if _file_identity(after) != _file_identity(before):
        return None
    return after


def _published_bundle_is_verified(
    directory_descriptor: int,
    name: str,
    staging_descriptor: int,
    content: bytes,
) -> bool:
    descriptor_state = _verified_descriptor_state(staging_descriptor, content)
    if descriptor_state is None:
        return False
    try:
        destination = os.stat(
            name, dir_fd=directory_descriptor, follow_symlinks=False
        )
    except FileNotFoundError:
        return False
    final_descriptor_state = os.fstat(staging_descriptor)
    return (
        stat.S_ISREG(destination.st_mode)
        and destination.st_nlink == 1
        and _file_identity(final_descriptor_state) == _file_identity(descriptor_state)
        and _file_identity(destination) == _file_identity(descriptor_state)
    )


def _remove_unverified_failed_publication(
    directory_descriptor: int,
    name: str,
    original_destination: tuple[int, int, int, int, int, int] | None,
    staging_descriptor: int,
    content: bytes,
) -> None:
    """Preserve an unchanged prior output; remove anything else unverified."""
    try:
        current = os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    if (
        original_destination is not None
        and _file_identity(current) == original_destination
    ):
        return
    if _published_bundle_is_verified(
        directory_descriptor, name, staging_descriptor, content
    ):
        return
    os.unlink(name, dir_fd=directory_descriptor)
    try:
        os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        os.fsync(directory_descriptor)
        return
    raise ValueError("unverified brand bundle output could not be removed")


def _publish_bundle(output: pathlib.Path, content: bytes) -> None:
    absolute_output = _absolute_path(output)
    if not absolute_output.name or absolute_output.name in {".", ".."}:
        raise ValueError(f"invalid bundle output path: {output}")
    parent_descriptor = _open_absolute_directory_no_follow(
        absolute_output.parent, create=True
    )
    temporary_name = (
        f".{absolute_output.name}.tmp-{os.getpid()}-{secrets.token_hex(8)}"
    )
    temporary_descriptor: int | None = None
    original_destination: tuple[int, int, int, int, int, int] | None = None
    publication_attempted = False
    try:
        original_destination = _output_destination_identity(
            parent_descriptor, absolute_output.name
        )
        temporary_descriptor = os.open(
            temporary_name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL | NOFOLLOW_OPEN_FLAG,
            0o600,
            dir_fd=parent_descriptor,
        )
        created = os.fstat(temporary_descriptor)
        if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
            raise ValueError("brand bundle staging file must be a new single-link file")
        _write_all(temporary_descriptor, content)
        os.fchmod(temporary_descriptor, 0o644)
        os.fsync(temporary_descriptor)
        staged = _verified_descriptor_state(temporary_descriptor, content)
        if staged is None or (
            staged.st_dev != created.st_dev or staged.st_ino != created.st_ino
        ):
            raise ValueError("brand bundle staging file changed before publication")

        current_destination = _output_destination_identity(
            parent_descriptor, absolute_output.name
        )
        if current_destination != original_destination:
            raise ValueError("bundle output destination changed before publication")
        current_staging = os.stat(
            temporary_name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if _file_identity(current_staging) != _file_identity(staged):
            raise ValueError("brand bundle staging file changed before publication")

        publication_attempted = True
        os.replace(
            temporary_name,
            absolute_output.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        if not _published_bundle_is_verified(
            parent_descriptor,
            absolute_output.name,
            temporary_descriptor,
            content,
        ):
            raise ValueError("published brand bundle identity or content is unsafe")
        os.fsync(parent_descriptor)
    except BaseException:
        if publication_attempted and temporary_descriptor is not None:
            _remove_unverified_failed_publication(
                parent_descriptor,
                absolute_output.name,
                original_destination,
                temporary_descriptor,
                content,
            )
        raise
    finally:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_descriptor)
        except FileNotFoundError:
            pass
        os.close(parent_descriptor)


def build_bundle(folder: pathlib.Path, output: pathlib.Path) -> pathlib.Path:
    folder = _absolute_path(pathlib.Path(folder))
    output = pathlib.Path(output)
    absolute_output = _absolute_path(output)
    canonical_folder = pathlib.Path(os.path.realpath(folder))
    canonical_output = (
        pathlib.Path(os.path.realpath(absolute_output.parent)) / absolute_output.name
    )
    try:
        canonical_output.relative_to(canonical_folder)
    except ValueError:
        pass
    else:
        raise ValueError("bundle output must be outside brand folder")

    files = selected_files(folder)
    sources = {source.relative: source for source in files}
    manifest = sources.get("brand.yml")
    if manifest is None:
        raise FileNotFoundError(f"brand.yml not found in {folder}")
    decoded = {source.relative: _decode_source(source) for source in files}
    manifest_text = decoded["brand.yml"]
    slug_match = MANIFEST_SLUG.search(manifest_text)
    if not slug_match:
        raise ValueError("brand.yml does not contain brand.slug")
    manifest_slug = slug_match.group(1)
    validate_test_state(
        manifest_text, decoded.get("strategy/test-register.yml")
    )

    evidence_files = [
        source for source in files if not source.relative.startswith("learning/")
    ]
    learning_files = [
        source for source in files if source.relative.startswith("learning/")
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
    for source in files:
        relative = source.relative
        content = decoded[relative].strip()
        structured = None
        if source.suffix == ".json":
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
        if text_contains_secret(content) or structure_contains_secret(structured):
            raise ValueError(f"possible secret found in bundle source: {relative}")
        parts.extend(
            [
                f"\n\n## Source: `{relative}`\n\n",
                f"```{fence_language(source)}\n",
                content,
                "\n```\n",
            ]
        )

    _publish_bundle(output, "".join(parts).encode("utf-8"))
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
