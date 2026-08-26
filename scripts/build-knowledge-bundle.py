#!/usr/bin/env python3
"""Concatenate references and contracts into one uploadable knowledge file.

For surfaces with no filesystem (ChatGPT knowledge files, Gemini, Grok, NotebookLM).
Run after any change to references/ or contracts/.

    python3 scripts/build-knowledge-bundle.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "knowledge-bundle.md"

HEADER = """# Marketing Strategist: knowledge bundle

Generated file. Do not edit by hand. Rebuild with `scripts/build-knowledge-bundle.py`.

Upload this alongside `PROMPT.md` on any surface that has no filesystem. It carries the full
reference library, every output contract, and the connector and runtime guides.

"""


def collect(folder, title):
    parts = [f"\n\n{'=' * 78}\n# PART: {title}\n{'=' * 78}\n"]
    files = sorted((ROOT / folder).glob("*.md"))
    if not files:
        sys.exit(f"No markdown found in {folder}")
    for f in files:
        parts.append(f"\n\n{'-' * 78}\n<!-- source: {folder}/{f.name} -->\n{'-' * 78}\n\n")
        parts.append(f.read_text().strip())
    return "".join(parts)


def build_body():
    body = HEADER
    body += collect("references", "REFERENCE LIBRARY")
    body += collect("contracts", "OUTPUT CONTRACTS")
    body += collect("connectors", "CONNECTOR AND RUNTIME GUIDES")
    return body


def main():
    body = build_body()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(body + "\n")
    kb = len(body) / 1024
    print(f"Wrote {OUT.relative_to(ROOT)}  ({kb:.0f} KB, {body.count(chr(10)):,} lines)")
    if kb > 500:
        print("WARNING: over 500 KB. Some upload surfaces cap below this.")


if __name__ == "__main__":
    main()
