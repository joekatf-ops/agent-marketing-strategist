"""Create portable, brand-scoped ad-analysis run manifests."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import re
import shlex
import stat
from typing import NamedTuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUN_TEMPLATE = ROOT / "templates" / "brand-folder" / "outputs" / "ad-analysis" / "README.md"
MODES = {"creative-audit", "performance-diagnosis"}
MAX_INTAKE_BYTES = 1_048_576
MAX_JSON_DEPTH = 32
RUN_ID = re.compile(r"^ADR-(?P<date>\d{8})-(?P<number>\d{3})$")
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VERSION = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
_TOP_LEVEL_METHOD = re.compile(
    r'^method_version:\s*(?:"(?P<double>[^"]*)"|\'(?P<single>[^\']*)\'|(?P<bare>[^\s#]+))\s*(?:#.*)?$'
)
_BRAND = re.compile(r"^brand:\s*(?:#.*)?$")
_INDENTED_SLUG = re.compile(
    r'^\s+slug:\s*(?:"(?P<double>[^"]*)"|\'(?P<single>[^\']*)\'|(?P<bare>[^\s#]+))\s*(?:#.*)?$'
)
_SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
_URL_LIKE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
_CREDENTIAL_FINGERPRINT = re.compile(
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
_AUTHORIZATION_VALUE = re.compile(
    r"\bauthorization\s*[:=]\s*(?:bearer|basic)\s+\S+",
    re.IGNORECASE,
)
_PRIVATE_KEY_HEADER = re.compile(
    r"-----BEGIN (?:ENCRYPTED |RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
_TOP_LEVEL_KEYS = {
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
}
_SOURCE_KEYS = {"source_id", "kind", "label", "location", "sha256"}
_SOURCE_KINDS = {"file", "attachment", "url", "screenshot", "table"}
_AD_KEYS = {
    "ad_id",
    "asset_source_ids",
    "asset_type",
    "primary_text",
    "headline",
    "description",
    "cta",
    "destination_url",
    "destination_type",
    "coordinate_key",
    "contst",
    "source",
    "who",
    "primary_problem",
    "awareness_code",
    "messaging_route",
    "format",
    "primary_hook",
    "post_id",
}
_AD_REQUIRED_KEYS = set(_AD_KEYS)
_AD_NULLABLE_TEXT_KEYS = {
    "primary_text",
    "headline",
    "description",
    "cta",
    "destination_url",
    "coordinate_key",
    "who",
    "primary_problem",
    "messaging_route",
    "format",
    "primary_hook",
    "post_id",
}
_ASSET_TYPES = {"video", "static", "carousel", "other"}
_DESTINATION_TYPES = {"LP", "PDP", "HP", "CP"}
_AD_SOURCES = {"NNT", "INSPO", "ITR"}
_AWARENESS_CODES = {"UWA", "PRA", "SLA", "PDA"}
_CONTST = re.compile(r"^CONTST\d{3}$")
_PERFORMANCE_KEYS = {
    "source_ids",
    "date_range",
    "attribution",
    "currency",
    "aggregation_level",
    "field_mapping",
    "ad_mapping",
    "logged_interventions",
    "account_norms",
    "reference_ranges",
    "threshold_basis",
}
_INTERVENTION_KEYS = {"occurred_at", "scope", "description", "ad_id"}
_INTERVENTION_SCOPES = {"account", "campaign", "ad-set", "ad"}
_ACCOUNT_NORM_KEYS = {"metric", "value", "unit", "comparison_window", "source"}
_REFERENCE_RANGE_KEYS = {"status", "sources"}
_REFERENCE_RANGE_STATUSES = {"permitted", "unavailable"}
_THRESHOLD_BASIS_KEYS = {
    "metric",
    "baseline",
    "comparison_window",
    "threshold",
    "unit",
    "source",
    "ad_id",
}
_REQUIRED_FIELD_MAPPINGS = {"ad_id", "spend", "purchases"}
_FUNNEL_FIELD_MAPPINGS = {
    "impressions",
    "reach",
    "frequency",
    "cpm",
    "link_clicks",
    "outbound_clicks",
    "landing_page_views",
    "ctr",
    "cpc",
    "adds_to_cart",
    "initiates_checkout",
    "checkouts",
    "purchase_value",
    "roas",
}
_VIDEO_FIELD_MAPPINGS = {
    "video_3_second_plays",
    "video_thruplays",
    "video_plays_at_25_percent",
    "video_plays_at_50_percent",
    "video_plays_at_75_percent",
    "video_plays_at_95_percent",
    "video_plays_at_100_percent",
    "average_video_play_time",
}
_FIELD_MAPPING_KEYS = (
    _REQUIRED_FIELD_MAPPINGS | _FUNNEL_FIELD_MAPPINGS | _VIDEO_FIELD_MAPPINGS
)


class ValidationResult(NamedTuple):
    """Immutable analysis-input readiness result."""

    status: str
    errors: tuple[str, ...]
    limitations: tuple[str, ...]
    inventory: tuple[tuple[str, str, str, str, str], ...]


class _SymlinkAccessError(OSError):
    pass


class _LinkedFileError(OSError):
    pass


class _ChangedFileError(OSError):
    pass


def _stable_file_identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
        metadata.st_nlink,
    )


def _scalar(match: re.Match[str]) -> str:
    return next(value for value in match.group("double", "single", "bare") if value is not None)


def _validate_method_version(method_version: str) -> tuple[int, int, int]:
    match = _VERSION.fullmatch(method_version)
    if not match:
        raise ValueError("brand method_version must use major.minor.patch format")
    return tuple(int(match.group(name)) for name in ("major", "minor", "patch"))


def _absolute_lexical(path: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(os.path.abspath(os.fspath(path)))


def _no_follow_flag() -> int:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if (
        type(no_follow) is not int
        or type(directory) is not int
        or os.open not in os.supports_dir_fd
        or os.stat not in os.supports_dir_fd
        or os.stat not in os.supports_follow_symlinks
    ):
        raise OSError("descriptor-anchored no-follow access is unavailable")
    return no_follow


def _open_directory_no_follow(path: pathlib.Path) -> int:
    path = _absolute_lexical(path)
    no_follow = _no_follow_flag()
    flags = os.O_RDONLY | no_follow | os.O_DIRECTORY
    descriptor = os.open(path.anchor, flags)
    try:
        for component in path.parts[1:]:
            metadata = os.stat(
                component,
                dir_fd=descriptor,
                follow_symlinks=False,
            )
            if stat.S_ISLNK(metadata.st_mode):
                raise _SymlinkAccessError(f"path component is a symlink: {component}")
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            if not stat.S_ISDIR(os.fstat(next_descriptor).st_mode):
                os.close(next_descriptor)
                raise OSError(f"path component is not a directory: {component}")
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_regular_relative_from_descriptor_no_follow(
    directory_descriptor: int, relative: pathlib.Path
) -> int:
    relative = pathlib.Path(relative)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise OSError("file path must be a non-empty safe relative path")
    no_follow = _no_follow_flag()
    directory_flags = os.O_RDONLY | no_follow | os.O_DIRECTORY
    descriptor = os.dup(directory_descriptor)
    try:
        for component in relative.parts[:-1]:
            metadata = os.stat(
                component,
                dir_fd=descriptor,
                follow_symlinks=False,
            )
            if stat.S_ISLNK(metadata.st_mode):
                raise _SymlinkAccessError(f"path component is a symlink: {component}")
            next_descriptor = os.open(component, directory_flags, dir_fd=descriptor)
            if not stat.S_ISDIR(os.fstat(next_descriptor).st_mode):
                os.close(next_descriptor)
                raise OSError(f"path component is not a directory: {component}")
            os.close(descriptor)
            descriptor = next_descriptor

        filename = relative.parts[-1]
        metadata = os.stat(filename, dir_fd=descriptor, follow_symlinks=False)
        if stat.S_ISLNK(metadata.st_mode):
            raise _SymlinkAccessError(f"file is a symlink: {filename}")
        file_descriptor = os.open(
            filename, os.O_RDONLY | no_follow, dir_fd=descriptor
        )
        opened_metadata = os.fstat(file_descriptor)
        if not stat.S_ISREG(opened_metadata.st_mode):
            os.close(file_descriptor)
            raise OSError(f"file is not regular: {filename}")
        if metadata.st_nlink != 1 or opened_metadata.st_nlink != 1:
            os.close(file_descriptor)
            raise _LinkedFileError(f"file has multiple hard links: {filename}")
        if (metadata.st_dev, metadata.st_ino) != (
            opened_metadata.st_dev,
            opened_metadata.st_ino,
        ):
            os.close(file_descriptor)
            raise _ChangedFileError(f"file changed before it was opened: {filename}")
        return file_descriptor
    finally:
        os.close(descriptor)


def _open_regular_relative_no_follow(
    directory: pathlib.Path, relative: pathlib.Path
) -> int:
    directory_descriptor = _open_directory_no_follow(directory)
    try:
        return _open_regular_relative_from_descriptor_no_follow(
            directory_descriptor, relative
        )
    finally:
        os.close(directory_descriptor)


def _read_relative_text_from_descriptor_no_follow(
    directory_descriptor: int, relative: pathlib.Path
) -> str:
    descriptor = _open_regular_relative_from_descriptor_no_follow(
        directory_descriptor, relative
    )
    with os.fdopen(descriptor, "r", encoding="utf-8") as file:
        return file.read()


def _read_relative_text_no_follow(
    directory: pathlib.Path, relative: pathlib.Path
) -> str:
    descriptor = _open_regular_relative_no_follow(directory, relative)
    with os.fdopen(descriptor, "r", encoding="utf-8") as file:
        return file.read()


def _read_limited_regular_bytes(
    descriptor: int, maximum: int, *, close_descriptor: bool = True
) -> bytes:
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("intake manifest must be a regular file")
        if metadata.st_nlink != 1:
            raise ValueError("intake manifest must have exactly one hard link")
        if metadata.st_size > maximum:
            raise ValueError(f"intake manifest exceeds maximum size of {maximum} bytes")
        chunks = []
        remaining = maximum + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
        if len(content) > maximum:
            raise ValueError(f"intake manifest exceeds maximum size of {maximum} bytes")
        return content
    finally:
        if close_descriptor:
            os.close(descriptor)


def _require_json_depth(text: str, maximum: int) -> None:
    depth = 0
    quoted = False
    escaped = False
    for character in text:
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted = True
        elif character in "[{":
            depth += 1
            if depth > maximum:
                raise ValueError(
                    f"intake manifest exceeds maximum depth of {maximum} containers"
                )
        elif character in "]}":
            depth -= 1


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_nonfinite_json_number(value: str) -> object:
    raise ValueError(f"non-finite JSON number: {value}")


def _parse_intake_json(content: bytes) -> dict[str, object]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("intake manifest must be UTF-8 JSON") from error
    _require_json_depth(text, MAX_JSON_DEPTH)
    intake = json.loads(
        text,
        object_pairs_hook=_reject_duplicate_json_keys,
        parse_constant=_reject_nonfinite_json_number,
    )
    if not isinstance(intake, dict):
        raise ValueError("intake manifest must contain a JSON object")
    return intake


def _open_or_create_directory_relative_from_descriptor_no_follow(
    directory_descriptor: int, relative: pathlib.Path
) -> int:
    relative = pathlib.Path(relative)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise OSError("directory path must be a non-empty safe relative path")
    if os.mkdir not in os.supports_dir_fd:
        raise OSError("descriptor-anchored directory creation is unavailable")
    no_follow = _no_follow_flag()
    flags = os.O_RDONLY | no_follow | os.O_DIRECTORY
    descriptor = os.dup(directory_descriptor)
    try:
        for component in relative.parts:
            try:
                metadata = os.stat(
                    component,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                try:
                    os.mkdir(component, 0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
                metadata = os.stat(
                    component,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            if stat.S_ISLNK(metadata.st_mode):
                raise _SymlinkAccessError(
                    f"path component is a symlink: {component}"
                )
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            if not stat.S_ISDIR(os.fstat(next_descriptor).st_mode):
                os.close(next_descriptor)
                raise OSError(f"path component is not a directory: {component}")
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_directory_relative_from_descriptor_no_follow(
    directory_descriptor: int, relative: pathlib.Path
) -> int:
    relative = pathlib.Path(relative)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise OSError("directory path must be a non-empty safe relative path")
    no_follow = _no_follow_flag()
    flags = os.O_RDONLY | no_follow | os.O_DIRECTORY
    descriptor = os.dup(directory_descriptor)
    try:
        for component in relative.parts:
            metadata = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise _SymlinkAccessError(
                    f"path component is a symlink: {component}"
                )
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            opened_metadata = os.fstat(next_descriptor)
            if not stat.S_ISDIR(opened_metadata.st_mode):
                os.close(next_descriptor)
                raise OSError(f"path component is not a directory: {component}")
            if (metadata.st_dev, metadata.st_ino) != (
                opened_metadata.st_dev,
                opened_metadata.st_ino,
            ):
                os.close(next_descriptor)
                raise _ChangedFileError(
                    f"directory changed while it was opened: {component}"
                )
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_or_create_directory_relative_no_follow(
    directory: pathlib.Path, relative: pathlib.Path
) -> int:
    directory_descriptor = _open_directory_no_follow(directory)
    try:
        return _open_or_create_directory_relative_from_descriptor_no_follow(
            directory_descriptor, relative
        )
    finally:
        os.close(directory_descriptor)


def _directory_descriptor_matches_path(
    descriptor: int, path: pathlib.Path
) -> bool:
    try:
        _require_no_symlink_components(path)
        path_metadata = os.stat(
            _absolute_lexical(path),
            follow_symlinks=False,
        )
    except OSError:
        return False
    descriptor_metadata = os.fstat(descriptor)
    return (
        stat.S_ISDIR(path_metadata.st_mode)
        and path_metadata.st_dev == descriptor_metadata.st_dev
        and path_metadata.st_ino == descriptor_metadata.st_ino
    )


def _write_new_regular_no_follow(
    directory_descriptor: int, filename: str, content: bytes
) -> None:
    if pathlib.Path(filename).name != filename:
        raise OSError("output filename must be one path component")
    descriptor = os.open(
        filename,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
        0o644,
        dir_fd=directory_descriptor,
    )
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise OSError("output target must be one regular, unlinked path")
        output = os.fdopen(descriptor, "wb")
        descriptor = -1
        with output:
            output.write(content)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _require_no_symlink_components(path: pathlib.Path) -> pathlib.Path:
    """Return an absolute lexical path after rejecting every symlinked component."""
    path = pathlib.Path(path)
    if not path.is_absolute():
        path = pathlib.Path.cwd() / path
    current = pathlib.Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            return path
        if stat.S_ISLNK(mode):
            raise ValueError(f"path must not contain a symlink: {current}")
    return path


def _parse_brand_identity(manifest_text: str) -> dict[str, str]:
    method_versions: list[str] = []
    slugs: list[str] = []
    in_brand = False
    for line in manifest_text.splitlines():
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("method_version:"):
            match = _TOP_LEVEL_METHOD.fullmatch(line)
            if not match:
                raise ValueError("brand method_version is malformed")
            method_versions.append(_scalar(match))
            continue
        if not line[0].isspace():
            in_brand = bool(_BRAND.fullmatch(line))
            continue
        if in_brand and line.lstrip().startswith("slug:"):
            match = _INDENTED_SLUG.fullmatch(line)
            if not match:
                raise ValueError("brand slug is malformed")
            slugs.append(_scalar(match))

    if len(method_versions) != 1:
        raise ValueError("brand manifest must contain exactly one method_version")
    if len(slugs) != 1:
        raise ValueError("brand manifest must contain exactly one brand.slug")
    if not _SLUG.fullmatch(slugs[0]):
        raise ValueError("brand slug must be lowercase hyphenated text")
    _validate_method_version(method_versions[0])
    return {"brand_slug": slugs[0], "method_version": method_versions[0]}


def _load_brand_identity_from_descriptor(
    brand_descriptor: int, manifest: pathlib.Path
) -> dict[str, str]:
    try:
        manifest_text = _read_relative_text_from_descriptor_no_follow(
            brand_descriptor, pathlib.Path("brand.yml")
        )
    except FileNotFoundError as error:
        raise FileNotFoundError(f"brand manifest not found: {manifest}") from error
    except _SymlinkAccessError as error:
        raise ValueError(f"path must not contain a symlink: {manifest}") from error
    return _parse_brand_identity(manifest_text)


def load_brand_identity(brand_folder: pathlib.Path) -> dict[str, str]:
    """Return brand_slug and method_version from a validated local brand.yml."""
    brand_folder = _absolute_lexical(_require_no_symlink_components(brand_folder))
    if not brand_folder.is_dir():
        raise FileNotFoundError(f"brand folder not found: {brand_folder}")

    manifest = brand_folder / "brand.yml"
    _require_no_symlink_components(manifest)
    brand_descriptor = _open_directory_no_follow(brand_folder)
    try:
        if not _directory_descriptor_matches_path(brand_descriptor, brand_folder):
            raise OSError("brand directory changed while reading its manifest")
        identity = _load_brand_identity_from_descriptor(brand_descriptor, manifest)
        if not _directory_descriptor_matches_path(brand_descriptor, brand_folder):
            raise OSError("brand directory changed while reading its manifest")
        return identity
    finally:
        os.close(brand_descriptor)


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "\n" in value or "\r" in value:
        raise ValueError(f"{field} must be non-empty single-line text")
    return value


def _validate_run_id(run_id: object) -> str:
    if not isinstance(run_id, str):
        raise ValueError("run_id must be an ADR-YYYYMMDD-### identifier")
    match = RUN_ID.fullmatch(run_id)
    if not match or int(match.group("number")) < 1:
        raise ValueError("run_id must be an ADR-YYYYMMDD-### identifier")
    try:
        dt.datetime.strptime(match.group("date"), "%Y%m%d")
    except ValueError as error:
        raise ValueError("run_id must contain a valid calendar date") from error
    return run_id


def _analysis_root(brand_folder: pathlib.Path) -> pathlib.Path:
    outputs = brand_folder / "outputs"
    analysis = outputs / "ad-analysis"
    _require_no_symlink_components(outputs)
    _require_no_symlink_components(analysis)
    return analysis


def _next_run_id(analysis_root: pathlib.Path, date: dt.date) -> str:
    prefix = f"ADR-{date:%Y%m%d}-"
    numbers = []
    if analysis_root.is_dir():
        for path in analysis_root.iterdir():
            match = RUN_ID.fullmatch(path.name)
            if match and path.name.startswith(prefix):
                numbers.append(int(match.group("number")))
    next_number = max(numbers, default=0) + 1
    if next_number > 999:
        raise ValueError("no run identifiers remain for this date")
    return f"{prefix}{next_number:03d}"


def _next_run_id_from_descriptor(descriptor: int, date: dt.date) -> str:
    prefix = f"ADR-{date:%Y%m%d}-"
    numbers = []
    for name in os.listdir(descriptor):
        match = RUN_ID.fullmatch(name)
        if match and name.startswith(prefix):
            numbers.append(int(match.group("number")))
    next_number = max(numbers, default=0) + 1
    if next_number > 999:
        raise ValueError("no run identifiers remain for this date")
    return f"{prefix}{next_number:03d}"


def _migration_limitations(method_version: str) -> list[str]:
    if _validate_method_version(method_version) < (0, 4, 0):
        return [
            f"Brand method version {method_version} requires reviewed migration before controlled persistence."
        ]
    return []


def _render_run_readme(brand_folder: pathlib.Path, run_folder: pathlib.Path) -> str:
    if not RUN_TEMPLATE.is_file():
        raise FileNotFoundError(f"ad-analysis run template not found: {RUN_TEMPLATE}")
    command = (
        "python3 scripts/validate-ad-analysis-run.py "
        f"{shlex.quote(str(brand_folder.resolve()))} "
        f"{shlex.quote(str(run_folder.resolve()))} --write-audit"
    )
    return RUN_TEMPLATE.read_text(encoding="utf-8").replace(
        "__VALIDATION_COMMAND__", command
    )


def initialise_run(
    brand_folder: pathlib.Path,
    mode: str,
    product_id: str,
    market: str,
    run_id: str | None = None,
    today: dt.date | None = None,
) -> pathlib.Path:
    """Create a new ad-analysis run without copying inputs or changing strategy records."""
    brand_folder = _absolute_lexical(
        _require_no_symlink_components(pathlib.Path(brand_folder))
    )
    if not brand_folder.is_dir():
        raise FileNotFoundError(f"brand folder not found: {brand_folder}")
    manifest = brand_folder / "brand.yml"
    brand_descriptor = _open_directory_no_follow(brand_folder)
    try:
        identity = _load_brand_identity_from_descriptor(brand_descriptor, manifest)
        if mode not in MODES:
            raise ValueError(f"mode must be one of: {', '.join(sorted(MODES))}")
        product_id = _require_text(product_id, "product_id")
        market = _require_text(market, "market")
        if today is None:
            today = dt.date.today()
        if isinstance(today, dt.datetime) or not isinstance(today, dt.date):
            raise ValueError("today must be a date")
        if not _directory_descriptor_matches_path(brand_descriptor, brand_folder):
            raise OSError("brand directory changed during run initialisation")

        analysis_root = _analysis_root(brand_folder)
        analysis_descriptor = (
            _open_or_create_directory_relative_from_descriptor_no_follow(
                brand_descriptor, pathlib.Path("outputs/ad-analysis")
            )
        )
        try:
            if run_id is None:
                run_id = _next_run_id_from_descriptor(analysis_descriptor, today)
            else:
                run_id = _validate_run_id(run_id)
            run_folder = analysis_root / run_id

            requested_at = today.isoformat()
            intake = {
                "schema_version": 1,
                "run_id": run_id,
                "mode": mode,
                "brand_slug": identity["brand_slug"],
                "method_version": identity["method_version"],
                "market": market,
                "product_id": product_id,
                "account_timezone": "",
                "requester": "",
                "requested_at": requested_at,
                "ads": [],
                "sources": [],
                "performance": None,
                "known_limitations": _migration_limitations(identity["method_version"]),
            }
            intake_content = (
                json.dumps(intake, indent=2, ensure_ascii=False) + "\n"
            ).encode("utf-8")
            readme_content = _render_run_readme(brand_folder, run_folder).encode(
                "utf-8"
            )
            if not _directory_descriptor_matches_path(
                brand_descriptor, brand_folder
            ):
                raise OSError("brand directory changed during run initialisation")
            if not _directory_descriptor_matches_path(
                analysis_descriptor, analysis_root
            ):
                raise OSError("analysis directory changed during run initialisation")

            try:
                os.mkdir(run_id, 0o755, dir_fd=analysis_descriptor)
            except FileExistsError as error:
                raise FileExistsError(
                    f"analysis run already exists: {run_folder}"
                ) from error
            run_descriptor = os.open(
                run_id,
                os.O_RDONLY | os.O_DIRECTORY | _no_follow_flag(),
                dir_fd=analysis_descriptor,
            )
            try:
                if not stat.S_ISDIR(os.fstat(run_descriptor).st_mode):
                    raise OSError(f"analysis run is not a directory: {run_folder}")
                _write_new_regular_no_follow(
                    run_descriptor, "intake.json", intake_content
                )
                _write_new_regular_no_follow(
                    run_descriptor, "README.md", readme_content
                )
            finally:
                os.close(run_descriptor)
            if not _directory_descriptor_matches_path(
                brand_descriptor, brand_folder
            ):
                raise OSError("brand directory changed during run initialisation")
            if not _directory_descriptor_matches_path(
                analysis_descriptor, analysis_root
            ):
                raise OSError("analysis directory changed during run initialisation")
            return run_folder
        finally:
            os.close(analysis_descriptor)
    finally:
        os.close(brand_descriptor)


def load_intake(run_folder: pathlib.Path) -> dict[str, object]:
    """Load a run's JSON intake manifest without mutating it."""
    run_folder = _require_no_symlink_components(run_folder)
    intake_path = run_folder / "intake.json"
    _require_no_symlink_components(intake_path)
    if not intake_path.is_file():
        raise FileNotFoundError(f"intake manifest not found: {intake_path}")
    try:
        descriptor = _open_regular_relative_no_follow(
            run_folder, pathlib.Path("intake.json")
        )
    except FileNotFoundError as error:
        raise FileNotFoundError(f"intake manifest not found: {intake_path}") from error
    except _SymlinkAccessError as error:
        raise ValueError(f"path must not contain a symlink: {intake_path}") from error
    return _parse_intake_json(
        _read_limited_regular_bytes(descriptor, MAX_INTAKE_BYTES)
    )


