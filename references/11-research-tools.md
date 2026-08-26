# Research tools and the intelligence pass

Research begins with the active brand folder, not a blank search box. The goal is to separate what
the brand knows, what the market suggests, what customers have actually said, and what the
strategist is inferring.

The standard describes capabilities. Named tools are current ways to satisfy them. A connector is
available only after a successful preflight call in the current runtime.

## Evidence hierarchy

Use the most direct source that can legitimately support the claim:

1. Verified internal product, offer, policy, economics, and claim records
2. Current active-brand customer evidence: reviews, interviews, support, surveys, returns
3. Active-brand behavioural evidence: purchases, supplied manual ad results, retention, returns
4. Current active-brand website assertions and dated change history
5. Competitor and category evidence: sites, ads, reviews, communities, search language
6. Strategist judgement, clearly labelled and paired with a validation step

Higher in this list does not always mean better quality. It means more direct to the active brand.
Record recency, sample limitations, contradictions, and confidence for every synthesis.

## Required capability map

| Capability | What it answers | Current routes |
|---|---|---|
| Brand-site truth | What does the brand say now, and what changed? | Firecrawl, browser, manual export |
| Customer voice | What words do customers use? | Brand reviews, interviews, support, competitor reviews, communities |
| Competitor creative | What arguments, formats, and offers are visible? | Foreplay, TrendTrack, public ad libraries |
| Demand signal | Which situations and queries appear or change? | Search language, trend tools, communities, retailer demand evidence |
| Own-brand learning | What has this brand already learned? | Brand folder, approved human revisions, supplied manual performance data |

## Website crawl with Firecrawl

Firecrawl is preferred for brand and competitor websites. Follow `connectors/firecrawl.md` and
`references/13-brand-folder.md`.

When the brand folder opens:

1. Read the crawl state.
2. Check the current URL set and change identifiers.
3. Retrieve every changed or new high-priority page.
4. Run a full crawl when the last successful full crawl is seven or more days old.
5. Force a full crawl before major research, concept work, positioning, or launch decisions.
6. Preserve the prior normalized snapshot and create a dated change summary.

Prioritise home, collection, product, offer, FAQ, about, review, shipping, returns, guarantee,
policy, and advertorial pages. Treat site copy as a brand assertion unless another record verifies
the fact. Never let a crawl silently overwrite an approved price, claim, offer, or rule.

If Firecrawl is unavailable, use browser retrieval or manual page exports and state what was not
checked. A fallback crawl is not complete unless its source URLs and dates were captured.

## Foreplay

Use discovered live tool descriptions as authoritative. Current integrations can expose:

| Job | Common capability |
|---|---|
| Find brands | category, keyword, domain, or ad discovery |
| Retrieve ads | domain or page-ID brand lookup and ad retrieval |
| Read saved evidence | swipe files, boards, and lenses |
| Compare patterns | creative velocity, duplicates, analytics, and time series |

Every cited ad keeps the connector's returned URL or identifier. Do not construct a Foreplay URL.
Longevity and repeated variation can suggest commitment, but neither proves profitability.

## TrendTrack

Use discovered live tool descriptions as authoritative. Current integrations can expose ad, shop,
product, advertiser, transcript, email, and tracked-brand research, plus usage or credit checks.

Resolve filter values through the connector rather than guessing identifiers. Transcripts are
useful for structure analysis, but do not treat the longest-running ad as a confirmed winner. Record
the observed dates and the limitations of the signal.

## Customer voice

Preferred first-party sources:

- the active brand's reviews;
- interviews and survey responses;
- support tickets and chat transcripts;
- return reasons and post-purchase feedback;
- approved human edits that reveal customer-language constraints.

For a pre-customer brand, use competitor reviews, public communities, video comments, search
language, and retailer feedback. Label each item as market evidence. It can shape hypotheses but
cannot prove what this brand's customers believe.

Tag exact quotes into:

1. activating situation;
2. problem language;
3. desired outcome;
4. failed alternatives;
5. objections;
6. proof language.

Keep the exact wording, source, date, evidence class, and any usage restriction. Never clean or
merge a quote presented as verbatim.

## Demand and own-brand learning

Demand evidence can include search trends, recurring queries, seasonality, community activity,
retailer signals, and repeated review situations. State the geography, date range, query, and tool.
Do not convert a directional trend into a market-size claim.

Own-brand learning currently comes from the brand folder, approved revisions, and manually supplied
performance exports. A live Meta connection is not required. Do not claim a performance lesson when
the supplied test did not isolate it.

## Intelligence pass, in order

1. **Resolve and preflight.** Confirm brand, market, product, folder version, crawl freshness, and
   connectors.
2. **Read internal truth.** Load product, claims, offers, economics, production limits, destination,
   approved rules, and unresolved conflicts.
3. **Refresh the active website.** Capture changes before treating current positioning as fact.
4. **Read first-party customer and behavioural evidence.** Record what exists and what does not.
5. **Sweep the market.** Competitor sites, ads, reviews, communities, search language, and demand.
6. **Build the evidence ledger.** Class, source, date, finding, confidence, contradiction, permitted use.
7. **Synthesize cautiously.** Sophistication, awareness, personas, outcomes, objections, and language.
8. **Propose opportunities.** Name the reviewed competitor set, supporting evidence, contrary
   evidence, confidence, and validation step.
9. **Publish what remains thin.** Missing evidence and the best next research action.

## Evidence ledger row

| ID | Finding or quote | Source class | Source | Retrieved | Confidence | Contradiction | Permitted use |
|---|---|---|---|---|---|---|---|

Every persona, objection, angle, and proof point must trace to one or more ledger rows. Use
`[UNSOURCED, strategist judgement]` only when the judgement is necessary and include a validation
step. Never quietly present judgement as evidence.

Whenever evidence rows are appended or materially replaced, increment `evidence_version`, update
`entry_count`, `last_evidence_id` and `last_refresh` in
`research/evidence-ledger/manifest.json`. Upload bundles also provide a deterministic SHA-256
evidence version across the included state. If a legacy folder has no version record, label it
unversioned rather than inventing one.
