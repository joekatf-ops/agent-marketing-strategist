# Evals

The package had 195 tests and no measurement of whether the ads were any good.
`OUTPUT-CONTRACT.md` defined a passing release as identical structure with different wording, which
made copy quality untested by construction. This directory is the replacement.

## What it measures

A brief goes in, hooks come out, and a judge scores them against the rubric the package already
declares in `references/20-hook-quality-standard.md`, plus awareness fit, specificity and
placeholder discipline. Scores are recorded so a change to the instructions produces a number that
moves.

| Criterion | What earns the mark |
|---|---|
| Opening type | Declared as promise or open loop, and correct for the strength of the body |
| Must-have carriers | At least two of emotion, curiosity gap and high stakes, each pointing at a named frame or line rather than asserted |
| No prior context | Reads cold, with no setup before the claim |
| Starts in action | Frame one is mid-scene, not mid-explanation |
| No chaos | One legible idea |
| Body handoff | The body can cash what the opening opened |
| Awareness fit | Sits at the awareness state the brief asked for |
| Specificity | Concrete rather than swappable to a competitor without changing a word |
| Placeholder discipline | Unverified specifics marked, nothing invented, nothing refused |
| Distinctness | Options differ strategically rather than cosmetically |

## Running it

```bash
export ANTHROPIC_API_KEY=...
python3 evals/run.py --out evals/results/$(date +%Y-%m-%d).json
python3 evals/report.py evals/results/<file>.json
```

Both scripts are standard library only. Without a key they exit with an actionable message rather
than a stack trace, so the repository stays coherent for anyone who does not have one.

`EVAL_MODEL` and `EVAL_JUDGE_MODEL` override the defaults if you want a different model on either
side.

## Briefs

`briefs/` holds product briefs built from public DTC product information. They are deliberately
brand-agnostic test fixtures: nothing here is a client, and no private commercial data belongs in
this directory. Each brief names its awareness target so awareness fit can be scored.

## Reading a result

A score is only meaningful against a baseline. `baseline.md` records the reference numbers and the
commit they came from. Compare, do not admire: the absolute value of an LLM-judged rubric score
drifts with the judge, which is why the head-to-head comparison in `report.py` matters more than the
raw mean.

Two things this cannot tell you. It cannot tell you an ad will convert, because no conversion data
is attached to any brief. And it cannot catch a claim that is compliant but commercially wrong for a
brand you know and it does not. Those remain human judgement.
