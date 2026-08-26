# Output Contract: Concept Batch
locked: 2026-08-26
version: 1.0.0

The strategic output. One batch is what goes into a creative test.

## Artefact
Markdown document plus a concept card per concept.
`concept-batch-{{brand.slug}}-YYYYMMDD.md`

## Sections, in order

1. **Batch header** - what question this batch answers, the NNT / INSPO / ITR allocation, the
   test budget and window, and the expected purchases at target CAC.
2. **Concept cards** - one per concept, in the fixed shape below.
3. **Coverage check** - a table showing persona, outcome, angle type and source across the
   batch, to prove the concepts are meaningfully different rather than one idea three ways.
4. **What this batch will and will not tell us** - honest statement of the read.

## Concept card shape, fixed

Every card carries exactly these fields, in this order:

| Field | Rule |
|---|---|
| Concept code | `{{CONCEPT}}###`, sequential, never reused |
| Source | NNT, INSPO or ITR. If ITR, names the prior test and the signal |
| Persona | Behavioural, traced to the intelligence brief |
| Outcome | One problem or desired outcome |
| Angle | One sentence. Never restates the outcome |
| Angle type | Exactly one of: How it works, The reframe, Vs the old way, Proof you can see |
| Hypothesis | If we tell [persona] that [angle], they will [expected response], because [evidence] |
| Evidence | The quotes, competitor gap or prior result this rests on, with links |
| Necessary belief targeted | Which of the eleven beliefs this concept moves |
| Claim ceiling | What this concept may not say |
| Meta ad set name | Per `references/07-naming.md` |
| Four executions | UWA, PRA, SLA, PDA. Each with format, length, destination and a one-line messaging job |

## Counts

- Concepts per batch: 3 by default, 2 to 5 allowed with a stated reason
- Executions per concept: exactly 4, one per awareness state
- Angle types across a batch: at least 2 distinct, so the batch is not one argument repeated

## Formatting rules

- The angle is one sentence. Not two, not a paragraph
- Every concept card fits on one screen
- No em dashes

## Never

- A concept whose angle restates its outcome
- More than one angle type per concept
- A hypothesis with no evidence line under it
- A persona that does not appear in the customer intelligence brief
- Format treated as a concept axis

## Self-check before presenting

- [ ] Every card has all thirteen fields, in order
- [ ] No angle restates its outcome
- [ ] Exactly one angle type per concept
- [ ] At least two distinct angle types across the batch
- [ ] Every hypothesis traces to evidence with a link
- [ ] Every concept has exactly four awareness executions
- [ ] Ad set names validate against the naming reference
- [ ] Concept numbers are sequential and unused
