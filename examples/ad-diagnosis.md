# Frozen Example: Performance Diagnosis

## 1. Input audit and read validity

- Run ID: `ADR-20260827-015`
- Intake path: `outputs/ad-analysis/ADR-20260827-015/intake.json`
- Validator status: `limited`
- Input-audit path: `outputs/ad-analysis/ADR-20260827-015/input-audit.md`
- Brand: `quiet-arc`
- Market: `AU`
- Product: `folding-reading-lamp`
- Account timezone: `Australia/Sydney`
- Manual source: `SRC-QA-PD-003`, Meta ad-level table supplied as
  `quiet-arc-20260820-20260824.csv`
- Date range: five full days, `2026-08-20 00:00` through `2026-08-24 23:59`
- Attribution: `7-day click`
- Currency: `AUD`
- Aggregation level: ad
- Active thresholds: minimum batch spend `$300`; minimum batch purchases `6`; target CAC `$60`
- Actual batch result: spend `$320`; purchases `4`; expected purchases at target CAC `5.33`
- Missing optional metric: first-frame retention: unavailable because the supplied export has no
  first-frame field. This limits opening-frame claims but does not block the business read.
- Logged interventions: none supplied
- Spend-bearing source ads mapped: `QA_CONTST042_UWA_VIDEO_PDP_991001` to `AD-QA-PD-001` and
  `QA_CONTST042_PDA_STATIC_PDP_991002` to `AD-QA-PD-002`

Read validity: **Direction**. Five full days elapsed and spend exceeded the `$300` minimum, but the
batch produced `4` purchases, `2` fewer than the `6`-purchase threshold. The report can describe
bounded associations and next checks; it cannot claim a final causal verdict. The missing optional
creative metric narrows section 5 only.

## 2. What was tested

| Ad | Existing test | Coordinate | Source | Who | Primary Problem | Awareness | Route | Format | Destination | Window | Intervention |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `AD-QA-PD-001` | `CONTST042` | `night-readers__shared-room-glare` | NNT | Night readers sharing a room | Lighting the page disturbs a partner | UWA | Page-light contrast | Video | PDP | Five full days | None supplied |
| `AD-QA-PD-002` | `CONTST042` | `night-readers__shared-room-glare` | NNT | Night readers sharing a room | Lighting the page disturbs a partner | PDA | Product convenience | Static | PDP | Five full days | None supplied |

Campaign: `QUIETARC_READINGLAMP_CT_ABO_AU_20260820`. Ad set:
`CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE`. No budget or creative intervention was supplied.

## 3. What happened: business result

| Ad | Stage | Spend | Spend share | Purchases | CAC vs `$60` target | Revenue | Contribution after advertising | Expected purchases at target |
|---|---|---:|---:|---:|---|---:|---|---:|
| `AD-QA-PD-001` | Initial test | `$240` | `75%` | `4` | `$60`, at target | `$476` | unavailable; margin not supplied | `4.00` |
| `AD-QA-PD-002` | Initial test | `$80` | `25%` | `0` | unavailable; no purchases | `$0` | unavailable; margin not supplied | `1.33` |

Every ad with supplied spend appears above. The uneven `75%`/`25%` delivery and the batch's two
missing purchases keep this read directional.

## 4. What happened: funnel result

| Ad | Outbound CTR | Landing-page-view rate | Add-to-cart rate | Checkout rate | Purchase rate |
|---|---:|---:|---:|---:|---:|
| `AD-QA-PD-001` | `1.80%` (`216/12,000`) | `87.96%` (`190/216`) | `10.53%` (`20/190`) | `50.00%` (`10/20`) | `40.00%` (`4/10`) |
| `AD-QA-PD-002` | `2.80%` (`70/2,500`) | `57.14%` (`40/70`) | `12.50%` (`5/40`) | `40.00%` (`2/5`) | `0.00%` (`0/2`) |

No account norms were supplied. These rows support comparisons within this pack only. In
particular, `AD-QA-PD-002` has the higher outbound CTR but the lower landing-page-view rate.

## 5. What happened: creative result

| Ad | Spend share | First-frame retention | Three-second view rate | Hold rate | Thumbstop | Frequency | Comments |
|---|---:|---|---:|---:|---:|---:|---|
| `AD-QA-PD-001` | `75%` | unavailable | `36%` | `18%` | `28%` | `1.4` | 3 positive, 1 delivery question |
| `AD-QA-PD-002` | `25%` | unavailable | not applicable to static | not applicable to static | unavailable | `1.2` | 1 delivery question |

