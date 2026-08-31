#!/usr/bin/env python3
"""Build the craft bundle: the paste-in artefact for chat surfaces.

    python3 scripts/build-craft-bundle.py

Two bundles exist because two runtimes have different constraints.

`build-knowledge-bundle.py` produces the full bundle: every reference, every
contract, the schemas and every connector and runtime guide. That is right for an
agent IDE that will work across the whole method, and wrong for a chat window,
where it spends context on install guides the model will never act on.

This builds the craft bundle instead: the always-loaded craft stack, the output
contracts a chat surface actually produces, and the operating prompt. Roughly half
the size, and none of it is documentation about installation.

Half rather than a tenth because the craft itself is large, and most of that is
`12-meta-platform.md` at about 12,500 tokens. That file is worth its size: it is
the only sourced, dated platform layer in the package. Splitting it into a specs
half and a hook-craft half would shrink this bundle further and is the obvious next
move if a target surface cannot take the current size.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "craft-bundle.md"
SKILL = ROOT / "SKILL.md"

# Parsed from SKILL.md rather than hardcoded, so the bundle cannot drift from the
# stack the skill declares.
CRAFT_SECTION = "The craft stack, always loaded"

CONTRACTS = (
    "contracts/strategist-read.md",
    "contracts/hook-batch.md",
    "contracts/ad-copy.md",
    "contracts/video-script.md",
    "contracts/static-spec.md",
    "contracts/concept-batch.md",
    "contracts/customer-intelligence.md",
)

HEADER = """# Marketing Strategist: craft bundle

Generated file. Do not edit by hand. Rebuild with `scripts/build-craft-bundle.py`.

Paste-in knowledge for a chat surface with no filesystem. Carries the craft stack and the output
contracts, and nothing about installing or configuring anything.

Use it with `PROMPT.md` as the operating instruction. For the full method, including naming, testing,
brand folders, connectors and the ad-analysis harness, use `dist/knowledge-bundle.md` on a runtime
that can act on it.
"""


def craft_stack() -> list[str]:
    text = SKILL.read_text()
    match = re.search(
        rf"^##[ \t]+{re.escape(CRAFT_SECTION)}[ \t]*$", text, re.MULTILINE
    )
    if match is None:
        sys.exit(f"SKILL.md has no '{CRAFT_SECTION}' section")
    following = re.search(r"^##[ \t]+", text[match.end() :], re.MULTILINE)
    section = text[match.end() : match.end() + following.start()] if following else text[match.end() :]
    found = re.findall(r"`(references/[^`]+\.md)`", section)
    if not found:
        sys.exit("no craft references found in the craft stack section")
    return found


def part(title: str) -> str:
    rule = "=" * 78
    return f"\n\n{rule}\n# PART: {title}\n{rule}\n"


def include(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        sys.exit(f"missing file listed for the craft bundle: {relative}")
    rule = "-" * 78
    return f"\n\n{rule}\n<!-- source: {relative} -->\n{rule}\n\n{path.read_text().strip()}"


def build() -> str:
    body = [HEADER, part("OPERATING PROMPT"), include("PROMPT.md"), part("CRAFT STACK")]
    body.extend(include(relative) for relative in craft_stack())
    body.append(part("OUTPUT CONTRACTS"))
    body.extend(include(relative) for relative in CONTRACTS)
    return "".join(body) + "\n"


def main() -> int:
    body = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(body)
    kilobytes = len(body) / 1024
    print(f"Wrote {OUT.relative_to(ROOT)}  ({kilobytes:.0f} KB, ~{len(body) // 4:,} tokens)")
    full = ROOT / "dist" / "knowledge-bundle.md"
    if full.is_file():
        other = len(full.read_text())
        print(f"Full bundle for comparison: {other / 1024:.0f} KB, ~{other // 4:,} tokens")
    if kilobytes > 200:
        print("WARNING: the craft bundle is larger than intended for a chat surface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
