# Meta platform layer: specs, policy, benchmarks, hooks, structures

Researched 26 August 2026. This file is the platform-and-numbers layer only. The theory
(awareness, sophistication, persuasion, offer, copy structures) lives in files 01 to 11 and is
not repeated here.

Everything below carries a source. Anything unsourced is tagged. Platform specs and policy
change without notice: re-verify anything load-bearing before a launch, and treat the dates in
this file as the last time it was checked.

## 1. Meta ad specs and truncation

### 1.1 The three-layer rule for copy fields

There are three different numbers for every text field and practitioners conflate them constantly:

| Layer | What it is | Behaviour |
|---|---|---|
| **Meta "recommended" count** | The number printed in Meta's Ads Guide per placement | Advisory only |
| **Ads Manager cap** | What the field will physically accept | Much larger; exceeding recommendation triggers a yellow informational warning, never a rejection |
| **Render/truncation point** | Where the UI actually cuts and appends "See more" | Layout-driven, not a fixed character count |

Meta does not publish the truncation threshold as a number. It is computed at render time from viewport width, line height, system font-size setting, language, emoji and manual line breaks ([AdPlus](https://adplus.com/tools/ad-specs-validator/facebook-125-character-primary-text); [SocialRails, updated 23 July 2026, verified against Meta's Ads Guide](https://socialrails.com/blog/facebook-ad-character-limits)). Solid's spec audit (verified 8 August 2026) states flatly that **character limits are "not published by Meta"** as hard values ([Solid](https://www.solidlabs.com/ad-specs/meta)).

**Operating rule: write to the recommended count as if it were a hard cut, because it approximates the mobile render.**

### 1.2 Recommended character counts by placement

Cross-checked across Sprout Social (updated 22 Aug 2025, cites Meta's Ads Guide), Strike Social (updated 20 May 2026), SocialRails (July 2026) and AdsUploader (5 Apr 2026). Where sources disagree the range is shown.

| Placement | Primary text | Headline | Description |
|---|---|---|---|
| Facebook Feed (image) | 50 to 150 (commonly cited 125; Strike lists 80) | 27 | 27 |
| Facebook Feed (video) | 80 to 125 | 25 to 27 | 25 to 27 |
| Instagram Feed | 125 | 40 | does not render |
| Instagram Reels | 72 (some campaign objectives 44) | 40 | does not render |
| Facebook Reels | 40 | 55 | does not render |
| Ads **on** Facebook Reels (banner overlay) | 60 | 10 | does not render |
| Facebook Stories | 125 | 40 | does not render |
| Instagram Stories | 125 | 40 | does not render |
| Instagram Explore | 125 | 40 | does not render |
| Facebook Marketplace | 125 | 40 | 30 |
| Facebook Search Results | 125 | 40 | 30 |
| Facebook In-Stream Video | 125 | 40 | 30 |
| Audience Network | 125 | 40 | 30 |
| Facebook Right Column | not shown | 40 | not shown |
| Carousel, Facebook Feed | 80 | 45 per card | 18 per card |

Sources: [Sprout Social Facebook](https://sproutsocial.com/insights/facebook-ad-sizes/), [Sprout Social Instagram](https://sproutsocial.com/insights/instagram-ad-sizes/), [Strike Social](https://strikesocial.com/blog/meta-ad-specs/), [SocialRails](https://socialrails.com/blog/facebook-ad-character-limits), [AdsUploader](https://adsuploader.com/blog/meta-ad-copy-specs).

### 1.3 Where "See more" cuts

| Surface | Practical cut | Source |
|---|---|---|
| Mobile feed (FB and IG) | ~125 characters | [AdPlus](https://adplus.com/tools/ad-specs-validator/facebook-125-character-primary-text), [AdsUploader](https://adsuploader.com/blog/meta-ad-copy-specs) |
| Desktop feed | ~200 characters | [AdPlus](https://adplus.com/tools/ad-specs-validator/facebook-125-character-primary-text) |
| Small phone (iPhone SE class) | ~110 characters | [AdPlus](https://adplus.com/tools/ad-specs-validator/facebook-125-character-primary-text) |
| Large phone (Pro Max class) | ~135 characters | same |
| Accessibility text scaling on | as few as ~80 characters | same |

- **A manual line break forces truncation early.** Any hard return in the primary text collapses the block at that point on mobile. Treat line breaks in the first 125 characters as a deliberate choice to lose everything after them.
- Roughly **1% of users expand "See more"** ([AdsUploader, 5 Apr 2026](https://adsuploader.com/blog/meta-ad-copy-specs)). `[Unverified against Meta; single source.]`
- Rule: the offer, the mechanism and the identity call must all live in the first ~80 characters to survive the worst case.

### 1.4 Description field: where it renders

Description is **absent** from Meta's Ads Guide pages for Stories, Reels, Explore and Instagram Feed. It reliably renders in exactly four places: **Marketplace, Audience Network, Facebook Search Results, In-Stream Video** ([AdsUploader, 5 Apr 2026](https://adsuploader.com/blog/meta-ad-copy-specs)). Sprout's placement tables corroborate: description only appears in the Marketplace and Audience Network rows ([Sprout](https://sproutsocial.com/insights/facebook-ad-sizes/)).

**Rule: never carry load-bearing information in the description. On a DTC Advantage+ campaign that runs everywhere, it is invisible on the majority of impressions.**

### 1.5 Aspect ratios and resolutions

| Placement | Ratio | Recommended resolution |
|---|---|---|
| Facebook Feed image | 1:1 or 4:5 | 1440x1440 / 1440x1800 |
| Facebook Feed video | 4:5 | 1440x1800 |
| Instagram Feed image | 1:1 (range 4:5 to 1.91:1) | 1440x1440 |
| Instagram Feed video | 4:5 | 1440x1800 |
| Instagram Reels / Facebook Reels | 9:16 | 1440x2560 |
| Instagram Stories / Facebook Stories | 9:16 | 1440x2560 |
| Ads on Facebook Reels (overlay) | 1.91:1 to 1:1 | 1080x1080 |
| In-Stream Video | 16:9 or 1:1 | 1080x1080 |

Minimum width 250px, rising to 500px for Reels ads over 30 seconds. Facebook Feed absolute minimum 120x120. Meta allows a **1% aspect ratio tolerance**. Video files MP4, MOV, GIF; Reels accepts MP4 and MOV only. Max 4GB video, 30MB image. ([Solid, verified 8 Aug 2026](https://www.solidlabs.com/ad-specs/meta); [Sprout](https://sproutsocial.com/insights/facebook-ad-sizes/))

### 1.6 Safe zones

The 9:16 safe zone converged in 2026. Multiple independent sources now report the same figure for Reels **and** Stories:

**9:16 safe zone: top 14%, bottom 35%, sides 6% each.**

At 1080x1920 that is **270px top, 672px bottom, 65px each side**, leaving a usable band of roughly **950 x 980px**. At 1440x2560 it is roughly **358px top, 896px bottom, 87px sides**.

| Source | Reels | Stories | Date |
|---|---|---|---|
| [Solid](https://www.solidlabs.com/ad-specs/meta) | 14 / 35 / 6 | 14 / 35 / 6 | verified 8 Aug 2026 |
| [AdNabu](https://blog.adnabu.com/meta-ads/meta-safe-zones/) | 14 / 35 / 6 | 14 / 20 to 35 / 6 | 14 Aug 2026 |
| [Billo](https://billo.app/blog/meta-ads-safe-zones/) | 14 / 20 to 35 / 6 | 14 / 20 to 35 / 6 | 16 Jun 2026 |
| [Strike Social](https://strikesocial.com/blog/meta-ad-specs/) | 14 / 35 / 6 | 14 / 20 | 20 May 2026 |
| [Sprout Social](https://sproutsocial.com/insights/instagram-ad-sizes/) | 14 / 20 | 14 / 20 | 22 Aug 2025 |
| [Hootsuite](https://blog.hootsuite.com/facebook-ad-sizes/) | keep critical content in centre 1080x1420 | same | 16 Jul 2026 |

**Where the disagreement is:** the older figure (14 / 20, that is 250px top and 340px bottom at 1080x1920) is Meta's long-standing **Stories** guidance and is what Sprout still prints. The 35% bottom is the **Reels** figure, driven by caption block, audio label, follow button, CTA button and the profile row. The 2026 sources say Meta unified both to 14 / 35 / 6 in **March 2026**.

**Verdict: design to 14 / 35 / 6 for all 9:16. It is the more recent reading, it is the strictest, and it is safe under the older spec too.**

`[FLAG] The "March 2026 unified safe zone update" is asserted by AdNabu, Billo and Mintec but I could not verify it against a Meta announcement or changelog. facebook.com/business is blocked to automated fetching (robots.txt), so all spec figures in section 1 are second-hand readings of Meta's Ads Guide, not direct quotes from it.`

**What occupies each zone** ([AdNabu](https://blog.adnabu.com/meta-ads/meta-safe-zones/)):
- Top 14%: profile picture, account name, "Ad" label
- Bottom 35%: caption, audio label, follow button, CTA button
- Sides 6%: like, comment, share, save icon rail (right edge)

**Feed placements have no UI overlay.** Practitioner padding convention for 4:5 (1080x1350) is ~250px top and bottom and ~100px sides; for 1:1, ~100px all round ([AdNabu](https://blog.adnabu.com/meta-ads/meta-safe-zones/)). `[PRACTITIONER CONVENTION, not a Meta spec]`

### 1.7 Video length by placement

Compiled by Jon Loomer directly from Meta's Ads Guide, 11 August 2025 ([source](https://www.jonloomer.com/meta-video-ad-length-requirements/)):

| Placement | Min | Max |
|---|---|---|
| Facebook Feed / Groups / Marketplace / Search / Right Column / Video Feeds / Business Explore | 1 sec | 241 min |
| Facebook Stories | 1 sec | 2 min (split into cards) |
| Facebook Reels | none | no limit |
| **Facebook In-Stream Video** | **5 sec** | **15 sec** |
| Ads **on** Facebook Reels (overlay) | 4 sec | 15 sec |
| Instagram Feed / Explore / Profile Feed | 1 sec | 60 min |
| Instagram Stories | 1 sec | 60 min (split into cards) |
| Instagram Reels / Profile Reels | 0 sec | 15 min |
| Messenger Stories | 1 sec | 2 min |
| Audience Network Native/Banner/Interstitial | 1 sec | 2 min |
| Audience Network Rewarded Video | 3 sec | 61 sec |

**The binding constraint is In-Stream Video: 5 to 15 seconds.** A video must sit in that window to be eligible for every single placement in Meta's guide. Loomer's recommendation: cut to **close to 15 seconds** if you want one asset to run everywhere without building variants.

Sprout reports Facebook Feed video max as 240 min and Strike as 241 min; treat as the same number with rounding noise.

---

## 2. Meta advertising policy as it bites on DTC

All Meta policy text below is quoted from transparency.meta.com, fetched 26 August 2026.

### 2.1 Health and Wellness policy (the one that governs supplements, weight loss, beauty)

Source: [transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/)

Stated rationale: Meta aims to foster "a body positive and inclusive environment" where people are not pressured to conform to appearance standards.

**Prohibited outright:**
- "side-by-side comparison after the use of a product or transformation for weight loss"
- "Close up on specific body area by pinching fat"
- "side-by-side comparison after the use of a product or transformation for wrinkles treatment"
- Messaging that could "make people feel negatively about the way they look" or that features "body-shaming"
- Skin whitening or bleaching products that cause permanent colour change

**Allowed but 18+ only:**
- Weight loss products showing "people using the product or the service, and its impact," with results timelines "clearly indicate[d]" and without "negative self-perception tactics"
- Cosmetic procedures: breast augmentation, rhinoplasty, dermal fillers, chemical peels, hair restoration
- "General cosmetic products, procedures, surgeries depicting before and after transformation, without employing negative self-perception tactics"
- Anti-aging: "zoomed-in or close-up images" are permitted, results "must reflect realistic outcomes over time," and **no side-by-side comparisons**

**No age restriction:**
- Fitness services and health clubs (fitness classes are the explicit carve-out from the side-by-side ban)
- General food products, makeup, hair products, teeth whitening

**The operative distinction: a general cosmetic before/after is allowed at 18+. A weight loss before/after and a wrinkle before/after are prohibited. An anti-aging close-up over time is allowed; the same content presented as two panels side by side is not.**

### 2.2 Age gating

Source: [Cosmetic Procedures and Wellness](https://transparency.meta.com/policies/ad-standards/content-specific-restrictions/cosmetic-procedures-and-wellness)

Verbatim:
- "Ads marketing weight loss products and services must be targeted to people at least 18 years or older."
- "Ads marketing cosmetic surgeries and procedures must be targeted to people at least 18 years or older."
- "Ads marketing dietary, health or herbal supplements must be targeted to people at least 18 years or older."

`[FLAG, sources disagree] Clikim reports a Meta health and wellness policy change effective 22 July 2026: that side-by-side imagery "is no longer automatically rejected" and is "prohibited only when paired with violative claims," and that supplements, vitamins and protein no longer default to 18+ (only weight loss/gain supplements retain it), with enforcement moving from "product-based to claims-based" (https://clikim.com/meta-health-wellness-policy-update/). Meta's own live policy pages, fetched 26 Aug 2026, still state the side-by-side prohibition and still state the blanket supplements 18+ requirement. Meta's own page is the more authoritative and equally current read. Treat the Clikim account as an enforcement-behaviour observation, not a policy text change. Do not build creative that depends on it.`

### 2.3 Personal attributes: the "you" rule

Source: [Privacy Violations and Personal Attributes](https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes)

The restricted attributes: race, ethnicity, religion, beliefs, age, sexual orientation, gender identity, disability, **physical or mental health**, financial status, voting status, union membership, criminal record, name.

Meta's stated principle: "Ads that make assumptions about people could be perceived as intrusive, unsettling or inaccurate."

**What counts as implying an attribute:** any second-person construction that asserts the reader *has* the condition. Not the word "you" itself, but "you" plus a diagnosis, state or identity.

**Verbatim prohibited examples:**

| Prohibited |
|---|
| "Bulimia counseling available" |
| "Depression counseling" |
| "New diabetes treatment available" |
| "Do you have diabetes?" |
| "Depression getting you down? Get help now." |
| "Don't wait!! Get your spouse treated for cancer today with help from our medical experts." |
| **"Ready to upgrade your skin to look younger?"** |
| "We have financial services to cover every financial need." |
| "Are you bankrupt? Check out our services." |
| "Are you 18 years old?" |
| "Meet seniors" |
| "A service for teens" |

**Verbatim allowed examples:**

| Allowed |
|---|
| **"Our new lotion and creams fight wrinkles like never before!"** |
| "Age is just a number. Anyone can now learn coding with our C program." |
| "Join us this summer at Nature Camp. Open to all teenagers." |
| "Meet other seniors" |
| "We print customizable t-shirts and stickers with your name." |
| "Learn about voter registration" |

**The rule extracted from the contrast pair:** "Ready to upgrade **your** skin to look younger?" is rejected. "**Our** new lotion and creams fight wrinkles like never before!" is accepted. The difference is subject position. **Move the sentence subject onto the product and off the reader's body.** "Meet seniors" is rejected but "Meet other seniors" is accepted, because "other" makes it self-selecting rather than an assertion about the reader.

Enforcement extends beyond ad copy: Meta has been disabling custom audience names and custom conversion event names that imply a sensitive health attribute, for example an audience called `arthritis_interest_list` ([Accelerated Digital Media, 18 Feb 2026](https://www.accelerateddigitalmedia.com/insights/guide-to-social-media-health-ad-restrictions-2026/)).

### 2.4 Claims: what gets rejected as deceptive

Source: [Unacceptable Business Practices](https://transparency.meta.com/policies/ad-standards/fraud-scams/unacceptable-business-practices/)

Prohibited verbatim:
- "Use deceptive or exaggerated claims about the success of a product or service to mislead people into purchasing or sharing sensitive information"
- "Use deceptive or exaggerated claims about **health-related benefits** of a product or service to mislead people into purchasing or sharing sensitive information"
- "Use the image of a famous person and misleading tactics in order to bait people into engaging with an ad"
- "Promise financial benefits by misrepresenting an entity, industry association or news outlet"

Meta names "health or weight loss schemes" and "misleading free product promotions" as frequent violation areas.

### 2.5 "Unrealistic outcomes" in practice

Two operative tests in the Health and Wellness policy:

1. **Timeline disclosure.** Results shown must have a timeline "clearly indicate[d]." An undated transformation is an unrealistic outcome by default.
2. **Realistic outcomes over time.** Anti-aging visual results "must reflect realistic outcomes over time."

What triggers rejection in practice:
- A result with no time anchor ("look 10 years younger")
- A speed claim that outruns physiology ("lose 20lbs in 2 weeks")
- Absolute or curative language on a supplement or cosmetic ("cure," "treat," "prevent," "eliminates," "guaranteed")
- Two panels with an implied causal arrow, for weight or wrinkles

Category-level term risk for supplements and weight loss: "diet," "fat-burning," "slimming" are flagged as high-probability algorithmic rejection triggers ([Meaningful Agency, 2026](https://www.meaningfulagency.com.au/blog/meta-ads-for-health-wellness-beauty-brands-2026-guide)) `[single practitioner source, unverified against Meta]`. The safer register per the same source: energy, strength, nourishment, vitality, ingredient transparency, formulation science.

### 2.6 Special Ad Categories

**There are four, and none of them is health, wellness, supplements, beauty or personal care.**

1. Financial Products and Services
2. Employment
3. Housing
4. Social Issues, Elections or Politics

Restrictions on the first three: age locked to 18 to 65+ with no narrowing; gender locked to all; detailed targeting partly unavailable and **exclusions prohibited**; location must cover a 15-mile radius minimum with no postal code targeting; lookalike and saved audiences unavailable; lead forms cannot collect age, gender, relationship status or location.

Source: [Jon Loomer, updated 1 March 2025](https://www.jonloomer.com/special-ad-categories-meta-ads/).

**Consequence for DTC health and beauty: full targeting and lookalike tooling remains available. The constraint is content and age gating (18+), not audience restriction.** Do not let a compliance conversation drift into assuming SAC applies.

Adjacent requirement: online pharmacy advertisers require LegitScript certification.

`[COULD NOT VERIFY] The Unsafe Substances policy page returned HTTP 429 on repeated attempts. Its prohibited-ingredient list is not captured here.`

---

## 3. Creative metric benchmarks and thresholds

### 3.1 Formulas first

| Metric | Formula | Source |
|---|---|---|
| Hook rate / thumbstop rate | 3-second video plays / impressions | [Motion](https://motionapp.com/blog/key-creative-performance-metrics) |
| Hold rate | 15-second plays / **3-second plays** | [Motion](https://motionapp.com/blog/key-creative-performance-metrics), [AdSights](https://www.adsights.ai/resources/glossary/metrics/hold-rate) |
| ThruPlay rate | 15-second plays / **impressions** | [AdSights](https://www.adsights.ai/resources/comparisons/hold-rate-vs-thruplay-rate) |
| 1st frame retention | % of impressions where the video is allowed to start playing | [Motion cheat sheet](https://help.motionapp.com/en/articles/7730931-metrics-cheat-sheet) |
| Thumbstop CTR | % who watched 3s **and** clicked to site | Motion cheat sheet |
| Click-to-purchase | purchases / link clicks | Motion cheat sheet |

**Hold rate and ThruPlay rate differ only in denominator and produce wildly different numbers. Always check which one a benchmark is quoting.** A 3-second view also counts if the video is shorter than 3 seconds and reaches 97% completion, which is why sub-15s videos post mechanically inflated hold rates.

### 3.2 Hook rate (3-second view rate)

**Motion, generic bands** ([source](https://motionapp.com/blog/key-creative-performance-metrics)): broken below 25%, workable 25 to 35%, strong above 35%.

**AdSights, segmented, updated 25 July 2026** ([source](https://www.adsights.ai/resources/glossary/metrics/thumbstop-rate-tsr)):

| Segment | Range | Median |
|---|---|---|
| In-feed video, DTC prospecting | 18 to 28% | ~23% |
| **Reels, DTC prospecting** | **24 to 36%** | **~30%** |
| Stories, DTC | 22 to 32% | ~27% |
| Retargeting (warm) | 30 to 45% | ~36% |
| Cold prospecting, all placements | 18 to 28% | ~22% |
| Beauty / skincare | 25 to 35% | ~28% |
| Apparel | 20 to 30% | ~24% |
| Supplements | 22 to 32% | ~26% |

**Judge a Reels prospecting ad against ~30%, not against 25%.** A warm-audience 36% is a brand-recognition signal and says nothing about creative quality.

Motion adds a rarely-used upstream metric: **1st frame retention, target above 90%.** If that is failing, the file, thumbnail or first frame is the problem, not the hook writing.

### 3.3 Hold rate (15s / 3s)

AdSights, updated 23 July 2026 ([source](https://www.adsights.ai/resources/glossary/metrics/hold-rate)):

| Segment | Range | Median |
|---|---|---|
| Feed, DTC prospecting, 15 to 30s | 12 to 25% | ~18% |
| Reels, any length | 18 to 30% | ~23% |
| Longer video 30 to 60s, prospecting | 8 to 18% | ~12% |
| Retargeting (warm) | 25 to 40% | ~30% |
| DTC beauty / UGC, 15 to 30s | 18 to 28% | ~22% |
| Video under 15s | 50 to 80% | ~65% (mechanically inflated) |

Motion's generic bands are far more optimistic (under 30% needs work, 40 to 50% average, above 60% strong). **These are not reconcilable.** Motion's bands are plausible only for short videos, retargeting, or a mixed book including sub-15s assets. Use AdSights' segmented figures for cold DTC prospecting at 15 to 30 seconds.

### 3.4 Cost and conversion: Triple Whale, 40,000+ brands, Aug 2025 to Jul 2026

Median values, Meta, with year-on-year change ([source](https://www.triplewhale.com/blog/facebook-ads-benchmarks)). Highest-credibility dataset here: named sample, named window.

**Platform-wide:** CPA $38.99 (+3.14%), CPM $15.06 (+13.24%), CVR 1.53% (-4.73%), CTR 2.39% (+15.97%), ROAS 1.88, AOV $73.36, MER 0.48.

| Vertical | CPA | CPM | CVR | CTR | ROAS | AOV | MER |
|---|---|---|---|---|---|---|---|
| Apparel & Accessories | $36.98 | $13.25 | 1.47% | 2.44% | 2.24 | $86.27 | 0.42 |
| Beauty | $39.31 | $18.80 | 1.79% | 2.46% | 1.54 | $61.23 | 0.60 |
| Food & Beverage | $38.57 | $15.32 | 1.89% | 1.98% | 1.61 | $64.32 | 0.56 |
| **Health & Wellness** | **$40.53** | **$21.80** | **1.50%** | **3.02%** | **1.44** | **$61.08** | **0.62** |
| Home & Garden | $47.93 | $14.67 | 1.24% | 2.38% | 2.25 | $110.41 | 0.38 |

**Read for Health and Wellness: the highest CPM and the highest CTR in the whole set, with the lowest ROAS. The category buys attention expensively and converts it poorly. CTR is not the constraint; CPM and post-click are.** Health and Wellness CVR fell 13.99% year on year, the steepest decline of any vertical.

Flighted (5 May 2026) puts ecommerce CPC at **$0.34 to $0.68** and Reels CPM $8 to $14 versus IG Feed $14 to $20 ([source](https://www.flighted.co/blog/meta-ads-performance-benchmarks-by-industry)). `[Lower credibility, no sample size. Their ROAS-by-vertical figures of 2x to 4x contradict Triple Whale's measured 1.44 to 2.25 and should be discarded.]`

### 3.5 Mid-funnel rates

| Metric | Benchmark | Source |
|---|---|---|
| Add-to-cart rate, **prospecting** | 7.2% | [Lebesgue](https://lebesgue.io/facebook-ads/add-to-cart-rate-benchmarks-a-closer-look-at-facebook-ads) |
| Add-to-cart rate, **retargeting** | 17.5% | same |
| Purchase CVR (median) | 1.53% platform, 1.50% Health and Wellness | [Triple Whale](https://www.triplewhale.com/blog/facebook-ads-benchmarks) |

`[GAP] No credible landing page view rate benchmark could be sourced. The commonly repeated 80 to 90% figure has no defensible source. Treat LPV rate as a diagnostic for site speed and tracking loss, read within your own account.`

### 3.6 Frequency

From [AdAmigo, 2026](https://www.adamigo.ai/blog/meta-ads-frequency-benchmarks-when-ads-start-fatiguing):

| Audience | Healthy | Warning | Broken |
|---|---|---|---|
| Prospecting (cold) | under 2.5 | 2.0 to 3.5 | 3.5 to 5.0+ |
| Retargeting (warm) | 4.0 to 6.0 | 6.0 | 6.0 to 10.0+ |

`[LOW CONFIDENCE. Methodology described only as "industry research synthesis". The directional shape matches practitioner consensus, so use the shape, not the decimals.]`

Better sourced: **time-to-fatigue of 21 to 35 days**, with the fatigue signal being **declining hook rate week over week while CPM is flat or rising** ([AdLibrary, 15 Mar 2026](https://adlibrary.com/posts/dtc-ad-intelligence-creative-frameworks-2026)). The diagnostic rule is more valuable than the day count.

### 3.7 What is actually a winner: Motion Creative Benchmarks 2026

**The strongest dataset in this document.** $1.29bn in Meta spend, 578,750 unique creatives, 6,015 accounts, Sep 2025 to Jan 2026 ([report](https://motionapp.com/library/research/creative-benchmarks-2026/)).

**Winner definition: an ad that spends at least 10x the account's median ad spend and at least $500.** That sits at the **92.3rd percentile**.

| Finding | Number |
|---|---|
| Share of creatives that are winners | ~5% overall; 3.8% micro accounts, ~8.2% enterprise |
| Mid-range creatives | 38 to 46% |
| Losers (turned off before 28 days) | ~50 to 53% |
| Share of total spend going to winners | **55%** overall |
| Expected hit rate | **1 in 10 to 13 creatives** |
| Creatives launched per week, mid-tier | 6 to 7 |
| Creatives launched per week, top accounts | 12 to 19+ |

**Implication for volume planning: if the base rate is 1 winner in 10 to 13, a brand needing 2 fresh winners a month must ship 20 to 26 creatives a month. Anything less is not a testing programme, it is hoping.**

### 3.8 Minimum spend before calling a test

From [Flighted, 1 July 2026](https://www.flighted.co/blog/how-to-calculate-your-meta-ads-creative-testing-budget):

**External benchmark observation only.** This section describes published practitioner frameworks;
it does not set the strategist's launch structure, duration or validity policy. The governed
protocol in `references/09-testing-and-diagnosis.md` always takes precedence.

**Formula: daily test budget = target conversions x expected CPA / test duration.**

| Signal | Decision |
|---|---|
| 3+ conversions at 3x CPA spend | Keep |
| 2 conversions | Yellow light: run ~1 more CPA of spend, then decide |
| 0 to 1 conversions | Cut |

- **3x target CPA: bare minimum before any decision**
- **5x target CPA: preferred, removes the yellow-light zone**
- **Below 10x CPA total per concept: almost certainly underfunding the test**

Flighted reports a seven-day default, three to four days for impulse products and 10 to 14 days for
long-consideration products. Those are observations about Flighted's framework, not defaults for
this strategist. The governed review point remains five full days, followed by the separate spend,
purchase and integrity validity checks in `references/09-testing-and-diagnosis.md`.

**The stated reasoning:** at 3x CPA the expected count is 3 purchases. Under a Poisson process an expected count of 3 has wide dispersion, so 0 or 1 observed is genuinely informative while 2 is not distinguishable from noise. Moving to 5x raises the expected count to 5, enough to separate outcomes cleanly. Nobody is claiming p<0.05 at these volumes; it is a decision rule under small counts, not a significance test.

**Learning phase:** Meta's documentation still specifies **50 optimised events in 7 days**. A temporary 10-events-in-3-days test ran for several months and reverted with no announcement ([Jon Loomer](https://www.jonloomer.com/qvt/learning-phase-10-or-50-events/)). Treat 50/7 as current.

**External volume-first observation** ([Caleb Kruse, Motion, Jan 2026](https://motionapp.com/library/talk/the-new-meta-ads-testing-strategy-10-ads-vs-100-ads/)): Kruse describes 50 to 100 ads per month as **10 concepts x 5 to 10 hook variations** on a four-week cadence, then doubling down on concepts converting about 2x better before exploring new directions. This is a report of that practitioner's framework, not the strategist's standard batch or hook count.

**These two external frameworks are in genuine tension.** Flighted funds each concept to a decision
threshold; Kruse uses volume and auction allocation. Do not turn the unsourced account-spend
synthesis into an operating policy. The governed method remains one CONTST batch per ad set,
exactly four ads for each initial NNT or INSPO batch, and the validity protocol in
`references/09-testing-and-diagnosis.md` at every spend level.

---

## 4. Hook mechanics on Meta specifically

### 4.1 The evidence base

Motion's Creative Benchmarks 2026 is the only large-sample published dataset that scores hook and format types against a spend-based outcome. **Hit rate = % of creatives of that type that spent 10x the account median.** Sample: 550,000+ ads, 6,000+ advertisers, ~$1.3bn ([source](https://motionapp.com/thumbstop-pulse/creative-benchmarks-2026)).

**Baseline: ~5% of all creatives are winners.** Above ~7% is materially outperforming; at or below ~5% is at or below chance.

### 4.2 Hook type, ranked by hit rate

| Hook type | Hit rate | Read |
|---|---|---|
| **Offer only** | **9.29%** | Best-performing hook type in the dataset. Lead with the deal, not the story |
| **Confession** | **8.74%** | "I was embarrassed to admit..." Second best |
| **Curiosity** | **7.77%** | Open loop |
| **Bold claim** | **7.19%** | Works, but carries the most policy risk in health and beauty |
| Storytelling | 6.23% | Below the confession variant of itself |
| Question | 5.47% | At baseline |
| How to | 5.47% | At baseline |
| Listicle | 5.45% | At baseline |
| Explainer | 5.24% | At baseline |

**The two things this data actually says:**
1. **Offer-first beats story-first by ~50% relative.** The instinct to warm up before the pitch is not supported at the hook layer.
2. **Confession beats storytelling by 40% relative.** The difference is the admission of a flaw. Generic narrative is baseline; self-incriminating narrative is top quartile.

### 4.3 Visual style, ranked by hit rate

| Visual style | Hit rate |
|---|---|
| **Letter** (a written note on screen) | **10.83%** |
| **Unconventional text placement** | **9.63%** |
| **ASMR** | **8.58%** |
| **Founder** (founder on camera) | **8.57%** |
| Sign (held placard) | 7.86% |
| UGC overlay | 6.73% |
| Us vs them | 6.52% |
| Feature benefit pointout | 5.61% |
| Listicle | 5.30% |
| **Green screen** | **4.87%** |

**Green screen is the worst-performing visual style in the dataset, below the 5% baseline.** It is still being briefed heavily. Letter format is the best and is under-used.

### 4.4 Asset type, ranked by hit rate

| Asset type | Hit rate |
|---|---|
| **Text only** | **11.6%** |
| **Product image with text** | **8.75%** |
| **UGC** | **7.56%** |
| High production | 6.97% |
| GIF | 6.82% |
| UGC mashup | 6.28% |
| Lifestyle-product image with text | 6.18% |
| Lifestyle image with text | 6.10% |
| Hybrid | 5.74% |
| **Animation** | **4.57%** |

**Text-only statics are the highest hit rate asset type in a 550,000-ad sample, at more than 2x baseline.** They beat high-production video by 66% relative.

`[FLAG on interpretation] Hit rate is a spend-concentration measure, not an efficiency measure. Text-only statics are cheap to produce, so accounts ship many and the winners scale. The number says "this format produces winners at a high rate," not "this format has the best ROAS." Motion's report explicitly does not measure ROAS, revenue, CVR, CTR, CPM, CPC or CPA.`

### 4.5 Sound-off and captions

- The canonical "**85% of Facebook video is watched without sound**" figure is from [Digiday, 17 May 2016](https://digiday.com/media/silent-world-facebook-video/), sourced from publisher self-reports. **It is ten years old, publisher-reported not Meta-reported, and predates Reels entirely.** Do not present it as a current Meta statistic.
- **Reels is a sound-on-first surface.** Feed autoplays muted; Reels does not behave the same way. `[No citable current Meta figure for Reels sound-on rate. Open gap.]`
- **Design rule that survives regardless:** the hook must be legible with the sound off and must not be redundant with the sound on. Captions carry the message in Feed; audio carries it in Reels. Build for both, never let one duplicate the other verbatim.

### 4.6 On-screen text in the opening

From [RocketShip HQ, 8 June 2026](https://www.rocketshiphq.com/text-overlays-video-ads-mobile/):

| Parameter | Value |
|---|---|
| **Hook text must land within** | **0.5 seconds** |
| Words per overlay card | 5 to 8, max 2 lines visible at once |
| Minimum on-screen duration per line | 1.5 seconds |
| Reading-speed rule | ~250 wpm, so a 10-word overlay needs 2.5s minimum |
| Total overlay words, 15s ad | 40 to 60 |
| Total overlay words, 30s ad | 80 to 100 |
| Text appears relative to voiceover | 0.1 to 0.3s **before** the matching line |
| Minimum readable font at 1080x1920 | 36px |
| Primary text | 48 to 72px Bold |
| Secondary text | 32 to 40px Semibold |
| Animation entrance | 150 to 250ms fade or pop |
| Side margins | 60px minimum |
| German / French expansion vs English | 30 to 40% longer |

`[Agency production rules, internally consistent and arithmetically checkable, but not Meta-published.]`

### 4.7 First-frame evidence

- **1st frame retention target above 90%** ([Motion cheat sheet](https://help.motionapp.com/en/articles/7730931-metrics-cheat-sheet)). Below that the file itself, not the idea, is failing.
- The frequently-cited "the first three seconds delivers 47% of a video ad's value" traces to a **Facebook-commissioned Nielsen study, March 2015**. What it actually found: viewers who watched **less than three seconds** still showed 47% lift in ad recall ([Marketing Dive](https://www.marketingdive.com/news/brand-lift-happens-in-less-than-1-second-of-video-study-finds/377333/)). **The circulated version is a misquote.** It is a brand-lift finding, eleven years old, commissioned by the platform it flatters. Do not build a direct-response argument on it.

### 4.8 What kills a hook

1. **Delayed payoff.** Performance drops "dramatically when the payoff takes longer than" three seconds ([Motion](https://motionapp.com/blog/best-dtc-meta-ad-hooks-2025)).
2. **Green screen and animation openers.** Both below the 5% baseline hit rate.
3. **Question openers.** 5.47%, at baseline, and in health and beauty they are the exact construction Meta's personal attributes policy rejects.
4. **Explainer and how-to openers.** 5.24% and 5.47%, at or below baseline.
5. **Text not readable inside 0.5 seconds**, or text inside the top 14% or bottom 35% where platform chrome covers it.
6. **Auto-cropped assets.** One agency reports a **23% ROAS drop** on auto-cropped verticals versus natively shot 9:16 ([Mintec](https://mintec.co/blog/meta-vertical-creative-safe-zone/)). `[Single client anecdote.]`
7. **Wrong ratio.** 4:5 versus 1:1 gave 12 to 18% CTR improvement; 9:16 ~7% higher CTR on video. `[Single-source. Directionally consistent: taller wins.]`

### 4.9 Hook variation as a production unit

Motion describes an external production pattern of **10 concepts x 5 to 10 hook variations**, where
the body, proof and offer are reused while openings vary. This is a benchmark observation, not the
strategist's standard batch shape or an instruction to treat the hook as an isolated test variable.
Under the governed method, six hook packages are a pre-production option set for an approved
execution and one coherent opening is selected per launch ad. Motion's 25-hook catalogue
([source](https://motionapp.com/blog/best-dtc-meta-ad-hooks-2025)) remains a format menu: post-it
reveal, sunglasses reflection, blurred-to-focus, phone screen text, remote-control SKU switch,
chase sequence, fake text exchange, off-camera partner validation, reverse drop, jump out of phone,
comment-skeptic response, "people always ask me", megaphone, whiteboard explainer, absurd demo,
man-on-the-street, story-time journal and multi-creator mashup.

---

## 5. Video script structures, second by second

### 5.1 The sourced backbone

Motion's published UGC structure is **Hook, Problem, Solution, Value Prop, Social Proof, CTA**, hook at **2 to 3 seconds**, total **under 20 seconds, approximately 60 words** ([Motion](https://motionapp.com/blog/how-to-write-ugc-ad-scripts)).

Billo's is **Hook, Problem, Solution, CTA** at **30 to 60 seconds, 75 to 120 words for a 30-second delivery** ([Billo](https://billo.app/blog/ugc-scripts/)).

**These disagree on length by a factor of three.** Motion's sub-20s aligns with Meta's placement constraint and should be the default for cold prospecting. Billo's 30 to 60s is a retargeting length. Word-rate is consistent at roughly **2.5 words per second**, which is the useful number to script against.

**One published beat-timing anchor beyond the hook:** proof should be deployed **within the first 10 seconds**, and creative with a clear proof element shows **20 to 30% higher completion rate** ([AdLibrary](https://adlibrary.com/posts/dtc-ad-intelligence-creative-frameworks-2026)) `[treat the 10-second proof rule as sound and the 20 to 30% figure as unverified]`.

### 5.2 Where retention drops, universally

Two cliffs. The first at **0 to 3s** (70 to 80% of impressions never reach 3s in cold DTC prospecting). The second at **3 to 15s** (a further 75 to 88% of those who reached 3s do not reach 15s in cold feed). **Roughly 3 to 6% of impressions reach 15 seconds on a cold feed ad.**

**The single most important consequence: the offer and the brand name must be delivered before 15 seconds, because 94 to 97% of impressions never get there.**

`[Everything in the timing columns below is PRACTITIONER CONVENTION unless a source is named. The beat sequences are extrapolated from Motion's six-beat backbone and the 2.5 words-per-second rate; the exact second boundaries are not published anywhere.]`

### UGC direct-to-camera (15s cold prospecting default)

| Sec | Beat | Fight the drop |
|---|---|---|
| 0.0 to 0.5 | Face already talking, mid-sentence. Caption card already on screen | No logo, no title card, no fade-in. First frame is a human face at conversational distance |
| 0.5 to 3 | Hook line. The data favours **offer-only or confession**, not question | Cut on the beat at ~3s. A visual change at the 3s mark resets attention right where hook rate is measured |
| 3 to 6 | Problem, stated behaviourally not demographically | Second cut. Introduce the product physically here even if not named |
| 6 to 10 | Mechanism plus first proof (10s proof window) | Proof must be visual, not spoken |
| 10 to 13 | Value prop, 2 to 3 differentiators max | |
| 13 to 15 | Offer plus CTA | Brand name legible on screen, not only spoken |

Drop points: 0 to 3s, and 6 to 8s where the pivot from problem to product happens. The pivot is where a scripted-sounding transition kills the ad. Bridge with a discovery line.

### Problem-solution narrative (20 to 30s)

| Sec | Beat |
|---|---|
| 0 to 3 | The problem shown, not described. Visual of the failure state |
| 3 to 7 | Escalation. A second, worse instance of the same problem |
| 7 to 9 | Turn. "Then I found..." |
| 9 to 15 | Mechanism. Why this works when the other things did not |
| 15 to 22 | Proof: demo, result, or third-party |
| 22 to 30 | Offer, risk reversal, CTA |

Drop: the 7 to 9s turn. Make the turn a **visual** cut, not a verbal one.

### Founder talking head (20 to 40s)

**Founder visual style hit rate: 8.57%, well above baseline.**

| Sec | Beat |
|---|---|
| 0 to 3 | Confession or contrarian claim. Not "hi I'm the founder of" |
| 3 to 6 | Credential established in one clause, in passing |
| 6 to 12 | The thing the category does wrong |
| 12 to 20 | What we built instead, held in hand |
| 20 to 30 | Proof: manufacturing, ingredient, test, or numbers |
| 30 to 40 | Direct ask |

Drop: 3 to 6s if the credential is front-loaded. The credential arrives **after** the hook is paid off, never as the opener.

### Product demo (10 to 20s)

Three demo categories ([Motion](https://motionapp.com/blog/demonstration-ads-for-facebook-tiktok)): **dramatic**, **street test**, **simple scientific**.

| Sec | Beat |
|---|---|
| 0 to 2 | The mess, the failure, the before state, in motion |
| 2 to 5 | Product enters frame and acts |
| 5 to 9 | The change happens on camera in one unbroken shot |
| 9 to 13 | Repeat the demo from a second angle or surface |
| 13 to 20 | Offer, CTA |

Drop: 5 to 9s if the transformation is cut around rather than shown continuously. **One unbroken shot of the change is the whole asset.**

### Comparison / us vs them (15 to 25s)

Us-vs-them hit rate **6.52%**, above baseline but well below Letter and Founder.

| Sec | Beat |
|---|---|
| 0 to 3 | Both options in frame simultaneously. The contrast IS the hook |
| 3 to 8 | Old way fails, on camera |
| 8 to 13 | New way succeeds, same test, same conditions |
| 13 to 18 | Named difference (the mechanism) |
| 18 to 25 | Offer |

Drop: 8s. Keep the failing option **in frame** during the success shot rather than cutting away.

**Policy note for health and beauty:** a side-by-side of a **person before and after** for weight loss or wrinkles is prohibited outright. A side-by-side of **two products or two conditions** is not. Keep the comparison off the body.

### Listicle (20 to 40s)

Listicle hook hit rate **5.45%**, listicle visual style **5.30%**. **Both at or below baseline. This format is measurably mediocre and is over-briefed.**

| Sec | Beat |
|---|---|
| 0 to 3 | The count plus the payoff, together |
| 3 to 9 | Item 1, strongest |
| 9 to 15 | Item 2 |
| 15 to 21 | Item 3 |
| 21 to 30 | Offer |

Drop: after item 1, at ~9s. Number on screen so the viewer sees how much is left, and put the strongest item first.

### Green screen (15 to 25s)

**Hit rate 4.87%, the lowest visual style in the dataset and below baseline. Recommend against unless there is account-level evidence to the contrary.**

If used: 0 to 3s the reaction to what is behind you, 3 to 8s what the artefact is, 8 to 15s your read on it, 15 to 25s the product tie and offer. Drop at 3 to 5s when the viewer cannot read the artefact, which most green screen ads fail.

### B-roll VSL (45 to 90s, warm and mid-funnel only)

Exceeds the 5 to 15s window that qualifies for all placements. Will not serve In-Stream.

| Sec | Beat |
|---|---|
| 0 to 3 | Hook over the single most arresting B-roll frame |
| 3 to 10 | Problem, wide |
| 10 to 20 | Failed alternatives |
| 20 to 30 | Mechanism reveal |
| 30 to 45 | Proof stack |
| 45 to 60 | Offer construction |
| 60 to 75 | Risk reversal |
| 75 to 90 | CTA plus urgency |

Cold hold rate for 30 to 60s prospecting is **8 to 18%, median ~12%**, roughly a third worse than 15 to 30s creative. **Do not run this cold.** Hard visual reset every 5 to 7 seconds, and plant a specific, dated open loop before 10s that only closes after 45s.

### Testimonial (15 to 30s)

UGC asset type hit rate **7.56%**; UGC overlay **6.73%**; UGC mashup **6.28%**.

| Sec | Beat |
|---|---|
| 0 to 3 | The result stated as a number or a specific, with the speaker's face |
| 3 to 7 | The skepticism admitted (the confession mechanic, 8.74% hit rate) |
| 7 to 14 | What changed, concretely and datedly |
| 14 to 22 | Sensory or usage detail that only a real user would say |
| 22 to 30 | Recommendation plus offer |

Drop: 3 to 7s. Fight it with the admitted doubt. **A testimonial that never concedes anything is read as an ad and dies at second 4.**

### 5.3 Published retention curve data

`[GAP, flagged] No public second-by-second retention curve for DTC Meta ads exists. Motion, Triple Whale and Meta all publish threshold metrics (3s, 15s, ThruPlay, 100%) but nobody publishes the curve between them. Any "retention drops 60% at second 7" claim is almost certainly account-level anecdote presented as industry data.`

What can be stated with sources:
- Impression to 3s: **18 to 28% survive** on cold DTC feed; **24 to 36%** on Reels
- 3s to 15s: **12 to 25% survive** on cold feed 15 to 30s; **8 to 18%** on 30 to 60s; **18 to 30%** on Reels
- Impression to 15s, cold feed: **roughly 3 to 6%**
- Under-15s videos post 50 to 80% hold rate, an artefact of the threshold resolving on completion, not real retention

---

## Sources

**Meta official (transparency.meta.com)**
- [Health and Wellness](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/)
- [Cosmetic Procedures and Wellness](https://transparency.meta.com/policies/ad-standards/content-specific-restrictions/cosmetic-procedures-and-wellness)
- [Privacy Violations and Personal Attributes](https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes)
- [Unacceptable Business Practices](https://transparency.meta.com/policies/ad-standards/fraud-scams/unacceptable-business-practices/)

**Primary datasets**
- [Motion, Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/), [key benchmarks](https://motionapp.com/thumbstop-pulse/cb2026-key-benchmarks-and-insights), [hit rate tables](https://motionapp.com/thumbstop-pulse/creative-benchmarks-2026)
- [Triple Whale, Facebook Ad Benchmarks, Aug 2025 to Jul 2026, 40,000+ brands](https://www.triplewhale.com/blog/facebook-ads-benchmarks)

**Metrics and definitions**
- [Motion, key creative performance metrics](https://motionapp.com/blog/key-creative-performance-metrics)
- [Motion Help Center, metrics cheat sheet](https://help.motionapp.com/en/articles/7730931-metrics-cheat-sheet)
- [AdSights, thumbstop rate, 25 Jul 2026](https://www.adsights.ai/resources/glossary/metrics/thumbstop-rate-tsr)
- [AdSights, hold rate, 23 Jul 2026](https://www.adsights.ai/resources/glossary/metrics/hold-rate)
- [Lebesgue, add-to-cart benchmarks](https://lebesgue.io/facebook-ads/add-to-cart-rate-benchmarks-a-closer-look-at-facebook-ads)

**Specs**
- [Solid, Meta ad specs, verified 8 Aug 2026](https://www.solidlabs.com/ad-specs/meta)
- [Jon Loomer, video ad length, 11 Aug 2025](https://www.jonloomer.com/meta-video-ad-length-requirements/)
- [Sprout Social, Facebook ad sizes](https://sproutsocial.com/insights/facebook-ad-sizes/) and [Instagram ad sizes](https://sproutsocial.com/insights/instagram-ad-sizes/)
- [Strike Social, Meta ad specs, 20 May 2026](https://strikesocial.com/blog/meta-ad-specs/)
- [SocialRails, character limits, 23 Jul 2026](https://socialrails.com/blog/facebook-ad-character-limits)
- [AdsUploader, ad copy specs, 5 Apr 2026](https://adsuploader.com/blog/meta-ad-copy-specs)
- [AdNabu, Meta safe zones, Aug 2026](https://blog.adnabu.com/meta-ads/meta-safe-zones/)
- [Billo, safe zones, 16 Jun 2026](https://billo.app/blog/meta-ads-safe-zones/)
- [Mintec, unified vertical safe zone, 18 Jun 2026](https://mintec.co/blog/meta-vertical-creative-safe-zone/)

**Policy secondary**
- [Jon Loomer, Special Ad Categories, 1 Mar 2025](https://www.jonloomer.com/special-ad-categories-meta-ads/)
- [Jon Loomer, learning phase](https://www.jonloomer.com/qvt/learning-phase-10-or-50-events/)
- [Accelerated Digital Media, health ad restrictions, 18 Feb 2026](https://www.accelerateddigitalmedia.com/insights/guide-to-social-media-health-ad-restrictions-2026/)
- [Clikim, policy update, Jul 2026](https://clikim.com/meta-health-wellness-policy-update/) `[contradicted by Meta's live pages]`
- [Meaningful Agency, health wellness beauty 2026](https://www.meaningfulagency.com.au/blog/meta-ads-for-health-wellness-beauty-brands-2026-guide)

**Creative and testing**
- [Motion, 25 video ad hooks](https://motionapp.com/blog/best-dtc-meta-ad-hooks-2025)
- [Motion, UGC ad scripts](https://motionapp.com/blog/how-to-write-ugc-ad-scripts)
- [Motion, demonstration ads](https://motionapp.com/blog/demonstration-ads-for-facebook-tiktok)
- [Caleb Kruse via Motion, 10 ads vs 100 ads, Jan 2026](https://motionapp.com/library/talk/the-new-meta-ads-testing-strategy-10-ads-vs-100-ads/)
- [Flighted, creative testing budget, 1 Jul 2026](https://www.flighted.co/blog/how-to-calculate-your-meta-ads-creative-testing-budget)
- [Flighted, benchmarks by industry, 5 May 2026](https://www.flighted.co/blog/meta-ads-performance-benchmarks-by-industry)
- [Billo, UGC scripts, 16 Jun 2026](https://billo.app/blog/ugc-scripts/)
- [RocketShip HQ, text overlays, 8 Jun 2026](https://www.rocketshiphq.com/text-overlays-video-ads-mobile/)
- [AdLibrary, DTC creative frameworks, 15 Mar 2026](https://adlibrary.com/posts/dtc-ad-intelligence-creative-frameworks-2026) `[aggregator]`
- [AdAmigo, frequency benchmarks](https://www.adamigo.ai/blog/meta-ads-frequency-benchmarks-when-ads-start-fatiguing) `[low confidence]`
- [Digiday, 85% sound off, 17 May 2016](https://digiday.com/media/silent-world-facebook-video/) `[dated]`
- [Marketing Dive, Facebook/Nielsen brand lift, Mar 2015](https://www.marketingdive.com/news/brand-lift-happens-in-less-than-1-second-of-video-study-finds/377333/) `[dated, commonly misquoted]`

---

### Access limitation to note

`facebook.com/business` (the Ads Guide and Business Help Center) is disallowed to automated fetching by robots.txt. **Every spec figure in section 1 is a second-hand reading of Meta's Ads Guide.** Sprout, SocialRails and Solid each state they verified against it (Aug 2025, Jul 2026, Aug 2026) and they agree on the load-bearing numbers, so confidence is reasonable. Section 2 policy text is quoted directly from transparency.meta.com and is first-hand.
