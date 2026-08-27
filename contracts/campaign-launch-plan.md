# Output Contract: Campaign Launch Plan
locked: 2026-08-27
version: 1.0.0

The manual build sheet for creating and validating Meta creative-testing and scaling campaigns. It
does not publish, edit budgets, retrieve account data or imply a live Meta connection.

## Artefact

Markdown document. `campaign-launch-plan-BRAND-PRODUCT-REGION-YYYYMMDD.md`

## Sections, in order

1. **Launch identity** - brand, market, product, region, operator, planned launch date, timezone,
   source folder or bundle version and readiness verdict
2. **Campaign structure** - stage, objective, conversion location and event, budget type, campaign
   name, ad sets and manual Ads Manager build order
3. **Test-batch manifest** - coordinate key, CONTST test ID, source, Who, Primary Problem, full ad-set
   name, prior CONTST for ITR and test question
4. **Budget and read plan** - daily ad-set budget, total planned spend, price, target CAC, break-even
   CAC, expected purchases at target CAC, observation window and read limitations
5. **Ad manifest** - one row per ad with full name, awareness job, messaging route, primary hook,
   media type, execution format, proof, destination, CTA, asset status and Post ID status
6. **Destination validation** - one linked Destination Handoff per ad, final URL, default or exception,
   message-match result, tracking and page-owner approval
7. **Manual preflight** - exact checks the human operator completes before publishing
8. **Observation protocol** - start and end timestamps, five-full-day protection, allowed interventions,
   manual evidence capture and review owner
9. **Scaling handoff** - eligible winners, real Post IDs, scaling campaign and ad-set placement, CBO
   budget decision, economics guardrail and scale-result record
10. **Launch decision** - READY, READY WITH LIMITS or BLOCKED, unresolved items and accountable owner

## Creative testing

- Budget type: ABO.
- One CONTST batch per ad set.
- Every initial NNT or INSPO ad set contains exactly four ads: UWA, PRA, SLA and PDA.
- An evidence-led ITR may use a narrower set when it cites the prior CONTST and states the reason.
- Absolute floor: $50 per ad set per day.
- Preferred starting point: approximately $100 per ad set per day.
- Planned observation window: five full days.

The daily budget may exceed the preferred starting point when price, target CAC, break-even CAC,
available capital and account context support it. It may never fall below the absolute floor. Record
the reasoning and the currency. Calculate expected purchases at target CAC before launch. Five days
is the planned review point, not permission to declare a verdict when spend or purchase thresholds
are unmet.

Use one creative-testing campaign for one product and one region. The campaign budget setting is
off because budgets live at the ad-set level. Each ad set contains one batch, never a mixture of
CONTST identifiers.

## Scaling

- Budget type: CBO.
- Create scaling only when useful winners exist.
- Graduated ads keep their real Post ID.
- Use the SC campaign name and record scaling performance separately from initial-test performance.
- Only ads that retain acceptable economics at higher spend enter the evergreen winner library.

Never rebuild a graduated winner as a fresh `POSTIDXXX` ad. The manual operator selects the existing
published post by its real Post ID, verifies the identity and records that ID in the handoff. A scale
failure does not erase the initial-test result.

## Naming, fixed

| Level | Exact shape |
|---|---|
| Creative-testing campaign | `[BRAND]_[PRODUCT]_CT_ABO_[REGION]_[YYYYMMDD]` |
| Scaling campaign | `[BRAND]_[PRODUCT]_SC_CBO_[REGION]_[YYYYMMDD]` |
| Ad set | `[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]` |
| Ad | `[FULL_AD_SET_NAME]_[UWA|PRA|SLA|PDA]_[FORMAT]_[LP|PDP|HP|CP]_[POSTID]` |

The full ad-set name is inherited without abbreviation. Before publication, `[POSTID]` is
`POSTIDXXX`. After publication, record and use the real Post ID. Use underscores only and no
version suffix.

## Initial ad manifest, fixed row shape

| Order | Full ad name | CONTST | Source | Who | Primary Problem | Awareness and job | Messaging route | Primary hook | Media type | Format | Proof and claims | Destination | CTA | People, assets and location | Asset status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Initial NNT and INSPO manifests contain exactly four rows in UWA, PRA, SLA and PDA order. UWA and
PRA default to LP. SLA and PDA default to PDP. Every deliberate deviation must use one controlled
destination token: LP, PDP, HP or CP, and requires a complete Destination Handoff. A page that
cannot be accurately represented by one of those tokens blocks launch.

## Manual preflight

- [ ] Correct brand, product, region, pixel or dataset, conversion event, currency and timezone
- [ ] Sales objective and conversion location match the approved plan
- [ ] Creative-testing campaign is ABO and each ad set has its own approved daily budget
- [ ] Each ad set contains one CONTST batch and no ad from another batch
- [ ] Initial NNT and INSPO ad sets contain exactly UWA, PRA, SLA and PDA once each
- [ ] Campaign, ad-set and ad names match the fixed shapes with no version suffix
- [ ] Every ad opens the intended asset and its copy, CTA and URL match the production record
- [ ] Every claim and proof object has the required approval for the active market
- [ ] Every Destination Handoff passes or records an approved deliberate exception
- [ ] Every default and exception uses one controlled destination token: LP, PDP, HP or CP
- [ ] Tracking parameters, page status, stock, price, shipping, offer and checkout are verified
- [ ] Start and end timestamps provide five full days in the recorded account timezone
- [ ] Manual operator and review owner are named

## Observation protocol

Do not make routine creative, copy, destination, audience or budget changes during the five full
days. Intervention is allowed only for an operational failure, broken destination, policy issue or
unacceptable commercial risk. Record what changed, when, why, by whom and how it limits the read.
Capture exports, screenshots or tables manually for diagnosis. No contract in this package
authorises automatic account access or campaign mutation.

## Self-check before presenting

- [ ] ABO testing and CBO scaling are not mixed
- [ ] One test batch maps to one testing ad set
- [ ] Budget floor, preferred starting point and five-full-day window are explicit
- [ ] Expected purchases at target CAC and validity limits are calculated
- [ ] Every initial NNT or INSPO manifest has exactly four correctly named ads
- [ ] Destination defaults and every exception are recorded
- [ ] Scaling uses real Post IDs and records scale results separately
- [ ] The plan is an executable manual build sheet, not a claim of live Meta access
