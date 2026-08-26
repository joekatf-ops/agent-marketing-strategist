# Frozen Example: Brand Readiness

## 1. Run identity

- Brand: `fieldnote-carry`
- Market: Australia
- Product: `snapgrid-pouch`
- Brand folder: `/brands/fieldnote-carry`
- Requested mode: customer research
- Evidence version: 4 from `research/evidence-ledger/manifest.json`
- Learning version: 3 from `learning/active-memory.json`

## 2. Readiness verdict

**READY WITH LIMITS.** Research can proceed. This is a pre-customer brand with no first-party
reviews, interviews, support data, or sales behaviour. Customer conclusions must remain market
evidence or founder hypotheses until first-party evidence exists.

## 3. Website freshness

- Change check completed: 2026-08-26 09:10 AEST
- Previous full crawl: 2026-08-18 16:30 AEST
- Action: full Firecrawl refresh completed because the snapshot was eight days old
- Material changes: launch price changed from AUD 69 to AUD 59; returns page unchanged
- Stored in: `sources/website/snapshots/2026-08-26/` and `sources/website/changes/2026-08-26.md`

## 4. Evidence inventory

| Class | Available evidence | Confidence | Legitimate use |
|---|---|---:|---|
| Verified brand fact | Product spec, price, material, 30-day returns | High | Product and offer truth |
| Brand assertion | "See every cable at a glance" website promise | Medium | Current positioning, not customer proof |
| Brand-customer evidence | None | Low | No first-party customer claims permitted |
| Market evidence | 63 competitor reviews, 8 competitor sites, 4 community threads | Medium | Category language and hypotheses |
| Behavioural evidence | None | Low | No conversion or retention conclusions |
| Strategist judgement | Visibility may be a stronger angle than compactness | Low | Concept hypothesis to validate |

## 5. Required-input check

| Input | Required for mode | Status | Source | Freshness | Consequence | Action |
|---|---|---|---|---|---|---|
| Brand identity | Yes | VERIFIED | `brand.yml` | Current | None | Use as supplied |
| Product truth | Yes | VERIFIED | `products/catalog.yml` | 2026-08-25 | None | Use approved fields |
| Website | Yes | VERIFIED | Firecrawl snapshot | 2026-08-26 | None | Cite retrieved pages |
| Customer reviews | No | MISSING | Pre-customer status | Current | No brand-customer conclusions | Use market evidence labels |
| Competitor set | Yes | PRESENT BUT UNVERIFIED | Founder seeds | 2026-08-25 | Discovery may be narrow | Expand by category search |
| Economics | No | PRESENT BUT UNVERIFIED | `products/economics.yml` | 2026-08-25 | Commercial advice provisional | Owner to verify landed cost |

## 6. Connector preflight

| Connector | Required capability | Result | Fallback |
|---|---|---|---|
| Firecrawl | Map and crawl public sites | Available; test page returned with URL | Browser export if later calls fail |
| TrendTrack | Discover relevant active ads | Unavailable; authentication rejected | Foreplay and public ad library |
| Foreplay | Brand and ad discovery | Available; one read-only brand query succeeded | Public ad library |

## 7. Claim and compliance gate

- Approved: transparent mesh divider, six elastic cable loops, AUD 59 launch price, 30-day returns
- Unapproved: waterproof, crush-proof, fits every charger
- Market restriction: do not imply verified customer preference before customers exist
- Owner: product lead

## 8. Learning state

- Active learning version: 3
- Unresolved conflicts: none
- Proposed learning awaiting review: none

## 9. Limits on this run

- May produce a customer-intelligence brief and evidence-backed hypotheses.
- Must label competitor and community material as market evidence.
- Must not describe the sample as Fieldnote Carry customers.
- Must not recommend final positioning as validated.

## 10. Next actions

1. Expand the competitor set beyond founder-supplied brands.
2. Mine category reviews and communities for situations, failed alternatives, and objections.
3. Recruit five target-user interviews after the first research pass.
4. Verify landed cost before commercial test-budget recommendations.
