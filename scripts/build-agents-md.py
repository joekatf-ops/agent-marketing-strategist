#!/usr/bin/env python3
"""Generate AGENTS.md from SKILL.md.

Codex reads `SKILL.md` with its YAML frontmatter. Other agent hosts read a bare
`AGENTS.md`. The operating body is identical, so it is written once in
`SKILL.md` and rendered here rather than maintained twice.

    python3 scripts/build-agents-md.py          # write AGENTS.md
    python3 scripts/build-agents-md.py --check  # fail if AGENTS.md is stale
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
AGENTS = ROOT / "AGENTS.md"

FRONTMATTER_FENCE = "---\n"
FRONTMATTER_CLOSE = "\n---\n"


def render(skill_text: str) -> str:
    """Return the AGENTS.md body for a given SKILL.md source."""
    if not skill_text.startswith(FRONTMATTER_FENCE):
        raise ValueError("SKILL.md must open with a YAML frontmatter block")
    closing = skill_text.find(FRONTMATTER_CLOSE, len(FRONTMATTER_FENCE))
    if closing == -1:
        raise ValueError("SKILL.md frontmatter block is not closed")
    body = skill_text[closing + len(FRONTMATTER_CLOSE) :].lstrip("\n")
    if not body.startswith("# "):
        raise ValueError("SKILL.md must open its body with a level-one heading")
    return body


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed AGENTS.md matches SKILL.md without writing",
    )
    args = parser.parse_args(argv[1:])

    expected = render(SKILL.read_text())

    if args.check:
        current = AGENTS.read_text() if AGENTS.is_file() else None
        if current == expected:
            print("AGENTS.md is current")
            return 0
        print(
            "ERROR: AGENTS.md is stale. Edit SKILL.md, then run "
            "scripts/build-agents-md.py",
            file=sys.stderr,
        )
        return 1

    AGENTS.write_text(expected)
    print(f"Wrote {AGENTS.relative_to(ROOT)} ({len(expected):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
