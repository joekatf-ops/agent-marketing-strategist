# Brand folder and readiness

The connected brand folder is the canonical source for every brand fact and retained learning.
The universal skill remains unchanged across brands.

## Resolve the brand

1. Find `brand.yml` in the folder supplied for the task.
2. Read the slug, method version, controlled naming codes, next test number, markets, products and
   evidence status from `brand.yml`, then read website freshness from
   `sources/website/crawl-state.json`.
3. Confirm the requested market and product. Do not merge market-specific prices, offers or claims.
4. Load the coordinate, test and winner registers plus approved rules before drafts or raw learning
   events.
5. State the versions used in the run header.

If several folders are available and the user did not name the brand, ask. The last brand used is
not a safe default.

## Source classes

| Class | Meaning | Examples |
|---|---|---|
| Verified brand fact | An internal fact with an owner or source | price, ingredient, guarantee |
| Brand assertion | What the brand currently says | website promise, founder belief |
| Brand-customer evidence | Evidence from this brand's customers | review, interview, support ticket |
| Market evidence | Evidence from category or competitor customers | competitor review, Reddit thread |
| Behavioural evidence | An observed action | purchase, return, supplied ad result |
| Strategist judgement | A reasoned inference | white-space hypothesis |

Never collapse these classes. A competitor review does not prove how this brand's customer thinks.
A website claim does not prove a product result.

## Mode-specific readiness

### Research

Minimum: brand identity, product truth, market, website, competitor seeds or discoverable category.
Economics may be missing, but commercial recommendations must then be marked provisional.

### Concepts

Requires current customer intelligence, approved product truth, claim ceiling, available
destinations and production constraints.

### Hooks, copy and production

Requires an approved concept, voice rules, exact offer, approved proof, claim wording, destination
and the formats the brand can actually produce.

### Manual diagnosis

Requires supplied dates, spend, purchases, attribution basis, account or sourced comparison ranges
and the mapping from ads to CONTST batches and coordinates. A live Meta connector is not required.

## Strategy memory

`brand.yml` declares the reviewed method version. Its `naming.test_prefix` is always `CONTST`, and
`naming.next_test_number` is reserved once for every new NNT, INSPO or ITR batch. The prefix is not
brand-configurable and numbers are not reused. `brand_code`, `product_codes` and `region_codes` are
controlled values used in the locked campaign names. Testing defaults record ABO, the $50 daily
ad-set floor, approximately $100 preferred daily budget and five-full-day planned window; actual
plans still use the active product and market economics.

The three strategy records have different lifecycles:

| Record | Identity | Retained history |
|---|---|---|
| Concept register | enduring `Who x Primary Problem` coordinate key | evidence, status and all linked CONTST batches |
| Test register | one sequential NNT, INSPO or ITR batch | launch plan, executions, results, cautious explanation and next action |
| Winner library | one graduated published ad | real Post ID, test result, separate scale history, status and linked ITR batches |

An initial NNT or INSPO record has four ads: UWA, PRA, SLA and PDA. An ITR record may be narrower
when prior evidence supports that scope, but it always receives the next CONTST identifier. Preserve
stopped, rejected, retired and archived records. Never delete or recycle history to make a register
look cleaner.

Every register carries the active `brand_slug`. A mismatch is a stop condition, not an invitation to
merge records. Coordinate evidence, test observations, winners and learning from one brand never
become facts or defaults for another brand automatically.

## Website freshness

Run a change check whenever the folder opens. If a crawler exposes a sitemap, change token or page
metadata, use that for the lightweight check. Otherwise compare the current URL set and page
fingerprints with the last snapshot.

- Crawl changed and new pages immediately.
- Full crawl after seven days.
- Forced crawl before major research, concept batches and launches.
- Prioritise homepage, PDPs, collections, about, FAQ, reviews, shipping, returns, guarantee and
  relevant editorial pages.
- Record URL, fetched time, source connector and content hash.
- Log added, removed and changed pages.

Changes to price, offer, product, guarantee, claim, review count or positioning are material. Flag
them before production. A changed page never silently overwrites an approved rule or claim.

## New brands

Set `customer_evidence.status` to `pre-customer`. Use product truth and founder hypotheses as the
starting brief, then research competitor sites, competitor reviews, public communities and search
language. Label the result as market evidence and lower confidence where first-party validation is
missing.

## Folder writes

Drafts, snapshots, evidence and learning events may be written when `run.writable` is true. Approved
rules, approved claims, coordinate keys, CONTST identifiers and real winner Post IDs are controlled
records. Update them only through their governing workflow. Never overwrite a non-empty folder
during initialisation.
