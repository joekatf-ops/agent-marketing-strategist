# Guided image workflow forward test

> Historical record. Copy references, contracts and tooling named below were removed in 1.9.0,
> when ad copy moved to the DTC Ad Copywriting playbook. They are preserved at the
> `pre-copy-consolidation-2026-10-01` tag.

Date: 2026-09-17
Version: 1.8.0
Runtime: independent Codex subagent; inherited model identifier not exposed by this test.

One independent subagent received only the raw requests, the relevant skill entrypoint and test
capabilities. It was instructed to treat scenarios independently and not read the expected criteria,
release notes, prior conversation or implementation diff. The five cases were evaluated against
`guided-cases.json` afterwards. The portable case was repeated after reducing duplicate bundle
content; both responses are retained below. No generation tools or paid model APIs were invoked.

## Assessment

| Case | Result | Observed behaviour |
|---|---|---|
| new-reference | Pass | Three use-situation options, one recommendation; preserves supplied layout and ratio; no research gate. |
| selection-continuity | Pass | Option 3 selects the latest dark navy art direction; exact copy stays fixed; no extra approval. |
| approved-revision | Pass | Direct 4:5 regeneration brief; preserves supplied properties; identifies inaccessible references honestly. |
| delegated-thin-input | Pass | Direct, factual text-led brief with provisional type; no research, font or photo prerequisite. |
| portable-guided | Pass | Reuses audience, format and ratio; offers headline choices without silently producing a finished ad. |

The simple spatula case used the removable head's practical washing use as its sole supported
message and moved directly to headlines, as allowed when alternatives would be manufactured.
These are bounded instruction-following checks, not proof of cross-model reliability, image quality
or advertising performance. The cases ran in one test agent, not five separate isolated model calls.

## Recorded responses

# Guided image forward test responses

## new-reference

Files read:

- `SKILL.md`
- `references/00-working-core.md`
- `references/26-copywriting-standards.md`
- `references/29-moment-to-meaning.md`
- `references/27-image-ad-workflow.md`
- `references/34-art-direction-and-revisions.md`
- `contracts/static-spec.md`
- `references/37-guided-image-development.md`
- `config/copy-lexicon.yml`
- `references/30-scientific-advertising.md`
- `references/21-evidence-and-doctrine.md`

Required brand-context check: `memory/brands/wayline/brand.yml` was absent.

Actual response:

Joe, I’m using the marketing strategist skill to develop this with you. We have the Story canvas, two-column comparison and product placement set. First, let’s choose the use situation.

1. **Home desk:** reaching for a charger between tasks, with frequently used cables kept beside the workspace.
2. **Bedside charging:** putting the phone down at night and having its charging cable within reach.
3. **Shared charging spot:** giving several household cables their own places instead of leaving them loose together.

I recommend **1, home desk**. It gives the six slots a clear job and supports a simple comparison between loose cables and cables organised in the dock, without needing competitor claims.

| Decision | Current choice |
|---|---|
| Product | Matte silicone, six cable slots, adhesive base; supplied facts |
| Layout | Two comparison columns, organiser as the main subject below; your selection |
| Delivery | One 9:16 Story |
| Offer | None |
| Use situation | Awaiting your selection; options are creative proposals |

Which use situation should we develop: **1, 2 or 3**?

## selection-continuity

Files read:

- `SKILL.md`
- `references/00-working-core.md`
- `references/26-copywriting-standards.md`
- `references/29-moment-to-meaning.md`
- `references/27-image-ad-workflow.md`
- `references/34-art-direction-and-revisions.md`
- `contracts/static-spec.md`
- `references/37-guided-image-development.md`
- `config/copy-lexicon.yml`
- `references/30-scientific-advertising.md`
- `references/21-evidence-and-doctrine.md`

Required brand-context check: `memory/brands/wayline/brand.yml` was absent.

Actual response:

Joe, direction **3 is selected: dark navy studio, warm spotlight and cream type**. I’m using the marketing strategist skill and carrying forward the approved audience, angle and copy. This text-only environment cannot render the image, so here is the finished production brief and prompt.

