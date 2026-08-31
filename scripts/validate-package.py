#!/usr/bin/env python3
"""Validate routing, frozen examples and duplicated entrypoints."""

from __future__ import annotations

import ast
import collections
import importlib.util
import json
import math
import pathlib
import re
import sysconfig
import sys


ROUTED_PATH = re.compile(
    r"`((?:references|contracts|examples|connectors|schemas)/[^`]+\.(?:md|json))`"
)
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
VERSION_DECLARATIONS = (
    (
        "README.md",
        re.compile(r"^\*\*Version:\*\*[ \t]*(?P<version>[^\s]+)[ \t]*$", re.MULTILINE),
        "the package version",
    ),
    (
        "templates/brand-folder/brand.yml",
        re.compile(
            r'^method_version:[ \t]*"(?P<version>[^"]+)"[ \t]*$', re.MULTILINE
        ),
        "method_version",
    ),
)
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|\b(?:TODO|TBD)\b")
TEMPLATE_TEST_REGISTER = "templates/brand-folder/strategy/test-register.yml"
CONTST_TEST_ID = re.compile(
    r"^[ \t-]*test_id:[ \t]*(CONTST(?P<number>[0-9]{3}))[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
V03_REQUIRED_FILES = (
    "references/18-master-creative-strategy.md",
    "contracts/campaign-launch-plan.md",
    "contracts/destination-handoff.md",
    "examples/campaign-launch-plan.md",
    "examples/destination-handoff.md",
    "connectors/notion-composio.md",
)
V04_REQUIRED_FILES = (
    "contracts/brand-readiness.md",
    "contracts/customer-intelligence.md",
    "contracts/concept-batch.md",
    "contracts/hook-batch.md",
    "contracts/ad-copy.md",
    "contracts/video-script.md",
    "contracts/static-spec.md",
    "contracts/learning-update.md",
    "contracts/campaign-launch-plan.md",
    "contracts/destination-handoff.md",
    "contracts/ad-diagnosis.md",
    "contracts/creative-audit.md",
    "references/19-ad-analysis-harness.md",
    "examples/ad-analysis-intake.json",
    "examples/creative-audit.md",
    "examples/ad-diagnosis.md",
    "examples/ad-diagnosis-intake.json",
    "examples/ad-diagnosis-input-audit.md",
    "examples/ad-diagnosis-performance.csv",
    "examples/ad-diagnosis-test-register-patch.yml",
)
CREATIVE_AUDIT_SECTIONS = (
    "Input coverage and limitations",
    "Ad identity and traceability",
    "Who x Primary Problem clarity",
    "Awareness job and messaging route",
    "Hook coherence and body handoff",
    "Proof, offer, claims and CTA",
    "Format, visual communication and production execution",
    "Destination continuity",
    "Ranked issues with evidence",
    "Pre-launch outcome by ad",
    "What cannot be concluded without performance data",
)
PERFORMANCE_ACTIONS = frozenset({"keep", "itr", "stop", "scale"})
DIAGNOSIS_PATCH_FIELDS = frozenset(
    {
        "matching_existing_test",
        "observations",
        "supplied_results",
        "confidence",
        "verdict",
        "next_action",
    }
)
DIAGNOSIS_SUPPLIED_RESULT_FIELDS = frozenset(
    {
        "window_full_days",
        "spend_aud",
        "purchases",
        "purchase_value_aud",
        "target_cac_aud",
        "minimum_batch_spend_aud",
        "minimum_batch_purchases",
    }
)
DIAGNOSIS_SUPPLIED_INTEGER_FIELDS = frozenset(
    {"window_full_days", "purchases", "minimum_batch_purchases"}
)
DIAGNOSIS_CONTROLLED_RESULT_FIELDS = frozenset(
    {
        "approved_revision",
        "approved_revisions",
        "approved_rule",
        "approved_rules",
        "confirmation",
        "confirmed",
        "graduation",
        "graduation_confirmed",
        "learning",
        "learning_event",
        "learning_events",
        "new_test_id",
        "next_test_number",
        "real_post_id",
        "test_id",
        "winner",
        "winner_library",
        "winners",
    }
)
# Scripts permitted to reach the network, because calling an API is their purpose.
NETWORK_SCRIPTS = frozenset(
    {
        "scripts/sync-swipe-corpus.py",
        "evals/run.py",
    }
)
# Sibling modules imported by path rather than installed.
LOCAL_MODULES = frozenset({"rubric", "content_safety"})
NETWORK_DEPENDENCIES = frozenset(
    {
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
DIAGNOSIS_CLASSIFICATIONS = frozenset(
    {
        "Financial winner",
        "Directional promise",
        "Interest, weak conversion",
        "Weak throughout",
        "Initial winner scale failure",
        "Winner at scale",
    }
)
ACTION_THRESHOLD_DESCRIPTOR = re.compile(
    r"`metric=(?P<metric>[^;]+); baseline=(?P<baseline>[^;]+); "
    r"comparison_window=(?P<window>[^;]+); threshold=(?P<threshold>[^;]+); "
    r"unit=(?P<unit>[^`]+)`"
)


NUMBER_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}


def read_invariant(text: str, path: str) -> str | None:
    """Read one dotted key out of invariants.yml.

    A focused reader rather than a YAML parser: this package is deliberately
    standard-library only, and the file's shape is fixed and shallow.
    """
    keys = path.split(".")
    indent = 0
    for depth, key in enumerate(keys):
        # Quoted values are taken whole: a naming shape such as `[CONTST###]`
        # contains a hash and must not be mistaken for a trailing comment.
        pattern = re.compile(
            rf"^[ ]{{{indent}}}{re.escape(key)}:[ \t]*"
            rf"(?P<value>\"[^\"]*\"|'[^']*'|[^\n#]*?)[ \t]*(?:#.*)?$",
            re.MULTILINE,
        )
        match = pattern.search(text)
        if match is None:
            return None
        value = match.group("value").strip().strip('"')
        if depth == len(keys) - 1:
            return value
        text = text[match.end() :]
        next_block = re.search(rf"^[ ]{{0,{indent}}}\S", text, re.MULTILINE)
        if next_block is not None:
            text = text[: next_block.start()]
        indent += 2
    return None


def invariant_drift_errors(root: pathlib.Path) -> list[str]:
    """Check the prose still carries the values declared in invariants.yml.

    Values, not phrasing. The documentation can be rewritten freely so long as
    the facts survive, which is the opposite of matching whole sentences.
    """
    path = root / "invariants.yml"
    if not path.is_file():
        return []
    source = path.read_text()

    def collect(naming_keys: tuple[str, ...]) -> list[tuple[str, str]]:
        found: list[tuple[str, str]] = []
        for key in naming_keys:
            value = read_invariant(source, f"naming.{key}")
            if value:
                found.append((value, f"naming.{key}"))
        for key in (
            "absolute_floor_per_ad_set_per_day",
            "preferred_start_per_ad_set_per_day",
        ):
            value = read_invariant(source, f"budget.{key}")
            if value:
                found.append((f"${value}", f"budget.{key}"))
        for key in ("creative_testing.budget_type", "scaling.budget_type"):
            value = read_invariant(source, key)
            if value:
                found.append((value, key))
        return found

    entrypoint_required = collect(
        ("campaign", "ad_set", "ad", "unpublished_post_id_token")
    )
    contract_required = collect(
        (
            "campaign_creative_testing",
            "campaign_scaling",
            "ad_set",
            "ad",
            "unpublished_post_id_token",
        )
    )

    window = read_invariant(source, "observation.planned_window_full_days")
    window_word = (
        NUMBER_WORDS.get(int(window), window) if window and window.isdigit() else None
    )

    def scope_errors(
        relative: str,
        scope: str,
        label: str,
        required: list[tuple[str, str]],
    ) -> list[str]:
        found: list[str] = []
        for value, key in required:
            if value not in scope:
                found.append(f"{relative} {label} lost {key}: {value!r}")
        if window_word and not re.search(
            rf"\b(?:{window}|{window_word})\b[^.\n]*full days", scope, re.IGNORECASE
        ):
            found.append(
                f"{relative} {label} lost the "
                f"{window_word}-full-day observation window"
            )
        return found

    errors: list[str] = []
    for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
        document = root / relative
        if not document.is_file():
            continue
        errors.extend(
            scope_errors(
                relative,
                markdown_section(document.read_text(), "Launch invariants"),
                "launch invariants",
                entrypoint_required,
            )
        )

    # The launch contract is the operator-facing copy of the same facts.
    contract = root / "contracts" / "campaign-launch-plan.md"
    if contract.is_file():
        errors.extend(
            scope_errors(
                "contracts/campaign-launch-plan.md",
                contract.read_text(),
                "contract",
                contract_required,
            )
        )
    return errors


DASH_EXTENSIONS = frozenset(
    {".md", ".py", ".yml", ".yaml", ".json", ".mjs", ".csv", ".txt"}
)
SKIP_DIRECTORIES = frozenset({".git", ".github", "dist", "__pycache__", ".worktrees"})
# The ban governs copy this package writes. These two hold verbatim copy from other
# brands' live ads, recorded as it ran. Editing someone else's ad to satisfy our
# house style would falsify the evidence, which is a worse outcome than the
# exemption. Nothing else is exempt.
VERBATIM_SOURCES = ("corpus", "references/22-swipe-corpus.md")


def dash_errors(root: pathlib.Path) -> list[str]:
    """Em and en dashes are banned everywhere in authored prose.

    A character scan, so unlike a prose rule it cannot be argued with or drift.
    """
    errors: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in DASH_EXTENSIONS:
            continue
        if SKIP_DIRECTORIES.intersection(path.parts):
            continue
        relative_posix = path.relative_to(root).as_posix()
        if any(
            relative_posix == source or relative_posix.startswith(f"{source}/")
            for source in VERBATIM_SOURCES
        ):
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        relative = path.relative_to(root).as_posix()
        for number, line in enumerate(text.splitlines(), 1):
            for character, name in (("\u2014", "em dash"), ("\u2013", "en dash")):
                if character in line:
                    errors.append(f"{relative}:{number} contains an {name}")
                    break
    return errors


def version_agreement_errors(root: pathlib.Path) -> list[str]:
    """Check that every live declaration agrees with VERSION.

    VERSION is the single source of truth. Pinning a literal here instead meant
    a release could not be cut without editing the validator.
    """
    version_path = root / "VERSION"
    if not version_path.is_file():
        return []

    declared = version_path.read_text().strip()
    if not SEMVER.fullmatch(declared):
        return [f"VERSION must use major.minor.patch format, found {declared!r}"]

    errors: list[str] = []
    for relative, pattern, label in VERSION_DECLARATIONS:
        path = root / relative
        if not path.is_file():
            continue
        match = pattern.search(path.read_text())
        if match is None:
            errors.append(f"{relative} does not declare {label}")
        elif match.group("version") != declared:
            errors.append(
                f"{relative} declares {label} {match.group('version')!r} "
                f"but VERSION is {declared!r}"
            )
    return errors


def load_agents_renderer(root: pathlib.Path):
    """Load the AGENTS.md generator so validation and generation cannot diverge.

    Prefers the generator in the validated root and falls back to the one beside
    this validator, so a minimal root still exercises the real rendering rule.
    """
    candidates = (
        root / "scripts" / "build-agents-md.py",
        pathlib.Path(__file__).resolve().parent / "build-agents-md.py",
    )
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("build_agents_md", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.render
    return None


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##[ \t]+{re.escape(heading)}[ \t]*$", text, re.IGNORECASE | re.MULTILINE
    )
    if match is None:
        return ""
    next_heading = re.search(r"^##[ \t]+", text[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end() : end]


def classify_read_validity(
    full_days: int,
    spend_thresholds_met: bool,
    purchase_thresholds_met: bool,
    material_integrity_failure: bool,
    uneven_delivery: bool,
    logged_intervention: bool,
) -> str:
    if full_days < 5:
        return "Too early"
    if not spend_thresholds_met and not purchase_thresholds_met:
        return "Too early"
    if (
        spend_thresholds_met
        and purchase_thresholds_met
        and not material_integrity_failure
        and not uneven_delivery
        and not logged_intervention
    ):
        return "Verdict"
    return "Direction"


def controlled_result_fields(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if isinstance(key, str):
                normalized_key = re.sub(r"[\s-]+", "_", key.strip().lower())
                if normalized_key in DIAGNOSIS_CONTROLLED_RESULT_FIELDS:
                    found.add(key)
            found.update(controlled_result_fields(nested_value))
    elif isinstance(value, list):
        for nested_value in value:
            found.update(controlled_result_fields(nested_value))
    return found


def diagnosis_patch_errors(
    patch_text: str, existing_test_ids: set[str]
) -> list[str]:
    try:
        patch = json.loads(patch_text)
    except (json.JSONDecodeError, TypeError):
        return ["diagnosis test-register patch must be valid JSON-compatible YAML"]
    if not isinstance(patch, dict):
        return ["diagnosis test-register patch must contain an object"]

    errors: list[str] = []
    for field in sorted(set(patch) - DIAGNOSIS_PATCH_FIELDS):
        errors.append(f"unsupported field: {field}")
    for field in sorted(DIAGNOSIS_PATCH_FIELDS - set(patch)):
        errors.append(f"missing required field: {field}")

    matching_test = patch.get("matching_existing_test")
    if not isinstance(matching_test, str) or matching_test not in existing_test_ids:
        errors.append("matching_existing_test must identify an existing test")
    observations = patch.get("observations")
    if not (
        isinstance(observations, list)
        and observations
        and all(isinstance(item, str) and item.strip() == item and item for item in observations)
    ):
        errors.append("observations must contain non-empty text values")
    supplied_results = patch.get("supplied_results")
    if not isinstance(supplied_results, dict) or not supplied_results:
        errors.append("supplied_results must contain supplied result fields")
    else:
        for field in sorted(controlled_result_fields(supplied_results)):
            errors.append(
                f"supplied_results contains forbidden controlled field: {field}"
            )
        for field in sorted(set(supplied_results) - DIAGNOSIS_SUPPLIED_RESULT_FIELDS):
            errors.append(f"supplied_results unsupported field: {field}")
        for field in sorted(DIAGNOSIS_SUPPLIED_RESULT_FIELDS - set(supplied_results)):
            errors.append(f"supplied_results missing required field: {field}")
        for field in sorted(DIAGNOSIS_SUPPLIED_RESULT_FIELDS & set(supplied_results)):
            value = supplied_results[field]
            if field in DIAGNOSIS_SUPPLIED_INTEGER_FIELDS:
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append(
                        f"supplied_results {field} must be a non-negative integer"
                    )
            elif (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
            ):
                errors.append(f"supplied_results {field} must be a non-negative number")
            elif isinstance(value, float) and not math.isfinite(value):
                errors.append(f"supplied_results {field} must be finite")
            elif value < 0:
                errors.append(f"supplied_results {field} must be a non-negative number")
    confidence = patch.get("confidence")
    if not isinstance(confidence, str) or not confidence:
        errors.append("confidence must be non-empty text")
    if patch.get("verdict") not in {"Too early", "Direction", "Verdict"}:
        errors.append("verdict must be Too early, Direction or Verdict")
    if patch.get("next_action") not in {"keep", "ITR", "stop", "scale"}:
        errors.append("next_action must be keep, ITR, stop or scale")
    return errors


def _numbered_markdown_section(text: str, number: int) -> str:
    match = re.search(
        rf"^## {number}\. [^\n]+\n(?P<body>.*?)(?=^## [0-9]+\.|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group("body") if match is not None else ""


def _markdown_table_rows(section: str, header: tuple[str, ...]) -> list[tuple[str, ...]]:
    lines = section.splitlines()
    expected = "| " + " | ".join(header) + " |"
    try:
        start = lines.index(expected)
    except ValueError:
        return []
    rows: list[tuple[str, ...]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = tuple(cell.strip() for cell in line.strip("|").split("|"))
        if len(cells) == len(header):
            rows.append(cells)
    return rows


def creative_audit_example_errors(
    text: str, intake: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    headings = [
        (int(number), title.strip())
        for number, title in re.findall(r"^## ([0-9]+)\. ([^\n]+)$", text, re.MULTILINE)
    ]
    expected_headings = list(enumerate(CREATIVE_AUDIT_SECTIONS, start=1))
    if headings != expected_headings:
        errors.append(
            "examples/creative-audit.md must contain all 11 sections exactly once and in order"
        )

    intake_ads = intake.get("ads")
    intake_sources = intake.get("sources")
    ad_ids = {
        item.get("ad_id")
        for item in intake_ads
        if isinstance(intake_ads, list)
        and isinstance(item, dict)
        and isinstance(item.get("ad_id"), str)
    } if isinstance(intake_ads, list) else set()
    source_ids = {
        item.get("source_id")
        for item in intake_sources
        if isinstance(intake_sources, list)
        and isinstance(item, dict)
        and isinstance(item.get("source_id"), str)
    } if isinstance(intake_sources, list) else set()

    outcome_rows = _markdown_table_rows(
        _numbered_markdown_section(text, 10),
        (
            "Ad",
            "Outcome",
            "Blocking or revision issue",
            "Evidence",
            "Exact change",
            "Owner",
        ),
    )
    outcome_ad_ids = [row[0].strip("`") for row in outcome_rows]
    if (
        collections.Counter(outcome_ad_ids)
        != collections.Counter(ad_ids)
        or len(outcome_rows) != len(ad_ids)
    ):
        errors.append(
            "examples/creative-audit.md outcome rows must correspond exactly once to intake ads"
        )
    outcomes = [row[1].strip("`") for row in outcome_rows]
    if any(outcome not in {"ready", "revise", "block"} for outcome in outcomes):
        errors.append(
            "examples/creative-audit.md outcomes must be ready, revise or block"
        )
    if not {"ready", "revise"}.issubset(outcomes):
        errors.append(
            "examples/creative-audit.md must demonstrate both ready and revise outcomes"
        )

    ranked_rows = _markdown_table_rows(
        _numbered_markdown_section(text, 9),
        ("Rank", "Ad", "Issue", "Severity", "Evidence", "Exact change", "Owner"),
    )
    if any(not row[4] or row[4].lower() in {"none", "unavailable"} for row in ranked_rows):
        errors.append(
            "examples/creative-audit.md ranked issues must resolve to supplied evidence"
        )
    if any(not row[3] for row in outcome_rows):
        errors.append(
            "examples/creative-audit.md outcome rows must resolve to supplied evidence"
        )

    referenced_sources = set(
        re.findall(r"`(SRC-[A-Za-z0-9._-]+)`", text)
    )
    for unknown in sorted(referenced_sources - source_ids):
        errors.append(
            f"examples/creative-audit.md references unknown evidence source {unknown}"
        )
    referenced_ads = set(re.findall(r"`(AD-[A-Za-z0-9._-]+)`", text))
    for unknown in sorted(referenced_ads - ad_ids):
        errors.append(
            f"examples/creative-audit.md references unknown intake ad {unknown}"
        )
    return errors


def diagnosis_example_traceability_errors(
    text: str, intake: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    required_read_provenance = (
        "Read-validity classification provenance: `strategist judgment`; "
        "the frozen intake does not supply a read-validity classification."
    )
    if required_read_provenance not in text:
        errors.append(
            "examples/ad-diagnosis.md must label its derived read-validity "
            "classification as strategist judgment or unavailable"
        )

    business_section = _numbered_markdown_section(text, 3)
    if "| Initial test |" in business_section:
        errors.append(
            "examples/ad-diagnosis.md must not supply an unfrozen stage classification"
        )

    rows = _markdown_table_rows(
        _numbered_markdown_section(text, 8),
        (
            "Full ad name",
            "Decision",
            "Classification provenance",
            "Top-level action",
            "Numbers and thresholds",
            "Likely explanation",
            "Explanation confidence",
            "Execution instruction",
        ),
    )
    intake_ads = intake.get("ads")
    ad_ids = {
        item.get("ad_id")
        for item in intake_ads
        if isinstance(item, dict) and isinstance(item.get("ad_id"), str)
    } if isinstance(intake_ads, list) else set()
    row_ids = [row[0].strip("`") for row in rows]
    if collections.Counter(row_ids) != collections.Counter(ad_ids):
        errors.append(
            "examples/ad-diagnosis.md decision rows must correspond exactly once to intake ads"
        )
    if any(row[1] not in DIAGNOSIS_CLASSIFICATIONS for row in rows):
        errors.append(
            "examples/ad-diagnosis.md must use the governed six-decision taxonomy"
        )
    if any(
        not (
            "strategist judgment" in row[2].lower()
            or "unavailable" in row[2].lower()
            or re.fullmatch(r"Frozen intake: `[^`]+`", row[2]) is not None
        )
        for row in rows
    ):
        errors.append(
            "examples/ad-diagnosis.md decision classifications must identify "
            "frozen-intake provenance or strategist judgment/unavailable"
        )
    if any(row[3].strip("`").lower() not in PERFORMANCE_ACTIONS for row in rows):
        errors.append(
            "examples/ad-diagnosis.md decision rows must use one governed top-level action"
        )

    performance = intake.get("performance")
    threshold_items = (
        performance.get("threshold_basis")
        if isinstance(performance, dict)
        else None
    )
    threshold_basis = {
        (
            item.get("metric"),
            str(item.get("baseline")),
            item.get("comparison_window"),
            str(item.get("threshold")),
            item.get("unit"),
        )
        for item in threshold_items
        if isinstance(threshold_items, list) and isinstance(item, dict)
    } if isinstance(threshold_items, list) else set()
    thresholds_resolve = bool(rows)
    for row in rows:
        match = ACTION_THRESHOLD_DESCRIPTOR.search(row[4])
        if match is None or (
            match.group("metric"),
            match.group("baseline"),
            match.group("window"),
            match.group("threshold"),
            match.group("unit"),
        ) not in threshold_basis:
            thresholds_resolve = False
            break
    if not thresholds_resolve:
        errors.append(
            "examples/ad-diagnosis.md action thresholds must resolve exact metric, "
            "baseline, comparison window, threshold and unit from frozen intake"
        )
    return errors


def unsafe_imports(
    path: pathlib.Path,
    allowed_local: frozenset[str] = frozenset(),
    network_allowed: bool = False,
) -> list[str]:
    """Report imports that are not standard library, and network use where banned.

    Every script here must run on a bare Python install, because a user should never
    have to pip install anything to use the package. Network access is permitted only
    in the scripts whose job is to call an API, named explicitly in NETWORK_SCRIPTS.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    standard_library = pathlib.Path(sysconfig.get_paths()["stdlib"]).resolve()
    unsafe: list[str] = []
    for name in sorted(imports - {"__future__"} - allowed_local):
        if name in NETWORK_DEPENDENCIES and not network_allowed:
            unsafe.append(name)
            continue
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin not in {"built-in", "frozen"}:
            try:
                origin = pathlib.Path(spec.origin).resolve()
                origin.relative_to(standard_library)
            except (AttributeError, TypeError, ValueError):
                unsafe.append(name)
                continue
            if "site-packages" in origin.parts:
                unsafe.append(name)
    return unsafe


def dependency_errors(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for directory in ("scripts", "evals"):
        folder = root / directory
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.py")):
            relative = path.relative_to(root).as_posix()
            for name in unsafe_imports(
                path,
                allowed_local=LOCAL_MODULES,
                network_allowed=relative in NETWORK_SCRIPTS,
            ):
                reason = (
                    "makes network calls, which only the scripts in NETWORK_SCRIPTS may do"
                    if name in NETWORK_DEPENDENCIES
                    else "is not in the standard library"
                )
                errors.append(f"{relative} imports {name}, which {reason}")
    return errors


def validate(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    required = ("SKILL.md", "AGENTS.md", "PROMPT.md", "VERSION")
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = root / "SKILL.md"
    agents_path = root / "AGENTS.md"
    if skill_path.is_file():
        skill_text = skill_path.read_text()
        for relative in sorted(set(ROUTED_PATH.findall(skill_text))):
            if not (root / relative).is_file():
                errors.append(f"SKILL.md references missing path: {relative}")
    else:
        skill_text = ""

    errors.extend(version_agreement_errors(root))
    errors.extend(invariant_drift_errors(root))
    errors.extend(dash_errors(root))

    for relative in V03_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing v0.3 required file: {relative}")

    for relative in V04_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing v0.4 required file: {relative}")

    creative_example_path = root / "examples" / "creative-audit.md"
    creative_intake_path = root / "examples" / "ad-analysis-intake.json"
    if creative_example_path.is_file():
        creative_example = creative_example_path.read_text()
        if creative_intake_path.is_file():
            try:
                creative_intake = json.loads(creative_intake_path.read_text())
            except json.JSONDecodeError:
                creative_intake = None
            if isinstance(creative_intake, dict):
                errors.extend(
                    creative_audit_example_errors(
                        creative_example, creative_intake
                    )
                )

    diagnosis_example_path = root / "examples" / "ad-diagnosis.md"
    diagnosis_intake_path = root / "examples" / "ad-diagnosis-intake.json"
    if diagnosis_example_path.is_file() and diagnosis_intake_path.is_file():
        try:
            diagnosis_intake = json.loads(diagnosis_intake_path.read_text())
        except json.JSONDecodeError:
            diagnosis_intake = None
        if isinstance(diagnosis_intake, dict):
            errors.extend(
                diagnosis_example_traceability_errors(
                    diagnosis_example_path.read_text(), diagnosis_intake
                )
            )

    diagnosis_patch_path = (
        root / "examples" / "ad-diagnosis-test-register-patch.yml"
    )
    if diagnosis_intake_path.is_file() and diagnosis_patch_path.is_file():
        try:
            diagnosis_intake = json.loads(diagnosis_intake_path.read_text())
            diagnosis_ads = diagnosis_intake.get("ads", [])
            existing_test_ids = {
                ad.get("ad_id", "").split("_", 1)[0]
                for ad in diagnosis_ads
                if isinstance(ad, dict) and isinstance(ad.get("ad_id"), str)
            }
        except (AttributeError, json.JSONDecodeError):
            existing_test_ids = set()
        for patch_error in diagnosis_patch_errors(
            diagnosis_patch_path.read_text(), existing_test_ids
        ):
            errors.append(
                "examples/ad-diagnosis-test-register-patch.yml " + patch_error
            )

    errors.extend(dependency_errors(root))

    test_register_path = root / TEMPLATE_TEST_REGISTER
    if test_register_path.is_file():
        test_ids = list(CONTST_TEST_ID.finditer(test_register_path.read_text()))
        identifiers = [match.group(1).upper() for match in test_ids]
        seen: set[str] = set()
        for identifier in identifiers:
            if identifier in seen:
                errors.append(f"{TEMPLATE_TEST_REGISTER} reuses {identifier}")
            seen.add(identifier)
        numbers = sorted({int(match.group("number")) for match in test_ids})
        if numbers and numbers != list(range(1, numbers[-1] + 1)):
            errors.append(
                f"{TEMPLATE_TEST_REGISTER} must use sequential CONTST values"
            )

    render_agents = load_agents_renderer(root)
    if skill_path.is_file() and agents_path.is_file() and render_agents is not None:
        try:
            expected_agents = render_agents(skill_text)
        except ValueError as error:
            errors.append(f"SKILL.md cannot be rendered to AGENTS.md: {error}")
        else:
            if agents_path.read_text() != expected_agents:
                errors.append(
                    "AGENTS.md is stale; regenerate it with "
                    "scripts/build-agents-md.py"
                )

    examples = root / "examples"
    if examples.is_dir():
        for example in sorted(examples.rglob("*.md")):
            if PLACEHOLDER.search(example.read_text()):
                relative = example.relative_to(root)
                errors.append(f"{relative} contains an unfinished placeholder")

    return errors


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1]).resolve() if len(argv) > 1 else pathlib.Path.cwd()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Package validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
