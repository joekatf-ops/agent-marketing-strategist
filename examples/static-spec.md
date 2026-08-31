# Frozen Example: Static Spec

The PRA execution from `CONTST004`, the second of the four ads in the batch. Read it alongside
`examples/video-script.md` and `examples/ad-copy.md`, which cover the SLA execution: the same
coordinate, a different awareness job.

## 1. Header

- Brand: Fieldnote Carry
- Market: Australia
- Product: SnapGrid Cable Pouch
- Coordinate key: `remote-workers__cable-search`
- CONTST test ID: `CONTST004`
- Source: NNT
- Who: remote workers who carry charging gear between home and shared workspaces
- Primary Problem: finding the required cable means searching through a mixed pouch
- Awareness code and job: PRA, diagnosis
- Messaging route: reframe
- Primary hook: "Packed is not the same as easy to find"
- Media type: STATIC
- Execution format: Text-led product image
- Destination: `LP`, `https://fieldnotecarry.example/pages/cable-search`
- CTA: Learn More
- Complete final ad name:
  `CONTST004_NNT_REMOTE_WORKERS_CABLE_SEARCH_PRA_STATIC_LP_POSTIDXXX`
- Ratios required: 1:1 and 4:5 master, 9:16 adaptation

## 2. The job

Name the problem precisely enough that the reader recognises it as theirs. A PRA reader knows the
pouch annoys them and has not articulated why.

### Opening gate

- Opening type: promise. The line states the whole idea, and the image proves it in the same glance
- Must-have carriers:
  - Emotion: recognition, carried by the primary line naming a state the reader has been in
  - Curiosity gap: narrow. Deliberate: at PRA the diagnosis is the payload, not a withheld answer
  - High stakes: absent. Stated rather than hidden, and accepted for a diagnosis ad
- Non-negotiables: no prior context, because the line needs no product knowledge. Starts in action,
  because the image is the failure state rather than an introduction to it. No chaos, one primary
  line over one photograph

For a static, `starts in action` means the asset shows the situation rather than introducing it. The
frame is a packed pouch mid-search, not a product on white.

## 3. Layout

| Zone | Contents |
|---|---|
| Top 14 percent | Empty. Reserved for platform chrome |
| Upper third | Primary line, two lines of type, left aligned |
| Middle half | Photograph: an ordinary pouch open on a desk, six cables tangled, one hand pushing them aside |
| Lower third | SnapGrid open beside it, cables in fixed loops, visible at a glance |
| Bottom 6 percent | Empty. Reserved for platform chrome |

The two pouches are the argument. No arrows, no labels, no tick and cross.

## 4. Copy on the asset

| Text | Zone | Hierarchy |
|---|---|---|
| Packed is not the same as easy to find | Upper third | Primary |
| See your cables at a glance | Lower third, above the product | Secondary |

Two lines. Twelve words total, inside the 25 word limit for a single static.

## 5. Visual direction and production needs

All values from `context/visual.md`, none invented.

- Subject: two pouches on the same desk, same light, shot from directly overhead
- Composition: ordinary pouch upper, SnapGrid lower, equal frame share, no size advantage
- Lighting: single soft key from the left, as in the brand's approved product photography
- Palette: approved neutral desk, no colour grading beyond the brand's standard
- Type: brand primary weight for the primary line, regular for the secondary
- People, assets and location: one hand model, both pouches, two matched sets of six cables, neutral
  desk, overhead rig

## 6. Image-model prompt

Only if the asset is generated rather than photographed. Derived from sections 3 to 5. Where the
prompt and the spec disagree, the spec is right.

```
Overhead product photograph, two open cable pouches on a plain light neutral desk, shot from
directly above, single soft key light from the left, no colour grading. Upper half: an ordinary
fabric cable pouch, six charging cables tangled together, one hand pushing them aside. Lower half:
a second pouch of equal frame size, six charging cables each held in its own elastic loop behind a
transparent mesh divider, all six visible. Equal frame share for both pouches, no size advantage.
No text, no labels, no arrows, no tick or cross marks, no logos. Leave the top 14 percent and the
bottom 6 percent of the frame empty. 4:5 aspect ratio.
```

Copy is composited, not generated. Both lines in section 4 are laid over the finished image using the
brand's type, because a generated headline can be subtly misspelled and will still pass review. If
either line ever has to be rendered as pixels, read it character by character against section 4
before the asset ships.

Safe zones are reserved in the prompt rather than cropped afterwards, so the primary line cannot end
up behind platform chrome.

### Generated imagery check

| Prohibited construction | Present | Note |
|---|---|---|
| Before and after | No | Two products side by side, not one subject across time |
| Side-by-side body comparison | No | No person or body part beyond one hand |
| Generated person implied to be a customer | No | Hand only, no face, no testimonial adjacency |
| Generated proof object | No | No award badge, press logo, review screenshot or certification mark |
| Depiction of an unmakeable claim | No | Shows only the divider and loops, which are `EVD-PROD-001` |
| Product misrepresented | No | Six loops and one divider, matching the shipped product |

Policy risk: LOW. The comparison is between two products, not two states of a person, so the health
and beauty prohibitions in `references/12-meta-platform.md` §2.1 do not bite. A version of this ad
showing a tidy desk against an untidy one would still be fine; a version showing a person before and
after would not.

## 7. Carousel frames

Not a carousel.

## 8. Proof and claim check

| Claim or proof | Evidence ID | Approved wording | Status |
|---|---|---|---|
| Transparent mesh divider and six elastic loops | `EVD-PROD-001` | as written | VERIFIED |
| "See your cables at a glance." | `EVD-CLAIM-006` | exact wording required | APPROVED for AU |
| Readers experience the searching state | `EVD-MKT-022` | market evidence, 21 comments | PRESENT, market evidence only |
| Generated or photographed imagery | this section | checked against section 6 | CLEARED, LOW risk |

Prohibited and absent: waterproof, indestructible, fits every charger, prevents forgetting, any
customer result, any prevalence claim about how common the problem is.

## 9. Rationale

Text-led product image because the PRA job is diagnosis, and a diagnosis is a sentence. The
photograph does not have to sell the product; it has to make the sentence land as true.

The reframe route is carried by the primary line alone. "Packed is not the same as easy to find"
separates two things the reader had merged, which is the whole diagnosis, and the image supplies the
evidence in the same glance.

Both pouches get equal frame share deliberately. An unfair comparison would be the fastest way to
lose the argument with a reader who owns the ordinary pouch, and it would breach the fair-comparison
requirement on the claim gate.

No high stakes, stated rather than hidden. A diagnosis ad that manufactures urgency reads as a
different awareness state and stops being a diagnosis.

`references/08-formats.md` puts text-only statics at the highest hit rate of any asset type, more
than twice baseline, with the standing caveat that hit rate is a spend-concentration measure rather
than a return. This is text-led over a photograph rather than text-only, chosen because the reframe
needs visible evidence and a pure text card would leave the primary line unsupported.
