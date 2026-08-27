# agent-marketing-strategist

An evidence-led direct-response Meta strategist for DTC brands. One universal method serves many
brands. Each brand keeps its own connected folder, evidence, coordinate history, test history,
winners and approved learning.

**Version:** 0.3.0

**Status:** ready for use

Version 0.3.0 is a breaking strategy release. It replaces the old concept equation with the Master
Creative Strategy coordinate `Who x Primary Problem`. It preserves the v0.2 brand isolation,
evidence, website-refresh, portability, security and approved-revision learning systems.

## The operating model

```text
Universal strategist
├── reviewed Master Creative Strategy snapshot
├── output contracts, naming, hook formats and research rules
├── optional connectors and read-only method-governance checks
└── one active brand folder per run
    ├── brand, product, offer, economics and approved claims
    ├── website snapshots and classified evidence
    ├── Who x Primary Problem coordinates
    ├── sequential CONTST batches and graduated winners
    ├── production outputs and destination records
    └── append-only revision learning and approved rules
```

The Master Creative Strategy in Notion is canonical for the universal method. This repository is
its reviewed portable snapshot. A connected brand folder is canonical for that brand's truth and
learning. A freshness check can flag a method change for human review, but no connector or LLM may
automatically rewrite the repository.

The universal strategist never absorbs one brand's preferences automatically. A brand folder
travels between supported LLMs through direct folder access or a generated brand bundle.

## Coordinate, test batch and execution

These records have different identities and lifecycles:

| Record | Identity | What changes it |
|---|---|---|
| Concept coordinate | One enduring `Who x Primary Problem` key | A different Who or Primary Problem creates a new coordinate |
| Concept test batch | One new sequential `CONTST###` with source NNT, INSPO or ITR | Every new batch receives the next number, including an ITR on the same coordinate |
| Ad execution | One complete ad inside a batch | Awareness, messaging route, hook, format, creator, proof, offer presentation, visual or destination may change without creating a new coordinate |

Every initial NNT or INSPO batch contains four standalone ads: UWA recognition, PRA diagnosis, SLA
differentiation and PDA decision. Most Aware is conversion-environment guidance, not a standard ad.
Six hook packages are a pre-production option set for one approved execution, not six launch ads.

## What it produces

The package has eleven governed artefacts:

| Artefact | What it does |
|---|---|
| Brand Readiness | Checks identity, evidence, website freshness, claims, connectors, strategy state and mode limits |
| Customer Intelligence | Prioritises possible Who definitions, primary Problems and pairing evidence while keeping evidence classes separate |
| Concept Batch | Defines enduring coordinates separately from sequential NNT, INSPO or ITR test batches |
| Hook Batch | Creates six strategically different pre-production openings across at least four hook formats |
| Ad Copy | Creates two lead routes, each in short, medium and long form, plus five headlines, two descriptions and one CTA |
| Video Script | Produces a shootable beat-by-beat script, coherent opening, shot list and claim check |
| Static and Carousel Spec | Produces an executable layout, exact copy, visual direction and claim check |
| Campaign Launch Plan | Gives a human operator an exact manual Meta build, budget, naming, observation and scaling handoff |
| Destination Handoff | Preserves ad-to-page promise, proof, offer and CTA continuity for every execution |
| Ad Diagnosis | Reads manually supplied Meta exports, screenshots or tables without requiring live access |
| Learning Update | Captures approved human revisions without turning every edit into a permanent rule |

Each artefact has a versioned contract in [`contracts/`](contracts/).

## Start a brand

Create one folder for every brand:

```bash
python3 scripts/init-brand-folder.py /path/to/brands/example-brand \
  --name "Example Brand" \
  --slug example-brand
```

Then fill the folder in this order:

1. `brand.yml`: identity, market, currency, method version, website monitoring, controlled naming
   codes, the next test number and approvals
2. `context/brand-core.md`: positioning and current brand assertions
3. `context/voice.md` and `context/visual.md`: approved rules and examples
4. `products/`: catalog, offers, economics, proof, approved claims and prohibited claims
5. `connectors/capabilities.yml`: configured capabilities and actual read-only preflight results
6. `research/`: first-party evidence, market evidence, evidence ledger and customer intelligence
7. `strategy/`: coordinate register, sequential test register, winner library and hypotheses
8. `learning/`: approved rules, raw append-only events, conflicts and preferences

Add authorised human names to `brand.yml` under `approvals.rule_approvers` before recording approved
learning. The recorder rejects unconfigured or unauthorised approvers. Do not put API keys,
passwords or tokens in the brand folder.

`config/brand.example.yml` is a legacy adapter that points older installations to a portable brand
folder. It is not the v0.3 source of truth.

## Migrating a v0.2 brand folder

Do not overwrite, delete or reinitialise an existing v0.2 brand folder. Old folders may remain
readable, but they must be reported as needing strategy migration before v0.3 launch work.

Make a backup or work on a copy, then add the v0.3 manifest fields and the coordinate, test and
winner registers while preserving all existing evidence, outputs, learning events, rejected ideas
and historical results. Translate old strategy records through an explicit reviewed migration. Do
not silently rename an old concept, recycle an identifier or treat an old angle as a coordinate
axis. The initializer refuses to overwrite a non-empty destination.

