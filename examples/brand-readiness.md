# Frozen Example: Brand Readiness

## 1. Run identity

- Brand: Fieldnote Carry (`fieldnote-carry`)
- Market: Australia
- Product: SnapGrid Cable Pouch (`snapgrid-pouch`)
- Region: Australia (`AU`)
- Brand folder: `/brands/fieldnote-carry`
- Requested mode: manual Meta launch planning
- Evidence version: 4 from `research/evidence-ledger/manifest.json`
- Approved-learning version: 3 from `learning/active-memory.json`

## 2. Readiness verdict

**READY.** The approved coordinate, next CONTST identifier, four production records, destinations,
economics and manual operator are present. This verdict authorises planning and manual build only.
It does not claim access to or publish into a Meta account.

## 3. Website freshness

- Change check completed: 2026-08-27 09:10 AEST
- Full crawl completed: 2026-08-27 09:18 AEST, forced before launch work
- Material change found: the product price changed from AUD 69 to AUD 59
- Action taken: the owner approved AUD 59 in `EVD-OFFER-003`; all four production records and both
  destinations now use that price
- Stored in: `sources/website/snapshots/2026-08-27/` and
  `sources/website/changes/2026-08-27.md`

## 4. Evidence inventory

| Class | Evidence ID | Available evidence | Confidence | Legitimate use |
|---|---|---|---:|---|
| Verified brand fact | `EVD-PROD-001` | Transparent mesh divider and six elastic cable loops | High | Product mechanism and visual demonstration |
| Verified brand fact | `EVD-OFFER-003` | AUD 59 price and 30-day returns | High | Offer and destination truth |
| Brand assertion | `EVD-WEB-014` | "See your cables at a glance" | Medium | Current promise, not customer proof |
| Brand-customer evidence | None | Pre-customer brand | Low | No first-party customer claims permitted |
| Market evidence | `EVD-MKT-021` | 63 category reviews from six public competitor pages | Medium | Category language and hypotheses |
| Market evidence | `EVD-MKT-022` | 21 of the 63 reviews mention digging, tangles or forgotten cables | Medium | Cable-search problem hypothesis only |
| Behavioural evidence | None | No prior Fieldnote Carry ad results | Low | No performance claim or ITR source |
| Strategist judgement | `JDG-STRAT-004` | Visibility may be more useful than adding pockets | Low | NNT messaging-route hypothesis to test |

## 5. Required-input check

| Input | Required for mode | Status | Source | Freshness | Consequence | Action |
|---|---|---|---|---|---|---|
| Brand, product and region identity | Yes | VERIFIED | `brand.yml` | 2026-08-27 | None | Use codes `FNC`, `SNAPGRID`, `AU` |
| Product truth | Yes | VERIFIED | `EVD-PROD-001` | 2026-08-27 | None | Stay inside verified feature wording |
| Approved offer | Yes | VERIFIED | `EVD-OFFER-003` | 2026-08-27 | None | Use AUD 59 and 30-day returns |
| Coordinate | Yes | VERIFIED | `strategy/concept-register.yml` | 2026-08-27 | None | Use `remote-workers__cable-search` |
| Test identifier | Yes | VERIFIED | `brand.yml`, `strategy/test-register.yml` | 2026-08-27 | None | Reserve `CONTST004` once |
| Four production records | Yes | VERIFIED | `outputs/production/CONTST004/` | 2026-08-27 | None | Build UWA, PRA, SLA and PDA once each |
| Economics | Yes | VERIFIED | `EVD-ECO-002` | 2026-08-27 | None | Use AUD 24 target CAC and AUD 31 break-even CAC |
| Destination pages | Yes | VERIFIED | `EVD-PAGE-031`, `EVD-PAGE-032` | 2026-08-27 | None | Use awareness defaults |

## 6. Connector preflight

| Connector | Required capability | Actual result | Fallback |
|---|---|---|---|
| Firecrawl | Read-only website crawl | Available; both destination URLs returned HTTP 200 | Browser export and manual URL check |
| Foreplay | Read-only ad discovery | Available; one discovery query succeeded | Public Meta Ad Library |
| TrendTrack | Optional trend discovery | Unavailable; account not connected | Continue without trend data |
| Composio Notion | Optional universal-method freshness check | Unavailable; account not connected | Use reviewed repository snapshot |
| Meta Ads Manager | Manual build only | No connector requested or assumed | Maya Chen builds from Campaign Launch Plan |

## 7. Claim and compliance gate

- Approved with `EVD-CLAIM-006`: "See your cables at a glance."
- Approved facts with `EVD-PROD-001`: transparent mesh divider and six elastic cable loops
- Approved offer with `EVD-OFFER-003`: AUD 59 and 30-day returns
- Prohibited: waterproof, crush-proof, fits every charger, prevents loss, customer preference claims
- Claim owner: Alex Reed
- Active market: Australia

## 8. Learning state

- Active learning version: 3
- Approved rules applied: no guaranteed loss-prevention wording; use the verified six-loop
  description
- Unresolved conflicts: none
- Proposed learning awaiting review: one execution-level educational CTA signal, not promoted

## 9. Strategy state

- Approved coordinate key: `remote-workers__cable-search`
- Who: remote workers who carry charging gear between home and shared workspaces
- Primary Problem: finding the required cable means searching through a mixed pouch
- Pairing evidence: `EVD-MKT-021`, `EVD-MKT-022`, `JDG-STRAT-004`
- Next available test number: `CONTST004`
- Source classification: NNT, because this is a new Who x Primary Problem hypothesis for the brand
- Prior test required for ITR: not applicable
- Test-register conflict: none

## 10. Launch and destination readiness

- Production capacity: one tabletop video day plus two static design files is approved
- Controlled codes: brand `FNC`, product `SNAPGRID`, region `AU`
- Creative-testing campaign: `FNC_SNAPGRID_CT_ABO_AU_20260831`
- Ad set: `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH`
- Economics: AUD 59 price, AUD 24 target CAC, AUD 31 break-even CAC
- Budget and window: AUD 100 per day for five full days, AUD 500 planned spend
- Expected purchases at target CAC: 20.8
- UWA and PRA destination: `LP`, `https://fieldnotecarry.example/pages/cable-search`
- SLA and PDA destination: `PDP`, `https://fieldnotecarry.example/products/snapgrid-cable-pouch`
- Message-match owner: Alex Reed
- Manual Meta operator: Maya Chen
- Scaling eligibility: none until a useful winner has a real Post ID and acceptable economics

## 11. Limits on this run

- The pre-customer evidence state means no execution may imply Fieldnote Carry customer results.
- The initial test compares four complete executions. It cannot isolate awareness, messaging route,
  format or destination as the cause of a result.
- Launch is manual. The operator must complete the preflight and replace `POSTIDXXX` only after each
  ad is published and its real Post ID is verified.
- Scaling remains blocked until supplied performance data supports a winner.

## 12. Next actions

1. Final-export all four approved assets and confirm their filenames against the ad manifest.
2. Re-run both destination checks on mobile on 2026-08-31.
3. Maya Chen manually builds the ABO campaign and completes the preflight.
4. Protect the five-full-day observation window unless an allowed intervention occurs.
5. Export the supplied Meta results for diagnosis before any scale decision.
