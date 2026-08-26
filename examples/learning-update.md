# Frozen Example: Learning Update

## 1. Source revision

- Brand: Fieldnote Carry
- Market: Australia
- Product: SnapGrid Cable Pouch
- Asset ID: FC-AD-017
- Generated version: `outputs/copy/FC-AD-017-v1.md`
- Approved version: `outputs/copy/FC-AD-017-v2-approved.md`
- Editor: Joe
- Approved: 2026-08-26 11:42 AEST

## 2. Meaning-level changes

| Before | After | Reason |
|---|---|---|
| "Never lose another charging cable." | "See your charging cables at a glance." | The original promised a behaviour outcome the product cannot guarantee |
| "Six dedicated slots for every cable." | "Six elastic cable loops." | "Every cable" exceeded the verified fit claim |
| "Upgrade your setup today." | "See how SnapGrid is laid out." | The educational ad should match the product-page destination |
| "small, sleek and smart" | "compact" | Style tightening only; no durable lesson |

## 3. Learning events recorded

| Event ID | Before | After | Reason | Classification | Scope | Status | Confidence | Destination |
|---|---|---|---|---|---|---|---:|---|
| LEARN-20260826A | Never lose another charging cable. | See your charging cables at a glance. | Remove an unsupported guaranteed outcome | compliance_correction | product | approved | 1.00 | `learning/events/2026/08/LEARN-20260826A.json` |
| LEARN-20260826B | Six dedicated slots for every cable. | Six elastic cable loops. | Stay inside verified product fit | factual_correction | product | approved | 1.00 | `learning/events/2026/08/LEARN-20260826B.json` |
| LEARN-20260826C | Upgrade your setup today. | See how SnapGrid is laid out. | Match CTA language to an educational destination | strategic_learning | execution | proposed | 0.75 | `learning/events/2026/08/LEARN-20260826C.json` |

## 4. Immediate memory changes

- Product rule approved: never promise that SnapGrid prevents lost or forgotten cables.
- Product fact approved: use "six elastic cable loops" unless a later verified specification supersedes it.

## 5. Signals retained but not promoted

- The softer educational CTA is stored as one execution-level signal. It does not yet establish a
  brand-wide CTA preference.

## 6. Non-learning edits

- Replacing three adjectives with "compact" is a one-off style tightening. It is not stored as a
  voice rule.

## 7. Conflicts

No approved-rule conflicts were found.

## 8. Next-run effect

- All future SnapGrid copy in Australia will reject guaranteed loss-prevention wording.
- Product copy will use the verified six-loop description.
- Educational CTAs may be proposed for similar executions, but are not mandatory.
- No rule was created for other Fieldnote Carry products or other brands.
