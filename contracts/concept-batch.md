# Output Contract: Concept Batch
locked: 2026-08-27
version: 3.0.0

The governed plan for testing one or more concept coordinates. A concept coordinate is exactly
`Who x Primary Problem`. A coordinate, a test batch and an execution are separate records.

## Artefact

Markdown document plus one coordinate card and one test-batch card for each proposed launch.
`concept-batch-BRAND-YYYYMMDD.md`

## Sections, in order

1. **Batch header** - brand, market, product, region, requested question, commercial constraints,
   production constraints and what would count as a useful read
2. **Evidence summary** - verified brand facts, brand assertions, brand-customer evidence, market
   evidence, behavioural evidence and strategist judgement used
3. **Coordinate cards** - the enduring Who x Primary Problem records
4. **Test-batch cards** - the new sequential CONTST batches proposed against those coordinates
5. **Execution manifest** - every standalone ad, its traceability and production dependencies
6. **Destination coverage** - default routes, deliberate exceptions and handoff status
7. **What this batch will and will not tell us** - useful associations, limits and open questions

## Coordinate card shape, fixed

| Field | Rule |
|---|---|
| Coordinate key | Stable key from the coordinate register; not a CONTST ID |
| Who | One recognisable person or broad segment traced to customer intelligence |
| Primary Problem | One problem, frustration, tension or unmet desire |
| Supporting lenses | Only lenses that deepen Who or the Primary Problem without creating new axes |
| Evidence | Supporting and disconfirming evidence, source class, link or ID and confidence |
| Claim ceiling | What executions against this coordinate may and may not say |
| Coordinate status | Proposed, active, rejected or archived |
| Linked test history | Every prior CONTST batch for this coordinate, including losers |

Messaging route, awareness, hook, format, creator, proof presentation, offer presentation, visual
execution and destination are execution variables. They never appear as coordinate axes.

## Test-batch card shape, fixed

| Field | Rule |
|---|---|
| Test ID | Next unused sequential `CONTST###`; never reused and never hidden behind a version suffix |
| Source | NNT, INSPO or ITR |
| Coordinate key | Links the batch to one approved coordinate card |
| Test question | One question the complete execution set can inform |
| Hypothesis | Expected response and the evidence-backed reason |
| Source evidence | NNT hypothesis, INSPO source elements, or prior CONTST signal for ITR |
| Planned read | Spend, expected purchases at target CAC, observation window and validity limits |
| Execution set | Initial NNT and INSPO use exactly four standalone ads; ITR may be narrower when cited evidence justifies it |
| Production state | Owner, dependencies, claim gate and launch readiness |

Every NNT, INSPO and ITR batch receives a new CONTST ID. INSPO records what structural element is
adapted and confirms that identity, claims, assets, language and scripts are not copied. ITR retains
Who and Primary Problem, cites an observed prior signal and names the execution variables changed.

## Initial NNT and INSPO execution set

Every initial NNT or INSPO batch contains exactly four standalone ads in this order:

| Order | Awareness code | Job | Default destination |
|---|---|---|---|
| 1 | UWA | Recognition: make the Who recognise the situation or tension | LP |
| 2 | PRA | Diagnosis: name and explain the Primary Problem precisely | LP |
| 3 | SLA | Differentiation: show why this route differs from alternatives | PDP |
| 4 | PDA | Decision: provide the proof and reason to choose | PDP |

Each execution records: awareness code and job, messaging route, primary hook, media type, execution
format, required proof and claims, destination, CTA, people, assets and location required, and the
complete final ad name ending in `POSTIDXXX` before publication.

A deliberate deviation is permitted only when the execution and page remain congruent and the page
maps to one controlled destination token: LP, PDP, HP or CP. Record the default, selected token,
final URL, reason, supporting evidence, risks, owner and approval in the Destination Handoff. If the
page cannot be accurately represented by one of the four tokens, block launch.

## ITR execution set

An ITR may use fewer than four ads when prior evidence makes a narrower follow-up more informative.
Its card must cite the prior CONTST, preserve the coordinate, list every changed and retained
execution variable, justify the narrower set and state what the comparison cannot establish.

## Interpretation rules

- Initial batches compare complete executions and intentionally vary large execution variables.
- A result may identify a strong complete execution and create a hypothesis.
- Never claim that awareness, messaging route, hook, format, proof or destination caused a result
  unless that variable was isolated in a suitable follow-up.
- Each ad is complete on its own because delivery order is never guaranteed.

## Self-check before presenting

- [ ] Coordinate cards and test-batch cards use separate identities
- [ ] Every coordinate is exactly Who x Primary Problem
- [ ] Every batch has the next unused CONTST ID and one source classification
- [ ] Every initial NNT or INSPO has exactly UWA, PRA, SLA and PDA once each
- [ ] Every execution includes route, format, proof, destination and job
- [ ] UWA and PRA default to LP; SLA and PDA default to PDP
- [ ] Every deliberate destination exception is recorded and remains congruent
- [ ] Every default and exception maps to one controlled destination token: LP, PDP, HP or CP
- [ ] Every ITR cites a prior signal and receives a new CONTST ID
- [ ] The interpretation states association and limits rather than unsupported causation
