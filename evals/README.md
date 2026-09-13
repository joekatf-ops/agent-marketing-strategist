# Evals

The package had 195 tests and no measurement of whether the ads were any good.
`OUTPUT-CONTRACT.md` defined a passing release as identical structure with different wording, which
made copy quality untested by construction. This directory is the replacement.

## What it measures

Version 1.6.0 uses rubric 2.1.0. Same-concept headline options are judged as expressions of the
requested thought, and factual accuracy does not rescue an off-brief set. A curiosity gap needs
a worthwhile answer for that reader; setup information cannot repay an outcome promise.

The preceding rubric 2.0.0 introduced buyer relevance and qualified interest in place of compulsory emotion,
curiosity and stakes; useful information replaces the mid-scene rule; specificity does not require
exclusivity. Shortening must preserve the selling argument. The maximum remains 36, but the meaning
has changed. Runs now record a fingerprint of the complete scoring instructions, method version,
generation protocol and exact brief content. Historical results stay unchanged as historical records.

A brief goes in, hooks come out, and a judge scores them against the rubric the package already
declares in `references/20-hook-quality-standard.md`, plus strategy and the line-level standards in
`references/26-copywriting-standards.md`. Scores are recorded so a change to the instructions produces
a number that moves.

Eighteen criteria, scored 0, 1 or 2, so 36 is the maximum. They are grouped in the judge prompt to
keep a rubric this long legible.

**Opening quality**

| Criterion | What earns the mark |
|---|---|
| Opening type | An approach appropriate to the selling job, without compulsory labels in simple lists |
| Qualified interest | A relevant buyer has a reason to continue to useful, supportable information |
| No prior context | Reads cold, with no setup before the claim |
| Immediacy | Starts promptly with relevant information or action; direct explanations can qualify |
| No chaos | One legible idea |
| Body handoff | The body can cash what the opening opened |

**Strategy**

| Criterion | What earns the mark |
|---|---|
| Awareness fit | Sits at the awareness state the brief asked for |
| Specificity | Concrete and useful; ordinary shared facts are valid |
| Placeholder discipline | Essential gaps marked in briefs, omitted from finished copy; nothing invented |
| Distinctness | New concepts differ strategically; requested rewrites preserve the concept and improve expression |
| End state | A relevant desired experience or practical payoff, without treating desire as proven efficacy |

**Line-level craft**

| Criterion | What earns the mark |
|---|---|
| Concision | No wasted words; necessary selling information survives |
| Reader selection | The right reader knows it is for them, through relevant situation, fact, offer or visual context |
| Tone per slot | The opening earns relevant attention, the body explains, the CTA instructs |
| No hedging | No qualifier that drains the claim, with approved wording exempt |
| Mechanism payoff | No machinery without the result it produces |
| Front loaded | Relevant information early, checked in its actual placement |
| No AI lexicon | None of the tier-one machine-writing phrases |

The last seven came in with the sixteen standards. Runs recorded before that change scored out of 20
and are not comparable, which `baseline.md` states in place.

## The rule that makes a score mean anything

The generator must be given exactly the craft stack `SKILL.md` declares, no more and no less. A
criterion may only score what the agent was handed.

`run.py` therefore parses that list out of `SKILL.md` rather than keeping its own copy, the same way
`scripts/build-craft-bundle.py` does, and a declared reference that is missing from disk stops the
run instead of being skipped. Both are guarded by tests, because the failure is silent: the run
completes, the number looks fine, and it is measuring a different agent than the one that ships.

That is not hypothetical. It is what produced the first 36-point reading, recorded in `baseline.md`.

## Running it

```bash
export ANTHROPIC_API_KEY=...
python3 evals/run.py --out evals/results/$(date +%Y-%m-%d).json
python3 evals/report.py evals/results/<file>.json
```

Both scripts are standard library only. The runner needs an API key; the report does not. Without
a key, the local runner exits with guidance. CI clearly skips the paid eval when the repository
secret is absent; structural checks still run. A configured generation or scoring failure still fails.

`EVAL_MODEL` and `EVAL_JUDGE_MODEL` override the defaults if you want a different model on either
side.

## Briefs

`briefs/` holds product briefs built from public DTC product information. They are deliberately
brand-agnostic test fixtures: nothing here is a client, and no private commercial data belongs in
this directory. Each brief names its awareness target so awareness fit can be scored.

## Reading a result

`report.py` shows deltas only when scoring fingerprints, models, generation protocol, brief content
and selection match and all verdicts are complete. A changed maximum or changed scoring meaning
blocks total and per-criterion deltas. Missing metadata is unverified, not assumed compatible.
Percentages cannot repair the comparison. To study an instruction change, generate matched outputs
and score both under the same current rubric and judge protocol.

A compatible delta is still one model-judged craft reading. It is not statistical certainty or sales
lift. Earlier repeated runs showed noise; their approximate one-point heuristic is not a universal
significance threshold for this changed rubric. Use repeated or blinded reviews for stronger evidence.

Two things this cannot tell you. It cannot tell you an ad will convert, because no conversion data
is attached to any brief. And it cannot catch a claim that is compliant but commercially wrong for a
brand you know and it does not. Those remain human judgement.

## Broader skill use checks

`scenarios/headline-craft.json` adds six raw requests for same-concept rewrites, answer-led curiosity,
thin input, supplied customer language, limited-evidence concept exploration and verified offers.
Run these as separate requests against the current skill or its focused bundle. Inspect exact
outputs, not just framework labels; these qualitative cases do not automatically run in the paid
CLI evaluator. The Cadian case exercises an existing worked example, so it is a continuity check,
not an unseen generalisation test. The other cases use different products from the worked edits.

`scenarios/scientific-advertising.json` contains six bounded tasks covering headlines, ordinary
product facts, trial terms and enquiry follow-up, commercial diagnosis, test planning and product
descriptors. The examples are supplied facts or fictional commercial fixtures, not client results.
They are separate from the hook-only paid scoring runner. For an independent review, give each
version the same raw requests in fresh sessions, retain exact outputs, randomise presentation order
and compare usefulness and factual fidelity without version labels. Record model/settings and
limits. A single qualitative comparison does not establish general model performance or sales lift.