def _inside(path: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


class _ValidationSession:
    """Retain one canonical run and intake identity for a complete validation transaction."""

    def __init__(
        self,
        brand_folder: pathlib.Path,
        run_folder: pathlib.Path,
        brand_descriptor: int,
        analysis_descriptor: int,
        run_descriptor: int,
        intake_descriptor: int,
        intake_identity: tuple[int, ...] | None,
        identity: dict[str, str],
        intake: dict[str, object],
        intake_error: str | None,
    ) -> None:
        self.brand_folder = brand_folder
        self.analysis_folder = brand_folder / "outputs" / "ad-analysis"
        self.run_folder = run_folder
        self.brand_descriptor = brand_descriptor
        self.analysis_descriptor = analysis_descriptor
        self.run_descriptor = run_descriptor
        self.intake_descriptor = intake_descriptor
        self.intake_identity = intake_identity
        self.identity = identity
        self.intake = intake
        self.intake_error = intake_error

    def __enter__(self) -> _ValidationSession:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        for name in (
            "intake_descriptor",
            "run_descriptor",
            "analysis_descriptor",
            "brand_descriptor",
        ):
            descriptor = getattr(self, name)
            if descriptor >= 0:
                os.close(descriptor)
                setattr(self, name, -1)

    def is_current(self) -> bool:
        if not _directory_descriptor_matches_path(
            self.brand_descriptor, self.brand_folder
        ):
            return False
        if not _directory_descriptor_matches_path(
            self.analysis_descriptor, self.analysis_folder
        ):
            return False
        if not _directory_descriptor_matches_path(
            self.run_descriptor, self.run_folder
        ):
            return False
        if self.intake_descriptor < 0 or self.intake_identity is None:
            return self.intake_error is not None
        try:
            path_metadata = os.stat(
                "intake.json",
                dir_fd=self.run_descriptor,
                follow_symlinks=False,
            )
            descriptor_metadata = os.fstat(self.intake_descriptor)
        except OSError:
            return False
        return (
            stat.S_ISREG(path_metadata.st_mode)
            and path_metadata.st_nlink == 1
            and _stable_file_identity(path_metadata) == self.intake_identity
            and _stable_file_identity(descriptor_metadata) == self.intake_identity
        )


def _open_validation_session(
    brand_folder: pathlib.Path, run_folder: pathlib.Path
) -> _ValidationSession:
    brand_folder = _absolute_lexical(pathlib.Path(brand_folder))
    run_folder = _absolute_lexical(pathlib.Path(run_folder))
    if not _inside(run_folder, brand_folder):
        raise ValueError("run folder must be inside the brand folder")
    expected_parent = brand_folder / "outputs" / "ad-analysis"
    if run_folder.parent != expected_parent:
        raise ValueError("run folder must be outputs/ad-analysis/<RUN_ID>")
    try:
        _validate_run_id(run_folder.name)
    except ValueError as error:
        raise ValueError("run folder must be outputs/ad-analysis/<RUN_ID>") from error

    brand_descriptor = -1
    analysis_descriptor = -1
    run_descriptor = -1
    intake_descriptor = -1
    try:
        brand_descriptor = _open_directory_no_follow(brand_folder)
        analysis_descriptor = _open_directory_relative_from_descriptor_no_follow(
            brand_descriptor, pathlib.Path("outputs/ad-analysis")
        )
        run_descriptor = _open_directory_relative_from_descriptor_no_follow(
            analysis_descriptor, pathlib.Path(run_folder.name)
        )
        if not (
            _directory_descriptor_matches_path(brand_descriptor, brand_folder)
            and _directory_descriptor_matches_path(
                analysis_descriptor, expected_parent
            )
            and _directory_descriptor_matches_path(run_descriptor, run_folder)
        ):
            raise OSError("run directory changed while validation was starting")

        identity = _load_brand_identity_from_descriptor(
            brand_descriptor, brand_folder / "brand.yml"
        )
        intake: dict[str, object] = {}
        intake_identity: tuple[int, ...] | None = None
        intake_error: str | None = None
        try:
            intake_descriptor = _open_regular_relative_from_descriptor_no_follow(
                run_descriptor, pathlib.Path("intake.json")
            )
            before = os.fstat(intake_descriptor)
            content = _read_limited_regular_bytes(
                intake_descriptor,
                MAX_INTAKE_BYTES,
                close_descriptor=False,
            )
            after = os.fstat(intake_descriptor)
            if _stable_file_identity(before) != _stable_file_identity(after):
                raise _ChangedFileError(
                    "intake manifest changed while it was being read"
                )
            intake_identity = _stable_file_identity(after)
            intake = _parse_intake_json(content)
        except FileNotFoundError:
            intake_error = f"intake manifest not found: {run_folder / 'intake.json'}"
        except _LinkedFileError:
            intake_error = "intake manifest must have exactly one hard link"
        except _ChangedFileError:
            intake_error = "intake manifest changed while it was being read"
        except (OSError, ValueError, json.JSONDecodeError) as error:
            intake_error = str(error)

        return _ValidationSession(
            brand_folder,
            run_folder,
            brand_descriptor,
            analysis_descriptor,
            run_descriptor,
            intake_descriptor,
            intake_identity,
            identity,
            intake,
            intake_error,
        )
    except BaseException:
        for descriptor in (
            intake_descriptor,
            run_descriptor,
            analysis_descriptor,
            brand_descriptor,
        ):
            if descriptor >= 0:
                os.close(descriptor)
        raise


def _is_text(value: object, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, str)
        and "\n" not in value
        and "\r" not in value
        and value == value.strip()
        and (allow_empty or bool(value))
    )


