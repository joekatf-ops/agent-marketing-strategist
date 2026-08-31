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

The 36-point scale is still unmeasured, and the first attempt at measuring it does not count. See
"The 36-point reading, and why it is void" below.

```
brief                           before   after
greens-powder-cold                  15      18
grounding-sheet-thin                15      19
hair-growth-regulated               17      17
```

## The 36-point reading, and why it is void

CI scored all eight briefs against the eighteen-criterion rubric on pull request 1 and returned
**35.25 / 36**, model and judge both `claude-sonnet-4-5`. Three criteria came in under 2.00:

| Criterion | Mean | Which standard it enforces |
|---|---|---|
| end_state | 1.62 | Standard 1, sell the end state |
| concision | 1.88 | Standard 3, cut then cut again |
| mechanism_payoff | 1.88 | Standard 12, benefit not mechanism |

Every one of the three is a standard from `references/26-copywriting-standards.md`, and
`evals/run.py` was not loading that file. It kept a hardcoded twelve-file craft stack while
`SKILL.md` had grown to fifteen, so the run also withheld `23-commercial-context.md` and
`24-writing-for-low-awareness.md`, the second of which exists for exactly the cold-traffic case that
`pet-food-topper-unaware` tests.

So the number measures an agent operating without three of the references it ships with. It is not a
reading of this package. Discard it and re-run.

**The `end_state` investigation, since the diagnosis came out of it.** The suspicion was that the
judge was punishing correct cold-traffic behaviour, because the criterion carries a deliberate
exception: the end state does not have to lead, and at Unaware it must not. Reading the artefact says
otherwise. The judge did not mark a single opening down for withholding the end state. On
`pet-food-topper-unaware` it looked at the body handoffs, which is precisely where the standard puts
the end state when it cannot lead, and found that all six terminate on the dog eating the bowl.
Nothing reaches the owner who stops dreading dinner. On `protein-coffee-offer` the handoffs land on
concentrate format, whey isolate and sediment-free liquid, which is machinery, not a life.

The agent was under-selling the outcome, the judge read the rubric correctly including the exception,
and neither was the cause. The harness was.

**Fixed** by parsing the craft stack out of `SKILL.md` in `run.py` instead of listing it, which is
what `scripts/build-craft-bundle.py` already did and why the bundle never drifted. A missing declared
reference now stops the run rather than being silently skipped, and two tests hold the two halves:
the eval's list must equal the builder's, and the standards file behind a criterion must be loaded.

## Does loading the file actually fix it

A two-brief A/B, run through subagents because no API key was available. Same model on both sides,
same judge, same brief, identical prompts from `run.generation_prompt`. The only difference is the
craft stack: twelve references against fifteen. The absolute totals are not comparable to the CI run,
which used `claude-sonnet-4-5`, but the within-pair delta is a controlled reading.

| Brief | Awareness | Twelve refs | Fifteen refs |
|---|---|---|---|
| pet-food-topper-unaware | UWA | 33 / 36 | 33 / 36 |
| protein-coffee-offer | PDA | 31 / 36 | 32 / 36 |

`end_state` went 1.00 to 1.50, and the average hides the shape of it. **On the cold brief it moved 1
to 2**, which is the brief the whole investigation came from. Without the file the judge said the
end state was "never named in a sentence the reader could carry away". With it, the output writes an
explicit end state into all six body handoffs, none of which needs the product's name: "the sentence
on the fridge stops being true", "the bowl becomes something he has an opinion about". That is
standard 1's own check appearing as an artefact in the output. Only the fifteen-reference outputs
cite the numbered standards at all, which is the cleanest evidence that the file was the difference.

**On the offer brief it did not move.** Five of six packages still sell attributes, price and
reassurance. Loading the standard fixed the case where the end state has to carry the argument and
left the case where an offer is competing with it.

Two things this found that the CI run did not.

**`concision` is measuring the harness, not the copy.** It scored 1.00 in all four cells here, and
every judge blamed the same thing: the summary tables, gate records and per-package rationale that
`generation_prompt` explicitly demands. "The delivered lines are tight, but the surrounding
apparatus restates itself." The prompt asks for opening type, must-have carriers, three
non-negotiables and a body handoff on every option, then the rubric marks the output down for
repeating itself. Some of that verbosity is this model rather than the harness, so the size of the
effect is not established. The conflict in the instructions is.

**`mechanism_payoff` improved in kind without improving in score.** The cold brief's handoffs now
attach a payoff to the ingredients and to the bag staying, and still lose the point on "portioned to
his weight", which appears in five of six as bare machinery. Standard 12 is landing partially.

