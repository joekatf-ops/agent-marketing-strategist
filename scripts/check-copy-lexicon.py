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
import re
import sys

LIST_KEYS = ("banned_phrases", "flagged_words", "hedge_phrases", "structural_tells")


def read_lexicon(path: pathlib.Path) -> dict[str, list[str]]:
    """Read the shallow list-of-strings blocks out of the lexicon file.

    A focused reader rather than a YAML parser, matching read_invariant in
    validate-package.py: this package is deliberately standard-library only and the
    file's shape is fixed.
    """
    text = path.read_text(encoding="utf-8")
    lexicon: dict[str, list[str]] = {key: [] for key in LIST_KEYS}
    current: str | None = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.match(r"^([a-z_]+):\s*$", line)
        if top:
            current = top.group(1) if top.group(1) in lexicon else None
            continue
        if re.match(r"^[a-z_]+:", line):
            current = None
            continue
        item = re.match(r"^\s+-\s+(.*?)\s*$", line)
        if item and current:
            value = item.group(1).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            lexicon[current].append(value)
    return lexicon


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    """Compile one lexicon entry.

    A `*` stands for any run of characters on the same line, so a template such as
    "that's where * comes in" matches whatever brand name is dropped into it. Apostrophes
    match both the straight and the typographic form, because copy arrives with either.
    """
    parts = [re.escape(part) for part in phrase.split("*")]
    body = ".{0,40}".join(parts)
    body = body.replace(re.escape("'"), "['\u2019]")
    leading = r"\b" if phrase[:1].isalnum() else ""
    trailing = r"\b" if phrase[-1:].isalnum() else ""
    return re.compile(leading + body + trailing, re.IGNORECASE)


def scan(text: str, phrases: list[str]) -> list[tuple[int, str, str]]:
    """Return (line number, phrase, the line) for every hit."""
    patterns = [(phrase, phrase_pattern(phrase)) for phrase in phrases]
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for phrase, pattern in patterns:
            if pattern.search(line):
                hits.append((number, phrase, line.strip()))
    return hits


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
