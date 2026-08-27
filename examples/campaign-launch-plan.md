# Frozen Example: Campaign Launch Plan

## 1. Launch identity

- Brand: Fieldnote Carry (`fieldnote-carry`)
- Market: Australia
- Product: SnapGrid Cable Pouch (`snapgrid-pouch`)
- Region: Australia (`AU`)
- Manual operator: Maya Chen
- Review owner: Alex Reed
- Planned launch: 2026-08-31 09:00 AEST
- Account timezone: Australia/Sydney
- Source: `/brands/fieldnote-carry`, evidence version 4, approved-learning version 3
- Readiness verdict: READY in `examples/brand-readiness.md`
- Live Meta connection: not present, required or implied

## 2. Campaign structure

| Field | Approved value |
|---|---|
| Stage | Creative testing |
| Objective | Sales |
| Conversion location | Website |
| Conversion event | Purchase |
| Budget type | ABO |
| Campaign name | `FNC_SNAPGRID_CT_ABO_AU_20260831` |
| Campaign budget setting | Off |
| Ad set | `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH` |
| Ad-set count | 1 |
| Ads in ad set | 4 |

Manual Ads Manager build order:

1. Maya Chen selects the approved Australia ad account, dataset and Purchase event.
2. Create the Sales campaign named `FNC_SNAPGRID_CT_ABO_AU_20260831` with campaign budget off.
3. Create one ad set named `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH` at AUD 100 per day.
4. Apply the approved Australia prospecting audience and placements from the brand folder.
5. Create the UWA, PRA, SLA and PDA ads from the manifest below, in that order.
6. Attach each approved asset, copy record, CTA and final URL.
7. Complete the manual preflight, publish, then record each real Post ID without renaming the batch.

## 3. Test-batch manifest

| Field | Value |
|---|---|
| Coordinate key | `remote-workers__cable-search` |
| CONTST test ID | `CONTST004` |
| Source | NNT |
| Who | Remote workers who carry charging gear between home and shared workspaces |
| Primary Problem | Finding the required cable means searching through a mixed pouch |
| Full ad-set name | `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH` |
| Prior CONTST for ITR | Not applicable |
| Pairing evidence | `EVD-MKT-021`, `EVD-MKT-022`, `JDG-STRAT-004` |
| Test question | Which complete execution produces the strongest commercially valid signal for this new coordinate? |

This NNT batch creates the first record for the coordinate. It intentionally varies awareness job,
messaging route, format and destination. Its result can identify a promising complete execution,
but cannot prove which individual variable caused the result.

## 4. Budget and read plan

| Input | Value |
|---|---:|
| Daily ad-set budget | AUD 100 |
| Absolute method floor | AUD 50 |
| Planned observation window | 5 full days |
| Planned start | 2026-08-31 09:00 AEST |
| Planned end and first review | 2026-09-05 09:00 AEST |
| Total planned spend | AUD 500 |
| Product price | AUD 59 |
| Target CAC | AUD 24 |
| Break-even CAC | AUD 31 |
| Expected purchases at target CAC | 20.8 |
| Economics source | `EVD-ECO-002` |

AUD 100 is above the AUD 50 floor and matches the preferred starting point. It is supported by the
supplied target CAC and the approved AUD 500 test allocation. Five full days is the planned review
point, not an automatic verdict. If delivery or purchases are too low for the brand thresholds, the
read remains directional or too early.

## 5. Ad manifest