## Website freshness

Firecrawl is preferred when available. The strategist:

- checks the site whenever the brand folder opens;
- retrieves new and changed pages;
- runs a full crawl when the last full snapshot is seven or more days old;
- forces a fresh crawl before major research, concept batches and launches;
- records added, changed and removed pages without silently replacing approved facts.

For a new brand without reviews, it researches competitor sites, reviews, communities, search
language and ads. Those findings stay labelled as market evidence until first-party evidence exists.

## Optional connectors

The reviewed repository snapshot and one complete brand folder are sufficient for normal use.
Connectors are optional capability upgrades, not prerequisites and not proof of live access.

Start with [`connectors/README.md`](connectors/README.md), then use the relevant guide:

- [`connectors/firecrawl.md`](connectors/firecrawl.md) for website retrieval
- [`connectors/trendtrack.md`](connectors/trendtrack.md) for trend discovery
- [`connectors/foreplay.md`](connectors/foreplay.md) for ad discovery
- [`connectors/notion-composio.md`](connectors/notion-composio.md) for a read-only universal-method freshness check

A connector is available only after a successful read-only call in the current runtime. Missing
connectors trigger an explicit fallback, never simulated results. Live Meta publishing, account
reads and automated budget changes are intentionally outside this release.

## Multiple LLM support

Clone the repository once:

```bash
git clone https://github.com/joekatf-ops/agent-marketing-strategist.git
```

Use the guide for the selected LLM surface:

- [Codex](connectors/runtime-codex.md)
- [Claude](connectors/runtime-claude.md)
- [Claude Code](connectors/runtime-claude-code.md)
- [ChatGPT](connectors/runtime-chatgpt.md)
- [Gemini](connectors/runtime-gemini.md)
- [Grok](connectors/runtime-grok.md)
- [Grok Agents](connectors/runtime-grok-agents.md)

Writable runtimes open the strategist and exactly one active brand folder. Upload-only runtimes use
two generated files:

```bash
python3 scripts/build-knowledge-bundle.py
python3 scripts/build-brand-bundle.py /path/to/brands/example-brand /path/to/example-brand-bundle.md
```

Upload `PROMPT.md`, `dist/knowledge-bundle.md` and the generated brand bundle. The canonical brand
folder remains the source of truth. Rebuild both bundles after an approved universal-method release
or canonical brand-folder change.

## Manual launch workflow

1. Resolve one active brand, market, product and region.
2. Run Brand Readiness and force a fresh website crawl before launch work.
3. Complete customer intelligence, then pause for human direction.
4. Approve a `Who x Primary Problem` coordinate and reserve the next `CONTST###` batch.
5. Build the UWA, PRA, SLA and PDA executions, then pause before full production.
6. Complete production contracts and one Destination Handoff per selected ad.
7. Produce the Campaign Launch Plan with fixed names, destinations, operator and manual preflight.
8. The human operator builds one ABO creative-testing campaign, one batch per ad set, at no less
   than $50 per ad set per day. Approximately $100 is the preferred starting point when economics
   and capital support it. Record the active brand currency in the plan.
9. Protect the five-full-day planned observation window. Record only allowed interventions.
10. Diagnose manually supplied exports, screenshots or tables. A useful winner may graduate with
    its real Post ID into a separate CBO scaling campaign.
11. Record scale performance separately and use evidence-led ITR batches for follow-up questions.

Five days is a planned review point, not permission to declare a verdict without enough spend or
purchases. Initial broad tests compare complete executions and do not prove isolated causation.

## Learning without drift

Use `scripts/record-learning.py` for approved human revisions. Each event stores before, after, edit
reason, normalised learning, memory key, classification, scope, status, confidence, event author,
approver and timestamp. The script rebuilds `learning/active-memory.json`, which is included in the
next brand bundle.

- Factual and compliance corrections can become approved scoped rules after explicit approval.
- Voice rules require explicit approval.
- Preferences need three consistent approved signals before they can be proposed.
- Execution and editor preferences remain narrow.
- Brand learning never crosses brands automatically.
- Test observations remain in the test register and do not become isolated causal claims.
- Promotion into the universal method is a separate human decision.

Upload-only runtimes return the Learning Update contract as a patch. They cannot claim the brand has
learned until the canonical folder is updated.

## Validate and build

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/validate-package.py .
python3 scripts/build-knowledge-bundle.py
git diff --check
```

Frozen examples live in [`examples/`](examples/).

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.3.0 | 2026-08-27 | Adopted `Who x Primary Problem`, four-ad CONTST batches, locked naming, manual ABO launch plans, destination handoffs, CBO scaling with real Post IDs, safe strategy registers and read-only Notion governance. |
| 0.2.0 | 2026-08-26 | Added multi-brand folders, recurring website refresh, evidence classes, six-hook batches, copy lengths, approved-revision learning, upload bundles and seven runtime guides. |
| 0.1.0 | 2026-08-26 | Initial strategist with research, concepts, creative production and diagnosis contracts. |