def _contains_credential(value: str) -> bool:
    return bool(
        _CREDENTIAL_FINGERPRINT.search(value)
        or _AUTHORIZATION_VALUE.search(value)
        or _PRIVATE_KEY_HEADER.search(value)
    )


def _credential_errors(value: object, path: str = "") -> list[str]:
    if isinstance(value, str):
        if _contains_credential(value):
            location = path or "intake"
            return [f"{location} must not contain a credential or access token"]
        return []
    if isinstance(value, list):
        errors: list[str] = []
        for index, item in enumerate(value):
            child = f"{path}[{index}]" if path else f"[{index}]"
            errors.extend(_credential_errors(item, child))
        return errors
    if isinstance(value, dict):
        errors = []
        for key, item in value.items():
            if isinstance(key, str) and _contains_credential(key):
                location = path or "intake"
                errors.append(
                    f"{location} key must not contain a credential or access token"
                )
                child = f"{location}.[REDACTED]"
            else:
                child = f"{path}.{key}" if path else str(key)
            errors.extend(_credential_errors(item, child))
        return errors
    return []


def _redact_credentials(value: str) -> str:
    redacted = _CREDENTIAL_FINGERPRINT.sub("[REDACTED]", value)
    redacted = _AUTHORIZATION_VALUE.sub("[REDACTED]", redacted)
    return _PRIVATE_KEY_HEADER.sub("[REDACTED]", redacted)