| Order | Full ad name | CONTST | Source | Who | Primary Problem | Awareness and job | Messaging route | Primary hook | Media type | Format | Proof and claims | Destination | CTA | People, assets and location | Asset status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH_UWA_UGC_LP_POSTIDXXX` | `CONTST004` | NNT | Remote workers | Cable search | UWA, recognition | Story | "The cable search starts before the work does" | VIDEO | UGC | `EVD-MKT-021`; staged situation, no customer claim | `LP` | Learn More | Creator, work bag, mixed pouch, laptop, home-office desk | READY |
| 2 | `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH_PRA_STATIC_LP_POSTIDXXX` | `CONTST004` | NNT | Remote workers | Cable search | PRA, diagnosis | Reframe | "Packed is not the same as easy to find" | STATIC | STATIC | `EVD-MKT-022`; no prevalence claim | `LP` | Learn More | SnapGrid, plain pouch, six cables, overhead product image | READY |
| 3 | `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH_SLA_COMPARISON_PDP_POSTIDXXX` | `CONTST004` | NNT | Remote workers | Cable search | SLA, differentiation | Proof that can be seen | "Same six cables. Two very different ways to find one" | VIDEO | COMPARISON | `EVD-PROD-001`; fair same-item demonstration | `PDP` | Shop Now | Hand model, two pouches, matched cables, locked tabletop camera | READY |
| 4 | `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH_PDA_CAROUSEL_PDP_POSTIDXXX` | `CONTST004` | NNT | Remote workers | Cable search | PDA, decision | Objection resolution | "See the layout before you decide" | CAROUSEL | CAROUSEL | `EVD-PROD-001`, `EVD-OFFER-003`, `EVD-CLAIM-006` | `PDP` | Shop Now | Product stills, dimension diagram, returns card, design files | READY |

All four names inherit the complete ad-set name, use one controlled awareness code, one controlled
format token and one controlled destination token, and end in `POSTIDXXX` before publication.

## 6. Destination validation

| Ad | Linked Destination Handoff | Final URL | Route status | Message match | Tracking | Page-owner approval |
|---|---|---|---|---|---|---|
| UWA | `examples/destination-handoff.md`, UWA card | `https://fieldnotecarry.example/pages/cable-search` | `LP`, DEFAULT | PASS | `utm_content=CONTST004_UWA` verified | Alex Reed, 2026-08-31 |
| PRA | `examples/destination-handoff.md`, PRA card | `https://fieldnotecarry.example/pages/cable-search` | `LP`, DEFAULT | PASS | `utm_content=CONTST004_PRA` verified | Alex Reed, 2026-08-31 |
| SLA | `examples/destination-handoff.md`, SLA card | `https://fieldnotecarry.example/products/snapgrid-cable-pouch` | `PDP`, DEFAULT | PASS | `utm_content=CONTST004_SLA` verified | Alex Reed, 2026-08-31 |
| PDA | `examples/destination-handoff.md`, PDA card | `https://fieldnotecarry.example/products/snapgrid-cable-pouch` | `PDP`, DEFAULT | PASS | `utm_content=CONTST004_PDA` verified | Alex Reed, 2026-08-31 |

No destination exception is used. The LP recognises and diagnoses cable-search friction before
introducing the product. The PDP shows the layout, verified mechanism, AUD 59 price, 30-day returns
and purchase CTA required by the SLA and PDA executions.

## 7. Manual preflight

- [x] Brand, product, region, dataset, Purchase event, AUD currency and Australia/Sydney timezone checked
- [x] Sales objective and website conversion location match the approved plan
- [x] Creative-testing campaign uses ABO and the ad set uses AUD 100 per day
- [x] The ad set contains only `CONTST004`
- [x] UWA, PRA, SLA and PDA each appear exactly once
- [x] Campaign, ad-set and ad names match the fixed shapes with no version suffix
- [x] Each approved asset opens and matches its production record, CTA and URL
- [x] Claims and proof objects are approved for Australia
- [x] All four Destination Handoff cards pass with controlled destination tokens
- [x] Tracking, page status, stock, AUD 59 price, shipping, 30-day returns and checkout checked
- [x] Observation timestamps cover five full days
- [x] Manual operator Maya Chen and review owner Alex Reed are recorded

Manual preflight completed by Maya Chen at 2026-08-31 08:42 AEST.

## 8. Observation protocol

- Protected window: 2026-08-31 09:00 AEST through 2026-09-05 09:00 AEST
- No routine creative, copy, audience, destination or budget changes during the window
- Allowed intervention: operational failure, broken destination, policy issue or unacceptable
  commercial risk only
- Intervention record: timestamp, exact change, reason, operator and effect on read validity
- Evidence capture: Maya Chen exports campaign, ad-set and ad tables after the window and saves the
  attribution setting, date range, currency and screenshots
- Review owner: Alex Reed

## 9. Scaling handoff

- Eligible winners: none before the creative-testing read
- Scaling campaign shape: `FNC_SNAPGRID_SC_CBO_AU_YYYYMMDD`, dated only when created
- Budget type: CBO
- Post ID rule: a graduated ad keeps its verified real Post ID; it is never rebuilt as `POSTIDXXX`
- Economics guardrail: target CAC AUD 24, break-even CAC AUD 31, plus supplied contribution data
- Scale result: stored separately from the `CONTST004` initial-test result
- Evergreen eligibility: only after acceptable economics persist at higher spend

## 10. Launch decision

**READY.** The manual preflight passed at 2026-08-31 08:42 AEST. Maya Chen is accountable for the
manual build and publication. Alex Reed owns the five-day review. No unresolved blocking item or
destination exception remains, and no live Meta access is claimed.
