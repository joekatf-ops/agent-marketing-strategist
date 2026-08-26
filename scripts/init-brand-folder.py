#!/usr/bin/env python3
"""Create a portable brand folder from the versioned template."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "brand-folder"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EMPTY_FILES = (
    "research/evidence-ledger/evidence.jsonl",
    "learning/learning-events.jsonl",
)


def initialise(
    destination: pathlib.Path,
    name: str,
    slug: str,
    template_root: pathlib.Path = DEFAULT_TEMPLATE,
) -> pathlib.Path:
    destination = pathlib.Path(destination)
    if not SLUG.fullmatch(slug):
        raise ValueError("brand slug must be lowercase hyphenated text")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"destination is not empty: {destination}")
    if not template_root.is_dir():
        raise FileNotFoundError(f"brand template not found: {template_root}")

    destination.mkdir(parents=True, exist_ok=True)
    tokens = {
        "__BRAND_NAME__": name,
        "__BRAND_SLUG__": slug,
        "__CREATED_DATE__": dt.date.today().isoformat(),
    }
    for source in sorted(template_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(template_root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text()
        for token, value in tokens.items():
            content = content.replace(token, value)
        target.write_text(content)

    for relative in EMPTY_FILES:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=pathlib.Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--slug", required=True)
    args = parser.parse_args()
    result = initialise(args.destination, args.name, args.slug)
    print(f"Created brand folder: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
