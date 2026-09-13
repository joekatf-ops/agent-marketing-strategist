"""The scoring rubric, kept separate so the judge prompt and the report share one definition."""

from __future__ import annotations

import hashlib
import json
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
        "Opening approach suits the selling job: direct statement, honest open loop or a useful benefit "
        "plus explanation gap. Labels belong in detailed packages, not mandatory in plain headline lists.",
    ),
    (
        "qualified_interest",
        "The likely buyer has a relevant reason to continue and useful selling substance awaits. "
        "Emotion, curiosity and high stakes are optional. Do not reward vague intrigue, artificial "
        "intensity or a loop used to conceal a weak payload.",
    ),
    (
        "no_prior_context",
        "Reads cold. No backstory assumed, no setup spent before the claim.",
    ),
    (
        "immediacy",
        "Gets promptly to relevant information or action without wasted setup. A direct explanation, "
        "feature, offer or demonstration can pass; opening mid-scene is not mandatory.",
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
        "opening that pitches the product, price, offer or category benefit before establishing "
        "relevance. A recognisable situation or desire can establish relevance. Distinguish problem "
        "awareness from category or brand familiarity; cold targeting alone does not determine it.",
    ),
    (
        "specificity",
        "Concrete and useful. Specificity does not require exclusivity: verified ordinary facts can "
        "persuade even when competitors share them. Apply the moment-to-meaning check: the execution makes a "
        "situation or practical payoff matter and gives this product a supported role. "
        "A generic pain label with an intense emotion word is insufficient. A clear feature, offer "
        "or demonstration can earn full credit without overt emotion. Do not reward invented "
        "customer experience, exaggerated distress or an unsupported emotional outcome.",
    ),
    (
        "placeholder_discipline",
        "Essential unknowns are marked in the brief, while finished copy omits unsupported specifics "
        "and remains useful. Never put placeholders in final pixels. Nothing refused for thin input. "
        "Score 0 if any "
        "specific was invented, including an invented figure wrapped in a marker or tagged for "
        "removal: a marker names a gap and never wraps a guess.",
    ),
    (
        "distinctness",
        "Options differ strategically, by route into the argument, rather than cosmetically by "
        "adjective or camera angle, when exploration is requested. A controlled wording comparison may "
        "retain the same appeal deliberately. Respect the requested task and count.",
    ),
    (
        "end_state",
        "Conveys what the person wants back or wants to experience, with a supported product role. "
        "The test is whether YOU can state that experience or practical payoff without the product's name. If you "
        "can, score 2. The copy does not have to contain that sentence: implied is sufficient, and "
        "position depends on awareness and the argument. At Problem Aware, recognition or desired "
        "experience may lead. At Unaware, establish relevance before the category; an everyday desire "
        "can do this. Assess headline, visual and support together. Do not reward implied outcomes "
        "without evidence. Score 1 when only some options pass, and 0 when none does.",
    ),
    (
        "concision",
        "Every word earns its place. Deleting any sentence would cost the argument something. Padding, "
        "throat-clearing and restatement at length all fail. Shortening must preserve necessary selling "
        "information, evidence and material terms across the execution. No fixed word count is required.",
    ),
    (
        "reader_selection",
        "The intended reader recognises relevant use, desire, fact or offer from the opening and visual "
        "together. A product descriptor can qualify; do not force a dramatic situation. Penalise empty "
        "qualifiers such as "
        "\"if you're someone who\", which spends words without selecting anyone.",
    ),
    (
        "tone_per_slot",
        "Register supports the job: the opening earns relevant attention, the body explains, the "
        "headline makes the point legible and the CTA instructs. A useful direct explanation can "
        "open; no compulsory tonal contrast or two-sentence cadence.",
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
        "The relevant point comes early at every scale and remains clear in the requested placement. "
        "An 80-character cut is a stress test, not a universal rule. At UWA the important thing "
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
            "qualified_interest",
            "no_prior_context",
            "immediacy",
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
        "Judge only what is present. Do not reward intent; do not penalise a marked placeholder in a brief.",
        "Finished copy should omit unknown specifics, not present placeholders as usable copy.",
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

RUBRIC_VERSION = "2.0.0"

def fingerprint() -> str:
    """Changes when scoring meaning, scale, grouping or judge instructions change."""
    canonical = {"version": RUBRIC_VERSION, "prompt": judge_prompt("", "")}
    return hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()

RUBRIC_FINGERPRINT = fingerprint()
