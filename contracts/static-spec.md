# Output Contract: Static and Carousel Spec
locked: 2026-08-27
version: 1.3.0

One spec per static or carousel execution. Complete enough that a designer or an image model
can build it without asking a question.

## Artefact
Markdown. One spec block per asset.

## Sections, in order

1. **Header** - brand, market, product, coordinate key, CONTST test ID, source classification, Who,
   Primary Problem, awareness code and job, messaging route, primary hook, media type, execution
   format from the format library, destination, CTA, complete final ad name ending in `POSTIDXXX`
   before publication, and ratios required
2. **The job** - one line: the belief this asset has to move
3. **Layout** - zone by zone, top to bottom, with what sits in each
4. **Copy on the asset** - every word that appears, with its zone and hierarchy level
5. **Visual direction and production needs** - subject, composition, lighting, palette and type,
   all drawn from the active brand folder's approved visual context, plus people, assets and location
   required
6. **Image-model prompt** - a generation prompt derived from sections 3 to 5, plus the composite
   plan for any copy that must render exactly. Derived, not written separately: if the prompt and the
   spec disagree, the spec is right
7. **Carousel frames** - if carousel, one row per frame with its job and its copy
8. **Proof and claim check** - every proof object and claim required, its evidence ID, approved
   wording and status, covering generated imagery as well as copy
9. **Rationale** - the format chosen and why, the proof used, the objection pre-empted

## Layout rules

- **Ratios:** 4:5 master where the production route allows it, 1:1 otherwise, adapt to 9:16 where the
  placement needs it. 4:5 takes more feed height and the one CTR comparison on record favours it
  (`references/12-meta-platform.md`), so drop to 1:1 as a tool constraint rather than a default. State
  which and why in section 1
- **Safe zones:** keep all copy clear of the platform chrome. Check
  `references/12-meta-platform.md` for the current margins per placement
- **Hierarchy:** exactly one primary line. Everything else is secondary or tertiary
- **Legibility:** the primary line readable at thumbnail size, on a phone, at arm's length

## Opening gate

The primary line, feed object and hierarchy together are the hook, so they clear
`references/20-hook-quality-standard.md` as one unit. Record the result under section 2:

- Opening type: promise or open loop, declared once
- Must-have carriers: which of the primary line, feed object or proof object carries emotion,
  curiosity gap and high stakes, with at least two named and any absent element stated
- Non-negotiables: no prior context, starts in action, no chaos

For a static, `starts in action` means the asset shows the situation or the proof rather than
introducing it. For a carousel, frame one alone clears the gate; the later frames may not be used to
supply context the opening needed. `No chaos` is a hierarchy requirement here: competing type
weights, more than one primary idea or a crowded frame fail the gate whatever the copy says.

## Image-model prompt

When the asset will be generated rather than photographed, section 6 carries the prompt. It is
derived from the spec so there is one source of truth and no hand translation.

For Higgsfield specifically, `connectors/higgsfield.md` has the verified model choice, the aspect
ratio constraint that decides it, and the reference-image handling.

The prompt states subject, composition, camera or rendering style, lighting, palette, type treatment,
aspect ratio and what must be left empty for the safe zones. Palette, type and photography direction
come from `context/visual.md` and are never invented, exactly as for a photographed asset.

**Composite the copy, do not generate it.** Image models render text unreliably, and a headline that
is subtly misspelled will pass review and spend money. Default to generating the image without text
and compositing the copy exactly as specified in section 4. When copy must be generated as pixels,
the spec requires a verification step: read the rendered text character by character against section
4 before the asset ships.

Safe zones survive generation. A generated image that fills the frame edge to edge will lose copy
behind platform chrome, so the prompt reserves the margins from
`references/12-meta-platform.md` rather than trusting a crop afterwards.

### The claim gate covers generated imagery

An image model will produce whatever composition it is asked for, including compositions Meta
prohibits. The claim gate therefore applies to pixels as well as words.

- **No before and after, and no side-by-side body comparison** in health, wellness, beauty or weight
  management. `references/12-meta-platform.md` §2.1 has the current policy text. An image model will
  generate this construction on request and it is a rejection, not a warning.
- No generated person implied to be a real customer, and no generated result implied to be a real
  outcome. A synthetic face next to a testimonial is an invented testimonial.
- No generated proof object: a fabricated award badge, press logo, review screenshot, certification
  mark or lab document is invented proof and prohibited outright.
- No generated depiction of a claim the brand cannot make in words. If the copy cannot say it, the
  picture cannot show it happening.
- A generated depiction of the product must match the product as it actually is. Restyling the
  packaging or the contents is a factual misrepresentation.

Record each generated asset's policy risk in section 8 alongside the copy claims, with the
prohibition it was checked against.

## Counts

- Primary line: 1
- Secondary lines: 0 to 3
- Total words on a single static: 25 or fewer, unless the format is listicle, comparison or
  advertorial, which may go to 60
- Carousel frames: 3 to 8, each with one job

## Formatting rules

- Every copy line specified exactly as it will appear, including capitalisation
- Every visual instruction specific enough to execute
- No em dashes
- Palette, type and photography direction come from `context/visual.md`, never invented

## Never

- More than one primary line
- A generated before and after, or a generated side-by-side body comparison
- A generated face, result, award badge, press logo or review screenshot presented as real
- Copy generated as pixels without a character-by-character verification against the spec
- An image-model prompt written separately from the spec rather than derived from it
- An opening that assumes prior context, or a carousel whose first frame needs frame two to land
- A promise and an open loop mixed into one primary line
- A crowded frame standing in for a reason to stop
- Copy that only works if the reader zooms
- A comparison table with an unfair or unsubstantiated column
- Invented review text, star counts or press logos
- Platform chrome mimicry that could be mistaken for a real interface

## Self-check before presenting

- [ ] Exactly one primary line
- [ ] Opening type declared as promise or open loop
- [ ] At least two must-have carriers named, and any absent element stated
- [ ] Primary line reads cold with no prior context, and frame one lands alone
- [ ] The asset or the destination cashes what the primary line opened
- [ ] Word count inside the limit for the format
- [ ] All copy clear of safe zones in every ratio
- [ ] Every visual value traces to the active brand folder's visual context
- [ ] Any image-model prompt is derived from the spec and agrees with it
- [ ] Generated imagery cleared against the prohibited constructions, and the risk recorded
- [ ] Any copy rendered as pixels verified character by character against section 4
- [ ] Safe-zone margins reserved in the prompt, not left to a later crop
- [ ] Every claim in the claim check, covering imagery as well as words
- [ ] Carousel frames each carry one job
- [ ] Readable at thumbnail
- [ ] Header carries CONTST, source, Who, Primary Problem, awareness job and messaging route
- [ ] Primary hook, media type, execution format, proof, destination and CTA agree
- [ ] People, assets and location required are explicit
- [ ] Complete final ad name uses the full ad-set name and ends in POSTIDXXX before publication
