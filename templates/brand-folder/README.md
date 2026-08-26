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
- `strategy/`: concept register and hypothesis backlog
- `outputs/`: generated and human-approved assets
- `learning/`: append-only events, revisions, approved rules and conflicts
- `connectors/`: capability status only, never credentials

Before recording an event with `status: approved`, add the authorized human names to
`brand.yml` under `approvals.rule_approvers`. The recorder rejects approved events from anyone else.
