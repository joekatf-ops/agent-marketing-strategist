# Retained learning

The brand gets smarter through traceable approved changes, not through general conversation memory.

## Learning event

Every event records brand, market, product, source asset, before, after, edit reason, normalized
learning, memory key, scope, classification, status, confidence, author and timestamp. The schema is
`schemas/learning-event.schema.json`.

`after` is the approved asset copy. `learning` is the generalized instruction that may affect a
future run. Never turn the replacement copy itself into a permanent rule. `memory_key` gives related
signals and conflicts one stable identity, for example `claims.loss_prevention`.

## Classifications

| Classification | Example | Default scope |
|---|---|---|
| Factual correction | Guarantee is 60 days, not 30 | product or brand |
| Compliance correction | This claim cannot use clinically proven | market or brand |
| Voice rule | Never call the customer a biohacker | brand |
| Preference | Approved copy repeatedly removes hype | proposed brand preference |
| Execution-specific | This creator needs shorter sentences | execution |
| Strategic learning | Persona rejects the mechanism explanation | product or market |
| Editor preference | One editor avoids a phrase | editor |
| Accidental edit | Typo or incomplete revision | none |

## Capture workflow

1. Preserve the generated asset and its identifier.
2. Preserve the human-approved version.
3. Diff meaning, not only characters.
4. Record each materially different lesson as a separate event.
5. Ask for a reason and write the normalized learning separately. If the reason is unavailable,
   store `Reason unavailable`, lower confidence and keep the event proposed.
6. Append the event. Never rewrite the event history.
7. Rebuild `learning/active-memory.json`, the deterministic projection used by future runs.
8. Produce a Learning Update showing what was captured, activated, proposed or excluded.

## Promotion policy

- Factual and compliance corrections need one explicit approval before becoming hard rules.
- A voice rule needs explicit approval.
- A preference needs three consistent approved signals before it may be proposed.
- Proposal is not approval.
- Execution-specific and editor-specific changes do not become brand rules automatically.
- Accidental and rejected edits do not teach the agent.
- A rule keeps its source event, approver, date, scope and supersession history.
- Brand learning never crosses brands automatically.
- Promotion into Joe's universal method is a separate explicit human action.
- Approved hard rules and preferences require a stable memory key and an author listed in
  `brand.yml` under `approvals.rule_approvers`.
- Three preference signals must use distinct source assets. A candidate remains proposed until a
  human approves a rule event.

## Conflicts

Do not silently use the newest event. When approved rules conflict, show both, their scope and their
dates. Prefer the narrower valid scope until an approver resolves the conflict. Supersede the old
rule rather than deleting it. `supersedes` must point to an existing event in the same brand ledger.

## Active memory

`scripts/record-learning.py` appends the validated event and rebuilds
`learning/active-memory.json`.

- Approved factual, compliance and voice events become scoped active rules using `learning`.
- Approved strategic events become approved insights.
- Approved preferences remain signals; three distinct matching signals create a proposed candidate.
- Execution and editor notes remain scoped.
- Universal candidates do not enter the universal method automatically.
- Proposed, rejected and accidental events do not become active.
- Rules sharing a memory key and carrying contradictory values appear as unresolved conflicts.

Raw events remain the audit history. Active memory is the compact, bundled projection for the next
run. Human-curated `approved-rules.yml` remains an additional controlled source and conflicts with
active memory must be surfaced.

## Writable and upload-only runtimes

In a writable brand folder, use `scripts/record-learning.py` to append events and rebuild active
memory. In an upload-only runtime, return the Learning Update contract as a patch. The canonical
folder owner applies each event with the same script, then rebuilds the brand bundle.

## What not to learn

- Unapproved drafts
- Changes with identical meaning
- Accidental deletions
- A model's own rewrite of its previous output
- Private personal data not needed for the lesson
- Competitor practices as brand preferences
- Performance conclusions that the supplied test did not isolate
