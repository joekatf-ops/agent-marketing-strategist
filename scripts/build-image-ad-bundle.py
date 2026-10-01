#!/usr/bin/env python3
"""Build the self-contained image-ad bundle. No API or third-party dependency."""
import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist/image-ad-bundle.md"
PLAYBOOK = "/Users/joekatf/JOEKA OS/AI/AI Playbooks/Playbooks/write-dtc-ad-copy/write-dtc-ad-copy.md"
SOURCES = (
    "references/00-working-core.md",
    "references/27-image-ad-workflow.md", "references/37-guided-image-development.md",
    "references/34-art-direction-and-revisions.md",
    "references/08-formats.md", "contracts/format-options.md",
    "references/28-saved-ad-layouts.md", "contracts/static-spec.md",
    "contracts/reference-analysis.md", "connectors/higgsfield.md", "connectors/foreplay.md",
)


def image_excerpt(source, text):
    """Keep image instructions intact while omitting non-image and duplicate teaching material.

    Extract from canonical sources, never maintain a second copy of the rules. Ad copy is not
    carried here: it follows the DTC Ad Copywriting playbook named in the bundle header.
    """
    omitted = {
        "PROMPT.md": {"Additional workflows", "Launch invariants"},
        # Image-specific planning is carried in full by 37, 34 and static-spec. Keep
        # 27's operational generation/verification, without repeating its planning
        # summary, format table or delivery summary.
        "references/27-image-ad-workflow.md": {
            "Three entry points", "1. Resolve the product and request", "2. Choose the message and format",
            "3. Select and adapt a visual reference", "4. Write the production brief",
            "7. Deliver and improve", "Selling role of the layout",
        },
        # The image edition carries the operative core instead of duplicating PROMPT.
        # Keep visual/format methods without video tables, study rankings, bibliographies
        # or dated connector setup instructions in every image request.
        "references/08-formats.md": {"Video formats", "Choosing a format"},
        "connectors/foreplay.md": {"Access and authentication", "Read routes verified in this session"},
        "contracts/static-spec.md": {"Self-check before presenting"},
        "contracts/format-options.md": {"Quick self-check"},
    }
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    kept = []
    for section in sections:
        heading = section.splitlines()[0].removeprefix("## ").strip() if section else ""
        if heading in omitted.get(source, set()):
            continue
        kept.append(section)
    text = "".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build():
    version = (ROOT / "VERSION").read_text().strip()
    parts = [f"# Marketing Strategist: image ads\n\nVersion: {version}\n\n"
             "Self-contained instructions for product-first Meta image ads. Upload this one file, "
             "then describe the product and request. Customer research is optional. Every image concept gets "
             "1:1 and 9:16 versions unless the request or selected brand's delivery preferences override them. Tools remain host-dependent; without generation, deliver the brief and a prompt.\n\n"
             "Ad copy (hooks, scripts, headlines, primary text, descriptions, static ad copy) follows the DTC Ad "
             f"Copywriting playbook: {PLAYBOOK}. Read it before writing any ad copy. This bundle carries no "
             "copywriting method; write the words on the image with the playbook.\n\n"
             "New concepts default to guided choices and one master first. Ready briefs, approved revisions "
             "and explicit delegation proceed directly. The operating core is included directly; PROMPT.md is not required with this edition. "
             "This image edition omits non-image operations, extended worked examples, historical setup detail and duplicate checklists; "
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