Treat all of this as directional. Two briefs move every criterion mean in steps of 0.5, a total
delta of +0.50 is inside the noise for that sample, and one brief is an observation rather than a
finding. The claim it does support is narrow and was the question asked: on the cold brief that lost
the point, loading the standard recovers it.

## The first real reading, and the noise floor that makes it unreadable

CI, eight briefs, `claude-sonnet-4-5` both sides, on the branch that loads all fifteen references.

**34.75 / 36**, against the void 35.25. So: lower.

Then a mistake produced the most useful number recorded here. Because the `paths` filter on a
`pull_request` event is evaluated against the whole PR diff rather than the latest push, a second
push re-triggered the eval, and two runs went in parallel against commits whose eval-relevant files
were byte-identical. **Two runs of the same agent, same model, same judge, same eight briefs.**

| | Run 1 | Run 2 |
|---|---:|---:|
| Mean | 34.75 | **35.00** |
| end_state | 1.25 | **1.62** |
| concision | 1.88 | **1.62** |
| no_ai_lexicon | 1.88 | **2.00** |
| specificity | 1.88 | 1.88 |
| mechanism_payoff | 1.88 | 1.88 |

Per-brief, four of eight briefs moved, three up and one down, by a full point each.

**`end_state` moved 0.38 between two runs of an identical agent.** The drop from 1.62 to 1.25 that
this section was originally written to explain is 0.37. The `no_ai_lexicon` drop was 0.12 and that
criterion swung 0.12 between the identical runs too.

So the honest reading is that **this eval cannot resolve a difference of half a point**, and the
first version of this section over-explained noise. The per-criterion story it told was wrong, not
because the reasoning was bad but because there was nothing there to reason about. Recorded as an
error rather than quietly deleted, because the same mistake is available to anyone reading a single
run's per-criterion table.

What the two runs do support:

- Loading the three missing references did not visibly move the score in either direction. The A/B
  finding that the copy changes, with explicit end states appearing in the output, still holds and is
  visible in the artefacts. It does not show up in the number.
- The usable comparison is a mean across repeated runs, not a criterion delta from one run. Two runs
  average 34.875, against 35.25 from the void run, and that gap is smaller than the observed spread.
- Anything below roughly one point on the mean needs repeat runs before it means anything. That is
  now the stated read floor.

### One thing the reasons show that the scores cannot

Independent of the score, the `end_state` criterion is worded wrongly, and the judge text says so
plainly. On `hair-growth-regulated`:

> End state is present (normal growth cycle, sustained density) but not foregrounded at PRA; the
> focus correctly stays on problem and mechanism, **so this is appropriate restraint rather than
> failure**, but it's not explicitly named in one sentence per the rubric standard.

The judge describes the behaviour as correct and then scores it 1, because the criterion read as
requiring an explicit sentence in the copy. Standard 1 in `26-copywriting-standards.md` defines the
check as "name the end state in one sentence without using the product's name", which is a test the
*reader* performs, and adds "position, not presence". Those two readings disagree on exactly the case
the awareness model says is correct.

**Changed:** the wording now asks whether the reader can name the end state, says implied is
sufficient, and says position is set by awareness. A test pins it to standard 1's own language.

Changing a criterion after seeing a low score deserves suspicion, so the reasoning is on the record.
The justification is the judge's own text, not the score. The change makes the instrument agree with
the doctrine it measures, the doctrine is the authority, and it is reversible in one commit. **34.75
and 35.00 stand as recorded.** Nothing here improves them retroactively, and the corrected wording
is measured by the next run.

`no_ai_lexicon` also changed instrument this branch: the judge now derives all twenty-three tier-one
phrases from `config/copy-lexicon.yml` plus four structural tells, instead of eight phrases quoted
inside the criterion. Strictly more accurate, and its effect on the score is inside the noise.

### What is still open

`concision` and `mechanism_payoff` sat at 1.88 in both runs and were supposed to benefit from loading
the standards file. The `concision` reasons blame the same thing at full scale that the two-brief A/B
found, and it is not the ad copy: "Core hooks are tight, but write-ups contain restatement." The eval
asks for opening type, must-have carriers, three non-negotiables and a body handoff on every option,
then marks the output down for repeating itself. That conflict lives in `generation_prompt` and is
not fixed here, because fixing it changes what the eval asks for, which deserves a deliberate
decision rather than one taken while chasing a number.

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
