#!/usr/bin/env python3
"""Check copy against the machine-writing lexicon in config/copy-lexicon.yml.

Rule 16 and rule 7 of references/26-copywriting-standards.md.

Tier one phrases are errors. Flagged words and hedges are reported and never fail the run,
because both have legitimate uses that no scanner can distinguish from the filler versions:
"seamless" is a fact about a garment, and "helps support" is required structure-function wording
for a supplement in several markets.

Default scope is examples/, which are frozen representations of agent output. Pass paths or
--text to check real copy on the way out.

    python3 scripts/check-copy-lexicon.py
    python3 scripts/check-copy-lexicon.py drafts/ad.md
    python3 scripts/check-copy-lexicon.py --text "Elevate your morning routine."

Standard library only, in line with the rest of this package.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from copy_lexicon import LIST_KEYS, phrase_pattern, read_lexicon, scan  # noqa: E402,F401


def collect_targets(root: pathlib.Path, given: list[str]) -> list[pathlib.Path]:
    if not given:
        return sorted((root / "examples").glob("*.md"))
    targets: list[pathlib.Path] = []
    for raw in given:
        path = pathlib.Path(raw)
        if not path.is_absolute():
            path = root / path
        if path.is_dir():
            targets.extend(sorted(path.rglob("*.md")))
        elif path.exists():
            targets.append(path)
        else:
            print(f"no such path: {raw}", file=sys.stderr)
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="files or directories, default examples/")
    parser.add_argument("--text", help="check a string instead of files")
    parser.add_argument("--root", default=None, help="package root")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail on flagged words, for a final pass before delivery",
    )
    args = parser.parse_args()

    root = pathlib.Path(args.root) if args.root else pathlib.Path(__file__).resolve().parent.parent
    lexicon = read_lexicon(root / "config" / "copy-lexicon.yml")

    if not lexicon["banned_phrases"]:
        print("lexicon is empty, nothing to check against", file=sys.stderr)
        return 1

    sources: list[tuple[str, str]] = []
    if args.text is not None:
        sources.append(("--text", args.text))
    # --text on its own checks only that string. The examples/ default applies when no
    # source was named at all, so a quick one-off check does not drag the whole suite in.
    if args.paths or args.text is None:
        for path in collect_targets(root, args.paths):
            try:
                sources.append((str(path.relative_to(root)), path.read_text(encoding="utf-8")))
            except ValueError:
                sources.append((str(path), path.read_text(encoding="utf-8")))

    errors = 0
    flagged = 0
    hedges = 0

    for label, text in sources:
        for number, phrase, line in scan(text, lexicon["banned_phrases"]):
            print(f"BANNED  {label}:{number}: \"{phrase}\" in: {line}")
            errors += 1
        for number, phrase, line in scan(text, lexicon["flagged_words"]):
            print(f"flagged {label}:{number}: \"{phrase}\" in: {line}")
            flagged += 1
        for number, phrase, line in scan(text, lexicon["hedge_phrases"]):
            print(f"hedge   {label}:{number}: \"{phrase}\" in: {line}")
            hedges += 1

    checked = len(sources)
    if errors == 0 and flagged == 0 and hedges == 0:
        print(f"copy lexicon check passed: {checked} source(s) clean")
        return 0

    print(
        f"\n{checked} source(s) checked: {errors} banned, {flagged} flagged, {hedges} hedge(s)"
    )
    if flagged or hedges:
        print(
            "Flagged words and hedges are reports, not failures. Justify a flagged word in the "
            "rationale. For a hedge, delete it and read the line: if it now asserts something "
            "unsupportable the hedge belongs to the claim and stays."
        )
    if errors:
        return 1
    if args.strict and flagged:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