def _validation_result(
    status: str,
    errors: tuple[str, ...] | list[str],
    limitations: tuple[str, ...] | list[str] = (),
    inventory: tuple[tuple[str, str, str, str, str], ...] = (),
) -> ValidationResult:
    safe_errors = tuple(sorted({_redact_credentials(error) for error in errors}))
    safe_limitations = tuple(
        sorted({_redact_credentials(limitation) for limitation in limitations})
    )
    safe_inventory = tuple(
        tuple(_redact_credentials(field) for field in item) for item in inventory
    )
    return ValidationResult(status, safe_errors, safe_limitations, safe_inventory)


def _is_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_timezone(value: object) -> bool:
    if not _is_text(value):
        return False
    assert isinstance(value, str)
    try:
        ZoneInfo(value)
    except (ValueError, ZoneInfoNotFoundError):
        return False
    return True


def _unknown_key_errors(value: dict[str, object], allowed: set[str], path: str) -> list[str]:
    prefix = f"{path}." if path else ""
    return [f"{prefix}{key} is not allowed" for key in value if key not in allowed]


def _hash_regular_file(descriptor: int) -> str:
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("source is not a regular file")
        if before.st_nlink != 1:
            raise _LinkedFileError("source has multiple hard links")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(descriptor)
        if after.st_nlink != 1:
            raise _LinkedFileError("source has multiple hard links")
        if _stable_file_identity(before) != _stable_file_identity(after):
            raise _ChangedFileError("source changed while it was being read")
        return digest.hexdigest()
    finally:
        os.close(descriptor)


