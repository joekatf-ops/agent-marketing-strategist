#!/usr/bin/env python3
"""Concatenate references and contracts into one uploadable knowledge file.

For surfaces with no filesystem (ChatGPT knowledge files, Gemini, Grok, NotebookLM).
Run after any change to references/ or contracts/.

    python3 scripts/build-knowledge-bundle.py
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "knowledge-bundle.md"

HEADER = """# Marketing Strategist: knowledge bundle

Generated file. Do not edit by hand. Rebuild with `scripts/build-knowledge-bundle.py`.

Upload this alongside `PROMPT.md` on any surface that has no filesystem. It carries the full
reference library, every output contract, schema guidance, and the connector and runtime guides.

"""


def collect(folder, title, pattern="*.md"):
    parts = [f"\n\n{'=' * 78}\n# PART: {title}\n{'=' * 78}\n"]
    files = sorted((ROOT / folder).glob(pattern))
    if not files:
        sys.exit(f"No files matching {pattern} found in {folder}")
    for f in files:
        parts.append(f"\n\n{'-' * 78}\n<!-- source: {folder}/{f.name} -->\n{'-' * 78}\n\n")
        parts.append(f.read_text().strip())
    return "".join(parts)


def build_body():
    body = HEADER
    body += collect("references", "REFERENCE LIBRARY")
    body += collect("contracts", "OUTPUT CONTRACTS")
    body += collect("schemas", "SCHEMA GUIDANCE", "*.json")
    body += collect("connectors", "CONNECTOR AND RUNTIME GUIDES")
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed bundle matches its sources without writing",
    )
    args = parser.parse_args()

    body = build_body() + "\n"

    if args.check:
        current = OUT.read_text() if OUT.is_file() else None
        if current == body:
            print(f"{OUT.relative_to(ROOT)} is current")
            return 0
        reason = "is stale" if current is not None else "is missing"
        print(
            f"ERROR: {OUT.relative_to(ROOT)} {reason}. Run scripts/build-knowledge-bundle.py",
            file=sys.stderr,
        )
        return 1

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(body)
    kb = len(body) / 1024
    print(f"Wrote {OUT.relative_to(ROOT)}  ({kb:.0f} KB, {body.count(chr(10)):,} lines)")
    if kb > 500:
        print("WARNING: over 500 KB. Some upload surfaces cap below this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
