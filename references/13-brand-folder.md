# Brand folder and readiness

The connected brand folder is the canonical source for every brand fact and retained learning.
The universal skill remains unchanged across brands.

## Resolve the brand

1. Find `brand.yml` in the folder supplied for the task.
2. Read the slug, markets, products and evidence status from `brand.yml`, then read website
   freshness from `sources/website/crawl-state.json`.
3. Confirm the requested market and product. Do not merge market-specific prices, offers or claims.
4. Load approved rules before drafts or raw learning events.
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
and the mapping from ads to concepts. A live Meta connector is not required.

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
rules, approved claims and concept identifiers are controlled records. Update them only through
their approval workflow. Never overwrite a non-empty folder during initialisation.
