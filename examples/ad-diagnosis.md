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
- Manual source: `SRC-QA-PD-META`, `ad-diagnosis-performance.csv`, SHA-256
  `336d4fe2be9ff8bd67338e34e297de30662c02c653f97a65c0029564824f0482`
- Date range: five full account days, `2026-08-20` through `2026-08-24`
- Attribution: `7-day click`
- Currency: `AUD`
- Aggregation level: ad
- Active thresholds supplied in the table: minimum batch spend `$300`; minimum batch purchases
  `6`; target CAC `$60`
- Actual batch result: spend `$320`; purchases `3`; revenue `$357`; expected purchases at target
  CAC `5.33`
- Missing optional metric: first-frame retention: unavailable because the supplied table has no
  first-frame field. This limits opening-frame claims but does not block the business read.
- Logged interventions: none supplied
- Spend-bearing source ads mapped: all four complete ad names listed in sections 2–5 and 8

Read validity: **Direction**. Five full days elapsed and spend exceeded the `$300` minimum, but the
batch produced `3` purchases, `3` fewer than the `6`-purchase threshold. The report can describe
bounded associations and next checks; it cannot claim a final causal verdict. The missing optional
creative metric narrows section 5 only.

## 2. What was tested

| Full ad name | Existing test | Coordinate | Source | Who | Primary Problem | Awareness | Route | Format | Destination | Window | Intervention |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001` | `CONTST042` | `night-readers__shared-room-glare` | NNT | Night readers sharing a room | Lighting the page disturbs a partner | UWA | Page-light recognition | VSL | LP | Five full days | None supplied |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002` | `CONTST042` | `night-readers__shared-room-glare` | NNT | Night readers sharing a room | Lighting the page disturbs a partner | PRA | Glare-direction diagnosis | STATIC | LP | Five full days | None supplied |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003` | `CONTST042` | `night-readers__shared-room-glare` | NNT | Night readers sharing a room | Lighting the page disturbs a partner | SLA | Light-direction differentiation | COMPARISON | PDP | Five full days | None supplied |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004` | `CONTST042` | `night-readers__shared-room-glare` | NNT | Night readers sharing a room | Lighting the page disturbs a partner | PDA | Product decision | STATIC | PDP | Five full days | None supplied |

Campaign: `QUIETARC_READINGLAMP_CT_ABO_AU_20260820`. Ad set:
`CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE`. The initial NNT contains UWA, PRA, SLA and PDA. UWA
and PRA use LP; SLA and PDA use PDP. Every execution follows its awareness default, so no
Destination Handoff exception is applicable. No budget or creative intervention was supplied.

## 3. What happened: business result

| Full ad name | Stage | Spend | Spend share | Purchases | CAC vs `$60` target | Revenue | Contribution after advertising | Expected purchases at target |
|---|---|---:|---:|---:|---|---:|---|---:|
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001` | Initial test | `$180` | `56.25%` | `2` | `$90`, `$30` above target | `$238` | unavailable; margin not supplied | `3.00` |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002` | Initial test | `$80` | `25.00%` | `1` | `$80`, `$20` above target | `$119` | unavailable; margin not supplied | `1.33` |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003` | Initial test | `$40` | `12.50%` | `0` | unavailable; no purchases | `$0` | unavailable; margin not supplied | `0.67` |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004` | Initial test | `$20` | `6.25%` | `0` | unavailable; no purchases | `$0` | unavailable; margin not supplied | `0.33` |

Every ad with supplied spend appears above. The uneven `56.25%`/`25.00%`/`12.50%`/`6.25%`
delivery and the batch's three missing purchases keep this read directional.

## 4. What happened: funnel result

| Full ad name | Outbound CTR | Landing-page-view rate | Add-to-cart rate | Checkout rate | Purchase rate |
|---|---:|---:|---:|---:|---:|
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001` | `1.80%` (`162/9,000`) | `86.42%` (`140/162`) | `10.00%` (`14/140`) | `50.00%` (`7/14`) | `28.57%` (`2/7`) |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002` | `2.40%` (`96/4,000`) | `67.71%` (`65/96`) | `12.31%` (`8/65`) | `50.00%` (`4/8`) | `25.00%` (`1/4`) |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003` | `1.80%` (`36/2,000`) | `83.33%` (`30/36`) | `13.33%` (`4/30`) | `50.00%` (`2/4`) | `0.00%` (`0/2`) |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004` | `2.50%` (`25/1,000`) | `48.00%` (`12/25`) | `8.33%` (`1/12`) | `0.00%` (`0/1`) | unavailable; no checkout |

