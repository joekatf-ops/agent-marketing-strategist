# Frozen Example: Creative Audit

## 1. Input coverage and limitations

- Run: `ADR-20260827-014`
- Brand: `quiet-arc`
- Market: `AU`
- Product: `folding-reading-lamp`
- Method version: `0.4.0`
- Evidence version: unavailable; not supplied by the frozen intake or a frozen brand bundle
- Approved-learning version: unavailable; not supplied by the frozen intake or a frozen brand bundle
- Requester: Mina Cole
- Input readiness: `limited`
- Ads audited: `AD-QA-001`, `AD-QA-002`
- Creative sources: `SRC-QA-001`, `SRC-QA-002`
- Destination evidence: `SRC-QA-003`
- Performance material: not supplied
- Limitations: awareness job and messaging route are explicit nulls in the intake; attachment
  hashes are absent; attachment and screenshot contents are not frozen inputs. Findings below stay
  within the supplied identifiers, copy, coordinate keys, destination URL and source labels.

## 2. Ad identity and traceability

| Ad | Creative source | Coordinate key | Destination | Traceability finding |
|---|---|---|---|---|
| `AD-QA-001` | `SRC-QA-001` | `night-readers__shared-room-glare` | PDP URL in intake | Ad, asset, coordinate and destination are linked |
| `AD-QA-002` | `SRC-QA-002` | `night-readers__shared-room-glare` | PDP URL in intake | Ad, asset, coordinate and destination are linked |

CONTST, source and Post ID are explicit nulls in the frozen intake, so none are inferred.

## 3. Who x Primary Problem clarity

- `AD-QA-001`: the supplied line "Read one more chapter without lighting the whole room" makes the
  intended reader and shared-room light problem legible and agrees with the supplied coordinate.
- `AD-QA-002`: the supplied primary text introduces bedtime softness, desk tidiness and reading
  light as three competing problems. The supplied coordinate names only shared-room glare, so the
  execution does not hold one clear problem.

## 4. Awareness job and messaging route

The intake supplies explicit nulls for governed awareness job and messaging route for both ads. This section
therefore checks coherence only and does not assign missing strategy fields.

- `AD-QA-001`: the page-light contrast is coherent from primary text to headline.
- `AD-QA-002`: no single persuasive route dominates the three promises in the supplied text.

## 5. Hook coherence and body handoff

- `AD-QA-001`: "Read one more chapter" opens on the reading situation; "without lighting the whole
  room" names the tension; the folding-light sentence supplies the product handoff; the headline
  repeats the same contrast.
- `AD-QA-002`: each short sentence opens a new promise, while the headline broadens again to
  "changes your evenings". The supplied copy never selects one hook for the body to carry.

## 6. Proof, offer, claims and CTA

| Ad | Supplied support | Offer | Claim risk | CTA |
|---|---|---|---|---|
| `AD-QA-001` | The folding-light statement is present in the supplied primary text | None supplied | Brand substantiation and claim ceiling are unavailable | `Shop Now` |
| `AD-QA-002` | No support is supplied for the three broad benefit statements | None supplied | Brand substantiation and claim ceiling are unavailable | `Shop Now` |

## 7. Format, visual communication and production execution

Visual conclusions: unavailable; attachment contents are not frozen inputs. The intake inventories
`SRC-QA-001` and `SRC-QA-002` by label, but supplies neither content nor hashes that could support a
frozen visual or production finding.

## 8. Destination continuity

Destination continuity: unavailable; the screenshot contents are not frozen inputs. The intake
supplies the PDP URL and the `SRC-QA-003` screenshot label, but not page or screenshot content from
which to assess promise, proof, offer or CTA continuity.

## 9. Ranked issues with evidence

| Rank | Ad | Issue | Severity | Evidence | Exact change | Owner |
|---|---|---|---|---|---|---|
| 1 | `AD-QA-002` | Three competing promises obscure the supplied coordinate | Material revision | Supplied primary text and headline | Replace the three-promise opening with "Read without lighting the whole room" and use headline "Light the page, not the room" | unassigned |

## 10. Pre-launch outcome by ad

| Ad | Outcome | Blocking or revision issue | Evidence | Exact change | Owner |
|---|---|---|---|---|---|
| `AD-QA-001` | `ready` | None within the reviewable supplied copy scope; visual and destination conclusions remain unavailable | Supplied primary text and headline | None | unassigned |
| `AD-QA-002` | `revise` | Supplied copy divides attention across three promises | Supplied primary text and headline | Use the single page-light contrast specified in ranked issue 1 | unassigned |

## 11. What cannot be concluded without performance data

This audit establishes only creative readiness within the frozen intake. It does not establish how
either ad affected audience response, purchase behaviour or unit economics. Those questions require
a complete supplied performance pack and the Ad Diagnosis contract.
