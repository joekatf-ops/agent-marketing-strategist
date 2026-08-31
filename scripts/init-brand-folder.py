#!/usr/bin/env python3
"""Create a portable brand folder from the versioned template.

    python3 scripts/init-brand-folder.py ~/brands/<slug> --name "Brand" --slug <slug>
    python3 scripts/init-brand-folder.py ~/brands/<slug> --name "Brand" --slug <slug> \
        --seed /tmp/from-connector.json

`--seed` takes a JSON file and writes the parts of the folder a connector can answer, so
nobody has to hand-edit YAML to attach a brand. The intended producer is a store or site
read: pull the catalogue, write it to JSON, pass it here.

Only fields the source actually establishes are written. The seed cannot set an approved
claim, a proof point or a voice rule, because a store listing does not establish any of
those: a product description is marketing copy the brand already published, not evidence
that a claim is approved for a market. Those stay empty and `check-brand-folder.py` reports
them as missing, which is the honest state.

Seed shape, every key optional:

    {
      "canonical_url": "https://example.com",
      "default_market": "AU",
      "markets": ["AU", "NZ"],
      "currency": "AUD",
      "products": [
        {"id": "sku-1", "name": "Product", "price": "34.00", "currency": "AUD",
         "status": "active", "url": "https://example.com/p", "source": "store read",
         "variants": ["Default"], "description_from_source": "..."}
      ]
    }
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "brand-folder"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EMPTY_FILES = (
    "research/evidence-ledger/evidence.jsonl",
    "learning/learning-events.jsonl",
)
# Directories the template does not carry because they hold binaries, which a text
# template cannot represent. An image ad needs somewhere to put a real product photograph.
ASSET_DIRECTORIES = (
    "assets/product",
    "assets/lifestyle",
    "assets/logo",
)
SEED_BRAND_FIELDS = ("canonical_url", "default_market", "currency")
PRODUCT_FIELDS = (
    "id",
    "name",
    "status",
    "url",
    "price",
    "currency",
    "variants",
    "description_from_source",
    "source",
)


def yaml_scalar(value: object) -> str:
    """Render one scalar for the canonical YAML subset the bundle validator accepts."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value)
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def render_catalog(products: list[dict]) -> str:
    lines = ["schema_version: 1"]
    if not products:
        lines.append("products: []")
    else:
        lines.append("products:")
        for product in products:
            first = True
            for field in PRODUCT_FIELDS:
                if field not in product:
                    continue
                marker = "  - " if first else "    "
                first = False
                value = product[field]
                if isinstance(value, list):
                    rendered = "[" + ", ".join(yaml_scalar(item) for item in value) + "]"
                else:
                    rendered = yaml_scalar(value)
                lines.append(f"{marker}{field}: {rendered}")
            if first:
                continue
            for field, note in (
                ("ingredients_or_specs", "not established by the seed source"),
                ("use_cases", "not established by the seed source"),
                ("differentiators", "not established by the seed source"),
            ):
                lines.append(f"    # {field}: {note}")
    lines.extend(
        [
            "",
            "# Seeded from a connector read. A store listing establishes identity, price and",
            "# variants. It does not establish an approved claim, a proof point, a mechanism or",
            "# a differentiator, so those are absent rather than guessed.",
        ]
    )
    return "\n".join(lines) + "\n"


def apply_seed(destination: pathlib.Path, seed: dict) -> list[str]:
    """Write the seedable parts of the folder. Returns what was written."""
    written: list[str] = []

    brand_path = destination / "brand.yml"
    text = brand_path.read_text()
    for field in SEED_BRAND_FIELDS:
        value = seed.get(field)
        if not value:
            continue
        pattern = re.compile(rf'^(  {field}: )""$', re.MULTILINE)
        text, count = pattern.subn(lambda m: m.group(1) + yaml_scalar(value), text, count=1)
        if count:
            written.append(f"brand.{field}")
    markets = seed.get("markets")
    if isinstance(markets, list) and markets:
        rendered = "[" + ", ".join(yaml_scalar(item) for item in markets) + "]"
        text, count = re.subn(r"^  markets: \[\]$", f"  markets: {rendered}", text, count=1, flags=re.MULTILINE)
        if count:
            written.append("brand.markets")
    brand_path.write_text(text)

    products = seed.get("products")
    if isinstance(products, list) and products:
        (destination / "products" / "catalog.yml").write_text(render_catalog(products))
        written.append(f"products/catalog.yml ({len(products)} product(s))")

    return written


def initialise(
    destination: pathlib.Path,
    name: str,
    slug: str,
    template_root: pathlib.Path = DEFAULT_TEMPLATE,
    seed: dict | None = None,
) -> pathlib.Path:
    destination = pathlib.Path(destination)
    if not SLUG.fullmatch(slug):
        raise ValueError("brand slug must be lowercase hyphenated text")
    if not name.strip() or "\n" in name or "\r" in name:
        raise ValueError("brand name must be non-empty single-line text")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"destination is not empty: {destination}")
    if not template_root.is_dir():
        raise FileNotFoundError(f"brand template not found: {template_root}")

    destination.mkdir(parents=True, exist_ok=True)
    tokens = {
        "__BRAND_NAME__": name,
        "__BRAND_NAME_YAML__": json.dumps(name, ensure_ascii=False)[1:-1],
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

    for relative in ASSET_DIRECTORIES:
        directory = destination / relative
        directory.mkdir(parents=True, exist_ok=True)
        keep = directory / ".gitkeep"
        if not keep.exists():
            keep.write_text("")

    if seed is not None:
        apply_seed(destination, seed)
    return destination



def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("destination", type=pathlib.Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument(
        "--seed",
        type=pathlib.Path,
        help="JSON file of connector-established brand and product facts",
    )
    args = parser.parse_args()

    seed = None
    if args.seed is not None:
        seed = json.loads(args.seed.expanduser().read_text(encoding="utf-8"))
        if not isinstance(seed, dict):
            raise SystemExit("seed file must contain a JSON object")

    destination = args.destination.expanduser()
    result = initialise(destination, args.name, args.slug)
    print(f"Created brand folder: {result}")
    if seed is not None:
        for line in apply_seed(result, seed):
            print(f"  seeded {line}")
    print(f"\nNext: python3 scripts/check-brand-folder.py {result} --for copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
