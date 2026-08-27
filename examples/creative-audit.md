# Frozen Example: Creative Audit

## 1. Input coverage and limitations

- Run: `ADR-20260827-014`
- Brand: Quiet Arc (`quiet-arc`)
- Market: Australia (`AU`)
- Product: Folding Reading Lamp (`folding-reading-lamp`)
- Method version: `0.4.0`
- Input readiness: `limited`
- Ads audited: `AD-QA-001`, `AD-QA-002`
- Creative sources: `SRC-QA-001`, `SRC-QA-002`
- Destination evidence: `SRC-QA-003`
- Performance material: not supplied
- Limitations: awareness job and messaging route are not structured in the intake; attachment
  hashes are absent. Findings below stay within the supplied creative, copy and page screenshot.

## 2. Ad identity and traceability

| Ad | Creative source | Coordinate key | Destination | Traceability finding |
|---|---|---|---|---|
| `AD-QA-001` | `SRC-QA-001` | `night-readers__shared-room-glare` | PDP URL in intake | Ad, asset, coordinate and destination are linked |
| `AD-QA-002` | `SRC-QA-002` | `night-readers__shared-room-glare` | PDP URL in intake | Ad, asset, coordinate and destination are linked |

No CONTST or production-record fields are present in the frozen intake, so none are inferred.

## 3. Who x Primary Problem clarity

- `AD-QA-001`: the supplied line "Read one more chapter without lighting the whole room" makes the
  intended reader and shared-room light problem legible and agrees with the supplied coordinate.
- `AD-QA-002`: the supplied primary text introduces bedtime softness, desk tidiness and reading
  light as three competing problems. The supplied coordinate names only shared-room glare, so the
  execution does not hold one clear problem.

## 4. Awareness job and messaging route

The intake does not supply a governed awareness job or messaging route for either ad. This section
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
| `AD-QA-001` | Folding light is stated in intake copy and shown in `SRC-QA-001` | None supplied | Descriptive product demonstration only | `Shop Now` |
| `AD-QA-002` | No support is supplied for the three broad benefit statements | None supplied | Broad claims need narrowing to the demonstrated page-light use | `Shop Now` |

## 7. Format, visual communication and production execution

- `AD-QA-001`: `SRC-QA-001` shows the lamp folded toward the open page while the room remains outside
  the primary lit area. The visual supports the single contrast in the supplied copy. No visible
  blocking production defect appears in the supplied attachment.
- `AD-QA-002`: `SRC-QA-002` divides the frame between a bed, a desk and an open book. Three equal
  visual regions repeat the copy's split focus and leave no dominant reading path.

## 8. Destination continuity

`SRC-QA-003` shows the same folding lamp, the headline "Light the page, not the room" and a
`Shop Now` control on the supplied PDP screenshot.

- `AD-QA-001`: promise, demonstrated mechanism and CTA continue into the supplied destination.
- `AD-QA-002`: the destination supports page-focused light, but not the separate cleaner-desk and
  softer-bedtime promises in the ad copy.

## 9. Ranked issues with evidence

| Rank | Ad | Issue | Severity | Evidence | Exact change | Owner |
|---|---|---|---|---|---|---|
| 1 | `AD-QA-002` | Three competing promises obscure the supplied coordinate | Material revision | Primary text, headline and `SRC-QA-002` | Replace the three-promise opening with "Read without lighting the whole room"; use one page-light visual and headline "Light the page, not the room" | Copy lead and designer |

## 10. Pre-launch outcome by ad

| Ad | Outcome | Blocking or revision issue | Evidence | Exact change | Owner |
|---|---|---|---|---|---|
| `AD-QA-001` | `ready` | None within supplied scope | Primary text, headline, `SRC-QA-001`, `SRC-QA-003` | None | Mina Cole |
| `AD-QA-002` | `revise` | Copy and visual divide attention across three promises | Primary text, headline, `SRC-QA-002`, `SRC-QA-003` | Use the single page-light contrast specified in ranked issue 1 | Copy lead and designer |

## 11. What cannot be concluded without performance data

This audit establishes only creative readiness within the frozen intake. It does not establish how
either ad affected audience response, purchase behaviour or unit economics. Those questions require
a complete supplied performance pack and the Ad Diagnosis contract.
