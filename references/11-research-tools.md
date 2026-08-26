# Research tools and the intelligence pass

Every run starts here. The agent does not write a hook before it knows how the customer
speaks, what the market has already heard, and what is currently working.

The standard describes **capabilities**. The named tools are what satisfies them today. If a
tool is unavailable, name the capability that is missing and say what the output will lack.
Never substitute invention for evidence.

## The four capabilities

| Capability | What it answers | Tools that satisfy it |
|---|---|---|
| Competitor ad intelligence | What is the market already saying, and what is scaling? | Foreplay, Trendtrack, Meta Ad Library |
| Customer voice | How does the customer actually talk about this? | Review scraping, Reddit, YouTube comments, support tickets |
| Demand signal | Is the desire growing, flat or seasonal? | Google Trends, keyword volume |
| Own-account performance | What has this brand already learned? | Meta Ads reporting, the brand's own test archive |

## Foreplay: competitor ads and swipe

| Job | Tool |
|---|---|
| Find brands advertising in a category | `search_discovery_brands`, `discover_brands_by_ads` |
| Pull a specific brand's live ads | `get_brands_by_domain`, then `get_brands_ads_by_page_id` |
| Search the discovery index by attributes | `search_discovery_ads` |
| Track a competitor over time | `get_spyder_brand_ads`, `get_spyder_brands` |
| See what a brand is scaling into | `display_creative_velocity`, `get_brands_analytics` |
| Find duplicate or iterated variants of one ad | `get_group_duplicates_by_ad_id` |
| Read the brand's own saved swipe | `get_boards`, `get_board_ads`, `get_swipefile_ads` |
| Performance lenses on connected accounts | `get_lenses`, `get_lens_insights`, `get_lens_metrics`, `get_lens_timeseries` |

Every ad object returns a `foreplay_url`. Cite it as a markdown link whenever you reference a
specific ad, so the reader can open it in one click. Never construct that URL by hand.

**How to read a competitor set.** Longevity is the strongest available signal. An ad running
for months is more likely to be working than a new one. Creative velocity shows what a brand
is committing to. Neither proves profitability.

## Trendtrack: market, shops and ad libraries

| Job | Tool |
|---|---|
| Search ads across libraries | `search_ads`, `search_google_ads_library`, `search_tiktok_library` |
| Find and profile advertisers | `search_advertisers`, `brief_competitor` |
| Find and compare stores | `search_shops`, `find_similar_shops` |
| Track a brand and see what changed | `add_to_brandtracker`, `analyze_tracked_brand`, `analyze_brand_changes` |
| See what a tracked brand is scaling | `get_brandtracker_scaling_ads` |
| Pull ad transcripts for structure analysis | `get_brandtracker_transcripts` |
| Email and lifecycle intelligence | `search_emails`, `analyze_shop_emails`, `get_email_html` |
| Product-level demand | `find_winning_products` |
| Daily market movement | `daily_radar` |
| Creative inspiration by theme | `creative_inspiration_pack` |
| Deep-read one ad | `scan_ad` |

`lookup` and `lookup_filter_ids` resolve filter values before a search. Use them rather than
guessing filter IDs.

**Transcripts are the highest-value output here.** A transcript lets you reverse-engineer
structure: where the hook lands, when the mechanism appears, how long before the offer. Pull
transcripts for the three longest-running competitor ads before writing any script.

## Customer voice

| Job | Capability |
|---|---|
| Mine competitor store reviews | Review scraping, Trustpilot and Amazon scrapers, on-site review widgets |
| Community language | Reddit search and scraping |
| Video comment language | YouTube comment retrieval, transcripts |
| Search intent | Keyword volume, Google Trends |

**Minimum viable customer voice pass.** Two competitor review sets, one community source, one
search-intent source. Under that, the output says so and marks its persona and objection
sections as thin.

**Tag every extract** into the six-part language bank in `10-voice-and-claims.md`: situation,
problem language, desired outcome, failed alternatives, objections, proof language. Keep the
verbatim. Keep the source link.

## The intelligence pass, in order

1. **Business guardrails.** Read target CAC, AOV, margin and test budget from config. If they
   are missing, ask. Everything downstream is priced against them.
2. **Product truth.** Read the approved claim library. Note the claim ceiling before any angle
   is written.
3. **Competitor sweep.** Pull the ad set for the category. Note distinct promises, named
   mechanisms, dominant formats, and how long the top ads have run.
4. **Sophistication call.** Count distinct promises across the competitor set and state the
   stage, with the evidence that led you there.
5. **Customer voice harvest.** Reviews, community, comments. Tag into the six-part bank.
6. **Awareness call.** From the language harvested, state where the bulk of the market sits.
7. **White space.** Name what nobody in the set is saying that the evidence supports.
8. **Brief the concepts.** Only now does persona, outcome and angle get written.

Skipping steps 3 to 7 and going straight to concepts is the single most common failure. It
produces ads that sound like every other ad in the category, because they were written from
the same place: the model's prior, not the market's evidence.

## Citing evidence

Every persona, objection, angle and proof point in any output traces to a source. Use this
inline form:

```
[claim or quote] source: <link or "competitor review, Brand X, 2026-08">
```

If a line cannot be sourced, either cut it or mark it `[UNSOURCED, strategist judgement]`.
Never quietly present judgement as evidence.