| Element | Production decision |
|---|---|
| Deliverable | One 9:16 Story, target 1080 × 1920 pixels |
| Audience and message | Home-desk users; keep frequently used cables within reach; approved |
| Format | Product hero; approved |
| Composition | Headline above a large dock illustration, supporting line below; original layout |
| Art direction | Dark navy studio, warm spotlight, cream typography; option 3 selected |
| Typography | Arial Bold headline and Arial Regular support; provisional, no font files inspected |
| Product | Matte silicone, six slots, adhesive base; supplied facts |
| References | None accessible; product geometry and colour are unverified |

**Exact image copy**

Your charger, right where you left it.

Six slots. One tidy desk.

**Production prompt**

:::writing{variant="standard" id="76102"}
Create one 9:16 Story image ad for Wayline Cable Dock, targeting 1080 × 1920 pixels. Use an original product-hero layout for people working at a home desk. Communicate that frequently used cables can have a place within reach.

Use a deep navy studio background and surface with one soft, warm spotlight from the upper left. Keep the shadows rich, the light falloff gradual and all contact shadows consistent with one perspective. Make the product the principal visual beneath the headline, with ample breathing room around the typography.

There is no product photograph. Depict a provisional, simplified neutral-grey matte silicone organiser with exactly six cable slots, including a charging cable seated in a slot. Its shape and neutral colour are illustrative choices, not verified Wayline appearance. Do not add packaging, a logo, visible adhesive mechanisms or unsupported hardware. Do not depict a glossy material.

Use cream typography throughout. Headline: Arial Bold, large, arranged in readable lines. Render exactly: “Your charger, right where you left it.” Supporting line: smaller Arial Regular, render exactly: “Six slots. One tidy desk.” Keep both lines away from the canvas edges and legible at phone size.

Add no other words, badge, offer, rating or claim. Generate the integrated scene and typography as one complete ad.
:::

The product illustration is provisional. No image has been generated, and dimensions, spelling in pixels and visual fidelity remain unchecked.

## approved-revision

Files read:

- `SKILL.md`
- `references/00-working-core.md`
- `references/26-copywriting-standards.md`
- `references/29-moment-to-meaning.md`
- `references/27-image-ad-workflow.md`
- `references/34-art-direction-and-revisions.md`
- `contracts/static-spec.md`
- `references/37-guided-image-development.md`
- `config/copy-lexicon.yml`
- `references/30-scientific-advertising.md`
- `references/21-evidence-and-doctrine.md`
- `references/14-learning-system.md`

Actual response:

Joe, I’ve prepared the 4:5 full-regeneration brief using the marketing strategist skill. The approved Story remains the design authority. I can’t render a faithful version here because image generation, the approved master and the product photograph are unavailable.

| Preserve | Change |
|---|---|
| Warm grey studio light | Recompose for 4:5, target 1080 × 1350 pixels |
| Off-white typography | Reflow spacing and line breaks as needed |
| Six-slot silicone product | Regenerate the complete scene and product |
| Both exact copy lines | No wording changes |

The approved master must govern composition, typography and finish; the product photograph must govern the product’s actual shape, colour and construction. Neither has been inspected here.

**Production prompt, for use once both references are accessible**

:::writing{variant="standard" id="76103"}
Fully regenerate the attached approved Story ad as one 4:5 image, targeting 1080 × 1350 pixels. Use the approved Story master as the authority for its visual hierarchy, composition, warm grey studio light, off-white typography and overall finish. Use the attached product photograph as the authority for the actual silicone product, including its six cable slots, proportions, colour and construction. Product identity takes precedence if the master and photograph conflict.

Generate the entire integrated scene and product anew. Preserve the approved lighting direction, softness, tonal relationships, material response and atmosphere. Recompose the existing design for the shorter 4:5 canvas, adjusting spacing and line breaks while retaining its focal order and subject prominence. Do not crop the Story, stretch it or reuse a product cutout.

Preserve these exact words and punctuation:
Headline: “Your charger, right where you left it.”
Supporting copy: “Six slots. One tidy desk.”

Retain the master’s off-white type treatment and clear difference between headline and supporting copy. Keep all essential content readable at phone size and inside the canvas. Add no new copy, props, product features, offers or decorative treatments. Do not infer missing visual details from this text: the master and product photograph are required inputs.
:::

