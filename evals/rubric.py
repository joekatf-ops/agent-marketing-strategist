"""The scoring rubric, kept separate so the judge prompt and the report share one definition."""

from __future__ import annotations

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
    for key, description in CRITERIA:
        lines.append(f"- `{key}`: {description}")
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
