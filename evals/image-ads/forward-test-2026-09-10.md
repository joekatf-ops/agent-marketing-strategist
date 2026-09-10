# Independent text-only forward test

Date: 2026-09-10. Package: working v1.1.0. Runtime: Codex subagent, inherited model;
exact model identifier not exposed in the result. Capability scope: local reading and text only.
No live rendering, browsing or advertising-performance test. Two independent raw tasks were
provided without target answers. Responses below are the evaluator's actual delivered text.


## task-a-response.md

Joe, here’s a simple square ad brief and ready-to-use prompt. Image generation isn’t available in this session, so no image has been rendered.

**Brief:** One 1:1 ad for your desk cable organiser, using the supplied six-cable capacity. The message is keeping six desk cables together.

**Image copy:**

- Main line: “Keep six desk cables together.”
- Small product label: “Desk cable organiser”
- CTA: “Shop now”

**Layout:** Large headline at the top, six decorative cable-like lines in the middle, product label and CTA below. Off-white, charcoal and muted blue are provisional design choices. This text-led design needs no product photo.

:::writing{variant="standard" id="57241"}
Create one 1:1 square image ad, requested canvas 2048 × 2048 pixels, for a desk cable organiser that holds six cables. Communicate one idea: keeping six desk cables together.

Use an off-white background, bold charcoal sans-serif typography and muted blue accents. Place the large headline in the top third. Use exactly six simple cable-like curved lines as decorative graphics in the middle, with generous space around them. These are abstract graphics, not a product demonstration. Do not depict the organiser or imply its shape, materials, mounting method, separate slots or connector compatibility.

Render only this exact text:
Main headline: “Keep six desk cables together.”
Smaller product label: “Desk cable organiser”
Small CTA at the bottom: “Shop now”

Keep all text comfortably inside the edges and legible on a phone. Add no logo, price, offer, reviews, ratings, guarantees or other claims. Produce only the square ad.
:::

The copy uses your product description and capacity. Brand styling is provisional; rendered dimensions, spelling and layout still need checking once an image is generated.


## task-a-limitations.md

Joe, Task A was run as an independent text-only session using the supplied skill.

Request: “Make me an image ad for my desk cable organiser. It holds six cables. I have no customer research or photos yet. Keep it simple.”

Delivered: One concise square-ad brief, exact consumer copy and a complete portable image prompt. No research intake, customer-belief requirement, concept approval or campaign batch was introduced.

Observed limitations:

- No image generation or vision was available. No image was rendered or visually inspected, and no actual pixel dimensions were verified.
- Product appearance, materials, mounting method and separate cable positions are unknown. The design uses decorative cable-like graphics and does not depict a fabricated product.
- No brand voice, logo, palette, customer evidence, offer or destination was supplied. Provisional art direction is identified; unsupported proof and optional commercial details are omitted.
- “Holds six cables” supports the capacity and gathering message. The core reference's example of six separate loops was not treated as a fact about this product.
- The requested image remains unrendered because of the test's capability limit. The skill explicitly permits a brief and prompt fallback, which was delivered without pretending it was an image.

References read: SKILL.md; references/00-working-core.md; references/26-copywriting-standards.md; references/27-image-ad-workflow.md; contracts/static-spec.md; config/copy-lexicon.yml.

No source skill or external system was changed. Only these requested test records were written.


## task-b-response.md

Joe, here’s your Nano Banana Pro prompt. The linked image wasn’t inspected in this text-only session, so the layout is original. I’ve adapted the saved caption’s rhythm without assuming your product has six separate slots.

:::writing{variant="standard" id="57242"}
Create one 1:1 square image ad in Nano Banana Pro, requested canvas 2048 × 2048 pixels, for a desk cable organiser that holds six cables.

Use the supplied caption “Six cables. Six places.” only as inspiration for a short, count-led message. Do not infer a visual layout from the unavailable reference image. Do not copy a competitor's branding or assume this product has separate slots.

Make an original, text-led composition. Use a warm white background, oversized black sans-serif typography and one cobalt-blue accent. Put the headline in the upper half, with “Six cables.” above “One organiser.” Use exactly six abstract cable-like curves as a simple decorative motif beneath the headline. Keep the motif separate from any product illustration. Place the small supporting line near the bottom. These colors and type choices are provisional art direction.

Render only this exact text:
Main headline: “Six cables. One organiser.”
Supporting line: “Keep your desk cables together.”

Keep the reading order clear, leave generous margins and make both lines legible on a phone. Do not depict the organiser, packaging, logo, mounting method, materials, connector types or separate slots. Include no price, offer, testimonials, ratings, guarantees, performance claims or additional text. Produce only one square ad.
:::


## task-b-limitations.md

Joe, Task B was run as a separate text-only session using the supplied skill, without carrying creative decisions from Task A into the request.

Request: “Make a Nano Banana Pro image ad using this competitor reference: https://example.com/unavailable-ad.png. The caption I saved was Six cables. Six places. My product is a desk organiser that holds six cables. I only need the prompt today.”

Delivered: One Nano Banana Pro prompt specifying a 1:1 square image, exact copy, original composition, provisional styling and factual exclusions. No image generation was attempted because the user requested only a prompt.

Source record:

