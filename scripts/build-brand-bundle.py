#!/usr/bin/env python3
"""Build a compact brand knowledge bundle for upload-only LLM runtimes."""

from __future__ import annotations

import argparse
import pathlib
import re


ALLOWED_EXACT = {
    "brand.yml",
    "research/customer-intelligence.md",
    "learning/approved-rules.yml",
    "learning/preference-signals.yml",
    "learning/rejected-patterns.yml",
    "learning/decisions.md",
    "connectors/capabilities.yml",
}
ALLOWED_PREFIXES = ("context/", "products/", "strategy/")
ALLOWED_SUFFIXES = {".md", ".yml", ".yaml", ".json"}
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*\S+"
)


def selected_files(folder: pathlib.Path) -> list[pathlib.Path]:
    selected = []
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(folder).as_posix()
        allowed = relative in ALLOWED_EXACT or relative.startswith(ALLOWED_PREFIXES)
        if allowed and path.suffix.lower() in ALLOWED_SUFFIXES:
            selected.append(path)
    return sorted(selected, key=lambda path: path.relative_to(folder).as_posix())


def fence_language(path: pathlib.Path) -> str:
    return {
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
    }.get(path.suffix.lower(), "markdown")


def build_bundle(folder: pathlib.Path, output: pathlib.Path) -> pathlib.Path:
    folder = pathlib.Path(folder).resolve()
    output = pathlib.Path(output)
    manifest = folder / "brand.yml"
    if not manifest.is_file():
        raise FileNotFoundError(f"brand.yml not found in {folder}")

    parts = [
        "# Brand knowledge bundle\n\n",
        "Generated from the canonical brand folder. Raw evidence, revision history and secrets "
        "are intentionally excluded. Return a learning patch after approved human revisions.\n",
    ]
    for path in selected_files(folder):
        relative = path.relative_to(folder).as_posix()
        content = path.read_text().strip()
        if SECRET_ASSIGNMENT.search(content):
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
