# Output Contract: Ad Diagnosis
locked: 2026-08-27
version: 1.2.0

Reading performance data and returning what to do about it. Not a dashboard, not a summary.
This workflow accepts manually supplied Meta exports, screenshots or tables. It does not require a live Meta connection.

## Artefact
Markdown report. `diagnosis-{{brand.slug}}-YYYYMMDD.md`

## Sections, in order

1. **Input audit and read validity** - names every manual file, screenshot or table supplied, its
   date range, attribution setting, currency, level of aggregation and missing fields. Then checks
   spend, purchases and days elapsed against the minimum thresholds in the brand folder. States
   plainly whether this is a verdict, a direction, or too early to call. This section comes first
   because it governs how much weight everything after it carries.
2. **What was tested** - coordinate key, CONTST test ID, source, Who, Primary Problem, campaign and
   ad-set names, each complete ad name, awareness job, messaging route, format, destination,
   observation window, budget, and any logged intervention
3. **What happened: business result** - table by batch and ad: spend, purchases, CAC against target,
   revenue, contribution after advertising, expected purchases at target CAC and testing or scaling stage
4. **What happened: funnel result** - table by batch or ad: outbound CTR, landing page view rate, add to
   cart rate, checkout rate, purchase rate
5. **What happened: creative result** - table by ad: spend share, first-frame retention,
   three-second view rate, hold rate, thumbstop,
   frequency, comments
6. **Strongest and weakest complete executions** - ranked with the business, funnel and creative
   evidence, delivery share and read-validity qualification
7. **Likely explanations** - per batch or execution, the observed association, likely explanation,
   disconfirming evidence, explanation confidence and what would test it
8. **Six-decision taxonomy** - each reviewed item classified as Financial winner, Directional
   promise, Interest weak conversion, Weak throughout, Initial winner scale failure or Winner at
   scale, with exactly one literal top-level action field: keep, ITR, stop or scale
9. **Ranked change list** - what to do, in order
10. **What we learned** - retained test observations, including losers and scale failures, kept
    separate from approved human-revision learning
11. **What this does not tell us** - the honest limits of this read

## Ranked change list, fixed row shape

| Rank | What | Where | Why | The number | Expected impact | Effort | Priority |
|---|---|---|---|---|---|---|---|

Every row carries a number in the number column. A row without one does not get written.

## Decision row, fixed shape

| Reviewed item | Decision | Top-level action | Numbers and thresholds | Likely explanation | Explanation confidence | Execution instruction |
|---|---|---|---|---|---|---|

`Top-level action` contains exactly one literal value: `keep`, `ITR`, `stop` or `scale`. Do not put
alternatives, sequences or conditional prose in that field. Use the execution instruction only to
implement the selected action.

## Counts

- Change list rows: as many as the data supports, and no more
- Zero rows is a valid output when the data does not support a change

## Hard rules

1. Manual input is accepted as the current source of truth. Do not imply direct account access
2. Preserve the supplied date range, attribution setting, currency and level of aggregation
3. Do not combine screenshots or exports whose scopes differ without showing the reconciliation
4. Every recommendation names the metric and the threshold it crossed
5. No verdict called below the minimum spend or purchase count in the active brand folder. "Needs N more
   purchases" is the correct output in that case
6. Never attribute a result to a variable the test did not isolate. Write "associated with",
   not "caused by"
7. Distinguish concept results from execution results. One losing video does not kill a
   concept when its other selected executions received no meaningful delivery
8. Losers get analysed, not skipped. Section 10 covers them
9. Initial broad tests compare complete executions. Do not infer isolated awareness, route, hook,
   format, proof or destination causation from them
10. Keep initial-test performance and CBO scaling performance as separate result records
11. An ITR retains Who and Primary Problem but always receives a new CONTST ID
12. Every decision records exactly one literal top-level action: keep, ITR, stop or scale

## Never

- A recommendation with no number behind it
- Generic best practice: "test more creative", "improve the hook", "add urgency"
- A confident verdict on an underpowered test
- Silent omission of an ad or concept that spent money
- Inventing a benchmark. If no account norm exists, use the sourced ranges in
  `references/12-meta-platform.md` and say which you used

## Self-check before presenting

- [ ] Section 1 states validity before any conclusion is drawn
- [ ] Every manual source, date range, attribution setting and missing field is listed
- [ ] The report never implies live Meta access
- [ ] Every change list row has a number
- [ ] Every batch and ad that spent money appears in the tables
- [ ] No causal language on a non-isolated variable
- [ ] Coordinate, batch, execution and scaling results remain separate
- [ ] Strongest and weakest executions are identified only within the valid supplied read
- [ ] Every likely explanation has confidence, disconfirming evidence and a follow-up test
- [ ] Every decision uses the six-decision taxonomy and exactly one literal top-level action field
- [ ] Section 11 is filled honestly
- [ ] If the test is underpowered, that governs the whole report rather than a footnote
