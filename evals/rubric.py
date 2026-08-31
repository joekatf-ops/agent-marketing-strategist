"""The scoring rubric, kept separate so the judge prompt and the report share one definition."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import copy_lexicon  # noqa: E402

# Read from config/copy-lexicon.yml rather than restated here. The eight phrases this
# criterion used to quote were a second copy of the tier-one list, so extending the lexicon
# updated the mechanical check in scripts/check-copy-lexicon.py and left the judge scoring
# the old set. Same defect as the eval's hardcoded craft stack, same fix.
_LEXICON = copy_lexicon.read_lexicon()
_BANNED = copy_lexicon.quoted(_LEXICON["banned_phrases"])
_STRUCTURAL = "; ".join(_LEXICON["structural_tells"])

CRITERIA = (
    (
        "opening_type",
        "Opening type declared as promise or open loop, and appropriate for how strong the body is.",
    ),
    (
        "must_have_carriers",
        "At least two of emotion, curiosity gap and high stakes, each attributed to a named frame, "
        "line or visual element rather than merely asserted. An absent element is stated, not hidden.",
    ),
    (
        "no_prior_context",
        "Reads cold. No backstory assumed, no setup spent before the claim.",
    ),
    (
        "starts_in_action",
        "Opens mid-scene rather than mid-explanation. Nothing spent explaining what the viewer needs "
        "to know first.",
    ),
    (
        "no_chaos",
        "One legible idea. Not sensory overload, not two competing ideas.",
    ),
    (
        "body_handoff",
        "The body can cash what the opening opened. No promise the execution cannot deliver.",
    ),
    (
        "awareness_fit",
        "Sits at the awareness state the brief asked for. Score 0 if a UWA brief is answered with an "
        "opening that leads on the product name, a price, an offer or a product benefit, regardless "
        "of how strong that opening is in the abstract.",
    ),
    (
        "specificity",
        "Concrete. Fails if every specific could be swapped to a competitor's product without "
        "changing a word.",
    ),
    (
        "placeholder_discipline",
        "Unverified specifics are marked in place. Nothing refused for thin input. Score 0 if any "
        "specific was invented, including an invented figure wrapped in a marker or tagged for "
        "removal: a marker names a gap and never wraps a guess.",
    ),
    (
        "distinctness",
        "Options differ strategically, by route into the argument, rather than cosmetically by "
        "adjective or camera angle.",
    ),
    (
        "end_state",
        "Sells the life the product produces rather than the object. The test is whether YOU, having "
        "read it, can state the end state in one sentence without using the product's name. If you "
        "can, score 2. The copy does not have to contain that sentence: implied is sufficient, and "
        "position is set by awareness, so at Unaware and Problem Aware the end state must not lead "
        "and will usually be carried by the body rather than stated outright. Score 1 when you can "
        "name it for some options and not others, and 0 when the copy sells the object and there is "
        "no life behind it to name.",
    ),
    (
        "concision",
        "No word carries no weight. Deleting any sentence would cost the argument something. Padding, "
        "throat-clearing and restatement at length all fail.",
    ),
    (
        "reader_selection",
        "The intended reader can tell inside the first line that this is about them, and it is done "
        "with a recognisable situation rather than a label. Score 0 for a bare qualifier such as "
        "\"if you're someone who\", which spends words without selecting anyone.",
    ),
    (
        "tone_per_slot",
        "Register matches the job of each slot: the opening interrupts, the body explains, a headline "
        "compresses, a CTA instructs. Score 0 if one register is applied across all of them, most "
        "commonly a hook that reads like body copy.",
    ),
    (
        "no_hedging",
        "No qualifier that drains the claim without adding accuracy. A hedge that belongs to approved "
        "regulated wording is correct and does not count against this. A hedge in quoted or "
        "first-person voice that signals a real speaker is also fine.",
    ),
    (
        "mechanism_payoff",
        "Every mechanism appears with the payoff it produces, stated or plainly implied. A mechanism "
        "may lead when the reader has already conceded the benefit. Machinery with no \"so that\" "
        "fails at every awareness level.",
    ),
    (
        "front_loaded",
        "The most important thing comes first at every scale. Truncating the first line at 80 "
        "characters should still leave a complete, compelling proposition. At UWA the important thing "
        "is the situation, not the product, so a withheld product name is not a failure here.",
    ),
    (
        "no_ai_lexicon",
        "No machine-writing tells. Score 0 for any tier-one phrase from the banned list, where X "
        f"stands for any words on the same line: {_BANNED}. Also penalise these structural tells, "
        f"which need a read rather than a match: {_STRUCTURAL}.",
    ),
)

# Rendered as headings in the judge prompt so an eighteen-criterion rubric stays legible.
# Purely presentational: CRITERIA remains the single flat source of truth for scoring.
GROUPS = (
    (
        "Opening quality",
        (
            "opening_type",
            "must_have_carriers",
            "no_prior_context",
            "starts_in_action",
            "no_chaos",
            "body_handoff",
        ),
    ),
    (
        "Strategy",
        ("awareness_fit", "specificity", "placeholder_discipline", "distinctness", "end_state"),
    ),
    (
        "Line-level craft",
        (
            "concision",
            "reader_selection",
            "tone_per_slot",
            "no_hedging",
            "mechanism_payoff",
            "front_loaded",
            "no_ai_lexicon",
        ),
    ),
)

SCALE = """Score each criterion 0, 1 or 2.

0 = fails outright
1 = partially meets it, or meets it for some options and not others
2 = meets it clearly

Be strict. A 2 means an experienced direct-response strategist would not ask for a revision on that
criterion. Most competent-but-unremarkable output should land on 1."""


def judge_prompt(brief: str, output: str) -> str:
    lines = [
        "You are auditing direct-response advertising output against a fixed rubric.",
        "",
        "Judge only what is present. Do not reward intent, do not penalise a marked placeholder: a",
        "marked placeholder is correct behaviour when a specific was not supplied in the brief.",
        "",
        "## The brief",
        "",
        brief.strip(),
        "",
        "## The output to score",
        "",
        output.strip(),
        "",
        "## Rubric",
        "",
    ]
    described = dict(CRITERIA)
    for group, keys in GROUPS:
        lines.extend([f"### {group}", ""])
        for key in keys:
            lines.append(f"- `{key}`: {described[key]}")
        lines.append("")
    lines.extend(
        [
            "",
            SCALE,
            "",
            "## Response format",
            "",
            "Reply with JSON only, no prose outside it:",
            "",
            '{"scores": {"<criterion>": {"score": 0, "reason": "<one sentence>"}, ...},',
            ' "strongest": "<the single best line in the output, quoted>",',
            ' "weakest": "<the single weakest thing, named as a mechanism>"}',
        ]
    )
    return "\n".join(lines)


MAX_SCORE = len(CRITERIA) * 2

_grouped = tuple(key for _, keys in GROUPS for key in keys)
assert _grouped == tuple(key for key, _ in CRITERIA), (
    "GROUPS must list every criterion exactly once, in CRITERIA order"
)
