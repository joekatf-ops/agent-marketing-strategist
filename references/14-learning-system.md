# Retained learning

The brand gets smarter through traceable approved changes, not through general conversation memory.

## Learning event

Every event records brand, market, product, source asset, before, after, reason, scope,
classification, status, confidence, author and timestamp. The schema is
`schemas/learning-event.schema.json`.

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
5. Ask for a reason when the reason changes the scope. Do not block capture when it is unavailable.
6. Append the event. Never rewrite the event history.
7. Produce a Learning Update showing what was captured and what, if anything, is eligible for
   promotion.

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

## Conflicts

Do not silently use the newest event. When approved rules conflict, show both, their scope and their
dates. Prefer the narrower valid scope until an approver resolves the conflict. Supersede the old
rule rather than deleting it.

## Writable and upload-only runtimes

In a writable brand folder, use `scripts/record-learning.py` to append events. In an upload-only
runtime, return the Learning Update contract as a patch. The canonical folder owner applies it.

## What not to learn

- Unapproved drafts
- Changes with identical meaning
- Accidental deletions
- A model's own rewrite of its previous output
- Private personal data not needed for the lesson
- Competitor practices as brand preferences
- Performance conclusions that the supplied test did not isolate
