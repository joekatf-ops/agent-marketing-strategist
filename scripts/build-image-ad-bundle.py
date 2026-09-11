#!/usr/bin/env python3
"""Build the self-contained image-ad bundle. No API or third-party dependency."""
import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist/image-ad-bundle.md"
SOURCES = (
    "PROMPT.md", "references/00-working-core.md", "references/26-copywriting-standards.md",
    "references/29-moment-to-meaning.md",
    "references/27-image-ad-workflow.md", "references/28-saved-ad-layouts.md", "contracts/static-spec.md",
    "contracts/reference-analysis.md", "connectors/higgsfield.md", "connectors/foreplay.md", "config/copy-lexicon.yml",
)


def build():
    version = (ROOT / "VERSION").read_text().strip()
    parts = [f"# Marketing Strategist: image ads\n\nVersion: {version}\n\n"
             "Self-contained instructions for product-first Meta image ads. Upload this one file, "
             "then describe the product and request. Customer research is optional. Every image concept gets "
             "1:1 and 9:16 versions unless explicitly overridden. Tools remain host-dependent; without generation, deliver copy and a prompt.\n\n"
             "Optional deeper-library references are not prerequisites. The included core and image "
             "workflow govern this task; house campaign rules apply only to that named profile.\n"]
    for source in SOURCES:
        parts.append(f"\n\n---\n<!-- source: {source} -->\n\n{(ROOT / source).read_text().strip()}\n")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    body = build()
    if args.check:
        current = OUT.read_text() if OUT.is_file() else None
        if current != body:
            print("ERROR: dist/image-ad-bundle.md is missing or stale")
            return 1
        print("dist/image-ad-bundle.md is current")
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(body)
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(body.encode())} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
