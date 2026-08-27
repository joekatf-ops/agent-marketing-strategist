"""Create portable, brand-scoped ad-analysis run manifests."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shlex
import stat
from typing import NamedTuple


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUN_TEMPLATE = ROOT / "templates" / "brand-folder" / "outputs" / "ad-analysis" / "README.md"
MODES = {"creative-audit", "performance-diagnosis"}
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
    "primary_text",
    "headline",
    "description",
    "cta",
    "destination_url",
    "destination_type",
    "coordinate_key",
}
_AD_OPTIONAL_TEXT_KEYS = _AD_KEYS - {"ad_id", "asset_source_ids"}
_PERFORMANCE_KEYS = {
    "source_ids",
    "date_range",
    "attribution",
    "currency",
    "aggregation_level",
    "field_mapping",
    "ad_mapping",
    "logged_interventions",
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


def _open_regular_relative_no_follow(
    directory: pathlib.Path, relative: pathlib.Path
) -> int:
    relative = pathlib.Path(relative)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise OSError("file path must be a non-empty safe relative path")
    no_follow = _no_follow_flag()
    directory_flags = os.O_RDONLY | no_follow | os.O_DIRECTORY
    descriptor = _open_directory_no_follow(directory)
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
        if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
            os.close(file_descriptor)
            raise OSError(f"file is not regular: {filename}")
        return file_descriptor
    finally:
        os.close(descriptor)


def _read_relative_text_no_follow(
    directory: pathlib.Path, relative: pathlib.Path
) -> str:
    descriptor = _open_regular_relative_no_follow(directory, relative)
    with os.fdopen(descriptor, "r", encoding="utf-8") as file:
        return file.read()


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


def load_brand_identity(brand_folder: pathlib.Path) -> dict[str, str]:
    """Return brand_slug and method_version from a validated local brand.yml."""
    brand_folder = _require_no_symlink_components(brand_folder)
    if not brand_folder.is_dir():
        raise FileNotFoundError(f"brand folder not found: {brand_folder}")

    manifest = brand_folder / "brand.yml"
    _require_no_symlink_components(manifest)
    if not manifest.is_file():
        raise FileNotFoundError(f"brand manifest not found: {manifest}")

    method_versions: list[str] = []
    slugs: list[str] = []
    in_brand = False
    try:
        manifest_text = _read_relative_text_no_follow(
            brand_folder, pathlib.Path("brand.yml")
        )
    except FileNotFoundError as error:
        raise FileNotFoundError(f"brand manifest not found: {manifest}") from error
    except _SymlinkAccessError as error:
        raise ValueError(f"path must not contain a symlink: {manifest}") from error
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
    brand_folder = pathlib.Path(brand_folder)
    identity = load_brand_identity(brand_folder)
    if mode not in MODES:
        raise ValueError(f"mode must be one of: {', '.join(sorted(MODES))}")
    product_id = _require_text(product_id, "product_id")
    market = _require_text(market, "market")
    if today is None:
        today = dt.date.today()
    if not isinstance(today, dt.date):
        raise ValueError("today must be a date")

    analysis_root = _analysis_root(brand_folder)
    if run_id is None:
        run_id = _next_run_id(analysis_root, today)
    else:
        run_id = _validate_run_id(run_id)
    run_folder = analysis_root / run_id
    _require_no_symlink_components(run_folder)
    if run_folder.exists() or run_folder.is_symlink():
        raise FileExistsError(f"analysis run already exists: {run_folder}")

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
    analysis_root.mkdir(parents=True, exist_ok=True)
    run_folder.mkdir()
    (run_folder / "intake.json").write_text(
        json.dumps(intake, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (run_folder / "README.md").write_text(
        _render_run_readme(brand_folder, run_folder), encoding="utf-8"
    )
    return run_folder


def load_intake(run_folder: pathlib.Path) -> dict[str, object]:
    """Load a run's JSON intake manifest without mutating it."""
    run_folder = _require_no_symlink_components(run_folder)
    intake_path = run_folder / "intake.json"
    _require_no_symlink_components(intake_path)
    if not intake_path.is_file():
        raise FileNotFoundError(f"intake manifest not found: {intake_path}")
    try:
        intake_text = _read_relative_text_no_follow(
            run_folder, pathlib.Path("intake.json")
        )
    except FileNotFoundError as error:
        raise FileNotFoundError(f"intake manifest not found: {intake_path}") from error
    except _SymlinkAccessError as error:
        raise ValueError(f"path must not contain a symlink: {intake_path}") from error
    intake = json.loads(intake_text)
    if not isinstance(intake, dict):
        raise ValueError("intake manifest must contain a JSON object")
    return intake


def _inside(path: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _is_text(value: object, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, str)
        and "\n" not in value
        and "\r" not in value
        and value == value.strip()
        and (allow_empty or bool(value))
    )


def _is_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _unknown_key_errors(value: dict[str, object], allowed: set[str], path: str) -> list[str]:
    prefix = f"{path}." if path else ""
    return [f"{prefix}{key} is not allowed" for key in value if key not in allowed]


def _hash_regular_file(descriptor: int) -> str:
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("source is not a regular file")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)
    finally:
        os.close(descriptor)


