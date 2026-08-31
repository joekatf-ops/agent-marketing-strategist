"""Reader for `config/copy-lexicon.yml`, shared by the checker and the eval rubric.

This module exists because the list had started to live in two places. `evals/rubric.py`
restated eight tier-one phrases inside the `no_ai_lexicon` criterion description, so adding
a phrase to the lexicon updated the mechanical check and left the judge scoring the old set.
That is the same defect as the eval's hardcoded craft stack: two copies of one list with
nothing forcing agreement.

Importable, unlike `scripts/check-copy-lexicon.py`, whose hyphenated name cannot be imported
without `importlib`. The checker imports from here, and so does the rubric.

Standard library only, in line with the rest of this package. The reader is focused rather
than a YAML parser, matching `read_invariant` in `validate-package.py`: the file's shape is
fixed and a dependency is not worth one flat mapping of string lists.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEXICON_PATH = ROOT / "config" / "copy-lexicon.yml"
LIST_KEYS = ("banned_phrases", "flagged_words", "hedge_phrases", "structural_tells")


def read_lexicon(path: pathlib.Path | None = None) -> dict[str, list[str]]:
    """Read the shallow list-of-strings blocks out of the lexicon file."""
    path = pathlib.Path(path) if path is not None else LEXICON_PATH
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


def quoted(phrases: list[str]) -> str:
    """Render entries for a prompt. A `*` becomes "X" so the judge reads it as a template."""
    return ", ".join('"' + phrase.replace("*", "X") + '"' for phrase in phrases)
