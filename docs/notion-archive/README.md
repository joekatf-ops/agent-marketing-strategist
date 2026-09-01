# Notion archive

Export of the Master Creative Strategy hub and its subpages, fetched from the 27 August 2026
snapshot and written on 31 August 2026. Twelve pages were exported, totalling 7,039 words. Eleven
are here, with brand names redacted. One was removed. See [What was redacted](#what-was-redacted).

Nothing here is loaded by the agent. It is a record, kept so the migration is auditable and so
nothing is lost now that the repository rather than Notion is canonical for the universal method.

## Why it exists

`references/18-master-creative-strategy.md` used to declare the Notion hub canonical and this
repository its reviewed snapshot. That created a standing synchronisation cost with no benefit,
since the method has one author and the repository is where it is loaded, versioned, tested and
shipped. The rule was retired and the content moved here.

## What was integrated, and what was not

Most of this material was already in the reference library, because the library was derived from
these pages. The audit of what was missing found one genuine gap: **the commercial layer.** Across
the whole of `references/`, contribution margin, payback period, LTV, product-market fit,
segmentation and conversion-rate optimisation each appeared zero times.

That gap is now `references/23-commercial-context.md`, which carries the unit economics, fit signals,
segmentation and jobs-to-be-done, offer levers, conversion diagnosis, channels, the four measurement
levels, retention and the ethics principles. It is condensed and rewritten into the library's style
rather than copied, because a verbatim paste would have contradicted files that already cover
awareness, formats and naming in more detail.

| Notion page | Where it lives now |
|---|---|
| 00. Marketing Fundamentals | `references/23-commercial-context.md` for the commercial half. The persuasion and awareness halves were already in `01-foundations.md` and `02-customer-state.md` |
| 01. Research and Strategic Inputs | `references/11-research-tools.md`, `13-brand-folder.md` |
| 02. Core Concept Framework | `references/06-concept-model.md` |
| 03. Awareness and Creative Execution | `references/02-customer-state.md`, `08-formats.md` |
| 04. Creative Sources: NNT, INSPO, ITR | `references/06-concept-model.md` |
| 05. Meta Campaign and Ad Set Structure | `invariants.yml`, `contracts/campaign-launch-plan.md` |
| 06. Naming Conventions | `references/07-naming.md`, `invariants.yml` |
| 07. Testing, Measurement and Decisions | `references/09-testing-and-diagnosis.md`, plus the measurement levels in `23-commercial-context.md` |
| 08. Advertising and Messaging Frameworks | `references/04-persuasion.md`, `05-copy-craft.md` |
| 09. Formats and Production Guidance | `references/08-formats.md` |
| 10. Worked Example | Not integrated, then removed. Brand-specific, and the repository is deliberately brand-neutral. It belongs in a brand folder |

## What was redacted

This was a verbatim export until 1 September 2026. It is no longer, and that is deliberate: the
repository is brand-agnostic, and the exported hub named a real client brand. A record that is
quietly edited is worth less than one that declares its own edits, so they are listed here rather
than absorbed.

- **Page 10, a brand-specific worked example, was removed in full.** It illustrated the concept
  coordinate, the four-ad batch and the naming registers through one brand's product, Who and daily
  budget. Its own closing note told the reader not to copy any of that into another brand, which is
  the argument for keeping it in a brand folder rather than here. What it demonstrated about the
  method is already documented brand-neutrally in `references/06-concept-model.md` and
  `references/07-naming.md`, so nothing was lost with it.
- **Four brand-name mentions were replaced,** in `hub.md`, `00-marketing-fundamentals.md` and
  `01-research-and-strategic-inputs.md`. Two were prose, now `[brand name redacted]`. Two were
  page-list entries pointing at the removed page, now pointing here. Surrounding wording is
  untouched, and both prose mentions happen to state that core documentation stays brand-neutral,
  which is the rule being applied to them.

Nothing else was altered. `MANIFEST.md` still records all twelve exported pages against their Notion
page ids, with the removed one marked, so it remains traceable to its source.

## One conversion note

Notion's markdown rendering had turned the underscore-delimited naming templates on page 06 into
italics, emitting `[BRAND]*[PRODUCT]*` where the page reads `[BRAND]_[PRODUCT]_`. The underscores were
restored and those lines wrapped in code spans. Beyond that and the redactions above, no wording was
changed, including small source quirks that were left as they were.