No account norms were supplied. These rows support comparisons within this pack only. The PRA and
PDA executions have the highest outbound CTRs but materially lower landing-page-view rates than
the UWA and SLA executions.

## 5. What happened: creative result

| Full ad name | Spend share | First-frame retention | Three-second view rate | Hold rate | Thumbstop | Frequency | Comments |
|---|---:|---|---:|---:|---:|---:|---|
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001` | `56.25%` | unavailable | `30.00%` (`2,700/9,000`) | `33.33%` (`900/2,700`) | `30.00%` | `1.38` | 3 positive, 1 delivery question |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002` | `25.00%` | not applicable to static | not applicable to static | not applicable to static | not applicable to static | `1.33` | 1 positive, 0 delivery question |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003` | `12.50%` | unavailable | `40.00%` (`800/2,000`) | `40.00%` (`320/800`) | `40.00%` | `1.25` | 1 positive, 0 delivery question |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004` | `6.25%` | not applicable to static | not applicable to static | not applicable to static | not applicable to static | `1.11` | 0 positive, 1 delivery question |

First-frame retention is unavailable for both video executions. No opening-frame conclusion is
made from that gap. Static rows do not receive video-rate claims.

## 6. Strongest and weakest complete executions

1. The UWA is the strongest business execution: it produced `2` purchases at `$90` CAC. This still
   misses the `$60` target and remains directional because the batch is three purchases short and
   delivery was uneven.
2. The PRA produced `1` purchase at `$80` CAC while its `2.40%` outbound CTR narrowed to a `67.71%`
   landing-page-view rate.
3. The SLA had the strongest supplied video ratios, but `$40` spend produced no purchase. That is a
   bounded creative signal, not proof that its route or format caused a result.
4. The PDA is the weakest delivered read: it received only `$20`, and its `2.50%` outbound CTR
   narrowed to a `48.00%` landing-page-view rate. That low exposure does not support a stop verdict.

## 7. Likely explanations

| Full ad name | Observed association | Likely explanation to check | Disconfirming evidence | Confidence | What would test it |
|---|---|---|---|---|---|
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001` | `2` purchases at `$90` CAC are associated with the UWA and `56.25%` of spend | The page-light recognition execution may carry the clearest complete commercial argument | Higher delivery could explain part of the purchase concentration; first-frame retention is absent | Low | A human-approved narrower ITR against the same coordinate |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002` | `2.40%` outbound CTR is associated with a `67.71%` landing-page-view rate and `$80` CAC | Destination load, tracking or promise continuity may weaken after the click | The execution did produce one purchase; no technical destination audit was supplied | Low | Verify URL, load and events before further spend |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003` | `40.00%` thumbstop and hold are associated with no purchase from `$40` spend | The comparison may hold attention without enough decision value | Only `2` checkouts and `$40` spend were supplied; first-frame retention is absent | Low | A separately approved ITR isolating proof or decision value |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004` | `2.50%` outbound CTR is associated with a `48.00%` landing-page-view rate and no checkout | A click-to-page break may sit before product evaluation | The ad received only `$20`; delivery is too low for a confident execution verdict | Low | Verify the destination, then collect a fuller read without changing the execution |

These are cautious explanations from a broad complete-execution comparison, not isolated-variable
findings.

## 8. Six-decision taxonomy