def _validate_source_file(
    source: dict[str, object],
    index: int,
    brand_folder: pathlib.Path,
    run_folder: pathlib.Path,
    run_descriptor: int,
    errors: list[str],
) -> str:
    location = source.get("location")
    path = f"sources[{index}].location"
    if not _is_text(location):
        return ""
    assert isinstance(location, str)
    if _URL_LIKE.match(location) or location.lower().startswith("file:"):
        errors.append(f"{path} must not be a URL")
        return ""
    relative = pathlib.Path(location)
    if relative.is_absolute():
        errors.append(f"{path} must be a relative path")
        return ""
    if ".." in relative.parts:
        errors.append(f"{path} must not contain '..' traversal")
        return ""
    candidate = _absolute_lexical(run_folder / relative)
    if not _inside(candidate, brand_folder):
        errors.append(f"{path} must stay inside the brand folder")
        return ""
    try:
        descriptor = _open_regular_relative_from_descriptor_no_follow(
            run_descriptor, relative
        )
    except _SymlinkAccessError:
        errors.append(f"{path} must not be a symlink")
        return ""
    except _LinkedFileError:
        errors.append(f"{path} must have exactly one hard link")
        return ""
    except _ChangedFileError:
        errors.append(f"{path} changed while it was being read")
        return ""
    except FileNotFoundError:
        errors.append(f"{path} must identify an existing regular file")
        return ""
    except (OSError, ValueError):
        errors.append(f"{path} could not be read as a regular non-symlink file")
        return ""
    try:
        actual_hash = _hash_regular_file(descriptor)
    except _LinkedFileError:
        errors.append(f"{path} must have exactly one hard link")
        return ""
    except _ChangedFileError:
        errors.append(f"{path} changed while it was being read")
        return ""
    except (OSError, ValueError):
        errors.append(f"{path} could not be read as a regular non-symlink file")
        return ""
    supplied_hash = source.get("sha256")
    if isinstance(supplied_hash, str) and _SHA256.fullmatch(supplied_hash):
        if supplied_hash.lower() != actual_hash:
            errors.append(f"sources[{index}].sha256 does not match the local file")
    return actual_hash


def _validate_sources(
    value: object,
    brand_folder: pathlib.Path,
    run_folder: pathlib.Path,
    run_descriptor: int,
    errors: list[str],
) -> tuple[set[str], tuple[tuple[str, str, str, str, str], ...]]:
    if not isinstance(value, list):
        errors.append("sources must be an array")
        return set(), ()
    source_ids: set[str] = set()
    inventory: list[tuple[str, str, str, str, str]] = []
    for index, item in enumerate(value):
        path = f"sources[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        errors.extend(_unknown_key_errors(item, _SOURCE_KEYS, path))
        for key in sorted(_SOURCE_KEYS - item.keys()):
            errors.append(f"{path}.{key} is required")

        source_id = item.get("source_id")
        if not _is_text(source_id):
            errors.append(f"{path}.source_id must be non-empty text")
        elif source_id in source_ids:
            errors.append(f"{path}.source_id duplicates {source_id}")
        else:
            source_ids.add(source_id)

        kind = item.get("kind")
        if not isinstance(kind, str) or kind not in _SOURCE_KINDS:
            errors.append(
                f"{path}.kind must be one of: {', '.join(sorted(_SOURCE_KINDS))}"
            )
        label = item.get("label")
        if not _is_text(label):
            errors.append(f"{path}.label must be non-empty text")
        location = item.get("location")
        if not _is_text(location):
            errors.append(f"{path}.location must be non-empty text")
        supplied_hash = item.get("sha256")
        if supplied_hash is not None and (
            not isinstance(supplied_hash, str) or not _SHA256.fullmatch(supplied_hash)
        ):
            errors.append(f"{path}.sha256 must be null or a 64-character hexadecimal digest")

        effective_hash = ""
        if kind == "file":
            effective_hash = _validate_source_file(
                item,
                index,
                brand_folder,
                run_folder,
                run_descriptor,
                errors,
            )
        elif isinstance(supplied_hash, str) and _SHA256.fullmatch(supplied_hash):
            effective_hash = supplied_hash.lower()
        inventory.append(
            (
                source_id if isinstance(source_id, str) else "",
                kind if isinstance(kind, str) else "",
                label if isinstance(label, str) else "",
                location if isinstance(location, str) else "",
                effective_hash,
            )
        )
    return source_ids, tuple(sorted(inventory))


