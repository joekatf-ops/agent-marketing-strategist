<!-- archived verbatim from Notion. Not loaded by the agent. See README.md in this
directory for what was integrated into the reference library and what was not. -->

# Naming principles

Names must make every campaign, ad set and ad traceable from strategy through production, testing and scaling.

Use underscores only. Do not add a version suffix.

# Concept test ID

Format: CONTST###

Examples:

- CONTST001
- CONTST002
- CONTST003

The number identifies a specific test batch. Every new NNT, INSPO or ITR batch receives the next sequential number.

The Notion concept title and production folder may use the short CONTST### code.

# Campaign name

Brand-neutral template:

`[BRAND]_[PRODUCT]_[CT|SC]_[ABO|CBO]_[REGION]_[YYYYMMDD]`

Definitions:

- BRAND: account or brand code
- PRODUCT: product or product-family code
- CT: creative testing
- SC: scaling
- ABO or CBO: budget structure
- REGION: AU, US, NZ or another agreed market code
- YYYYMMDD: campaign launch date

A campaign is created per product, per region.

# Ad-set name

Format:

`[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]`

Example:

CONTST001_NNT_SideSleepers_MorningNeckPain

Rules:

1. Begin with the sequential test ID.
2. Add the source classification.
3. Add a concise Who token.
4. Add a concise primary Problem token.
5. Do not include awareness, angle, format, destination or version.

# Ad name

Format:

`[FULL AD SET NAME]_[AWARENESS]_[FORMAT]_[DESTINATION]_[POSTID]`

Example before a Post ID exists:

CONTST001_NNT_SideSleepers_MorningNeckPain_UWA_UGC_LP_POSTIDXXX

Example after publication:

CONTST001_NNT_SideSleepers_MorningNeckPain_UWA_UGC_LP_123456789012345

The complete ad-set name must be inherited without abbreviation.

# Awareness codes

- UWA: Unaware
- PRA: Problem Aware
- SLA: Solution Aware
- PDA: Product Aware

# Format codes

Use a concise, controlled description of the execution format:

- UGC
- VSL
- FOUNDER
- DEMO
- TESTIMONIAL
- STATIC
- CAROUSEL
- COMPARISON

Add new codes only when a genuinely different production format is introduced.

# Destination codes

- LP: landing page
- PDP: product detail page
- HP: homepage
- CP: collection page

# Post ID rule

Every new ad begins with POSTIDXXX at the end of its name. Replace it with the real Post ID once the ad is published.

The Post ID makes it easy to identify, find and move the exact winning ad into the CBO scaling campaign while preserving its history.

# Locked examples

Ad set:

CONTST001_INSPO_BusyProfessionals_AfternoonEnergyCrash

Ads:

- CONTST001_INSPO_BusyProfessionals_AfternoonEnergyCrash_UWA_UGC_LP_POSTIDXXX
- CONTST001_INSPO_BusyProfessionals_AfternoonEnergyCrash_PRA_VSL_LP_POSTIDXXX
- CONTST001_INSPO_BusyProfessionals_AfternoonEnergyCrash_SLA_DEMO_PDP_POSTIDXXX
- CONTST001_INSPO_BusyProfessionals_AfternoonEnergyCrash_PDA_STATIC_PDP_POSTIDXXX