- Source: https://example.com/unavailable-ad.png
- Session date: 2026-09-10.
- Actual image inspected: no. No browsing or vision was permitted in this test. The URL was not fetched, so no claim is made about its HTTP status or actual accessibility outside the session.
- Available source content: the user-supplied saved caption, “Six cables. Six places.” It was not assumed to be text embedded in the unseen image.
- Source ratio, colors, layout, hierarchy, typography, product depiction and proof objects: unknown.
- Performance evidence: none. The reference was treated as inspiration only.

Interpretation and adaptation:

- The caption's short paired phrases and repeated count suggest a capacity-led message. This is a reading of supplied text, not a visual observation or a claim about performance.
- Retained: the concise paired-phrase structure and known six-cable count.
- Replaced: “Six places” with “One organiser” because distinct cable positions were not supplied as a product fact.
- Removed: no observed visual element can be said to have been removed, since the image was not inspected. The prompt excludes unsupported competitor identity, product attributes and proof.
- Added: an original square typographic layout, six abstract decorative lines and the practical gathering message.

Observed limitations:

- Faithful visual adaptation cannot be assessed without the actual image. The user received a clearly identified original-layout fallback rather than fabricated reference analysis.
- Unknown product appearance prevented faithful product depiction. The prompt deliberately uses an abstract text-led design.
- Brand voice and visuals were unavailable, so styling is provisional. No customer validation or performance prediction was claimed.
- No render, image spelling inspection, product fidelity inspection or actual pixel measurement occurred. Those checks are outside a prompt-only deliverable.
- No Higgsfield call was made, and no provider-specific resolution support, generation parameters or pricing were asserted. “2048 × 2048” is the requested canvas in the portable prompt, not a verified provider result.

References read: SKILL.md; references/00-working-core.md; references/26-copywriting-standards.md; references/27-image-ad-workflow.md; contracts/static-spec.md; contracts/reference-analysis.md; config/copy-lexicon.yml. The Higgsfield connector guide was unnecessary because no connector was used.

No source skill or external system was changed. Only these requested test records were written.

## Prompt-only follow-up

Two further independent tasks used only PROMPT.md, with no supporting reference files.

### task-c-response.md

Joe, the support questions show that these customers want clarity on desk setup and cable fit. They do not establish compatibility, so this draft uses the confirmed six-cable capacity and avoids suggesting answers we do not have.

**Brief:** One 1:1 square image for a desk organiser that holds six cables. Communicate keeping six desk cables together. Use a text-led layout with a large headline, a smaller product label and generous space. Warm white, charcoal and blue are provisional styling choices. No product or image reference was supplied.

:::writing{variant="standard" id="57243"}
Create one 1:1 square image ad for a desk organiser that holds six cables. Make the message easy to understand at phone size: keeping six desk cables together.

Use an original typographic composition with a warm white background, charcoal text and a restrained blue accent. Put the headline prominently in the upper two-thirds, with the smaller product label beneath it. Keep generous margins and clear space around the text. Use flat graphic styling without a photographic scene.

Render only this exact text:
Main headline: “Keep six desk cables together.”
Product label: “Desk cable organiser”

The customer support questions concern standing-desk use and thick charging-cable fit, but neither answer is known. Do not imply either capability in words or imagery. Do not depict a standing desk, cable thickness, connector type, mounting method or product shape. Do not add a product illustration, packaging, logo, reviews, ratings, price, offer, compatibility claim or additional text. Deliver only one square ad.
:::

**Limitations:** This is a prompt, not a rendered image. No generation or visual inspection occurred. The two questions informed the factual boundaries of the ad; they are not evidence of product performance or how common these concerns are. Brand styling remains provisional, and the final image will need its dimensions, spelling and legibility checked.

### task-d-response.md

Joe, I’ve used your correction to six cables and kept the old eight-cable note unchanged. For buyers ready to purchase, the ad leads with the $20 price and states its validity date.

**Brief:** One 1:1 square offer image for a desk organiser that holds six cables. Price: $20, valid through 30 September 2026. Use a text-led composition with the product label at the top, the price and capacity prominent in the centre, then the validity date and one CTA below. White, black and green are provisional styling choices. No product photo or brand visuals were supplied.

:::writing{variant="standard" id="57244"}
Create one 1:1 square offer image for a desk cable organiser that holds six cables, aimed at people ready to buy. The confirmed price is $20, valid through 30 September 2026. The owner has corrected an old eight-cable note to six cables. Use only the current six-cable fact in the artwork.

Create an original typographic design on a white background with black sans-serif text and a green CTA accent. Place the product label at the top. Make the main headline the largest element in the centre, with the price especially prominent. Put the validity line below at a clearly readable size, then the CTA near the bottom. Leave generous margins and keep the whole image legible on a phone. Use flat graphic styling, with no product depiction or photographic scene.

Render only this exact text:
Product label: “Desk cable organiser”
Main headline: “Six cables. $20.”
Validity line: “Price valid through 30 September 2026.”
CTA: “Shop now”

Preserve the price notation exactly as supplied. Do not add a currency code, former price, percentage saving, sale badge, countdown, stock claim, shipping promise, reviews or guarantees. Do not mention eight cables. Do not invent the organiser's appearance, packaging or logo. Add no other text. Deliver only one square image.
:::

**Limitations:** This is a prompt only; no image was generated or inspected. The supplied facts support the capacity, price and date. The dollar currency was not specified, so the prompt preserves “$20” without assigning one. Styling is provisional. Your current correction governs this draft; no saved brand record was rewritten. Final dimensions, spelling and layout remain unchecked until an image is rendered.
