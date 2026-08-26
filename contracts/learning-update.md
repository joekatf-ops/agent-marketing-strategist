# Output Contract: Learning Update
locked: 2026-08-26
version: 1.0.0

The audit trail produced after a human edits or approves strategist work.

## Sections, in order

1. **Source revision** - brand, market, product, asset ID, generated version, approved version,
   editor, approver, approval timestamp
2. **Meaning-level changes** - one row per material change, including before, after, edit reason,
   normalized learning and memory key
3. **Learning events recorded** - event ID, classification, scope, status, confidence, and file
4. **Immediate memory changes** - active rules and insights projected into `active-memory.json`
5. **Signals retained but not promoted** - preferences, strategic signals, execution notes, and why
6. **Non-learning edits** - typo fixes, formatting changes, accidental deletions, or same-meaning edits
7. **Conflicts** - existing rule, new signal, applicable scope, and required owner decision
8. **Next-run effect** - exactly what will change, what will not change, and where it applies

## Event row

| Event ID | Before | After | Edit reason | Normalized learning | Memory key | Classification | Scope | Status | Recorded by | Approved by | Confidence | Destination |
|---|---|---|---|---|---|---|---|---|---|---|---:|---|

Use the exact enums and fields in `schemas/learning-event.schema.json`.
The normalized learning is the future instruction. Never use the approved replacement line as the
rule unless the human explicitly confirms that exact line is the reusable instruction.
`author` records who created the event. `approved_by` is separate and required for approved events;
it must match an authorized rule approver in the active brand manifest.

## Promotion rules

- One explicit factual or compliance correction may become an approved scoped rule.
- One explicitly approved voice rule may become an approved scoped rule.
- A preference needs three consistent approved signals before it may be proposed for promotion.
- A proposal does not become approved without a human decision.
- Execution-specific and editor-specific changes remain scoped.
- Universal-method promotion requires a separate explicit decision by Joe.

## Upload-only patch

When the runtime cannot write the brand folder, include a machine-copyable JSON event object for
each recordable learning and name the destination folder. The folder owner validates and appends it
with `scripts/record-learning.py`, which rebuilds active memory. Never claim the brand has learned
until the canonical folder and active memory were updated.

## Never

- Learning from an unapproved draft
- Treating every edit as a brand rule
- Crossing learning between brands
- Replacing event history instead of appending or superseding
- Hiding a conflict by choosing the newest signal
- Using the model's own revision as human evidence

## Self-check

- [ ] Generated and approved versions are identified
- [ ] Every material change has a reason or is marked reason unavailable
- [ ] Every event has a normalized learning and stable memory key where required
- [ ] Every event validates against the schema
- [ ] Promotions follow the thresholds
- [ ] Non-learning edits are excluded from memory
- [ ] Conflicts remain visible
- [ ] Next-run effects are concrete and correctly scoped