def _validate_ads(
    value: object,
    source_ids: set[str],
    errors: list[str],
    limitations: list[str],
) -> set[str]:
    if not isinstance(value, list):
        errors.append("ads must be an array")
        return set()
    if not value:
        errors.append("ads must contain at least one ad")
    ad_ids: set[str] = set()
    for index, item in enumerate(value):
        path = f"ads[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        errors.extend(_unknown_key_errors(item, _AD_KEYS, path))
        for key in sorted(_AD_REQUIRED_KEYS - item.keys()):
            errors.append(f"{path}.{key} is required")

        ad_id = item.get("ad_id")
        if not _is_text(ad_id):
            errors.append(f"{path}.ad_id must be non-empty text")
        elif ad_id in ad_ids:
            errors.append(f"{path}.ad_id duplicates {ad_id}")
        else:
            ad_ids.add(ad_id)

        assets = item.get("asset_source_ids")
        if not isinstance(assets, list):
            errors.append(f"{path}.asset_source_ids must be an array")
        elif not assets:
            errors.append(f"{path}.asset_source_ids must contain at least one source ID")
        else:
            seen_assets: set[str] = set()
            for asset_index, source_id in enumerate(assets):
                if not _is_text(source_id):
                    errors.append(
                        f"{path}.asset_source_ids[{asset_index}] must be non-empty text"
                    )
                elif source_id in seen_assets:
                    errors.append(
                        f"{path}.asset_source_ids duplicates source ID {source_id}"
                    )
                elif source_id not in source_ids:
                    errors.append(
                        f"{path}.asset_source_ids references unknown source {source_id}"
                    )
                if isinstance(source_id, str):
                    seen_assets.add(source_id)

        for key in sorted(_AD_NULLABLE_TEXT_KEYS & item.keys()):
            if item[key] is not None and not isinstance(item[key], str):
                errors.append(f"{path}.{key} must be text or null")

        asset_type = item.get("asset_type")
        if asset_type is not None and (
            not isinstance(asset_type, str) or asset_type not in _ASSET_TYPES
        ):
            errors.append(
                f"{path}.asset_type must be null or one of: {', '.join(sorted(_ASSET_TYPES))}"
            )
        destination_type = item.get("destination_type")
        if destination_type is not None and (
            not isinstance(destination_type, str)
            or destination_type not in _DESTINATION_TYPES
        ):
            errors.append(
                f"{path}.destination_type must be null or one of: "
                f"{', '.join(sorted(_DESTINATION_TYPES))}"
            )
        contst = item.get("contst")
        if contst is not None and (
            not isinstance(contst, str) or _CONTST.fullmatch(contst) is None
        ):
            errors.append(f"{path}.contst must be null or a CONTST### identifier")
        source = item.get("source")
        if source is not None and (
            not isinstance(source, str) or source not in _AD_SOURCES
        ):
            errors.append(
                f"{path}.source must be null or one of: {', '.join(sorted(_AD_SOURCES))}"
            )
        awareness_code = item.get("awareness_code")
        if awareness_code is not None and (
            not isinstance(awareness_code, str)
            or awareness_code not in _AWARENESS_CODES
        ):
            errors.append(
                f"{path}.awareness_code must be null or one of: "
                f"{', '.join(sorted(_AWARENESS_CODES))}"
            )

        copy_fields = ("primary_text", "headline", "description", "cta")
        if not any(_is_text(item.get(key)) for key in copy_fields):
            limitations.append(f"{path} copy is unavailable")
        if not (
            _is_text(item.get("destination_url"))
            and _is_text(item.get("destination_type"))
        ):
            limitations.append(f"{path} destination is unavailable")
        if not _is_text(item.get("coordinate_key")):
            limitations.append(f"{path} strategic traceability is unavailable")
    return ad_ids


def _required_performance_error(errors: list[str], field: str) -> None:
    if field == "source_ids":
        errors.append("performance sources are required")
    else:
        errors.append(f"performance.{field} is required")


def _is_finite_number(value: object) -> bool:
    return type(value) in {int, float} and math.isfinite(value)


def _validate_logged_interventions(
    value: object, ad_ids: set[str], errors: list[str]
) -> None:
    if not isinstance(value, list):
        errors.append("performance.logged_interventions must be an array")
        return
    for index, intervention in enumerate(value):
        path = f"performance.logged_interventions[{index}]"
        if not isinstance(intervention, dict):
            errors.append(f"{path} must be an object")
            continue
        errors.extend(_unknown_key_errors(intervention, _INTERVENTION_KEYS, path))
        for key in sorted(_INTERVENTION_KEYS - intervention.keys()):
            errors.append(f"{path}.{key} is required")
        for key in ("occurred_at", "description"):
            if key in intervention and not _is_text(intervention[key]):
                errors.append(f"{path}.{key} must be non-empty text")
        scope = intervention.get("scope")
        if not isinstance(scope, str) or scope not in _INTERVENTION_SCOPES:
            errors.append(
                f"{path}.scope must be one of: {', '.join(sorted(_INTERVENTION_SCOPES))}"
            )
        ad_id = intervention.get("ad_id")
        if ad_id is not None and not _is_text(ad_id):
            errors.append(f"{path}.ad_id must be a non-empty ad ID or null")
        elif isinstance(ad_id, str) and ad_id not in ad_ids:
            errors.append(f"{path}.ad_id references unknown ad {ad_id}")


def _validate_account_norms(value: object, errors: list[str]) -> int:
    if not isinstance(value, list):
        errors.append("performance.account_norms must be an array")
        return 0
    for index, norm in enumerate(value):
        path = f"performance.account_norms[{index}]"
        if not isinstance(norm, dict):
            errors.append(f"{path} must be an object")
            continue
        errors.extend(_unknown_key_errors(norm, _ACCOUNT_NORM_KEYS, path))
        for key in sorted(_ACCOUNT_NORM_KEYS - norm.keys()):
            errors.append(f"{path}.{key} is required")
        for key in ("metric", "unit", "comparison_window", "source"):
            if key in norm and not _is_text(norm[key]):
                errors.append(f"{path}.{key} must be non-empty text")
        if "value" in norm and not _is_finite_number(norm["value"]):
            errors.append(f"{path}.value must be a finite number")
    return len(value)


def _validate_reference_ranges(value: object, errors: list[str]) -> str:
    if not isinstance(value, dict):
        errors.append("performance.reference_ranges must be an object")
        return ""
    errors.extend(
        _unknown_key_errors(value, _REFERENCE_RANGE_KEYS, "performance.reference_ranges")
    )
    for key in sorted(_REFERENCE_RANGE_KEYS - value.keys()):
        errors.append(f"performance.reference_ranges.{key} is required")
    status = value.get("status")
    if not isinstance(status, str) or status not in _REFERENCE_RANGE_STATUSES:
        errors.append(
            "performance.reference_ranges.status must be one of: permitted, unavailable"
        )
        status = ""
    sources = value.get("sources")
    if not isinstance(sources, list):
        errors.append("performance.reference_ranges.sources must be an array")
        return status if isinstance(status, str) else ""
    seen: set[str] = set()
    for index, source in enumerate(sources):
        if not _is_text(source):
            errors.append(
                f"performance.reference_ranges.sources[{index}] must be non-empty text"
            )
        elif source in seen:
            errors.append(
                f"performance.reference_ranges.sources duplicates {source}"
            )
        else:
            seen.add(source)
    if status == "permitted" and not sources:
        errors.append(
            "performance.reference_ranges.sources must name at least one permitted source"
        )
    if status == "unavailable" and sources:
        errors.append(
            "performance.reference_ranges.sources must be empty when ranges are unavailable"
        )
    return status


def _validate_threshold_basis(
    value: object, ad_ids: set[str], errors: list[str]
) -> None:
    if not isinstance(value, list):
        errors.append("performance.threshold_basis must be an array")
        return
    if not value:
        errors.append("performance.threshold_basis must contain at least one threshold")
    for index, basis in enumerate(value):
        path = f"performance.threshold_basis[{index}]"
        if not isinstance(basis, dict):
            errors.append(f"{path} must be an object")
            continue
        errors.extend(_unknown_key_errors(basis, _THRESHOLD_BASIS_KEYS, path))
        for key in sorted(_THRESHOLD_BASIS_KEYS - basis.keys()):
            errors.append(f"{path}.{key} is required")
        for key in ("metric", "comparison_window", "unit", "source"):
            if key in basis and not _is_text(basis[key]):
                errors.append(f"{path}.{key} must be non-empty text")
        for key in ("baseline", "threshold"):
            if key in basis and not _is_finite_number(basis[key]):
                errors.append(f"{path}.{key} must be a finite number")
        ad_id = basis.get("ad_id")
        if ad_id is not None and not _is_text(ad_id):
            errors.append(f"{path}.ad_id must be a non-empty ad ID or null")
        elif isinstance(ad_id, str) and ad_id not in ad_ids:
            errors.append(f"{path}.ad_id references unknown ad {ad_id}")


