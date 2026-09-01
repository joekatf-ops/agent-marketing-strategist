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
`12-meta-platform.md` at about 10,100 tokens even after the diagnostic benchmarks
were split out to `25-meta-benchmarks.md` in the ops stack. That file is worth its
size: it is the only sourced, dated platform layer in the package.

The warning threshold is 220 KB, raised from 200 KB when
`26-copywriting-standards.md` joined the craft stack. The threshold exists to catch
silent bloat, not to cap the method, so a deliberate addition raises it and an
accidental one trips it. If a target surface cannot take the current size, the next
cuts in order of payoff are `22-swipe-corpus.md` at about 5,400 tokens, which is
evidence rather than instruction, and the specs half of `12-meta-platform.md`.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "craft-bundle.md"
SKILL = ROOT / "SKILL.md"

# Parsed from SKILL.md rather than hardcoded, so the bundle cannot drift from the
# stack the skill declares.
CRAFT_SECTION = "The craft stack, always loaded"
FORMATS_SECTION = "Formats available on request"

# Contracts SKILL.md offers that a chat surface cannot act on, each with the reason. The
# contract list is parsed from SKILL.md and every entry must be either bundled or excluded
# here, so adding a contract to the skill forces a decision instead of silently missing the
# bundle. That silent-miss is the defect this replaces: CONTRACTS was a hardcoded seven while
# the skill offered thirteen.
CHAT_SURFACE_EXCLUSIONS = {
    "contracts/brand-readiness.md": "reports on a connected folder a chat surface cannot read",
    "contracts/campaign-launch-plan.md": "needs naming, testing and invariants from the ops stack",
    "contracts/destination-handoff.md": "needs the naming register from the ops stack",
    "contracts/creative-audit.md": "ad analysis runs from the harness repository",
    "contracts/ad-diagnosis.md": "ad analysis runs from the harness repository",
    "contracts/learning-update.md": "writes to a brand folder's learning records",
}

HEADER = """# Marketing Strategist: craft bundle

Generated file. Do not edit by hand. Rebuild with `scripts/build-craft-bundle.py`.

Paste-in knowledge for a chat surface with no filesystem. Carries the craft stack and the output
contracts, and nothing about installing or configuring anything.

Use it with `PROMPT.md` as the operating instruction. For the full method, including naming, testing,
brand folders, connectors and the ad-analysis harness, use `dist/knowledge-bundle.md` on a runtime
that can act on it.
"""


def section_after(heading: str, level: str = "##") -> str:
    text = SKILL.read_text()
    match = re.search(rf"^{level}[ \t]+{re.escape(heading)}[ \t]*$", text, re.MULTILINE)
    if match is None:
        sys.exit(f"SKILL.md has no '{heading}' section")
    following = re.search(rf"^{level}[ \t]+", text[match.end() :], re.MULTILINE)
    if following is None:
        return text[match.end() :]
    return text[match.end() : match.end() + following.start()]


def craft_stack() -> list[str]:
    found = re.findall(r"`(references/[^`]+\.md)`", section_after(CRAFT_SECTION))
    if not found:
        sys.exit("no craft references found in the craft stack section")
    return list(dict.fromkeys(found))


def contracts() -> list[str]:
    """Every contract SKILL.md offers, minus the ones a chat surface cannot act on."""
    offered = list(dict.fromkeys(re.findall(r"`(contracts/[^`]+\.md)`", section_after(FORMATS_SECTION, "###"))))
    if not offered:
        sys.exit(f"no contracts found in the '{FORMATS_SECTION}' section")
    unknown = sorted(set(CHAT_SURFACE_EXCLUSIONS) - set(offered))
    if unknown:
        sys.exit(
            "CHAT_SURFACE_EXCLUSIONS names contracts SKILL.md no longer offers: "
            + ", ".join(unknown)
        )
    return [relative for relative in offered if relative not in CHAT_SURFACE_EXCLUSIONS]


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
    body.extend(include(relative) for relative in contracts())
    return "".join(body) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed bundle matches its sources without writing",
    )
    args = parser.parse_args()

    body = build()

    if args.check:
        current = OUT.read_text() if OUT.is_file() else None
        if current == body:
            print(f"{OUT.relative_to(ROOT)} is current")
            return 0
        reason = "is stale" if current is not None else "is missing"
        print(
            f"ERROR: {OUT.relative_to(ROOT)} {reason}. Run scripts/build-craft-bundle.py",
            file=sys.stderr,
        )
        return 1

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(body)
    kilobytes = len(body) / 1024
    print(f"Wrote {OUT.relative_to(ROOT)}  ({kilobytes:.0f} KB, ~{len(body) // 4:,} tokens)")
    full = ROOT / "dist" / "knowledge-bundle.md"
    if full.is_file():
        other = len(full.read_text())
        print(f"Full bundle for comparison: {other / 1024:.0f} KB, ~{other // 4:,} tokens")
    if kilobytes > 220:
        print("WARNING: the craft bundle is larger than intended for a chat surface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
