# Meta creative benchmarks and thresholds

Benchmark data for reading performance, not for writing. Loaded with the ops stack when planning or
diagnosing a test, and deliberately not in the always-loaded craft stack: a benchmark tells you
whether a number is good, and it cannot help you write the next line.

Split out of `12-meta-platform.md`, which keeps the specs, the policy, the hook data and the script
structures. Provenance for every figure below is in the Sources section of that file.

Two standing cautions. Every figure here has a sample window and will age, so recheck before relying
on one. And a benchmark is market evidence, never evidence about this brand's customers: a result in
the brand's own test register outranks anything here. See `13-brand-folder.md` for the evidence
classes and `21-evidence-and-doctrine.md` for what to do when a benchmark and the brand disagree.

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
