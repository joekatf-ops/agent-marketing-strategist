# Output Contract: Creative Audit
locked: 2026-08-27
version: 1.0.0

A pre-launch or creative-only review of supplied first-party ads against the selected brand's truth,
strategy and destination. It evaluates execution readiness without predicting performance.

## Artefact

Markdown report. `creative-audit.md` in the active ad-analysis run folder.

## Sections, in order

1. **Input coverage and limitations** - input-readiness status, the completed input audit, every
   supplied source and ad, unavailable material, evidence versions and the permitted scope
2. **Ad identity and traceability** - ad identifier, asset source, coordinate, CONTST and production
   fields that are supplied, plus every missing or conflicting identity field
3. **Who x Primary Problem clarity** - whether each complete execution communicates one traceable
   Who and one Primary Problem without inventing an absent coordinate
4. **Awareness job and messaging route** - the supplied or evidenced awareness job, the persuasive
   route and whether the execution performs them coherently
5. **Hook coherence and body handoff** - opening claim or visual, dominant idea, body progression
   and whether the opening promise is carried through
6. **Proof, offer, claims and CTA** - supplied proof, exact offer, claim ceiling, substantiation,
   CTA and any compliance gate
7. **Format, visual communication and production execution** - legibility, hierarchy, pacing,
   audio dependence, demonstration, asset completeness and production defects visible in the
   supplied material
8. **Destination continuity** - whether the supplied destination continues the promise, proof,
   offer and CTA; mark this unavailable when destination evidence was not supplied
9. **Ranked issues with evidence** - issues ordered by severity, each tied to supplied evidence and
   an exact revision rather than generic advice
10. **Pre-launch outcome by ad** - exactly one governed creative outcome per supplied ad
11. **What cannot be concluded without performance data** - the performance questions this audit
    cannot answer and the material needed to answer them

## Pre-launch outcome, fixed row shape

| Ad | Outcome | Blocking or revision issue | Evidence | Exact change | Owner |
|---|---|---|---|---|---|

`Outcome` contains exactly one literal value: `ready`, `revise` or `block`.

- `ready`: no material creative-readiness issue is evidenced in the supplied scope.
- `revise`: the ad is reviewable, but one or more evidenced execution issues need an exact change.
- `block`: missing creative, unsafe claims or another evidenced stop condition prevents approval.

These are per-ad Creative Audit outcomes. They are distinct from input readiness
`ready | limited | blocked` and from Performance Diagnosis actions.

## Ranked issue, fixed row shape

| Rank | Ad | Issue | Severity | Evidence | Exact change | Owner |
|---|---|---|---|---|---|---|

Zero ranked issues is valid when the supplied evidence supports no change.

## Hard rules

1. Begin with the deterministic input audit and its input-readiness status. A blocked ad is not
   reconstructed from assumptions
2. Audit every supplied ad and keep findings tied to its source IDs and supplied fields
3. Preserve the active brand, market, product, evidence version and approved-learning version
4. Use only supplied creative, selected-brand truth and cited evidence. Missing fields remain
   unavailable, not inferred
5. Separate coordinate quality from execution quality. Do not rewrite Who or Primary Problem merely
   to repair a weak execution
6. Treat competitor ads as competitor research, not as first-party Creative Audit material
7. Use one dominant idea per ad and assess the full hook-to-body-to-destination argument
8. Apply the selected brand's claim ceiling. A claim lacking required approval or substantiation
   produces `block`
9. Give exact, local revisions. Do not prescribe generic best practice
10. Creative Audit cannot assign `keep`, `ITR`, `stop` or `scale`; those belong only to Performance
    Diagnosis with adequate supplied performance data
11. Absent metrics prohibit claims about winning, conversion, CAC or scaling. Creative readiness is
    not a performance forecast

## Self-check before presenting

- [ ] The eleven sections appear once and in order
- [ ] The input audit and input-readiness label appear before findings
- [ ] Every supplied ad has exactly one `ready`, `revise` or `block` outcome
- [ ] Every issue cites supplied evidence and gives an exact change and owner
- [ ] Missing strategic, destination or production evidence is named rather than invented
- [ ] Claims and compliance follow the selected brand's approved ceiling
- [ ] The report contains no performance prediction or Performance Diagnosis action
- [ ] Section 11 states the limits created by absent or inadequate metrics
