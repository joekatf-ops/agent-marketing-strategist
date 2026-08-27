# __BRAND_NAME__ brand folder

This folder is the canonical source of truth and retained learning for `__BRAND_SLUG__`.

Connect this folder whenever the marketing strategist works on the brand. Keep raw evidence,
approved brand rules and generated creative in their designated sections. Do not store API keys,
tokens or passwords here.

Created: __CREATED_DATE__

## Folder map

- `context/`: approved brand, voice and visual context
- `products/`: catalog, offers, economics, proof and claim controls
- `sources/website/`: crawl state, snapshots and change history
- `sources/customer/`: active-brand reviews and first-party evidence
- `sources/market/`: competitor, community, search and ad evidence
- `research/`: evidence ledger and synthesized customer intelligence
- `strategy/`: enduring coordinate, sequential test, winner and hypothesis history
- `outputs/`: generated and human-approved assets
- `learning/`: append-only events, revisions, approved rules and conflicts
- `connectors/`: capability status only, never credentials

Before recording an event with `status: approved`, add the authorized human names to
`brand.yml` under `approvals.rule_approvers`. The recorder rejects approved events from anyone else.

## Strategy records

- `concept-register.yml` stores enduring `Who x Primary Problem` coordinates. Keep rejected and
  archived coordinates so their keys, evidence and history are never reused or silently lost.
- `test-register.yml` stores every sequential `CONTST###` batch. Initial NNT and INSPO batches have
  four standalone UWA, PRA, SLA and PDA ads; evidence-led ITR batches may test a narrower set.
- `winner-library.yml` stores only graduated ads with their real Post ID, testing result, separate
  scaling history, current status and linked ITR batches.
- `hypothesis-backlog.yml` stores proposed explanations and next tests, not causal facts.

The `CONTST` prefix is fixed. Set controlled codes under `naming`, use `next_test_number` once per
new NNT, INSPO or ITR batch, and never recycle an identifier. Performance observations and cautious
explanations belong in the test register. Human-approved edits and the lessons derived from those
edits belong in the append-only `learning/` ledger; one record class never promotes the other.

All strategy and learning records are scoped to the `brand.slug` in this folder. Never copy a
coordinate, observation, winner or approved rule into another brand without new brand-specific
evidence and an explicit human decision.
