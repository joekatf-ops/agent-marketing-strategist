#!/usr/bin/env python3
"""Build the self-contained image-ad bundle. No API or third-party dependency."""
import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist/image-ad-bundle.md"
SOURCES = (
    "PROMPT.md", "references/00-working-core.md", "references/26-copywriting-standards.md",
    "references/29-moment-to-meaning.md", "references/30-scientific-advertising.md",
    "references/27-image-ad-workflow.md", "references/28-saved-ad-layouts.md", "contracts/static-spec.md",
    "contracts/reference-analysis.md", "connectors/higgsfield.md", "connectors/foreplay.md", "config/copy-lexicon.yml",
)


def image_excerpt(source, text):
    """Keep image instructions intact while omitting non-image and duplicate teaching material.

    Extract from canonical sources, never maintain a second copy of the rules. The full writing
    guide and examples still ship in the craft and knowledge bundles and as standalone files.
    """
    omitted = {
        "PROMPT.md": {"Additional workflows", "Launch invariants"},
        "references/26-copywriting-standards.md": {"Where each rule is enforced", "Running them"},
        # Intake and final checks already ship in PROMPT, 00, 26 and 30. Retain the complete
        # thinking, drafting/editing process and slot guidance, not repeated intake/checklists.
        "references/29-moment-to-meaning.md": {
            "Instructions for the receiving agent", "Work from the available inputs",
            "Worked examples", "Acceptance check", "Origin and scope",
            "Selling usefulness after the depth check",
        },
    }
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    kept = []
    for section in sections:
        heading = section.splitlines()[0].removeprefix("## ").strip() if section else ""
        if heading in omitted.get(source, set()):
            continue
        if source == "PROMPT.md" and heading == "Selling usefulness and commercial decisions":
            # The first paragraph is the complete selling check. Operational methods are optional.
            section = "\n\n".join(section.split("\n\n")[:2]) + "\n"
        kept.append(section)
    text = "".join(kept)
    if source == "references/26-copywriting-standards.md":
        # Explanations of the failure each rule prevents duplicate its actionable check.
        text = re.sub(r"^\*\*Prevents:\*\*.*?(?=\n\n|\Z)", "", text,
                      flags=re.MULTILINE | re.DOTALL)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build():
    version = (ROOT / "VERSION").read_text().strip()
    parts = [f"# Marketing Strategist: image ads\n\nVersion: {version}\n\n"
             "Self-contained instructions for product-first Meta image ads. Upload this one file, "
             "then describe the product and request. Customer research is optional. Every image concept gets "
             "1:1 and 9:16 versions unless explicitly overridden. Tools remain host-dependent; without generation, deliver copy and a prompt.\n\n"
             "This image edition omits non-image operations, extended worked examples and duplicate enforcement commentary; "
             "the actual core checks and image workflow are retained from their canonical sources. "
             "Optional deeper-library references are not prerequisites. The included core and image "
             "workflow govern this task; house campaign rules apply only to that named profile.\n"]
    for source in SOURCES:
        parts.append(f"\n\n---\n<!-- source: {source} -->\n\n{image_excerpt(source, (ROOT / source).read_text())}\n")
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
