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
ALLOWED_PREFIXES = ("context/", "products/", "strategy/")
ALLOWED_SUFFIXES = {".md", ".yml", ".yaml", ".json"}
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*[\"']?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|"
    r"client[_-]?secret|private[_-]?key|secret|password)[\"']?\s*[:=]\s*\S+"
)
AUTHORIZATION_VALUE = re.compile(
    r"(?im)^\s*[\"']?authorization[\"']?\s*[:=]\s*[\"']?(?:bearer|basic)\s+\S+"
)
MANIFEST_SLUG = re.compile(r'(?m)^\s*slug:\s*["\']?([^"\'\s,}]+)')
BRAND_SLUG_FIELD = re.compile(
    r'(?m)^\s*["\']?brand_slug["\']?\s*:\s*["\']?([^"\'\s,}]+)'
)


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


def digest_files(folder: pathlib.Path, files: list[pathlib.Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(folder).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_bundle(folder: pathlib.Path, output: pathlib.Path) -> pathlib.Path:
    folder = pathlib.Path(folder).resolve()
    output = pathlib.Path(output)
    manifest = folder / "brand.yml"
    if not manifest.is_file():
        raise FileNotFoundError(f"brand.yml not found in {folder}")
    slug_match = MANIFEST_SLUG.search(manifest.read_text())
    if not slug_match:
        raise ValueError("brand.yml does not contain brand.slug")
    manifest_slug = slug_match.group(1)

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
        "Generated from the canonical brand folder. Raw evidence, revision history and secrets "
        "are intentionally excluded. Return a learning patch after approved human revisions.\n\n",
        f"Evidence version: `sha256:{evidence_version}`\n\n",
        f"Learning version: `sha256:{learning_version}`\n",
    ]
    for path in files:
        relative = path.relative_to(folder).as_posix()
        content = path.read_text().strip()
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
        if SECRET_ASSIGNMENT.search(content) or AUTHORIZATION_VALUE.search(content):
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
