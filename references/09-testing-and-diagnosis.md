# Testing, measurement and diagnosis

This file governs test structure, observation and decisions. Benchmarks and sourced platform
thresholds live in `references/12-meta-platform.md`. Meta launch, evidence capture and campaign
changes are manual. This method neither requires nor implies live Meta access.

## Creative-testing stage

Use one creative-testing campaign for one product and one region.

| Level | Governed structure |
|---|---|
| Campaign | CT sales campaign using ABO |
| Ad set | One new CONTST batch per ad set |
| Initial NNT or INSPO ads | Exactly four standalone executions: UWA, PRA, SLA and PDA |
| ITR ads | May be narrower when a cited prior signal makes that follow-up more informative |
| Daily budget | $50 per ad set absolute floor; approximately $100 per ad set preferred starting point |
| Planned observation | Five full days in the recorded account timezone |

The $50 floor is not a recommendation to underfund a read. Set higher budgets from price, target
CAC, break-even CAC, capital and account context. State the currency and reasoning. Before launch,
calculate:

```
expected purchases at target CAC = planned spend / target CAC
```

Say the result plainly. A five-day review remains directional or too early when spend, purchase or
brand-specific validity thresholds are not met.

## Initial four-ad logic

| Awareness | Job | Default destination |
|---|---|---|
| UWA | Recognition | LP |
| PRA | Diagnosis | LP |
| SLA | Differentiation | PDP |
| PDA | Decision | PDP |

Each ad must make a complete argument because delivery order and spend distribution are not
guaranteed. Every deliberate deviation must map to one controlled destination token: LP, PDP, HP or
CP. It is allowed only when the page continues the execution's promise, proof and CTA and the
Destination Handoff records the exception. A page that cannot map to one of those tokens blocks launch.

Initial tests make large changes across awareness, messaging route, hook, format, proof presentation
and destination. They compare complete executions in a live acquisition environment. They identify
associations and generate hypotheses. They do not prove which isolated variable caused the result.

## Observation protocol

Record the planned start and end timestamps. Five full days means five complete 24-hour account
days after delivery begins, not a launch-day fragment plus four dates.

Do not make routine creative, copy, destination, audience or budget changes during the planned
window. Intervene only for:

- operational failure;
- broken destination or tracking;
- policy issue;
- unacceptable commercial risk.

Log any intervention with timestamp, reason, owner, fields changed and the resulting validity limit.
At review, use manually supplied exports, screenshots or tables and preserve their date range,
attribution setting, currency and aggregation level.

## Read validity

Classify the read before interpreting performance. Apply these rules in order; each read receives
exactly one category:

1. **Too early.** Fewer than five full days is always Too early, regardless of spend or purchases.
   After five or more full days, the read is also Too early when neither the active brand's minimum
   spend threshold nor its minimum purchase threshold is met.
2. **Verdict.** Five or more full days have elapsed, all active spend and purchase thresholds are
   met, and there is no material integrity failure, no uneven delivery and no logged intervention
   that limits interpretation.
3. **Direction.** This is the remaining five-or-more-day category: at least one active spend or
   purchase threshold is met but not all thresholds are met, or all thresholds are met but uneven
   delivery, a logged intervention or a material integrity failure limits interpretation.

These rules are mutually exclusive. High volume on day three is still Too early. A five-day read
with neither volume threshold met is also Too early; a five-day read with only one threshold met is
Direction. Five days alone never creates statistical certainty. Report the expected and actual
purchases, the additional spend or purchases required and any delivery imbalance. Never omit an ad
that spent money.

## Three measurement layers

Always read the layers in this order.

| Layer | Measures | Question |
|---|---|---|
| 1. Business | Spend, purchases, CAC, revenue and contribution after advertising | Did the execution acquire economically? |
| 2. Funnel | Outbound CTR, landing-page-view rate, add-to-cart rate, checkout rate and purchase rate | Where did the path lose commercial intent? |
| 3. Creative | Spend distribution, first-frame retention, three-second view rate, hold rate, frequency, comments, awareness and format | What complete-execution signal could inform the next creative? |

A creative observation without its business and funnel context is incomplete. Compare first against
the active account norm. When no account norm exists, name the sourced range from
`references/12-meta-platform.md` and its limitation.

## Diagnostic chain

Work from the first weak stage. Later weakness may be a downstream symptom.

| Observed association | Likely explanation to investigate | Next check |
|---|---|---|
| Low first-frame retention | File, thumbnail, render or opening-frame problem | Verify playback and first-frame legibility |
| Low three-second view rate relative to the valid comparison | Opening lacks clarity or relevance for the delivered audience | Review opening visual, primary hook and Who congruence |
| Healthy three-second rate, sharp drop before proof | Body does not fulfil or sustain the opening | Check handoff, pacing and proof timing |
| Healthy hold, low outbound CTR | Argument creates attention without enough desire or reason to click | Review route, proof, objection and CTA |
| Healthy CTR, low landing-page-view rate | Load, tracking or destination failure | Test URL, speed and event integrity |
| Good landing-page views, low add to cart | Ad-to-page message break, product explanation or offer weakness | Audit Destination Handoff and page continuation |
| Good add to cart, low purchase | Price, shipping, trust, payment or checkout friction | Audit conversion environment |
| Healthy funnel, CAC above target | Economics or auction cost may be the constraint | Review CPM, AOV, margin and target CAC |
| Early efficiency decays as spend rises | Reach quality, fatigue or scale sensitivity | Read frequency and CTR trend, then scaling record |

