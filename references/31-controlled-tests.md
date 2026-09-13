# Controlled tests and appeal learning

Use when asked to plan or interpret a comparison. A draft plan can contain explicitly unknown
budget or volume fields; do not invent them or block useful planning. This reference does not
authorise spending, changing delivery or launching ads. The house profile in reference 09 applies
only when selected; a controlled test is not automatically a four-awareness-ad batch.

## Select the comparison

| Design | What changes | What the result can support |
|---|---|---|
| Broad exploration | Several elements, such as awareness, appeal, format and destination | Which complete execution performed better under observed conditions; possible explanations. |
| Single-variable comparison | One declared factor with other material factors held constant | An effect estimate only if allocation, volume, tracking and other design conditions support it. |
| Appeal/package comparison | A headline promise and the body or destination needed to fulfil it | The performance of the whole selling package, not the isolated headline. |
| Incrementality comparison | Exposure or an incentive versus a suitable control | Additional outcomes attributable to that intervention within the design's limits. |

Changing only text does not itself establish causality. Delivery may differ in audience, placement,
time or spend. Record whether allocation is randomised, how contamination is limited and whether
the comparison is observational. Do not label platform-selected spend as random assignment.

## Reusable test card

Return these fields as a compact table or structured record. Omit irrelevant fields with a reason.

| Field | Required decision |
|---|---|
| Question and hypothesis | What buyer response or commercial uncertainty will the test resolve? |
| Design | Broad, single-variable, package or incrementality comparison; justification. |
| Control and variants | Stable identifiers, exact assets/copy or references, existing result if known. |
| Changed factor | Exact difference; if supporting copy must change, classify the design accordingly. |
| Constants | Product, visual, body, offer, destination, audience eligibility and other material conditions. |
| Allocation | Actual assignment method, unit, overlap/contamination and placement/time controls. |
| Main outcome | A defined business result, denominator and observation window; e.g. cost per new customer. |
| Diagnostics and guardrails | Clicks, conversion stages, contribution, refunds, complaints and operational failure. |
| Exposure and budget | Proposed volume/duration, rationale, approved spend ceiling and unresolved inputs. |
| Decision and stopping rule | Minimum evidence and material improvement required, scheduled read, safety stops and inconclusive outcome. |
| Measurement limits | Attribution method, tracking gaps, delayed purchases, uncertainty and external changes. |
| Owner and state | Draft, approved, launched or reviewed; the plan alone is not a launch. |

If an inferential result is requested, plan sample size from baseline rate and a meaningful detectable
effect, record the chosen error/power assumptions and use an appropriate analysis. If inputs are
missing, state what is needed and keep the read directional. Account for repeated looks or many
variants in the design. A fixed duration alone does not establish adequate evidence.

Preserve a working control while exploring. A large increase in spend needs a separate read; limited
test economics do not guarantee scaled economics. Log changes and stop conditions instead of
silently combining incompatible periods. Do not claim a significant difference without its analysis.

## Business outcome before proxy outcome

Report cost per new customer and contribution where available. For a trial or lead campaign, include
trial/lead fulfilment, conversions, variable costs, returns and the relevant follow-up window.
Define cost categories so they are not counted twice. Distinguish projected relationship value
from observed contribution and payback.

High clicks with few customers may mean weak qualification, message mismatch, a poor offer, a weak
page or an operational issue. Healthy hook rate does not eliminate a creative problem. If ads vary
in several ways, propose a narrower follow-up rather than attributing the difference to one element.

## Store the appeal in existing test memory

Extend the existing `strategy/test-register.yml` entry with `test_design` and optional
`appeal_summary`. Keep prior records valid when these fields are absent. Do not create a second
canonical register or rewrite historic observations.

An appeal summary carries: reader/situation, wanted experience, argument, supporting evidence,
control and variant IDs, defined outcome values and window, observation, explanation confidence,
causal limits and proposed next question. Store lower-performing and inconclusive appeals too.
Use reference 14 for authority and persistence; a draft summary does not update controlled records.

Example: if two desk-organiser headlines use the same photo and offer but one needs a different
body, call it a package comparison. If only headline copy changes, preserve all other assets and
record allocation before interpreting the result. See `examples/controlled-headline-test.md`.