| Full ad name | Decision | Top-level action | Numbers and thresholds | Likely explanation | Explanation confidence | Execution instruction |
|---|---|---|---|---|---|---|
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001` | Directional promise | `ITR` | `$90` CAC is `$30` above the `$60` target; `2` purchases; batch is `3` short of minimum | The complete UWA is associated with the strongest supplied business result, with uneven delivery as a competing explanation | Low | Propose one narrower follow-up against the same Who and Primary Problem; leave CONTST unreserved |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002` | Interest, weak conversion | `keep` | `2.40%` outbound CTR; `67.71%` landing-page-view rate; `$80` CAC is `$20` above target | A destination or tracking break may sit between click and landing-page view | Low | Keep the execution and coordinate unchanged while URL, load and event integrity are checked |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003` | Directional promise | `ITR` | `40.00%` thumbstop and hold; `0` purchases from `$40` against a `$60` target CAC | The complete comparison may hold attention without enough decision value | Low | Propose a bounded proof or decision-value follow-up; leave CONTST unreserved |
| `CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004` | Interest, weak conversion | `keep` | `2.50%` outbound CTR; `48.00%` landing-page-view rate; `0` purchases from `$20` | A destination break may precede product evaluation, but delivery is low | Low | Keep unchanged while the destination is checked and a fuller read is collected |

Each reviewed spend-bearing item has exactly one top-level action. Every action cell equals one
literal governed value and contains no sequence, alternative or conditional prose.

## 9. Ranked change list

| Rank | What | Where | Why | The number | Expected impact | Effort | Priority |
|---|---|---|---|---|---|---|---|
| 1 | Verify destination URL, load and event integrity | PRA and PDA destinations | Click-to-view loss is the first measurable break | `67.71%` and `48.00%` landing-page-view rates | Determine whether those conversion reads are trustworthy | Low | 1 |
| 2 | Present a narrower UWA ITR brief for human build decision | Existing `CONTST042` coordinate | The strongest complete execution still misses target CAC and validity volume | `$90` CAC versus `$60`; `2/6` required purchases | Test whether the bounded signal repeats | Medium | 2 |
| 3 | Present a separate bounded SLA follow-up option | Existing `CONTST042` coordinate | Video ratios did not translate to a purchase | `40.00%` thumbstop and hold; `$40`; `0` purchases | Test proof or decision value without claiming format causation | Medium | 3 |

## 10. What we learned

- Proposed test observation for existing `CONTST042`: the UWA produced `2` supplied purchases at
  `$90` CAC while receiving `56.25%` of spend; confidence is low because the read is Direction and
  delivery was uneven.
- Proposed test observation for existing `CONTST042`: the PRA and PDA click signals narrowed at the
  landing-page-view stage; confidence is low because no destination audit was supplied.
- Proposed test observation for existing `CONTST042`: the SLA's `40.00%` thumbstop and hold did not
  produce a purchase from `$40`; confidence is low and no isolated cause is claimed.
- These remain test memory. No copy, claim, voice or universal-method rule is approved by this report.

## 11. What this does not tell us

This five-day read does not isolate awareness, route, format, hook, proof or destination causation.
It does not supply the three additional purchases required for a Verdict, first-frame retention,
account norms, margin inputs, a destination technical audit or evidence that any proposed patch was
confirmed. The complete names contain real Post IDs, but no winner can graduate because graduation
confirmation was not supplied.

## Persistence Summary

- Written run output: `diagnosis.md`.
- Proposed file: `test-register-patch.yml`, targeting matching existing test `CONTST042` only; it
  contains no new test ID.
- Proposed observation: UWA produced `2` purchases at `$90` CAC with `56.25%` of spend; PRA click to
  landing-page view narrowed to `67.71%`; SLA had `40.00%` thumbstop and hold with no purchase from
  `$40`; PDA click to landing-page view narrowed to `48.00%` with no purchase from `$20`.
- Evidence: five full days; `$320` spend; `3` purchases; `$357` revenue; `$60` target CAC; `$300`
  minimum spend; `6` minimum purchases; all four spend-bearing rows from
  `ad-diagnosis-performance.csv`.
- Explanation confidence: Low; uneven delivery, absent first-frame retention and no destination
  technical audit limit the explanation.
- Verdict: Direction.
- Next action: `ITR`; present the narrower UWA brief first, but do not reserve a new test.
- Destination record: `strategy/test-register.yml`, existing `CONTST042` observation only.
- Confirmation: required and not supplied; the proposed patch is not persisted.
- Proposed `next-brief.md`: one narrower UWA ITR description for the same coordinate.
- CONTST: unreserved — human decision required
- Winner-library proposal: none. Real Post IDs `991001000000001`–`991004000000004` are supplied.
- Graduation confirmation: not supplied; winner persistence is prohibited.
- Approved-revision learning: none. Any human copy, claim or voice edit routes through
  `contracts/learning-update.md`.
- Upload-only status: patch only; persistence not claimed.
- Owner: Mina Cole.
