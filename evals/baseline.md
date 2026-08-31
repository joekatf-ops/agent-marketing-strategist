# Baseline

First recorded measurement of this package's output. Both runs used the same three briefs, the same
rubric and the same judge.

| Version | Mean | Detail |
|---|---|---|
| v0.4.0, pristine `main` | 15.67 / 20 | `results/baseline-v0.4.0.json` |
| v1.0.0, restructured | 18.00 / 20 | `results/baseline.json` |

**These numbers are out of 20 and the rubric now scores out of 36.** The eight line-level craft
criteria added with `references/26-copywriting-standards.md` did not exist when these runs happened,
so the totals are not comparable to anything measured after that change and must not be read as a
percentage. The per-criterion table below is still valid, because those ten criteria are unchanged in
wording and still scored the same way.

## The full-brief CI run

The two runs above were three briefs each, generated and judged through subagents. CI then scored all
eight briefs against the real API on pull request 1, before the rubric grew. That is the most complete
measurement of the ten-criterion rubric and it is recorded here because the raw JSON is a CI artefact
rather than a committed file.

Model and judge both `claude-sonnet-4-5`. Mean **19.5 / 20 across 8 briefs**.

```
brief                            score
---------------------------------------
collagen-switch-solution         20/20
greens-powder-cold               20/20
grounding-sheet-thin             19/20
hair-growth-regulated            19/20
mushroom-coffee-problem          20/20
pet-food-topper-unaware          18/20
protein-coffee-offer             20/20
survival-water-filter-static     20/20
```

Eight of ten criteria scored a clean 2.00. The two that did not:

| Criterion | Mean | Reading |
|---|---|---|
| specificity | 1.75 | The one criterion that went **down** against the 3-brief run, where it was 2.00 |
| placeholder_discipline | 1.75 | Improved from 1.67, still the joint weakest |

**`awareness_fit` reached 2.00**, from 1.33. That is the cold-traffic regression fixed and confirmed
on real API calls across all eight briefs rather than on the three that found it.

Two things not to over-read. The 18.0 to 19.5 movement mixes three changes at once, a different brief
count, a different model and a different judge, so only `awareness_fit` is a claim this run supports
on its own. And `pet-food-topper-unaware` at 18 being the lowest score is consistent with unaware
traffic staying the hardest case, which is what `references/24-writing-for-low-awareness.md` exists
for, but one brief is an observation and not a finding.

The 36-point scale is still unmeasured. The next CI run on a branch carrying
`references/26-copywriting-standards.md` produces the first reading of it, and `report.py` will print
a `RUBRIC CHANGED` notice rather than subtracting across the two scales.

```
brief                           before   after
greens-powder-cold                  15      18
grounding-sheet-thin                15      19
hair-growth-regulated               17      17
```

## What moved, and the mechanism

| Criterion | Before | After | Delta |
|---|---|---|---|
| opening_type | 1.00 | 2.00 | +1.00 |
| specificity | 1.33 | 2.00 | +0.67 |
| body_handoff | 1.00 | 1.67 | +0.67 |
| placeholder_discipline | 1.00 | 1.67 | +0.67 |
| **awareness_fit** | **1.67** | **1.33** | **-0.34** |
| **no_chaos** | **2.00** | **1.67** | **-0.33** |

The gain is concentrated in the two thin briefs and is one mechanism, not four. The v0.4.0 agent
marked missing input in a gate section at the top and then **blocked the packages that depended on
it**: three of six hook packages blocked on the greens brief, three of six on hair, one held on
grounding. The v1.0.0 agent marks the same gaps inside the line that needs them, so the option set
survives. `body_handoff` follows downstream, because a gated specific leaves the opening promising
something the body is then forbidden to pay.

On the regulated brief the two versions tie at 17 by different routes, which is worth knowing: the
restructure did not help where the constraint is compliance rather than evidence thinness.

## A third routing bug, found by running the thing

The v0.4.0 run reported that it could not source two required fields. `contracts/hook-batch.md`
requires field 7, execution format from `references/08-formats.md`, and field 8, the controlled
ad-name token from `references/07-naming.md`. The `Build hooks` router row loaded neither, and
`SKILL.md` step 5 said to load only the routed references.

So the hook contract was **structurally unsatisfiable**: it demanded two fields from two files the
mode was forbidden to open. The same run also could not perform the readiness and connector checks
that "Start every run here" mandates, because `13-brand-folder.md` and `15-connectors.md` were
likewise unrouted for that mode.

This is the same class of defect as the awareness and platform-layer gaps found by inspection, and it
is the most conclusive of the three, because the instruction set contradicted itself rather than
merely underserving the work. Always-loading the craft stack removes it; the v1.0.0 run reached for
`07-naming.md` from the ops stack on its own, which is the intended behaviour.

Worth noting that no amount of reading found this one. It surfaced only when an agent tried to comply
literally and reported what it could not do, which is an argument for keeping a generation step in the
eval rather than scoring stored outputs.

## Two regressions, and what was done about them

The eval found real problems in the newer version on its first run. Both were fixed after this
measurement was recorded, so **neither fix is verified by these numbers.** Verifying them is the next
run's job.

**Marked invention.** The v1.0.0 output wrote an unsupported statistic, "everyone quits at week
five", into a spoken line and tagged it for removal. The v0.4.0 output invented nothing at all. This
was a loophole created by the placeholder discipline: told to mark unverified specifics, the model
wrote a guess and marked it. A marker that wraps a guess is worse than no marker, because the
sentence reads as real and somebody ships it.

Fixed in `SKILL.md` and `PROMPT.md`: a marker names a gap and never wraps a guess. The correct form
is `[STAT: needs a real figure]`, not an invented figure with a note beside it. If you do not have
the number, the sentence does not contain a number. `placeholder_discipline` now scores 0 for any
invented specific, including one inside a marker.

**Awareness drift on cold traffic.** The v1.0.0 output opened two packages on "One scoop" for a UWA
brief, and led three of six on brand-level evidence for a problem-aware reader. Almost certainly a
side effect of always-loading the platform data, where offer-first hooks show the highest aggregate
rate at 9.29 percent. That number was measured on traffic that already knew the product.

`references/21-evidence-and-doctrine.md` already resolved this in principle and was not forceful
enough. It now states it as a constraint rather than a trade-off, and points at the measured
alternative in the same table: confession at 8.74 percent and curiosity at 7.77 percent both beat
baseline and neither needs prior product knowledge. `awareness_fit` now scores 0 for a product-led
opening on a UWA brief.

## How this run was produced, and its limits

No API key was available in the environment that produced it, so generation and judging both ran
through subagents rather than `evals/run.py`. The pipeline is the same and the rubric is identical,
but this specific pair of numbers is not reproducible by re-running the script.

Three further limits, all of which matter more than the headline delta:

- **Three briefs.** Small enough that one brief moving three points shifts the mean by a point.
- **No conversion data.** The rubric scores craft compliance, not performance. Nothing here says an
  ad would sell anything.
- **One judge, one sitting.** An LLM-judged absolute score drifts. The delta between two runs scored
  the same way is the useful signal, which is why `report.py` leads on the comparison.

Re-record with `ANTHROPIC_API_KEY` set and all eight briefs, and treat that as the real baseline:

```bash
python3 evals/run.py --out evals/results/baseline.json
python3 evals/report.py evals/results/baseline-v0.4.0.json evals/results/baseline.json
```
