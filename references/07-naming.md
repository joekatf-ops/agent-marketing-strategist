# Naming conventions

Names make the coordinate, test batch and execution traceable without turning execution variables
into concept axes. Resolve every controlled token from the active brand folder. Never invent or
silently abbreviate a missing code. Stop and ask when a required token is unavailable.

## Locked shapes

Use underscores only. Spaces, hyphens and version suffixes are prohibited.

| Level | Exact shape |
|---|---|
| Test ID | `CONTST###` |
| Campaign | `[BRAND]_[PRODUCT]_[CT|SC]_[ABO|CBO]_[REGION]_[YYYYMMDD]` |
| Ad set | `[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]` |
| Ad | `[FULL_AD_SET_NAME]_[UWA|PRA|SLA|PDA]_[FORMAT]_[LP|PDP|HP|CP]_[POSTID]` |

The valid campaign pairs are CT with ABO for creative testing and SC with CBO for scaling. Do not
produce CT_CBO or SC_ABO names.

## Test ID

`CONTST` is the locked universal prefix. The three-digit number is sequential, never reused and
never replaced by a brand-configurable concept prefix. Every NNT, INSPO and ITR batch receives the
next unused value, even when an ITR retains the same Who x Primary Problem coordinate.

The short test ID may also name its tracker record and asset folder. It never substitutes for the
full ad-set name in Ads Manager.

## Campaign

```
[BRAND]_[PRODUCT]_[CT|SC]_[ABO|CBO]_[REGION]_[YYYYMMDD]
```

- BRAND, PRODUCT and REGION are controlled codes from the active brand folder.
- CT means creative testing and always pairs with ABO.
- SC means scaling and always pairs with CBO.
- YYYYMMDD is the planned campaign launch date in the account timezone.

Examples:

```
BRND_SKU_CT_ABO_AU_20260901
BRND_SKU_SC_CBO_AU_20260915
```

## Ad set

```
[CONTST###]_[NNT|INSPO|ITR]_[WHO]_[PROBLEM]
```

- CONTST### is the test batch, not the coordinate key.
- Source is exactly NNT, INSPO or ITR.
- WHO is the controlled code for the selected Who.
- PROBLEM is the controlled code for the one Primary Problem.
- The complete name represents one batch against one coordinate.

Example:

```
CONTST001_NNT_NIGHTSHIFT_ACHINGFEET
```

Messaging route, awareness, hook, format, creator, proof, offer presentation, visual treatment and
destination never enter the ad-set coordinate portion.

## Ad

```
[FULL_AD_SET_NAME]_[UWA|PRA|SLA|PDA]_[FORMAT]_[LP|PDP|HP|CP]_[POSTID]
```

The full ad-set name is inherited exactly and without abbreviation. Awareness is UWA, PRA, SLA or
PDA. Most Aware belongs to the conversion environment and has no standard ad code in this shape.

Before publication, `[POSTID]` is the placeholder `POSTIDXXX`. After manual publication, replace it
in the retained record with the real Post ID. A graduated winner keeps that real Post ID when it is
placed into scaling.

Example before publication:

```
CONTST001_NNT_NIGHTSHIFT_ACHINGFEET_UWA_UGC_LP_POSTIDXXX
```

Example retained after publication:

```
CONTST001_NNT_NIGHTSHIFT_ACHINGFEET_UWA_UGC_LP_123456789012345
```

## Controlled format codes

Initial controlled codes are UGC, VSL, FOUNDER, DEMO, TESTIMONIAL, STATIC, CAROUSEL and COMPARISON.
Add a new code only for a genuinely different production format and document it in the brand
folder before use. Do not use generic VID, IMG or CAR when the controlled execution format is known.

## Destination codes

| Code | Destination |
|---|---|
| LP | Landing page |
| PDP | Product-detail page |
| HP | Homepage |
| CP | Collection page |

UWA and PRA default to LP. SLA and PDA default to PDP. Every deliberate deviation must select
exactly one controlled destination token: LP, PDP, HP or CP. It is valid only when the destination
remains congruent and the Destination Handoff records the reason, evidence, risk, owner and
approval. If a page cannot be accurately represented by one of the four tokens, block launch rather
than inventing a token or producing an invalid ad name.

## Locked rules

1. Use only the exact campaign, ad-set and ad shapes above.
2. Use underscores only and never add a version suffix.
3. Never reuse or skip a CONTST number.
4. The ad inherits its complete ad-set name without abbreviation.
5. Hooks and messaging routes live in the execution record, not in names.
6. Never leave a blank token in a manual Meta build.
7. `POSTIDXXX` is only a pre-publication placeholder; scaling uses the real Post ID.
8. Read names from controlled records. Never reconstruct them from conversation memory.
9. Every destination, including an exception, maps to one controlled destination token.

## Preflight

- [ ] Campaign stage and budget pair is CT_ABO or SC_CBO
- [ ] Campaign includes brand, product, region and launch date codes
- [ ] Ad set includes one sequential CONTST ID, one source, one Who and one Primary Problem
- [ ] Ad inherits the full ad-set name and uses one allowed awareness code
- [ ] Format and destination codes exist in the controlled code maps
- [ ] New ads end in POSTIDXXX; graduated scaling ads carry their real Post ID
- [ ] No spaces, hyphens, optional suffixes or version markers appear
