# Output Contract: Destination Handoff
locked: 2026-08-27
version: 1.0.0

The ad-to-page continuity record for one execution. It gives the page owner everything needed to
continue the ad's argument after the click and makes deliberate destination exceptions auditable.

## Artefact

Markdown document with one handoff card per ad.
`destination-handoff-BRAND-CONTST###-YYYYMMDD.md`

## Sections, in order

1. **Execution identity** - brand, market, product, coordinate key, CONTST test ID, source, Who,
   Primary Problem, awareness code and job, messaging route, primary hook, media type, execution
   format, CTA and complete final ad name ending in `POSTIDXXX` before publication
2. **Destination decision** - default destination code and URL, selected controlled destination
   token and final URL, DEFAULT or EXCEPTION status, rationale, evidence and approval owner
3. **Ad promise** - exact opening promise, problem framing, mechanism, proof, offer language,
   objection handled and expectation created by the CTA
4. **Required page continuation** - first-screen promise, Who recognition, problem language,
   mechanism, proof, claim qualifiers, offer, CTA and next step the destination must carry
5. **Message-match map** - every load-bearing ad element mapped to the page element and location that
   continues it
6. **Proof and claim gate** - proof and claims required, evidence IDs, approved wording, qualifiers,
   prohibited extrapolations and market status
7. **Page production needs** - copy, design, people, assets, location or product imagery, tracking,
   technical owner, content owner and due date
8. **Preflight result** - URL status, mobile rendering, speed, stock, price, shipping, offer,
   checkout, tracking and approval result
9. **Risks and unresolved gaps** - consequence, owner and blocking status

## Default destination rules

| Awareness code | Job | Default destination |
|---|---|---|
| UWA | Recognition | LP |
| PRA | Diagnosis | LP |
| SLA | Differentiation | PDP |
| PDA | Decision | PDP |

LP is a landing page and PDP is a product-detail page. HP is homepage and CP is collection page.
The default is a routing rule, not permission to use a generic page. The actual page must continue
the selected execution's Who, Primary Problem, messaging route, proof and CTA.

## Deliberate destination exception

Every deliberate deviation must select exactly one controlled destination token: LP, PDP, HP or CP,
and is allowed only when it remains congruent. Record:

1. awareness code and default destination;
2. selected controlled destination token and final URL;
3. why the default is unsuitable;
4. how the selected page continues the exact promise, proof and CTA;
5. supporting evidence and known risk;
6. page changes required before launch;
7. approver, approval date and review trigger.

An unexplained URL swap is not an exception. A page that cannot be accurately represented by LP,
PDP, HP or CP is also invalid. Either case blocks launch.

## Message-match map, fixed row shape

| Ad element | Exact ad language or object | Required page continuation | Page location | Status | Gap and action | Owner |
|---|---|---|---|---|---|---|

Required rows: Who recognition, Primary Problem, messaging route, primary hook promise, mechanism,
proof, claim qualifier, offer where used and CTA next step.

## Hard rules

- Do not make the page promise stronger than the approved ad claim or its evidence.
- Do not send a recognition or diagnosis execution to a page whose first screen assumes product-ready intent.
- Do not send a differentiation or decision execution to a page that hides the mechanism, proof or product.
- Preserve exact price, offer, shipping, guarantee and availability truth across ad and page.
- Record deliberate destination exceptions before the Campaign Launch Plan is marked ready.
- Map every default and exception to exactly one controlled destination token: LP, PDP, HP or CP.
- This is a production handoff and manual preflight. It does not edit or publish the destination.

## Self-check before presenting

- [ ] The execution identity carries the complete traceability set
- [ ] UWA and PRA default to LP; SLA and PDA default to PDP
- [ ] Every exception records reason, congruence, evidence, risk and approval
- [ ] Every default and exception uses exactly one controlled destination token
- [ ] Every load-bearing ad element has a page continuation and owner
- [ ] Claims, qualifiers, offer and CTA agree across ad and page
- [ ] URL, mobile page, tracking, stock, price, shipping and checkout are verified manually
- [ ] Any blocking gap prevents launch readiness
