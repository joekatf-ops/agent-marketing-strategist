#!/usr/bin/env python3
"""Generate hooks for each brief and score them against the rubric.

    ANTHROPIC_API_KEY=... python3 evals/run.py --out evals/results/2026-08-31.json

Standard library only. The model transport is isolated in `complete` so it can be
replaced in tests without patching the rest of the pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import rubric  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRIEFS = ROOT / "evals" / "briefs"
SKILL = ROOT / "SKILL.md"
CRAFT_SECTION = "The craft stack, always loaded"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = os.environ.get("EVAL_MODEL", "claude-sonnet-4-5")
DEFAULT_JUDGE = os.environ.get("EVAL_JUDGE_MODEL", DEFAULT_MODEL)
TIMEOUT_SECONDS = 180
RETRIES = 3


def craft_stack() -> tuple[str, ...]:
    """The references SKILL.md declares, parsed rather than listed.

    A hardcoded copy of this list is how the eval came to score the agent on
    criteria drawn from a file it was never given. `end_state`, `concision` and
    `mechanism_payoff` are standards 1, 3 and 12 of
    `references/26-copywriting-standards.md`, and that file joined the craft stack
    without joining this constant, so the run measured an agent operating without
    it. `scripts/build-craft-bundle.py` reads the same section for the same reason.
    """
    text = SKILL.read_text()
    match = re.search(rf"^##[ \t]+{re.escape(CRAFT_SECTION)}[ \t]*$", text, re.MULTILINE)
    if match is None:
        raise SystemExit(f"SKILL.md has no '{CRAFT_SECTION}' section")
    following = re.search(r"^##[ \t]+", text[match.end() :], re.MULTILINE)
    section = (
        text[match.end() : match.end() + following.start()] if following else text[match.end() :]
    )
    found = tuple(re.findall(r"`(references/[^`]+\.md)`", section))
    if not found:
        raise SystemExit("no craft references found in the craft stack section")
    return found


CRAFT_STACK = craft_stack()


class MissingKey(SystemExit):
    def __init__(self) -> None:
        super().__init__(
            "ANTHROPIC_API_KEY is not set.\n"
            "Add it as a repository secret for CI, or export it locally:\n"
            "  export ANTHROPIC_API_KEY=...\n"
            "Create one at console.anthropic.com under Settings, API keys."
        )


def complete(prompt: str, model: str, key: str, max_tokens: int = 4096) -> str:
    """One completion. The only network call in this package."""
    body = json.dumps(
        {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode()
    headers = {
        "x-api-key": key,
        "anthropic-version": API_VERSION,
        "content-type": "application/json",
    }
    last: Exception | None = None
    for attempt in range(RETRIES):
        try:
            appeal = urllib.request.Request(API_URL, data=body, headers=headers)
            with urllib.request.urlopen(appeal, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode())
            return "".join(
                block.get("text", "")
                for block in payload.get("content", [])
                if block.get("type") == "text"
            )
        except urllib.error.HTTPError as error:
            last = error
            if error.code in (429, 500, 502, 503, 529) and attempt < RETRIES - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            detail = error.read().decode(errors="replace")[:400]
            raise SystemExit(f"Anthropic API error {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            last = error
            if attempt < RETRIES - 1:
                time.sleep(2 ** (attempt + 1))
                continue
    raise SystemExit(f"Anthropic API unreachable: {last}")


def craft_context() -> str:
    parts = []
    for relative in CRAFT_STACK:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(
                f"SKILL.md declares {relative} in the craft stack but the file is missing. "
                "Scoring the agent without a reference it is supposed to have measures "
                "something other than the method."
            )
        parts.append(f"<!-- {relative} -->\n{path.read_text()}")
    return "\n\n".join(parts)


def generation_prompt(brief: str, context: str) -> str:
    return "\n".join(
        [
            "You are an elite direct-response creative strategist for DTC ecommerce brands on Meta.",
            "",
            "Work from the whole reference library below. Never invent a specific: mark anything the",
            "brief does not supply, for example [CLAIM: needs approved wording] or [PROOF: verify].",
            "Never refuse for thin input.",
            "",
            "Produce hook options for the brief. As many as clear the quality gate and differ",
            "strategically, minimum three. For each, state the opening type, which element carries",
            "each must-have, the three non-negotiables, and the body handoff.",
            "",
            "# Reference library",
            "",
            context,
            "",
            "# Brief",
            "",
            brief.strip(),
        ]
    )


def parse_scores(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {"error": "judge did not return JSON", "raw": text[:600]}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as error:
        return {"error": f"judge JSON malformed: {error}", "raw": text[:600]}


def total(scores: dict) -> int | None:
    entries = scores.get("scores")
    if not isinstance(entries, dict):
        return None
    got = 0
    for key, _ in rubric.CRITERIA:
        item = entries.get(key)
        if isinstance(item, dict) and isinstance(item.get("score"), int):
            got += item["score"]
    return got


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--brief", action="append", help="run only these brief slugs")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE)
    args = parser.parse_args(argv[1:])

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise MissingKey()

    briefs = sorted(BRIEFS.glob("*.md"))
    if args.brief:
        wanted = set(args.brief)
        briefs = [b for b in briefs if b.stem in wanted]
    if not briefs:
        raise SystemExit(f"No briefs found in {BRIEFS}")

    context = craft_context()
    results = []
    for path in briefs:
        brief = path.read_text()
        print(f"generating: {path.stem}", flush=True)
        output = complete(generation_prompt(brief, context), args.model, key, 6000)
        print(f"judging:    {path.stem}", flush=True)
        verdict = parse_scores(
            complete(rubric.judge_prompt(brief, output), args.judge_model, key, 2000)
        )
        score = total(verdict)
        results.append(
            {
                "brief": path.stem,
                "model": args.model,
                "judge_model": args.judge_model,
                "output": output,
                "verdict": verdict,
                "total": score,
                "max": rubric.MAX_SCORE,
            }
        )
        print(f"  {path.stem}: {score}/{rubric.MAX_SCORE}", flush=True)

    scored = [r["total"] for r in results if isinstance(r["total"], int)]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "model": args.model,
                "judge_model": args.judge_model,
                "briefs": len(results),
                "mean": round(sum(scored) / len(scored), 2) if scored else None,
                "max": rubric.MAX_SCORE,
                "results": results,
            },
            indent=1,
        )
        + "\n"
    )
    print(f"\nwrote {args.out}")
    if scored:
        print(f"mean {sum(scored) / len(scored):.2f} / {rubric.MAX_SCORE} across {len(scored)} briefs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
