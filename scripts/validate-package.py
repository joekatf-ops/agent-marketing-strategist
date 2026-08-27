#!/usr/bin/env python3
"""Validate routing, frozen examples and duplicated entrypoints."""

from __future__ import annotations

import pathlib
import re
import sys


ROUTED_PATH = re.compile(
    r"`((?:references|contracts|examples|connectors|schemas)/[^`]+\.(?:md|json))`"
)
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|\b(?:TODO|TBD)\b")
SUPERSEDED_CONCEPT_MODEL = re.compile(r"persona\s+x\s+outcome\s+x\s+angle", re.IGNORECASE)
STANDARD_AD_CONTRACTS = (
    "contracts/ad-copy.md",
    "contracts/hook-batch.md",
    "contracts/video-script.md",
    "contracts/static-spec.md",
)
MOST_AWARE_ROW = re.compile(r"^\|\s*MWA\s*\|", re.MULTILINE)
V03_REQUIRED_FILES = (
    "references/18-master-creative-strategy.md",
    "contracts/campaign-launch-plan.md",
    "contracts/destination-handoff.md",
    "examples/campaign-launch-plan.md",
    "examples/destination-handoff.md",
    "connectors/notion-composio.md",
)


def operating_body(text: str) -> str:
    if text.startswith("---\n"):
        closing = text.find("\n---\n", 4)
        if closing != -1:
            text = text[closing + 5 :]
    heading = text.find("# Marketing Strategist")
    if heading != -1:
        text = text[heading:]
    return text.strip()


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

    for relative in ("SKILL.md", "AGENTS.md", "PROMPT.md"):
        path = root / relative
        if path.is_file() and SUPERSEDED_CONCEPT_MODEL.search(path.read_text()):
            errors.append(f"{relative} contains superseded concept model")

    version_path = root / "VERSION"
    if version_path.is_file() and version_path.read_text().strip() != "0.3.0":
        errors.append("VERSION must declare 0.3.0")

    for relative in V03_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing v0.3 required file: {relative}")

    for relative in STANDARD_AD_CONTRACTS:
        path = root / relative
        if path.is_file() and MOST_AWARE_ROW.search(path.read_text()):
            errors.append(f"{relative} contains a Most Aware standard-ad row")

    if skill_path.is_file() and agents_path.is_file():
        if operating_body(skill_text) != operating_body(agents_path.read_text()):
            errors.append("SKILL.md and AGENTS.md operating bodies have drifted")

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