def _validate_optional_performance_shape(
    value: dict[str, object],
    source_ids: set[str],
    ad_ids: set[str],
    errors: list[str],
) -> None:
    errors.extend(_unknown_key_errors(value, _PERFORMANCE_KEYS, "performance"))
    if "source_ids" in value:
        performance_sources = value["source_ids"]
        if not isinstance(performance_sources, list):
            errors.append("performance.source_ids must be an array")
        else:
            seen_sources: set[str] = set()
            for index, source_id in enumerate(performance_sources):
                if not _is_text(source_id):
                    errors.append(
                        f"performance.source_ids[{index}] must be non-empty text"
                    )
                elif source_id in seen_sources:
                    errors.append(f"performance.source_ids duplicates {source_id}")
                elif source_id not in source_ids:
                    errors.append(
                        f"performance.source_ids references unknown source {source_id}"
                    )
                if isinstance(source_id, str):
                    seen_sources.add(source_id)
    if "date_range" in value:
        date_range = value["date_range"]
        if not isinstance(date_range, dict):
            errors.append("performance.date_range must be an object")
        else:
            errors.extend(
                _unknown_key_errors(
                    date_range, {"start", "end"}, "performance.date_range"
                )
            )
            parsed: dict[str, dt.date] = {}
            for endpoint in ("start", "end"):
                if endpoint in date_range:
                    raw = date_range[endpoint]
                    if not _is_date(raw):
                        errors.append(
                            f"performance.date_range.{endpoint} must be an ISO calendar date"
                        )
                    else:
                        parsed[endpoint] = dt.date.fromisoformat(raw)
            if (
                parsed.get("start")
                and parsed.get("end")
                and parsed["end"] < parsed["start"]
            ):
                errors.append("performance.date_range.end must not precede start")
    if "attribution" in value and not _is_text(value["attribution"]):
        errors.append("performance.attribution must be non-empty text")
    if "currency" in value and (
        not isinstance(value["currency"], str)
        or re.fullmatch(r"[A-Z]{3}", value["currency"]) is None
    ):
        errors.append("performance.currency must be a three-letter uppercase code")
    if "aggregation_level" in value and value["aggregation_level"] != "ad":
        errors.append("performance.aggregation_level must equal ad")
    if "field_mapping" in value:
        field_mapping = value["field_mapping"]
        if not isinstance(field_mapping, dict):
            errors.append("performance.field_mapping must be an object")
        else:
            errors.extend(
                _unknown_key_errors(
                    field_mapping, _FIELD_MAPPING_KEYS, "performance.field_mapping"
                )
            )
            for field, mapped_name in field_mapping.items():
                if field in _FIELD_MAPPING_KEYS and not _is_text(mapped_name):
                    errors.append(
                        f"performance.field_mapping.{field} must be non-empty text"
                    )
    if "ad_mapping" in value:
        ad_mapping = value["ad_mapping"]
        if not isinstance(ad_mapping, dict):
            errors.append("performance.ad_mapping must be an object")
        else:
            for external_id, ad_id in ad_mapping.items():
                if not _is_text(external_id):
                    errors.append("performance.ad_mapping keys must be non-empty text")
                if not _is_text(ad_id):
                    errors.append(
                        f"performance.ad_mapping[{external_id!r}] must be a non-empty ad ID"
                    )
                elif ad_id not in ad_ids:
                    errors.append(f"performance.ad_mapping references unknown ad {ad_id}")
    if "logged_interventions" in value:
        _validate_logged_interventions(value["logged_interventions"], ad_ids, errors)
    if "account_norms" in value:
        _validate_account_norms(value["account_norms"], errors)
    if "reference_ranges" in value:
        _validate_reference_ranges(value["reference_ranges"], errors)
    if "threshold_basis" in value:
        _validate_threshold_basis(value["threshold_basis"], ad_ids, errors)


def _validate_performance(
    value: object,
    source_ids: set[str],
    ad_ids: set[str],
    errors: list[str],
    limitations: list[str],
) -> None:
    if not isinstance(value, dict):
        for field in (
            "source_ids",
            "date_range",
            "attribution",
            "currency",
            "aggregation_level",
            "field_mapping.ad_id",
            "field_mapping.spend",
            "field_mapping.purchases",
            "ad_mapping",
            "logged_interventions",
            "account_norms",
            "reference_ranges",
            "threshold_basis",
        ):
            _required_performance_error(errors, field)
        return
    errors.extend(_unknown_key_errors(value, _PERFORMANCE_KEYS, "performance"))

    performance_sources = value.get("source_ids")
    if not isinstance(performance_sources, list) or not performance_sources:
        _required_performance_error(errors, "source_ids")
    else:
        seen_sources: set[str] = set()
        for index, source_id in enumerate(performance_sources):
            if not _is_text(source_id):
                errors.append(f"performance.source_ids[{index}] must be non-empty text")
            elif source_id in seen_sources:
                errors.append(f"performance.source_ids duplicates {source_id}")
            elif source_id not in source_ids:
                errors.append(
                    f"performance.source_ids references unknown source {source_id}"
                )
            if isinstance(source_id, str):
                seen_sources.add(source_id)

    date_range = value.get("date_range")
    if not isinstance(date_range, dict):
        _required_performance_error(errors, "date_range")
    else:
        errors.extend(
            _unknown_key_errors(date_range, {"start", "end"}, "performance.date_range")
        )
        dates: dict[str, dt.date] = {}
        for endpoint in ("start", "end"):
            raw = date_range.get(endpoint)
            if not _is_date(raw):
                errors.append(
                    f"performance.date_range.{endpoint} must be an ISO calendar date"
                )
            else:
                dates[endpoint] = dt.date.fromisoformat(raw)
        if dates.get("start") and dates.get("end") and dates["end"] < dates["start"]:
            errors.append("performance.date_range.end must not precede start")

    if not _is_text(value.get("attribution")):
        _required_performance_error(errors, "attribution")
    currency = value.get("currency")
    if not isinstance(currency, str) or re.fullmatch(r"[A-Z]{3}", currency) is None:
        _required_performance_error(errors, "currency")
    if value.get("aggregation_level") != "ad":
        _required_performance_error(errors, "aggregation_level")

    field_mapping = value.get("field_mapping")
    if not isinstance(field_mapping, dict):
        for field in sorted(_REQUIRED_FIELD_MAPPINGS):
            _required_performance_error(errors, f"field_mapping.{field}")
        limitations.extend(
            (
                "optional funnel field mappings are unavailable",
                "optional video field mappings are unavailable",
            )
        )
    else:
        errors.extend(
            _unknown_key_errors(
                field_mapping, _FIELD_MAPPING_KEYS, "performance.field_mapping"
            )
        )
        for field in sorted(_REQUIRED_FIELD_MAPPINGS):
            if not _is_text(field_mapping.get(field)):
                _required_performance_error(errors, f"field_mapping.{field}")
        for field, mapped_name in field_mapping.items():
            if field in _FIELD_MAPPING_KEYS and not _is_text(mapped_name):
                errors.append(f"performance.field_mapping.{field} must be non-empty text")
        if not (_FUNNEL_FIELD_MAPPINGS & field_mapping.keys()):
            limitations.append("optional funnel field mappings are unavailable")
        if not (_VIDEO_FIELD_MAPPINGS & field_mapping.keys()):
            limitations.append("optional video field mappings are unavailable")

    ad_mapping = value.get("ad_mapping")
    if not isinstance(ad_mapping, dict) or not ad_mapping:
        errors.append(
            "performance.ad_mapping must contain at least one spend-bearing source ad"
        )
    else:
        for external_id, ad_id in ad_mapping.items():
            if not _is_text(external_id):
                errors.append("performance.ad_mapping keys must be non-empty text")
            if not _is_text(ad_id):
                errors.append(
                    f"performance.ad_mapping[{external_id!r}] must be a non-empty ad ID"
                )
            elif ad_id not in ad_ids:
                errors.append(f"performance.ad_mapping references unknown ad {ad_id}")

    if "logged_interventions" not in value:
        _required_performance_error(errors, "logged_interventions")
    else:
        _validate_logged_interventions(value["logged_interventions"], ad_ids, errors)

    if "account_norms" not in value:
        _required_performance_error(errors, "account_norms")
        account_norm_count = 0
    else:
        account_norm_count = _validate_account_norms(value["account_norms"], errors)

    if "reference_ranges" not in value:
        _required_performance_error(errors, "reference_ranges")
        reference_status = ""
    else:
        reference_status = _validate_reference_ranges(
            value["reference_ranges"], errors
        )

    if "threshold_basis" not in value:
        _required_performance_error(errors, "threshold_basis")
    else:
        _validate_threshold_basis(value["threshold_basis"], ad_ids, errors)

    if account_norm_count == 0 and reference_status == "unavailable":
        limitations.append(
            "account norms and permitted reference ranges are unavailable; "
            "benchmark comparisons are prohibited"
        )


