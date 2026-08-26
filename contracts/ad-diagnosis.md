# Output Contract: Ad Diagnosis
locked: 2026-08-26
version: 1.1.0

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
2. **Business result** - table by concept: spend, purchases, CAC against target, revenue,
   contribution after advertising
3. **Funnel result** - table by concept or ad: outbound CTR, landing page view rate, add to
   cart rate, checkout rate, purchase rate
4. **Creative result** - table by ad: spend share, three-second view rate, hold rate, thumbstop,
   frequency, comments
5. **Diagnosis** - per concept, which stage in the chain is the weak point and the number that
   shows it. Uses the diagnosis table in `references/09-testing-and-diagnosis.md` and the
   benchmarks in `references/12-meta-platform.md`
6. **Decisions** - each concept classified against the six-row decision framework, with the
   next action
7. **Ranked change list** - what to do, in order
8. **What we learned** - retained learning, including from the losers
9. **What this does not tell us** - the honest limits of this read

## Ranked change list, fixed row shape

| Rank | What | Where | Why | The number | Expected impact | Effort | Priority |
|---|---|---|---|---|---|---|---|

Every row carries a number in the number column. A row without one does not get written.

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
8. Losers get analysed, not skipped. Section 8 covers them

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
- [ ] Every concept that spent money appears in the tables
- [ ] No causal language on a non-isolated variable
- [ ] Concept results separated from execution results
- [ ] Section 9 is filled honestly
- [ ] If the test is underpowered, that governs the whole report rather than a footnote