First-frame retention is unavailable for the video and thumbstop is unavailable for the static.
No opening-frame conclusion is made from those gaps.

## 6. Strongest and weakest complete executions

1. `AD-QA-PD-001` is the strongest supplied execution: it produced all `4` purchases at the `$60`
   target CAC. This is directional because the batch remains two purchases short and delivery was
   uneven.
2. `AD-QA-PD-002` is the weakest business execution: it spent `$80` and produced no purchases. Its
   `2.80%` outbound CTR is a bounded interest signal, so the result does not establish that the
   complete execution or coordinate is weak throughout.

## 7. Likely explanations

| Ad | Observed association | Likely explanation to check | Disconfirming evidence | Confidence | What would test it |
|---|---|---|---|---|---|
| `AD-QA-PD-001` | All `4` purchases are associated with the video execution and `$240` spend | The page-light contrast may be more commercially coherent as a complete execution | `75%` of spend went to this ad, so delivery alone could explain part of the volume | Low | A separately approved narrower ITR against the same coordinate |
| `AD-QA-PD-002` | `2.80%` outbound CTR is associated with only `57.14%` landing-page-view rate and `0` purchases | Destination load, tracking or promise continuity may be losing visits after the click | Only `70` clicks and `2` checkouts were supplied; no speed or tracking audit was supplied | Low | Verify URL, load and events before further spend |

These are cautious explanations from a broad complete-execution comparison, not isolated-variable
findings.

## 8. Six-decision taxonomy

| Reviewed item | Decision | Top-level action | Numbers and thresholds | Likely explanation | Explanation confidence | Execution instruction |
|---|---|---|---|---|---|---|
| `AD-QA-PD-001` | Directional promise | `ITR` | `$60` CAC at target; `4` purchases; batch is `2` short of minimum | Complete page-light execution is associated with all supplied purchases, with uneven delivery as a competing explanation | Low | Propose one narrower follow-up against the same Who and Primary Problem; leave CONTST unreserved |
| `AD-QA-PD-002` | Interest, weak conversion | `keep` | `2.80%` outbound CTR; `57.14%` landing-page-view rate; `0` purchases from `$80` | A destination or tracking break may sit between click and landing-page view | Low | Keep the execution and coordinate unchanged while URL, load and event integrity are checked |

Each reviewed spend-bearing item has exactly one top-level action. The action field contains no
sequence, alternative or conditional prose.

## 9. Ranked change list

| Rank | What | Where | Why | The number | Expected impact | Effort | Priority |
|---|---|---|---|---|---|---|---|
| 1 | Verify destination URL, load and event integrity | `AD-QA-PD-002` to PDP | Click-to-view loss is the first measurable break | `57.14%` landing-page-view rate from `70` clicks | Determine whether the conversion read is trustworthy | Low | 1 |
| 2 | Present a narrower ITR brief for human build decision | `AD-QA-PD-001` coordinate | The complete execution reached target CAC but the read is short of purchase validity | `$60` CAC, `4/6` required purchases | Test whether the bounded signal repeats | Medium | 2 |

## 10. What we learned

- Proposed test observation for existing `CONTST042`: the video execution accounted for `4` supplied
  purchases at `$60` CAC while receiving `75%` of spend; confidence is low because the read is
  Direction and delivery was uneven.
- Proposed test observation for existing `CONTST042`: the static execution's `2.80%` outbound CTR
  narrowed to a `57.14%` landing-page-view rate and no purchases from `$80`; confidence is low.
- These remain test memory. No copy, claim, voice or universal-method rule is approved by this report.

## 11. What this does not tell us

This five-day read does not isolate awareness, route, format, hook, proof or destination causation.
It does not supply the two additional purchases required for a Verdict, a first-frame measure,
account norms, margin inputs, a destination technical audit or evidence that any proposed patch was
confirmed. No winner can graduate because no graduation confirmation was supplied.

## Persistence Summary

- Written run output: `diagnosis.md`.
- Proposed `test-register-patch.yml`: update observations, supplied results, confidence, verdict and
  next action for matching existing test `CONTST042` only. No new test ID is present. Human
  confirmation is required before the canonical test register changes.
- Proposed `next-brief.md`: one narrower ITR description for the same coordinate.
- CONTST: unreserved — human decision required
- Winner-library patch: none; graduation lacks confirmation even though real Post IDs are present.
- Approved-revision learning: none. Any human copy, claim or voice edit routes through
  `contracts/learning-update.md`.
- Upload-only status: patch only; persistence not claimed.
- Owner: Mina Cole.
