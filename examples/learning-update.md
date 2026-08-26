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

| Before | After | Edit reason | Normalized learning | Memory key |
|---|---|---|---|---|
| "Never lose another charging cable." | "See your charging cables at a glance." | The original promised a behaviour outcome the product cannot guarantee | Never promise that SnapGrid prevents lost or forgotten cables | `claims.snapgrid.loss_prevention` |
| "Six dedicated slots for every cable." | "Six elastic cable loops." | "Every cable" exceeded the verified fit claim | Describe SnapGrid as having six elastic cable loops | `product.snapgrid.cable_loops` |
| "Upgrade your setup today." | "See how SnapGrid is laid out." | The educational ad should match the product-page destination | Match educational CTA language to the information available at the destination | `cta.educational_destination_match` |
| "small, sleek and smart" | "compact" | Style tightening only | No durable learning | Not recorded |

## 3. Learning events recorded

| Event ID | Before | After | Edit reason | Normalized learning | Memory key | Classification | Scope | Status | Recorded by | Approved by | Confidence | Destination |
|---|---|---|---|---|---|---|---|---|---|---|---:|---|
| LEARN-20260826A | Never lose another charging cable. | See your charging cables at a glance. | Remove an unsupported guaranteed outcome | Never promise that SnapGrid prevents lost or forgotten cables | `claims.snapgrid.loss_prevention` | compliance_correction | product | approved | Joe | Joe | 1.00 | `learning/learning-events.jsonl` |
| LEARN-20260826B | Six dedicated slots for every cable. | Six elastic cable loops. | Stay inside verified product fit | Describe SnapGrid as having six elastic cable loops | `product.snapgrid.cable_loops` | factual_correction | product | approved | Joe | Joe | 1.00 | `learning/learning-events.jsonl` |
| LEARN-20260826C | Upgrade your setup today. | See how SnapGrid is laid out. | Match CTA language to an educational destination | Match educational CTA language to the information available at the destination | `cta.educational_destination_match` | strategic_learning | execution | proposed | Joe | Not approved | 0.75 | `learning/learning-events.jsonl` |

### Machine-copyable events

```json
{
  "event_id": "LEARN-20260826A",
  "brand_slug": "fieldnote-carry",
  "market": "AU",
  "product_id": "snapgrid-pouch",
  "source_asset_id": "FC-AD-017",
  "before": "Never lose another charging cable.",
  "after": "See your charging cables at a glance.",
  "reason": "Remove an unsupported guaranteed outcome.",
  "learning": "Never promise that SnapGrid prevents lost or forgotten cables.",
  "memory_key": "claims.snapgrid.loss_prevention",
  "scope": "product",
  "classification": "compliance_correction",
  "status": "approved",
  "confidence": 1.0,
  "author": "Joe",
  "approved_by": "Joe",
  "timestamp": "2026-08-26T11:42:00+10:00"
}
```

```json
{
  "event_id": "LEARN-20260826B",
  "brand_slug": "fieldnote-carry",
  "market": "AU",
  "product_id": "snapgrid-pouch",
  "source_asset_id": "FC-AD-017",
  "before": "Six dedicated slots for every cable.",
  "after": "Six elastic cable loops.",
  "reason": "Stay inside verified product fit.",
  "learning": "Describe SnapGrid as having six elastic cable loops.",
  "memory_key": "product.snapgrid.cable_loops",
  "scope": "product",
  "classification": "factual_correction",
  "status": "approved",
  "confidence": 1.0,
  "author": "Joe",
  "approved_by": "Joe",
  "timestamp": "2026-08-26T11:42:00+10:00"
}
```

```json
{
  "event_id": "LEARN-20260826C",
  "brand_slug": "fieldnote-carry",
  "market": "AU",
  "product_id": "snapgrid-pouch",
  "source_asset_id": "FC-AD-017",
  "before": "Upgrade your setup today.",
  "after": "See how SnapGrid is laid out.",
  "reason": "Match CTA language to an educational destination.",
  "learning": "Match educational CTA language to the information available at the destination.",
  "memory_key": "cta.educational_destination_match",
  "scope": "execution",
  "classification": "strategic_learning",
  "status": "proposed",
  "confidence": 0.75,
  "author": "Joe",
  "timestamp": "2026-08-26T11:42:00+10:00"
}
```

## 4. Immediate memory changes

- `active-memory.json` now contains the approved rule: never promise that SnapGrid prevents lost or
  forgotten cables.
- `active-memory.json` now contains the approved product fact: describe SnapGrid as having six
  elastic cable loops unless a later verified event supersedes it.

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