These are possible explanations, not causal findings. Use "associated with" unless a suitable
follow-up isolated the variable.

## Six-decision taxonomy

Every reviewed execution or batch receives one of these six decisions and exactly one literal
top-level action.

| Decision | Evidence pattern | Top-level action | Execution instruction |
|---|---|---|---|
| Financial winner | At or below target CAC with useful volume in a valid read | scale | Graduate the published winner by its real Post ID into CBO scaling |
| Directional promise | Economics miss target but attention, click, conversion or response shows a bounded signal | ITR | Create a new CONTST batch against the same coordinate and cite this signal |
| Interest, weak conversion | Ad earns traffic but destination, product explanation, offer or checkout underperforms | keep | Keep the execution and coordinate unchanged while repairing the identified conversion-environment break before further spend |
| Weak throughout | No meaningful attention or action after a valid read | stop | Stop the batch, retain the losing evidence and prioritise a materially different NNT |
| Initial winner, scale failure | Testing economics were acceptable but deteriorated materially at higher spend | stop | Stop scaling, preserve the initial and scale records separately, and return any later follow-up as a separately decided ITR |
| Winner at scale | Acceptable economics persist at higher spend | keep | Keep the real-Post-ID ad in CBO scaling and add it to the evergreen winner library |

The top-level action field contains exactly one of `keep`, `ITR`, `stop` or `scale`, with the
capitalisation shown in the table. Never join actions with "or", encode a sequence in that field or
leave the choice to the operator. The execution instruction implements the selected action and may
record a future review trigger, but it does not add a second top-level action. A losing ad still
creates learning. Record what happened, the likely explanation, confidence and selected action
without promoting association into causal learning.

An ITR recommendation preserves the coordinate and describes the next hypothesis, but it does not
reserve a new CONTST. Allocate the new CONTST only after the human decides to build the batch. Until
then, any next brief states `CONTST: unreserved — human decision required`.

## Scaling stage

Scaling uses one SC campaign per product and region.

- Budget type is CBO.
- Create it only when useful winners exist.
- Graduate the published winner with its real Post ID; never rebuild it as a new ad.
- Record scaling performance separately from initial-test performance.
- Record scale failure without rewriting the original test result.
- Add only winners that retain acceptable economics at higher spend to the evergreen winner library.
- Send evidence-led follow-ups back to testing as new ITR batches with new CONTST IDs.

The CBO budget comes from economics and account context. There is no universal automatic budget
increase rule, and this package does not authorise automatic budget changes.

## Diagnosis integrity rules

1. Name every manual source, date range, attribution setting, currency, aggregation level and gap.
2. State read validity before reporting conclusions.
3. Every recommendation names the metric, value and comparison threshold behind it.
4. Separate coordinate, batch, execution and scaling results.
5. Do not kill a coordinate because one execution received spend while the others did not receive a useful read.
6. Use association language for broad tests and record explanation confidence.
7. Preserve losers, interventions, destination exceptions and scale failures.
8. Zero recommended changes is valid when the evidence does not support action.
9. Every six-decision result has one literal top-level action field: keep, ITR, stop or scale.

## Operating loop

1. Verify economics, inventory, tracking, claims, production capacity and destinations.
2. Select one or more evidence-backed Who x Primary Problem coordinates.
3. Allocate the next CONTST ID to every NNT, INSPO or ITR batch.
4. Build the governed execution set and complete destination handoffs.
5. Produce the manual Campaign Launch Plan and run preflight.
6. Observe five full days without routine changes.
7. Audit validity, then read business, funnel and creative layers.
8. Apply one of the six decisions and record exactly one literal top-level action: keep, ITR, stop or scale.
9. Preserve the test record separately from approved human-revision learning.
10. Present proposed persistence files and obtain human confirmation before any controlled-record
    update. Winner graduation additionally requires a verified real Post ID.

## Diagnosis persistence handoff

Performance Diagnosis can write its governed run report immediately. It may also propose a
`test-register-patch.yml`, `next-brief.md` or `persistence-summary.md`, but those files do not update
the selected brand's controlled records. A test-register patch is limited to the matching existing
test's observations, supplied results, confidence, verdict and next action; it contains no new test
ID. Approved human copy, claim and voice changes follow `contracts/learning-update.md` rather than
the test-memory path. Upload-only runtimes return the same patches and never claim persistence.
