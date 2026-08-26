# agent-marketing-strategist

An evidence-led direct-response Meta strategist for DTC brands. One universal method serves many
brands. Each brand keeps its own connected folder, evidence, decisions, creative, and approved
learning.

**Version:** 0.2.0
**Status:** build candidate

## The operating model

```text
Universal strategist
├── Joe's method, contracts, hook formats, and research rules
├── Optional connectors: Firecrawl, TrendTrack, Foreplay
└── One active brand folder per run
    ├── brand and product truth
    ├── website snapshots and external evidence
    ├── customer intelligence and concepts
    ├── outputs and approved claims
    └── append-only learning and approved rules
```

The universal skill never absorbs one brand's preferences automatically. The brand folder is the
durable brain for that brand and travels between LLMs through direct folder access or a generated
brand bundle.

## What it produces

| Artefact | What it does |
|---|---|
| Brand Readiness | Checks identity, evidence, website freshness, claims, connectors, and mode limits |
| Customer Intelligence | Separates first-party truth, customer evidence, market evidence, behaviour, and judgement |
| Concept Batch | Builds an evidence-backed Persona x Outcome x Angle portfolio |
| Hook Batch | Creates six strategically different hooks across at least four formats |
| Ad Copy | Creates two lead routes, each in short, medium, and long form, plus five headlines |
| Video Script | Produces a shootable beat-by-beat script, opening, shot list, and claim check |
| Static and Carousel Spec | Produces an executable layout, copy, visual direction, and claim check |
| Ad Diagnosis | Reads manually supplied Meta exports or screenshots without requiring live access |
| Learning Update | Captures approved human revisions without turning every edit into a permanent rule |

Each output has a versioned contract in [`contracts/`](contracts/).

## Start a brand

Create one folder for every brand:

```bash
python3 scripts/init-brand-folder.py /path/to/brands/example-brand \
  --name "Example Brand" \
  --slug example-brand
```

Then fill the folder in this order:

1. `brand.yml`: identity, market, website, ownership, naming, and crawl state
2. `context/brand-core.md`: positioning and current brand assertions
3. `context/voice.md` and `context/visual.md`: approved rules and examples
4. `products/`: catalog, offers, economics, proof, approved claims, and prohibited claims
5. `connectors/capabilities.yml`: what is configured and what actually passed preflight
6. `research/`: first-party evidence, market evidence, evidence ledger, and intelligence brief
7. `learning/`: approved rules, raw append-only events, conflicts, and preferences

Add authorized human names to `brand.yml` under `approvals.rule_approvers` before recording approved
learning. The recorder rejects unconfigured or unauthorized approvers.

Do not put API keys, passwords, or tokens in the brand folder.

The previous `config/brand.example.yml` is a legacy migration adapter, not the v0.2 source of truth.

## Website freshness

Firecrawl is preferred. The strategist:

- checks the site whenever the brand folder opens;
- retrieves new and changed pages;
- runs a full crawl when the last full snapshot is seven or more days old;
- forces a fresh crawl before major research, concepts, positioning, or launch work;
- records added, changed, and removed pages without silently replacing approved facts.

For a new brand without reviews, it researches competitor sites, reviews, communities, search
language, and ads. Those findings stay labelled as market evidence until first-party evidence exists.

## Connector setup

Start with [`connectors/README.md`](connectors/README.md), then use the provider guide:

- [`connectors/firecrawl.md`](connectors/firecrawl.md)
- [`connectors/trendtrack.md`](connectors/trendtrack.md)
- [`connectors/foreplay.md`](connectors/foreplay.md)

A connector is available only after a successful read-only call in the current runtime. Missing
connectors trigger an explicit fallback, never simulated results.

## Runtime setup

Clone the repository once:

```bash
git clone https://github.com/joekatf-ops/agent-marketing-strategist.git
```

Use the guide for the chosen surface:

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

Upload `PROMPT.md`, `dist/knowledge-bundle.md`, and the generated brand bundle. The canonical brand
folder remains the source of truth.

## Working loop

1. Resolve one active brand, market, and product.
2. Run Brand Readiness and refresh the website when required.
3. Research and classify the evidence.
4. Pause after customer intelligence for human direction.
5. Build and select concepts.
6. Pause before full creative production.
7. Build hook batches, scripts, statics, and Meta copy.
8. Diagnose manually supplied performance data when available.
9. Record approved human revisions as scoped learning events.

Live Meta performance connection is intentionally deferred. Manual exports, screenshots, or tables
remain the current diagnosis input.

## Learning without drift

Use `scripts/record-learning.py` for approved revisions. Each event stores before, after, edit
reason, normalized learning, memory key, classification, scope, status, confidence, author and
timestamp. The script rebuilds `learning/active-memory.json`, which is included in the next brand
bundle.

- Factual and compliance corrections can become approved scoped rules after explicit approval.
- Voice rules require explicit approval.
- Preferences need three consistent approved signals before they can be proposed.
- Execution and editor preferences remain narrow.
- Brand learning never crosses brands automatically.
- Promotion into Joe's universal method is a separate decision.

Upload-only runtimes return the Learning Update contract as a patch. They cannot claim the brand has
learned until the canonical folder is updated.

## Validate and build

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate-package.py .
python3 scripts/build-knowledge-bundle.py
```

Frozen examples live in [`examples/`](examples/).

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.2.0 | 2026-08-26 | Added multi-brand folders, recurring website refresh, evidence classes, six-hook batches, copy lengths, approved-revision learning, upload bundles, and seven runtime guides. |
| 0.1.0 | 2026-08-26 | Initial strategist with research, concepts, creative production, and diagnosis contracts. |