The brief is ready; the 4:5 image has not been generated or visually checked.

## delegated-thin-input

Files read:

- `PROMPT.md`

Required brand-context check: `memory/brands/fernwick/brand.yml` was absent.

Actual response:

Joe, I’ve chosen a simple text-led square ad about taking the removable head off for washing. I can’t render images in this text-only environment, but the copy and generation prompt are ready.

| Element | Chosen direction |
|---|---|
| Output | One 1:1 image, target 1080 × 1080 pixels |
| Format | Text-led feature ad; chosen under your delegation |
| Audience | People washing up after cooking; creative assumption |
| Visual | Green background, cream text, generous spacing; provisional design |
| Type | Arial Bold headline, Arial Regular support; provisional, no font files supplied |
| Assets | Supplied text only; no product photograph, illustration or invented logo |

**Exact image copy**

Fernwick silicone spatula

Take it apart for washing.

Green silicone. Removable head.

**Generation prompt**

:::writing{variant="standard" id="76104"}
Create one square 1:1 image ad, targeting 1080 × 1080 pixels, for Fernwick silicone spatula. Make an original text-led design with a deep green background and warm cream typography. This palette is a provisional creative choice, not an established brand identity.

Use three left-aligned text levels with generous spacing. At the top, set the plain product identifier “Fernwick silicone spatula” in small Arial Regular. Make “Take it apart for washing.” the dominant headline in large Arial Bold, split naturally across two or three lines. Below it, set “Green silicone. Removable head.” in smaller Arial Regular. Render these exact words and punctuation with strong contrast and readable spacing at phone size.

The factual premise is a green silicone spatula with a removable head. Do not depict an unverified product shape, packaging, attachment mechanism or official logo. Use typography and colour as the complete composition. Add no other copy, offer, price, badge, rating, claim about cleaning speed or dishwasher-safety claim. Keep all text comfortably inside the canvas edges.
:::

No image has been generated or inspected.

## portable-guided

Files read:

- `dist/image-ad-bundle.md`

Required brand-context check: `memory/brands/fernwick/brand.yml` was absent.

Actual response:

Joe, I’m using the image-ad bundle to develop this with you. The audience, Benefits Callout format and 4:5 canvas are set. I recommend making the removable head’s practical use the message: take it off to wash it separately.

Let’s choose the headline:

1. **Take it apart for washing.** Leads with the practical use of the removable head.
2. **A spatula that comes apart.** Introduces the feature directly, leaving the callout to explain washing the head separately.
3. **After dinner, take the head off.** Starts with a familiar moment after cooking.

I recommend **1**. It gives the removable head a clear purpose in a short line.

| Decision | Current choice |
|---|---|
| Product | Fernwick silicone spatula with removable head; supplied fact |
| Audience | People cooking at home; supplied |
| Format and delivery | Benefits Callout, one 4:5 concept; supplied |
| Angle | Separate washing; proposed from the supplied feature |
| Headline | Three proposals above; awaiting selection |
| Support and visual direction | Open |
| Discount | None |

Which headline should we take forward: **1, 2 or 3**?


## Final portable-bundle rerun

## portable-guided

Files read:

- Raw input: portable-guided case only
- `dist/image-ad-bundle.md`: complete current file, lines 1 through 1451

Actual response:

Joe, I’m using the image-ad bundle to develop this with you. With the removable head as the feature, I recommend a straightforward message: take the head off to wash it separately. Let’s choose the headline first.

1. **Wash the head separately.** Leads with the practical use of the feature.
2. **A spatula that comes apart.** Introduces the product detail, with the callout explaining why it matters.
3. **Finished cooking? Take the head off.** Connects the feature to the familiar moment of washing up.

I recommend **1**. It gives the removable head a clear purpose in four words.

| Decision | Current status |
|---|---|
| Product | Fernwick silicone spatulas with removable heads; supplied |
| Audience | People cooking at home; supplied |
| Format | Simple Benefits Callout; supplied |
| Delivery | One 4:5 concept; requested |
| Message | Remove the head for separate washing; recommended |
| Headline | Three proposals above; awaiting selection |
| Supporting copy and visual direction | Still open |
| Discount | None |

Which headline should we develop: **1, 2 or 3**?
