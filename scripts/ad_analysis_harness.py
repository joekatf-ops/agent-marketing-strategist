"""Create portable, brand-scoped ad-analysis run manifests."""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import shlex
import stat


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


def _scalar(match: re.Match[str]) -> str:
    return next(value for value in match.group("double", "single", "bare") if value is not None)


def _validate_method_version(method_version: str) -> tuple[int, int, int]:
    match = _VERSION.fullmatch(method_version)
    if not match:
        raise ValueError("brand method_version must use major.minor.patch format")
    return tuple(int(match.group(name)) for name in ("major", "minor", "patch"))


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
    for line in manifest.read_text(encoding="utf-8").splitlines():
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
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    if not isinstance(intake, dict):
        raise ValueError("intake manifest must contain a JSON object")
    return intake