def _validate_source_file(
    source: dict[str, object],
    index: int,
    brand_folder: pathlib.Path,
    run_folder: pathlib.Path,
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
        descriptor = _open_regular_relative_no_follow(run_folder, relative)
    except _SymlinkAccessError:
        errors.append(f"{path} must not be a symlink")
        return ""
    except FileNotFoundError:
        errors.append(f"{path} must identify an existing regular file")
        return ""
    except (OSError, ValueError):
        errors.append(f"{path} could not be read as a regular non-symlink file")
        return ""
    try:
        actual_hash = _hash_regular_file(descriptor)
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
                item, index, brand_folder, run_folder, errors
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
        for key in sorted({"ad_id", "asset_source_ids"} - item.keys()):
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
            for asset_index, source_id in enumerate(assets):
                if not _is_text(source_id):
                    errors.append(
                        f"{path}.asset_source_ids[{asset_index}] must be non-empty text"
                    )
                elif source_id not in source_ids:
                    errors.append(
                        f"{path}.asset_source_ids references unknown source {source_id}"
                    )

        for key in sorted(_AD_OPTIONAL_TEXT_KEYS & item.keys()):
            if item[key] is not None and not isinstance(item[key], str):
                errors.append(f"{path}.{key} must be text or null")

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
            for index, source_id in enumerate(performance_sources):
                if not _is_text(source_id):
                    errors.append(
                        f"performance.source_ids[{index}] must be non-empty text"
                    )
                elif source_id not in source_ids:
                    errors.append(
                        f"performance.source_ids references unknown source {source_id}"
                    )
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
    for field in ("attribution", "currency", "aggregation_level"):
        if field in value and not _is_text(value[field]):
            errors.append(f"performance.{field} must be non-empty text")
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
    if "logged_interventions" in value and not isinstance(
        value["logged_interventions"], list
    ):
        errors.append("performance.logged_interventions must be an array")


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
        ):
            _required_performance_error(errors, field)
        return
    errors.extend(_unknown_key_errors(value, _PERFORMANCE_KEYS, "performance"))

    performance_sources = value.get("source_ids")
    if not isinstance(performance_sources, list) or not performance_sources:
        _required_performance_error(errors, "source_ids")
    else:
        for index, source_id in enumerate(performance_sources):
            if not _is_text(source_id):
                errors.append(f"performance.source_ids[{index}] must be non-empty text")
            elif source_id not in source_ids:
                errors.append(
                    f"performance.source_ids references unknown source {source_id}"
                )

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

    for field in ("attribution", "currency", "aggregation_level"):
        if not _is_text(value.get(field)):
            _required_performance_error(errors, field)

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

    interventions = value.get("logged_interventions")
    if not isinstance(interventions, list):
        _required_performance_error(errors, "logged_interventions")


def validate_run(
    brand_folder: pathlib.Path, run_folder: pathlib.Path
) -> ValidationResult:
    """Validate one brand-scoped run without mutating intake or controlled records."""
    errors: list[str] = []
    limitations: list[str] = []
    inventory: tuple[tuple[str, str, str, str, str], ...] = ()
    brand_folder = _absolute_lexical(pathlib.Path(brand_folder))
    run_folder = _absolute_lexical(pathlib.Path(run_folder))

    try:
        _require_no_symlink_components(brand_folder)
    except ValueError as error:
        return ValidationResult("blocked", (str(error),), (), ())
    if not _inside(run_folder, brand_folder):
        return ValidationResult(
            "blocked", ("run folder must be inside the brand folder",), (), ()
        )
    try:
        _require_no_symlink_components(run_folder)
    except ValueError:
        return ValidationResult("blocked", ("run folder must not be a symlink",), (), ())
    if not run_folder.is_dir():
        return ValidationResult("blocked", ("run folder not found",), (), ())

    try:
        identity = load_brand_identity(brand_folder)
    except (FileNotFoundError, OSError, ValueError) as error:
        return ValidationResult("blocked", (str(error),), (), ())
    try:
        intake = load_intake(run_folder)
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as error:
        return ValidationResult("blocked", (str(error),), (), ())

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
    if not _is_date(intake.get("requested_at")):
        errors.append("requested_at must be an ISO calendar date")

    known_limitations = intake.get("known_limitations")
    if not isinstance(known_limitations, list):
        errors.append("known_limitations must be an array")
    else:
        for index, limitation in enumerate(known_limitations):
            if not _is_text(limitation):
                errors.append(f"known_limitations[{index}] must be non-empty text")
            else:
                limitations.append(limitation)
    limitations.extend(_migration_limitations(identity["method_version"]))

    source_ids, inventory = _validate_sources(
        intake.get("sources"), brand_folder, run_folder, errors
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

    sorted_errors = tuple(sorted(set(errors)))
    sorted_limitations = tuple(sorted(set(limitations)))
    status = "blocked" if sorted_errors else "limited" if sorted_limitations else "ready"
    return ValidationResult(status, sorted_errors, sorted_limitations, inventory)


def _audit_value(value: object) -> str:
    if isinstance(value, (str, int)) and not isinstance(value, bool):
        return json.dumps(value, ensure_ascii=False)
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
    return "\n".join(lines) + "\n"