def _validate_session(session: _ValidationSession) -> ValidationResult:
    errors: list[str] = []
    limitations: list[str] = []
    inventory: tuple[tuple[str, str, str, str, str], ...] = ()
    if session.intake_error is not None:
        return _validation_result("blocked", (session.intake_error,))
    if not session.is_current():
        return _validation_result(
            "blocked", ("run or intake identity changed during validation",)
        )

    brand_folder = session.brand_folder
    run_folder = session.run_folder
    identity = session.identity
    intake = session.intake

    errors.extend(_credential_errors(intake))
    errors.extend(_unknown_key_errors(intake, _TOP_LEVEL_KEYS, ""))
    for field in sorted(_TOP_LEVEL_KEYS - intake.keys()):
        errors.append(f"{field} is required")

    if (
        type(intake.get("schema_version")) is not int
        or intake.get("schema_version") != 1
    ):
        errors.append("schema_version must equal integer 1")
    run_id = intake.get("run_id")
    try:
        validated_run_id = _validate_run_id(run_id)
    except ValueError as error:
        errors.append(str(error))
    else:
        if validated_run_id != run_folder.name:
            errors.append(
                f"intake run {validated_run_id} does not match run folder {run_folder.name}"
            )
    mode = intake.get("mode")
    if not isinstance(mode, str) or mode not in MODES:
        errors.append(f"mode must be one of: {', '.join(sorted(MODES))}")
    brand_slug = intake.get("brand_slug")
    if not _is_text(brand_slug):
        errors.append("brand_slug must be non-empty text")
    elif brand_slug != identity["brand_slug"]:
        errors.append(
            f"intake brand {brand_slug} does not match manifest brand {identity['brand_slug']}"
        )
    method_version = intake.get("method_version")
    if not isinstance(method_version, str) or not _VERSION.fullmatch(method_version):
        errors.append("method_version must use major.minor.patch format")
    elif method_version != identity["method_version"]:
        errors.append(
            f"intake method version {method_version} does not match manifest method version "
            f"{identity['method_version']}"
        )
    for field in ("market", "product_id"):
        if not _is_text(intake.get(field)):
            errors.append(f"{field} must be non-empty text")
    for field in ("account_timezone", "requester"):
        if not _is_text(intake.get(field), allow_empty=True):
            errors.append(f"{field} must be single-line text")
    if mode == "performance-diagnosis" and not _is_timezone(
        intake.get("account_timezone")
    ):
        errors.append(
            "account_timezone must be a valid IANA timezone for Performance Diagnosis"
        )
    if not _is_date(intake.get("requested_at")):
        errors.append("requested_at must be an ISO calendar date")

    known_limitations = intake.get("known_limitations")
    if not isinstance(known_limitations, list):
        errors.append("known_limitations must be an array")
    else:
        seen_limitations: set[str] = set()
        for index, limitation in enumerate(known_limitations):
            if not _is_text(limitation):
                errors.append(f"known_limitations[{index}] must be non-empty text")
            elif limitation in seen_limitations:
                errors.append(f"known_limitations duplicates {limitation}")
            else:
                limitations.append(limitation)
                seen_limitations.add(limitation)
    limitations.extend(_migration_limitations(identity["method_version"]))

    source_ids, inventory = _validate_sources(
        intake.get("sources"),
        brand_folder,
        run_folder,
        session.run_descriptor,
        errors,
    )
    ad_ids = _validate_ads(intake.get("ads"), source_ids, errors, limitations)
    if mode == "performance-diagnosis":
        _validate_performance(
            intake.get("performance"), source_ids, ad_ids, errors, limitations
        )
    elif mode == "creative-audit":
        optional_performance = intake.get("performance")
        if optional_performance is not None and not isinstance(
            optional_performance, dict
        ):
            errors.append("performance must be an object or null")
        elif isinstance(optional_performance, dict):
            _validate_optional_performance_shape(
                optional_performance, source_ids, ad_ids, errors
            )

    if not session.is_current():
        errors.append("run or intake identity changed during validation")
    status = "blocked" if errors else "limited" if limitations else "ready"
    return _validation_result(status, errors, limitations, inventory)


def validate_run(
    brand_folder: pathlib.Path, run_folder: pathlib.Path
) -> ValidationResult:
    """Validate one canonical brand-scoped run without mutating any record."""
    try:
        session = _open_validation_session(brand_folder, run_folder)
    except _SymlinkAccessError:
        return _validation_result("blocked", ("run folder must not be a symlink",))
    except (FileNotFoundError, OSError, ValueError) as error:
        return _validation_result("blocked", (str(error),))
    with session:
        return _validate_session(session)


def _audit_value(value: object) -> str:
    if isinstance(value, str) and _contains_credential(value):
        return json.dumps("[REDACTED]")
    if isinstance(value, (str, int)) and not isinstance(value, bool):
        return _redact_credentials(json.dumps(value, ensure_ascii=False))
    if value is None:
        return "null"
    return "invalid or unavailable"


def _audit_list(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def render_input_audit(intake: dict[str, object], result: ValidationResult) -> str:
    """Render a deterministic Markdown audit from untrusted intake metadata."""
    ads = intake.get("ads")
    performance = intake.get("performance")
    lines = [
        "# Ad analysis input audit",
        "",
        "## Run identity",
        "",
        f"- Run ID: {_audit_value(intake.get('run_id'))}",
        f"- Brand: {_audit_value(intake.get('brand_slug'))}",
        f"- Mode: {_audit_value(intake.get('mode'))}",
        f"- Method version: {_audit_value(intake.get('method_version'))}",
        f"- Market: {_audit_value(intake.get('market'))}",
        f"- Product: {_audit_value(intake.get('product_id'))}",
        "",
        "## Source inventory",
        "",
    ]
    if result.inventory:
        for source_id, kind, label, location, sha256 in result.inventory:
            lines.append(
                "- "
                f"{_audit_value(source_id)} | kind={_audit_value(kind)} | "
                f"label={_audit_value(label)} | location={_audit_value(location)} | "
                f"sha256={_audit_value(sha256 or None)}"
            )
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Ad coverage",
            "",
            f"- Intake ads: {len(ads) if isinstance(ads, list) else 'invalid or unavailable'}",
        ]
    )
    if isinstance(ads, list):
        for index, ad in enumerate(ads):
            ad_id = ad.get("ad_id") if isinstance(ad, dict) else None
            lines.append(f"- ads[{index}]: {_audit_value(ad_id)}")
    lines.extend(
        [
            "",
            "## Performance coverage",
            "",
            "- Performance input: "
            + ("supplied" if isinstance(performance, dict) else "not supplied"),
            "",
            "## Readiness",
            "",
            f"Input readiness: `{result.status}`",
            "",
            "This input-readiness label is distinct from the later Creative Audit per-ad "
            "outcomes `ready`, `revise` and `block`.",
            "",
            "## Errors",
            "",
        ]
    )
    lines.extend(_audit_list(result.errors))
    lines.extend(["", "## Limitations", ""])
    lines.extend(_audit_list(result.limitations))
    return _redact_credentials("\n".join(lines) + "\n")
