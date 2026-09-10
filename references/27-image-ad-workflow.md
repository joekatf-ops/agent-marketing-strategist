# Square image-ad workflow

Create a useful 1:1 image ad from product information and a prompt. Research is an enhancement.
The brief is about the product and the requested creative task, not a compulsory customer belief.

## Three entry points

1. **Create:** use the supplied product information to choose a message and composition.
2. **Adapt:** inspect a supplied ad, identify its useful structure, and rebuild the argument for
   the active product and brand.
3. **Revise:** change the requested part of an existing asset while preserving approved details.

Use whatever brand context and research are already available. Do not require setup, a research
report, customer persona, awareness label, CONTST ID or concept approval to start. Ordinary requests
default to one finished image unless a different count is requested. Options are not launch ads.

## 1. Resolve the product and request

When given a website, landing page or PDP, read it and the relevant product page first. Use the
website/PDP intake in `references/00-working-core.md` to extract product details, imagery, practical
questions and terms. A URL is sufficient input when accessible. Preserve the ad-to-page message;
do not request a separate product brief for facts the supplied page already contains.

Extract product name or type, supplied features, use, target market when relevant, offer if supplied,
brand preferences, image references and requested count. Missing optional information is not a
blocker. Choose an appropriate provisional style when none is supplied and identify that choice
briefly outside the creative. Ask only if the product itself is unknown or a required input cannot
be inferred responsibly.

Use a supplied product photo when available. Inspect it before generation: silhouette, material,
color, packaging, wordmark, proportions, hardware, connection points and visible text are identity
constraints. A photo reduces drift; it does not guarantee fidelity.

Without a product photo, a clearly specified simple product can be illustrated provisionally. For a
specific branded product with unknown appearance, choose a text-led or contextual design that does
not depict invented packaging or hardware. State any fidelity limitation. Do not refuse the whole
request just because photoreal product reproduction is not possible.

## 2. Choose the message and format

Use one concrete product detail, practical payoff, use case, demonstration, legitimate offer or
research-supported angle. Customer research can sharpen which message to choose; a belief-change
statement and formal awareness classification are optional. When the user requests awareness
variants, vary the argument to suit the requested state. Most Aware is available for ordinary ads.

Choose a design the facts can support. If no review exists, do not choose a testimonial card. If no
price exists, omit price. Never fill optional gaps with invented proof or a page of placeholders.

Useful format families:

| Format | Use when | Required material |
|---|---|---|
| Product hero | One feature or use deserves focus | Accurate product depiction or an honest text-led alternative |
| Use-case lifestyle | Context makes the product's relevance clear | Credible scene and supported use |
| Text-led statement | The main idea is strong without product photography | Exact, grounded copy |
| Annotated close-up | Detail explains fit, materials or use | Inspected product reference |
| Setup or demonstration | Seeing the action answers a question | Verified steps and correct hardware |
| Comparison | A useful difference can be shown fairly | Comparable sourced facts |
| Mechanism illustration | An explanation is accurate and useful | Verified mechanism without invented outcomes |
| Testimonial | A real person's words address the message | Exact quote and its source |
| Founder note | Authentic intent or experience is relevant | Real first-person material |
| Offer card | Current price or terms drive action | Supplied or verified terms |
| Checklist | Practical criteria organize the decision | Accurate useful criteria |
| Problem and solution | The product addresses a supported practical obstacle | Defensible connection between problem and product |

These are options, not a performance ranking. Do not automatically create every combination.

## 3. Adapt a reference when supplied

Use `contracts/reference-analysis.md` only for reference-based work. Inspect the actual image.
Separate embedded copy from platform fields and chrome. Record the layout and the persuasive move
as observations and interpretations respectively. Preserve the source URL or identifier and date.

State what is retained, replaced, removed and added. Transfer a composition or explanation structure,
not a competitor's claim, testimonial, review count or identity. Recompose a non-square reference
onto a square canvas. Do not stretch it, crop away essential information or inherit its ratio.

A source link without an accessible image permits a limited text reading, not invented visual
analysis. Proceed with an original square concept if adaptation is not possible, clearly stating
the limitation; ask for the source image only if faithful adaptation is essential to the request.

## 4. Write the production brief

Use `contracts/static-spec.md`. The brief carries product facts used, main message, exact image copy,
visual hierarchy, identity constraints, reference roles, square dimensions, generation route,
platform copy and CTA if relevant, and checks. Test identifiers and belief maps are unnecessary
outside a requested governed campaign batch.

The image-model prompt is derived from this brief. Give each reference a distinct job: product
identity, composition, style or logo. Product identity and exact copy outrank a decorative reference.
Keep unresolved factual placeholders out of generation prompts and final artwork.

## 5. Generate

Use `connectors/higgsfield.md` for the current tool contract. Honor the user's selected model.
Otherwise use the connector's ordinary image default; both preferred models receive `aspect_ratio:
"1:1"`. Start at the supported 2k resolution for final static ads unless the request requires another
resolution or cost choice. Quality parameters vary by model and must be checked before use.

Choose complete-image generation when integrated typography and image design fit the task. Use
generated imagery with separate exact composition when logos, small text or brand typography need
more control and the host supports that route. Both routes require final verification.

A request to make images authorizes the necessary generation within its count and stated budget.
Do not add approval pauses for routine creative choices. A plan-only request does not authorize
generation. Resolve a provider's explicit payment-choice question before proceeding. Estimate
through the dedicated read-only estimator; never use a generation call as a dry run.

Keep a stable index for each output. Store accepted job IDs, prompts, reference mapping, returned
adjustments and status. Wait on existing jobs. Retry only a failed position, at most once by default,
within authorized cost and scope. Never resubmit pending jobs or rerun successful outputs.

## 6. Verify the finished image

Check actual width equals height, nonempty output, correct product and brand, exact intended words,
legible hierarchy at phone size, supported proof and no unexpected additions. Check returned
parameter adjustments before calling an output complete. A 1:1 prompt does not prove a square file.

The local helper `scripts/validate-image-ad.py` can validate a production record and measure PNG,
JPEG or WebP dimensions with Python's standard library. Vision is still required for product fidelity,
spelling and layout; the helper cannot judge those. Without filesystem access, use available image
metadata and visual inspection and state any check that cannot be completed.

One focused correction is preferable to regenerating the entire batch. Keep the approved source
image and exact changed instruction for revisions. An unresolved product or copy error prevents
verified status. It does not require withholding other successful outputs.

## 7. Deliver and improve

Show the actual final images in requested order. Include useful platform copy and a concise
description of assumptions or material limitations. Prompts and internal checklists should not
dominate the user's result unless requested. Without a generation capability, deliver the exact
brief and prompt and state that the image was not generated.

Where persistence exists, retain `schemas/image-ad-run.schema.json` data beside the outputs. In chat,
the same information can be returned as a compact handoff. Saving a record does not make an ad
approved or launched. Keep generated, verified, approved and launched states distinct.

Customer research, human edits and supplied ad outcomes can improve the next execution. Record
which changed: product fact, voice preference, design choice, operational observation or performance
finding. No clicks or spend means no performance claim; no isolated variable means no causal lesson.
Preserve brand isolation. Use the existing learning system only when authorized to update memory.
