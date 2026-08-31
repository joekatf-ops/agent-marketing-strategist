#!/usr/bin/env python3
"""Report what a brand folder actually contains, and what it still needs.

    python3 scripts/check-brand-folder.py ~/brands/<brand-slug>
    python3 scripts/check-brand-folder.py ~/brands/<brand-slug> --for image
    python3 scripts/check-brand-folder.py ~/brands/<brand-slug> --strict

`init-brand-folder.py` creates about thirty files, all of them empty. Existence therefore
proves nothing, and an agent reading the folder cannot tell the difference between a fact
the brand does not have and a template nobody filled in. That gap is why attaching a brand
felt like guesswork: the first honest answer to "can you write for this brand yet" took a
human reading thirty files.

This answers it mechanically. Every input is judged on whether it carries content, not on
whether the file is there, and the requirement is stated per deliverable, because the
honest answer differs. Copy needs the product, the reader and the claim ceiling. An image
ad additionally needs the visual rules and a real product photograph, which no amount of
good copy substitutes for.

It is a report and not a gate. Missing input never blocks drafting, per hard rule 2: it
changes what gets marked. `--strict` exits non-zero for the cases where shipping without
the input would mean inventing it, which is the one thing that is never allowed.

Standard library only. The readers are focused rather than a YAML parser, matching
`read_invariant` in `validate-package.py`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

DELIVERABLES = ("copy", "image", "launch", "research")


def read_text(folder: pathlib.Path, relative: str) -> str | None:
    path = folder / relative
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "brand-folder"


def prose_body(text: str | None) -> str:
    """Everything that is not a heading or an HTML comment, whitespace collapsed."""
    if not text:
        return ""
    kept = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith(("#", "<!--"))
    ]
    return re.sub(r"\s+", " ", " ".join(kept)).strip()


def prose_is_filled(text: str | None, relative: str) -> bool:
    """Filled means it says something the template did not.

    Comparing against the shipped template rather than guessing which sentences are
    instructions. The first version of this check used a length threshold and reported
    `research/customer-intelligence.md` as present on every new folder, because its
    template carries two sentences of instruction and "Status: not researched". A folder
    that reports having the customer language when it has none is worse than no check.
    """
    body = prose_body(text)
    if not body:
        return False
    template = TEMPLATE / relative
    if template.is_file() and body == prose_body(template.read_text(encoding="utf-8")):
        return False
    return len(body) >= 40


def yaml_list_is_filled(text: str | None, key: str) -> bool:
    """True when `key:` opens a block sequence with at least one item."""
    if not text:
        return False
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^{re.escape(key)}:\s*(.*?)\s*(?:#.*)?$", line)
        if not match:
            continue
        inline = match.group(1)
        if inline and inline not in {"[]", "{}", "~", "null"}:
            return True
        if inline in {"[]", "{}"}:
            return False
        for following in lines[index + 1 :]:
            if not following.strip() or following.lstrip().startswith("#"):
                continue
            if not following.startswith(" "):
                return False
            return following.lstrip().startswith("- ")
    return False


def yaml_scalar(text: str | None, dotted: str) -> str | None:
    """Read a scalar at a known nesting depth, e.g. `brand.default_market`."""
    if not text:
        return None
    parts = dotted.split(".")
    depth = 0
    target = parts[0]
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent != depth * 2:
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*(?:#.*)?$", stripped)
        if not match or match.group(1) != target:
            continue
        value = match.group(2).strip().strip("\"'")
        if depth == len(parts) - 1:
            return value or None
        depth += 1
        target = parts[depth]
    return None


def json_is_filled(text: str | None, key: str) -> bool:
    if not text:
        return False
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return False
    return bool(isinstance(parsed, dict) and parsed.get(key))


def has_any_file(folder: pathlib.Path, relative: str, suffixes: tuple[str, ...]) -> bool:
    directory = folder / relative
    if not directory.is_dir():
        return False
    return any(
        path.is_file() and path.suffix.lower() in suffixes
        for path in directory.rglob("*")
    )


class Input:
    def __init__(self, label, where, needed_for, why, present):
        self.label = label
        self.where = where
        self.needed_for = needed_for
        self.why = why
        self.present = present


def inputs_for(folder: pathlib.Path) -> list[Input]:
    brand = read_text(folder, "brand.yml")
    catalog = read_text(folder, "products/catalog.yml")
    claims = read_text(folder, "products/claims.yml")

    return [
        Input(
            "What you sell and what it costs",
            "products/catalog.yml",
            ("copy", "image", "launch"),
            "Without it every product fact, price and specific is a marked placeholder, "
            "and marked placeholders cannot be published.",
            yaml_list_is_filled(catalog, "products"),
        ),
        Input(
            "Which market, and the currency",
            "brand.yml",
            ("copy", "image", "launch"),
            "Regulated wording and price formatting are market-specific. A claim approved "
            "in one market is not approved in another.",
            bool(yaml_scalar(brand, "brand.default_market")),
        ),
        Input(
            "Who it is for, and the problem they have",
            "context/brand-core.md",
            ("copy", "image", "research"),
            "The concept coordinate is Who x Primary Problem. Without it there is no "
            "coordinate, so there is nothing to test and no way to pick an awareness level.",
            prose_is_filled(read_text(folder, "context/brand-core.md"), "context/brand-core.md"),
        ),
        Input(
            "What you are allowed to claim",
            "products/claims.yml",
            ("copy", "image", "launch"),
            "Decides whether a draft can run. Missing approved wording blocks publication, "
            "not drafting.",
            yaml_list_is_filled(claims, "claims"),
        ),
        Input(
            "How the brand sounds",
            "context/voice.md",
            ("copy", "image"),
            "Without it the copy is competent and anonymous, and rule 15 cannot be met.",
            prose_is_filled(read_text(folder, "context/voice.md"), "context/voice.md"),
        ),
        Input(
            "Proof you can point at",
            "products/proof-library.yml",
            ("copy", "image"),
            "Sets the top of the proof ladder. Without it the argument runs on assertion, "
            "and no review count or study may be invented to fill the gap.",
            yaml_list_is_filled(read_text(folder, "products/proof-library.yml"), "proof"),
        ),
        Input(
            "The current offer",
            "products/offers.yml",
            ("copy", "launch"),
            "Decides the CTA and what a decision-stage ad can promise.",
            yaml_list_is_filled(read_text(folder, "products/offers.yml"), "offers"),
        ),
        Input(
            "Words real customers use",
            "research/customer-intelligence.md",
            ("copy", "research"),
            "Voice of customer is the single largest source of specificity. Its absence is "
            "why thin-brand copy reads generic.",
            prose_is_filled(read_text(folder, "research/customer-intelligence.md"), "research/customer-intelligence.md"),
        ),
        Input(
            "How it should look",
            "context/visual.md",
            ("image",),
            "The visual claim gate applies to generated pixels as well as words. Without "
            "the rules, a generated image can imply a claim the brand cannot support.",
            prose_is_filled(read_text(folder, "context/visual.md"), "context/visual.md"),
        ),
        Input(
            "Real product photographs",
            "assets/product/",
            ("image",),
            "A generated product shot invents the product. A reference photograph is the "
            "difference between styling a real object and fabricating one.",
            has_any_file(
                folder, "assets/product", (".jpg", ".jpeg", ".png", ".webp", ".heic")
            ),
        ),
        Input(
            "The website",
            "brand.yml",
            ("copy", "research"),
            "The destination has to match the ad. It is also the cheapest source of product "
            "truth and current offer wording.",
            bool(yaml_scalar(brand, "brand.canonical_url")),
        ),
        Input(
            "Unit economics",
            "products/economics.yml",
            ("launch",),
            "Needed to say whether an offer or a budget makes sense. Not needed to write.",
            yaml_list_is_filled(read_text(folder, "products/economics.yml"), "products"),
        ),
        Input(
            "Naming codes for this brand",
            "brand.yml",
            ("launch",),
            "Campaign, ad set and ad names are locked by the method and need a brand code, "
            "product codes and region codes.",
            bool(yaml_scalar(brand, "naming.brand_code")),
        ),
        Input(
            "Classified evidence",
            "research/evidence-ledger/manifest.json",
            ("research",),
            "Every finding has to trace to a source or be tagged as strategist judgement.",
            json_is_filled(
                read_text(folder, "research/evidence-ledger/manifest.json"), "entries"
            ),
        ),
    ]


def report(folder: pathlib.Path, wanted: str) -> tuple[str, list[Input], list[Input]]:
    relevant = [item for item in inputs_for(folder) if wanted in item.needed_for]
    missing = [item for item in relevant if not item.present]
    have = [item for item in relevant if item.present]

    blocking = {"copy": 2, "image": 3, "launch": 3, "research": 2}[wanted]
    if not missing:
        state = "ready"
    elif len(missing) >= blocking:
        state = "thin"
    else:
        state = "nearly"
    return state, have, missing


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brand_folder", type=pathlib.Path)
    parser.add_argument(
        "--for",
        dest="wanted",
        default="copy",
        choices=DELIVERABLES + ("all",),
        help="which deliverable to judge readiness for, default copy",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when a required input is absent",
    )
    args = parser.parse_args(argv[1:])

    folder = args.brand_folder.expanduser()
    if not (folder / "brand.yml").is_file():
        print(
            f"No brand folder at {folder}: brand.yml is missing.\n"
            "Create one with scripts/init-brand-folder.py.",
            file=sys.stderr,
        )
        return 2

    name = yaml_scalar(read_text(folder, "brand.yml"), "brand.name") or "unnamed"
    slug = yaml_scalar(read_text(folder, "brand.yml"), "brand.slug") or "unknown"
    print(f"Brand: {name}  ({slug})")
    print(f"Folder: {folder}")

    wanted = DELIVERABLES if args.wanted == "all" else (args.wanted,)
    incomplete = False
    for deliverable in wanted:
        state, have, missing = report(folder, deliverable)
        print(f"\n=== {deliverable}: {state} ===")
        for item in have:
            print(f"  have    {item.label}  ({item.where})")
        for item in missing:
            incomplete = True
            print(f"  MISSING {item.label}  ({item.where})")
            print(f"          {item.why}")

    print(
        "\nMissing input never stops a draft. It gets marked in place, per hard rule 2, "
        "and a marked gap is never filled with a guess."
    )
    if incomplete and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
